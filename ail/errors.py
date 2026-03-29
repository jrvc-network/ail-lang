"""
errors.py — Erreurs AIL standardisées
Codes E001-E010 définis dans la spec RFC-AIL-001
"""

class AILError(Exception):
    """Erreur de base AIL."""
    code = "E000"
    def __init__(self, message: str, details: str = ""):
        self.message = message
        self.details = details
        super().__init__(f"[AIL {self.code}] {message}" + (f" — {details}" if details else ""))

class AILSyntaxError(AILError):
    """E001 — Syntaxe invalide."""
    code = "E001"

class AILActionError(AILError):
    """E002 — Action inconnue."""
    code = "E002"

class AILAgentError(AILError):
    """E003 — Agent introuvable."""
    code = "E003"

class AILTokenError(AILError):
    """E004 — Tokens insuffisants."""
    code = "E004"

class AILTimeoutError(AILError):
    """E005 — Timeout dépassé."""
    code = "E005"

class AILPermissionError(AILError):
    """E006 — Permission refusée."""
    code = "E006"

class AILResourceError(AILError):
    """E007 — Ressource indisponible."""
    code = "E007"

class AILVersionError(AILError):
    """E008 — Conflit de version."""
    code = "E008"

class AILSignatureError(AILError):
    """E009 — Signature invalide."""
    code = "E009"

class AILQuotaError(AILError):
    """E010 — Quota dépassé."""
    code = "E010"


ERROR_MESSAGES = {
    "E001": "[AIL:ERROR|CODE:E001|MESSAGE:SYNTAX_INVALID]",
    "E002": "[AIL:ERROR|CODE:E002|MESSAGE:ACTION_UNKNOWN]",
    "E003": "[AIL:ERROR|CODE:E003|MESSAGE:AGENT_NOT_FOUND]",
    "E004": "[AIL:ERROR|CODE:E004|MESSAGE:INSUFFICIENT_TOKENS]",
    "E005": "[AIL:ERROR|CODE:E005|MESSAGE:TIMEOUT_EXCEEDED]",
    "E006": "[AIL:ERROR|CODE:E006|MESSAGE:PERMISSION_DENIED]",
    "E007": "[AIL:ERROR|CODE:E007|MESSAGE:RESOURCE_UNAVAILABLE]",
    "E008": "[AIL:ERROR|CODE:E008|MESSAGE:VERSION_CONFLICT]",
    "E009": "[AIL:ERROR|CODE:E009|MESSAGE:SIGNATURE_INVALID]",
    "E010": "[AIL:ERROR|CODE:E010|MESSAGE:QUOTA_EXCEEDED]",
}
