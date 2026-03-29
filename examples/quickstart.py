"""
AIL SDK — Quickstart
====================
Exemples d'utilisation du SDK ail-lang v1.0.0

Run : python examples/quickstart.py
"""

from ail import encode, decode, is_valid, MessageBuilder, AILParser, JRVCClient
from ail.builder import msg_analyze, msg_delegate, msg_transfer, msg_btr


def demo_encode_decode():
    print("=" * 60)
    print("1. ENCODE / DECODE")
    print("=" * 60)

    # Encodage simple
    msg = encode("ANALYZE", "CONTRACT", DOMAIN="LEGAL_CH", PRECISION="0.95")
    print(f"Encoded : {msg}")

    # Décodage
    decoded = decode(msg)
    print(f"Action  : {decoded.action}")
    print(f"Object  : {decoded.object}")
    print(f"Params  : {decoded.params}")
    print(f"Group   : {decoded.group}")
    print(f"Burns?  : {decoded.burns_token}")
    print()


def demo_builder():
    print("=" * 60)
    print("2. MESSAGE BUILDER (API fluente)")
    print("=" * 60)

    # Délégation
    msg = (MessageBuilder("DELEGATE")
           .to("ANALYST_AGENT")
           .param("PRIORITY", "HIGH")
           .param("TOKENS", "50")
           .param("TIMEOUT", "30S")
           .raw())
    print(f"Delegate : {msg}")

    # Transaction BTR
    btr = msg_btr("AGENT_GPT4", type_="URGENT", tokens="100")
    print(f"BTR msg  : {btr}")

    # Transfer JRVC
    tx = msg_transfer("500", "JARVIS_V90", "ANALYST_AGENT", MEMO="Paiement tâche #42")
    print(f"Transfer : {tx}")

    print()


def demo_parser():
    print("=" * 60)
    print("3. PARSER (extraction depuis texte libre)")
    print("=" * 60)

    agent_response = """
    Bonjour, je commence l'analyse.
    [ANALYZE:REPORT|DOMAIN:FINANCE|DEPTH:3]
    Je délègue la partie juridique.
    [DELEGATE:LEGAL_AGENT|PRIORITY:HIGH|TOKENS:20]
    Résultat prêt, je notifie.
    [NOTIFY:TASK_DONE|DATA:REPORT_ID_42|PRIORITY:NORMAL]
    """

    parser = AILParser()
    messages = parser.parse_text(agent_response)
    print(f"Messages extraits : {len(messages)}")
    for m in messages:
        print(f"  {m.action:15} | group={m.group:15} | burns={m.burns_token}")

    print()


def demo_network():
    print("=" * 60)
    print("4. JRVC CLIENT (réseau local)")
    print("=" * 60)

    client = JRVCClient(agent_id="MY_AGENT", balance=1000.0, local=True)
    client.register(capabilities=["COGNITION", "PREDICTION"])
    print(f"Client : {client}")

    # Envoyer une commande gratuite
    resp = client.send("[ANALYZE:MARKET|DOMAIN:CRYPTO|DEPTH:3]")
    print(f"ANALYZE → {resp.status} (tx={resp.tx_id})")

    # Envoyer une commande payante
    resp2 = client.send("[DELEGATE:ANALYST|PRIORITY:HIGH|TOKENS:5]")
    print(f"DELEGATE → {resp2.status} (coût déduit)")
    print(f"Solde restant : {client.balance():.1f} $JRVC")

    # Ping
    pong = client.ping()
    print(f"PING → {pong.data}")

    print()


def demo_validation():
    print("=" * 60)
    print("5. VALIDATION")
    print("=" * 60)

    tests = [
        ("[PING]",                         True),
        ("[ANALYZE:REPORT|DOMAIN:FIN]",    True),
        ("PING",                           False),   # sans crochets
        ("[FOOBAR:SOMETHING]",             False),   # action inconnue
        ("not ail at all",                 False),
    ]

    for msg, expected in tests:
        result = is_valid(msg)
        status = "OK" if result == expected else "FAIL"
        print(f"  [{status}] is_valid({msg!r}) → {result}")

    print()


if __name__ == "__main__":
    print()
    print("=" * 60)
    print("   AIL-LANG SDK v1.0.0 -- JARVIS Network")
    print("   AI Lingua -- Le langage universel inter-IA")
    print("=" * 60)
    print()

    demo_encode_decode()
    demo_builder()
    demo_parser()
    demo_network()
    demo_validation()

    print("Done. Tous les exemples ont été exécutés avec succès.")
