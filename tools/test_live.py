"""Controls for the portable runner; the archived UAT stays unchanged."""

import contextlib
import importlib.util
import io
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

_spec = importlib.util.spec_from_file_location(
    "portable_live", Path(__file__).with_name("live.py")
)
if _spec is None or _spec.loader is None:
    raise RuntimeError("Cannot load live runner")
live = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(live)


class LiveControls(unittest.TestCase):
    def test_extraction_preserves_baselines_and_detects_local_edits(self):
        with (
            tempfile.TemporaryDirectory() as td,
            patch.object(live, "RUNTIME", Path(td) / "runtime"),
        ):
            live.prepare()
            metadata = live.check_prepared()
            by_name = {entry["path"]: entry for entry in metadata["archivedSources"]}
            for name in (
                "checker.py",
                "langchain_agent.py",
                "prompts.mjs",
                "heldout.json",
            ):
                entry = by_name[f"{live.BASE}/{name}"]
                self.assertEqual(entry["sourceSha256"], entry["runtimeSha256"])
                self.assertFalse(entry["adapted"])
            service = by_name["simulator/service.py"]
            self.assertEqual(service["sourceSha256"], service["runtimeSha256"])
            self.assertTrue(by_name[f"{live.BASE}/runner.mjs"]["adapted"])
            subprocess.run(
                ["node", "--check", str(live.RUNTIME / live.BASE / "runner.mjs")],
                check=True,
                capture_output=True,
            )
            (live.RUNTIME / live.BASE / "checker.py").write_text("changed")
            with self.assertRaisesRegex(RuntimeError, "Prepared source changed"):
                live.check_prepared()

    def test_portability_patch_rejects_an_unexpected_source(self):
        with self.assertRaises(RuntimeError):
            live.replace_once("not the expected source", "old", "new")
        with self.assertRaises(RuntimeError):
            live.replace_once("old old", "old", "new")

    def test_paid_run_requires_a_key_and_finite_positive_budget(self):
        with (
            tempfile.TemporaryDirectory() as td,
            patch.object(live, "RUNTIME", Path(td)),
            patch.object(live, "doctor"),
            patch.object(live, "check_prepared", return_value={}),
        ):
            live.save(live.RUNTIME / live.BASE / "environment.json", {})
            with patch.dict(os.environ, {}, clear=True):
                with self.assertRaisesRegex(RuntimeError, "ANTHROPIC_API_KEY"):
                    live.run("run", 5, False)
            with patch.dict(
                os.environ, {"ANTHROPIC_API_KEY": "unpaid-test-placeholder"}
            ):
                for budget in (None, 0, -1, float("nan"), float("inf")):
                    with self.assertRaisesRegex(RuntimeError, "positive, finite"):
                        live.run("run", budget, False)

    def test_fresh_recheck_detects_an_altered_verdict(self):
        verifier = live.load_module(
            "live_test_saved_verifier", live.ROOT / "study/verify.py"
        )
        store = verifier.Store()
        try:
            with tempfile.TemporaryDirectory() as td:
                output = Path(td)
                prefix = (
                    verifier.STUDIES["v7"]
                    + "/live-v7-heldout-phone-clean-0/langchain_native"
                )
                store.extract(prefix, output / "trial")
                verdict = store.json(prefix + "/verdict.json")
                live.save(
                    output / "summary.json",
                    {
                        "results": [
                            {
                                **verdict,
                                "runKind": "fresh-model-trial",
                                "relativeDirectory": "trial",
                            }
                        ]
                    },
                )
                with contextlib.redirect_stdout(io.StringIO()):
                    live.recheck(output)
                live.save(output / "trial/verdict.json", {**verdict, "passed": False})
                with self.assertRaisesRegex(RuntimeError, "differs"):
                    live.recheck(output)
        finally:
            store.close()
            if store.p.stdout is not None:
                store.p.stdout.close()

    def test_fresh_recheck_rejects_path_traversal(self):
        with tempfile.TemporaryDirectory() as td:
            output = Path(td)
            live.save(
                output / "summary.json",
                {"results": [{"relativeDirectory": "../outside"}]},
            )
            with self.assertRaisesRegex(RuntimeError, "Unsafe case directory"):
                live.recheck(output)


if __name__ == "__main__":
    unittest.main()
