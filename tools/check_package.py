#!/usr/bin/env python3
"""Check preserved study bytes against this package's own provenance record."""

import hashlib
import json
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent


def check():
    inventory = json.loads((ROOT / "provenance/study-files.json").read_text())
    if inventory["format"] != 1:
        raise RuntimeError("unsupported inventory version")
    expected = inventory["files"]
    study = ROOT / "study"
    actual = set()
    for path in study.rglob("*"):
        if path.is_symlink():
            raise RuntimeError(f"unexpected symlink: {path.relative_to(study)}")
        if path.is_file():
            actual.add(path.relative_to(study).as_posix())
    if actual != set(expected):
        raise RuntimeError(
            f"study inventory changed: missing={sorted(set(expected) - actual)}, "
            f"unexpected={sorted(actual - set(expected))}"
        )
    for relative, digest in expected.items():
        name = PurePosixPath(relative)
        if name.is_absolute() or any(
            part in (".", "..") for part in relative.split("/")
        ):
            raise RuntimeError(f"unsafe inventory path: {relative}")
        with (study / relative).open("rb") as stream:
            actual_digest = hashlib.file_digest(stream, "sha256").hexdigest()
        if actual_digest != digest:
            raise RuntimeError(f"preserved file changed: {relative}")
    catalog = json.loads((study / "evidence/catalog.json").read_text())
    recorded_manifest = (
        "0338babcba8de5c6dfe04907cc316d38990ee58d0328dc5e26795811e96d45c2"
    )
    if catalog["manifestSha256"] != recorded_manifest:
        raise RuntimeError("unexpected evidence manifest identity")
    with (study / "evidence/manifest.bin").open("rb") as stream:
        if hashlib.file_digest(stream, "sha256").hexdigest() != recorded_manifest:
            raise RuntimeError("encrypted evidence manifest changed")
    return {
        "packagedStudyFilesMatched": len(expected),
        "evidenceManifestSha256": recorded_manifest,
    }


if __name__ == "__main__":
    print(json.dumps(check(), indent=2))
