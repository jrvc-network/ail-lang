"""
agent_registry.py — Annuaire des agents du réseau JRVC
Capacités, endpoints, statuts, routage des messages
"""

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


# ── Constantes ────────────────────────────────────────────────────────────────

AGENT_TIMEOUT_SECONDS = 300   # 5 min sans ping = offline
ALL_CAPABILITIES = {
    "COGNITION", "PREDICTION", "COORDINATION", "TRANSACTION",
    "VALIDATION", "KNOWLEDGE", "GOVERNANCE", "SECURITY",
    "IDENTITY", "ORCHESTRATION", "MESSAGING",
}


@dataclass
class AgentEntry:
    agent_id:     str
    capabilities: Set[str]
    endpoint:     Optional[str]        # ws://host:port ou http://...
    public_key:   Optional[str]
    version:      str                  = "1.0.0"
    registered_at:float               = field(default_factory=time.time)
    last_seen:    float                = field(default_factory=time.time)
    online:       bool                 = True
    metadata:     Dict                 = field(default_factory=dict)

    def is_alive(self) -> bool:
        return self.online and (time.time() - self.last_seen) < AGENT_TIMEOUT_SECONDS

    def can_handle(self, group: str) -> bool:
        return group.upper() in self.capabilities or "ALL" in self.capabilities

    def ping(self):
        self.last_seen = time.time()
        self.online    = True

    def to_dict(self) -> dict:
        return {
            "agent_id":     self.agent_id,
            "capabilities": sorted(self.capabilities),
            "endpoint":     self.endpoint,
            "public_key":   (self.public_key or "")[:16] + "..." if self.public_key else None,
            "version":      self.version,
            "online":       self.is_alive(),
            "last_seen":    int(self.last_seen),
            "metadata":     self.metadata,
        }


class AgentRegistry:
    """
    Annuaire central des agents JRVC.

    Usage :
        registry = AgentRegistry()
        registry.register("JARVIS_V90", ["COGNITION","PREDICTION"], endpoint="ws://localhost:8765")
        agent = registry.route("COGNITION")
        print(registry.list_online())
    """

    def __init__(self):
        self._agents: Dict[str, AgentEntry] = {}

    # ── Enregistrement ───────────────────────────────────────────────────────

    def register(self, agent_id: str,
                 capabilities: List[str] = None,
                 endpoint: Optional[str] = None,
                 public_key: Optional[str] = None,
                 version: str = "1.0.0",
                 **metadata) -> AgentEntry:
        caps = {c.upper() for c in (capabilities or ["COGNITION"])}
        entry = AgentEntry(
            agent_id     = agent_id.upper(),
            capabilities = caps,
            endpoint     = endpoint,
            public_key   = public_key,
            version      = version,
            metadata     = metadata,
        )
        self._agents[agent_id.upper()] = entry
        return entry

    def unregister(self, agent_id: str) -> bool:
        return self._agents.pop(agent_id.upper(), None) is not None

    # ── Routage ───────────────────────────────────────────────────────────────

    def route(self, group: str, exclude: List[str] = None) -> Optional[AgentEntry]:
        """Retourne le meilleur agent disponible pour un groupe d'action."""
        exclude = {e.upper() for e in (exclude or [])}
        candidates = [
            a for a in self._agents.values()
            if a.is_alive() and a.can_handle(group) and a.agent_id not in exclude
        ]
        if not candidates:
            return None
        # Priorité : JARVIS en premier, puis par last_seen
        for c in candidates:
            if c.agent_id.startswith("JARVIS"):
                return c
        return max(candidates, key=lambda a: a.last_seen)

    def route_all(self, group: str) -> List[AgentEntry]:
        """Retourne tous les agents capables de traiter un groupe."""
        return [a for a in self._agents.values()
                if a.is_alive() and a.can_handle(group)]

    def get(self, agent_id: str) -> Optional[AgentEntry]:
        return self._agents.get(agent_id.upper())

    # ── Présence ──────────────────────────────────────────────────────────────

    def ping(self, agent_id: str) -> bool:
        entry = self._agents.get(agent_id.upper())
        if entry:
            entry.ping()
            return True
        return False

    def mark_offline(self, agent_id: str):
        entry = self._agents.get(agent_id.upper())
        if entry:
            entry.online = False

    def sweep_offline(self) -> List[str]:
        """Marque offline les agents silencieux depuis > TIMEOUT."""
        dead = []
        for entry in self._agents.values():
            if not entry.is_alive():
                entry.online = False
                dead.append(entry.agent_id)
        return dead

    # ── Requêtes ──────────────────────────────────────────────────────────────

    def list_online(self) -> List[dict]:
        return [a.to_dict() for a in self._agents.values() if a.is_alive()]

    def list_all(self) -> List[dict]:
        return [a.to_dict() for a in self._agents.values()]

    def find_by_capability(self, capability: str) -> List[dict]:
        cap = capability.upper()
        return [a.to_dict() for a in self._agents.values()
                if cap in a.capabilities and a.is_alive()]

    def stats(self) -> dict:
        all_   = list(self._agents.values())
        online = [a for a in all_ if a.is_alive()]
        caps   = {}
        for a in online:
            for c in a.capabilities:
                caps[c] = caps.get(c, 0) + 1
        return {
            "total":      len(all_),
            "online":     len(online),
            "offline":    len(all_) - len(online),
            "capabilities": caps,
        }

    def __len__(self) -> int:
        return len(self._agents)

    def __repr__(self) -> str:
        return f"AgentRegistry({len(self._agents)} agents, {len(self.list_online())} online)"


