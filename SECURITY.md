# Security and execution boundaries

This is a local engineering study artifact, not a sandbox or a production safety system. The saved verifier starts the Node evidence reader and imports the preserved Python checker. It does not execute generated agent programs, contact models, or start Docker. Review the included executable code as you would any repository.

Encrypted blobs are authenticated and plaintext hashes/sizes checked. Public passphrase encryption is distribution packaging, not secrecy. Hash records establish consistency, not independent author provenance. Read THIRD_PARTY_NOTICES.md before redistributing material.

Default verification uses temporary directories and cleans them. Explicit evidence extraction persists plaintext at the selected destination; do not publish it. Use an ignored local directory outside `studies/recovery/` and remove it when finished. The original verifier's optional report output may overwrite a chosen existing path.

Python `-E -s -B` keeps environment overrides from disabling assertions, disables user site packages, and avoids bytecode files. It does not isolate filesystem/network access or make malicious Python safe. No wall-clock timeout, OS sandbox, or process-tree cleanup is added by this packaging. The CI job timeout bounds the hosted job only.

Report vulnerabilities privately using [GitHub private vulnerability reporting](https://github.com/ahmedibrahimX/agent-recovery-study/security/advisories/new). Do not post exploit details, private evidence, or credentials in public issues. Non-sensitive hardening suggestions can use the issue tracker. There is no security certification, production guarantee, or response-time SLA.

