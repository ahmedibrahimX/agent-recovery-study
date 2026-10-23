# Validation record

Saved-result verification was run on macOS 15.2 arm64 with Python 3.13.3 and Node 25.1.0 on 23 October 2026. These are author-side local checks, not independent human review. The configured Linux/macOS GitHub Actions jobs have not yet run on a hosted repository.

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

Verification used the frozen experimental source, UAT controls, encrypted evidence, and saved outcomes recorded in this repository.

The full verifier JSON stdout SHA-256 was:

```text
4361a136b818e4de6b94c9883fd46caa609cf32e0a5f7be2fb28e34f447c1374
```

A saved-result reproduction includes expected agent failures and reuses saved timings. Fresh model execution and independent human reproduction remain separate validation steps.

Development used AI assistance. The checks reported here are author-side verification; independent human review is pending.
