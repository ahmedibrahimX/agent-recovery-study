# Repository layout and integrity

The repository includes the documentation, offline verifier, original UAT controls, frozen experimental source, and saved evidence needed to inspect the study and reproduce its saved outcomes. No separate private checkout or evidence service is required.

Public documentation lives under `docs/`. Executable verification code and evidence live under `study/`. The exact agent implementations, experiment definitions, prompts, native snapshots, and requests are included in the encrypted evidence store and can be inspected locally with `study/evidence.py`.

`provenance/study-files.json` records hashes of the frozen study code and evidence. Run `python3 tools/check_package.py` to check these files. Documentation can evolve without rewriting the frozen implementation or changing the historical outcomes.

The encrypted evidence manifest digest is:

```text
0338babcba8de5c6dfe04907cc316d38990ee58d0328dc5e26795811e96d45c2
```

The inventory establishes consistency with the repository's records. It is not an independently signed provenance record or external preregistration. The original verifier additionally checks frozen source hashes and each retained result against its checker.

Source, manifests, lockfiles, tests, documentation, and required encrypted evidence belong in version control. Installed dependencies, build products, caches, real credentials, and local plaintext extractions do not. The root `.gitignore` covers these generated/private paths.

Saved-result verification is self-contained once Python and Node are installed. Fresh live execution additionally requires pinned dependencies, protected AppWorld assets, simulator rebuilds, and provider access; a clean live rebuild remains unvalidated. See [reproduction](REPRODUCING.md) for the exact boundary.
