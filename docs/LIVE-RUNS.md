# Run new trials from a clean checkout

This workflow rebuilds the simulator and reexecutes the published v7 cases with your own Anthropic API key. It uses the recorded agent, prompts, scenarios, shared safeguards, and checker. New outputs are kept separately from the frozen UAT and historical results.

These are already exposed cases. A rerun is a replication attempt, not a new held-out evaluation, and its outcomes can differ from the published results. The rebuilt Docker image is not claimed to be byte-identical to the original image.

## Requirements

- Linux or macOS with Python 3.12+, Node 22+, npm, and a running Docker engine. The original simulator uses Linux containers; Docker Desktop supplies these on macOS.
- Internet access during setup to obtain pinned dependencies, the base image, and the AppWorld data bundle. Allow several GB of disk space and several minutes for the initial build.
- An Anthropic API key with access to `claude-sonnet-5` for paid trials. Setup and preflight do not need a key.

From a clean clone:

```sh
git clone https://github.com/ahmedibrahimX/agent-recovery-study.git
cd agent-recovery-study
python3 tools/live.py doctor
python3 tools/live.py setup
python3 tools/live.py preflight
```

Setup authenticates the included evidence store, extracts the required source into the ignored `.live/runtime/` directory, installs the recorded Python dependencies and a minimal locked Node environment, and builds a new simulator image. It checks the downloaded AppWorld data bundle against the recorded SHA-256. No old checkout, Docker image, installed environment, or separate evidence download is needed.

The full unpaid preflight runs all 24 case/arm combinations through the native simulator and both interfaces using the original fixture driver. Four additional checks exercise the actual LangChain loop with explicitly scripted model responses, including notice delivery and terminal handling. Scripted responses test plumbing; they do not measure model capability. Spending-guard tests intercept the transport and verify that a small cap prevents dispatch and an unknown provider outcome prevents automatic retry.

For a shorter installation check, use `python3 tools/live.py preflight --quick`. It runs four fixture trials and four scripted-agent trials.

## Make paid model calls

Set the key in your shell environment, then choose an explicit local cost cap:

```sh
export ANTHROPIC_API_KEY='<your Anthropic API key>'
python3 tools/live.py run --budget-usd 5
```

The full command runs 24 new trials: the same 12 published cases and both arms in the recorded arm order. To try only the clean and inflight-withdrawal alarm pairs first, add `--quick` (four trials). Each invocation gets its own output directory and budget ledger; there is no automatic retry or pooling with earlier invocations.

The model identifier, prompts, call/output limits, and token prices remain those of the recorded comparison. Availability of that hosted model is a prerequisite; the runner does not silently substitute another model. A different model or recovery contract should be a separately versioned experiment.

The budget is a local guard calculated at the recorded prices: $2/M input, $10/M output, $2.50/M cache creation, and $0.20/M cache read. A conservative reservation is made before each provider request. Unknown outcomes retain their reservation and stop the run. This is not an invoice-verified spending guarantee; check your provider's current billing terms and account limits before paid execution. The historical matrix cost is descriptive, not a promise about a new run.

The real key stays in the parent process's environment; it is not written into run inputs or passed to the Python agent or generated code. The Python agent uses a local proxy credential. The simulator runs without network access, ports, or host mounts. Generated JavaScript runs through the existing isolated Code Mode worker.

## Inspect and verify the new results

The command prints a new directory under `reports/live/`. It contains:

- `run-config.json`, the exposed case set, rebuilt image identity, and source/adaptation hashes;
- per-trial requests/responses, histories, SQLite snapshots, submissions, and checker verdicts;
- `summary.json` and before/after ledgers, including partial results if a run stops.

Use the printed directory, for example:

```sh
python3 tools/live.py verify reports/live/run-<timestamp>-<suffix>
python3 tools/check_package.py
```

The first command recomputes the new local verdicts with the frozen checker; it does not require new model calls or the simulator image. Legitimate agent failures remain failures. A completed matrix can contain such failures; an infrastructure/provider/budget stop produces a nonzero exit and preserves the partial evidence. Inspect that evidence before deciding whether to start a separate new invocation.

The frozen checker retains its documented [question-type limitation](KNOWN-LIMITATIONS.md) and incomplete prose evaluation. New trials do not modify or replace the published 12/12 versus 11/12 outcomes.

## Local files and troubleshooting

`.live/` and `reports/` are ignored by Git. Extracted source and fresh traces can contain protected AppWorld-derived material; keep them local and do not publish plaintext logs, extractions, or run directories. Setup details are recorded locally in `.live/setup.log`; only bounded summaries are printed by the preflight.

If Docker is unavailable, start it and rerun `doctor`. If setup fails, inspect `.live/setup.log` locally and rerun `setup` after resolving the issue. An interrupted extraction or changed prepared source requires moving `.live/runtime/` aside before preparing a new workspace. Existing results under `reports/live/` are preserved.

The portability layer changes the local Python path, rebuilds the simulator, adds a data-download digest check, and replaces the original shared spending cap with a new per-run cap. It records original and prepared-source hashes. The experimental agent, prompts, shared service, case set, checker, and packaged UAT remain unchanged. No claim of new independent review or fresh held-out evidence follows from a successful setup or preflight.
