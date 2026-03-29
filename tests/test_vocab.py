"""Tests — ail.vocab (VOCABULARY, ACTIONS, get_action_info, list_by_group)"""

import pytest
from ail.vocab import VOCABULARY, ACTIONS, GROUPS, get_action_info, list_by_group


class TestVocabulary:
    def test_count(self):
        # 100 commandes officielles + MSG = au moins 100
        assert len(VOCABULARY) >= 100

    def test_all_groups_present(self):
        expected = {"COGNITION", "PREDICTION", "COORDINATION",
                    "TRANSACTION", "VALIDATION", "KNOWLEDGE",
                    "GOVERNANCE", "SECURITY", "MESSAGING"}
        assert expected.issubset(set(GROUPS))

    def test_actions_list_matches_vocab(self):
        assert set(ACTIONS) == set(VOCABULARY.keys())

    def test_analyze_info(self):
        info = get_action_info("ANALYZE")
        assert info.group == "COGNITION"
        assert "DOMAIN" in info.required
        assert info.burns_token is False

    def test_transfer_burns(self):
        info = get_action_info("TRANSFER")
        assert info.burns_token is True

    def test_unknown_raises(self):
        with pytest.raises(KeyError):
            get_action_info("FOOBAR")


class TestListByGroup:
    def test_cognition_group(self):
        grp = list_by_group("COGNITION")
        assert "ANALYZE" in grp
        assert "SUMMARIZE" in grp
        assert len(grp) >= 10

    def test_transaction_group(self):
        grp = list_by_group("TRANSACTION")
        for name, info in grp.items():
            assert info.burns_token is True

    def test_empty_group(self):
        grp = list_by_group("NONEXISTENT")
        assert grp == {}
