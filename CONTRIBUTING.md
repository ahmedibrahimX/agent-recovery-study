# Contributing

Useful contributions challenge a scenario contract, reproduce a saved outcome, improve the public explanation, identify an oracle/baseline weakness, or fix a portability problem without concealing historical failures.

## Verify locally

Requirements: Python 3.12+ with SQLite deserialize, Node 22+, and about 200 MB temporary free space. From the root:

```sh
python3 tools/check_package.py
python3 -E -s -B study/verify.py
python3 -E -s -B -m unittest discover -s study -p test_verifier.py -v
```

No credentials, paid calls, Docker, or package installation are needed. The verifier executes trusted preserved Python checker code. Review SECURITY.md before running any external artifact.

## Preserve the experiment

Treat `study/` and its provenance inventory as frozen. Propose explanatory changes under `docs/`. Diagnose portability fixes separately; experimental behavior changes need a separately versioned implementation and appropriate fresh cases, not edited historical scores. Do not tune on exposed failures and present the rerun as heldout evidence.

For a proposed change, describe the problem, before/after behavior, validation, and limits. Add meaningful tests for new functionality. Identify whether a result is saved-evidence verification, a new live run, or outside human review. Credit collaborators and substantial AI assistance where relevant. Contributions must be material you can license under the applicable project terms.

## Reporting findings

Once the GitHub repository exists, use an issue or pull request for non-sensitive findings. Include OS/runtime versions, redacted commands, exit status, local changes, and the affected claim. The review template under `study/reviews/` can record a broader reproduction.

Never post credentials, workplace material, or decrypted AppWorld-derived evidence. Refer to protected logical paths without pasting contents. Follow SECURITY.md for security-sensitive findings.

