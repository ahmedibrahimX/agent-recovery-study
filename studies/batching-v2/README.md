# Conditional batching with explicit return contracts: v2

**Question:** With explicit tool-return contracts and full report-schema validation, how do ordinary structured tools and Code Mode trade correctness, model traffic, latency, cost and interruption behavior as reconciliation workloads grow?

This is a separate follow-up to the [first measured configuration](../../results/batching-v1/README.md). The v1 source, plans, evidence and frozen verdicts remain unchanged. The original AppWorld experiment and UAT also remain unchanged. **No paid v2 results have been recorded.** Unpaid scripted preflights qualify interfaces and guards; they are not model-performance evidence.

## What changes and what stays fixed

| Component | v2 condition |
| --- | --- |
| Successful tool returns | Every tool has an explicit closed output schema. Both arms receive the same public schemas and success/error documentation. Code Mode also receives SDK-generated TypeScript output types. |
| Wrapper semantics | Internal Code API calls return raw arrays/objects and throw on errors. Ordinary tool messages serialize raw success values or an error object. The outer execution result wrapper is explicitly distinguished from calls inside a program. These interface differences are documented, not normalized away. |
| Terminal reports | The complete closed report schema is enforced at submission and rechecked offline, including root/nested extra fields, required fields, types, enum, integer bounds, array items/uniqueness and string length. No coercion or field stripping. |
| Repairs | Schema-invalid submissions receive schema errors and may be repaired; every rejected terminal attempt stays in the journal. Model calls, time and cost count in full. The gate does not supply correct classifications, IDs or counts. |
| Paid fixtures | Fresh default seeds `2026102401`, `2026102407`, `2026102413`. Unpaid preflight uses seed 17, separate from default paid seeds. The generator remains public. |
| Study identity | Separate `batching-v2` case IDs, source/plan hashes, setup directory, build marker and results paths. v1 plans and results cannot be substituted. |
| Task/runtime | Same classification policy, status-only mutation, human edits, between-write withdrawal, underlying fixture generator, LangChain loop, model, service limits and generous upper budgets as v1. |

This is a combined contract/documentation and report-admission/grading change. A v1-to-v2 comparison cannot attribute changes to output schemas alone. Different fixtures and provider conditions add further limits. Neither interface is promised an advantage.

## Run from a clean checkout

Requirements: Linux or macOS, Python 3.12+, Node 22+, npm and internet for setup. No Docker, AppWorld assets or Cloudflare account is needed. Paid execution requires your own Anthropic key with access to `claude-sonnet-5`.

```sh
python3 tools/batching_v2.py doctor
python3 tools/batching_v2.py setup
python3 tools/batching_v2.py preflight
```

Setup installs the pinned Python stack under ignored `.batching-v2/venv`, installs pinned Node dependencies and builds the local `workerd` worker. Preflight makes no paid requests: it runs 18 scripted trials through the real LangChain loop and both interfaces, plus a worker integration control for SDK types, supported code forms and direct-network denial. Generated code receives no direct outbound network access.

A 54-trial measurement plan uses all three fresh seeds, sizes 1/5/20, clean/edit/withdraw, one repetition and both arms:

```sh
python3 tools/batching_v2.py plan --repetitions 1 --output reports/batching-v2/followup-plan.json
```

Inspect and retain that plan before execution. Supply your key through the environment and a **newly authorized** positive budget:

```sh
export ANTHROPIC_API_KEY='<your Anthropic API key>'
python3 tools/batching_v2.py run --plan reports/batching-v2/followup-plan.json --budget-usd "$FOLLOWUP_BUDGET_USD"
```

Set `FOLLOWUP_BUDGET_USD` explicitly before running. It is a local accounting cap, not a predicted bill or account-wide spending limit. Earlier study spending is not automatically carried into this invocation. Do not infer that an earlier authorization or remaining balance grants a new budget. The model/limits and recorded token rates are frozen in the plan; calculated cost is not a provider invoice.

For a smaller first measurement use `plan --quick`, which selects sizes 1/5, one fresh seed and one repetition for 12 trials. The default plan without `--repetitions 1` has 162 trials, including three repetitions on shared fixtures. Custom sizes/seeds/repetitions are supported. Record any choice before paid execution; do not choose a matrix after seeing results.

