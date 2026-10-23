import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { PaidModel, load, save } from './experiments/live-v7/runner.mjs';

test('a capped run refuses dispatch before calling the provider', async () => {
  const folder = mkdtempSync(join(tmpdir(), 'live-budget-'));
  const oldFetch = globalThis.fetch;
  let dispatches = 0;
  process.env.ANTHROPIC_API_KEY = 'unpaid-test-placeholder';
  mkdirSync('runs/pilot-budget', { recursive: true });
  globalThis.fetch = async () => { dispatches++; throw new Error('unexpected transport'); };
  try {
    save('runs/pilot-budget/budget.json', { spentUsd: 0, capUsd: 0.001, reservations: {} });
    const model = new PaidModel(folder);
    await assert.rejects(model.request({ model: 'claude-sonnet-5', max_tokens: 8192, messages: [] }), /cap reached/);
    assert.equal(dispatches, 0);
    assert.equal(Object.keys(load('runs/pilot-budget/budget.json').reservations).length, 0);
  } finally { globalThis.fetch = oldFetch; rmSync(folder, { recursive: true }); }
});

test('an unknown provider outcome retains its reservation and prevents retry', async () => {
  const folder = mkdtempSync(join(tmpdir(), 'live-provider-failure-'));
  const oldFetch = globalThis.fetch;
  let dispatches = 0;
  globalThis.fetch = async () => { dispatches++; throw new Error('simulated network loss'); };
  try {
    save('runs/pilot-budget/budget.json', { spentUsd: 0, capUsd: 5, reservations: {} });
    const model = new PaidModel(folder);
    const request = { model: 'claude-sonnet-5', max_tokens: 8192, messages: [] };
    await assert.rejects(model.request(request), /network loss/);
    assert.equal(Object.keys(load('runs/pilot-budget/budget.json').reservations).length, 1);
    await assert.rejects(model.request(request), /Outstanding paid-request reservation/);
    assert.equal(dispatches, 1);
    assert.ok(!readFileSync(join(folder, 'model-0-request.json'), 'utf8').includes(process.env.ANTHROPIC_API_KEY));
  } finally { globalThis.fetch = oldFetch; rmSync(folder, { recursive: true }); }
});

test('successful usage is charged and its reservation is released', async () => {
  const folder = mkdtempSync(join(tmpdir(), 'live-usage-'));
  const oldFetch = globalThis.fetch;
  globalThis.fetch = async () => new Response(JSON.stringify({ model: 'claude-sonnet-5',
    stop_reason: 'end_turn', content: [], usage: { input_tokens: 100, output_tokens: 10 } }), { status: 200 });
  try {
    save('runs/pilot-budget/budget.json', { spentUsd: 0, capUsd: 5, reservations: {} });
    const model = new PaidModel(folder);
    await model.request({ model: 'claude-sonnet-5', max_tokens: 8192, messages: [] });
    const ledger = load('runs/pilot-budget/budget.json');
    assert.equal(ledger.spentUsd, 0.0003);
    assert.equal(Object.keys(ledger.reservations).length, 0);
    assert.equal(model.calls.length, 1);
  } finally { globalThis.fetch = oldFetch; rmSync(folder, { recursive: true }); }
});
