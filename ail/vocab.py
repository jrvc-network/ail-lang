"""
vocab.py — Vocabulaire officiel AIL v1.0
100 commandes dans 7 groupes — RFC-AIL-001
"""

from typing import Dict, List, NamedTuple


class ActionInfo(NamedTuple):
    group:       str
    description: str
    required:    List[str]   # Paramètres obligatoires
    optional:    List[str]   # Paramètres optionnels
    burns_token: bool        # Si True : génère un burn $JRVC


VOCABULARY: Dict[str, ActionInfo] = {

    # ── GROUPE A — COGNITION ──────────────────────────────
    "ANALYZE":    ActionInfo("COGNITION",    "Analyser un objet",
                             ["DOMAIN"],     ["DEPTH","PRECISION","ASYNC"], False),
    "SYNTHESIZE": ActionInfo("COGNITION",    "Synthétiser plusieurs sources",
                             ["SOURCES"],    ["OUTPUT","FORMAT"],           False),
    "EVALUATE":   ActionInfo("COGNITION",    "Évaluer selon des critères",
                             ["CRITERIA"],   ["SCALE","CONFIDENCE"],        False),
    "CLASSIFY":   ActionInfo("COGNITION",    "Classer dans une taxonomie",
                             ["TAXONOMY"],   ["CONFIDENCE","DEPTH"],        False),
    "COMPARE":    ActionInfo("COGNITION",    "Comparer deux objets",
                             ["WITH"],       ["CRITERIA","OUTPUT"],         False),
    "EXTRACT":    ActionInfo("COGNITION",    "Extraire des champs",
                             ["FIELDS"],     ["FORMAT","FILTER"],           False),
    "SUMMARIZE":  ActionInfo("COGNITION",    "Résumer un contenu",
                             [],             ["LENGTH","LANGUAGE"],         False),
    "INFER":      ActionInfo("COGNITION",    "Déduire une conclusion",
                             [],             ["CONFIDENCE","METHOD"],       False),
    "REASON":     ActionInfo("COGNITION",    "Raisonner étape par étape",
                             [],             ["STEPS","METHOD"],            False),
    "CRITIQUE":   ActionInfo("COGNITION",    "Critiquer sous plusieurs angles",
                             [],             ["ANGLE","DEPTH"],             False),
    "VERIFY":     ActionInfo("COGNITION",    "Vérifier l'exactitude",
                             [],             ["SOURCES","CONFIDENCE"],      False),
    "DECOMPOSE":  ActionInfo("COGNITION",    "Décomposer un problème",
                             [],             ["PARTS","METHOD"],            False),
    "ABSTRACT":   ActionInfo("COGNITION",    "Abstraire à un niveau",
                             [],             ["LEVEL"],                     False),
    "GENERALIZE": ActionInfo("COGNITION",    "Généraliser depuis des exemples",
                             [],             ["CONFIDENCE"],                False),

    # ── GROUPE B — PRÉDICTION ─────────────────────────────
    "PREDICT":    ActionInfo("PREDICTION",   "Prédire l'évolution",
                             ["HORIZON"],    ["CONFIDENCE","METHOD"],       False),
    "FORECAST":   ActionInfo("PREDICTION",   "Projeter une métrique",
                             ["PERIOD"],     ["MODEL","GRANULARITY"],       False),
    "SIMULATE":   ActionInfo("PREDICTION",   "Simuler un scénario",
                             ["VARIABLES"],  ["RUNS","OUTPUT"],             False),
    "EXTRAPOLATE":ActionInfo("PREDICTION",   "Extrapoler une tendance",
                             ["FROM","TO"],  ["METHOD"],                    False),
    "BACKTEST":   ActionInfo("PREDICTION",   "Tester sur données historiques",
                             ["PERIOD"],     ["DATASET","METRICS"],         False),
    "SCENARIO":   ActionInfo("PREDICTION",   "Définir un scénario probabiliste",
                             ["TYPE","PROBABILITY"], ["HORIZON"],           False),
    "ALERT":      ActionInfo("PREDICTION",   "Déclencher une alerte",
                             ["CONDITION","THRESHOLD"], ["ACTION"],         False),
    "MONITOR":    ActionInfo("PREDICTION",   "Surveiller une métrique",
                             ["METRIC","INTERVAL"], ["THRESHOLD"],          False),
    "TREND":      ActionInfo("PREDICTION",   "Analyser une tendance",
                             ["PERIOD"],     ["GRANULARITY"],               False),
    "DETECT":     ActionInfo("PREDICTION",   "Détecter des anomalies",
                             ["SENSITIVITY"],["DATASET"],                   False),

    # ── GROUPE C — COMMUNICATION ──────────────────────────
    "DELEGATE":   ActionInfo("COORDINATION", "Déléguer une tâche",
                             ["AGENT"],      ["PRIORITY","TOKENS","TIMEOUT"],True),
    "COLLABORATE":ActionInfo("COORDINATION", "Collaboration multi-agents",
                             ["AGENTS"],     ["ROLE","PROJECT"],            True),
    "BROADCAST":  ActionInfo("COORDINATION", "Diffuser à tout le réseau",
                             [],             ["PRIORITY","FILTER"],         True),
    "REQUEST":    ActionInfo("COORDINATION", "Demander un service",
                             ["FROM"],       ["PARAMS","TIMEOUT"],          False),
    "RESPOND":    ActionInfo("COORDINATION", "Répondre à une requête",
                             ["REQUEST_ID","STATUS"], [],                   False),
    "HANDOFF":    ActionInfo("COORDINATION", "Transférer une responsabilité",
                             ["TO"],         ["CONTEXT","PRIORITY"],        False),
    "NOTIFY":     ActionInfo("COORDINATION", "Notifier un agent",
                             ["EVENT"],      ["DATA","PRIORITY"],           False),
    "QUERY":      ActionInfo("COORDINATION", "Interroger un agent",
                             ["FIELD"],      ["FILTER"],                    False),
    "PING":       ActionInfo("COORDINATION", "Vérifier disponibilité",
                             [],             ["TIMEOUT"],                   False),
    "SUBSCRIBE":  ActionInfo("COORDINATION", "S'abonner aux événements",
                             ["FROM","EVENT"],["CALLBACK"],                 False),
    "RELAY":      ActionInfo("COORDINATION", "Relayer un message",
                             ["FROM","TO"],  [],                            False),
    "MERGE":      ActionInfo("COORDINATION", "Fusionner des résultats",
                             ["FROM"],       ["METHOD"],                    False),
    "CHAIN":      ActionInfo("COORDINATION", "Enchaîner des tâches",
                             ["SEQUENCE"],   ["ON_FAIL"],                   False),
    "PARALLEL":   ActionInfo("COORDINATION", "Tâches en parallèle",
                             ["TASKS","AGENTS"], ["SYNC"],                  False),

    # ── GROUPE D — TRANSACTIONS $JRVC ────────────────────
    "TRANSFER":   ActionInfo("TRANSACTION",  "Transférer des tokens",
                             ["AMOUNT","FROM","TO"], ["MEMO"],              True),
    "STAKE":      ActionInfo("TRANSACTION",  "Staker des tokens",
                             ["AMOUNT"],     ["DURATION","PURPOSE"],        True),
    "UNSTAKE":    ActionInfo("TRANSACTION",  "Débloquer des tokens",
                             ["AMOUNT"],     ["STAKE_ID"],                  True),
    "REWARD":     ActionInfo("TRANSACTION",  "Récompenser un agent",
                             ["AGENT","AMOUNT"], ["REASON"],                True),
    "BURN":       ActionInfo("TRANSACTION",  "Brûler des tokens",
                             ["AMOUNT"],     ["REASON"],                    True),
    "MINT":       ActionInfo("TRANSACTION",  "Émettre des tokens",
                             ["AMOUNT"],     ["PROOF"],                     True),
    "ESCROW":     ActionInfo("TRANSACTION",  "Bloquer avec condition",
                             ["AMOUNT","CONDITION"], ["RELEASE_TO"],        True),
    "BID":        ActionInfo("TRANSACTION",  "Offre pour une tâche",
                             ["TASK","AMOUNT"], ["SLA"],                    True),
    "PAY":        ActionInfo("TRANSACTION",  "Payer une facture",
                             ["INVOICE_ID"], ["TOKENS"],                    True),
    "SPLIT":      ActionInfo("TRANSACTION",  "Répartir un paiement",
                             ["AMOUNT","RECIPIENTS"], [],                   True),

    # ── GROUPE E — VALIDATION ─────────────────────────────
    "VALIDATE":   ActionInfo("VALIDATION",   "Valider la conformité",
                             [],             ["RULES","STRICT"],            False),
    "AUDIT":      ActionInfo("VALIDATION",   "Auditer un système",
                             [],             ["SCOPE","DEPTH"],             False),
    "CERTIFY":    ActionInfo("VALIDATION",   "Certifier un objet",
                             ["STANDARD"],   ["EXPIRY"],                    True),
    "APPROVE":    ActionInfo("VALIDATION",   "Approuver une demande",
                             ["REQUEST_ID"], ["CONDITIONS"],                False),
    "REJECT":     ActionInfo("VALIDATION",   "Rejeter une demande",
                             ["REQUEST_ID","REASON"], [],                   False),
    "SCORE":      ActionInfo("VALIDATION",   "Scorer selon critères",
                             ["CRITERIA"],   ["SCALE"],                     False),
    "BENCHMARK":  ActionInfo("VALIDATION",   "Benchmarker un agent",
                             ["TASKS"],      ["BASELINE"],                  False),
    "CALIBRATE":  ActionInfo("VALIDATION",   "Calibrer un modèle",
                             ["DATASET"],    ["TARGET"],                    False),
    "GRADE":      ActionInfo("VALIDATION",   "Noter un output",
                             ["RUBRIC"],     ["SCALE"],                     False),
    "DISPUTE":    ActionInfo("VALIDATION",   "Contester une transaction",
                             ["TX_ID","REASON"], ["EVIDENCE"],              True),

    # ── GROUPE F — CONNAISSANCE ───────────────────────────
    "STORE":      ActionInfo("KNOWLEDGE",    "Stocker une connaissance",
                             ["DOMAIN"],     ["KEY","TTL"],                 True),
    "RETRIEVE":   ActionInfo("KNOWLEDGE",    "Récupérer une connaissance",
                             ["KEY"],        ["DOMAIN"],                    True),
    "INDEX":      ActionInfo("KNOWLEDGE",    "Indexer un contenu",
                             [],             ["TAGS","SEARCHABLE"],         False),
    "SEARCH":     ActionInfo("KNOWLEDGE",    "Rechercher dans la base",
                             ["QUERY"],      ["DOMAIN","LIMIT","SORT"],     True),
    "CITE":       ActionInfo("KNOWLEDGE",    "Citer une source",
                             [],             ["URL","CONFIDENCE"],          False),
    "LEARN":      ActionInfo("KNOWLEDGE",    "Apprendre d'un feedback",
                             ["TASK_ID","SCORE"], [],                       False),
    "FORGET":     ActionInfo("KNOWLEDGE",    "Supprimer une connaissance",
                             ["KEY"],        ["DOMAIN","REASON"],           False),
    "UPDATE":     ActionInfo("KNOWLEDGE",    "Mettre à jour une connaissance",
                             ["KEY","NEW_VALUE"], [],                       False),
    "SHARE":      ActionInfo("KNOWLEDGE",    "Partager avec d'autres agents",
                             ["WITH"],       ["ACCESS"],                    True),
    "EMBED":      ActionInfo("KNOWLEDGE",    "Créer un embedding vectoriel",
                             [],             ["MODEL","DIMENSIONS"],        False),

    # ── GROUPE G — GOUVERNANCE & SÉCURITÉ ─────────────────
    "VOTE":       ActionInfo("GOVERNANCE",   "Voter sur une proposition",
                             ["PROPOSAL_ID","CHOICE"], ["WEIGHT","REASON"], True),
    "PROPOSE":    ActionInfo("GOVERNANCE",   "Soumettre une proposition",
                             ["TYPE","DESCRIPTION"], ["QUORUM"],            True),
    "VETO":       ActionInfo("GOVERNANCE",   "Opposer un veto",
                             ["PROPOSAL_ID","REASON"], ["AUTHORITY"],       True),
    "EXECUTE":    ActionInfo("GOVERNANCE",   "Exécuter une décision",
                             ["PROPOSAL_ID"], [],                           False),
    "REGISTER":   ActionInfo("GOVERNANCE",   "Enregistrer un agent",
                             ["IDENTITY"],   ["CAPABILITIES"],              True),
    "UNREGISTER": ActionInfo("GOVERNANCE",   "Retirer un agent",
                             ["REASON"],     ["EVIDENCE"],                  True),
    "BAN":        ActionInfo("GOVERNANCE",   "Bannir un agent malveillant",
                             ["DURATION","REASON"], ["EVIDENCE"],           True),
    "SIGN":       ActionInfo("SECURITY",     "Signer un message",
                             [],             ["ALGORITHM","KEY_ID"],        False),
    "VERIFY_SIG": ActionInfo("SECURITY",     "Vérifier une signature",
                             ["SIGNATURE","PUBLIC_KEY"], [],                False),
    "ENCRYPT":    ActionInfo("SECURITY",     "Chiffrer un payload",
                             [],             ["ALGORITHM","KEY"],           False),

    # ── GROUPE G (suite) — SÉCURITÉ ──────────────────────
    "DECRYPT":    ActionInfo("SECURITY",     "Déchiffrer un payload",
                             [],             ["ALGORITHM","KEY"],           False),
    "HASH":       ActionInfo("SECURITY",     "Hacher un contenu",
                             [],             ["ALGORITHM"],                 False),
    "REVOKE":     ActionInfo("SECURITY",     "Révoquer une clé ou permission",
                             ["TARGET"],     ["REASON"],                    False),
    "AUDIT_LOG":  ActionInfo("SECURITY",     "Journaliser un audit",
                             ["EVENT"],      ["LEVEL","DATA"],              False),

    # ── GROUPE G (suite) — GOUVERNANCE ───────────────────
    "DELEGATE_GOV": ActionInfo("GOVERNANCE", "Déléguer son vote",
                             ["TO"],         ["DURATION","SCOPE"],          True),
    "SNAPSHOT":   ActionInfo("GOVERNANCE",   "Capturer l'état du réseau",
                             [],             ["SCOPE","FORMAT"],            False),
    "UPGRADE":    ActionInfo("GOVERNANCE",   "Proposer une mise à jour",
                             ["VERSION"],    ["MIGRATION","ROLLBACK"],      True),

    # ── GROUPE I — AGENTS & IDENTITÉ ─────────────────────
    "SPAWN":      ActionInfo("IDENTITY",     "Créer un sous-agent",
                             ["ROLE"],       ["CAPABILITIES","BUDGET"],     True),
    "CLONE":      ActionInfo("IDENTITY",     "Cloner un profil agent",
                             ["SOURCE"],     ["MODIFICATIONS"],             True),
    "MERGE_AGENT":ActionInfo("IDENTITY",     "Fusionner deux agents",
                             ["AGENTS"],     ["STRATEGY"],                  True),
    "PAUSE":      ActionInfo("IDENTITY",     "Mettre en pause un agent",
                             ["AGENT_ID"],   ["REASON"],                    False),
    "RESUME":     ActionInfo("IDENTITY",     "Reprendre un agent pausé",
                             ["AGENT_ID"],   [],                            False),
    "STATUS":     ActionInfo("IDENTITY",     "Obtenir le statut d'un agent",
                             [],             ["AGENT_ID","FIELDS"],         False),
    "PROFILE":    ActionInfo("IDENTITY",     "Lire le profil d'un agent",
                             ["AGENT_ID"],   ["FIELDS"],                    False),

    # ── GROUPE J — ORCHESTRATION ─────────────────────────
    "SCHEDULE":   ActionInfo("ORCHESTRATION","Planifier une tâche",
                             ["TASK","AT"],  ["REPEAT","TIMEZONE"],         False),
    "CANCEL":     ActionInfo("ORCHESTRATION","Annuler une tâche planifiée",
                             ["TASK_ID"],    ["REASON"],                    False),
    "RETRY":      ActionInfo("ORCHESTRATION","Réessayer une tâche échouée",
                             ["TASK_ID"],    ["MAX_ATTEMPTS","DELAY"],      False),
    "ROLLBACK":   ActionInfo("ORCHESTRATION","Revenir à un état précédent",
                             ["CHECKPOINT"], ["REASON"],                    False),

    # ── GROUPE J (suite) ─────────────────────────────────
    "CHECKPOINT": ActionInfo("ORCHESTRATION","Sauvegarder un état",
                             [],             ["LABEL","SCOPE"],             False),
    "LOG":        ActionInfo("ORCHESTRATION","Journaliser un événement",
                             ["EVENT"],      ["LEVEL","DATA"],              False),
    "REPORT":     ActionInfo("ORCHESTRATION","Générer un rapport",
                             [],             ["FORMAT","SCOPE","PERIOD"],   False),

    # ── GROUPE H — MESSAGERIE BTR ─────────────────────────
    "MSG":        ActionInfo("MESSAGING",    "Messagerie Burn-to-Read",
                             [],             ["TO","TYPE","TOKENS","EXPIRY"],True),
}

# Alias groupés
ACTIONS = list(VOCABULARY.keys())
GROUPS  = sorted(set(v.group for v in VOCABULARY.values()))


def get_action_info(action: str) -> ActionInfo:
    """Retourne les infos d'une action AIL."""
    if action not in VOCABULARY:
        raise KeyError(f"Action inconnue : {action}. Actions disponibles : {ACTIONS}")
    return VOCABULARY[action]


def list_by_group(group: str):
    """Liste toutes les actions d'un groupe."""
    return {k: v for k, v in VOCABULARY.items() if v.group == group}
