/**
 * test.js — Tests SDK JavaScript AIL
 */

const { encode, decode, isValid, MessageBuilder, AILParser,
        msgAnalyze, msgDelegate, msgTransfer, msgBTR,
        AILSyntaxError, AILActionError } = require('./index');

let passed = 0, failed = 0;

function test(name, fn) {
  try {
    fn();
    console.log(`  [OK ] ${name}`);
    passed++;
  } catch(e) {
    console.log(`  [FAIL] ${name} — ${e.message}`);
    failed++;
  }
}

function assert(val, msg) { if (!val) throw new Error(msg || 'Assertion failed'); }
function assertEqual(a, b) { if (a !== b) throw new Error(`Expected ${b}, got ${a}`); }

console.log('=== AIL-LANG SDK JS v1.0.0 — TESTS ===\n');

// encode
console.log('-- encode --');
test('simple action',       () => assertEqual(encode('PING'), '[PING]'));
test('with object',         () => assertEqual(encode('ANALYZE','CONTRACT'), '[ANALYZE:CONTRACT]'));
test('with params',         () => assert(encode('ANALYZE','CONTRACT',{DOMAIN:'LEGAL'}).includes('DOMAIN:LEGAL')));
test('lowercase normalize', () => assertEqual(encode('ping'), '[PING]'));
test('unknown action',      () => { try { encode('FOOBAR'); assert(false); } catch(e) { assert(e.code === 'E002'); } });

// decode
console.log('\n-- decode --');
test('simple',              () => assertEqual(decode('[PING]').action, 'PING'));
test('with object',         () => assertEqual(decode('[ANALYZE:CONTRACT]').object, 'CONTRACT'));
test('with params',         () => assertEqual(decode('[ANALYZE:REPORT|DOMAIN:FIN]').get('DOMAIN'), 'FIN'));
test('group',               () => assertEqual(decode('[ANALYZE:X|DOMAIN:Y]').group, 'COGNITION'));
test('burns token',         () => assertEqual(decode('[TRANSFER|AMOUNT:1|FROM:A|TO:B]').burnsToken, true));
test('not burns',           () => assertEqual(decode('[PING]').burnsToken, false));
test('invalid syntax',      () => { try { decode('PING'); assert(false); } catch(e) { assert(e.code === 'E001'); } });
test('unknown action',      () => { try { decode('[FOOBAR]'); assert(false); } catch(e) { assert(e.code === 'E002'); } });

// isValid
console.log('\n-- isValid --');
test('[PING] valid',        () => assert(isValid('[PING]')));
test('[ANALYZE...] valid',  () => assert(isValid('[ANALYZE:REPORT|DOMAIN:FIN]')));
test('no brackets',         () => assert(!isValid('PING')));
test('unknown action',      () => assert(!isValid('[FOOBAR]')));

// MessageBuilder
console.log('\n-- MessageBuilder --');
test('chain',               () => {
  const r = new MessageBuilder('DELEGATE').to('ANALYST').param('PRIORITY','HIGH').raw();
  assert(r.includes('DELEGATE:ANALYST'));
  assert(r.includes('PRIORITY:HIGH'));
});
test('build returns AILMsg',() => assertEqual(new MessageBuilder('PING').build().action, 'PING'));
test('toString',            () => assertEqual(String(new MessageBuilder('PING')), '[PING]'));

// AILParser
console.log('\n-- AILParser --');
test('parse text', () => {
  const text = 'Hello [ANALYZE:REPORT|DOMAIN:FIN] and [DELEGATE:ANALYST|TOKENS:20]';
  const msgs = new AILParser().parseText(text);
  assertEqual(msgs.length, 2);
  assertEqual(msgs[0].action, 'ANALYZE');
  assertEqual(msgs[1].action, 'DELEGATE');
});
test('filter burns', () => {
  const msgs = [decode('[ANALYZE:X|DOMAIN:Y]'), decode('[TRANSFER|AMOUNT:1|FROM:A|TO:B]')];
  const burns = new AILParser().filterBurns(msgs);
  assertEqual(burns.length, 1);
});

// Factories
console.log('\n-- Factories --');
test('msgAnalyze',  () => assert(msgAnalyze('CONTRACT',{DOMAIN:'LEGAL'}).includes('ANALYZE:CONTRACT')));
test('msgDelegate', () => assert(msgDelegate('ANALYST',{PRIORITY:'HIGH'}).includes('PRIORITY:HIGH')));
test('msgTransfer', () => {
  const r = msgTransfer('500','JARVIS','AGENT_X');
  assert(r.includes('AMOUNT:500'));
  assert(r.includes('FROM:JARVIS'));
});
test('msgBTR',      () => {
  const r = msgBTR('AGENT_GPT4','URGENT','100','7D');
  assert(r.includes('TO:AGENT_GPT4'));
  assert(r.includes('TOKENS:100'));
});

console.log(`\n${'='.repeat(40)}`);
console.log(`TOTAL : ${passed + failed} tests | ${passed} OK | ${failed} FAILED`);
process.exit(failed > 0 ? 1 : 0);
