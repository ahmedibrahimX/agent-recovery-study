# Batching with explicit tool contracts: measured results

**In this run, ordinary tools usually favored 1- and 5-intent tasks. At 20 intents, Code Mode was faster in all nine pairs, with fewer model requests and lower calculated model cost, while making more public API calls.** Both arms passed all 27 state/history/full-report-schema outcomes. This supports a workload-dependent integration decision, not a universal crossover, general framework ranking or production-recovery claim.

## Design and source identity

The source is frozen at commit `bdf4880945c945f4fbc78b0d2bf21ada19b73778`. The paid plan SHA-256 is `416bac1af2611b89e576310166c43c31b06c11ffcacf07f3644b9c9478d22b2d`. One invocation recorded all 54 planned trials without whole-trial retries or replacements:

| Factor | Condition |
| --- | --- |
| Workload | Public synthetic payment-intent status reconciliation; no money moves |
| Sizes | 1, 5, 20 intents |
| Histories | Clean, stale-list human-note edit, between-write approval withdrawal |
| Fixture seeds | `2026102401`, `2026102407`, `2026102413` |
| Repetitions | One per case and arm; 27 paired cases |
| Agent/model | Same LangChain `create_agent` loop and `claude-sonnet-5` identifier |
| Interfaces | Ordinary structured tools, allowing parallel calls; Cloudflare Code Mode in local `workerd` |
| Shared service | Concurrency four, injected 20 ms delay per call, status-only authority, per-write approval guard, model-notice terminal gate |
| Return contracts | Explicit success schemas and raw-value/wrapper/error documentation supplied to both arms; Code receives SDK-generated output types |
| Report contract | Full closed schema at submission and offline grading; no coercion or extra-field stripping |
| Upper limits | 128 model requests, 512 public calls, 128 code blocks, 8,192 output tokens, 1 MB request, 600 seconds per trial |

Cases, source identities, model, limits, accounting rates and case/arm order were frozen before execution. No agent, prompt, policy, limit or grading changes were made during the run. The generator is public and the source freeze is local, not independent preregistration. The separately retained unpaid preflight has 18 scripted trials and is not capability evidence.

## Outcomes and efficiency

| All-attempt outcome | Ordinary tools | Code Mode |
| --- | ---: | ---: |
| Primary outcomes | 27/27 | 27/27 |
| State integrity / committed classification / full report schema | 27/27 each | 27/27 each |
| Original full goal reached | 21/27 | 21/27 |
| Correct partial stops after withdrawal | 6 | 6 |
| Model requests | 185 | 126 |
| Public API calls | 714 | 804 |
| Execution blocks | — | 98 |
| Tool-result bytes presented to model, including repeated history | 1,373,795 | 644,132 |
| Committed updates / repeated committed updates | 195 / 0 | 195 / 0 |
| Guard-denied mutation requests | 23 | 33 |
| Mutation requests after withdrawal reached recorded model input | 0 | 0 |
| Rejected terminal submissions | 0 | 2 |
| Calculated model cost | $4.027068 | $2.354418 |

A withdrawal trial can pass without finishing the original full task. Both arms correctly stopped with partial work in the six size-5/20 withdrawal cases. Size-1 withdrawal occurs after its sole update; the original goal is already reached. A primary pass does not mean error-free execution or complete prose truthfulness.

| Intents | Median agent seconds, ordinary / Code | Code faster, agent and full elapsed | Median paired Code minus ordinary agent seconds | All-attempt cost, ordinary / Code |
| --- | ---: | ---: | ---: | ---: |
| 1 | 10.775 / 12.536 | 2/9 | +1.984 | $0.392954 / $0.416298 |
| 5 | 21.421 / 23.593 | 3/9 | +3.697 | $0.685658 / $0.705316 |
| 20 | 59.008 / 35.959 | 9/9 | −23.077 | $2.948456 / $1.232804 |

There are nine attempted trials per arm at each size. All pairs passed, so no failed counterpart is excluded from paired comparisons. Arm medians and medians of paired differences are different statistics; subtracting the two arm medians does not reproduce the paired result. Agent time includes framework/Python startup; full elapsed additionally includes worker cold setup/cleanup. All in-trial repairs remain included. Median full elapsed at size 20 is 59.122 seconds ordinary versus 36.256 Code, with a paired median advantage of 22.998 seconds for Code.

At size 20, Code uses 42 versus 93 model requests and costs $1.232804 versus $2.948456 (58.2% lower calculated cost), but makes 616 versus 533 public calls. It is faster in all three clean, all three edit and all three withdrawal pairs. The [machine-readable metrics](metrics.json) retain separate size/history groups. The fixed matrix's aggregate cost advantage is driven by larger workloads and is not an estimate for an arbitrary production task mix.

Costs use the plan's recorded per-million-token rates: input $2, output $10, cache creation $2.50 and cache read $0.20. They are not provider invoices, current price quotes or total infrastructure costs. Tool-result bytes count result content in repeated model-request history, not total network wire traffic. Model time is provider round-trip time; residual time is not isolated sandbox CPU. Offline verification rechecks saved clocks and usage, not hosted model latency.

## Inspect one paired batching trajectory

Case `batching-v2-cc729b0c4f83` is size 20, clean, seed `2026102413`. Its archived paths start with that case ID, followed by `ordinary/` or `code/`.

