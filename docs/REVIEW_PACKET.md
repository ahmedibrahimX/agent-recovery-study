# Independent review and reproduction

**Status: pending.** The goal is independent scrutiny and a useful architecture conclusion, not an endorsement or a badge. A reviewer with experience shipping tool-using agents should challenge both baseline competence and the oracle contract. Disclose relevant framework affiliations when recording a review.

## Review questions

1. Read [how the investigation developed](EXPERIMENT_HISTORY.md), the [batching results with explicit contracts](../results/batching-v2/README.md), and [the historical recovery scenario contracts](SCENARIOS.md). Is the permitted outcome after an inflight write settles reasonable? Distinguish dispatch, commit, result delivery, and model notice exposure. Record contract disagreements without silently changing historical scores.
2. Inspect both execution adapters and the shared guard/terminal path. Public synthetic sources are in `studies/batching-v2/` (explicit contracts) and `studies/batching-v1/` (initial batching); the [source guide](SOURCE-GUIDE.md) maps encrypted recovery sources. Were policy, information, budgets, and terminal semantics comparable? Are both implementations competent?
3. Run the root README commands. Confirm 48 adapter-affected and 24 corrected recovery verdicts, five original negative controls, the initial batching pilot/confirmation, and all 54 paid outcomes from batching with explicit contracts. Keep the studies, unpaid preflights and expected failures separate; use the [technical identity map](EXPERIMENT_HISTORY.md#technical-identity-map) to match verifier identifiers.
4. Inspect the [paired batching trajectory](../results/batching-v2/README.md#inspect-one-paired-batching-trajectory), its ordinary parallel-call baseline and retained reporting repairs, plus one corrected recovery inflight case and concurrent edit. Evaluate explanations as well as structured state/protocol outcomes. Challenge whether model-chosen grouping, synthetic delay or task mix limits the efficiency conclusion.
5. Identify one way the comparison or checker could mislead an engineer, and one architecture decision it helps—or explain why it is not useful.

Record the evidence manifest digest, OS/runtime versions, commands/output hashes, local changes, unexpected findings, and unresolved disagreements. The [review template](../study/reviews/template.json) is available for structured reports. For the protected historical archive, keep source/data encrypted in public discussion and use logical paths. Public synthetic sources and results are directly inspectable.

The unpaid verification checks saved evidence. It does not rerun stochastic model behavior. A fresh independent live run is a separate undertaking with additional setup and cost. Preserve unfavorable findings and implementation faults; a review should not become a search for cleaner headline scores.

The [NeurIPS checklist](https://neurips.cc/public/guides/PaperChecklist) and [ACM SIGIR artifact guidance](https://sigir.org/general-information/acm-sigir-artifact-badging/) inform the emphasis on bounded claims and reproducibility. Following parts of those guides conveys no certification.
