# Offline verification versus a fresh experiment

`python3 -E -s -B study/verify.py` needs Python 3.12+ (SQLite deserialize enabled), Node 22+, no third-party packages, and the included study files. Tested on Python 3.12.12, SQLite as provided by that interpreter, Node 23.3.0/macOS. It processes one trial at a time and removes temporary plaintext afterwards. Allow 200 MB free space. The artifact itself occupies approximately 128 MB logical / somewhat more allocated filesystem space.

The command authenticates all encrypted blobs and manifest, compares original frozen-file hashes, checks reserved inputs and paired initial context equality after opaque-token normalization, imports the frozen checker, and compares every recalculated verdict with saved verdicts and summaries. It recomputes model cost from saved response token usage at pinned prices and verifies ledger deltas. Timing is recomputed descriptively from saved clocks; speed is **not remeasured live**. The exact reserved case membership is validated. These are author-generated records, not externally notarized provenance.

`python3 -E -s -B -m unittest discover -s study -p test_verifier.py -v` adds five controls: ciphertext alteration fails; traversal paths fail; an intermediate lost-label edit is detected despite unchanged final state; a wrongly accepted guard is detected; the known agent failure remains a failure.

## Inspect original code and traces locally

```sh
python3 -E -s -B study/evidence.py
python3 -E -s -B study/evidence.py experiments/live-v7/checker.py
python3 -E -s -B study/evidence.py experiments/live-v6/service.py
python3 -E -s -B study/evidence.py experiments/live-v7 --extract-to /tmp/recovery-v7-source
```

The listing includes all original logical lab paths. Inspect exact baseline, prompts, freeze/reservation records and raw requests locally. Never upload the decrypted content to public pages, issues, screenshots or source hosting. Temporary extraction persists only if you request `--extract-to`; delete that directory when finished. `verify.py` handles its own temporary cleanup.

## Environment pins retained for live reruns

Exact original package-lock, Python lockfiles, Dockerfiles, worker source, source freezes, prompts, generated/effective programs, provider requests/responses/usages, histories, evaluation scripts and budget ledger are encrypted and individually addressed by SHA-256. Headline pins include:

- `@cloudflare/codemode` 0.5.5; Miniflare 4.20260730.0; workerd as locked in package-lock.
- LangChain 1.4.7; LangGraph 1.2.16; langchain-anthropic 1.7.6; anthropic 1.17.0; Python 3.12.12; Node 23.3.0.
- AppWorld commit `42b5bcf3cd334fee33f0c37c02070a9f5807add5`.
- Shared simulator image ID `sha256:aa4f41c65cdd9fc6b7a1b4bd1cca7de16c3a06df1d5848f299366f96a369d37c`; base `sha256:56d0dbfe5b3904e3c1378afe2337e969b8f237697a923aa08ad6bc87e1a9b61c`.
- Provider model identifier `claude-sonnet-5`. Hosted model weights/backend behavior cannot be archived.
- Prices per million tokens: input $2; output $10; cache creation $2.50; cache read $0.20. These are historical pinned accounting values, not a current pricing recommendation.

Fresh live reexecution requires reacquiring protected AppWorld assets, rebuilding the simulator and local Cloudflare worker, installing pinned dependencies, fixing original machine-specific paths and environment chains, and an approved provider key/budget. No one-command from-scratch live reexecution has been validated. Docker image archives and installed dependencies are not distributed. Source definitions and image IDs are provenance, **not a guarantee of a byte-identical rebuild**. A future independently executed live rerun remains outstanding. Offline saved-state verification is the reproducible milestone delivered here.

Credentials, installed dependencies, caches, and build outputs are excluded. Earlier raw-evidence deletions are documented in the experiment history.