1. Both arms list the same 20 intents and use 61 public API calls. Ordinary tools use nine model requests; Code uses four. Both update all 20 statuses correctly and pass the same state/history/schema checks.
2. Code `program-0.json` lists intents. `program-1.json` chains each recipient lookup into its dependent ledger lookup, using 40 public calls inside one execution block. It returns the observations to the model. This trajectory does not perform classification entirely inside the program.
3. Code `program-2.json` performs 20 status-only updates from model-produced classifications, in batches of four within one block. Public service concurrency remains four in both arms; this is fewer model transitions, not a higher concurrency allowance.
4. Ordinary responses issue parallel recipient and ledger calls, then split writes across additional model turns. Its interface allows more parallel writes; the observed grouping is a model strategy, not an intrinsic lower bound for structured tools.
5. Retained timings/costs are 59.008 seconds and $0.324964 ordinary, versus 38.730 seconds and $0.132674 Code. Read `blocks.json`, `program-*.json`, provider requests/responses, `evidence.json`, `report.json` and `verdict.json` to reproduce the sequence.

This shows substantive chaining/batching without assuming every Code trajectory returns compact summaries, processes all data locally, or uses the minimum possible API calls.

## Errors, guard boundaries and reporting repairs

There are no primary trial failures, but there are 57 failed public results: 56 approval-withdrawn guard denials and one ordinary read error. In `batching-v2-11eef6c08a7c/ordinary`, the model speculatively supplies a recipient ID as a ledger account before reading the correct account. The next request corrects it. The only Code program-level error is `approval_withdrawn` in `batching-v2-f2a79037e18e/code`; it is retained as part of correct eventual stopping.

Ordinary tools log zero mutation-request arrivals after withdrawal but 23 guard denials: those calls arrived earlier and reached their queued admission checks later. Code logs 24 arrivals after withdrawal and 33 denials. Arrival, admission, effect and notice exposure are different boundaries. Neither arm requests a mutation after the notice reaches an actual recorded model request. Generated programs can encounter a rejection before the next model request; those exposure counts do not prove that the program was unaware of the rejection. Guards are shared deterministic application engineering.

In `batching-v2-24b2e54eaf6a/code` (size 20, clean, seed `2026102401`), a model report includes an extra `code` field. The gate rejects it. The unchanged agent fallback parses that tool rejection as a prospective report and resubmits it, causing a second rejection without another model request. The next model request corrects the report, which passes. These are one malformed model submission and an adapter fallback quirk, not two independent model mistakes. Both journal records, all six model requests, 51.717 seconds and $0.200566 remain included. The frozen adapter is not silently fixed here.

The schema gate rejects shape defects; it does not supply the correct IDs, counts or classifications. State/history and semantic claims are separately checked. The gate and offline checker share a same-author schema validator, so negative controls are not independent implementation certification. Final prose still lacks comprehensive independent human review.

## Preserve the full experiment sequence

[The initial batching experiment](../batching-v1/README.md) remains visible and unchanged: its separate pilot and confirmation, mixed efficiencies, ambiguous return values, long repairs, premature ordinary stop and incomplete report-schema coverage are all retained. The [historical AppWorld study](../../README.md#historical-appworld-results) remains separate as well.

The follow-up jointly changes return schemas, wrapper/error documentation and report admission/grading, uses fresh fixtures and runs later against a hosted provider. The results do not isolate an output-schema effect. Different contracts also prevent pass rates from the initial batching experiment, the follow-up and the AppWorld study from being compared as a single score. Do not pool the studies, replace failures, subtract repair time, or hide the earlier configuration.

There are only three unique fixture seeds and one trial per case/arm. Sizes share prefixes and histories are correlated. Service latency is synthetic and provider/host conditions are noisy. There are no significance, population reliability or immutable-provider-internals claims. The edit changes a note, not classification inputs: it tests stale-read field preservation, not replanning changed business facts. Withdrawal is between writes with no preemption; no real human approval/resume cycle, payment creation, process restart, durable execution or cross-service atomicity is evaluated. Independent engineer review remains pending.

## Verify saved evidence offline

Python 3.12+ and Node 22+ are sufficient; no model calls, API key, dependency installation, Docker or generated-program execution is needed:

```sh
python3 -B tools/verify_batching_v2.py
```

The command verifies archive hashes and every original file byte, then uses the frozen verifier to reproduce source/plan identities, fixtures, verdicts, usage/cost, CSV and comparisons. It also recomputes `metrics.json` from all attempted outcomes. The two archives preserve all 2,151 original paid/unpaid run files, including requests/responses, programs/results, terminal attempts, snapshots, logs and budgets. Provider credentials and installed dependencies/build outputs are not included. Hashes establish integrity against this record, not independent provider provenance.

For trace inspection after verification:

```sh
mkdir -p /tmp/batching-v2-paid
tar -xzf results/batching-v2/paid.tar.gz -C /tmp/batching-v2-paid
```

The measured source stays unchanged in `studies/batching-v2/` and `tools/batching_v2.py`. Its pre-execution README/protocol status text is intentionally frozen because plans hash those files. This results record and the root README provide the current measured status. Use the [frozen run guide](../../studies/batching-v2/README.md) for exposed replication; the included cases are no longer unseen evaluation evidence.
