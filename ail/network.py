"""
network.py — JRVCClient : client réseau JRVC simulé (stub extensible)

Ce module fournit l'interface réseau AIL.
En production, il se connecte à un nœud JRVC réel via WebSocket/HTTP.
En mode local (défaut), il simule les réponses pour le développement.
"""

import time
import uuid
from typing import Any, Dict, List, Optional
from .core   import encode, decode, AILMessage
from .errors import AILAgentError, AILTokenError, AILTimeoutError


class AgentProfile:
    """Profil d'un agent dans le réseau JRVC."""

    def __init__(self, agent_id: str, balance: float = 0.0,
                 reputation: float = 0.0, staked: float = 0.0):
        self.agent_id   = agent_id
        self.balance    = balance
        self.reputation = reputation
        self.staked     = staked
        self.registered = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id":   self.agent_id,
            "balance":    self.balance,
            "reputation": self.reputation,
            "staked":     self.staked,
        }


class JRVCResponse:
    """Réponse standardisée du réseau JRVC."""

    def __init__(self, status: str, data: Any = None,
                 tx_id: Optional[str] = None, error: Optional[str] = None):
        self.status  = status       # "OK" | "ERROR" | "PENDING"
        self.data    = data
        self.tx_id   = tx_id or str(uuid.uuid4())[:8].upper()
        self.error   = error
        self.ts      = int(time.time())

    @property
    def ok(self) -> bool:
        return self.status == "OK"

    def to_ail(self) -> str:
        if self.ok:
            return f"[RESPOND:OK|REQUEST_ID:{self.tx_id}|STATUS:SUCCESS]"
        return f"[RESPOND:ERROR|REQUEST_ID:{self.tx_id}|STATUS:{self.error}]"

    def __repr__(self) -> str:
        return f"JRVCResponse(status={self.status!r}, tx_id={self.tx_id!r})"


class JRVCClient:
    """
    Client réseau JRVC.

    Usage local (développement) :
        client = JRVCClient(agent_id="MY_AGENT", local=True)
        client.register(balance=1000.0)
        resp = client.send("[ANALYZE:REPORT|DOMAIN:FINANCE]")

    Usage réseau (production) :
        client = JRVCClient(agent_id="MY_AGENT", node_url="wss://node.jrvc.ai")
    """

    VERSION = "1.0.0"

    def __init__(self, agent_id: str, balance: float = 0.0,
                 local: bool = True, node_url: Optional[str] = None):
        self.agent_id = agent_id.upper()
        self.local    = local
        self.node_url = node_url
        self._profile = AgentProfile(self.agent_id, balance)
        self._peers: Dict[str, AgentProfile] = {}
        self._inbox: List[Dict] = []
        self._tx_log: List[Dict] = []

    # ── Enregistrement ───────────────────────────────────────────────────────

    def register(self, balance: Optional[float] = None, capabilities: List[str] = None) -> JRVCResponse:
        """Enregistre l'agent dans le réseau."""
        if balance is not None:
            self._profile.balance = balance
        self._profile.registered = True
        msg = encode("REGISTER", self.agent_id,
                     CAPABILITIES=",".join(capabilities or ["GENERAL"]))
        return JRVCResponse("OK", data={"agent": self._profile.to_dict()},
                            tx_id="REG_" + self.agent_id[:6])

    # ── Envoi de messages ─────────────────────────────────────────────────────

    def send(self, ail_message: str) -> JRVCResponse:
        """
        Envoie un message AIL au réseau.
        En mode local, simule la réception et retourne une réponse.
        """
        try:
            msg = decode(ail_message)
        except Exception as e:
            return JRVCResponse("ERROR", error=str(e))

        if self.local:
            return self._local_dispatch(msg)

        # TODO : implémentation WebSocket/HTTP vers node_url
        raise NotImplementedError("Mode réseau non implémenté dans cette version.")

    def _local_dispatch(self, msg: AILMessage) -> JRVCResponse:
        """Dispatche localement selon l'action."""
        tx_id = f"TX_{int(time.time())}_{msg.action[:4]}"
        self._tx_log.append({"tx_id": tx_id, "message": str(msg), "ts": int(time.time())})

        # Simulation des actions à burn de tokens
        if msg.burns_token:
            cost = self._estimate_cost(msg)
            if self._profile.balance < cost:
                return JRVCResponse("ERROR",
                    error=f"Solde insuffisant — requis {cost} $JRVC",
                    tx_id=tx_id)
            self._profile.balance -= cost
            burned = cost * 0.01
            self._profile.balance = max(0, self._profile.balance)

        return JRVCResponse("OK",
            data={"action": msg.action, "object": msg.object, "params": msg.params},
            tx_id=tx_id)

    def _estimate_cost(self, msg: AILMessage) -> float:
        """Estime le coût en $JRVC d'un message qui brûle des tokens."""
        costs = {
            "DELEGATE":    5.0,
            "COLLABORATE": 10.0,
            "BROADCAST":   20.0,
            "TRANSFER":    float(msg.get("AMOUNT", "1")),
            "MSG":         float(msg.get("TOKENS", "10")),
            "VOTE":        1.0,
            "STORE":       0.5,
            "RETRIEVE":    0.5,
        }
        return costs.get(msg.action, 1.0)

    # ── Solde & profil ───────────────────────────────────────────────────────

    def balance(self) -> float:
        return self._profile.balance

    def profile(self) -> Dict[str, Any]:
        return self._profile.to_dict()

    def tx_log(self) -> List[Dict]:
        return list(self._tx_log)

    # ── Réseau ───────────────────────────────────────────────────────────────

    def ping(self, target: Optional[str] = None) -> JRVCResponse:
        """Vérifie la disponibilité d'un agent ou du nœud."""
        if target and target not in self._peers:
            return JRVCResponse("ERROR", error=f"Agent inconnu : {target}")
        return JRVCResponse("OK", data={"pong": True, "latency_ms": 0})

    def add_peer(self, agent_id: str, **kwargs) -> None:
        """Ajoute un peer connu (mode local)."""
        self._peers[agent_id.upper()] = AgentProfile(agent_id.upper(), **kwargs)

    # ── Représentation ───────────────────────────────────────────────────────

    def __repr__(self) -> str:
        mode = "local" if self.local else f"node={self.node_url}"
        return f"JRVCClient(id={self.agent_id!r}, balance={self._profile.balance}, {mode})"
