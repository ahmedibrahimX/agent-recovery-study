#!/usr/bin/env python3
"""Prepare and run new trials without changing the archived study."""

import argparse
import hashlib
import importlib.util
import json
import math
import os
import platform
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import uuid
from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
RUNTIME = ROOT / ".live" / "runtime"
PUBLIC = ROOT / "live"
BASE = "experiments/live-v7"
IMAGE = "agent-recovery-study-live:local"
DATA_SHA256 = "c9299e6cafe92bce4592a3c117c047c973d1554a667c21dd81537e78ab2f532e"


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


def command(args: list[str], *, cwd: Path = RUNTIME) -> str:
    """Keep raw setup/benchmark output local; it can contain protected material."""
    log = ROOT / ".live" / "setup.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a") as stream:
        result = subprocess.run(args, cwd=cwd, text=True, stdout=stream, stderr=stream)
    if result.returncode:
        raise RuntimeError(f"{Path(args[0]).name} failed; inspect {log} locally")
    return str(log)


def doctor() -> None:
    if sys.version_info < (3, 12):
        raise RuntimeError("Python 3.12+ is required")
    if not hasattr(sqlite3.Connection, "deserialize"):
        raise RuntimeError("Python must provide SQLite Connection.deserialize")
    for name in ("node", "npm", "docker"):
        if shutil.which(name) is None:
            raise RuntimeError(f"Install {name} before setup")
    node = subprocess.check_output(["node", "--version"], text=True).strip()
    if int(node.removeprefix("v").split(".")[0]) < 22:
        raise RuntimeError("Node 22+ is required")
    result = subprocess.run(
        ["docker", "info", "--format", "{{.ServerVersion}}"], capture_output=True
    )
    if result.returncode:
        raise RuntimeError("Docker must be running and accessible to this user")
    print(
        f"Python {sys.version.split()[0]}, Node {node}, and Docker are available.",
        flush=True,
    )


def replace_once(source: str, old: str, new: str) -> str:
    if source.count(old) != 1:
        raise RuntimeError("Archived source no longer matches the portability patch")
    return source.replace(old, new)


def prepare() -> None:
    """Extract authenticated source only into an ignored local working directory."""
    verifier = load_module(
        "live_saved_verifier", ROOT / "studies" / "recovery" / "verify.py"
    )
    package = load_module("live_package_check", ROOT / "tools" / "check_package.py")
    package.check()
    if (RUNTIME / "prepared.json").exists():
        check_prepared()
        return
    if RUNTIME.exists():
        raise RuntimeError(
            f"Incomplete preparation at {RUNTIME}; move that directory aside and retry"
        )
    RUNTIME.mkdir(parents=True, mode=0o700)
    records = []
    store = verifier.Store()
    try:
        store.call(op="verify")

        def materialize(logical: str, dest: str, transform=None) -> None:
            original = store.get(logical)
            path = RUNTIME / dest
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(
                original if transform is None else transform(original.decode()).encode()
            )
            records.append(
                {
                    "source": logical,
                    "path": dest,
                    "sourceSha256": hashlib.sha256(original).hexdigest(),
                    "runtimeSha256": digest(path),
                    "adapted": transform is not None,
                }
            )

        def portable_runner(src: str) -> str:
            src = replace_once(
                src,
                "const PY=resolve('experiments/live-v5/.venv/bin/python');",
                "const PY=resolve('.venv/bin/python');",
            )
            src = replace_once(src, "if(b.spentUsd>=30)", "if(b.spentUsd>=b.capUsd)")
            src = replace_once(
                src,
                "if(b.spentUsd+reservation>30)",
                "if(b.spentUsd+reservation>b.capUsd)",
            )
            return replace_once(
                src, "Total $30 budget exhausted", "Run budget exhausted"
            )

        for name in (
            "langchain_agent.py",
            "checker.py",
            "pack_sqlite.py",
            "prompts.mjs",
            "code-envelope.mjs",
            "report-parser.mjs",
            "heldout.json",
            "requirements.lock.txt",
        ):
            materialize(f"{BASE}/{name}", f"{BASE}/{name}")
        materialize(f"{BASE}/runner.mjs", f"{BASE}/runner.mjs", portable_runner)

        def fixture_module(src: str) -> str:
            start = src.index("async function fixtureDriver(")
            end = src.index("\nif(mode==='preflight')", start)
            return "export " + src[start:end] + "\n"

        materialize(f"{BASE}/cli.mjs", "fixture-driver.mjs", fixture_module)
        for name in ("catalog.ts", "cloudflare-worker.ts"):
            materialize(
                f"src/appworld-typed-v2/{name}", f"src/appworld-typed-v2/{name}"
            )
        materialize("src/appworld-v1/activities.ts", "src/appworld-v1/activities.ts")
        probe = "experiments/appworld-probe-v1"
        materialize("experiments/live-v6/service.py", "simulator/service.py")
        materialize(
            "experiments/appworld-recovery-v1/docker/client.py", "simulator/client.py"
        )
        materialize(f"{probe}/docker/state_checker.py", "simulator/state_checker.py")
        materialize(
            f"{probe}/resolved-environment.lock.txt", "simulator/requirements.txt"
        )

        def pin_data(src: str) -> str:
            return replace_once(
                src,
                "archive=decrypt_bytes(raw,PASSWORD,SALT)",
                "if hashlib.sha256(raw).hexdigest() != "
                + repr(DATA_SHA256)
                + ":\n raise RuntimeError('AppWorld data bundle digest changed')\n"
                + "archive=decrypt_bytes(raw,PASSWORD,SALT)",
            )

        materialize(
            f"{probe}/docker/prepare_data.py", "simulator/prepare_data.py", pin_data
        )
        vendor = f"{probe}/docker/vendor/appworld-src/"
        for path in store.call(op="manifest")["files"]:
            if path.startswith(vendor):
                materialize(
                    path, "simulator/vendor/appworld-src/" + path[len(vendor) :]
                )
    finally:
        store.close()
        if store.p.stdout is not None:
            store.p.stdout.close()
    for name in ("package.json", "package-lock.json", "cli.mjs", "budget.test.mjs"):
        shutil.copyfile(PUBLIC / name, RUNTIME / name)
    shutil.copyfile(PUBLIC / "Dockerfile", RUNTIME / "simulator" / "Dockerfile")
    save(
        RUNTIME / "prepared.json",
        {
            "format": 1,
            "archivedSources": records,
            "publicInputs": {
                p.name: digest(p) for p in PUBLIC.iterdir() if p.is_file()
            },
            "runtimeInputs": {
                name: digest(RUNTIME / name)
                for name in (
                    "package.json",
                    "package-lock.json",
                    "cli.mjs",
                    "budget.test.mjs",
                    "simulator/Dockerfile",
                )
            },
            "adaptations": [
                "Use the workspace Python environment instead of an original machine path",
                "Use a fresh per-run spending cap instead of the historical shared $30 ledger",
                "Reuse the original unpaid fixture driver without the historical CLI",
                "Require the recorded AppWorld data-bundle SHA-256 before unpacking",
                "Rebuild the simulator image from recorded source and dependency pins",
            ],
        },
    )


