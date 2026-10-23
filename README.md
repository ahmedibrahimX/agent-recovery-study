# Ordinary tools vs Code Mode: recovery and conditional batching

**How do ordinary structured tools and Code Mode trade correctness, model traffic, latency and cost as workloads grow or human intervention changes the task?**

We compare **ordinary structured tools versus Cloudflare Code Mode** under shared application safeguards. The historical AppWorld study examines small recovery tasks; a measured synthetic reconciliation study adds larger conditional workloads. Each comparison holds the LangChain loop, model, task policy and safeguards fixed while changing the execution interface and its associated instructions. The studies have different tasks and terminal contracts; their pass rates are never pooled.

The historical prototype decision was to start with ordinary tools plus explicit application safeguards. The larger-workload configuration shows batching opportunities alongside return-contract ambiguity, repairs and interruption overhead, without a consistent Code Mode efficiency advantage. These results inform integration choices; they do not establish a general framework ranking, production safety, a new recovery runtime or research novelty.

**Reproducibility:** verify both studies' saved evidence offline, or run new trials with your own API key. The [explicit-contract follow-up](studies/batching-v2/README.md) is separately versioned and has no paid results yet. Independent human review remains pending. Nothing here is an official AppWorld benchmark score or an upstream endorsement.

## What an engineer can learn here

The [first measured batching configuration](results/batching-v1/README.md) has 18 pilot and 54 separate confirmation trials, including raw programs, requests, states and verdicts. Its frozen source remains in [batching-v1](studies/batching-v1/README.md). The [batching-v2 follow-up](studies/batching-v2/README.md) supplies explicit return contracts to both arms and checks the complete report schema without rewriting v1 outcomes.

- Distinguish a mutation request, dispatch admission, commit, result delivery, and exposure of a notice to the model.
- Check intermediate external effects: a final correct database can hide an earlier lost edit.
- Separate safeguards enforced by application code from behavior chosen by an agent.
- See how an execution adapter defect distorted an initial comparison, how it was corrected, and why the original results must remain separate.
- Inspect how ambiguous tool returns, generated-program repairs and batch size affect an interface comparison.
- Reproduce the saved verdicts and inspect an actual failure before accepting the architecture decision.

Start with [one complete saved case](docs/CASE-WALKTHROUGH.md): both interfaces finish an admitted write after withdrawal, but return different terminal statuses. Then use the [reviewer guide](docs/REVIEWER-WALKTHROUGH.md), [architecture](docs/ARCHITECTURE.md), [scenario contracts](docs/SCENARIOS.md), and [claims-to-evidence map](docs/CLAIMS.md).

## Conditional-batching results

The first measured synthetic configuration reconciles 1, 5 or 20 payment-intent statuses under clean, human-edit and between-write withdrawal histories. No money moves. The confirmation uses three fresh seeds, one repetition and both arms: 54 trials, separate from its 18-trial pilot. The default 162-trial matrix was not run.

| Confirmation metric | Ordinary tools | Code Mode |
| --- | ---: | ---: |
| Frozen state/history/selected-protocol outcomes | 26/27 | 27/27 |
| State-integrity passes | 27/27 | 27/27 |
| Model requests | 172 | 227 |
| Public API calls | 691 | 1,039 |
| Guard-denied mutation requests | 13 | 119 |
| Mutation requests after withdrawal reached the model | 0 | 0 |
| Calculated model cost, all 27 attempts per arm | $3.135602 | $4.610532 |

Code Mode was faster in 0/9 jointly successful pairs at size 1, 6/9 at size 5 and 4/8 at size 20. It batched calls but did not consistently reduce model requests, traffic, latency or cost. One ordinary run mistook a note edit for withdrawal and stopped after 8/20 updates. Its Code counterpart eventually completed after 41 model requests and 208.106 seconds; that slow success is excluded from paired-success latency because the ordinary counterpart failed, but retained in costs and per-arm results.

The generated tool return types were `unknown`, and programs repeatedly confused raw values with execution-result wrappers. This is an integration weakness, not evidence that Code Mode inherently needs those repairs. The frozen checker also accepts extra report keys: two passing confirmation reports include an extra `code` field. These passes validate selected claims, not the complete closed schema or prose truthfulness. The guard prevents forbidden effects but does not establish independent agent judgment.

Read the [full findings, size/history breakdowns, paired walkthrough and limitations](results/batching-v1/README.md). The pilot's stronger size-20 advantage is reported separately, not pooled or substituted. A [new contract condition](studies/batching-v2/README.md) addresses return documentation and report validation together; it cannot isolate their individual causal effects, and has no paid findings yet.

## Reproduce the saved results

Requirements: Python **3.12+** with SQLite `deserialize`, Node **22+**, and about 200 MB temporary free space. Saved-result verification runs entirely offline using the included evidence. It requires only Python and Node.js.

From the repository root:

```sh
python3 tools/check_package.py
python3 -E -s -B study/verify.py
python3 -E -s -B -m unittest discover -s study -p test_verifier.py -v
python3 -B tools/verify_batching_v1.py
```

Expected: the verifier authenticates 5,369 logical files across 3,257 unique blobs and reproduces **48 v6 saved verdicts and 24 v7 saved verdicts, reported separately**. All five negative controls pass. A zero exit code means the saved evidence reproduces, **including expected agent failures**; it does not mean all agents passed.

