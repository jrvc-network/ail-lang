"""
parser.py — AILParser : extraction de messages AIL depuis du texte libre
"""

import re
from typing import List, Iterator
from .core   import decode, AILMessage
from .errors import AILSyntaxError, AILActionError

# Détecte tous les tokens [MAJUSCULES...] dans un texte
_SCAN_RE = re.compile(r'\[[A-Z][A-Z_]*[^\]]*\]')


class AILParser:
    """
    Parse et extrait des messages AIL depuis du texte brut ou des flux.

    Usage :
        parser = AILParser()
        messages = parser.parse_text(agent_response)
        for msg in messages:
            print(msg.action, msg.params)
    """

    def __init__(self, strict: bool = False):
        """
        strict=False  → ignore les tokens mal formés (défaut)
        strict=True   → lève une exception au premier token invalide
        """
        self.strict = strict
        self._errors: List[str] = []

    # ── Parsing texte libre ───────────────────────────────────────────────────

    def parse_text(self, text: str) -> List[AILMessage]:
        """Extrait tous les messages AIL valides d'un texte."""
        results = []
        for raw in _SCAN_RE.findall(text):
            try:
                results.append(decode(raw))
            except (AILSyntaxError, AILActionError) as e:
                self._errors.append(str(e))
                if self.strict:
                    raise
        return results

    def scan(self, text: str) -> Iterator[AILMessage]:
        """Générateur — itère sur chaque message AIL trouvé."""
        for raw in _SCAN_RE.findall(text):
            try:
                yield decode(raw)
            except (AILSyntaxError, AILActionError) as e:
                self._errors.append(str(e))
                if self.strict:
                    raise

    # ── Parsing ligne par ligne ───────────────────────────────────────────────

    def parse_lines(self, lines: List[str]) -> List[AILMessage]:
        """Parse une liste de lignes (une par message)."""
        results = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                results.append(decode(line))
            except (AILSyntaxError, AILActionError) as e:
                self._errors.append(str(e))
                if self.strict:
                    raise
        return results

    # ── Filtrage ──────────────────────────────────────────────────────────────

    def filter_by_group(self, messages: List[AILMessage], group: str) -> List[AILMessage]:
        """Retourne uniquement les messages d'un groupe."""
        return [m for m in messages if m.group == group.upper()]

    def filter_burns(self, messages: List[AILMessage]) -> List[AILMessage]:
        """Retourne uniquement les messages qui brûlent des tokens."""
        return [m for m in messages if m.burns_token]

    # ── Diagnostic ────────────────────────────────────────────────────────────

    @property
    def errors(self) -> List[str]:
        return list(self._errors)

    def clear_errors(self):
        self._errors.clear()

    def __repr__(self) -> str:
        return f"AILParser(strict={self.strict}, errors={len(self._errors)})"
