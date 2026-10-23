// Portable orchestration around locally extracted, recorded experimental code.
import { mkdirSync, openSync, closeSync, unlinkSync, copyFileSync } from 'node:fs';
import { join, relative } from 'node:path';
import { spawnSync } from 'node:child_process';
import { BASE, load, save, runCase, PaidModel } from './experiments/live-v7/runner.mjs';
import { fixtureDriver } from './fixture-driver.mjs';

const [mode, output, budgetText, ...flags] = process.argv.slice(2);
if (!['preflight', 'run'].includes(mode) || !output) throw new Error('Use the tools/live.py entry point');
const quick = flags.includes('--quick');
const allCases = load(join(BASE, 'heldout.json'));
const smokeCases = allCases.filter(c => c.app === 'phone' && ['clean', 'withdraw_inflight_write'].includes(c.family));
const cases = quick ? smokeCases : allCases;
mkdirSync('runs/pilot-budget', { recursive: true });
const lock = openSync('runs/pilot.lock', 'wx', 0o600);
const ledger = 'runs/pilot-budget/budget.json';
let stopped = false;
const results = [];

// Scripted Anthropic-shaped responses exercise the actual LangChain loop,
// middleware, gateway, Code Mode sandbox, and simulator without provider access.
// These are plumbing checks, never model-performance observations.
function installScriptedModel() {
  process.env.ANTHROPIC_API_KEY = 'unpaid-preflight-placeholder';
  PaidModel.prototype.request = async function(request) {
    const n = this.calls.length;
    if (n >= 4) throw new Error('Scripted agent exceeded its expected turn count');
    save(join(this.folder, `model-${n}-request.json`), request);
    await this.beforeRequest?.(request, n);
    const config = load(join(this.folder, 'agent-input.json'));
    const info = config.context;
    const codeArm = (request.tools ?? []).some(t => t.name === 'execute');
    const noticed = JSON.stringify(request.messages).includes('Live user message [');
    const plan = [];
    await fixtureDriver({ info,
      call: async (app, api, args) => { plan.push({ app, api, args }); return info.priorPublicObservations; },
      pullNotices: async () => noticed ? [{}] : [],
      submit: async report => { plan.push({ report }); },
    });
    const action = noticed ? plan.at(-1) : plan[n];
    if (!action) throw new Error('No scripted fixture action for this turn');
    let content;
    if (!action.report) {
      const name = `${action.app}__${action.api}`;
      content = [{ type: 'tool_use', id: `unpaid-tool-${n}`, name: codeArm ? 'execute' : name,
        input: codeArm ? { code: `return await codemode.${name}(${JSON.stringify(action.args)})` } : action.args }];
    } else {
      content = [{ type: 'text', text: JSON.stringify(action.report) }];
    }
    const response = { id: `unpaid-response-${n}`, type: 'message', role: 'assistant', model: request.model,
      content, stop_reason: content[0].type === 'tool_use' ? 'tool_use' : 'end_turn', stop_sequence: null,
      usage: { input_tokens: 0, output_tokens: 0 } };
    save(join(this.folder, `model-${n}-response.json`), response);
    this.calls.push({ model: request.model, usage: response.usage, costUsd: 0, latencyMs: 0, scripted: true });
    save(join(this.folder, 'model-usage.json'), this.calls);
    return response;
  };
}

async function matrix(selected, kind, fixture = false) {
  for (const c of selected) for (const arm of c.armOrder) {
    const directory = join(output, kind, c.id, arm);
    const result = await runCase(c, arm, directory, fixture ? { fixtureDriver } : {});
    results.push({ ...result, runKind: kind, relativeDirectory: relative(output, directory) });
    save(join(output, 'summary.json'), { mode, results, stopped });
    console.log(JSON.stringify({ kind, domain: c.app, history: c.family, arm,
      passed: result.passed ?? false, valid: result.valid ?? false, safe: result.safe ?? false }));
    const runtime = load(join(directory, 'runner.json'));
    if (result.invalid || result.valid === false || Object.keys(load(ledger).reservations).length
        || (runtime.error && runtime.failureCategory !== 'model_resource_limit')
        || (mode === 'preflight' && !result.passed)) {
      stopped = true;
      return false;
    }
  }
  return true;
}

try {
  const cap = mode === 'run' ? Number(budgetText) : 0;
  if (mode === 'run' && (!Number.isFinite(cap) || cap <= 0 || !process.env.ANTHROPIC_API_KEY)) {
    throw new Error('A positive budget and your ANTHROPIC_API_KEY are required');
  }
  save(ledger, { spentUsd: 0, capUsd: cap, reservations: {} });
  save(join(output, 'budget-before.json'), load(ledger));
  copyFileSync(join(BASE, 'heldout.json'), join(output, 'published-case-set.json'));
  copyFileSync(join(BASE, 'environment.json'), join(output, 'environment.json'));
  save(join(output, 'run-config.json'), {
    format: 1, mode, quick, model: 'claude-sonnet-5', capUsd: cap,
    caseSet: 'Reexecution of the published v7 cases; these are already exposed cases, not new held-out evidence',
    historicalResultsChanged: false,
    pricesUsdPerMillionTokens: { input: 2, output: 10, cacheCreation: 2.5, cacheRead: 0.2 },
    costKind: 'Calculated token cost at the recorded prices; not invoice verification',
    node: process.version,
    plannedTrials: mode === 'preflight' ? cases.length * 2 + smokeCases.length * 2 : cases.length * 2,
  });
  if (mode === 'preflight') {
    delete process.env.ANTHROPIC_API_KEY;
    // Budget guards are checked with an intercepted transport, not a real key.
    const test = spawnSync(process.execPath, ['--test', 'budget.test.mjs'], { encoding: 'utf8' });
    save(join(output, 'budget-tests.json'), { passed: test.status === 0 });
    if (test.status !== 0) {
      save(join(output, 'budget-test-error.json'), { stdout: test.stdout, stderr: test.stderr });
      throw new Error('Budget guard tests failed');
    }
    save(ledger, { spentUsd: 0, capUsd: 0, reservations: {} });
    if (await matrix(cases, 'unpaid-native-fixture', true)) {
      installScriptedModel();
      await matrix(smokeCases, 'unpaid-scripted-agent');
    }
    if (load(ledger).spentUsd !== 0 || Object.keys(load(ledger).reservations).length) {
      throw new Error('An unpaid preflight changed the spending ledger');
    }
  } else {
    await matrix(cases, 'fresh-model-trial');
  }
} catch (error) {
  stopped = true;
  save(join(output, 'orchestrator-error.json'), { error: String(error) });
} finally {
  save(join(output, 'budget-after.json'), load(ledger));
  save(join(output, 'summary.json'), { mode, results, stopped });
  closeSync(lock);
  unlinkSync('runs/pilot.lock');
}
if (stopped) {
  console.error('Stopped. Detailed diagnostics are in the new local output directory.');
  process.exitCode = 1;
} else {
  console.log(`${results.length} trials recorded; historical results were not changed.`);
}
