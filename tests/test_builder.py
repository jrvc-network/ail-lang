"""Tests — ail.builder (MessageBuilder + factories)"""

import pytest
from ail.builder import MessageBuilder, msg_analyze, msg_delegate, msg_transfer, msg_btr
from ail.errors  import AILActionError


class TestMessageBuilder:
    def test_ping(self):
        assert MessageBuilder("PING").raw() == "[PING]"

    def test_chain(self):
        result = (MessageBuilder("DELEGATE")
                  .to("ANALYST_AGENT")
                  .param("PRIORITY", "HIGH")
                  .param("TOKENS", "50")
                  .raw())
        assert result == "[DELEGATE:ANALYST_AGENT|PRIORITY:HIGH|TOKENS:50]"

    def test_params_batch(self):
        result = MessageBuilder("ANALYZE").on("REPORT").params(DOMAIN="FINANCE").raw()
        assert "DOMAIN:FINANCE" in result

    def test_build_returns_ail_message(self):
        msg = MessageBuilder("PING").build()
        assert msg.action == "PING"

    def test_unknown_action_raises(self):
        with pytest.raises(AILActionError):
            MessageBuilder("FOOBAR").raw()

    def test_str_repr(self):
        b = MessageBuilder("PING")
        assert str(b) == "[PING]"
        assert "PING" in repr(b)


class TestFactories:
    def test_msg_analyze(self):
        r = msg_analyze("CONTRACT", DOMAIN="LEGAL_CH")
        assert r == "[ANALYZE:CONTRACT|DOMAIN:LEGAL_CH]"

    def test_msg_delegate(self):
        r = msg_delegate("ANALYST", PRIORITY="HIGH")
        assert "DELEGATE:ANALYST" in r

    def test_msg_transfer(self):
        r = msg_transfer("500", "JARVIS", "AGENT_X")
        assert "TRANSFER" in r
        assert "AMOUNT:500" in r
        assert "FROM:JARVIS" in r
        assert "TO:AGENT_X" in r

    def test_msg_btr_defaults(self):
        r = msg_btr("AGENT_X")
        assert "MSG" in r
        assert "TO:AGENT_X" in r
        assert "TOKENS:10" in r
        assert "TYPE:SIMPLE" in r
