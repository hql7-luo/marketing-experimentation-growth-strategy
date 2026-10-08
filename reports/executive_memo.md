# Executive Decision Memo

**Decision:** Prefer a simple Men's Email baseline for a fresh randomized pilot. With a strict budget, reserve a control group and compare the learned segment rule against capacity-matched random Men's Email before investing in personalization.

**Scope:** Retrospective analysis of Kevin Hillstrom's March 2008 public challenge, 64,000 randomized customers, two-week outcomes. This is an analytical recommendation; no campaign was implemented and no growth was realized.

## What did we find, and how confident are we?

| Assignment | Customers | Conversion | Spend / assigned customer |
|---|---:|---:|---:|
| No Email | 21,306 | 0.573% | $0.653 |
| Men's Email | 21,307 | 1.253% | $1.423 |
| Women's Email | 21,387 | 0.884% | $1.077 |

Men's Email increased conversion by **0.681 percentage points** versus no email (95% CI **0.500–0.861 pp**, Holm p=4.57×10⁻¹³). Women's Email increased conversion by **0.311 pp** (CI **0.150–0.472 pp**, Holm p=0.000314). Men exceeded Women by **0.369 pp** (CI **0.174–0.564 pp**, Holm p=0.000314). All three primary conversion comparisons survive the family adjustment.

Secondary incremental spend was **$0.770/customer** for Men (CI **$0.485–$1.055**) and **$0.424** for Women (CI **$0.169–$0.680**). Men–Women spend was $0.345 (Holm p=0.0305), but its conservative Bonferroni familywise CI was **−$0.037–$0.728**. Purchase spend is sparse: only 578 buyers. The campaign preference is strongest on conversion; monetary precision is weaker.

Largest absolute pre-treatment standardized imbalance was **0.0169**. This supports comparability, without independently verifying the retailer's randomization. Exploratory conversion interaction p=0.0472 is borderline; spend interaction p=0.2258 provides no clear heterogeneity evidence. Recent customers who historically bought both categories are an experimental candidate, not a proven deployable segment.

## Which strategy, under limited resources?

On 32,000 untouched test customers, assume **40% contribution margin and $0.02/email**. Values below are incremental contribution estimates per 10,000 eligible customers, not measured profit.

| Policy | Emails / 10,000 | Assumed contribution | Pointwise 95% CI |
|---|---:|---:|---:|
| No Email | 0 | $0 | $0–$0 |
| Blanket Men | 10,000 | $3,073 | $1,468–$4,677 |
| Blanket Women | 10,000 | $1,486 | $71–$2,901 |
| Random Men, 50% capacity | 5,000 | $1,638 | $555–$2,720 |
| Purchase propensity Men, 50% | 5,000 | $1,468 | $226–$2,709 |
| Segment incremental, 50% | 5,000 | $1,859 | $692–$3,025 |

The segment rule sends approximately 4,267 Men and 733 Women emails per 10,000 eligible customers. Its spend advantage over random Men is **$0.055/customer**, paired CI **−$0.261–$0.372**; over purchase propensity targeting, **$0.098**, CI **−$0.120–$0.315**. Neither establishes a reliable advantage. The expected extra contribution over random Men is about **$221/10,000**, with an interval spanning **−$1,045 to $1,486**. Added targeting complexity has not earned its business case.

The control purchase model has AUROC **0.654** and Brier **0.006149**, only slightly better than constant probability **0.006158**. Higher predicted natural purchase likelihood cannot identify who needs an email; individual “would-buy-anyway” customers are unobservable here.

## Financial assumptions and allocation

At $0.02/email, budgets of **$50, $100, $200 per 10,000 customers** fund maximum capacities of **25%, 50%, 100%**. At $0.10/email, those same capacities require $250, $500, $1,000. Use actual cost and margin before selecting an operating policy; both are absent from the data.

At 40% assumed margin, the full-sample Men's Email spend estimate implies a break-even cost of **$0.308/email** (pointwise uncertainty range **$0.194–$0.422**). Women's estimate implies $0.170 ($0.068–$0.272). These are expected two-week contribution thresholds, not real ROI or safe spending guarantees. A $0.50/email scenario causes the segment rule to withhold most emails; maximum capacity is an upper limit, not a requirement to spend the budget.

**Management action:** Use Men as the simple campaign benchmark, and keep a randomized no-email control. At limited capacity, do not claim the available evidence proves segment or propensity targeting is superior to random allocation. Test the transparent segment rule as a challenger. Send nothing where train-estimated contribution falls below the chosen threshold; validate that no-send decision prospectively.

## Risks and the next experiment

Historical retailer, no exact campaign/deliverability metadata, no customer IDs, 6,562 indistinguishable rows retained, sparse purchases, only two weeks of follow-up, unknown costs/margins, no unsubscribe/customer-fatigue measures. Model intervals omit training instability. Secondary segment/policy/scenario analyses have exploratory or pointwise uncertainty; the retrospective plan is not a prospective preregistration.

Run a current, consent-compliant policy experiment with equal budget for **random Men** and **segment incremental**, plus **No Email control**. Freeze rules and costs before assignment, randomize within historical customer strata, record delivery and unsubscribes, and collect actual contribution margin. Primary outcome: incremental contribution per eligible customer; conversion is a supporting endpoint. Size the trial from a management-approved minimum effect and expected variance, not a promised historical uplift. Record a primary contrast and multiplicity plan, stop rules, and a longer customer-value horizon.

Evidence: [campaign contrasts](tables/campaign_contrasts.csv), [held-out policies](tables/policies_holdout.csv), [paired differences](tables/policy_paired_differences.csv), [all financial scenarios](tables/scenario_grid.csv), [methods](../docs/methodology.md), [source and rights](../docs/data-source.md).
