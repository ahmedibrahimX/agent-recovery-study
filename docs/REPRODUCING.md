# Reproduction levels

## Packaged-file consistency

`python3 tools/check_package.py` checks the included study files against `provenance/study-files.json` and the evidence manifest against its recorded digest. This detects unexpected changes relative to this package's own records. It is not an independently signed or externally timestamped provenance claim.

## Saved-result verification

From the repository root:

```sh
python3 -E -s -B study/verify.py
python3 -E -s -B -m unittest discover -s study -p test_verifier.py -v
```

Python 3.12+ must support SQLite `Connection.deserialize`; Node must be 22+. `-E` prevents Python environment variables such as `PYTHONOPTIMIZE` from disabling assertions, `-s` disables user site packages, and `-B` avoids bytecode writes into the preserved artifact. These flags do not sandbox Python.

The unchanged verifier authenticates evidence, loads the exact frozen checker, compares intermediate and final database/history verdicts, and checks source freezes, reserved inputs, paired contexts, usage costs, and budget deltas. It reports v6 and v7 separately.

To save a new local JSON result, choose a new filename under the ignored `reports/` directory:

```sh
mkdir -p reports
python3 -E -s -B study/verify.py --output reports/verification.json
```

The original verifier's `--output` can overwrite an existing file. Avoid paths inside `study/`; the package consistency check detects changed study bytes.

For a limited study, use `--study v6` or `--study v7`. The separate negative-control command always runs the original full control suite, including its v7 fixtures.

## Fresh live execution

The [live-run guide](LIVE-RUNS.md) provides a clean-checkout setup, an unpaid native/agent preflight, paid execution with your own key and explicit budget, and fresh-result checks. The portable layer rebuilds the simulator from included source, uses recorded dependency pins, and records its adaptations separately from the frozen source.

Fresh runs use new local output directories and per-run ledgers. They do not use the historical shared budget or replace the saved outcomes. Rerunning the published cases is a replication on exposed cases, not new held-out evidence. No model/API calls are needed for saved verification or unpaid preflight.

## Independent review

Passing local checks or hosted CI does not establish independent human review, author-independent checkers, production safety, or generalization. The next credibility milestone remains an outside engineer challenging the contract and baseline and reproducing a meaningful saved result.

