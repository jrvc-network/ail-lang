"""Tests — ail.core (encode / decode / is_valid / AILMessage)"""

import pytest
from ail.core   import encode, decode, is_valid, AILMessage
from ail.errors import AILSyntaxError, AILActionError


# ── encode ────────────────────────────────────────────────────────────────────

class TestEncode:
    def test_simple_action(self):
        assert encode("PING") == "[PING]"

    def test_action_with_object(self):
        assert encode("ANALYZE", "CONTRACT") == "[ANALYZE:CONTRACT]"

    def test_action_with_params(self):
        result = encode("ANALYZE", "CONTRACT", DOMAIN="LEGAL_CH", PRECISION="0.95")
        assert result == "[ANALYZE:CONTRACT|DOMAIN:LEGAL_CH|PRECISION:0.95]"

    def test_action_lowercase_normalized(self):
        assert encode("ping") == "[PING]"

    def test_transfer(self):
        result = encode("TRANSFER", AMOUNT="500", FROM="JARVIS", TO="AGENT_X")
        assert "[TRANSFER|" in result
        assert "AMOUNT:500" in result

    def test_unknown_action_raises(self):
        with pytest.raises(AILActionError):
            encode("FOOBAR")


# ── decode ────────────────────────────────────────────────────────────────────

class TestDecode:
    def test_simple(self):
        msg = decode("[PING]")
        assert msg.action == "PING"
        assert msg.object is None
        assert msg.params == {}

    def test_with_object(self):
        msg = decode("[ANALYZE:CONTRACT]")
        assert msg.action == "ANALYZE"
        assert msg.object == "CONTRACT"

    def test_with_params(self):
        msg = decode("[ANALYZE:CONTRACT|DOMAIN:LEGAL_CH|PRECISION:0.95]")
        assert msg.params["DOMAIN"] == "LEGAL_CH"
        assert msg.params["PRECISION"] == "0.95"

    def test_roundtrip(self):
        original = "[DELEGATE:ANALYST|PRIORITY:HIGH|TOKENS:50]"
        assert str(decode(original)) == original

    def test_invalid_syntax_raises(self):
        with pytest.raises(AILSyntaxError):
            decode("PING")   # sans crochets

    def test_unknown_action_raises(self):
        with pytest.raises(AILActionError):
            decode("[FOOBAR:SOMETHING]")

    def test_msg_btr(self):
        msg = decode("[MSG|TO:AGENT_X|TYPE:SIMPLE|TOKENS:10|EXPIRY:30D]")
        assert msg.action == "MSG"
        assert msg.params["TO"] == "AGENT_X"


# ── is_valid ──────────────────────────────────────────────────────────────────

class TestIsValid:
    def test_valid(self):
        assert is_valid("[PING]") is True
        assert is_valid("[ANALYZE:REPORT|DOMAIN:FINANCE]") is True

    def test_invalid_no_brackets(self):
        assert is_valid("PING") is False

    def test_invalid_unknown_action(self):
        assert is_valid("[FOOBAR]") is False


# ── AILMessage ────────────────────────────────────────────────────────────────

class TestAILMessage:
    def setup_method(self):
        self.msg = decode("[DELEGATE:ANALYST|PRIORITY:HIGH|TOKENS:50]")

    def test_get(self):
        assert self.msg.get("PRIORITY") == "HIGH"
        assert self.msg.get("MISSING", "default") == "default"

    def test_contains(self):
        assert "PRIORITY" in self.msg
        assert "MISSING" not in self.msg

    def test_burns_token(self):
        assert self.msg.burns_token is True
        plain = decode("[ANALYZE:REPORT|DOMAIN:FINANCE]")
        assert plain.burns_token is False

    def test_group(self):
        assert self.msg.group == "COORDINATION"

    def test_to_dict(self):
        d = self.msg.to_dict()
        assert d["ACTION"] == "DELEGATE"
        assert d["OBJECT"] == "ANALYST"
        assert d["PRIORITY"] == "HIGH"
