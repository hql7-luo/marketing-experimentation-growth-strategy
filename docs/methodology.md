# Methods and decision boundaries

## Unit, features and outcomes

Each of 64,000 publisher rows is one assigned customer. No customer identifier is supplied. All rows are retained, including 6,562 indistinguishable full-field records. We cannot establish that these are duplicate customers. There are no missing values; only the documented `Surburban` spelling is normalized.

Eight original customer attributes precede treatment; `history_segment` duplicates a discretization of `history`, so the logistic baseline uses seven attributes with log1p(history). `mens` and `womens` represent prior purchases, not gender. Assigned campaign, visit, conversion and spend are excluded from all targeting feature frames.

`conversion` is a purchase within two weeks, `visit` a site visit, and `spend` purchase dollars. Rates and monetary means use every assigned customer as denominator. Buyer-only average spend would condition on a treatment-affected outcome and cannot replace intention-to-treat incremental spend.

## Average campaign effects

For each comparison, effect = treatment mean − reference mean. Binary SE = sqrt(p_t(1−p_t)/n_t + p_c(1−p_c)/n_c); two-sided hypothesis tests pool the proportion under the equality null. Spend uses sample variance and Welch unequal-variance degrees of freedom. These are large-sample intervals; spend is especially sparse (578 buyers, 0.903% of customers) and has a heavy right tail.

Holm correction controls the three-comparison family separately for conversion, visits, and spend. Conversion is the primary endpoint; visits/spend are secondary, so significance across all outcomes is not one globally controlled nine-test claim. Pointwise 95% CIs and more conservative Bonferroni 95% familywise CIs are both exported. Holm tests can reject a comparison whose Bonferroni CI contains zero because the adjustments are different. Men–Women spend does exactly this; report it instead of hiding it.

Balance: all pre-treatment numeric/binary/dummy variables have pairwise standardized mean differences. ANOVA and chi-square diagnostics accompany them. Small SMDs support comparability but do not verify assignment implementation, interference, deliverability or missing source records.

Sources: [SciPy Welch test](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_ind.html), [statsmodels proportion z-test](https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.proportions_ztest.html), [Holm multiple tests](https://www.statsmodels.org/stable/generated/statsmodels.stats.multitest.multipletests.html).

## Historical heterogeneity

The frozen grid is recency ≤4 vs >4 months crossed with historical Men only/Women only/Both/Neither merchandise. Neither is absent; six cells are observed. Preserve the planned 16 treatment-versus-control hypotheses per outcome by padding the four unestimable comparisons with p=1 before Holm. Only observed cells receive estimates. Full-sample subgroup plots are exploratory and cannot train the policy. HC3 additive treatment × segment joint Wald tests diagnose conversion/spend heterogeneity; sparse purchases weaken their asymptotic precision. A significant subgroup and a nonsignificant subgroup do not themselves prove different effects.

## Predictive baseline and policy learning

A fixed L2 logistic model (C=1) is trained on training control customers only. Recency, log-history and binary numeric predictors are standardized using training control means/SDs; categorical predictors use one-hot reference levels. Coefficients for numeric variables are per training SD and remain regularized associations. Test AUROC, Brier, log loss and calibration are evaluated only in held-out control rows; low Brier in rare outcomes is not evidence of a strong targeting policy.

The incremental rule estimates training arm/cell spend means and shrinks each toward its training arm average with fixed pseudo-count 1000. This transparent heuristic stabilizes small cells; it is not a validated individual uplift model. For each historical profile, choose the arm with higher estimated net contribution, filter below a minimum, and rank under capacity. Ties use input order; the absence of real customer ID prevents a portable personalized deployment rule. No tree/complex learner is needed to establish the main finding.

Data split is stratified by arm, 32,000 train and 32,000 test, seed 20080320. Model/segment choices and primary scenario were fixed before pipeline outcome estimation. The plan is retrospective, not a prospective preregistration. Full sample effect reporting does not feed policy fitting; no tuning uses test outcomes.

## Offline policy evaluation

Assume the published 1/3 treatment probabilities. For fixed policy pi, incremental score against no email:

`z_i = Y_i × (1[A_i = pi(X_i)] − 1[A_i = 0]) / p(A_i)`.

Average z over all test customers, not just matched assignments. No Email selections cancel exactly. Standard error is sample SD(z)/sqrt(n); policy comparisons difference the two score vectors before estimating their SE, retaining covariance. [Horvitz–Thompson (1952)](https://stat.cmu.edu/~brian/905-2008/papers/Horvitz-Thompson-1952-jasa.pdf).

Intervals are pointwise and conditional on this fitted training rule; they omit training instability and do not correct a search over scenarios. The original exact fixed-count randomization mechanics are unavailable; the IID variance approximation is disclosed. Full-sample difference-in-means and held-out HT estimates target related population effects but need not match exactly.

Blanket policies send to 100%; the primary constrained policies to at most 50%. Compare them with their email volume visible, not as if they consume the same budget. Capacity-matched random and propensity policies are the fair targeting comparators. Do not call the highest point estimate a proven winner.

## Financial scenarios

For N eligible customers, margin m, cost c, selected share q:

- Incremental purchase spend = N × estimated policy spend improvement.
- Email budget consumed = N × q × c.
- Assumed incremental contribution = N × (m × improvement − c × q).
- Maximum send capacity with budget B = min(1, B/(N×c)), when c>0.
- Break-even cost = m × improvement/q, when q>0; this is estimated, not a real contractual cost ceiling.

Margin/cost/threshold inputs are explicitly hypothetical. The dataset has no actual cost, gross margin, unsubscribe, lifetime value or net profit. Do not report real ROI or realized growth. All displayed per-10,000 effects are scaled estimates under stable-population assumptions, not executed campaigns.