def check_prepared() -> dict:
    path = RUNTIME / "prepared.json"
    if not path.exists():
        raise RuntimeError("Run 'python3 tools/live.py setup' first")
    metadata = json.loads(path.read_text())
    for entry in metadata["archivedSources"]:
        if digest(RUNTIME / entry["path"]) != entry["runtimeSha256"]:
            raise RuntimeError(
                "Prepared source changed; use a separate experiment version"
            )
    for name, expected in metadata["publicInputs"].items():
        if digest(PUBLIC / name) != expected:
            raise RuntimeError(
                "Live tooling changed; move .live/runtime aside and rerun setup"
            )
    for name, expected in metadata["runtimeInputs"].items():
        if digest(RUNTIME / name) != expected:
            raise RuntimeError(
                "Prepared live tooling changed; rerun setup in a fresh workspace"
            )
    return metadata


def setup() -> None:
    doctor()
    prepare()
    print(
        "Installing the pinned live dependencies; detailed output stays in .live/setup.log.",
        flush=True,
    )
    command([sys.executable, "-m", "venv", str(RUNTIME / ".venv")])
    python = str(RUNTIME / ".venv" / "bin" / "python")
    command(
        [
            python,
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--no-cache-dir",
            "-r",
            str(RUNTIME / BASE / "requirements.lock.txt"),
        ]
    )
    command(
        [
            "npm",
            "ci",
            "--no-audit",
            "--no-fund",
            "--cache",
            str(ROOT / ".live/npm-cache"),
        ]
    )
    esbuild = str(RUNTIME / "node_modules" / ".bin" / "esbuild")
    for source in ("appworld-v1/activities", "appworld-typed-v2/catalog"):
        command(
            [
                esbuild,
                f"src/{source}.ts",
                "--format=esm",
                "--platform=node",
                f"--outfile=dist/{source}.js",
            ]
        )
    command(
        [
            esbuild,
            "src/appworld-typed-v2/cloudflare-worker.ts",
            "--bundle",
            "--format=esm",
            "--platform=browser",
            "--external:cloudflare:workers",
            "--outfile=dist/appworld-typed-v2/cloudflare-worker.js",
        ]
    )
    print(
        "Building the simulator from the included source; this downloads AppWorld data.",
        flush=True,
    )
    command(["docker", "build", "--tag", IMAGE, "simulator"])
    image_id = subprocess.check_output(
        ["docker", "image", "inspect", IMAGE, "--format", "{{.Id}}"], text=True
    ).strip()
    save(
        RUNTIME / BASE / "environment.json",
        {
            "imageId": image_id,
            "rebuilt": True,
            "hostPython": sys.version,
            "hostPlatform": platform.platform(),
            "node": subprocess.check_output(["node", "--version"], text=True).strip(),
        },
    )
    check_prepared()
    print("Live setup completed. Next: python3 tools/live.py preflight")


