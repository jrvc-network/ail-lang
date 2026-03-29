"""
schema.py — Validation stricte des paramètres AIL
Vérifie les types, les plages, les formats des valeurs
"""

import re
from typing import Any, Callable, Dict, List, Optional, Tuple
from .errors import AILSyntaxError


# ── Validateurs atomiques ──────────────────────────────────────────────────────

def _is_positive_number(v: str) -> bool:
    try:    return float(v) > 0
    except: return False

def _is_number(v: str) -> bool:
    try:    float(v); return True
    except: return False

def _is_percentage(v: str) -> bool:
    try:    return 0.0 <= float(v) <= 1.0
    except: return False

def _is_duration(v: str) -> bool:
    return bool(re.match(r'^\d+[SMHDWY]$', v.upper()))

def _is_agent_id(v: str) -> bool:
    return bool(re.match(r'^[A-Z0-9_]{2,64}$', v.upper()))

def _is_nonempty(v: str) -> bool:
    return bool(v and v.strip())

def _is_hash(v: str) -> bool:
    return bool(re.match(r'^[A-F0-9]{8,64}$', v.upper()))

def _is_proposal_id(v: str) -> bool:
    return bool(re.match(r'^[A-Z0-9_-]{3,32}$', v.upper()))


# ── Schémas par action ────────────────────────────────────────────────────────

# Format : {PARAM: (validator_fn, error_message)}
ACTION_SCHEMAS: Dict[str, Dict[str, Tuple[Callable, str]]] = {

    "TRANSFER": {
        "AMOUNT": (_is_positive_number, "AMOUNT doit etre un nombre > 0"),
        "FROM":   (_is_agent_id,        "FROM doit etre un ID agent valide [A-Z0-9_]"),
        "TO":     (_is_agent_id,        "TO doit etre un ID agent valide [A-Z0-9_]"),
    },

    "STAKE": {
        "AMOUNT":   (_is_positive_number, "AMOUNT doit etre > 0"),
        "DURATION": (_is_duration,        "DURATION format : 30D, 6M, 1Y"),  # optionnel mais validé si présent
    },

    "UNSTAKE": {
        "AMOUNT": (_is_positive_number, "AMOUNT doit etre > 0"),
    },

    "REWARD": {
        "AGENT":  (_is_agent_id,        "AGENT doit etre un ID valide"),
        "AMOUNT": (_is_positive_number, "AMOUNT doit etre > 0"),
    },

    "BURN": {
        "AMOUNT": (_is_positive_number, "AMOUNT doit etre > 0"),
    },

    "MINT": {
        "AMOUNT": (_is_positive_number, "AMOUNT doit etre > 0"),
    },

    "ESCROW": {
        "AMOUNT":    (_is_positive_number, "AMOUNT doit etre > 0"),
        "CONDITION": (_is_nonempty,        "CONDITION ne peut pas etre vide"),
    },

    "BID": {
        "AMOUNT": (_is_positive_number, "AMOUNT doit etre > 0"),
        "TASK":   (_is_nonempty,        "TASK ne peut pas etre vide"),
    },

    "SPLIT": {
        "AMOUNT":     (_is_positive_number, "AMOUNT doit etre > 0"),
        "RECIPIENTS": (_is_nonempty,        "RECIPIENTS ne peut pas etre vide"),
    },

    "MSG": {
        "TOKENS": (_is_positive_number, "TOKENS doit etre > 0"),
        "EXPIRY": (_is_duration,        "EXPIRY format : 7D, 30D, 90D"),
    },

    "DELEGATE": {
        "AGENT": (_is_agent_id, "AGENT doit etre un ID valide"),
    },

    "VOTE": {
        "PROPOSAL_ID": (_is_proposal_id, "PROPOSAL_ID invalide"),
        "CHOICE":      (lambda v: v.upper() in ("FOR","AGAINST","ABSTAIN"),
                        "CHOICE doit etre FOR, AGAINST ou ABSTAIN"),
    },

    "PREDICT": {
        "HORIZON": (_is_duration, "HORIZON format : 7D, 1M, 1Y"),
    },

    "FORECAST": {
        "PERIOD": (_is_duration, "PERIOD format : 30D, 6M"),
    },

    "VERIFY_SIG": {
        "SIGNATURE":  (_is_nonempty, "SIGNATURE ne peut pas etre vide"),
        "PUBLIC_KEY": (_is_nonempty, "PUBLIC_KEY ne peut pas etre vide"),
    },

    "TRANSFER_GOV": {
        "AMOUNT": (_is_positive_number, "AMOUNT doit etre > 0"),
    },
}

