# Claims to evidence

## Conditional batching

The public synthetic run archives are separate from the encrypted historical AppWorld store. Run `python3 -B tools/verify_batching_v2.py` or `python3 -B tools/verify_batching_v1.py` from the repository root.

| Claim | Evidence | Boundary |
| --- | --- | --- |
| Batching with explicit tool contracts passes 27/27 in each arm, including full report schema | [Preserved runs and metrics](../results/batching-v2/README.md), `case.json`, `evidence.json`, `report.json`, `verdict.json`, frozen checker | Same-author checker and shared schema validator; correct withdrawal can leave work incomplete; prose truth is not comprehensively graded. |
| With explicit tool contracts, Code is faster in all nine size-20 pairs and uses fewer model requests at lower calculated cost | `results/batching-v2/metrics.json`, archived provider requests/responses/usage, clocks, CSV and comparisons | Three correlated seeds, one trial per case/arm, one provider/model and synthetic latency. Smaller sizes usually favor ordinary tools. No universal crossover. |
| Substantive batching occurs | Case `batching-v2-cc729b0c4f83`: Code blocks chain 40 dependent reads, then perform 20 updates; ordinary requests batch reads but split writes | Observed model strategy, not an intrinsic minimum turn count for structured tools. Code's overall public-call count is higher. |
| Guard protection and agent stopping are distinct | Both batching studies' journals, guard events and actual provider input exposure | The explicit-contract study has 23/33 denied mutations and zero mutation requests after model exposure. Request arrival can precede withdrawal while admission follows it. |
| The explicit-contract study includes reporting repair | Case `batching-v2-24b2e54eaf6a`: two rejected terminals and later accepted report, six model requests | One malformed model submission plus one adapter fallback resubmission, not two independent model mistakes. Full time/cost retained. |
| Initial batching limitations and original outcomes remain visible | [Initial batching result record](../results/batching-v1/README.md), file manifests, unchanged source, separate pilot/confirmation | No rescoring, selected replacements, repair subtraction or pooling. Multiple condition changes prevent an output-schema-only causal claim. |

## Historical AppWorld

Paths below refer to the encrypted archive's logical file listing. Use `evidence.py` locally.

| Claim | Evidence | Boundary |
|---|---|---|
| The corrected recovery comparison has 24 reserved runs, 12/12 versus 11/12 outcomes | `experiments/live-v7/heldout.json`, `freeze.json`; v7 study `case.json`, `verdict.json`, history and native SQLite | Custom structured/state oracle; not comprehensive prose correctness. |
| No observed invalid effects, lost edits or duplicates | Each paid run's initial/intermediate/final DBs and history; exact frozen checker | Finite simulator evidence under shared guards; not a production guarantee. |
| Corrected speed and cost differences | v7 `runner.json`, `model-*-response.json`, `model-usage.json`, native history clocks, ledger before/after | Saved timing; small, noisy, correlated sample; no significance/general ranking. |
| Little batching materialized | v7 original `program-*.js`, `outputs.json`, public journals and call counters | Does not prove why the model chose its trajectory or measure larger workloads. |
| Both arms saw equivalent initial information | Paired `initial-context.json`, public native interfaces, frozen prompts | Opaque tokens normalized; tool schemas and subsequent observations naturally differ. |
| The earlier recovery adapter caused format repairs | All original v6 programs/errors/provider requests, v6/v7 envelope code | Keep v6 separate. No repair-latency subtraction. |
| Prose reports can mislead despite primary pass | v7 manual-report-audit and original submission/request/history | Supplementary, unblinded, incomplete review. |
| Prior parser corrections changed diagnostics | `experiments/reporting-v4/`, v3 audit, completed summaries | Historical raw failures removed; not independently reconstructable. |
| No new recovery runtime warranted so far | Full case-study reasoning and limitations | Engineering decision within this scope; not proof of no possible research gap. |

No claim of production traffic coverage, official AppWorld performance, independent review, security certification, cross-service exactly-once effects, durable recovery, new research novelty, or business demand is made.
