#!/usr/bin/env python3
"""Audit saved question types and characterize the frozen oracle's type gap.

This supplemental diagnostic does not change the UAT, checker, or saved scores.
Exit zero means the audit completed and reproduced the documented limitation.
"""

import importlib.util
import json
import tempfile
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parent.parent


def load_module(name: str, source: Path) -> ModuleType:
    """Load a frozen source by path without changing import search paths."""
    spec = importlib.util.spec_from_file_location(name, source)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module from {source}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def audit():
    verifier = load_module("frozen_verifier", ROOT / "studies/recovery/verify.py")
    store = verifier.Store()
    studies = verifier.STUDIES
    try:
        paths = store.call(op="manifest")["files"]
        counts = {}
        invalid = 0
        for version, prefix in studies.items():
            claims = [
                store.json(path)
                for path in paths
                if path.startswith(prefix + "/") and path.endswith("/submission.json")
            ]
            asks = [claim for claim in claims if claim.get("status") == "ask"]
            invalid += sum(
                not isinstance(c.get("question"), str) or not c["question"].strip()
                for c in asks
            )
            counts[version] = len(asks)
        if invalid:
            raise RuntimeError("saved approval questions include invalid text values")
        candidate = next(
            path.removesuffix("/submission.json")
            for path in paths
            if path.startswith(studies["v7"] + "/")
            and "withdraw_after_read" in path
            and path.endswith("/langchain_native/submission.json")
        )
        with tempfile.TemporaryDirectory(
            prefix="recovery-question-audit-"
        ) as directory:
            temporary = Path(directory)
            case = temporary / "case"
            store.extract(candidate, case)
            source = temporary / "checker.py"
            source.write_bytes(store.get("experiments/live-v7/checker.py"))
            checker = load_module("frozen_question_audit", source)
            original = json.loads((case / "submission.json").read_text())
            if not checker.check(case)["passed"]:
                raise RuntimeError("unmodified saved case unexpectedly fails")
            accepted = []
            samples: tuple[tuple[str, object], ...] = (
                ("null", None),
                ("number", 42),
                ("array", []),
                ("object", {}),
            )
            for label, question in samples:
                (case / "submission.json").write_text(
                    json.dumps({**original, "question": question})
                )
                if not checker.check(case)["passed"]:
                    raise RuntimeError(
                        f"documented frozen behavior changed for {label}"
                    )
                accepted.append(label)
        return {
            "audit": "frozen oracle question-type limitation",
            "savedAskQuestionsChecked": counts,
            "savedInvalidQuestionTypes": invalid,
            "malformedTypesAcceptedByFrozenOracle": accepted,
            "savedScoresChanged": False,
        }
    finally:
        store.close()


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
