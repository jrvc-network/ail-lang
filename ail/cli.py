"""
cli.py — Interface ligne de commande AIL
Usage : python -m ail [commande] [args]
        ail encode ANALYZE CONTRACT DOMAIN=LEGAL_CH
        ail decode "[ANALYZE:CONTRACT|DOMAIN:LEGAL_CH]"
        ail validate "[PING]"
        ail vocab [groupe]
        ail send --to AGENT_X --node ws://localhost:8765 "[ANALYZE:REPORT]"
"""

import sys
import json
import argparse


def cmd_encode(args):
    from ail import encode
    from ail.errors import AILActionError
    try:
        params = {}
        for p in args.params:
            if "=" in p:
                k, v = p.split("=", 1)
                params[k.upper()] = v
        result = encode(args.action, args.object or None, **params)
        print(result)
    except AILActionError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_decode(args):
    from ail import decode
    from ail.errors import AILSyntaxError, AILActionError
    try:
        msg = decode(args.message)
        if args.json:
            print(json.dumps(msg.to_dict(), indent=2))
        else:
            print(f"ACTION  : {msg.action}")
            print(f"OBJECT  : {msg.object or '(none)'}")
            print(f"GROUP   : {msg.group}")
            print(f"BURNS   : {msg.burns_token}")
            if msg.params:
                print("PARAMS  :")
                for k, v in msg.params.items():
                    print(f"  {k:15} = {v}")
    except (AILSyntaxError, AILActionError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_validate(args):
    from ail import is_valid
    messages = args.messages
    all_ok = True
    for msg in messages:
        ok = is_valid(msg)
        status = "VALID  " if ok else "INVALID"
        print(f"[{status}] {msg}")
        if not ok:
            all_ok = False
    sys.exit(0 if all_ok else 1)


def cmd_vocab(args):
    from ail.vocab import VOCABULARY, list_by_group, GROUPS
    group = args.group.upper() if args.group else None

    if args.list_groups:
        print("Groups:")
        for g in GROUPS:
            count = len(list_by_group(g))
            print(f"  {g:20} ({count} actions)")
        return

    actions = list_by_group(group) if group else VOCABULARY
    if group and not actions:
        print(f"Unknown group: {group}")
        print(f"Available: {', '.join(GROUPS)}")
        sys.exit(1)

    for name, info in actions.items():
        req = ", ".join(info.required) or "-"
        opt = ", ".join(info.optional) or "-"
        burn = "[BURN]" if info.burns_token else "      "
        print(f"  {burn} {name:15} | req={req:30} | opt={opt}")


def cmd_hash(args):
    from ail.crypto import message_hash
    print(message_hash(args.message))


def cmd_sign(args):
    from ail.crypto import AILKeyPair, sign_message
    kp = AILKeyPair.generate()
    signed = sign_message(args.message, args.agent, kp)
    print(f"WIRE    : {signed.to_wire()}")
    print(f"PUBKEY  : {kp.public_key_b64[:32]}...")


def cmd_send(args):
    """Envoie un message AIL a un noeud WebSocket."""
    try:
        import asyncio
        import websockets
    except ImportError:
        print("ERROR: pip install websockets", file=sys.stderr)
        sys.exit(1)

    from ail import is_valid
    if not is_valid(args.message):
        print(f"ERROR: Invalid AIL message: {args.message}", file=sys.stderr)
        sys.exit(1)

    async def _send():
        node = args.node or "ws://127.0.0.1:8765"
        agent = args.agent or "CLI_AGENT"
        url = f"{node}/ws/{agent}"
        try:
            async with websockets.connect(url) as ws:
                payload = json.dumps({
                    "type":    "AIL_MESSAGE",
                    "message": args.message,
                    "to":      args.to or "BROADCAST",
                })
                await ws.send(payload)
                response = await asyncio.wait_for(ws.recv(), timeout=5)
                print(f"SENT    : {args.message}")
                print(f"RESPONSE: {response}")
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)

    asyncio.run(_send())


# ── Parser principal ──────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ail",
        description="AI Lingua CLI v1.0.0 — JRVC Network"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # encode
    p = sub.add_parser("encode", help="Encode an AIL message")
    p.add_argument("action",          help="AIL action (e.g. ANALYZE)")
    p.add_argument("object", nargs="?",help="Object (e.g. CONTRACT)")
    p.add_argument("params", nargs="*",help="KEY=VALUE params")

    # decode
    p = sub.add_parser("decode", help="Decode an AIL message")
    p.add_argument("message",         help="AIL message string")
    p.add_argument("--json", action="store_true", help="Output as JSON")

    # validate
    p = sub.add_parser("validate", help="Validate AIL message(s)")
    p.add_argument("messages", nargs="+", help="AIL message(s) to validate")

    # vocab
    p = sub.add_parser("vocab", help="Browse AIL vocabulary")
    p.add_argument("group",  nargs="?",  help="Filter by group")
    p.add_argument("--list-groups", action="store_true", help="List all groups")

    # hash
    p = sub.add_parser("hash", help="Hash an AIL message (SHA-256)")
    p.add_argument("message")

    # sign
    p = sub.add_parser("sign", help="Sign an AIL message")
    p.add_argument("message")
    p.add_argument("--agent", default="CLI_AGENT")

    # send
    p = sub.add_parser("send", help="Send AIL message to a JRVC node")
    p.add_argument("message",           help="AIL message to send")
    p.add_argument("--to",              help="Target agent ID")
    p.add_argument("--node",            help="Node URL (ws://host:port)")
    p.add_argument("--agent",           help="Your agent ID")

    return parser


def main():
    parser = build_parser()
    args   = parser.parse_args()

    dispatch = {
        "encode":   cmd_encode,
        "decode":   cmd_decode,
        "validate": cmd_validate,
        "vocab":    cmd_vocab,
        "hash":     cmd_hash,
        "sign":     cmd_sign,
        "send":     cmd_send,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
