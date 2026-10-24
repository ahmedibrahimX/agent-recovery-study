# First measured conditional-batching configuration

The unchanged `batching-v1` source at commit `6b30ae1ace20158494cfb620846a49240d4f86be` produced these runs. The frozen primary checker validates state/history and selected structured claims; it does **not** enforce the entire closed report schema or grade free-form prose truthfulness. Later findings do not rewrite its saved verdicts.

The pilot has 18 paid trials: sizes 1/5/20 × clean/edit/withdraw × one seed (`20261023`) × one repetition × two arms. The separately planned confirmation has 54 paid trials with fresh seeds `93473`, `54781`, and `71839`, one repetition and both arms. All confirmation cases were retained. The default 162-trial matrix was not run. The 18-trial unpaid preflight is recorded separately and is not model-performance evidence.

## Verify and inspect

Python 3.12+ and Node 22+ are sufficient. No API key, dependency installation, Docker, model request or generated-program execution is needed:

```sh
python3 -B tools/verify_batching_v1.py
```

This checks every archive and file hash, then uses the unchanged v1 verifier to reproduce plans, source identities, fixtures, verdicts, costs, CSV and grouped comparisons. It also recomputes [metrics.json](metrics.json). Hashes establish integrity relative to this record, not independent authentication of provider provenance or external preregistration.

Each archive contains its original complete run directory, with relative file names and every file byte preserved: plan, environment, requests, responses, usage, programs, program results, journals, snapshots, reports, verdicts, aggregate files and local budget accounting. No dependencies or build files are included. The manifest identifies all 3,246 preserved run files. The source remains in `studies/batching-v1/` and `tools/batching.py`; even its original no-results status text is intentionally frozen because plans hash those bytes. This results record supplies the later status.

To read individual confirmation traces after verification:

```sh
mkdir -p /tmp/batching-v1-confirmation
tar -xzf results/batching-v1/confirmation.tar.gz -C /tmp/batching-v1-confirmation
```

## Confirmation outcomes

Each arm has 27 attempted trials. Costs are calculated from recorded usage at the plan's fixed accounting rates, not provider invoices or infrastructure costs.

| Metric | Ordinary tools | Code Mode |
| --- | ---: | ---: |
| Frozen primary outcomes | 26/27 | 27/27 |
| State-integrity passes | 27/27 | 27/27 |
| Model requests | 172 | 227 |
| Public API calls | 691 | 1,039 |
| Code execution blocks | — | 200 |
| Tool-result bytes presented to model, including repeated history | 1,167,591 | 1,720,094 |
| Guard-denied mutation requests | 13 | 119 |
| Mutation requests after withdrawal reached the model | 0 | 0 |
| Calculated model cost | $3.135602 | $4.610532 |

Code Mode batched API calls (5.195 calls per execution block across all confirmation trials), but this did not translate into an aggregate reduction in model requests or tool-result traffic. Calls per block includes retries, reads and denied requests; it is not a measure of productive batching by itself.

| Intents | Ordinary primary passes | Code primary passes | Median successful agent seconds, ordinary / Code | Code faster in jointly successful pairs | Median paired Code minus ordinary seconds | All-attempt cost, ordinary / Code |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 9/9 | 9/9 | 10.707 / 13.275 | 0/9 | +2.721 | $0.279666 / $0.343592 |
| 5 | 9/9 | 9/9 | 20.438 / 23.058 | 6/9 | −0.768 | $0.552258 / $0.562138 |
| 20 | 8/9 | 9/9 | 53.868 / 55.475 | 4/8 | −1.847 | $2.303678 / $3.704802 |

Arm medians and the median of paired differences answer different questions; subtracting arm medians does not reproduce the paired result. Size/history groups, including all failures and costs, are in `metrics.json` and each archived `comparison.json`. At size 20 the jointly successful comparison excludes one ordinary failure whose Code counterpart took 208.106 seconds. Keep that asymmetry visible. Agent time includes framework startup; full elapsed additionally includes worker startup/cleanup. Recorded clocks are rechecked, not remeasured offline.

