# Claims to evidence

Paths below refer to the encrypted archive's logical file listing. Use `evidence.py` locally.

| Claim | Evidence | Boundary |
|---|---|---|
| v7 has 24 reserved runs, 12/12 versus 11/12 outcomes | `experiments/live-v7/heldout.json`, `freeze.json`; v7 study `case.json`, `verdict.json`, history and native SQLite | Custom structured/state oracle; not comprehensive prose correctness. |
| No observed invalid effects, lost edits or duplicates | Each paid run's initial/intermediate/final DBs and history; exact frozen checker | Finite simulator evidence under shared guards; not a production guarantee. |
| Corrected speed and cost differences | v7 `runner.json`, `model-*-response.json`, `model-usage.json`, native history clocks, ledger before/after | Saved timing; small, noisy, correlated sample; no significance/general ranking. |
| Little batching materialized | v7 original `program-*.js`, `outputs.json`, public journals and call counters | Does not prove why the model chose its trajectory or measure larger workloads. |
| Both arms saw equivalent initial information | Paired `initial-context.json`, public native interfaces, frozen prompts | Opaque tokens normalized; tool schemas and subsequent observations naturally differ. |
| v6 adapter caused format repairs | All original v6 programs/errors/provider requests, v6/v7 envelope code | Keep v6 separate. No repair-latency subtraction. |
| Prose reports can mislead despite primary pass | v7 manual-report-audit and original submission/request/history | Supplementary, unblinded, incomplete review. |
| Prior parser corrections changed diagnostics | `experiments/reporting-v4/`, v3 audit, completed summaries | Historical raw failures removed; not independently reconstructable. |
| No new recovery runtime warranted so far | Full case-study reasoning and limitations | Engineering decision within this scope; not proof of no possible research gap. |

No claim of production traffic coverage, official AppWorld performance, independent review, security certification, cross-service exactly-once effects, durable recovery, new research novelty, or business demand is made.
