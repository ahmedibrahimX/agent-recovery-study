# Release checklist

## Verification

- [x] Run the root README commands from a clean checkout.
- [ ] Run the GitHub Actions workflow on Linux and macOS.
- [x] Confirm that study-file hashes match before and after verification.
- [x] Keep v6 and v7 outcomes separate and retain expected failures.
- [x] Record runtime versions and verification output hashes.
- [x] Audit saved approval-question types and document the frozen checker limitation.

## Distribution

- [ ] Review license scope, third-party notices, and required attribution.
- [ ] Inspect tracked files and Git history for credentials and private material.
- [x] Exclude installed dependencies, build outputs, caches, and plaintext evidence extractions.
- [ ] Enable private vulnerability reporting and document the reporting URL.
- [ ] Document the private moderation contact.
- [ ] Configure required CI checks for the default branch.
- [ ] Tag the release and publish its changelog after checks pass.

## Review status

Independent review is pending. Reviewers can use the [review questions](REVIEW_PACKET.md) and [walkthrough](REVIEWER-WALKTHROUGH.md) to assess the contract, baseline, oracle, and architecture conclusion. Record both reproduced outcomes and disagreements.

## References

- [GitHub Open Source Guides](https://opensource.guide/starting-a-project/)
- [GitHub Actions security guidance](https://docs.github.com/en/actions/reference/security/secure-use)
- [OpenSSF Best Practices criteria](https://www.bestpractices.dev/en/criteria/0)