## One complete paired failure and repair case

Case `batching-v1-3206004ab13a` is size 20, `edit`, seed `71839`. Its archived paths start with that case ID followed by `ordinary/` or `code/`.

1. `case.json` and `evidence.json` show the edit after the initial list snapshot and before result delivery. There is no withdrawal event or notice. The changed human note must survive.
2. Ordinary tools read recipients and ledgers, then correctly update 8 intents. Its `report.json` incorrectly interprets the changed note as a withdrawal signal, submits `stopped`, and leaves 12 intents pending. Updated classifications and state integrity pass; `verdict.json` fails the terminal-status contract. This is premature stopping, not an unauthorized committed write. It takes 6 model requests, 49 public calls, 54.185 seconds and $0.178148.
3. Code Mode initially reads a raw intent array. In `program-1.json`, it calls `JSON.parse((await codemode.list_intents({})).result)`. Internal API calls actually return raw values, so `program-1-result.json` reports that `undefined` is not valid JSON. Later programs repeat wrapper assumptions and include other coding errors; not every error has the same cause.
4. Code Mode eventually reconciles all 20 intents, preserving the human note. Its full trace retains 41 model requests, 135 public calls, 40 blocks, 208.106 seconds and $1.259658. No repair time or cost is subtracted. Its final selected structured claims pass the frozen checker; free-form text still needs review.

The recorded request context shows all generated success-return types as `unknown`. The source descriptors supply input schemas but omit output schemas. The API descriptions convey fields, but do not make the raw-value versus execution-wrapper distinction explicit. The traces support identifying this ambiguity as an integration weakness; they do not establish how much time explicit contracts would save or whether all repairs would disappear.

## Guard and schema boundaries

The 119 Code and 13 ordinary guard denials produced no forbidden effects. Withdrawal arrives between committed writes; already-generated parallel calls or code are not preempted. No mutation request occurs after withdrawal is visible in a recorded model request. Generated code may already have encountered and handled a rejection before the next model request, so this does not imply it was unaware of the rejection.

The frozen checker also accepts extra report root keys despite `additionalProperties: false` in the declared report schema. This occurs in one pilot report (`batching-v1-fa7b6f16f66a/code`) and two passing confirmation reports (`batching-v1-fcf14ee4f2e3/code`, `batching-v1-8e3376ae8c65/code`), each with an extra `code` field. Preserve their original passes, but do not call them complete schema compliance. Selected structured claims and complete free-form truthfulness are separate outcomes; prose has not received comprehensive independent review.

## Pilot remains separate

Both arms pass all 9 pilot trials. At size 20, the successful median agent times are 60.425 seconds ordinary versus 39.863 Code, with costs $0.881346 versus $0.519772. The stronger pilot advantage does not reproduce consistently in confirmation. Do not pool the runs, select favorable seeds, replace failures or remove repairs.

## Interpretation and next condition

This configuration shows successful batching in some trajectories and substantial repair/denial overhead in others. It does not establish a consistent efficiency advantage for Code Mode, nor general superiority for ordinary tools. Code Mode's one additional primary pass is meaningful case evidence, not a statistically established reliability difference.

The workload is synthetic status reconciliation, not payment creation. There are three confirmation fixture seeds, one repetition per case, one provider/model and a shared host. Sizes share fixture prefixes and histories are correlated. Service delay is an injected 20 ms with concurrency four. Guards and notice gates are shared application engineering, not independent model judgment. There is no production distribution, real human approval/resume cycle, process-restart or cross-service atomicity evaluation.

The separately [measured batching-v2 condition](../batching-v2/README.md) supplies explicit return contracts to both arms and validates the complete report schema online and offline. It changes documentation and grading/admission together, uses fresh paid seeds, and produces separate plans/results. It cannot isolate the causal effect of output schemas alone or retroactively repair these v1 outcomes.
