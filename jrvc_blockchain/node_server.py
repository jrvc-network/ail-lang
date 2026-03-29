"""
node_server.py — Noeud JRVC WebSocket (FastAPI)
Permet a 2 agents de se connecter et echanger des messages AIL en temps reel

Lancer : python node_server.py
         python node_server.py --port 8765 --host 0.0.0.0
"""

import asyncio
import json
import sys
import time
import argparse
from typing import Dict, Set

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from fastapi.responses import JSONResponse
    import uvicorn
    FASTAPI_OK = True
except ImportError:
    FASTAPI_OK = False

# Imports locaux
sys.path.insert(0, __file__.rsplit("\\", 1)[0])
from agent_registry import AgentRegistry, bootstrap_jarvis_network

try:
    from ail import decode, is_valid
    from ail.errors import AILSyntaxError, AILActionError
    AIL_OK = True
except ImportError:
    AIL_OK = False


# ── Gestionnaire de connexions WebSocket ──────────────────────────────────────

class ConnectionManager:
    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}   # agent_id -> ws
        self.message_log = []

    async def connect(self, agent_id: str, ws: WebSocket):
        await ws.accept()
        self.connections[agent_id.upper()] = ws
        print(f"[+] {agent_id} connecte ({len(self.connections)} actifs)")

    def disconnect(self, agent_id: str):
        self.connections.pop(agent_id.upper(), None)
        print(f"[-] {agent_id} deconnecte ({len(self.connections)} actifs)")

    async def send_to(self, agent_id: str, message: dict) -> bool:
        ws = self.connections.get(agent_id.upper())
        if ws:
            try:
                await ws.send_json(message)
                return True
            except Exception:
                self.disconnect(agent_id)
        return False

    async def broadcast(self, message: dict, exclude: str = None):
        dead = []
        for aid, ws in list(self.connections.items()):
            if aid == (exclude or "").upper():
                continue
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(aid)
        for aid in dead:
            self.disconnect(aid)

    def online_agents(self):
        return list(self.connections.keys())

    def log(self, entry: dict):
        self.message_log.append({**entry, "ts": int(time.time())})
        if len(self.message_log) > 500:
            self.message_log = self.message_log[-500:]


# ── Application FastAPI ───────────────────────────────────────────────────────

def create_app(registry: AgentRegistry = None) -> "FastAPI":
    if not FASTAPI_OK:
        raise ImportError("pip install fastapi uvicorn")

    app      = FastAPI(title="JRVC Node", version="1.0.0")
    manager  = ConnectionManager()
    registry = registry or bootstrap_jarvis_network()

    # ── REST endpoints ────────────────────────────────────────────────────────

    @app.get("/")
    def root():
        return {
            "node": "JRVC Network Node v1.0.0",
            "agents_online": len(manager.online_agents()),
            "ail_sdk": AIL_OK,
        }

    @app.get("/agents")
    def list_agents():
        return {"agents": registry.list_online()}

    @app.get("/agents/{agent_id}")
    def get_agent(agent_id: str):
        entry = registry.get(agent_id)
        if not entry:
            return JSONResponse({"error": "Agent not found"}, status_code=404)
        return entry.to_dict()

    @app.get("/network/stats")
    def network_stats():
        return {
            **registry.stats(),
            "ws_connections": len(manager.online_agents()),
            "messages_logged": len(manager.message_log),
        }

    @app.get("/messages")
    def recent_messages(limit: int = 20):
        return {"messages": manager.message_log[-limit:]}

    @app.post("/send")
    async def send_message(body: dict):
        """
        Envoie un message AIL via HTTP (sans WebSocket).
        Body: {"from": "AGENT_X", "to": "AGENT_Y", "message": "[AIL...]"}
        """
        raw   = body.get("message", "")
        to    = body.get("to", "")
        from_ = body.get("from", "HTTP_CLIENT")

        if AIL_OK and not is_valid(raw):
            return JSONResponse({"error": "Invalid AIL message"}, status_code=400)

        result = await manager.send_to(to, {
            "type":    "AIL_MESSAGE",
            "from":    from_,
            "message": raw,
            "ts":      int(time.time()),
        })

        manager.log({"from": from_, "to": to, "message": raw, "delivered": result})
        return {"delivered": result, "to": to}

    # ── WebSocket ─────────────────────────────────────────────────────────────

    @app.websocket("/ws/{agent_id}")
    async def websocket_endpoint(ws: WebSocket, agent_id: str):
        await manager.connect(agent_id, ws)
        registry.ping(agent_id)

        # Notifier les autres
        await manager.broadcast({
            "type":  "AGENT_JOINED",
            "agent": agent_id.upper(),
            "ts":    int(time.time()),
        }, exclude=agent_id)

        try:
            while True:
                data = await ws.receive_text()

                # Ping keepalive
                if data == "PING":
                    registry.ping(agent_id)
                    await ws.send_text("PONG")
                    continue

                # Parser le message
                try:
                    payload = json.loads(data)
                except json.JSONDecodeError:
                    # Traiter comme message AIL brut
                    payload = {"type": "AIL_MESSAGE", "message": data, "to": "BROADCAST"}

                msg_type = payload.get("type", "AIL_MESSAGE")
                raw_ail  = payload.get("message", "")
                to       = payload.get("to", "BROADCAST")

                # Valider AIL si disponible
                if AIL_OK and raw_ail and not is_valid(raw_ail):
                    await ws.send_json({
                        "type":  "ERROR",
                        "code":  "E001",
                        "error": f"Invalid AIL: {raw_ail[:50]}"
                    })
                    continue

                # Logger
                manager.log({"from": agent_id, "to": to, "message": raw_ail})

                # Router
                if to.upper() == "BROADCAST":
                    await manager.broadcast({
                        "type":    "AIL_MESSAGE",
                        "from":    agent_id.upper(),
                        "message": raw_ail,
                        "ts":      int(time.time()),
                    }, exclude=agent_id)
                else:
                    delivered = await manager.send_to(to, {
                        "type":    "AIL_MESSAGE",
                        "from":    agent_id.upper(),
                        "message": raw_ail,
                        "ts":      int(time.time()),
                    })
                    if not delivered:
                        await ws.send_json({
                            "type":  "ERROR",
                            "code":  "E003",
                            "error": f"Agent {to} not connected"
                        })

        except WebSocketDisconnect:
            manager.disconnect(agent_id)
            registry.mark_offline(agent_id)
            await manager.broadcast({
                "type":  "AGENT_LEFT",
                "agent": agent_id.upper(),
                "ts":    int(time.time()),
            })

    return app


# ── Point d'entrée ────────────────────────────────────────────────────────────

def main():
    import os
    parser = argparse.ArgumentParser(description="JRVC Network Node")
    parser.add_argument("--host", default=os.getenv("HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", 8765)))
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()

    if not FASTAPI_OK:
        print("ERROR: pip install fastapi uvicorn")
        sys.exit(1)

    app = create_app()
    print(f"JRVC Node starting on ws://{args.host}:{args.port}")
    print(f"REST API : http://{args.host}:{args.port}/docs")
    print(f"AIL SDK  : {AIL_OK}")
    uvicorn.run(app, host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
