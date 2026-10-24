# Ordinary tools vs Code Mode: recovery and conditional batching

**How do ordinary structured tools and Code Mode trade correctness, model traffic, latency and cost as workloads grow or human intervention changes the task?**

We compare **ordinary structured tools versus Cloudflare Code Mode** under shared application safeguards. The historical AppWorld study examines small recovery tasks; a measured synthetic reconciliation study adds larger conditional workloads.

Both batching studies include simulated human-in-the-loop (HITL) conditions: the harness changes a human note or withdraws approval during execution. They measure field preservation, stopping and reports of completed versus remaining work alongside efficiency.

Each comparison holds the LangChain loop, model, task policy and safeguards fixed while changing the execution interface and its associated instructions. The studies have different tasks and terminal contracts; their pass rates are never pooled.

**Latest measured finding:** with explicit return contracts, ordinary tools were usually faster and slightly cheaper at 1 and 5 intents. At 20 intents, Code Mode was faster in all nine paired cases and used fewer model requests at 58.2% lower calculated model cost, while making more public API calls. Both arms passed 27/27 state/history/full-report-schema outcomes. This is a workload-dependent result from a bounded synthetic study, not a universal crossover, production-safety guarantee or general framework ranking.

**Reproducibility:** the results for [batching with explicit tool contracts](results/batching-v2/README.md), [initial batching experiment: pilot and confirmation](results/batching-v1/README.md) and historical AppWorld study all verify offline. Their original source, evidence and verdicts remain separate and unchanged. You can also run exposed replications with your own API key. Independent human review remains pending; nothing here is an official AppWorld benchmark score or an upstream endorsement.

## How the investigation developed

