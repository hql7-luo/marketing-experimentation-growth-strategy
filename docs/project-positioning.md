# Existing project audit and new-project distinction

Reviewed on 2026-10-07 (America/Los_Angeles). This is a read-only scope/architecture audit, not a fresh test run of the existing applications. Live GitHub repository listing, main commit identities, current README files, file trees and selected key implementation/architecture files were inspected. The Oct 5 local clones were stale and were not edited.

## Verified current projects

| Project | Current main commit | Existing decision problem | Data/evidence boundary | What the marketing project adds |
| --- | --- | --- | --- | --- |
| [Supply Chain Decision Intelligence](https://github.com/hql7-luo/supply-chain-decision-intelligence) | `605fd679391c8e4deb12b3bcce7901ba60bfbce7` | Prioritize historical availability risk, compare observed-sales forecasts, explore transparent replenishment assumptions | Real FreshRetailNet-50K data, 2024-03-28 to 2024-07-02; normalized observed sales, not monetary revenue; no causal lost-demand or realized-savings claim | A randomized customer-level experiment, conversion/spend causal contrasts, multiple comparisons, campaign heterogeneity and constrained marketing resource decisions |
| [B2B Export Sales Workspace](https://github.com/hql7-luo/b2b-export-sales-intelligence) | `7df2b056013d8d6f1a123cc2836b8caa86560df8` | Persist Inquiry → Customer → Quotation → Follow-up relationships and support sales operations | All bundled contacts, costs, quotations and outcomes are fictional; stage/conversion analytics are demo workflow ratios | Marketing effectiveness with real treatment/control outcomes, uncertainty and an explicit counterfactual rather than CRM records |
| [Foreign Trade Enterprise RAG](https://github.com/hql7-luo/foreign-trade-enterprise-rag) | `1593b56f5e2fa4ef10892b945fed8c2ea5e40ed8` | Distinguish current approved facts from proposed/historical knowledge; retrieve with claim-level evidence | Synthetic Northstar corpus; developer-authored frozen benchmark; offline hashing results are not neural/production accuracy | Statistical inference and economic decision quality rather than retrieval, approvals, roles or knowledge governance |
| [Foreign Customer Investigation Skill](https://github.com/hql7-luo/foreign-customer-investigation-skill) | `2e51aeb0483b283d676c4a052d3002a402ae8e21` | Evidence-based B2B customer due diligence, product-fit scoring and development priority with consistent documents | Fictional public examples; auditable rule scores/grade caps; no fabricated company revenue or purchase potential | Experimentally estimated customer response, held-out policy evaluation and scenario assumptions rather than rules-based lead grades |

## Actual files inspected

- Supply Chain: full current README, `docs/methodology.md`, `pyproject.toml`, `.github/workflows/ci.yml`, SQL inventory and the implementation module/function inventory. Full fresh clone saved under `work/existing-supply-chain/`.
- B2B: full current README/file tree and `services/workflow.py`. SQLite inheritance of linked quotation fields confirms that the core is transactional workflow orchestration. The new repository should not recreate this app.
- RAG: full current README/file tree and `docs/architecture.md`. SQLite is fact authority, Qdrant a rebuildable index, with reviewer approval and claim-level synthesis. Keep these existing benchmark qualifications unchanged.
- Customer Investigation: full current README/file tree and the scoring/report model inventory in `.agents/skills/foreign-customer-investigation/scripts/models.py`. It validates input/evidence states, score subtotals, grade safeguards and deterministic ranking. The public examples remain labeled fictional.
- Public snapshots used for audit are saved under `work/audit-snapshots/`; these are temporary audit inputs and should not be published as new-project source assets.

## Quality bar for the new project

The current real-data Supply Chain project is the strongest analytical comparator: it includes source/license provenance, fixed data scope, visible SQL, separated assumptions, immutable validation/holdout boundaries, retained negative model findings, generated/reconciled visuals, executive summary and Python 3.11/3.12 CI. B2B, RAG and the customer skill add substantial workflow/evidence engineering, but their fictional demos are not marketing causal evidence.

The new project should match the analytical comparator's reproducibility and evidence boundaries, with stronger experimental inference where the dataset supports it. Required before portfolio synchronization: source and redistribution review; full row/field audit; reproducible SQL/Python statistics; primary estimands and multiplicity adjustment; no outcome leakage; locked exploratory/holdout distinction; honest spend/profit assumptions; meaningful tests; 4–6 generated decision charts; executive memo; and clean CI. Do not invent realized growth, individual uplift certainty, true ROI or current-market relevance.

## Portfolio integration discovery

Live GitHub Pages settings were verified: `hql7-luo.github.io`, public, HTTPS enforced, legacy Pages build from `main` at repository root (`/`). Fresh clone target: `work/portfolio/`. The old clone README confirms a vanilla HTML/CSS/JS static site, embedded per-page English/Chinese translation JSON, no package manager/backend/build step, and prohibited use of the ignored historical `portfolio-v2-demo` generator. Current integration files and exact baseline will be recorded after the fresh clone finishes.

Fresh clone completed at current main `2847c5f488f452ad615809a5f0f5e1e451c77555`, with a clean worktree. Current README and live Pages settings agree. There is no `AGENTS.md` in this repository. Current site contains the five featured projects and five secondary builds, including the new Supply Chain case and Customer Investigation case missing from the older clone.

Exact intended integration files:

- `index.html`: one additional `research-row` in `featured-analytics`, its `meg.*` English/Chinese translation keys, and the featured project count (`work.subtitle`) only.
- `projects/marketing-experimentation-growth-strategy.html`: one independent bilingual decision case with verified findings, generated evidence charts, methodology, recommendations and historical/financial/data-rights limitations; share the existing shell/navigation/footer and image dialog.
- `assets/projects/marketing-experimentation-growth-strategy/`: only generated chart copies plus a `SOURCES.md` and hash manifest to preserve provenance.
- `README.md`: add the project to the featured inventory, new case/asset provenance and validation scope; preserve all personal/project facts.
- `scripts/check-marketing-experiment.mjs` and `.github/workflows/portfolio-checks.yml`: publishable metric/chart/hash checks if the verified new project provides a suitable generated evidence manifest. Existing all-page validator automatically discovers the new HTML case.
- No changes planned to existing project pages, `app.js`, `style.css`, demos, personal facts, academic claims or Resume PDFs. Reuse the tested Supply Chain case layout classes without changing the original case.

Baseline Resume hashes: English `751e052ee076932a3aae8bc0fda048b433b85bd306e0b6a7d46fd5e7acac6a6d`; Chinese `06fc952e2adbbcd9b6312c9508095939fc86b49d49a4bda7cbc60ed70a863dd4`.

Existing local checks: `node --check app.js`; `node --check demos/supply-chain/demo.js`; `node scripts/check-supply-chain.mjs`; `node scripts/check-portfolio-pages.mjs`. Existing GitHub Actions `portfolio-checks.yml` runs these on main pushes/PRs with Node 22. Browser QA should check the new case and homepage in English/Chinese at desktop/mobile, navigation, image expansion, no missing assets/overflow/page errors, and Resume language links without changing the Resume content.

Only new-project entry/case study/assets and directly corresponding README project inventory should change. Preserve existing project descriptions, personal facts, academic/team metrics, dates and both Resume PDFs byte-for-byte. Wait for verified findings and project URL from the main project before writing publishable claims.
