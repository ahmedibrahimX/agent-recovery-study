// Dependency-free offline verification of new batching-study results.
import { readFileSync, existsSync } from 'node:fs';
import { join, resolve, sep } from 'node:path';
import { isDeepStrictEqual as equal } from 'node:util';
import { check } from './checker.mjs';
import { fixture } from './scenario.mjs';
import { tokenCost } from './provider.mjs';
import { analyze, csv } from './analysis.mjs';

const read = path => JSON.parse(readFileSync(path, 'utf8'));
export function verify(folder) {
  folder = resolve(folder);
  const plan = read(join(folder, 'plan.json'));
  const summary = read(join(folder, 'summary.json'));
  if (summary.planSha256 !== plan.planSha256) throw new Error('Summary plan identity differs');
  const seen = new Set();
  const paired = new Map();
  const expectedOrder = plan.cases.flatMap(c => c.armOrder.map(arm => `${c.id}/${arm}`));
  let totalCost = 0;
  for (const row of summary.results) {
    const trial = resolve(folder, row.relativeDirectory);
    if (!trial.startsWith(folder + sep)) throw new Error('Unsafe trial path');
    const definition = read(join(trial, 'case.json'));
    if (!equal(definition, plan.cases.find(c => c.id === row.case))) throw new Error('Case differs from frozen plan');
    if (!['ordinary', 'code'].includes(row.arm)) throw new Error('Unknown arm');
    const key = `${row.case}/${row.arm}`;
    if (key !== expectedOrder[seen.size]) throw new Error('Trial order differs from the frozen plan');
    if (seen.has(key)) throw new Error('Duplicate case/arm');
    seen.add(key);
    const evidence = read(join(trial, 'evidence.json'));
    if (!equal(fixture(definition), evidence.initial)) throw new Error('Initial fixture differs from planned seed');
    const context = read(join(trial, 'public-context.json'));
    if (paired.has(row.case) && !equal(paired.get(row.case), context)) throw new Error('Paired public contexts differ');
    paired.set(row.case, context);
    const runtime = read(join(trial, 'runtime.json'));
    const requests = evidence.events.filter(e => e.kind === 'model_request').map(e => read(join(trial, `model-${e.index}-request.json`)));
    const verdict = check({ definition, evidence, report: existsSync(join(trial, 'report.json')) ? read(join(trial, 'report.json')) : null, runtime, requests });
    if (!equal(verdict, read(join(trial, 'verdict.json')))) throw new Error('Recomputed verdict differs');
    for (const [k, v] of Object.entries({ ...verdict, ...runtime })) if (!equal(v, row[k])) throw new Error(`Summary differs: ${k}`);
    const usage = existsSync(join(trial, 'model-usage.json')) ? read(join(trial, 'model-usage.json')) : [];
    let cost = 0;
    const totalUsage = Object.fromEntries(['input_tokens', 'output_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens'].map(k => [k, 0]));
    let toolBytes = 0;
    for (const call of usage) {
      const response = read(join(trial, `model-${call.index}-response.json`));
      const request = read(join(trial, `model-${call.index}-request.json`));
      if (request.model !== plan.model || response.model !== plan.model || request.max_tokens !== plan.limits.outputTokens) throw new Error('Model or limits differ');
      if (!equal(response.usage, call.usage)) throw new Error('Usage differs from provider response');
      for (const k of Object.keys(totalUsage)) totalUsage[k] += call.usage[k] ?? 0;
      for (const message of request.messages) if (Array.isArray(message.content)) for (const block of message.content) {
        if (block.type === 'tool_result') toolBytes += Buffer.byteLength(JSON.stringify(block.content));
      }
      const expected = plan.kind === 'unpaid-preflight' ? 0 : tokenCost(response.usage, plan.prices);
      if (Math.abs(call.costUsd - expected) > 1e-10) throw new Error('Calculated cost differs');
      cost += expected;
    }
    if (Math.abs(cost - runtime.costUsd) > 1e-10) throw new Error('Runtime cost differs');
    if (usage.length !== runtime.modelCallsCompleted || !equal(totalUsage, runtime.usage)) throw new Error('Runtime model count or token totals differ');
    if (toolBytes !== runtime.toolResultBytesPresentedToModel) throw new Error('Tool-result traffic measurement differs');
    if (Math.abs(usage.reduce((n, c) => n + c.latencyMs, 0) - runtime.modelMs) > 1e-7) throw new Error('Model timing decomposition differs');
    const blocks = read(join(trial, 'blocks.json'));
    if (blocks.length !== runtime.executionBlocks) throw new Error('Execution block count differs');
    for (const [index, block] of blocks.entries()) {
      if (block.index !== index || block.code !== read(join(trial, `program-${index}.json`)).code) throw new Error('Generated program differs');
      const count = evidence.events.filter(e => e.kind === 'request' && e.executionBlock === index).length;
      if (block.nativeCalls !== count) throw new Error('Calls-per-block measurement differs');
    }
    totalCost += cost;
  }
  const planned = plan.cases.length * 2;
  if (!summary.stopped && seen.size !== planned) throw new Error('Missing trials in a supposedly complete matrix');
  if (!seen.size) throw new Error('No completed trial evidence to verify');
  const budget = read(join(folder, 'budget-after.json'));
  if (!summary.stopped && budget.reservations.length) throw new Error('A complete run has unresolved cost reservations');
  if (Math.abs(budget.spentUsd - totalCost) > 1e-9) throw new Error('Ledger total differs');
  if (!equal(analyze(plan, summary.results), read(join(folder, 'comparison.json')))) throw new Error('Comparison differs from trial results');
  if (csv(plan, summary.results) !== readFileSync(join(folder, 'trials.csv'), 'utf8')) throw new Error('CSV differs from trial results');
  return { verifiedTrials: seen.size, plannedTrials: planned, stopped: summary.stopped, kind: plan.kind, calculatedCostUsd: totalCost,
    meaning: 'Recomputed local state/history/structured-report outcomes; does not rerun models or independently authenticate author provenance.' };
}

if (process.argv[1] && resolve(process.argv[1]) === resolve(new URL(import.meta.url).pathname)) console.log(JSON.stringify(verify(process.argv[2]), null, 2));
