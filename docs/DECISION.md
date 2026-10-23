# Architecture decision

For a bounded task that can finish within a single agent invocation, use ordinary `create_agent` tools and explicit approval/field checks, reliable input delivery, and evidence-grounded reporting. This is the simplest approach supported by the corrected local comparison. It still needs independent review and production validation.

Use Code Mode when real tasks benefit from conditional batches, processing large intermediate results, or a large typed tool surface. This pilot's tiny catalogs and roughly one API call per execute block did not demonstrate those advantages. Measure the actual workload before adding the extra interface.

Consider Temporal when tasks must survive process/host failure, wait across long approval periods, track execution over days, or retry durable activities. Correct external effects still require endpoint idempotency/reconciliation and current authority at dispatch. The final comparison did not exercise restart/durable-resume behavior; it cannot tell us whether Temporal is unnecessary for such requirements. Earlier exploratory Temporal results do not settle that question.

Do not build new runtime machinery on this evidence. Use/contribute to existing projects if a reviewed failure is an implementation issue. A small integration library becomes justified if the same verified glue recurs in independent applications and someone wants to use it. A research effort requires a precise unresolved failure that persists under competent baselines and fresh independent checks, or a demonstrably useful rigorous benchmark. The current contribution is an engineering account of the methods, mistakes, and resulting decision.

Next gate: one outside engineer reviews a scenario and baseline path, reproduces an important saved result, and reports whether this artifact helps an architecture decision. If they find a repairable baseline flaw, correct/version it and reserve fresh cases. If no residual gap survives, stop the new-runtime direction.
