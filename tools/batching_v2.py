#!/usr/bin/env python3
"""Run the separate batching-v2 interface study; never changes historical evidence."""

import argparse
import hashlib
import json
import math
import os
import platform
import random
import shutil
import subprocess
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STUDY = ROOT / "studies" / "batching-v2"
ENV = ROOT / ".batching-v2" / "venv"


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def sources() -> dict[str, str]:
    files = [ROOT / "tools" / "batching_v2.py"]
    files.extend(
        p
        for p in STUDY.rglob("*")
        if p.is_file()
        and not any(x in p.parts for x in ("node_modules", ".runtime", "__pycache__"))
    )
    return {
        p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(files)
    }


def write_new(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def doctor() -> None:
    if sys.version_info < (3, 12):
        raise RuntimeError("Python 3.12+ is required")
    if platform.system() not in ("Linux", "Darwin"):
        raise RuntimeError("Use Linux, macOS or a Linux environment such as WSL")
    for name in ("node", "npm"):
        if not shutil.which(name):
            raise RuntimeError(f"Install {name}")
    version = subprocess.check_output(["node", "--version"], text=True).strip()
    if int(version.removeprefix("v").split(".")[0]) < 22:
        raise RuntimeError("Node 22+ is required")
    print(f"Python {sys.version.split()[0]}, Node {version}. No Docker needed.")


def setup() -> None:
    doctor()
    subprocess.run([sys.executable, "-m", "venv", str(ENV)], check=True)
    subprocess.run(
        [
            str(ENV / "bin" / "python"),
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "-r",
            str(STUDY / "requirements.lock.txt"),
        ],
        check=True,
    )
    subprocess.run(["npm", "ci", "--no-audit", "--no-fund"], cwd=STUDY, check=True)
    subprocess.run(["npm", "run", "build"], cwd=STUDY, check=True)
    (ROOT / ".batching-v2" / "setup.json").write_text(
        json.dumps(build_identity(), indent=2) + "\n"
    )
    print("Setup complete. Run: python3 tools/batching_v2.py preflight")


def build_identity() -> dict[str, str]:
    return {
        name: hashlib.sha256((STUDY / name).read_bytes()).hexdigest()
        for name in (
            "package.json",
            "package-lock.json",
            "requirements.lock.txt",
            "worker.ts",
            ".runtime/worker.mjs",
        )
    }


def case_definition(size: int, history: str, seed: int, repetition: int) -> dict:
    core = {"size": size, "history": history, "seed": seed, "repetition": repetition}
    order = (
        size + seed + repetition + ("clean", "edit", "withdraw").index(history)
    ) % 2
    return {
        **core,
        "id": "batching-v2-" + digest(core)[:12],
        "withdrawAfter": max(1, size // 2),
        "armOrder": ["ordinary", "code"] if order else ["code", "ordinary"],
    }


def make_plan(
    *,
    quick: bool = False,
    preflight: bool = False,
    sizes: list[int] | None = None,
    seeds: list[int] | None = None,
    repetitions: int | None = None,
) -> dict:
    protocol = json.loads((STUDY / "protocol.json").read_text())
    selected_sizes = (
        sizes if sizes is not None else ([1, 5] if quick else protocol["sizes"])
    )
    selected_seeds = (
        seeds
        if seeds is not None
        else (
            [17] if preflight else protocol["seeds"][:1] if quick else protocol["seeds"]
        )
    )
    repeats = (
        repetitions
        if repetitions is not None
        else (1 if quick or preflight else protocol["repetitions"])
    )
    if (
        not selected_sizes
        or len(set(selected_sizes)) != len(selected_sizes)
        or any(type(n) is not int or n < 1 or n > 100 for n in selected_sizes)
        or not selected_seeds
        or len(set(selected_seeds)) != len(selected_seeds)
        or any(type(n) is not int or n < 0 or n >= 2**32 for n in selected_seeds)
        or type(repeats) is not int
        or repeats < 1
        or repeats > 100
    ):
        raise ValueError(
            "Use unique sizes 1..100, uint32 seeds, and 1..100 repetitions"
        )
    cases = [
        case_definition(size, history, seed, repetition)
        for repetition in range(repeats)
        for seed in selected_seeds
        for size in selected_sizes
        for history in protocol["histories"]
    ]
    random.Random(protocol["orderSeed"]).shuffle(cases)
    for index, definition in enumerate(cases):
        definition["armOrder"] = (
            ["ordinary", "code"] if index % 2 == 0 else ["code", "ordinary"]
        )
    plan = {
        "format": 1,
        "study": "batching-v2",
        "kind": "unpaid-preflight" if preflight else "paid-model-comparison",
        "createdAt": datetime.now(UTC).isoformat(),
        "model": protocol["model"],
        "prices": protocol["accountingUsdPerMillionTokens"],
        "service": protocol["service"],
        "limits": protocol["limits"],
        "repetitions": repeats,
        "sizes": selected_sizes,
        "seeds": selected_seeds,
        "orderSeed": protocol["orderSeed"],
        "samplingNote": protocol["samplingNote"],
        "sourceSha256": sources(),
        "cases": cases,
    }
    return {**plan, "planSha256": digest(plan)}


def validate_plan(plan: dict) -> None:
    body = {k: v for k, v in plan.items() if k != "planSha256"}
    if plan.get("planSha256") != digest(body):
        raise RuntimeError("Plan digest differs")
    if plan.get("format") != 1 or plan.get("study") != "batching-v2":
        raise RuntimeError("Unsupported plan")
    if plan.get("sourceSha256") != sources():
        raise RuntimeError("Study source changed since planning; reserve a new plan")
    if plan.get("kind") not in ("paid-model-comparison", "unpaid-preflight"):
        raise RuntimeError("Unknown plan kind")
    expected = make_plan(
        preflight=plan["kind"] == "unpaid-preflight",
        sizes=plan["sizes"],
        seeds=plan["seeds"],
        repetitions=plan["repetitions"],
    )
    for name in ("model", "prices", "service", "limits", "orderSeed"):
        if plan.get(name) != expected[name]:
            raise RuntimeError(f"Planned {name} differs from the versioned protocol")
    if plan["cases"] != expected["cases"]:
        raise RuntimeError("Case matrix or arm order differs from its declared factors")
    seen = set()
    for c in plan["cases"]:
        if c["id"] in seen:
            raise RuntimeError("Duplicate planned case")
        seen.add(c["id"])
    if not seen:
        raise RuntimeError("Empty plan")


def output_path(kind: str) -> Path:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return ROOT / "reports" / "batching-v2" / f"{kind}-{stamp}-{uuid.uuid4().hex[:8]}"


def run(plan_path: Path, budget: float | None, preflight: bool) -> None:
    doctor()
    plan_path = plan_path.resolve()
    plan = json.loads(plan_path.read_text())
    validate_plan(plan)
    if preflight != (plan["kind"] == "unpaid-preflight"):
        raise RuntimeError("Execution mode differs from the plan kind")
    if (
        not (ENV / "bin" / "python").exists()
        or not (STUDY / ".runtime" / "worker.mjs").exists()
    ):
        raise RuntimeError("Run python3 tools/batching_v2.py setup first")
    marker = ROOT / ".batching-v2" / "setup.json"
    if not marker.exists() or json.loads(marker.read_text()) != build_identity():
        raise RuntimeError("Prepared build differs from current inputs; rerun setup")
    if not preflight:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise RuntimeError("Export your ANTHROPIC_API_KEY before paid execution")
        if budget is None or not math.isfinite(budget) or budget <= 0:
            raise RuntimeError("Use a positive, finite --budget-usd")
    output = output_path("preflight" if preflight else "run")
    output.mkdir(parents=True, mode=0o700)
    write_new(
        output / "environment.json",
        {
            "hostPython": sys.version,
            "platform": platform.platform(),
            "node": subprocess.check_output(["node", "--version"], text=True).strip(),
            "agentPython": subprocess.check_output(
                [str(ENV / "bin" / "python"), "--version"], text=True
            ).strip(),
            "installedPythonPackages": subprocess.check_output(
                [str(ENV / "bin" / "python"), "-m", "pip", "freeze"], text=True
            ).splitlines(),
            "buildSha256": build_identity(),
        },
    )
    env = dict(os.environ)
    if preflight:
        env.pop("ANTHROPIC_API_KEY", None)
        subprocess.run(
            ["node", "--test", "test/worker.integration.mjs"],
            cwd=STUDY,
            env=env,
            check=True,
        )
    print(f"Planned trials: {len(plan['cases']) * 2}. New output: {output}", flush=True)
    result = subprocess.run(
        [
            "node",
            "cli.mjs",
            "preflight" if preflight else "run",
            str(plan_path),
            str(output),
            str(ENV / "bin" / "python"),
            str(budget or 0),
        ],
        cwd=STUDY,
        env=env,
    )
    print(f"New output: {output}")
    if result.returncode:
        raise RuntimeError(
            "Run stopped. Inspect partial evidence and budget reservations; no automatic retry was made."
        )


def verify(folder: Path) -> None:
    plan = json.loads((folder / "plan.json").read_text())
    validate_plan(plan)
    subprocess.run(["node", "verify.mjs", str(folder.resolve())], cwd=STUDY, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="mode", required=True)
    commands.add_parser("doctor")
    commands.add_parser("setup")
    plan = commands.add_parser(
        "plan",
        help="Freeze case definitions, arm order and source hashes before paid execution",
    )
    plan.add_argument("--quick", action="store_true")
    plan.add_argument("--sizes", type=int, nargs="+")
    plan.add_argument("--seeds", type=int, nargs="+")
    plan.add_argument("--repetitions", type=int)
    plan.add_argument("--output", type=Path, required=True)
    preflight = commands.add_parser(
        "preflight",
        help="Exercise both actual interfaces with scripted model responses; no key",
    )
    preflight.add_argument("--quick", action="store_true")
    paid = commands.add_parser("run")
    paid.add_argument("--plan", type=Path, required=True)
    paid.add_argument("--budget-usd", type=float, required=True)
    check = commands.add_parser("verify")
    check.add_argument("folder", type=Path)
    args = parser.parse_args()
    if args.mode == "doctor":
        doctor()
    elif args.mode == "setup":
        setup()
    elif args.mode == "plan":
        value = make_plan(
            quick=args.quick,
            sizes=args.sizes,
            seeds=args.seeds,
            repetitions=args.repetitions,
        )
        write_new(args.output, value)
        print(
            f"Frozen {len(value['cases']) * 2} trials: {args.output}\nPlan SHA-256: {value['planSha256']}"
        )
    elif args.mode == "preflight":
        path = output_path("preflight-plan").with_suffix(".json")
        write_new(path, make_plan(quick=args.quick, preflight=True))
        run(path, 0, True)
    elif args.mode == "run":
        run(args.plan, args.budget_usd, False)
    elif args.mode == "verify":
        verify(args.folder)


if __name__ == "__main__":
    try:
        main()
    except (
        RuntimeError,
        OSError,
        ValueError,
        KeyError,
        subprocess.CalledProcessError,
    ) as error:
        sys.exit(str(error))
