"""
crypto.py — Signature Ed25519 des messages AIL
Sécurise les transactions et l'identité des agents
"""

import hashlib
import hmac
import os
import base64
import json
import time
from typing import Optional, Tuple

# Import optionnel cryptography (pip install cryptography)
try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey, Ed25519PublicKey
    )
    from cryptography.hazmat.primitives.serialization import (
        Encoding, PublicFormat, PrivateFormat, NoEncryption
    )
    from cryptography.exceptions import InvalidSignature
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

from .errors import AILSignatureError


# ── Clés ─────────────────────────────────────────────────────────────────────

class AILKeyPair:
    """Paire de clés Ed25519 pour un agent AIL."""

    def __init__(self, private_key=None):
        if not CRYPTO_AVAILABLE:
            # Mode HMAC-SHA256 de secours (sans cryptography)
            self._private_bytes = private_key or os.urandom(32)
            self._public_bytes  = hashlib.sha256(self._private_bytes).digest()
            self._mode = "hmac"
            return

        self._mode = "ed25519"
        if private_key is None:
            self._private = Ed25519PrivateKey.generate()
        elif isinstance(private_key, bytes):
            from cryptography.hazmat.primitives.serialization import load_der_private_key
            self._private = Ed25519PrivateKey.from_private_bytes(private_key[:32])
        else:
            self._private = private_key
        self._public = self._private.public_key()

    @property
    def public_key_b64(self) -> str:
        if self._mode == "hmac":
            return base64.b64encode(self._public_bytes).decode()
        raw = self._public.public_bytes(Encoding.Raw, PublicFormat.Raw)
        return base64.b64encode(raw).decode()

    @property
    def private_key_b64(self) -> str:
        if self._mode == "hmac":
            return base64.b64encode(self._private_bytes).decode()
        raw = self._private.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
        return base64.b64encode(raw).decode()

    def sign(self, message: str) -> str:
        """Signe un message, retourne la signature en base64."""
        data = message.encode("utf-8")
        if self._mode == "hmac":
            sig = hmac.new(self._private_bytes, data, hashlib.sha256).digest()
            return base64.b64encode(sig).decode()
        sig = self._private.sign(data)
        return base64.b64encode(sig).decode()

    def verify(self, message: str, signature_b64: str) -> bool:
        """Vérifie une signature. Retourne True si valide."""
        try:
            data = message.encode("utf-8")
            sig  = base64.b64decode(signature_b64)
            if self._mode == "hmac":
                expected = hmac.new(self._private_bytes, data, hashlib.sha256).digest()
                return hmac.compare_digest(sig, expected)
            self._public.verify(sig, data)
            return True
        except Exception:
            return False

    @classmethod
    def generate(cls) -> "AILKeyPair":
        return cls()

    @classmethod
    def from_b64(cls, private_b64: str) -> "AILKeyPair":
        return cls(base64.b64decode(private_b64))

    def to_dict(self) -> dict:
        return {
            "public_key":  self.public_key_b64,
            "private_key": self.private_key_b64,
            "mode":        self._mode,
        }


# ── Message signé ─────────────────────────────────────────────────────────────

class SignedAILMessage:
    """Message AIL avec signature cryptographique."""

    def __init__(self, raw: str, agent_id: str, signature: str,
                 public_key: str, timestamp: Optional[float] = None):
        self.raw        = raw
        self.agent_id   = agent_id
        self.signature  = signature
        self.public_key = public_key
        self.timestamp  = timestamp or time.time()

    def to_wire(self) -> str:
        """Sérialise en format transmissible sur le réseau."""
        payload = {
            "msg":    self.raw,
            "agent":  self.agent_id,
            "sig":    self.signature,
            "pub":    self.public_key,
            "ts":     int(self.timestamp),
        }
        return base64.b64encode(json.dumps(payload).encode()).decode()

    @classmethod
    def from_wire(cls, wire: str) -> "SignedAILMessage":
        payload = json.loads(base64.b64decode(wire).decode())
        return cls(
            raw       = payload["msg"],
            agent_id  = payload["agent"],
            signature = payload["sig"],
            public_key= payload["pub"],
            timestamp = payload.get("ts", 0),
        )

    def __repr__(self) -> str:
        return f"SignedAILMessage(agent={self.agent_id!r}, msg={self.raw!r})"


