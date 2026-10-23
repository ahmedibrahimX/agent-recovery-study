# Validation record

Saved-result verification was run on macOS 15.2 arm64 with Python 3.13.3 and Node 25.1.0 on 23 October 2026. These are author-side local checks, not independent human review. Hosted [CI passed](https://github.com/ahmedibrahimX/agent-recovery-study/actions/runs/39997654980) on Linux and macOS using Python 3.13 and Node 22. Supplemental tools passed mypy 2.4.0, Ruff 0.17.2 linting, and Ruff formatting checks.

| Check | Outcome |
| --- | --- |
| Packaged code/evidence inventory | 3,268 frozen files matched |
| Included implementation/evidence versus source records | Byte identical |
| Saved v6 verdicts | All 48 reproduced; primary passes 23/24 in each arm |
| Saved v7 verdicts | All 24 reproduced; primary passes 12/12 ordinary, 11/12 Code Mode |
| Original negative controls | All five passed |
| Evidence authentication | 5,369 logical files / 3,257 unique blobs |
| Markdown links | All local targets resolve |
| Installed dependencies/build outputs/caches | Excluded |
| Clean Git clone, root README commands | Passed; verifier output hash unchanged |
| Saved approval-question type audit | All 33 saved questions are nonempty strings |
| Malformed-question diagnostic | Null, number, array, and object accepted by frozen checker; see [limitation](KNOWN-LIMITATIONS.md) |
| Live environment rebuild | Passed from included source on macOS arm64 with Docker; no original experiment image required |
| Unpaid live preflight | All 24 native fixture trials and four scripted-agent trials passed; all 28 fresh verdicts rechecked |
| New portability controls | Five Python controls and three intercepted-transport budget tests passed |
| Preflight model API spending | $0; no provider model calls, with zero outstanding reservations |

Verification used the frozen experimental source, UAT controls, encrypted evidence, and saved outcomes recorded in this repository.

The separate live workflow rebuild/preflight used Python 3.13.3 and Node 25.1.0 locally. The live CI job uses Python 3.12 and Node 22 on Ubuntu, rebuilds the simulator, and runs the complete unpaid preflight. Scripted responses validate plumbing, not hosted-model behavior; a fresh paid model replication was not performed as part of this change.

The full verifier JSON stdout SHA-256 was:

```text
4361a136b818e4de6b94c9883fd46caa609cf32e0a5f7be2fb28e34f447c1374
```

A saved-result reproduction includes expected agent failures and reuses saved timings. Fresh model execution and independent human reproduction remain separate validation steps.

Development used AI assistance. The checks reported here are author-side verification; independent human review is pending.