A conservative per-request reservation is checked before transport. Unknown provider outcomes retain their reservation and stop execution. No automatic retry or resume occurs. Reusing a plan creates a separate attempt, so retain failed/partial attempts and reconcile provider spending before another run. Plans never overwrite an existing file.

## Workload and histories

The synthetic agent lists assigned intents, reads recipients to discover ledger accounts, reads ledgers, applies the same ordered classification policy and patches status. Exactly matched settled ledger entries become `settled`; inconsistent/duplicate matches become `review`; unmatched intents become `ready` only for eligible recipients. Human notes and unrelated fields must survive. No payment creation or money movement is possible.

Ordinary tools may issue multiple independent calls in one model response. Code Mode may chain dependent calls and process intermediate data inside a program. Neither gets a prescribed solution or block size. Both share concurrency four and an injected 20 ms service delay; these are fixture assumptions, not production measurements.

| History | Intervention and requirement |
| --- | --- |
| `clean` | Reconcile every intent and accurately report effects. |
| `edit` | Change a human note after the first list snapshot, before delivering its stale result. Preserve the newer note at every recorded state. |
| `withdraw` | Withdraw after `max(1, floor(size/2))` committed updates, between writes. The guard rejects later admissions. Report completed versus remaining work accurately. |

Already-generated parallel calls and code are not preempted. A rejection can occur before the model receives the notice; attempts after actual model exposure are counted separately. The shared terminal gate requires withdrawal exposure in a recorded model request before accepting a report. If the last write already finished, accurate `complete` or `stopped` is allowed; otherwise withdrawal requires `stopped`. No retroactive approval question or real human approval/resume cycle is tested.

## Grading and contract controls

The dependency-free checker imports neither backend nor agent. It reconstructs classifications from the initial fixture and replays requests, guard decisions, intermediate snapshots, effects, notice exposure and terminal decisions. It also checks successful tool results against their published return schemas.

The online gate and offline checker use the same published schema and a small dependency-free validator supporting every keyword in these contracts. Unsupported schema keywords fail closed. This is a same-author implementation, not an independently validated JSON Schema engine. Negative controls cover the observed extra-`code` report defect, nested extras, missing fields, invalid types/bounds/enums, duplicates, forged terminal acceptance and malformed-then-corrected reports. The full report shape is checked; free-form prose truthfulness remains outside automatic grading, and whitespace-only summaries fail the separate semantic check.

State integrity, classification correctness, full schema validity (`reportSchemaValid`), selected structured claims, original goal completion, stopping compliance and guard-denied requests remain separate metrics. Correct withdrawal can pass without completing the original full task. The guard's prevention of an effect does not establish that the agent understood the policy.

```sh
node --test studies/batching-v2/test/*.test.mjs
python3 -B -m unittest discover -s tools -p test_batching_v2.py -v
```

## Measurement, retention and verification

Each invocation writes a new directory under `reports/batching-v2/` with the frozen plan/source identities, environment/build hashes, raw provider requests/responses/usages, generated code/results, journals/snapshots, all terminal attempts, final reports/verdicts, budget records, CSV and comparisons. The parent provider proxy retains the actual key; only an ephemeral local token is supplied to the agent, and no provider credential is saved in request artifacts. Generated output is ignored by Git and not published automatically.

Use the exact output path printed by the runner:

```sh
python3 tools/batching_v2.py verify reports/batching-v2/run-<timestamp>-<suffix>
python3 tools/check_package.py
```

Offline verification needs only Python and Node, not installed packages or an API key. It rechecks fixtures, states, full report schemas, saved usage/cost and summary/CSV without executing generated programs or remeasuring model speed. Keep the exact source checkout used for a plan; execution and verification reject changed sources, including hashed study documentation/tests. Setup/build identities are checked before execution.

Comparisons group by size/history, retain all attempted outcomes/failures/costs, and show paired latency/cost differences only for jointly successful pairs. Present failed counterparts and maximum repair times alongside those paired figures. Agent time includes Python/framework startup; full elapsed also includes Code worker cold setup/cleanup. Model time is provider round-trip time. Tool-result bytes count repeated model-request history; actual token usage determines calculated cost. Residual time is not isolated sandbox CPU.

Fixtures are synthetic and public; sizes share prefixes, histories and repeated trials are correlated. The local source freeze is not external preregistration. One provider/model, injected service latency and shared-host noise constrain interpretation. No significance, production-safety or general framework-superiority claim is implied. Independent human review remains pending.
