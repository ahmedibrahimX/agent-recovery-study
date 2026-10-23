# Changelog

## Unreleased

- Clean-checkout live setup using included experimental source, pinned dependencies, and a rebuilt simulator image.
- Unpaid native-scenario and scripted-agent preflight checks; new paid trials with an explicit per-run budget and the user's API key.
- Separate local evidence and fresh-verdict checks, preserving the frozen UAT and saved outcomes.

## 0.1.0 — 2026-10-23

- Offline verification of saved v6 and v7 outcomes against native state and action histories.
- Five negative controls covering evidence tampering, path traversal, transient lost edits, guard decisions, and a known agent failure.
- Local inspection of frozen sources, model requests, histories, and database snapshots through the encrypted evidence store.
- Scenario contracts, comparison results, limitations, and reproduction instructions.

- Mypy, Ruff linting/formatting, and Linux/macOS saved-evidence CI checks.