| Investigation | Question and finding | What it led to |
| --- | --- | --- |
| [Recovery on small AppWorld tasks](#recovery-on-small-appworld-tasks-results) | Under human edits and approval withdrawal, both interfaces preserved checked external state with shared safeguards; terminal responses could still violate the chosen contract. Small tasks offered little batching. | Separate agent behavior from guard protection, and test larger dependent workloads. |
| [Initial batching experiment](results/batching-v1/README.md) | Larger read/classify/update workloads under human edits and withdrawal exposed ambiguous return values, long repairs and incomplete report validation. Confirmation did not show a consistent Code efficiency advantage. | Make tool-return contracts explicit for both arms and enforce the complete report schema. |
| [Batching with explicit tool contracts](results/batching-v2/README.md) | Both arms passed all 27 cases, including note preservation and correct partial stopping. Ordinary tools usually favored smaller tasks; Code reduced model requests, time and calculated cost at 20 intents while making more API calls. | Treat workload size, tool contracts and execution granularity as integration choices to validate on the intended task distribution. |

The initial batching experiment exposed ambiguous tool returns and incomplete report validation. A follow-up supplied explicit return contracts and enforced the full report schema. Both measured conditions remain available; their differences do not isolate the effect of return contracts alone. The [detailed experiment history](docs/EXPERIMENT_HISTORY.md) also retains the earliest adapter-affected recovery comparison, its correction and earlier exploratory diagnostics. Technical identifiers remain in source/evidence paths for reproducibility.

## What an engineer can learn here

The [study of batching with explicit tool contracts](results/batching-v2/README.md) retains all 54 paid trials, code, requests, state histories, guard denials and reporting repairs. The [initial batching experiment](results/batching-v1/README.md) remains visible with its 18-trial pilot, separate 54-trial confirmation, limitations and frozen verdicts. Its integration weaknesses motivated explicit return contracts and full report validation in the follow-up; multiple factors changed, so the difference is not an output-schema-only effect.

- Distinguish a mutation request, dispatch admission, commit, result delivery, and exposure of a notice to the model.
- Check intermediate external effects: a final correct database can hide an earlier lost edit.
- Separate safeguards enforced by application code from behavior chosen by an agent.
- See how an execution adapter defect distorted an initial comparison, how it was corrected, and why the original results must remain separate.
- Inspect how ambiguous tool returns, generated-program repairs and batch size affect an interface comparison.
- Reproduce the saved verdicts and inspect an actual failure before accepting the architecture decision.

Start with [one paired batching trajectory](results/batching-v2/README.md#inspect-one-paired-batching-trajectory), where Code chains 40 dependent reads inside one block. The [historical withdrawal case](docs/CASE-WALKTHROUGH.md) explains why achieved state and terminal protocol can disagree. Then use the [reviewer guide](docs/REVIEWER-WALKTHROUGH.md), [historical architecture](docs/ARCHITECTURE.md), [scenario contracts](docs/SCENARIOS.md), and [claims-to-evidence map](docs/CLAIMS.md).

## Batching with explicit tool contracts

**Comparing efficiency, correctness and stopping behavior under human edits and approval withdrawal.**

The study of batching with explicit tool contracts reconciles 1, 5 or 20 synthetic payment-intent statuses under clean, stale-list human-note-edit and between-write approval-withdrawal histories. No money moves. Three fresh fixture seeds, one repetition and two arms produce 54 trials. Both arms use the same model, LangChain loop, underlying APIs, policy and service limits; ordinary tools may issue parallel calls. Every attempted trial is retained; all pairs passed and no failed counterpart is excluded from timing comparisons.

| Condition | Required behavior |
| --- | --- |
| Clean execution | Reconcile every assigned intent and report the actual updates. |
| Simulated human edit | Preserve the newer human note after a stale list snapshot; classification inputs do not change. |
| Approval withdrawal | The guard rejects new admissions after withdrawal; the agent stops requesting mutations once it sees the notice and accurately reports updated and remaining intents. |

Completed/remaining IDs and counts provide handoff information. The batching contract requires accurate completion or stopping, without a renewed-approval question. It does not evaluate a real person replying, approving a resumption, escalation routing or resumed execution. Some original recovery contracts separately required an approval-question response; that requirement remains part of their unchanged scoring.

| Intents | Median agent seconds, ordinary / Code | Code faster in paired agent and full elapsed time | All-attempt calculated cost, ordinary / Code |
| --- | ---: | ---: | ---: |
| 1 | 10.775 / 12.536 | 2/9 | $0.392954 / $0.416298 |
| 5 | 21.421 / 23.593 | 3/9 | $0.685658 / $0.705316 |
| 20 | 59.008 / 35.959 | 9/9 | $2.948456 / $1.232804 |

At size 20, Code uses 42 versus 93 model requests and 616 versus 533 public API calls. The median paired Code advantage is 23.077 seconds of agent time, or 22.998 seconds including worker setup/cleanup. Agent time includes Python/framework startup. Repairs and errors remain included; costs use recorded token usage at frozen rates, not provider invoices or infrastructure costs.

| All 27 attempts per arm | Ordinary tools | Code Mode |
| --- | ---: | ---: |
| Primary outcomes / state integrity / full report schema | 27/27 each | 27/27 each |
| Original full goal reached | 21/27 | 21/27 |
| Correct partial stops after withdrawal | 6 | 6 |
| Model requests | 185 | 126 |
| Public API calls | 714 | 804 |
| Tool-result bytes presented to model, including repeated history | 1,373,795 | 644,132 |
| Guard-denied mutation requests | 23 | 33 |
| Mutation requests after withdrawal reached the model | 0 | 0 |
| Rejected terminal submissions | 0 | 2 |
| Calculated model cost | $4.027068 | $2.354418 |

A correct partial stop can pass without finishing the original full task. Guards prevent forbidden effects; they do not prove independent model judgment. A malformed Code report was rejected and corrected; a fallback quirk caused a second rejection without another model request. Final schema compliance does not mean error-free execution or truthful prose.

The [full results record](results/batching-v2/README.md) includes size/history breakdowns, a trace-level batching walkthrough, all observed errors/repairs, exact source/plan hashes and offline verification. Ordinary tools did use parallel reads; additional write grouping was a model choice, not an inherent interface limit. The edit changes notes rather than business classification facts. Three correlated fixture seeds, one execution per case, one provider/model and injected service latency constrain generalization. There is no real human approval/resume, production recovery or independently reviewed prose evaluation.

## Initial batching experiment

The initial batching experiment also combines larger dependent workloads with simulated human-note edits, approval withdrawal and completed/remaining-work reporting. It remains part of the public record: [18 pilot and 54 separate confirmation trials, unchanged](results/batching-v1/README.md). Confirmation outcomes were 26/27 ordinary versus 27/27 Code, with calculated costs $3.135602 versus $4.610532 and no consistent Code efficiency advantage. It exposed ambiguous return values, long program repairs, one ordinary premature stop and incomplete report-schema coverage. The pilot's stronger large-workload advantage remains separate rather than being pooled or selected as the headline.

The follow-up adds explicit return documentation/schemas and full report admission/grading, uses fresh fixtures and runs later. These combined changes do not isolate the effect of output schemas. The initial experiment's passes, failures, costs and repairs have not been rescored or replaced. Historical AppWorld outcomes below also retain their own tasks and terminal contracts.

## Reproduce the saved results

Requirements: Python **3.12+** with SQLite `deserialize`, Node **22+**, and about 200 MB temporary free space. Saved-result verification runs entirely offline using the included evidence. It requires only Python and Node.js.

From the repository root:

```sh
python3 tools/check_package.py
python3 -E -s -B study/verify.py
python3 -E -s -B -m unittest discover -s study -p test_verifier.py -v
python3 -B tools/verify_batching_v1.py
python3 -B tools/verify_batching_v2.py
```

Expected: the verifier authenticates 5,369 logical files across 3,257 unique blobs and reproduces **48 adapter-affected recovery verdicts and 24 corrected recovery verdicts, reported separately** (technical archive identifiers `v6` and `v7`). All five negative controls pass. A zero exit code means the saved evidence reproduces, **including expected agent failures**; it does not mean all agents passed.

The historical checker validates state and parts of the structured protocol, not complete prose truthfulness. It has a [question-type validation gap](docs/KNOWN-LIMITATIONS.md); all 33 saved approval questions were checked and have valid string types. The initial batching verifier separately reproduces 54 confirmation, 18 pilot and 18 unpaid preflight trials, including the expected ordinary failure. The explicit-contract batching verifier reproduces 54 paid and 18 unpaid trials. Every saved run file is preserved, and each version's published metrics are recomputed. Verification rechecks saved clocks and usage; it does not remeasure hosted model speed. See [what reproduction means](docs/REPRODUCING.md) and the [validation record](docs/VALIDATION.md).

## Run new trials

For an exposed replication of the synthetic explicit-contract condition, no Docker is needed:

```sh
python3 tools/batching_v2.py setup
python3 tools/batching_v2.py preflight
python3 tools/batching_v2.py plan --repetitions 1 --output reports/batching-v2/followup-plan.json
```

This freezes a new execution plan for the published 54-trial matrix. The default seeds are now exposed measured cases, not unseen evaluation evidence. Paid execution additionally needs your API key and an explicit budget; follow the [frozen run guide for batching with explicit contracts](studies/batching-v2/README.md). New attempts stay separate from all saved results. Versioned source documentation retains its pre-execution status because plans hash those bytes; the [results record](results/batching-v2/README.md) supplies the current measured status.

For a replication of the historical AppWorld study:

With Python, Node/npm, and Docker running:

```sh
python3 tools/live.py setup
python3 tools/live.py preflight
export ANTHROPIC_API_KEY='<your Anthropic API key>'
python3 tools/live.py run --budget-usd 5
```

Setup rebuilds the environment from included source and pinned dependencies. Preflight makes no model calls. Paid execution reruns the published corrected recovery cases, writes new local evidence under `reports/live/`, and leaves historical results and UAT unchanged. These exposed cases are a replication attempt, not new held-out evidence. Read the [live-run guide](docs/LIVE-RUNS.md) for prerequisites, budget accounting, shorter smoke runs, and fresh-result verification.

## Recovery on small AppWorld tasks: design

This is a controlled engineering exploration using custom recovery histories, not an official benchmark or an independently preregistered study.

| Design choice | Implementation |
| --- | --- |
| Question | Compare state/protocol outcomes, latency, and calculated model API cost across execution interfaces under fixed recovery contracts. |
| Controlled components | Same LangChain loop, model, native APIs, initial information, policy safeguards, upper budgets, and terminal-report path. |
| Changed component | Ordinary structured tools versus Cloudflare Code Mode execution. |
| Evaluation sequence | Exposed development qualification is separate from the reserved, source-frozen corrected comparison; the earlier adapter-affected matrix remains separate. |
| Primary outcome | Same-author, separate state/history checker examining intermediate and final effects plus terminal protocol. |
| Secondary measurements | Saved request counts, API calls, latency, token usage, and model API cost. |
| Retention | Both full matrices, expected failures, original programs/errors, and later audits are retained; exposed reruns are not substituted into heldout scores. |
| Limits | Two fresh worlds in familiar families, one repetition, correlated schedules, no independent preregistration or review, and incomplete prose evaluation. |

Read the [experiment history](docs/EXPERIMENT_HISTORY.md), [scenario contracts](docs/SCENARIOS.md), and [oracle limitation](docs/KNOWN-LIMITATIONS.md) alongside the results.

<a id="historical-appworld-results"></a>

## Recovery on small AppWorld tasks: results

The corrected recovery comparison used two previously unused worlds in familiar AppWorld task families, six authored histories, one repetition, and two arms: 24 trials. Both arms used the same LangChain `create_agent` loop, Sonnet model, native backend, approval and field-scope safeguards, notice delivery, and terminal-report path.

| Metric | Ordinary tools | Code Mode |
| --- | ---: | ---: |
| State / structured protocol outcomes | 12/12 | 11/12 |
| Clean / edit goals completed | 6/6 | 6/6 |
| Withdrawal outcomes | 6/6 | 5/6 |
| Invalid effects / lost edits / duplicate payments | 0 / 0 / 0 | 0 / 0 / 0 |
| Mutation requests rejected by the shared gateway | 2 | 2 |
| Model requests | 35 | 38 |
| Native public API calls | 23 | 30 |
| Calculated model API cost (12 trials per arm) | $0.782038 | $0.816218 |
| Median agent time | 12.795 s | 15.549 s |

Zero invalid effects describes the guarded system's observed outcomes; it does not mean the agents never requested a rejected action. The aggregate [rejection counts](study/verification-author.json) do not establish that either model knowingly ignored withdrawal. That requires inspecting the rejection reason and whether withdrawal had reached the model before the request. See the [shared safeguard boundary](docs/ARCHITECTURE.md).

Model API costs are totals across each arm's 12 trials, calculated from saved token usage at the experiment's recorded prices. They exclude infrastructure costs and are not current price quotes.

Ordinary tools were faster in 8/11 jointly successful pairs, with a median paired advantage of 2.734 s. This small, correlated sample does not establish statistical or general superiority. Code Mode realized little batching in this AppWorld matrix; larger workloads are examined separately in the synthetic study above.

The one primary Code Mode failure occurred when an already admitted write settled after withdrawal. Both paired runs achieved the requested external state without forbidden effects. The contract nevertheless required a renewed-approval question: ordinary tools returned `ask`, while Code Mode returned `complete`. This is a failure under the chosen interaction contract, not evidence of an unauthorized write. A product could instead require an accurate explanation that the write settled and no further action will be taken; that would need a separately evaluated contract. See the [saved-case walkthrough](docs/CASE-WALKTHROUGH.md) for the full sequence and evidence.

Both arms also had prose inaccuracies in an unblinded supplementary audit. **A primary pass is not complete end-to-end correctness.**

The earlier adapter-affected recovery comparison has 48 trials and 23/24 primary outcomes per arm. Its Code Mode adapter rejected valid function bodies in 23/24 runs, forcing repairs. Those results and mistakes remain preserved; the adapter-affected and corrected recovery comparisons are never pooled, and repair latency is not subtracted. Read the [experiment history](docs/EXPERIMENT_HISTORY.md).

## What is in this repository?

```text
README.md                 question, results, quickstart, interpretation
docs/                     reviewer guide, reproduction, packaging, release status
study/                    verifier, UAT controls, encrypted source and evidence
  verify.py               unchanged offline verifier
  test_verifier.py        unchanged negative-control suite
  tools/store.mjs         unchanged local encrypted evidence reader
  evidence/               encrypted source, requests, histories, and native snapshots
provenance/               checksums documenting frozen study code and evidence
tools/check_package.py    checks packaged study bytes against the provenance record
tools/live.py             setup, unpaid preflight, new paid runs, fresh-result checks
tools/batching.py         frozen first synthetic study runner and verifier
tools/batching_v2.py      explicit-contract follow-up runner and verifier
tools/verify_batching_v1.py  reproduce earlier synthetic evidence and metrics
tools/verify_batching_v2.py  reproduce latest synthetic evidence and metrics
studies/batching-v1/      unchanged first measured synthetic configuration
studies/batching-v2/      separate return-contract and report-schema condition
results/batching-v1/      preserved earlier runs, hashes, metrics and findings
results/batching-v2/      preserved latest runs, hashes, metrics and findings
live/                     portable orchestration and simulator build definition
.github/                  CI and contribution templates
```

The exact experimental agent implementations, prompts, environment definitions, scenarios, and checkers are preserved inside the evidence store. Use `python3 -E -s -B study/evidence.py` to list logical paths locally. See the [source guide](docs/SOURCE-GUIDE.md). Encryption preserves protected-data distribution boundaries; the public passphrase is packaging, not secrecy.

This repository contains the study, verification/testing code, and live-run setup. Installed dependencies and generated build outputs are excluded. Live dependencies, extracted source, and fresh outputs stay in ignored local directories; see the [live-run guide](docs/LIVE-RUNS.md).

## Review and contribution

An outside engineer should be able to challenge a scenario contract, inspect the shared safeguards and both adapters, reproduce a saved result, and decide whether the study informs an architecture choice. Independent review is **pending**, not implied by passing CI. The [review packet](docs/REVIEW_PACKET.md) gives a bounded review request.

Read [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and [third-party notices](THIRD_PARTY_NOTICES.md). The [release checklist](docs/RELEASE.md) records remaining publication steps. Original project code and editorial documentation use [MIT](LICENSE); separately licensed third-party and derived material retains its applicable terms.

