# Analysis plan — frozen before outcome estimation

Authored 2026-10-07. This is a retrospective portfolio analysis, not a prospectively registered clinical/business trial. The analyst knows the public dataset's broad context. The plan was recorded before this implementation's outcome estimates and is retained without rewriting around favorable findings.

## Decision and estimands

Retail email allocation over a two-week horizon. Assignment is intention-to-treat: denominator is every assigned customer, not visitors or buyers. Primary efficacy outcome: binary conversion; secondary visit and spend. Three pairwise comparisons per outcome (Men–Control, Women–Control, Men–Women), Holm adjustment within each outcome. Conversion is the confirmatory outcome; secondary outcomes and segment analyses are exploratory. Report pointwise 95% intervals and familywise Bonferroni intervals, unpooled proportion SE, pooled proportion tests and Welch spend tests. Approximate spend intervals can be sensitive to a sparse, heavy-tailed outcome; do not trim genuine purchases to improve significance.

Full sample campaign comparisons assess average treatment effects; full sample tables are never input to learned policy fitting. Standardized balance differences and omnibus balance tests diagnose assignment comparability; they cannot prove the randomization process was implemented correctly.

## Independent policy evaluation

Fixed seed 20080320, treatment-stratified 50/50 train/test split, using only assigned arm during splitting. Primary fixed scenario: 50% maximum email capacity, hypothetical contribution margin 40%, email cost $0.02, minimum net incremental contribution $0.00. No hyperparameter search, model selection, or refitting based on test outcomes. All scenario grids are fixed here: capacities 25%, 50%, 100%; costs $0, $0.02, $0.10, $0.50; margins 20%, 40%, 60%; minimum net contribution $0, $0.05, $0.10.

Baseline purchase propensity: L2 logistic regression fit to training control customers, features recency, log1p(history), prior mens/womens purchase flags, newbie, channel, zip category. Report held-out control AUROC, Brier score, calibration, and coefficients as regularized associations, not causal effects.

Transparent incremental policy: eight cells defined before fitting: recency <=4 vs >4 months crossed with historical merchandise flags (Men only, Women only, Both, Neither). For each arm/cell, shrink the training spend mean toward that arm's training overall mean with prior weight 1000. Rank maximum estimated incremental contribution, choose Men or Women, send nothing when the training score is not above the threshold, and enforce capacity. This is a simple partially pooled estimate, not a claim of individual causal effects. Prior weight is a fixed heuristic, not estimated Bayesian evidence.

Compare no email, blanket Men, blanket Women, capacity-matched random Men/Women, control-propensity Men, and segment incremental targeting. Fixed random priorities and tie-breaks use row sequence/seed, never outcomes. Separate propensity and causal targeting.

Evaluate on untouched test rows using assignment probabilities 1/3 from the published randomized design. Horvitz–Thompson (HT) policy improvement over no email uses the paired score Y_i * (1[A_i=pi(X_i)] - 1[A_i=0]) / p(A_i). SE is the sample SD of this score divided by sqrt(n). Comparison between policies uses paired score differences. Conditional on the training sample, intervals describe evaluation uncertainty; they omit training instability. Fixed count randomization details are unavailable, so IID design-based approximation is disclosed. Secondary policy/scenario estimates have pointwise intervals and are not a multiplicity-controlled search for a winning policy.

## Heterogeneity and next experiment

Eight prespecified cells: exploratory within-cell treatment effects, 16 cell-versus-control tests corrected together per outcome. An omnibus treatment × cell interaction diagnostic complements cellwise intervals; overlapping/nonoverlapping subgroup significance alone does not establish different treatment effects. Segment findings require a new experiment before deployment.

## Financial boundary

Spend is observed customer purchase spend. Incremental spend is a treatment-control or policy-control contrast. Contribution scenarios = assumed margin × estimated incremental spend − assumed cost × emails. Actual margins, deliverability, customer lifetime value, unsubscribes, and operating costs are absent; no actual profit, realized growth, or measured ROI is claimed. Historical 2008 findings do not establish current marketing performance.
