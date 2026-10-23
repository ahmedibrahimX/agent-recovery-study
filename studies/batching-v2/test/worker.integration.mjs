import { test } from 'node:test';
import assert from 'node:assert/strict';
import { resolve } from 'node:path';
import { Miniflare, Response as MFResponse } from 'miniflare';
import { tools as publicTools } from '../schema.mjs';

test('the pinned worker accepts bodies/arrows/comments and denies direct outbound fetch', async () => {
  const mf = new Miniflare({ modules: true, scriptPath: resolve('.runtime/worker.mjs'), compatibilityDate: '2026-07-30',
    compatibilityFlags: ['nodejs_compat'], workerLoaders: { LOADER: {} },
    serviceBindings: { BROKER: async request => {
      const p = await request.json();
      return new MFResponse(JSON.stringify({ ok: true, result: p.args.value }), { headers: { 'content-type': 'application/json' } });
    } },
  });
  try {
    await mf.ready;
    const description = await (await mf.dispatchFetch('http://worker/describe', {
      method: 'POST', body: JSON.stringify({ operation: 'describe', tools: publicTools }),
    })).json();
    assert.doesNotMatch(description.types, /= unknown|Promise<unknown>/);
    assert.match(description.types, /ledger_account_id: string/);
    assert.match(description.types, /amount_minor: number/);
    assert.match(description.types, /type ListIntentsOutput =/);
    const tools = { echo: { description: 'Return a value', inputSchema: { type: 'object', properties: { value: { type: 'integer' } }, required: ['value'], additionalProperties: false } } };
    for (const code of [
      'return await codemode.echo({value: 7});',
      'async () => await codemode.echo({value: 7})',
      '// A valid leading comment\nasync () => await codemode.echo({value: 7})',
    ]) {
      const r = await (await mf.dispatchFetch('http://worker/execute', { method: 'POST', body: JSON.stringify({ code, tools, token: 'unpaid-test', block: 0 }) })).json();
      assert.equal(r.result, 7, JSON.stringify(r));
      assert.equal(Boolean(r.error), false);
    }
    const r = await (await mf.dispatchFetch('http://worker/execute', { method: 'POST', body: JSON.stringify({ code: 'return await fetch("https://example.com");', tools, token: 'unpaid-test', block: 0 }) })).json();
    assert.ok(r.error, 'Generated code must not have direct network access');
  } finally { await mf.dispose(); }
});
