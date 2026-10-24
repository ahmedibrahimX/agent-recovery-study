# How the investigation developed

This investigation compares ordinary structured tools and Code Mode. Each study answers a narrower question and exposes the next uncertainty; the studies are not a single pooled benchmark or an independently preregistered research program.

## Recovery on small AppWorld tasks

The original recovery study examined human edits and approval withdrawal around external effects. Under shared application safeguards, the corrected comparison produced 12/12 ordinary and 11/12 Code primary outcomes, with no checked invalid effects, lost edits or duplicate payments. The Code failure concerned a required renewed-approval response after an admitted write settled, not a forbidden committed effect. Both arms also had prose inaccuracies outside complete automatic grading.

Small tasks offered little batching, so these results did not measure Code Mode's potential benefit on substantial dependent workloads. An earlier recovery comparison was also distorted by an adapter rejecting valid code forms: 23/24 Code trials incurred repairs. All 48 affected trials remain separate from the 24 corrected trials, with full repair time retained. Read the [recovery results](../README.md#recovery-on-small-appworld-tasks-results) and [paired withdrawal walkthrough](CASE-WALKTHROUGH.md).

## Initial batching experiment

The next study introduced synthetic status-reconciliation workloads of 1, 5 and 20 intents under clean, note-edit and between-write withdrawal histories. These are simulated human-in-the-loop conditions: the harness injects interventions, and the agent must preserve the newer note or stop and report completed versus remaining work. No live person approves resumption, and the batching contract does not require a renewed-approval question. Its 18-trial pilot and separate 54-trial confirmation remain intact. Confirmation outcomes were 26/27 ordinary versus 27/27 Code, without a consistent Code efficiency advantage.

The traces exposed ambiguous raw tool returns versus execution wrappers, lengthy generated-code repairs, one ordinary premature stop, and a checker that validated selected report claims while accepting extra root fields. These were integration and measurement limitations worth investigating, not evidence that either interface is generally superior. The [original results, failures and limits](../results/batching-v1/README.md) remain public and unchanged.

## Batching with explicit tool contracts

The follow-up supplied explicit success-return schemas and wrapper/error documentation to both arms, and enforced the full closed report schema at admission and offline grading. The same clean, simulated human-edit and withdrawal histories remain part of the follow-up; batching efficiency and intervention handling are evaluated together. Fresh fixture seeds and one repetition produced 54 paid trials. Both arms passed 27/27. Ordinary tools were usually faster and slightly cheaper at sizes 1/5; Code was faster in all nine size-20 pairs, using fewer model requests at lower calculated cost while making more public API calls.

The [results record](../results/batching-v2/README.md) retains every attempted outcome, denied mutation and reporting repair, including the adapter fallback quirk. Return documentation, report admission/grading, fixture seeds and execution conditions changed together. The observed differences cannot isolate output-schema causality or locate a universal crossover. Earlier outcomes were not rescored, replaced or pooled.

## Technical identity map

Descriptive names organize the public narrative. Frozen identifiers remain in plans, source directories, run IDs and verifier output so an engineer can find the exact bytes:

| Investigation / configuration | Frozen technical identifier | Source and evidence |
| --- | --- | --- |
| Recovery on small AppWorld tasks, adapter-affected comparison | `live-v6` | Encrypted archive logical paths; 48 paid trials |
| Recovery on small AppWorld tasks, corrected comparison | `live-v7` | Encrypted archive logical paths; 24 paid trials |
| Initial batching experiment | `batching-v1` | Source at `6b30ae1`, `studies/batching-v1/`, `results/batching-v1/`; separate pilot/confirmation |
| Batching with explicit tool contracts | `batching-v2` | Source at `bdf4880`, `studies/batching-v2/`, `results/batching-v2/`; 54 paid trials |

Measured source, prompts, checkers, UAT and evidence remain byte-for-byte unchanged. Source-local README/protocol text preserves its pre-execution status because it is included in plan hashes; the root README and results records provide current findings. Study names are editorial descriptions, not new experiments or renamed artifacts.

## Earlier recovery exploration and corrections

The detailed record below retains preliminary configurations and diagnostics. Some early raw histories were deleted before public packaging; surviving source and summaries do not restore those observations. Complete saved-state verification exists for both retained recovery matrices and, separately, for the public synthetic batching evidence. Exposure status and denominators must stay attached to each configuration.

This is an exploratory sequence, not a single preregistered benchmark. Preserve each version's denominator and exposure status.

| Stage | Problem / change | How to interpret it |
|---|---|---|
| Early synthetic account histories | Output/request caps, refusal diagnosis, old B-pause fixture, receipt-service error handling, native type generation and compact JSON control were investigated in versioned sources. | Engineering qualifications; do not turn them into a consolidated framework score. Earlier raw bundles were deleted during storage cleanup; retained summaries cannot independently reproduce these results. |
| Adaptive comparison v3 | Compared ordinary tools, Code Mode, Cloudflare + Temporal and Codex. Model/loop/reporting differences included a different Codex model and unpriced subscription cost. | Historical exploration, not a controlled framework ranking. |
| Reporting v4 diagnostic | Accept one unambiguous terminal JSON after prose/fences and Codex final-answer callback; no semantic status/reason repair. | Offline parser correction and selected exposed-case reruns, not new held-out evidence. No best-of pooling. |
| Live v5 | Unequal control paths/notice handling and no equivalent shared write guards; event-clock instrumentation was corrected before heldout. | Motivated common safeguards. Cannot attribute differences solely to Temporal or Code Mode. Raw histories removed earlier. |
| Live v6 | Shared create_agent loop, approval/field guards, terminal pending-input gate. Code adapter unnecessarily required a full async arrow. | Keep all 48 trials: 23/24 Code Mode trials incurred format repair. Do not use their timing to rank intrinsic runtimes. |
| Live v7 | Mechanical function-body wrapping and interface description corrected; backend, checker, model and safeguards unchanged. Four unpaid equivalence checks and four paid development trials qualified it. Fresh worlds reserved before tuning/freeze. | All 24 new trials retained; corrected comparison reported separately. No repair-time subtraction or selected success replacement. |
| Supplementary audits | Timing decomposition, guard-boundary audit and manual prose inspection were added after exposure. | Explanatory diagnostics; no changes to primary outcomes. Manual audit was unblinded and incomplete. |

v3's original outcome counts were 19/20 ordinary tools, 17/20 LangChain Code Mode, 16/20 Cloudflare + Temporal, 16/20 Codex. v4 parsing reinterpretation changed these to 19/20, 18/20, 16/20, 19/20 on the same trajectories. Twelve selected exposed failures were rerun once; 11/12 passed and all four previously dropped reports parsed. These are **diagnostic counts**, not an improved headline sample. The old raw failed model traces no longer exist. Frozen parser regression tests, source and compact summaries remain encrypted; they are not substitutes for original traces.

All v6/v7 paid raw trials, including failed responses/programs and every retained native snapshot, are preserved losslessly. Earlier cleanup manifests document intentional deletions; these records do not restore missing evidence. The encrypted archive also preserves current development/preflight files, some of which had previously lost redundant snapshots. Within this encrypted historical archive, only the paid v6/v7 matrices have complete saved-state verification. Public synthetic batching runs are preserved and verified separately.

The current archive is a deduplicated content store, not a new experiment. Packing and offline checks do not tune agents or change verdicts. Hashes prove consistency with these retained files, not independent provenance or external review.