# ── Fonctions publiques ───────────────────────────────────────────────────────

def sign_message(raw_ail: str, agent_id: str, keypair: AILKeyPair) -> SignedAILMessage:
    """Signe un message AIL brut avec la clé privée de l'agent."""
    payload   = f"{agent_id}:{int(time.time())}:{raw_ail}"
    signature = keypair.sign(payload)
    return SignedAILMessage(
        raw       = raw_ail,
        agent_id  = agent_id,
        signature = signature,
        public_key= keypair.public_key_b64,
    )


def verify_message(signed: SignedAILMessage,
                   keypair: Optional[AILKeyPair] = None,
                   max_age_seconds: int = 300) -> bool:
    """
    Vérifie la signature d'un message signé.
    max_age_seconds : rejette les messages trop anciens (anti-replay).
    """
    # Vérification temporelle
    age = time.time() - signed.timestamp
    if max_age_seconds > 0 and age > max_age_seconds:
        raise AILSignatureError(
            "Message expiré",
            f"Age: {int(age)}s > max {max_age_seconds}s"
        )

    # Reconstruction du payload signé
    ts_approx = int(signed.timestamp)
    payload   = f"{signed.agent_id}:{ts_approx}:{signed.raw}"

    # Vérification avec la clé fournie ou la clé publique embarquée
    if keypair:
        ok = keypair.verify(payload, signed.signature)
    else:
        # Reconstruire une clé publique depuis le b64 (vérification légère HMAC)
        try:
            pub_bytes = base64.b64decode(signed.public_key)
            tmp = AILKeyPair.__new__(AILKeyPair)
            tmp._mode         = "hmac"
            tmp._private_bytes= pub_bytes
            tmp._public_bytes = pub_bytes
            ok = tmp.verify(payload, signed.signature)
        except Exception:
            ok = False

    if not ok:
        raise AILSignatureError(
            "Signature invalide",
            f"Agent: {signed.agent_id}"
        )
    return True


def message_hash(raw_ail: str) -> str:
    """Hash SHA-256 d'un message AIL — utilisé comme ID unique."""
    return hashlib.sha256(raw_ail.encode()).hexdigest()[:16].upper()


# ── Demo ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== AIL CRYPTO ===")
    print(f"Mode: {'Ed25519' if CRYPTO_AVAILABLE else 'HMAC-SHA256 (fallback)'}")
    print()

    # Générer des clés
    kp = AILKeyPair.generate()
    print(f"Public key : {kp.public_key_b64[:32]}...")

    # Signer un message
    msg = "[TRANSFER|AMOUNT:500|FROM:JARVIS_V90|TO:AGENT_X]"
    signed = sign_message(msg, "JARVIS_V90", kp)
    print(f"Message    : {signed.raw}")
    print(f"Signature  : {signed.signature[:32]}...")

    # Vérifier
    ok = verify_message(signed, kp)
    print(f"Valide     : {ok}")

    # Falsification
    signed.raw = "[TRANSFER|AMOUNT:9999|FROM:JARVIS_V90|TO:HACKER]"
    try:
        verify_message(signed, kp)
    except AILSignatureError as e:
        print(f"Falsif detectee : {e.code}")

    # Hash
    h = message_hash("[ANALYZE:REPORT|DOMAIN:FINANCE]")
    print(f"Hash       : {h}")

    # Wire format
    original = sign_message("[PING]", "AGENT_X", kp)
    wire     = original.to_wire()
    restored = SignedAILMessage.from_wire(wire)
    print(f"Wire round-trip : {restored.raw == original.raw}")
