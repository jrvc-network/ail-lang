"""
builder.py — MessageBuilder : API fluente pour construire des messages AIL
"""

from typing import Optional
from .core   import encode, AILMessage
from .errors import AILSyntaxError


class MessageBuilder:
    """
    Construit un message AIL étape par étape.

    Usage :
        msg = (MessageBuilder("DELEGATE")
               .to("ANALYST_AGENT")
               .param("PRIORITY", "HIGH")
               .param("TOKENS", "50")
               .build())
        # → '[DELEGATE:ANALYST_AGENT|PRIORITY:HIGH|TOKENS:50]'
    """

    def __init__(self, action: str):
        self._action: str              = action.upper()
        self._object: Optional[str]    = None
        self._params: dict             = {}

    # ── Méthodes chaînables ──────────────────────────────────────────────────

    def on(self, object_: str) -> "MessageBuilder":
        """Définit l'objet de l'action."""
        self._object = object_
        return self

    def to(self, target: str) -> "MessageBuilder":
        """Alias de on() — sémantique 'à destination de'."""
        return self.on(target)

    def param(self, key: str, value: str) -> "MessageBuilder":
        """Ajoute un paramètre clé/valeur."""
        self._params[key.upper()] = str(value)
        return self

    def params(self, **kwargs: str) -> "MessageBuilder":
        """Ajoute plusieurs paramètres en une fois."""
        for k, v in kwargs.items():
            self._params[k.upper()] = str(v)
        return self

    # ── Raccourcis sémantiques ────────────────────────────────────────────────

    def amount(self, value: str) -> "MessageBuilder":
        return self.param("AMOUNT", value)

    def from_(self, agent: str) -> "MessageBuilder":
        return self.param("FROM", agent)

    def priority(self, level: str) -> "MessageBuilder":
        return self.param("PRIORITY", level)

    def tokens(self, n: str) -> "MessageBuilder":
        return self.param("TOKENS", n)

    def expiry(self, value: str) -> "MessageBuilder":
        return self.param("EXPIRY", value)

    def domain(self, value: str) -> "MessageBuilder":
        return self.param("DOMAIN", value)

    # ── Finalisation ──────────────────────────────────────────────────────────

    def build(self) -> AILMessage:
        """
        Finalise et retourne un AILMessage validé.
        Lève AILSyntaxError si l'action est invalide.
        """
        from .core import decode
        raw = encode(self._action, self._object, **self._params)
        msg = decode(raw)
        msg.validate()
        return msg

    def raw(self) -> str:
        """Retourne la chaîne AIL sans créer un AILMessage."""
        return encode(self._action, self._object, **self._params)

    def __str__(self) -> str:
        return self.raw()

    def __repr__(self) -> str:
        return f"MessageBuilder({self.raw()!r})"


# ── Factories rapides ─────────────────────────────────────────────────────────

def msg_analyze(object_: str, **params) -> str:
    return MessageBuilder("ANALYZE").on(object_).params(**params).raw()

def msg_delegate(agent: str, **params) -> str:
    return MessageBuilder("DELEGATE").to(agent).params(**params).raw()

def msg_transfer(amount: str, from_: str, to: str, **params) -> str:
    return (MessageBuilder("TRANSFER")
            .amount(amount)
            .from_(from_)
            .param("TO", to)
            .params(**params)
            .raw())

def msg_btr(to: str, type_: str = "SIMPLE", tokens: str = "10",
            expiry: str = "30D") -> str:
    return (MessageBuilder("MSG")
            .param("TO", to)
            .param("TYPE", type_)
            .tokens(tokens)
            .expiry(expiry)
            .raw())