The historical checker validates state and parts of the structured protocol, not complete prose truthfulness. It has a [question-type validation gap](docs/KNOWN-LIMITATIONS.md); all 33 saved approval questions were checked and have valid string types. The batching verifier separately reproduces 54 confirmation, 18 pilot and 18 unpaid preflight trials, including the expected ordinary failure, with every saved run file preserved. Verification rechecks saved clocks and usage; it does not remeasure hosted model speed. See [what reproduction means](docs/REPRODUCING.md) and the [validation record](docs/VALIDATION.md).

## Run new trials

For the synthetic explicit-contract follow-up, no Docker is needed:

```sh
python3 tools/batching_v2.py setup
python3 tools/batching_v2.py preflight
python3 tools/batching_v2.py plan --repetitions 1 --output reports/batching-v2/followup-plan.json
```

This freezes a fresh 54-trial plan. Paid execution additionally needs your API key and an explicit budget; follow the [v2 run guide](studies/batching-v2/README.md). New results stay separate from measured v1 evidence.

For a replication of the historical AppWorld study:

With Python, Node/npm, and Docker running:

```sh
python3 tools/live.py setup
python3 tools/live.py preflight
export ANTHROPIC_API_KEY='<your Anthropic API key>'
python3 tools/live.py run --budget-usd 5
```

Setup rebuilds the environment from included source and pinned dependencies. Preflight makes no model calls. Paid execution reruns the published v7 cases, writes new local evidence under `reports/live/`, and leaves historical results and UAT unchanged. These exposed cases are a replication attempt, not new held-out evidence. Read the [live-run guide](docs/LIVE-RUNS.md) for prerequisites, budget accounting, shorter smoke runs, and fresh-result verification.

## Historical AppWorld experimental design

This is a controlled engineering exploration using custom recovery histories, not an official benchmark or an independently preregistered study.

| Design choice | Implementation |
| --- | --- |
| Question | Compare state/protocol outcomes, latency, and calculated model API cost across execution interfaces under fixed recovery contracts. |
| Controlled components | Same LangChain loop, model, native APIs, initial information, policy safeguards, upper budgets, and terminal-report path. |
| Changed component | Ordinary structured tools versus Cloudflare Code Mode execution. |
| Evaluation sequence | Exposed development qualification is separate from the reserved, source-frozen v7 evaluation; the earlier v6 matrix remains separate. |
| Primary outcome | Same-author, separate state/history checker examining intermediate and final effects plus terminal protocol. |
| Secondary measurements | Saved request counts, API calls, latency, token usage, and model API cost. |
| Retention | Both full matrices, expected failures, original programs/errors, and later audits are retained; exposed reruns are not substituted into heldout scores. |
| Limits | Two fresh worlds in familiar families, one repetition, correlated schedules, no independent preregistration or review, and incomplete prose evaluation. |

Read the [experiment history](docs/EXPERIMENT_HISTORY.md), [scenario contracts](docs/SCENARIOS.md), and [oracle limitation](docs/KNOWN-LIMITATIONS.md) alongside the results.

## Historical AppWorld results

The final comparison (v7) used two previously unused worlds in familiar AppWorld task families, six authored histories, one repetition, and two arms: 24 trials. Both arms used the same LangChain `create_agent` loop, Sonnet model, native backend, approval and field-scope safeguards, notice delivery, and terminal-report path.

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

The earlier v6 study has 48 trials and 23/24 primary outcomes per arm. Its Code Mode adapter rejected valid function bodies in 23/24 runs, forcing repairs. Those results and mistakes remain preserved; v6 and v7 are never pooled, and repair latency is not subtracted. Read the [experiment history](docs/EXPERIMENT_HISTORY.md).

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
tools/verify_batching_v1.py  reproduce preserved synthetic evidence and metrics
studies/batching-v1/      unchanged first measured synthetic configuration
studies/batching-v2/      separate return-contract and report-schema condition
results/batching-v1/      preserved run archives, hashes, metrics and findings
live/                     portable orchestration and simulator build definition
.github/                  CI and contribution templates
```

The exact experimental agent implementations, prompts, environment definitions, scenarios, and checkers are preserved inside the evidence store. Use `python3 -E -s -B study/evidence.py` to list logical paths locally. See the [source guide](docs/SOURCE-GUIDE.md). Encryption preserves protected-data distribution boundaries; the public passphrase is packaging, not secrecy.

This repository contains the study, verification/testing code, and live-run setup. Installed dependencies and generated build outputs are excluded. Live dependencies, extracted source, and fresh outputs stay in ignored local directories; see the [live-run guide](docs/LIVE-RUNS.md).

## Review and contribution

An outside engineer should be able to challenge a scenario contract, inspect the shared safeguards and both adapters, reproduce a saved result, and decide whether the study informs an architecture choice. Independent review is **pending**, not implied by passing CI. The [review packet](docs/REVIEW_PACKET.md) gives a bounded review request.

Read [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and [third-party notices](THIRD_PARTY_NOTICES.md). The [release checklist](docs/RELEASE.md) records remaining publication steps. Original project code and editorial documentation use [MIT](LICENSE); separately licensed third-party and derived material retains its applicable terms.

