"""Controls for the new study; no changes to the historical UAT."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "batching_controls", Path(__file__).with_name("batching_v2.py")
)
if spec is None or spec.loader is None:
    raise RuntimeError("Cannot load batching CLI")
batching = importlib.util.module_from_spec(spec)
spec.loader.exec_module(batching)


class PlanningControls(unittest.TestCase):
    def test_full_plan_has_expected_factors_and_unique_pairs(self):
        plan = batching.make_plan()
        batching.validate_plan(plan)
        self.assertEqual(len(plan["cases"]) * 2, 162)
        self.assertEqual(len({c["id"] for c in plan["cases"]}), 81)
        ordinary_first = sum(c["armOrder"][0] == "ordinary" for c in plan["cases"])
        self.assertLessEqual(abs(2 * ordinary_first - len(plan["cases"])), 1)
        for c in plan["cases"]:
            self.assertEqual(set(c["armOrder"]), {"ordinary", "code"})
            self.assertEqual(c["withdrawAfter"], max(1, c["size"] // 2))

    def test_quick_plan_contains_both_interfaces_and_all_histories(self):
        plan = batching.make_plan(quick=True)
        self.assertEqual(len(plan["cases"]) * 2, 12)
        self.assertEqual(
            {c["history"] for c in plan["cases"]}, {"clean", "edit", "withdraw"}
        )

    def test_changed_plan_or_source_is_rejected(self):
        plan = batching.make_plan(quick=True)
        plan["cases"][0]["size"] = 99
        with self.assertRaisesRegex(RuntimeError, "digest"):
            batching.validate_plan(plan)
        plan["planSha256"] = batching.digest(
            {k: v for k, v in plan.items() if k != "planSha256"}
        )
        with self.assertRaisesRegex(RuntimeError, "Case matrix"):
            batching.validate_plan(plan)

    def test_plan_output_never_overwrites_an_existing_file(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "plan.json"
            batching.write_new(path, {"first": True})
            with self.assertRaises(FileExistsError):
                batching.write_new(path, {"first": False})
            self.assertEqual(json.loads(path.read_text()), {"first": True})

    def test_followup_uses_separate_sources_paths_and_fresh_paid_seeds(self):
        paid = batching.make_plan()
        qualification = batching.make_plan(preflight=True)
        previously_used = {17, 41, 73, 20261023, 93473, 54781, 71839}
        self.assertTrue(set(paid["seeds"]).isdisjoint(previously_used))
        self.assertTrue(set(paid["seeds"]).isdisjoint(qualification["seeds"]))
        self.assertEqual(paid["study"], "batching-v2")
        self.assertTrue(all(c["id"].startswith("batching-v2-") for c in paid["cases"]))
        self.assertEqual(batching.ENV.name, "venv")
        self.assertEqual(batching.ENV.parent.name, ".batching-v2")
        self.assertEqual(batching.output_path("control").parent.name, "batching-v2")
        self.assertTrue(
            all(
                "batching-v2" in p or p == "tools/batching_v2.py"
                for p in paid["sourceSha256"]
            )
        )

    def test_invalid_or_duplicate_factors_are_rejected(self):
        for factors in (
            {"sizes": [0]},
            {"sizes": [1, 1]},
            {"seeds": [-1]},
            {"seeds": [17, 17]},
            {"repetitions": 0},
        ):
            with self.assertRaises(ValueError):
                batching.make_plan(**factors)


if __name__ == "__main__":
    unittest.main()
