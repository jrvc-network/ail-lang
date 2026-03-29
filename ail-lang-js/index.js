/**
 * ail-lang — AI Lingua SDK JavaScript v1.0.0
 * Le premier langage universel inter-IA
 * Standard CC0 — JRVC Network — 2026
 *
 * npm install ail-lang
 * const { encode, decode, isValid, MessageBuilder } = require('ail-lang')
 */

'use strict';

// ── Vocabulaire (100 actions) ─────────────────────────────────────────────────

const VOCABULARY = {
  // COGNITION
  ANALYZE:    { group:'COGNITION',    required:['DOMAIN'],   burns:false },
  SYNTHESIZE: { group:'COGNITION',    required:['SOURCES'],  burns:false },
  EVALUATE:   { group:'COGNITION',    required:['CRITERIA'], burns:false },
  CLASSIFY:   { group:'COGNITION',    required:['TAXONOMY'], burns:false },
  COMPARE:    { group:'COGNITION',    required:['WITH'],     burns:false },
  EXTRACT:    { group:'COGNITION',    required:['FIELDS'],   burns:false },
  SUMMARIZE:  { group:'COGNITION',    required:[],           burns:false },
  INFER:      { group:'COGNITION',    required:[],           burns:false },
  REASON:     { group:'COGNITION',    required:[],           burns:false },
  CRITIQUE:   { group:'COGNITION',    required:[],           burns:false },
  VERIFY:     { group:'COGNITION',    required:[],           burns:false },
  DECOMPOSE:  { group:'COGNITION',    required:[],           burns:false },
  ABSTRACT:   { group:'COGNITION',    required:[],           burns:false },
  GENERALIZE: { group:'COGNITION',    required:[],           burns:false },
  // PREDICTION
  PREDICT:    { group:'PREDICTION',   required:['HORIZON'],  burns:false },
  FORECAST:   { group:'PREDICTION',   required:['PERIOD'],   burns:false },
  SIMULATE:   { group:'PREDICTION',   required:['VARIABLES'],burns:false },
  EXTRAPOLATE:{ group:'PREDICTION',   required:['FROM','TO'],burns:false },
  BACKTEST:   { group:'PREDICTION',   required:['PERIOD'],   burns:false },
  SCENARIO:   { group:'PREDICTION',   required:['TYPE','PROBABILITY'], burns:false },
  ALERT:      { group:'PREDICTION',   required:['CONDITION','THRESHOLD'], burns:false },
  MONITOR:    { group:'PREDICTION',   required:['METRIC','INTERVAL'], burns:false },
  TREND:      { group:'PREDICTION',   required:['PERIOD'],   burns:false },
  DETECT:     { group:'PREDICTION',   required:['SENSITIVITY'], burns:false },
  // COORDINATION
  DELEGATE:   { group:'COORDINATION', required:['AGENT'],    burns:true  },
  COLLABORATE:{ group:'COORDINATION', required:['AGENTS'],   burns:true  },
  BROADCAST:  { group:'COORDINATION', required:[],           burns:true  },
  REQUEST:    { group:'COORDINATION', required:['FROM'],     burns:false },
  RESPOND:    { group:'COORDINATION', required:['REQUEST_ID','STATUS'], burns:false },
  HANDOFF:    { group:'COORDINATION', required:['TO'],       burns:false },
  NOTIFY:     { group:'COORDINATION', required:['EVENT'],    burns:false },
  QUERY:      { group:'COORDINATION', required:['FIELD'],    burns:false },
  PING:       { group:'COORDINATION', required:[],           burns:false },
  SUBSCRIBE:  { group:'COORDINATION', required:['FROM','EVENT'], burns:false },
  RELAY:      { group:'COORDINATION', required:['FROM','TO'],burns:false },
  MERGE:      { group:'COORDINATION', required:['FROM'],     burns:false },
  CHAIN:      { group:'COORDINATION', required:['SEQUENCE'], burns:false },
  PARALLEL:   { group:'COORDINATION', required:['TASKS','AGENTS'], burns:false },
  // TRANSACTION
  TRANSFER:   { group:'TRANSACTION',  required:['AMOUNT','FROM','TO'], burns:true },
  STAKE:      { group:'TRANSACTION',  required:['AMOUNT'],   burns:true  },
  UNSTAKE:    { group:'TRANSACTION',  required:['AMOUNT'],   burns:true  },
  REWARD:     { group:'TRANSACTION',  required:['AGENT','AMOUNT'], burns:true },
  BURN:       { group:'TRANSACTION',  required:['AMOUNT'],   burns:true  },
  MINT:       { group:'TRANSACTION',  required:['AMOUNT'],   burns:true  },
  ESCROW:     { group:'TRANSACTION',  required:['AMOUNT','CONDITION'], burns:true },
  BID:        { group:'TRANSACTION',  required:['TASK','AMOUNT'], burns:true },
  PAY:        { group:'TRANSACTION',  required:['INVOICE_ID'], burns:true },
  SPLIT:      { group:'TRANSACTION',  required:['AMOUNT','RECIPIENTS'], burns:true },
  // VALIDATION
  VALIDATE:   { group:'VALIDATION',   required:[],           burns:false },
  AUDIT:      { group:'VALIDATION',   required:[],           burns:false },
  CERTIFY:    { group:'VALIDATION',   required:['STANDARD'], burns:true  },
  APPROVE:    { group:'VALIDATION',   required:['REQUEST_ID'], burns:false },
  REJECT:     { group:'VALIDATION',   required:['REQUEST_ID','REASON'], burns:false },
  SCORE:      { group:'VALIDATION',   required:['CRITERIA'], burns:false },
  BENCHMARK:  { group:'VALIDATION',   required:['TASKS'],    burns:false },
  CALIBRATE:  { group:'VALIDATION',   required:['DATASET'],  burns:false },
  GRADE:      { group:'VALIDATION',   required:['RUBRIC'],   burns:false },
  DISPUTE:    { group:'VALIDATION',   required:['TX_ID','REASON'], burns:true },
  // KNOWLEDGE
  STORE:      { group:'KNOWLEDGE',    required:['DOMAIN'],   burns:true  },
  RETRIEVE:   { group:'KNOWLEDGE',    required:['KEY'],      burns:true  },
  INDEX:      { group:'KNOWLEDGE',    required:[],           burns:false },
  SEARCH:     { group:'KNOWLEDGE',    required:['QUERY'],    burns:true  },
  CITE:       { group:'KNOWLEDGE',    required:[],           burns:false },
  LEARN:      { group:'KNOWLEDGE',    required:['TASK_ID','SCORE'], burns:false },
  FORGET:     { group:'KNOWLEDGE',    required:['KEY'],      burns:false },
  UPDATE:     { group:'KNOWLEDGE',    required:['KEY','NEW_VALUE'], burns:false },
  SHARE:      { group:'KNOWLEDGE',    required:['WITH'],     burns:true  },
  EMBED:      { group:'KNOWLEDGE',    required:[],           burns:false },
  // GOVERNANCE
  VOTE:       { group:'GOVERNANCE',   required:['PROPOSAL_ID','CHOICE'], burns:true },
  PROPOSE:    { group:'GOVERNANCE',   required:['TYPE','DESCRIPTION'], burns:true },
  VETO:       { group:'GOVERNANCE',   required:['PROPOSAL_ID','REASON'], burns:true },
  EXECUTE:    { group:'GOVERNANCE',   required:['PROPOSAL_ID'], burns:false },
  REGISTER:   { group:'GOVERNANCE',   required:['IDENTITY'], burns:true  },
  UNREGISTER: { group:'GOVERNANCE',   required:['REASON'],   burns:true  },
  BAN:        { group:'GOVERNANCE',   required:['DURATION','REASON'], burns:true },
  // SECURITY
  SIGN:       { group:'SECURITY',     required:[],           burns:false },
  VERIFY_SIG: { group:'SECURITY',     required:['SIGNATURE','PUBLIC_KEY'], burns:false },
  ENCRYPT:    { group:'SECURITY',     required:[],           burns:false },
  DECRYPT:    { group:'SECURITY',     required:[],           burns:false },
  HASH:       { group:'SECURITY',     required:[],           burns:false },
  REVOKE:     { group:'SECURITY',     required:['TARGET'],   burns:false },
  AUDIT_LOG:  { group:'SECURITY',     required:['EVENT'],    burns:false },
  // MESSAGING
  MSG:        { group:'MESSAGING',    required:[],           burns:true  },
};

