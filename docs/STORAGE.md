# Evidence retention

All paid v6 and v7 run evidence is retained losslessly in the encrypted content store: requests/responses, programs and errors, ordered histories, native database snapshots, frozen sources, and budget records. The store uses content-addressed deduplication, compression, and authenticated encryption. It occupies about 128 MB of logical file storage.

The separate raw-run copies were removed only after byte comparisons against the encrypted store and successful verification of all 72 saved verdicts. The five negative controls also passed. The physical encrypted files and their local reader are included in this repository.

Earlier exploratory studies have source freezes and compact summaries, but many original raw traces were deleted during storage cleanup. They cannot now be independently reconstructed from those summaries. The [experiment history](EXPERIMENT_HISTORY.md) records these gaps; retained v6/v7 evidence must not be used to imply completeness for older studies.

Installed Node/Python dependencies, generated output, and simulator/Temporal images or state are not retained. The corrected v6/v7 comparison did not use Temporal. Source definitions and image identifiers remain, but they do not guarantee a byte-identical live rebuild. Saved-evidence verification does not need those removed resources.
