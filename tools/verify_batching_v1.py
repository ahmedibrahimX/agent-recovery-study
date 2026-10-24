#!/usr/bin/env python3
"""Verify preserved batching-v1 runs offline without executing saved programs."""

import argparse
import hashlib
import importlib.util
import json
import statistics
import tarfile
import tempfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent
SAVED = ROOT / "results" / "batching-v1"


def extract_run(name: str, destination: Path, record: dict) -> None:
    archive = SAVED / record["archive"]
    if hashlib.sha256(archive.read_bytes()).hexdigest() != record["sha256"]:
        raise RuntimeError(f"Archive checksum differs: {name}")
    seen = set()
    with tarfile.open(archive, "r:gz") as stream:
        members = stream.getmembers()
        if sum(member.size for member in members) > 100_000_000:
            raise RuntimeError("Saved run exceeds extraction size limit")
        for member in members:
            path = PurePosixPath(member.name)
            if (
                not member.isfile()
                or path.is_absolute()
                or ".." in path.parts
                or member.name in seen
                or member.name not in record["files"]
            ):
                raise RuntimeError(
                    f"Unexpected or unsafe archive member: {member.name}"
                )
            seen.add(member.name)
            content = stream.extractfile(member)
            if content is None:
                raise RuntimeError("Missing archived content")
            data = content.read()
            if hashlib.sha256(data).hexdigest() != record["files"][member.name]:
                raise RuntimeError(f"Saved file checksum differs: {member.name}")
            target = destination / member.name
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as output:
                output.write(data)
    if seen != set(record["files"]):
        raise RuntimeError("Missing archived files")


def summarize(folder: Path) -> dict:
    plan = json.loads((folder / "plan.json").read_text())
    rows = json.loads((folder / "summary.json").read_text())["results"]
    cases = {case["id"]: case for case in plan["cases"]}

    def arm_summary(selected: list[dict]) -> dict:
        successful = [row for row in selected if row["passed"]]
        return {
            "attempted": len(selected),
            "passed": len(successful),
            "stateIntegrityPasses": sum(row["stateIntegrity"] for row in selected),
            **{
                key: sum(row[key] for row in selected)
                for key in (
                    "modelCallsCompleted",
                    "publicCalls",
                    "executionBlocks",
                    "blockedMutationAttempts",
                    "mutationRequestsAfterModelExposure",
                    "toolResultBytesPresentedToModel",
                )
            },
            "calculatedCostUsd": round(sum(row["costUsd"] for row in selected), 6),
            "medianSuccessfulAgentSeconds": round(
                statistics.median(row["agentMs"] for row in successful) / 1000, 6
            )
            if successful
            else None,
            "maximumSuccessfulAgentSeconds": round(
                max(row["agentMs"] for row in successful) / 1000, 6
            )
            if successful
            else None,
        }

    def group(selected: list[dict]) -> dict:
        arms = {
            arm: arm_summary([row for row in selected if row["arm"] == arm])
            for arm in ("ordinary", "code")
        }
        pairs = []
        for case in sorted({row["case"] for row in selected}):
            pair = {row["arm"]: row for row in selected if row["case"] == case}
            if len(pair) == 2 and all(row["passed"] for row in pair.values()):
                pairs.append(pair)
        deltas = [
            (pair["code"]["agentMs"] - pair["ordinary"]["agentMs"]) / 1000
            for pair in pairs
        ]
        return {
            "arms": arms,
            "jointlySuccessfulPairs": len(pairs),
            "codeFasterPairs": sum(delta < 0 for delta in deltas),
            "medianPairedCodeMinusOrdinarySeconds": round(statistics.median(deltas), 6)
            if deltas
            else None,
        }

    return {
        "planSha256": plan["planSha256"],
        "kind": plan["kind"],
        "seeds": plan["seeds"],
        "repetitions": plan["repetitions"],
        "overall": group(rows),
        "bySize": {
            str(size): group(
                [row for row in rows if cases[row["case"]]["size"] == size]
            )
            for size in sorted(plan["sizes"])
        },
        "bySizeAndHistory": {
            f"{size}/{history}": group(
                [
                    row
                    for row in rows
                    if cases[row["case"]]["size"] == size
                    and cases[row["case"]]["history"] == history
                ]
            )
            for size in sorted(plan["sizes"])
            for history in ("clean", "edit", "withdraw")
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-metrics", action="store_true")
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location(
        "frozen_batching_v1", ROOT / "tools" / "batching.py"
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load frozen v1 verifier")
    frozen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(frozen)
    manifest = json.loads((SAVED / "manifest.json").read_text())
    metrics = {}
    with tempfile.TemporaryDirectory(prefix="batching-v1-verify-") as temporary:
        for name, record in manifest["runs"].items():
            destination = Path(temporary) / name
            extract_run(name, destination, record)
            plan = json.loads((destination / "plan.json").read_text())
            if plan["planSha256"] != record["planSha256"]:
                raise RuntimeError("Archived plan identity differs")
            print(f"Verifying preserved {name}", flush=True)
            frozen.verify(destination)
            metrics[name] = summarize(destination)
    encoded = json.dumps(metrics, indent=2, sort_keys=True) + "\n"
    target = SAVED / "metrics.json"
    if args.write_metrics:
        target.write_text(encoded)
    elif target.read_text() != encoded:
        raise RuntimeError("Published metrics differ from preserved trial evidence")
    print("All preserved file hashes, v1 verdicts and published metrics reproduce.")


if __name__ == "__main__":
    main()
