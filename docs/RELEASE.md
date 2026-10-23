# Release checklist

## Verification

- [x] Run the root README commands from a clean checkout.
- [x] Run the GitHub Actions workflow on Linux and macOS.
- [x] Confirm that study-file hashes match before and after verification.
- [x] Keep v6 and v7 outcomes separate and retain expected failures.
- [x] Record runtime versions and verification output hashes.
- [x] Audit saved approval-question types and document the frozen checker limitation.
- [x] Rebuild the live environment and exercise all native scenarios plus both agent paths without paid calls.

## Distribution

- [x] Include license scope, third-party notices, and upstream attribution.
- [x] Inspect tracked files and Git history for credential patterns and private preparation notes.
- [x] Exclude installed dependencies, build outputs, caches, and plaintext evidence extractions.
- [x] Enable private vulnerability reporting and document the reporting URL.
- [x] Document the private GitHub conduct-reporting route and public maintainer contact.
- [x] Configure required CI checks for the default branch.
Publish versioned tags and release notes only after their checks pass. See [releases](https://github.com/ahmedibrahimX/agent-recovery-study/releases).

## Review status

Independent review is pending. Reviewers can use the [review questions](REVIEW_PACKET.md) and [walkthrough](REVIEWER-WALKTHROUGH.md) to assess the contract, baseline, oracle, and architecture conclusion. Record both reproduced outcomes and disagreements.

## References

- [GitHub Open Source Guides](https://opensource.guide/starting-a-project/)
- [GitHub Actions security guidance](https://docs.github.com/en/actions/reference/security/secure-use)
- [OpenSSF Best Practices criteria](https://www.bestpractices.dev/en/criteria/0)
