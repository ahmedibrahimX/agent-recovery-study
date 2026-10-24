import { mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { performance } from 'node:perf_hooks';

export const save = (path, value) => writeFileSync(path, JSON.stringify(value, null, 2) + '\n', { mode: 0o600 });
export function tokenCost(usage, prices) {
  const names = { input_tokens: 'input', output_tokens: 'output', cache_creation_input_tokens: 'cacheCreation', cache_read_input_tokens: 'cacheRead' };
  return Object.entries(names).reduce((sum, [field, price]) => sum + (usage[field] ?? 0) * prices[price] / 1e6, 0);
}

export class Provider {
  constructor({ folder, config, ledger, beforeRequest, scripted, transport = fetch }) {
    Object.assign(this, { folder, config, ledger, beforeRequest, scripted, transport });
    this.calls = [];
    this.started = performance.now();
    mkdirSync(folder, { recursive: true });
  }

  async request(request) {
    const { limits, model, prices } = this.config;
    if (this.ledger.reservations.length) throw new Error('Unknown provider outcome: outstanding cost reservation; no automatic retry');
    if (this.calls.length >= limits.modelRequests) throw new Error('Model request limit reached');
    if (request.model !== model || request.max_tokens !== limits.outputTokens || request.stream) throw new Error('Unexpected model/output/stream settings');
    const body = JSON.stringify(request);
    if (Buffer.byteLength(body) > limits.requestBytes) throw new Error('Model request byte limit reached');
    const index = this.calls.length;
    save(join(this.folder, `model-${index}-request.json`), request);
    const started = performance.now();
    let response, transport;
    if (this.scripted) {
      await this.beforeRequest(request, index);
      response = await this.scripted(request, index);
    }
    else {
      if (!process.env.ANTHROPIC_API_KEY) throw new Error('ANTHROPIC_API_KEY is required for paid trials');
      // UTF-8 request bytes bound token count conservatively. Count cache creation
      // at the highest supplied input rate and reserve the full output budget.
      const reserve = Buffer.byteLength(body) * Math.max(prices.input, prices.cacheCreation, prices.cacheRead) / 1e6 + limits.outputTokens * prices.output / 1e6;
      if (this.ledger.spentUsd + reserve > this.ledger.capUsd) throw new Error('Local token-cost budget would be exceeded before provider dispatch');
      this.ledger.reservations.push({ caseDirectory: this.folder, request: index, reservedUsd: reserve });
      this.ledger.persist();
      await this.beforeRequest(request, index);
      this.controller = new AbortController();
      const r = await this.transport('https://api.anthropic.com/v1/messages', {
        method: 'POST', headers: { 'content-type': 'application/json', 'anthropic-version': '2023-06-01', 'x-api-key': process.env.ANTHROPIC_API_KEY },
        body, signal: AbortSignal.any([AbortSignal.timeout(180000), this.controller.signal]),
      });
      response = await r.json();
      transport = { status: r.status, requestId: r.headers.get('request-id') };
      save(join(this.folder, `model-${index}-response.json`), response);
      save(join(this.folder, `model-${index}-transport.json`), transport);
      if (!r.ok || !response.usage) throw new Error('Provider failed; retain spending reservation and stop');
      for (const key of ['input_tokens', 'output_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens']) {
        const value = response.usage[key] ?? 0;
        if (!Number.isSafeInteger(value) || value < 0) throw new Error('Invalid provider usage; retain reservation');
      }
      const actual = tokenCost(response.usage, prices);
      this.ledger.spentUsd += actual;
      this.ledger.reservations = [];
      this.ledger.persist();
    }
    save(join(this.folder, `model-${index}-response.json`), response);
    const costUsd = this.scripted ? 0 : tokenCost(response.usage, prices);
    this.calls.push({ index, model: response.model, usage: response.usage, costUsd, latencyMs: performance.now() - started, scripted: Boolean(this.scripted) });
    save(join(this.folder, 'model-usage.json'), this.calls);
    if (response.model !== model) throw new Error('Served model differs from the planned identifier');
    if (['refusal', 'max_tokens'].includes(response.stop_reason)) throw new Error(`Model stopped: ${response.stop_reason}`);
    if (this.ledger.spentUsd > this.ledger.capUsd && !this.scripted) throw new Error('Accounted usage exceeded the local estimate; stop');
    return response;
  }

  cancelPending() { this.controller?.abort(new Error('Trial ended before provider outcome was known')); }
}
