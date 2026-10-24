# Review the experiment before the conclusion

Use this guide to assess the scenario contract, inspect the implementation, and reproduce a saved result.

Start with the [paired trajectory from batching with explicit tool contracts](../results/batching-v2/README.md#inspect-one-paired-batching-trajectory): original requests, dependent reads, grouped writes, effects, timings and verdicts. The separate [historical withdrawal case](CASE-WALKTHROUGH.md) explains how an achieved external state can still violate a chosen terminal contract. Both walkthroughs summarize retained evidence, not new demonstrations.

## 1. Start with the decision

The [study of batching with explicit tool contracts](../results/batching-v2/README.md) supports a size-dependent choice on this workload: both arms pass 27/27, ordinary tools are usually faster at sizes 1/5, and Code is faster in all nine size-20 pairs with fewer model requests and lower calculated cost. Read the paired trace and retained repairs, then challenge whether the finding transfers to your workload. The [initial batching experiment](../results/batching-v1/README.md) remains visible with mixed efficiencies and return-contract/report-schema limitations; multiple changes prevent an output-schema-only causal claim. Keep the tasks, scoring contracts and versions separate. The [historical decision](DECISION.md) to start with ordinary tools concerns the original bounded AppWorld prototype; Temporal's durability value was not tested by that final comparison.

## 2. Challenge one scenario contract

Read `withdraw_inflight_write` in the [scenario document](SCENARIOS.md).

```text
write admitted → approval withdrawn → write settles → notice reaches model → final report
```

The contract permits the already admitted effect to settle. Further changes need authority. It additionally requires a renewed-approval question even if the requested state is already achieved. That terminal rule is a product policy choice. Ask whether an accurate settled-write explanation with no further action would be preferable; disagreement belongs in review findings, not a silent change to historical scoring.

The Code Mode failure in the corrected recovery comparison violated this terminal protocol. It did not create a forbidden external effect. Distinguishing these facts is central to interpreting the 12/12 versus 11/12 result.

## 3. Inspect the architecture

Read the [architecture](ARCHITECTURE.md). Both arms share approval/field checks, notice delivery, and the pending-notice terminal gate. Zero observed invalid effects cannot be attributed solely to model reasoning.

The exact sources are available locally through the evidence reader. [Source guide](SOURCE-GUIDE.md) maps the shared service, Python agent loop, Node execution adapters, prompts, and checker. Review policy equality and interface competence before comparing timings.

## 4. Reproduce the outcomes

Run the saved-result commands in the root README. Keep the adapter-affected and corrected recovery comparisons, the initial batching experiment, and batching with explicit tool contracts separate. The [technical identity map](EXPERIMENT_HISTORY.md#technical-identity-map) connects those names to archive identifiers. Confirm expected failures remain failures and all five original negative controls pass. A useful negative control detects a transient lost edit even when the final state is unchanged. `python3 -B tools/verify_batching_v1.py` and `python3 -B tools/verify_batching_v2.py` separately check each version's measured run bytes, source identities, verdicts and published metrics.

The original verification report is [study/verification-author.json](../study/verification-author.json). A fresh local report is an author-side reproduction, not outside certification. Do not describe the saved model calls as newly rerun.

## 5. Identify what the score misses

The supplementary prose audit found inaccuracies in both arms despite preserved external state. This demonstrates why a structured/state pass does not imply a truthful or useful final explanation. See the [interpretation](CASE_STUDY.md) and [claims map](CLAIMS.md).

Return one criticism of the scenario or baseline, one outcome you reproduced, and one architecture conclusion you found useful—or explain why it was not useful. Include runtime versions, local changes, and the evidence manifest digest. The original [review template](../study/reviews/template.json) can capture this. No endorsement is requested or presumed.