# Types de messages BTR valides
BTR_MSG_TYPES = {"SIMPLE", "URGENT", "MULTI", "CONDITIONAL", "HERITAGE", "NOTARIZED", "LOOP"}

# Règles transversales (s'appliquent à toutes les actions)
GLOBAL_RULES = [
    # sender != receiver pour TRANSFER et MSG
    lambda action, params: (
        None if action not in ("TRANSFER", "MSG")
        else ("FROM et TO ne peuvent pas etre identiques"
              if params.get("FROM","").upper() == params.get("TO","").upper()
              and params.get("FROM") else None)
    ),
    # TYPE de message BTR valide
    lambda action, params: (
        None if action != "MSG" or "TYPE" not in params
        else (None if params["TYPE"].upper() in BTR_MSG_TYPES
              else f"TYPE invalide. Valeurs: {', '.join(sorted(BTR_MSG_TYPES))}")
    ),
]


# ── Classe principale ─────────────────────────────────────────────────────────

class AILSchema:
    """
    Valide les paramètres d'un message AIL contre son schéma.

    Usage :
        schema = AILSchema()
        errors = schema.validate("TRANSFER", {"AMOUNT": "500", "FROM": "JARVIS", "TO": "AGENT_X"})
        # → []  si valide, liste d'erreurs sinon
    """

    def __init__(self, strict: bool = True):
        self.strict = strict   # strict=True : lève une exception si invalide

    def validate(self, action: str, params: Dict[str, str]) -> List[str]:
        """
        Valide les params d'une action.
        Retourne une liste d'erreurs (vide = valide).
        """
        errors = []

        # Schéma spécifique à l'action
        schema = ACTION_SCHEMAS.get(action, {})
        for param, (validator, msg) in schema.items():
            if param in params:
                if not validator(params[param]):
                    errors.append(f"{action}.{param}: {msg}")

        # Règles globales
        for rule in GLOBAL_RULES:
            err = rule(action, params)
            if err:
                errors.append(err)

        if errors and self.strict:
            raise AILSyntaxError(
                f"Validation echouee pour {action}",
                " | ".join(errors)
            )

        return errors

    def validate_message(self, msg) -> List[str]:
        """Valide un AILMessage directement."""
        return self.validate(msg.action, msg.params)

    def is_valid(self, action: str, params: Dict[str, str]) -> bool:
        """Retourne True si les params sont valides, False sinon."""
        tmp = AILSchema(strict=False)
        return len(tmp.validate(action, params)) == 0


# ── Instance partagée (singleton léger) ──────────────────────────────────────

_default_schema = AILSchema(strict=False)

def validate(action: str, params: Dict[str, str]) -> List[str]:
    return _default_schema.validate(action, params)

def is_param_valid(action: str, params: Dict[str, str]) -> bool:
    return _default_schema.is_valid(action, params)


# ── Demo ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    schema = AILSchema(strict=False)

    tests = [
        ("TRANSFER", {"AMOUNT": "500",  "FROM": "JARVIS", "TO": "AGENT_X"},  True),
        ("TRANSFER", {"AMOUNT": "-10",  "FROM": "JARVIS", "TO": "AGENT_X"},  False),  # négatif
        ("TRANSFER", {"AMOUNT": "500",  "FROM": "JARVIS", "TO": "JARVIS"},   False),  # sender=receiver
        ("TRANSFER", {"AMOUNT": "abc",  "FROM": "JARVIS", "TO": "AGENT_X"},  False),  # non-numérique
        ("MSG",      {"TOKENS": "10",   "TYPE": "SIMPLE",  "EXPIRY": "30D"}, True),
        ("MSG",      {"TOKENS": "10",   "TYPE": "INVALID", "EXPIRY": "30D"}, False),  # type invalide
        ("VOTE",     {"PROPOSAL_ID": "PROP_001", "CHOICE": "FOR"},            True),
        ("VOTE",     {"PROPOSAL_ID": "PROP_001", "CHOICE": "MAYBE"},          False),  # choix invalide
        ("PREDICT",  {"HORIZON": "6M"},                                        True),
        ("PREDICT",  {"HORIZON": "BIENTOT"},                                   False),  # format invalide
    ]

    print("=== SCHEMA VALIDATION ===")
    for action, params, expected in tests:
        errors = schema.validate(action, params)
        ok     = len(errors) == 0
        status = "OK  " if ok == expected else "FAIL"
        print(f"  [{status}] {action:12} params={list(params.values())} -> {'valid' if ok else errors[0][:40]}")
