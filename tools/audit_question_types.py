#!/usr/bin/env python3
"""Audit saved question types and characterize the frozen oracle's type gap.

This supplemental diagnostic does not change the UAT, checker, or saved scores.
Exit zero means the audit completed and reproduced the documented limitation.
"""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "study"))
from verify import Store, STUDIES  # noqa: E402


def audit():
    store = Store()
    try:
        paths = store.call(op="manifest")["files"]
        counts = {}
        invalid = 0
        for version, prefix in STUDIES.items():
            claims = [store.json(path) for path in paths
                      if path.startswith(prefix + "/") and path.endswith("/submission.json")]
            asks = [claim for claim in claims if claim.get("status") == "ask"]
            invalid += sum(not isinstance(c.get("question"), str) or not c["question"].strip()
                           for c in asks)
            counts[version] = len(asks)
        if invalid:
            raise RuntimeError("saved approval questions include invalid text values")
        candidate = next(path.removesuffix("/submission.json") for path in paths
                         if path.startswith(STUDIES["v7"] + "/")
                         and "withdraw_after_read" in path
                         and path.endswith("/langchain_native/submission.json"))
        with tempfile.TemporaryDirectory(prefix="recovery-question-audit-") as directory:
            temporary = Path(directory)
            case = temporary / "case"
            store.extract(candidate, case)
            source = temporary / "checker.py"
            source.write_bytes(store.get("experiments/live-v7/checker.py"))
            spec = importlib.util.spec_from_file_location("frozen_question_audit", source)
            checker = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(checker)
            original = json.loads((case / "submission.json").read_text())
            if not checker.check(case)["passed"]:
                raise RuntimeError("unmodified saved case unexpectedly fails")
            accepted = []
            for label, question in [("null", None), ("number", 42), ("array", []), ("object", {})]:
                (case / "submission.json").write_text(json.dumps({**original, "question": question}))
                if not checker.check(case)["passed"]:
                    raise RuntimeError(f"documented frozen behavior changed for {label}")
                accepted.append(label)
        return {"audit": "frozen oracle question-type limitation",
                "savedAskQuestionsChecked": counts,
                "savedInvalidQuestionTypes": invalid,
                "malformedTypesAcceptedByFrozenOracle": accepted,
                "savedScoresChanged": False}
    finally:
        store.close()


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