const AIL_REGEX = /^\[([A-Z_]+)(?::([^\|\]]+))?(\|[^\]]+)?\]$/;
const PARAM_REGEX = /\|([A-Z_]+):([^\|\]]+)/g;

// ── Erreurs ────────────────────────────────────────────────────────────────────

class AILError extends Error {
  constructor(code, message, details = '') {
    super(`[AIL ${code}] ${message}${details ? ' — ' + details : ''}`);
    this.code    = code;
    this.ailMsg  = message;
    this.details = details;
  }
}
class AILSyntaxError  extends AILError { constructor(m, d) { super('E001', m, d); } }
class AILActionError  extends AILError { constructor(m, d) { super('E002', m, d); } }

// ── AILMessage ─────────────────────────────────────────────────────────────────

class AILMessage {
  constructor(action, object, params, raw) {
    this.action = action;
    this.object = object || null;
    this.params = params || {};
    this.raw    = raw   || '';
  }

  get group()      { return VOCABULARY[this.action]?.group || 'UNKNOWN'; }
  get burnsToken() { return VOCABULARY[this.action]?.burns || false; }

  get(key, defaultVal = null) { return this.params[key] ?? defaultVal; }
  has(key)   { return key in this.params; }
  toDict()   { return { ACTION: this.action, OBJECT: this.object, ...this.params }; }
  toString() { return encode(this.action, this.object, this.params); }
}

// ── encode ─────────────────────────────────────────────────────────────────────

