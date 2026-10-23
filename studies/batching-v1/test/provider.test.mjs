import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, rmSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { Provider, tokenCost } from '../provider.mjs';

const config = { model: 'claude-sonnet-5', limits: { modelRequests: 128, outputTokens: 8192, requestBytes: 1000000 }, prices: { input: 2, output: 10, cacheCreation: 2.5, cacheRead: 0.2 } };
const request = { model: config.model, max_tokens: 8192, messages: [] };
async function withProvider(cap, transport, action) {
  const folder = mkdtempSync(join(tmpdir(), 'batch-budget-'));
  const ledger = { spentUsd: 0, capUsd: cap, reservations: [], persist() {} };
  process.env.ANTHROPIC_API_KEY = 'unpaid-unit-test-placeholder';
  try {
    const provider = new Provider({ folder, config, ledger, beforeRequest: async () => {}, transport });
    await action(provider, ledger, folder);
  } finally { delete process.env.ANTHROPIC_API_KEY; rmSync(folder, { recursive: true }); }
}

test('small cap prevents provider transport and exposure recording', async () => {
  await withProvider(0.001, () => { throw new Error('Must not call transport'); }, async (p, ledger) => {
    let exposed = false; p.beforeRequest = async () => { exposed = true; };
    await assert.rejects(p.request(request), /budget/);
    assert.equal(exposed, false);
    assert.equal(ledger.reservations.length, 0);
  });
});

test('unknown provider outcome retains its reservation and prevents retry', async () => {
  let dispatched = 0;
  await withProvider(5, async () => { dispatched++; throw new Error('Unknown network outcome'); }, async (p, ledger) => {
    await assert.rejects(p.request(request), /Unknown network/);
    assert.equal(ledger.reservations.length, 1);
    await assert.rejects(p.request(request), /outstanding/);
    assert.equal(dispatched, 1);
  });
});

test('successful usage is charged and request artifacts contain no provider credential', async () => {
  const usage = { input_tokens: 100, output_tokens: 10, cache_read_input_tokens: 5 };
  await withProvider(5, async () => new Response(JSON.stringify({ model: config.model, usage, stop_reason: 'end_turn', content: [] })), async (p, ledger, folder) => {
    await p.request(request);
    assert.equal(ledger.spentUsd, tokenCost(usage, config.prices));
    assert.equal(ledger.reservations.length, 0);
    assert.equal(readFileSync(join(folder, 'model-0-request.json'), 'utf8').includes('unpaid-unit-test-placeholder'), false);
  });
});

test('HTTP provider errors are not retried or treated as free successful calls', async () => {
  await withProvider(5, async () => new Response(JSON.stringify({ error: 'test rejection' }), { status: 429 }), async (p, ledger) => {
    await assert.rejects(p.request(request), /Provider failed/);
    assert.equal(ledger.reservations.length, 1);
    assert.equal(p.calls.length, 0);
  });
});
