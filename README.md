# Agent recovery: an engineering case study

**How should a tool-using agent behave when a person edits external state or withdraws approval while the agent is working?**

We compared existing agent approaches on small, controlled recovery scenarios, checking actual external effects, response protocol, latency, and model API cost. The corrected comparison holds the LangChain agent loop and application safeguards fixed, and changes the execution interface: **ordinary structured tools versus Cloudflare Code Mode**.

The practical decision for this bounded prototype was to start with ordinary tools plus explicit application safeguards. The study found no demonstrated need for a new recovery runtime. It does not establish a general framework ranking, production safety, or research novelty.

**Reproducibility:** saved-result verification is available; independent human review and fresh live reexecution are pending. Nothing in this package is an official AppWorld benchmark score or an upstream endorsement.

## What an engineer can learn here

- Distinguish a mutation request, dispatch admission, commit, result delivery, and exposure of a notice to the model.
- Check intermediate external effects: a final correct database can hide an earlier lost edit.
- Separate safeguards enforced by application code from behavior chosen by an agent.
- See how an execution adapter defect distorted an initial comparison, how it was corrected, and why the original results must remain separate.
- Reproduce the saved verdicts and inspect an actual failure before accepting the architecture decision.

Start with the [five-minute reviewer walkthrough](docs/REVIEWER-WALKTHROUGH.md). The [architecture](docs/ARCHITECTURE.md), [scenario contracts](docs/SCENARIOS.md), and [claims-to-evidence map](docs/CLAIMS.md) provide the technical detail.

## Reproduce the saved results

Requirements: Python **3.12+** with SQLite `deserialize`, Node **22+**, and about 200 MB temporary free space. No package installation, Docker, API key, or model call is required after obtaining this repository and those runtimes.

From the repository root:

```sh
python3 tools/check_package.py
python3 -E -s -B study/verify.py
python3 -E -s -B -m unittest discover -s study -p test_verifier.py -v
```

Expected: the verifier authenticates 5,369 logical files across 3,257 unique blobs and reproduces **48 v6 saved verdicts and 24 v7 saved verdicts, reported separately**. All five negative controls pass. A zero exit code means the saved evidence reproduces, **including expected agent failures**; it does not mean all agents passed.

The checker validates state and parts of the structured protocol, not complete prose truthfulness. It has a [question-type validation gap](docs/KNOWN-LIMITATIONS.md); all 33 saved approval questions were checked and have valid string types. Verification rechecks saved clocks and usage; it does not remeasure hosted model speed. See [what reproduction means](docs/REPRODUCING.md) and the [validation record](docs/VALIDATION.md).

## Experimental design

This is a controlled engineering exploration using custom recovery histories, not an official benchmark or an independently preregistered study.

| Design choice | Implementation |
| --- | --- |
| Question | Compare ordinary tools and code execution under the same recovery contracts. |
| Controlled components | Same LangChain loop, model, native APIs, initial information, policy safeguards, upper budgets, and terminal-report path. |
| Changed component | Ordinary structured tools versus Cloudflare Code Mode execution. |
| Evaluation sequence | Exposed development qualification is separate from the reserved, source-frozen v7 evaluation; the earlier v6 matrix remains separate. |
| Primary outcome | Same-author, separate state/history checker examining intermediate and final effects plus terminal protocol. |
| Secondary measurements | Saved request counts, API calls, latency, token usage, and model API cost. |
| Retention | Both full matrices, expected failures, original programs/errors, and later audits are retained; exposed reruns are not substituted into heldout scores. |
| Limits | Two fresh worlds in familiar families, one repetition, correlated schedules, no independent preregistration or review, and incomplete prose evaluation. |

Read the [experiment history](docs/EXPERIMENT_HISTORY.md), [scenario contracts](docs/SCENARIOS.md), and [oracle limitation](docs/KNOWN-LIMITATIONS.md) alongside the results.

## Results

The final comparison (v7) used two previously unused worlds in familiar AppWorld task families, six authored histories, one repetition, and two arms: 24 trials. Both arms used the same LangChain `create_agent` loop, Sonnet model, native backend, approval and field-scope safeguards, notice delivery, and terminal-report path.

| Metric | Ordinary tools | Code Mode |
| --- | ---: | ---: |
| State / structured protocol outcomes | 12/12 | 11/12 |
| Clean / edit goals completed | 6/6 | 6/6 |
| Withdrawal outcomes | 6/6 | 5/6 |
| Invalid effects / lost edits / duplicate payments | 0 / 0 / 0 | 0 / 0 / 0 |
| Model requests | 35 | 38 |
| Native public API calls | 23 | 30 |
| Calculated model API cost (12 trials per arm) | $0.782038 | $0.816218 |
| Median agent time | 12.795 s | 15.549 s |

Model API costs are totals across each arm's 12 trials, calculated from saved token usage at the experiment's recorded prices. They exclude infrastructure costs and are not current price quotes.

Ordinary tools were faster in 8/11 jointly successful pairs, with a median paired advantage of 2.734 s. This small, correlated sample does not establish statistical or general superiority. Code Mode realized little batching; larger batch workloads were not tested.

The one primary Code Mode failure occurred when an already admitted write settled after withdrawal. The effect was permitted, but the agent reported completion instead of asking for renewed approval. Both arms also had prose inaccuracies in an unblinded supplementary audit. **A primary pass is not complete end-to-end correctness.**

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
.github/                  CI and contribution templates
```

The exact experimental agent implementations, prompts, environment definitions, scenarios, and checkers are preserved inside the evidence store. Use `python3 -E -s -B study/evidence.py` to list logical paths locally. See the [source guide](docs/SOURCE-GUIDE.md). Encryption preserves protected-data distribution boundaries; the public passphrase is packaging, not secrecy.

This repository contains the study and its verification/testing code. Python and Node run the saved-result checks. Installed dependencies and generated build outputs are excluded. Fresh live execution has separate setup requirements, described in the reproduction guide.

## Review and contribution

An outside engineer should be able to challenge a scenario contract, inspect the shared safeguards and both adapters, reproduce a saved result, and decide whether the study informs an architecture choice. Independent review is **pending**, not implied by passing CI. The [review packet](docs/REVIEW_PACKET.md) gives a bounded review request.

Read [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and [third-party notices](THIRD_PARTY_NOTICES.md). The [release checklist](docs/RELEASE.md) records remaining publication steps. Original project code and editorial documentation use [MIT](LICENSE); separately licensed third-party and derived material retains its applicable terms.

