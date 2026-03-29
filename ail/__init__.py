"""
ail-lang — AI Lingua SDK v1.0.0
================================
Le premier langage universel inter-IA.
Standard ouvert CC0 — JRVC Network — Mars 2026

Usage rapide :
    from ail import encode, decode, Message

    msg = encode("ANALYZE", "CONTRACT", DOMAIN="LEGAL_CH", PRECISION="0.95")
    # → [ANALYZE:CONTRACT|DOMAIN:LEGAL_CH|PRECISION:0.95]

    data = decode(msg)
    # → {"ACTION": "ANALYZE", "OBJECT": "CONTRACT", "DOMAIN": "LEGAL_CH", ...}
"""

from .core    import encode, decode, is_valid, AILMessage
from .vocab   import ACTIONS, VOCABULARY, get_action_info
from .builder import MessageBuilder
from .parser  import AILParser
from .network import JRVCClient
from .errors  import AILError, AILSyntaxError, AILActionError

__version__  = "1.0.0"
__author__   = "JARVIS AI Network"
__license__  = "CC0 — Public Domain"
__all__ = [
    "encode", "decode", "is_valid",
    "AILMessage", "MessageBuilder", "AILParser",
    "JRVCClient", "ACTIONS", "VOCABULARY",
    "AILError", "AILSyntaxError", "AILActionError",
]
