# Review the experiment before the conclusion

Use this guide to assess the scenario contract, inspect the implementation, and reproduce a saved result.

For a concrete starting point, read [one complete paired case](CASE-WALKTHROUGH.md): objective, intervention, observed actions, external effects, terminal reports, and verdicts. It is a summary of retained experimental evidence, not a new demonstration.

## 1. Start with the decision

For short bounded tasks, the corrected experiment supports ordinary tools with explicit application safeguards. Code Mode's potential value for substantial batching remains untested; Temporal's durability value was not tested by the final comparison. Read the [decision](DECISION.md), then try to disprove its scoped reasoning.

## 2. Challenge one scenario contract

Read `withdraw_inflight_write` in the [scenario document](SCENARIOS.md).

```text
write admitted → approval withdrawn → write settles → notice reaches model → final report
```

The contract permits the already admitted effect to settle. Further changes need authority. It additionally requires a renewed-approval question even if the requested state is already achieved. That terminal rule is a product policy choice. Ask whether an accurate settled-write explanation with no further action would be preferable; disagreement belongs in review findings, not a silent change to historical scoring.

The Code Mode failure in v7 violated this terminal protocol. It did not create a forbidden external effect. Distinguishing these facts is central to interpreting the 12/12 versus 11/12 result.

## 3. Inspect the architecture

Read the [architecture](ARCHITECTURE.md). Both arms share approval/field checks, notice delivery, and the pending-notice terminal gate. Zero observed invalid effects cannot be attributed solely to model reasoning.

The exact sources are available locally through the evidence reader. [Source guide](SOURCE-GUIDE.md) maps the shared service, Python agent loop, Node execution adapters, prompts, and checker. Review policy equality and interface competence before comparing timings.

## 4. Reproduce the outcomes

Run the three commands in the root README. Keep v6 and v7 separate. Confirm expected failures remain failures and all five negative controls pass. A useful negative control detects a transient lost edit even when the final state is unchanged.

The original verification report is [study/verification-author.json](../study/verification-author.json). A fresh local report is an author-side reproduction, not outside certification. Do not describe the saved model calls as newly rerun.

## 5. Identify what the score misses

The supplementary prose audit found inaccuracies in both arms despite preserved external state. This demonstrates why a structured/state pass does not imply a truthful or useful final explanation. See the [interpretation](CASE_STUDY.md) and [claims map](CLAIMS.md).

Return one criticism of the scenario or baseline, one outcome you reproduced, and one architecture conclusion you found useful—or explain why it was not useful. Include runtime versions, local changes, and the evidence manifest digest. The original [review template](../study/reviews/template.json) can capture this. No endorsement is requested or presumed.

