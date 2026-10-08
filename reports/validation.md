# Validation record

Verified on 2026-10-07 (America/Los_Angeles). This report distinguishes source-dependent local reproduction from the narrower remote CI contract.

## Completed local checks

- **Source:** two independent downloads from the publisher matched the pinned SHA-256. Actual 64,000 rows / 12 fields, 0 missing values, preserved 6,562 indistinguishable records. Source audit and explicit redistribution boundary are documented. No source rows or customer predictions are staged.
- **SQL reconciliation:** all three SQLite outputs agree with pandas; primary campaign rates and monetary means match to numerical tolerance.
- **Independent calculation:** a separate calculation script importing no project modules reproduced all nine campaign contrasts, Holm/Bonferroni statistics, seven fixed policies, three paired policy contrasts and 108 scenarios from the original CSV. This is an independent automated calculation, not a human external peer review.
- **Methods tests:** 48 tests pass, covering hand-computed proportions/Welch intervals, multiplicity families, comparison orientation, exhaustive randomization expectation, paired covariance, action/index/probability validation, outcome-independent selection, split/capacity invariants and refusal to overwrite a local file with changed publisher bytes. Synthetic fixtures appear only in tests.
- **Packaging and clean reproduction:** editable install succeeds. A separate source directory and newly created Python 3.12 environment, installed from the exact lock file, complete the source-dependent pipeline and all 48 tests. All **28** published aggregate/figure artifacts reproduce byte-for-byte, including deterministic SVGs and PNGs. Identical hashes demonstrate packaging/reproducibility, not the external validity of the experiment.
- **Notebook:** all six code cells executed successfully and were saved. Outputs contain aggregates and charts only; no customer records or row-level predictions.
- **Code checks:** Ruff check/format and staged whitespace check pass. MIT scope excludes the dataset.
- **Visual QA:** all six actual PNGs were inspected for correct values/intervals, labels, visible captions and legibility. No clipping/overlap was observed. Figure 03 explicitly says segment differences need confirmation. Budget figure uses point estimates and sends readers to complete interval tables.
- **Interpretation review:** both README and memo languages reconcile with tables. Targeting advantage is unproven, Holm-vs-Bonferroni difference is disclosed, financial inputs are assumptions, merchandise history is not gender, and there are no actual ROI/realized-growth/current-market claims.

## Remote CI contract

GitHub Actions runs on Python 3.12 and 3.13: locked dependency installation, editable package install, Ruff, all tests, executed-notebook/error checks, raw-publication guard, local-link validation and aggregate/figure checksum verification. It **does not download customer data or rerun the full source-dependent pipeline**. Review the actual commit's Actions run before describing remote CI as passed; this file records the contract and completed local checks, not a future run result.

## Remaining analytical uncertainty

Original randomization implementation and customer identity cannot be independently audited. Normal/Welch and sparse-subgroup HC3 intervals are asymptotic. Holdout intervals condition on training and omit training instability. Policy/scenario intervals are pointwise, not an adjusted winner search. Historical two-week effects, unknown margin/cost and absent delivery/unsubscribe/long-term information require a current prospective experiment.
