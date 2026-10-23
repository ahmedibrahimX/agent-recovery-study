# Independent review and reproduction

**Status: pending.** The goal is independent scrutiny and a useful architecture conclusion, not an endorsement or a badge. A reviewer with experience shipping tool-using agents should challenge both baseline competence and the oracle contract. Disclose relevant framework affiliations when recording a review.

## Review questions

1. Read [the scenario contracts](SCENARIOS.md). Is the permitted outcome after an inflight write settles reasonable? Distinguish dispatch, commit, result delivery, and model notice exposure. Record contract disagreements without silently changing historical scores.
2. Inspect both execution adapters and the shared guard/terminal path using the [source guide](SOURCE-GUIDE.md). Were policy, information, budgets, and terminal semantics comparable? Are both implementations competent?
3. Run the root README commands. Confirm 48 v6 and 24 v7 saved verdict matches, five passing negative controls, and preserved expected agent failures. Keep the two matrices separate.
4. Inspect one v7 inflight failure and one concurrent-edit case's requests, terminal submission, history, and intermediate SQLite snapshots. Evaluate the explanation as well as the structured state/protocol outcome.
5. Identify one way the comparison or checker could mislead an engineer, and one architecture decision it helps—or explain why it is not useful.

Record the evidence manifest digest, OS/runtime versions, commands/output hashes, local changes, unexpected findings, and unresolved disagreements. The [review template](../study/reviews/template.json) is available for structured reports. Keep protected source/data encrypted in public discussion; use logical paths rather than decrypted contents.

The unpaid verification checks saved evidence. It does not rerun stochastic model behavior. A fresh independent live run is a separate undertaking with additional setup and cost. Preserve unfavorable findings and implementation faults; a review should not become a search for cleaner headline scores.

The [NeurIPS checklist](https://neurips.cc/public/guides/PaperChecklist) and [ACM SIGIR artifact guidance](https://sigir.org/general-information/acm-sigir-artifact-badging/) inform the emphasis on bounded claims and reproducibility. Following parts of those guides conveys no certification.
