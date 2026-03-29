"""
core.py — Encodeur/Décodeur AIL v1.0
Syntaxe : [ACTION:OBJECT|PARAM1:VALUE1|PARAM2:VALUE2]
"""

import re
from typing import Any, Dict, Optional
from .errors import AILSyntaxError, AILActionError
from .vocab  import VOCABULARY, get_action_info

# Regex : [ACTION:OBJECT|KEY:VALUE|...]  (OBJECT optionnel)
_AIL_RE = re.compile(
    r'^\[(?P<action>[A-Z_]+)'
    r'(?::(?P<object>[^\|\]]+))?'
    r'(?P<params>(?:\|[A-Z_]+:[^\|\]]+)*)\]$'
)
_PARAM_RE = re.compile(r'\|([A-Z_]+):([^\|\]]+)')


class AILMessage:
    """Représente un message AIL décodé."""

    def __init__(self, action: str, object_: Optional[str] = None,
                 params: Optional[Dict[str, str]] = None, raw: str = ""):
        self.action  = action
        self.object  = object_
        self.params  = params or {}
        self.raw     = raw

    # ── Accès pratique ──────────────────────────────────────────────────────
    def get(self, key: str, default: Any = None) -> Any:
        return self.params.get(key, default)

    def __getitem__(self, key: str) -> str:
        return self.params[key]

    def __contains__(self, key: str) -> bool:
        return key in self.params

    # ── Sérialisation ────────────────────────────────────────────────────────
    def __str__(self) -> str:
        return encode(self.action, self.object, **self.params)

    def __repr__(self) -> str:
        return f"AILMessage(action={self.action!r}, object={self.object!r}, params={self.params!r})"

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"ACTION": self.action}
        if self.object:
            d["OBJECT"] = self.object
        d.update(self.params)
        return d

    # ── Validation ────────────────────────────────────────────────────────────
    def validate(self) -> bool:
        """Vérifie que les params obligatoires sont présents."""
        info = get_action_info(self.action)
        missing = [r for r in info.required if r not in self.params and r != "OBJECT"]
        if missing:
            raise AILSyntaxError(
                f"Paramètres manquants pour {self.action}",
                f"Required: {missing}"
            )
        return True

    @property
    def burns_token(self) -> bool:
        return VOCABULARY[self.action].burns_token

    @property
    def group(self) -> str:
        return VOCABULARY[self.action].group


# ── Fonctions publiques ──────────────────────────────────────────────────────

def encode(action: str, object_: Optional[str] = None, **params: str) -> str:
    """
    Encode une commande AIL en chaîne standard.

    >>> encode("ANALYZE", "CONTRACT", DOMAIN="LEGAL_CH", PRECISION="0.95")
    '[ANALYZE:CONTRACT|DOMAIN:LEGAL_CH|PRECISION:0.95]'

    >>> encode("PING")
    '[PING]'
    """
    action = action.upper()
    if action not in VOCABULARY:
        raise AILActionError(f"Action inconnue : {action}")

    parts = [action]
    if object_:
        parts[0] = f"{action}:{object_}"

    for k, v in params.items():
        parts.append(f"{k.upper()}:{v}")

    return "[" + "|".join(parts) + "]"


def decode(message: str) -> AILMessage:
    """
    Décode une chaîne AIL en AILMessage.

    >>> msg = decode("[ANALYZE:CONTRACT|DOMAIN:LEGAL_CH]")
    >>> msg.action
    'ANALYZE'
    >>> msg.object
    'CONTRACT'
    >>> msg.params
    {'DOMAIN': 'LEGAL_CH'}
    """
    message = message.strip()
    m = _AIL_RE.match(message)
    if not m:
        raise AILSyntaxError(
            "Format AIL invalide",
            f"Reçu : {message!r}  —  Attendu : [ACTION:OBJECT|KEY:VALUE]"
        )

    action = m.group("action")
    if action not in VOCABULARY:
        raise AILActionError(f"Action inconnue : {action}")

    object_ = m.group("object")
    params  = {k: v for k, v in _PARAM_RE.findall(m.group("params") or "")}

    return AILMessage(action=action, object_=object_, params=params, raw=message)


def is_valid(message: str) -> bool:
    """Retourne True si la chaîne est un message AIL syntaxiquement valide."""
    try:
        decode(message)
        return True
    except (AILSyntaxError, AILActionError):
        return False


def decode_batch(messages: list) -> list:
    """Décode une liste de messages AIL."""
    return [decode(m) for m in messages]
