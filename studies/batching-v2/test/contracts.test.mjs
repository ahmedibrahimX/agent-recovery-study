import { test } from 'node:test';
import assert from 'node:assert/strict';
import { Backend } from '../scenario.mjs';
import { tools, reportSchema, returnContracts } from '../schema.mjs';
import { schemaErrors } from '../validation.mjs';

const definition = { id: 'contracts-control', size: 1, seed: 17, history: 'clean', withdrawAfter: 1 };
const validReport = () => ({ status: 'complete', updated_intent_ids: ['intent-a'], remaining_intent_ids: [], counts: { settled: 1, ready: 0, review: 0 }, summary: 'Completed one update.' });

test('all public success values satisfy explicit closed return schemas', async () => {
  const backend = new Backend(definition, { concurrency: 4, latencyMs: 0 });
  const intent = (await backend.invoke('list_intents', {})).result[0];
  const recipient = (await backend.invoke('get_recipient', { recipient_id: intent.recipient_id })).result;
  await backend.invoke('get_intent', { intent_id: intent.id });
  await backend.invoke('get_ledger', { ledger_account_id: recipient.ledger_account_id });
  await backend.invoke('patch_intent', { intent_id: intent.id, patch: { status: 'review' } });
  for (const observation of backend.publicObservations) {
    assert.equal(observation.ok, true);
    assert.deepEqual(schemaErrors(tools[observation.name].outputSchema, observation.result), []);
  }
  assert.deepEqual(Object.keys(returnContracts.successSchemas).sort(), Object.keys(tools).sort());
  assert.match(returnContracts.code, /not a JSON string/);
  assert.match(returnContracts.ordinary, /error string/);
  assert.ok(schemaErrors(tools.list_intents.outputSchema, { result: [intent] }).length);
  assert.ok(schemaErrors(tools.get_recipient.outputSchema, JSON.stringify(recipient)).length);
  assert.ok(schemaErrors(tools.get_recipient.outputSchema, { ...recipient, active: 'yes' }).length);
});

test('full report validation rejects extra keys, missing fields and malformed nested values without coercion', () => {
  const mutations = [
    report => { report.code = 'an unexpected root property'; },
    report => { report.counts.other = 0; },
    report => { delete report.status; },
    report => { delete report.counts.review; },
    report => { report.counts.ready = -1; },
    report => { report.counts.ready = 0.5; },
    report => { report.counts.ready = true; },
    report => { report.counts.ready = '0'; },
    report => { report.counts = null; },
    report => { report.status = 'ask'; },
    report => { report.updated_intent_ids = ['intent-a', 'intent-a']; },
    report => { report.remaining_intent_ids = [123]; },
    report => { report.remaining_intent_ids = 'intent-b'; },
    report => { report.summary = ''; },
    report => { report.summary = null; },
  ];
  for (const mutate of mutations) {
    const backend = new Backend(definition, { concurrency: 4, latencyMs: 0 });
    const report = validReport();
    mutate(report);
    const before = structuredClone(report);
    const errors = schemaErrors(reportSchema, report);
    assert.ok(errors.length, JSON.stringify(report));
    const response = backend.terminal(report);
    assert.equal(response.accepted, false);
    assert.deepEqual(response.reportSchemaErrors, errors);
    assert.deepEqual(report, before, 'Do not silently discard fields or coerce values');
    assert.equal(backend.events.at(-1).accepted, false);
    assert.equal(backend.terminal(validReport()).accepted, true, 'A corrected schema can be submitted');
  }
  for (const malformed of [null, [], 'report', 1, false]) assert.ok(schemaErrors(reportSchema, malformed).length);
});

test('contract extensions using unimplemented keywords fail closed', () => {
  assert.throws(() => schemaErrors({ type: 'string', pattern: '^x' }, 'x'), /Unsupported schema keyword/);
});
