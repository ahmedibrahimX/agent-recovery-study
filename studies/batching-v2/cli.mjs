import { mkdirSync, readFileSync, openSync, closeSync, unlinkSync, writeFileSync } from 'node:fs';
import { join, relative } from 'node:path';
import { runTrial } from './runner.mjs';
import { save } from './provider.mjs';
import { analyze, csv } from './analysis.mjs';

const [mode, planPath, output, python, capText] = process.argv.slice(2);
if (!['preflight', 'run'].includes(mode) || !output || !python) throw new Error('Use tools/batching_v2.py');
const plan = JSON.parse(readFileSync(planPath, 'utf8'));
if ((mode === 'preflight') !== (plan.kind === 'unpaid-preflight')) throw new Error('Plan kind differs from execution mode');
mkdirSync(output, { recursive: true, mode: 0o700 });
const ledger = {
  spentUsd: 0, capUsd: Number(capText), reservations: [],
  persist() { save(join(output, 'budget-after.json'), { spentUsd: this.spentUsd, capUsd: this.capUsd, reservations: this.reservations }); },
};
if (mode === 'run' && (!process.env.ANTHROPIC_API_KEY || !Number.isFinite(ledger.capUsd) || ledger.capUsd <= 0)) throw new Error('A key and positive budget are required');
const lock = openSync('.runtime/run.lock', 'wx', 0o600);
const rows = [];
let stopped = false;
const persist = () => {
  ledger.persist();
  save(join(output, 'summary.json'), { study: plan.study, planSha256: plan.planSha256, mode, plannedTrials: plan.cases.length * 2, results: rows, stopped });
  save(join(output, 'comparison.json'), analyze(plan, rows));
  writeFileSync(join(output, 'trials.csv'), csv(plan, rows));
};
try {
  save(join(output, 'plan.json'), plan);
  save(join(output, 'budget-before.json'), { spentUsd: 0, capUsd: ledger.capUsd, reservations: [] });
  outer: for (const definition of plan.cases) for (const arm of definition.armOrder) {
    const folder = join(output, definition.id, arm);
    const row = await runTrial({ definition, arm, folder,
      config: { model: plan.model, limits: plan.limits, service: plan.service, prices: plan.prices },
      ledger, python, scripted: mode === 'preflight' });
    rows.push({ ...row, relativeDirectory: relative(output, folder) });
    console.log(JSON.stringify({ kind: plan.kind, size: definition.size, history: definition.history, arm, passed: row.passed, stateIntegrity: row.stateIntegrity, modelCalls: row.modelCallsCompleted, publicCalls: row.publicCalls, codeBlocks: row.executionBlocks }));
    if (row.error || ledger.reservations.length || !row.valid || (mode === 'preflight' && !row.passed)) {
      stopped = true; persist(); break outer;
    }
    persist();
  }
} catch (error) {
  stopped = true;
  save(join(output, 'orchestrator-error.json'), { error: String(error) });
} finally {
  persist();
  closeSync(lock); unlinkSync('.runtime/run.lock');
}
console.log(`${rows.length}/${plan.cases.length * 2} trials recorded. ${mode === 'preflight' ? 'Scripted plumbing checks; not model-performance evidence.' : 'New results only; historical results unchanged.'}`);
if (stopped) process.exitCode = 1;