function encode(action, object = null, params = {}) {
  action = action.toUpperCase();
  if (!VOCABULARY[action]) throw new AILActionError(`Action inconnue: ${action}`);
  const parts = [object ? `${action}:${object}` : action];
  for (const [k, v] of Object.entries(params)) {
    parts.push(`${k.toUpperCase()}:${v}`);
  }
  return '[' + parts.join('|') + ']';
}

// ── decode ─────────────────────────────────────────────────────────────────────

function decode(message) {
  message = message.trim();
  const m = AIL_REGEX.exec(message);
  if (!m) throw new AILSyntaxError('Format AIL invalide', message.substring(0, 50));
  const action = m[1];
  if (!VOCABULARY[action]) throw new AILActionError(`Action inconnue: ${action}`);
  const params = {};
  for (const [, k, v] of (m[3] || '').matchAll(PARAM_REGEX)) params[k] = v;
  return new AILMessage(action, m[2] || null, params, message);
}

// ── isValid ────────────────────────────────────────────────────────────────────

function isValid(message) {
  try { decode(message); return true; } catch { return false; }
}

// ── MessageBuilder ─────────────────────────────────────────────────────────────

class MessageBuilder {
  constructor(action) {
    this._action = action.toUpperCase();
    this._object = null;
    this._params = {};
    if (!VOCABULARY[this._action]) throw new AILActionError(`Action inconnue: ${action}`);
  }
  on(object)       { this._object = object; return this; }
  to(target)       { return this.on(target); }
  param(k, v)      { this._params[k.toUpperCase()] = String(v); return this; }
  params(obj)      { Object.entries(obj).forEach(([k,v]) => this.param(k,v)); return this; }
  amount(v)        { return this.param('AMOUNT', v); }
  from(agent)      { return this.param('FROM', agent); }
  priority(level)  { return this.param('PRIORITY', level); }
  tokens(n)        { return this.param('TOKENS', n); }
  expiry(v)        { return this.param('EXPIRY', v); }
  raw()            { return encode(this._action, this._object, this._params); }
  build()          { return decode(this.raw()); }
  toString()       { return this.raw(); }
}

// ── AILParser ──────────────────────────────────────────────────────────────────

const SCAN_REGEX = /\[[A-Z][A-Z_]*[^\]]*\]/g;

class AILParser {
  constructor(strict = false) { this.strict = strict; this.errors = []; }
  parseText(text) {
    const results = [];
    for (const raw of (text.match(SCAN_REGEX) || [])) {
      try { results.push(decode(raw)); }
      catch (e) { this.errors.push(e.message); if (this.strict) throw e; }
    }
    return results;
  }
  filterByGroup(messages, group) {
    return messages.filter(m => m.group === group.toUpperCase());
  }
  filterBurns(messages) { return messages.filter(m => m.burnsToken); }
}

// ── JRVCClient (stub réseau) ───────────────────────────────────────────────────

class JRVCClient {
  constructor(agentId, balance = 0, nodeUrl = null) {
    this.agentId = agentId.toUpperCase();
    this.balance = balance;
    this.nodeUrl = nodeUrl;
    this._log    = [];
  }

  async send(rawMessage) {
    const msg = decode(rawMessage);
    const tx  = { action: msg.action, ts: Date.now(), raw: rawMessage };
    this._log.push(tx);
    if (msg.burnsToken && this.balance <= 0) {
      return { status: 'ERROR', error: 'Insufficient balance' };
    }
    if (msg.burnsToken) this.balance -= 1;
    if (this.nodeUrl) {
      return this._sendHTTP(rawMessage);
    }
    return { status: 'OK', action: msg.action, txId: `TX_${Date.now()}` };
  }

  async _sendHTTP(rawMessage) {
    try {
      const r = await fetch(this.nodeUrl + '/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ from: this.agentId, to: 'BROADCAST', message: rawMessage }),
      });
      return r.json();
    } catch (e) {
      return { status: 'ERROR', error: e.message };
    }
  }

  txLog() { return [...this._log]; }
}

// ── Factories rapides ──────────────────────────────────────────────────────────

const msgAnalyze  = (obj, params={}) => new MessageBuilder('ANALYZE').on(obj).params(params).raw();
const msgDelegate = (agent, params={}) => new MessageBuilder('DELEGATE').to(agent).params(params).raw();
const msgTransfer = (amount, from, to, memo='') => {
  const b = new MessageBuilder('TRANSFER').amount(amount).param('FROM', from).param('TO', to);
  if (memo) b.param('MEMO', memo);
  return b.raw();
};
const msgBTR = (to, type='SIMPLE', tokens='10', expiry='30D') =>
  new MessageBuilder('MSG').param('TO',to).param('TYPE',type).tokens(tokens).expiry(expiry).raw();

// ── Exports ────────────────────────────────────────────────────────────────────

module.exports = {
  // Core
  encode, decode, isValid,
  // Classes
  AILMessage, MessageBuilder, AILParser, JRVCClient,
  // Errors
  AILError, AILSyntaxError, AILActionError,
  // Vocab
  VOCABULARY,
  // Factories
  msgAnalyze, msgDelegate, msgTransfer, msgBTR,
};
