# Find the implementation and evidence

The study has two layers: documentation under `docs/` and executable code/evidence under `study/`. Its experimental source/evidence is stored encrypted with content-addressed blobs. The source is inspectable locally through the existing reader.

From the repository root:

```sh
python3 -E -s -B study/evidence.py
python3 -E -s -B study/evidence.py experiments/live-v7/langchain_agent.py
```

The first command lists protected logical paths. The second prints the exact agent implementation locally. Do not paste decrypted task-derived code, prompts, inputs, or snapshots into public issues or screenshots.

The [complete case walkthrough](CASE-WALKTHROUGH.md) provides exact logical paths and local inspection commands for a paired saved outcome, so a reviewer can start with one case rather than the entire catalog.

| Review question | Logical source/evidence path |
| --- | --- |
| What does each agent see and how is its loop controlled? | `experiments/live-v7/langchain_agent.py` |
| Where are approval admission, schedules, and native effects implemented? | `experiments/live-v6/service.py` |
| How do ordinary tools and code execution differ? | `experiments/live-v7/runner.mjs` and `prompts.mjs` |
| What changed after the v6 envelope defect? | `experiments/live-v7/code-envelope.mjs`, v6/v7 original programs and errors |
| What does the oracle actually check? | `experiments/live-v7/checker.py` (same bytes as v6) |
| Were source and inputs frozen? | v7 `freeze.json`, `reservation.json`, and `heldout.json` |
| Which environments were used? | v7 `environment.json`, `requirements.lock.txt`, preserved lockfiles |
| Where are original observations and side effects? | v6/v7 heldout run folders: model requests/responses, histories, intermediate/final SQLite |
| Which report inaccuracies were recorded? | `experiments/live-v7-audit/` and associated manual-report audit files |

Exact task identifiers and native API details stay in protected storage. Listing the store locally gives the full evidence tree without putting decrypted benchmark material in the public source tree.

Retained experimental sources, environment definitions, and evidence are included in the authenticated store. Verification and inspection do not depend on a separate private checkout or external evidence download.