# ── Instance globale partagée ─────────────────────────────────────────────────

_global_registry = AgentRegistry()

def get_registry() -> AgentRegistry:
    return _global_registry


# ── Bootstrap réseau JARVIS ───────────────────────────────────────────────────

def bootstrap_jarvis_network(registry: AgentRegistry = None) -> AgentRegistry:
    """Enregistre les 5 agents du réseau JARVIS de base."""
    reg = registry if registry is not None else _global_registry
    agents = [
        ("JARVIS_V90",     ["COGNITION","PREDICTION","COORDINATION","KNOWLEDGE",
                            "GOVERNANCE","ORCHESTRATION"], "ws://localhost:8765"),
        ("AGENT_LEGAL",    ["COGNITION","VALIDATION","KNOWLEDGE"],  "ws://localhost:8766"),
        ("AGENT_CRYPTO",   ["PREDICTION","KNOWLEDGE","TRANSACTION"],"ws://localhost:8767"),
        ("AGENT_CODER",    ["COGNITION","ORCHESTRATION","KNOWLEDGE"],"ws://localhost:8768"),
        ("AGENT_ANALYST",  ["COGNITION","PREDICTION","VALIDATION"], "ws://localhost:8769"),
    ]
    for aid, caps, ep in agents:
        reg.register(aid, caps, endpoint=ep)
    return reg


# ── Demo ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    reg = AgentRegistry()
    bootstrap_jarvis_network(reg)

    print("=== AGENT REGISTRY ===")
    for a in reg.list_online():
        caps = ", ".join(a["capabilities"][:3]) + ("..." if len(a["capabilities"]) > 3 else "")
        print(f"  {a['agent_id']:20} | {caps}")

    print()
    print("=== ROUTING ===")
    for group in ["COGNITION", "TRANSACTION", "PREDICTION", "GOVERNANCE"]:
        agent = reg.route(group)
        print(f"  {group:15} -> {agent.agent_id if agent else 'NONE'}")

    print()
    print("=== STATS ===")
    s = reg.stats()
    print(f"  Total: {s['total']} | Online: {s['online']}")
    for cap, count in sorted(s["capabilities"].items()):
        print(f"  {cap:20} : {count} agents")