def run(mode: str, budget: float | None, quick: bool) -> None:
    doctor()
    metadata = check_prepared()
    if not (RUNTIME / BASE / "environment.json").exists():
        raise RuntimeError("Setup has not completed")
    if mode == "run":
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise RuntimeError("Export your ANTHROPIC_API_KEY before a paid run")
        if budget is None or not math.isfinite(budget) or budget <= 0:
            raise RuntimeError("A positive, finite --budget-usd value is required")
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    output = ROOT / "reports" / "live" / f"{mode}-{stamp}-{uuid.uuid4().hex[:8]}"
    output.mkdir(parents=True, mode=0o700)
    save(output / "source-manifest.json", metadata)
    args = ["node", "cli.mjs", mode, str(output), str(budget or 0)]
    if quick:
        args.append("--quick")
    env = dict(os.environ)
    if mode != "run":
        env.pop("ANTHROPIC_API_KEY", None)
    package = load_module("live_run_package_check", ROOT / "tools" / "check_package.py")
    package.check()
    try:
        result = subprocess.run(args, cwd=RUNTIME, env=env)
    finally:
        package.check()
    print(f"New local output: {output}")
    if result.returncode:
        raise RuntimeError("Run stopped; inspect its local summary and error files")


def recheck(folder: Path) -> None:
    folder = folder.resolve()
    summary = json.loads((folder / "summary.json").read_text())
    verifier = load_module(
        "fresh_saved_verifier", ROOT / "studies" / "recovery" / "verify.py"
    )
    store = verifier.Store()
    try:
        published = {case["id"]: case for case in store.json(f"{BASE}/heldout.json")}
        with tempfile.TemporaryDirectory(prefix="fresh-recheck-") as td:
            path = Path(td) / "checker.py"
            path.write_bytes(store.get(f"{BASE}/checker.py"))
            checker = load_module("fresh_frozen_checker", path)
            seen = set()
            for row in summary["results"]:
                case = folder / row["relativeDirectory"]
                if not case.resolve().is_relative_to(folder):
                    raise RuntimeError("Unsafe case directory")
                definition = json.loads((case / "case.json").read_text())
                if definition != published.get(row["case"]):
                    raise RuntimeError("Fresh case differs from the published case set")
                if row["arm"] not in definition["armOrder"]:
                    raise RuntimeError("Unexpected fresh experiment arm")
                key = (row["case"], row["arm"], row["runKind"])
                if key in seen:
                    raise RuntimeError("Duplicate case/arm in the fresh run")
                seen.add(key)
                fresh = checker.check(case)
                if fresh != json.loads((case / "verdict.json").read_text()):
                    raise RuntimeError("Fresh verdict differs from saved local verdict")
                if any(row[k] != v for k, v in fresh.items()):
                    raise RuntimeError("Fresh summary differs from the checked verdict")
            if not seen:
                raise RuntimeError("No trials to recheck")
    finally:
        store.close()
        if store.p.stdout is not None:
            store.p.stdout.close()
    print(f"Rechecked {len(seen)} fresh verdicts, including any agent failures.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="mode", required=True)
    commands.add_parser("doctor", help="Check Python, Node, npm, and Docker")
    commands.add_parser(
        "setup", help="Build the portable live environment (no model calls)"
    )
    preflight = commands.add_parser(
        "preflight", help="Test native scenarios and agent plumbing without API calls"
    )
    preflight.add_argument(
        "--quick",
        action="store_true",
        help="Use two histories instead of the full fixture matrix",
    )
    paid = commands.add_parser(
        "run", help="Run the published v7 case matrix with your API key"
    )
    paid.add_argument(
        "--budget-usd",
        required=True,
        type=float,
        help="Local token-cost cap for this new run",
    )
    paid.add_argument(
        "--quick",
        action="store_true",
        help="Run only clean and inflight-withdrawal phone pairs",
    )
    verify = commands.add_parser(
        "verify", help="Recheck new local outcomes with the frozen checker"
    )
    verify.add_argument("folder", type=Path)
    args = parser.parse_args()
    if args.mode == "doctor":
        doctor()
    elif args.mode == "setup":
        setup()
    elif args.mode == "verify":
        recheck(args.folder)
    else:
        run(args.mode, getattr(args, "budget_usd", None), args.quick)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, ValueError) as error:
        sys.exit(str(error))
