# Industry and Regulatory Practice: Risk Horizons, ES vs VaR, and Dependence Modeling

## What horizons does FRTB/Basel use for market risk capital (and liquidity horizons)?

### Takeaway
FRTB replaces Basel 2.5’s uniform **10-day VaR** with **97.5% Expected Shortfall** on a **10-day base holding period**, then layers **five regulatory liquidity horizons (10, 20, 40, 60, 120 days)** by risk-factor category; capital also uses **stressed 12-month calibration** (history from 2007) and, for IMA, a **50/50 blend** of unconstrained vs risk-class-constrained ES. As of 2024–2026, **binding FRTB capital is live in some jurisdictions but delayed to 2027–2028 in the EU/UK** while the US remains unsettled.

### Cited Findings

**Basel 2.5 (pre-FRTB) — single 10-day horizon**

- Basel 2.5 improved pre-crisis market risk capital by adding **stressed VaR** alongside regular VaR; the framework **assumed banks could exit or hedge trading-book exposures over 10 days** without moving prices, a assumption FRTB later rejected as crisis-inadequate. — [BIS Explanatory Note (Jan 2019)](https://www.bis.org/bcbs/publ/d457.htm) (see §2.3(b) in [PDF mirror](https://www.dirittobancario.it/wp-content/uploads/sites/default/files/allegati/explanatory_note.pdf))

**FRTB IMA — ES confidence, base horizon, liquidity buckets**

- IMA ES must use a **97.5th percentile, one-tailed** confidence level, computed **daily** at bank and desk level. — [BIS MAR33 (in force)](https://www.bis.org/committees/bcbs/basel-framework/standard/mar/33/inforce/2023-01-01/published/2020-03-27)
- Liquidity horizons are reflected by scaling ES from a **base liquidity horizon T = 10 days**; bucket lengths **LH_j ∈ {10, 20, 40, 60, 120} days** (Table 1). ES at T is computed on **actual 10-day risk-factor changes** (overlapping allowed), **not** by √t scaling from 1-day ES. — [BIS MAR33.3–33.4](https://www.bis.org/committees/bcbs/basel-framework/standard/mar/33/inforce/2023-01-01/published/2020-03-27); [MAR33 PDF chapter](https://www.bis.org/committees/bcbs/basel-framework/81327/chapter.pdf)
- **Liquidity horizon** is defined as time to exit/hedge **without materially affecting prices under stress**; ES is intended to capture loss over that horizon in a stress period, raising capital for illiquid factors. — [BIS Explanatory Note](https://www.dirittobancario.it/wp-content/uploads/sites/default/files/allegati/explanatory_note.pdf)

**Example risk-factor → liquidity horizon mappings (Table 2, MAR33.12)**

- **Interest rate (specified currencies: EUR, USD, GBP, AUD, JPY, SEK, CAD, domestic): 10 days**; unspecified currencies **20 days**; IR **volatility 60 days**. — [BIS MAR33](https://www.bis.org/committees/bcbs/basel-framework/standard/mar/33/inforce/2023-01-01/published/2020-03-27)
- **Equity price large cap: 10 days**; small cap **20 days**; equity price **volatility 60 days**; large-cap repo/dividend **20 days** (other equity repo/dividend **60 days**). — [BIS MAR33 FAQs](https://www.bis.org/committees/bcbs/basel-framework/standard/mar/33/inforce/2023-01-01/published/2020-03-27)
- **FX pairs (most liquid list): 10 days**; other FX **20 days**; FX volatility **60 days**.
- **IG sovereign/corporate credit spreads: 20–40 days** (by sub-category); **HY corporate spreads: 60 days**; CSR volatility **60–120 days** depending on bucket.
- **Commodity price: 20 days** (typical); **other/illiquid commodity types: 120 days**.
- Desks may **raise** n to 20/40/60/120 with documentation and supervisory approval (floor, not ceiling); horizon **capped at instrument maturity** (with “next longer” bucket if maturity is shorter than assigned LH). — [BIS MAR33.12](https://www.bis.org/committees/bcbs/basel-framework/standard/mar/33/inforce/2023-01-01/published/2020-03-27); [EU RTS mapping logic](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX%3A32022R2058)

**Stressed vs current observation windows (IMA)**

- Regulatory ES combines: **ES_R,S** on the **worst 12-month stress window** (must include **2007**, updated ≥ quarterly); scaled by **max(ES_F,C / ES_R,C, 1)** where **ES_F,C** and **ES_R,C** use the **current 12-month** window (full vs reduced factor set). — [BIS MAR33.6–33.8](https://www.bis.org/committees/bcbs/basel-framework/standard/mar/33/inforce/2023-01-01/published/2020-03-27)
- Stressed calibration is a **joint assessment across risk factors** (captures **stressed correlations**). Reduced factor set must explain ≥ **75%** of full ES variation (12-week average ratio). — [BIS MAR33.5](https://www.bis.org/committees/bcbs/basel-framework/standard/mar/33/inforce/2023-01-01/published/2020-03-27)
- **IMCC** = **ρ·ES_unconstrained + (1−ρ)·Σ ES_constrained_by_risk_class** with **ρ = 0.5** (limits cross-asset diversification). — [BIS MAR33.14–33.15](https://www.bis.org/committees/bcbs/basel-framework/standard/mar/33/inforce/2023-01-01/published/2020-03-27)

**Liquidity-horizon scaling mechanics (implementation detail)**

- FRTB requires **multiple ES runs**: full **E_ST(P)** plus partial **E_ST(P,j)** where only risk factors in subset **Q(p_i,j)** (factors with LH ≥ bucket j) move; results are **time-scaled and aggregated** across the five LH slices (industry guides describe this under a **√(LH/T)**-style aggregation when losses are treated as independent across slices). — [Nagler FRTB LH note](https://www.nagler-company.com/fileadmin/user_upload/News/NC_FRTB_LiquidityHorizons.pdf); [BIS MAR33.4–33.5](https://www.bis.org/committees/bcbs/basel-framework/81327/chapter.pdf)
- EBA/industry comments: **LH assigned to a desk can differ across legs of a hedge** (e.g. equity 20d vs futures capped at 10d near expiry), creating **“broken hedge” partial ES** and operational burden. — [EBA response on LH RTS](https://www.eba.europa.eu/eba-response/7181)

**FRTB Standardised Approach (SA) — implicit horizon via shocks, not ES**

- SA capital = **sensitivities-based method + default risk capital + residual risk add-on**; delta/vega use **regulatory risk weights** and **fixed correlation matrices (ρ within bucket, γ across buckets)**, computed under **high / medium / low correlation scenarios** (high: ρ, γ multiplied by **1.25**, capped at 100%). — [BIS MAR21](https://www.bis.org/committees/bcbs/basel-framework/standard/mar/21/inforce/2022-01-01/published/2019-12-15); [MAR standard overview](https://www.bis.org/committees/bcbs/basel-framework/MAR/standard.pdf)
- SA is **stress-calibrated** (conceptually similar to a stress test on sensitivities), not a single explicit 10-day VaR/ES number. — [BIS Explanatory Note §3.3](https://www.dirittobancario.it/wp-content/uploads/sites/default/files/allegati/explanatory_note.pdf)

**Non-modellable risk factors (NMRF)**

- NMRF stress scenarios use **97.5%-equivalent prudence**, **common 12-month stress period per risk class**, and LH = **max(regulatory LH, 20 days)**. — [BIS MAR33.16](https://www.bis.org/committees/bcbs/basel-framework/standard/mar/33/inforce/2023-01-01/published/2020-03-27); [EBA universal NMRF stress paper](https://www.eba.europa.eu/sites/default/files/document_library/1017256/A%20universal%20stress%20scenario%20approach%20to%20capitalise%20NMRF.pdf)

**Implementation status (2024–2026)**

- BIS framework **effective date** for the revised market risk standard: **1 January 2022** at the global rule level; **national binding capital** dates vary. — [BIS d457 landing page](https://www.bis.org/bcbs/publ/d457.htm)
- **EU**: FRTB **capital requirements postponed to 1 January 2027** (second one-year delay from 2026), citing **level playing field** vs US/UK delays; most other Basel III elements applied **1 Jan 2025**. — [European Commission Q&A (2025)](https://finance.ec.europa.eu/publications/questions-and-answers-postponing-market-risk-requirements-preserve-international-level-playing-field_en); [Commission press release PDF](https://ec.europa.eu/commission/presscorner/api/files/document/print/en/ip_25_1478/IP_25_1478_EN.pdf)
- **UK PRA**: proposed **IMA delay to 1 Jan 2028**; other FRTB elements targeted **2027**. — [Moody’s regulatory summary (2025)](https://www.moodys.com/web/en/us/insights/regulatory-news/global-regulators-adjust-to-shifting-dynamics-in-frtb-rollout.html)
- **US**: FRTB/endgame **not finalized** as of Commission assessment (**earliest ~2027**). — [EU delegated act draft assessment](https://finance.ec.europa.eu/document/download/34725892-ac6a-47a2-88bc-15c4008cf050_en?filename=crr-delegated-act-2025_en.pdf)
- **APAC**: uneven rollout (e.g. Japan/HK/SG timelines 2024–2025; Australia ~2026). — [Numerix jurisdictional summary (2024–2025)](https://www.numerix.com/resources/blog/exploring-frtbs-fragmented-implementation-across-jurisdictions)

### Inferences

- Regulators moved from **one 10-day horizon for everything** to **horizon heterogeneity by asset liquidity**, but still within a **small discrete set of horizons** and a **single 10-day ES engine**—not continuous multi-scale dependence models.
- **Horizon and dependence interact in FRTB** via (i) **which factors are shocked together** in each LH slice, (ii) **stressed-period joint calibration**, and (iii) **50% constraint** on cross-class diversification—partially addressing crisis correlation breakdown without estimating scale-dependent copulas.

### Gaps

- Exact closed-form **LH aggregation formula** in MAR33 is often rendered as images in PDFs; industry white papers paraphrase it—verify against supervisor FAQ/implementations before coding.
- **US final rule timing** remains uncertain; treat US-specific capital numbers as **scenario-dependent** for competition memos.

---

## Why is ES preferred to VaR in recent regulation?

### Takeaway
Post-crisis reform favors **97.5% ES under stress** because it measures **average tail loss** (not just a cutoff), is **subadditive/coherent**, reduces **tail-risk gaming**, and pairs naturally with **liquidity horizons**—while acknowledging ES is **harder to estimate and backtest** than VaR.

### Cited Findings

**Official FRTB rationale**

- VaR at a fixed quantile **ignores loss severity beyond the threshold**, creating incentives to hold **tail risk** that looks fine in “normal” periods; ES averages **worst (1−α)% losses**. — [BIS Explanatory Note §3.2(ii)](https://www.dirittobancario.it/wp-content/uploads/sites/default/files/allegati/explanatory_note.pdf)
- FRTB **replaces VaR and stressed VaR** with **one ES metric** calibrated to **stress**, incorporating **illiquidity** via LH. — [BIS d352 overview](https://www.bis.org/bcbs/publ/d352.htm)
- **97.5% ES ≈ 99% VaR** under “normal” conditions but **ES exceeds VaR more under fat tails**; framework explicitly notes this equivalence guide. — [BIS Explanatory Note footnote 8](https://www.dirittobancario.it/wp-content/uploads/sites/default/files/allegati/explanatory_note.pdf)

**Coherence / tail risk (academic & regulatory consensus)**

- Basel Committee (2013 reform path) cited VaR weaknesses: **inability to capture tail risk**, **non-subadditivity**; **Artzner et al. ES (CVaR)** considers losses beyond VaR and is **subadditive**. — [Basel working paper cited via McNeil et al. survey in](https://repub.eur.nl/pub/79539/EI2015-38.pdf); [ScienceDirect ES vs VaR stochastic dominance](https://www.sciencedirect.com/science/article/abs/pii/S1059056018301072)
- **Stochastic dominance** analysis suggests **97.5% ES** can yield **preferable capital charge distributions** vs **99% VaR** for risk-averse policymakers (tail-aware, stability arguments). — [ScienceDirect (2018)](https://www.sciencedirect.com/science/article/abs/pii/S1059056018301072)

**Practical / industry pushback (important nuance for competitions)**

- **ES needs more tail data** than VaR for stable estimates; with ~250 days, **99% ES** uses only ~**2–3 tail points** (GARP-style teaching materials). — [PastPaperHero FRM ES notes](https://www.pastpaperhero.com/resources/garp-frm-part2-advanced-var-and-es-expected-shortfall-properties-and-estimation)
- **Danielsson et al. (VoxEU)**: in practice, **VaR can be more statistically precise** than ES; with **one year of data**, **99% VaR can exceed 97.5% ES**, so the regulatory shift may **lower and destabilize** forecasts—**coherence ≠ easy estimation**. — [CEPR VoxEU](http://cepr.org/index%2Ephp/voxeu/columns/why-risk-hard-measure)
- Industry association critique: FRTB ES design (NMRF, PLA, overlapping constraints) can **inflate capital** and **reduce diversification incentives** beyond tail-measure theory. — [BPI (2023)](https://bpi.com/wp-content/uploads/2023/05/Why-is-the-FRTB-Expected-Shortfall-Calculation-Designed-as-it-is.pdf)

**Basel 2.5 → FRTB shift in computation**

- Basel 2.5: **10-day VaR + 10-day stressed VaR** (often from **250-day windows**, with √10 scaling from 1-day in some implementations). FRTB: **direct 10-day ES** on overlapping returns for the base horizon. — [BPI illustrative note](https://bpi.com/wp-content/uploads/2023/05/Why-is-the-FRTB-Expected-Shortfall-Calculation-Designed-as-it-is.pdf)

### Inferences

- Regulators chose ES primarily for **incentive compatibility** (tail severity) and **aggregation logic**, not because ES is always **easier** or **more stable** to estimate.
- A competition-ready narrative should pair **“ES for tail severity”** with **“VaR still common internally / ES needs long history + stressed windows.”**

### Gaps

- **Official ES backtesting** standards under FRTB IMA remain **less prescriptive** than VaR backtesting in Basel II; EU firms report **limited methodology guidance** for ES backtesting. — [Numerix IMA commentary](https://www.numerix.com/resources/blog/exploring-frtbs-fragmented-implementation-across-jurisdictions)

---

## How do practitioners usually handle multi-asset dependence today?

### Takeaway
Banks and asset managers still rely overwhelmingly on **(i) historical simulation with joint scenario resampling**, **(ii) variance–covariance / factor models with estimated correlation matrices**, and **(iii) Gaussian or Student-t copulas**—typically on **one chosen horizon** (often 1-day or 10-day)—with **stress overlays** and **regulatory correlation floors**; **wavelet-scale copulas** remain research-grade, not core production stacks.

### Cited Findings

**Regulatory-aligned bank practice (FRTB IMA)**

- Supervisors permit ES models based on **historical simulation, Monte Carlo, or analytical methods** if PLA/backtesting pass. — [BIS MAR33.9](https://www.bis.org/committees/bcbs/basel-framework/standard/mar/33/inforce/2023-01-01/published/2020-03-27)
- Banks may use **empirical correlations within broad risk classes**, but **cross-class correlations are constrained** by the **50/50 IMCC** scheme; correlations must be **consistent with liquidity horizons** and **explainable to supervisors**. — [BIS MAR33.10](https://www.bis.org/committees/bcbs/basel-framework/standard/mar/33/inforce/2023-01-01/published/2020-03-27)
- **Stressed ES** explicitly aims to embed **stressed correlation measures** via joint 12-month stress selection. — [BIS MAR33.5](https://www.bis.org/committees/bcbs/basel-framework/standard/mar/33/inforce/2023-01-01/published/2020-03-27)

**Historical simulation (most common “dependence = data” approach)**

- HS **re-applies historical joint shocks** to current positions; **cross-sectional dependence is preserved** by resampling **full vectors** of risk-factor moves—avoiding explicit high-dimensional correlation maintenance. — [Filtered HS paper (2026)](https://filteredhistoricalsimulation.com/downloads/GBA_FHS_Feb%202026_ssrn-6120707.pdf)
- **Filtered HS (EWMA/GARCH + residual bootstrap)** addresses **volatility clustering** while keeping **empirical co-movements** in standardized residuals. — [Filtered HS (2026)](https://filteredhistoricalsimulation.com/downloads/GBA_FHS_Feb%202026_ssrn-6120707.pdf)
- **EBA 2016 benchmarking**: banks using HS showed **homogeneous P&L correlation clusters** (similar methods → similar outcomes), indicating **method choice dominates** subtle dependence modeling for many portfolios. — [EBA MR benchmarking report](https://www.eba.europa.eu/sites/default/files/documents/10180/15947/5c829f1b-b23a-477e-ad48-972b50a7de10/EBA%20Report%20results%20from%20the%202016%20market%20risk%20benchmarking%20%20-%20March%202017.pdf)

**Parametric / copula practice**

- **Variance–covariance** and **Gaussian copula** remain widespread for **speed and explainability**; **Student-t copula** preferred when tail dependence matters (adds **ν** tail parameter while keeping a **correlation matrix**). — [CEPR “Selecting Copulas for Risk Management”](http://cepr.org/index%2Ephp/publications/dp5652); [FH Wien real-world portfolio study](https://www.fh-vie.ac.at/uploads/WP-068_2012.pdf)
- Gaussian copula can **understate joint extreme down moves** and **overstate diversification** vs t-copula in multi-asset portfolios. — [CEPR DP5652](http://cepr.org/index%2Ephp/publications/dp5652); [Wuppertal copula VaR guide](https://acm.uni-wuppertal.de/fileadmin/mathe/www-num/preprints/amna_09_02.pdf)
- High-dimensional copula calibration (**vine/hierarchical**) is **possible but costly**; performance is **structure-dependent** and may **overfit**. — [CSAM copula VaR study](http://www.csam.or.kr/journal/view.html?doi=10.29220%2FCSAM.2021.28.1.059)
- **Time-varying copulas** (e.g. SJC) improve **crisis dependence** vs static Gaussian for mixed-asset VaR. — [Physica A mixed-asset TV copula paper](https://www.sciencedirect.com/science/article/abs/pii/S0378437115009474)

**Standardised-approach dependence (fallback / floor)**

- Banks using SA inherit **regulatory ρ and γ** plus **three correlation scenarios**—dependence is **prescriptive**, not estimated. — [BIS MAR21.6–21.7](https://www.bis.org/committees/bcbs/basel-framework/standard/mar/21/inforce/2022-01-01/published/2019-12-15)

**GARP / risk-manager skill set (industry education baseline)**

- GARP FRM curriculum centers **VaR & ES**, **historical & parametric** methods, **liquidity horizons**, **stress/scenario analysis**, and **backtesting**—not wavelet methods. — [GARP survey syllabus excerpt](https://bleu-azur-consulting.eu/wp-content/uploads/2019/06/click-here-to-access-garps-detailed-survey-report.pdf); [LearnSignal FRM summary](https://www.learnsignal.com/blog/topics-covered-in-market-risk-measurement-and-management/)

**Why single-horizon dependence persists (despite multi-scale academic results)**

- **Regulatory auditability**: FRTB requires **documented, supervisor-explainable** correlation use tied to **discrete LH buckets**, not scale-varying copula families. — [BIS MAR33.10](https://www.bis.org/committees/bcbs/basel-framework/standard/mar/33/inforce/2023-01-01/published/2020-03-27)
- **Validation burden**: desk-level **PLA and backtesting** favor **stable, low-parameter** dependence (HS resampling, single correlation matrix) over **multi-scale models** with many free parameters. — [BIS Explanatory Note §3.2(i)](https://www.dirittobancario.it/wp-content/uploads/sites/default/files/allegati/explanatory_note.pdf)
- **Data limits at the tail**: ES already stresses **scarce tail samples**; estimating **separate tail copulas per horizon** multiplies data demand. — [PastPaperHero ES estimation](https://www.pastpaperhero.com/resources/garp-frm-part2-advanced-var-and-es-expected-shortfall-properties-and-estimation); [CEPR VoxEU](http://cepr.org/index%2Ephp/voxeu/columns/why-risk-hard-measure)
- **Legacy infrastructure**: risk engines, limits, and **10-day market-risk convention** (Basel II lineage) are deeply embedded; FRTB **extends horizons via LH scaling**, not continuous wavelet bands. — [REF Press FRTB overview](https://refpress.org/wp-content/uploads/2023/12/Vuuren_REF.pdf)

### Inferences

- **Dependence modeling in industry ≈ joint shocks + linear correlations + stress**, with **copulas** used mainly where **non-Gaussian tails** are material and dimensionality is manageable.
- **Multi-horizon risk** in regulation is handled by **liquidity buckets and partial ES**, not by estimating **ρ(h)** or **λ_U(h)** at each scale.

### Gaps

- **No recent public survey (2024–2026)** quantifying % of banks on HS vs MC vs copula for **FRTB ES** specifically; inference relies on **pre-FRTB benchmarking** and vendor/regulatory commentaries.
- **Asset managers** (vs banks) often use **1-day VaR/ES** for fund risk; less harmonized public documentation than Basel/FRTB.

---

## Gap between academic wavelet-copula results and industry implementation — barriers?

### Takeaway
Academic **wavelet–copula** work consistently finds **time-scale-dependent tail dependence** (short-run contagion vs long-run interdependence), but industry stays with **single-horizon ES/VaR + stressed correlations** because of **validation, governance, data, and regulatory compatibility**—not because practitioners deny scale effects.

### Cited Findings

**What wavelet-copula literature shows**

- **Tail dependence and average dependence vary by investment horizon** (short/medium/long scales); copula parameters differ across scales for commodity vol indexes. — [Energy Economics (2017)](https://www.sciencedirect.com/science/article/abs/pii/S0140988317302013)
- **Contagion vs interdependence** can be separated by scale: post-Lehman **higher correlation and tail dependence** appear at **multiple scales**, not only high-frequency. — [Physica A wavelet contagion (2015)](https://www.sciencedirect.com/science/article/abs/pii/S0378437115004689)
- **Oil–equity**: dependence **weak at fine scales pre-crisis**, **strengthens at longer scales**; post-crisis **dependence rises at all scales**; diversification benefits **scale-dependent**. — [Energy Economics (2016)](https://ideas.repec.org/a/eee/energy/v107y2016icp866-888.html)
- Wavelet-copula models can **improve VaR/CVaR accuracy** vs traditional approaches in agricultural/commodity settings (academic claim). — [RePEc DP 0413](https://ideas.repec.org/p/dpc/wpaper/0413.html)

**What regulation/industry already does (partial overlap)**

- FRTB **acknowledges horizon heterogeneity** via **five LH bands** and **partial ES**—a **discrete, auditable** cousin of multi-scale thinking. — [BIS MAR33](https://www.bis.org/committees/bcbs/basel-framework/standard/mar/33/inforce/2023-01-01/published/2020-03-27)
- **Stressed 12-month window** + **high-correlation SA scenario** embed **crisis dependence** without estimating continuous **λ(h)**. — [BIS MAR33.5](https://www.bis.org/committees/bcbs/basel-framework/standard/mar/33/inforce/2023-01-01/published/2020-03-27); [BIS MAR21.6](https://www.bis.org/committees/bcbs/basel-framework/standard/mar/21/inforce/2022-01-01/published/2019-12-15)

**Barriers to adoption (evidence-based)**

| Barrier | Evidence |
|--------|----------|
| **Supervisory explainability & model approval** | IMA requires PLA/backtesting and **supervisor-explainable** correlation/LH choices; exotic dependence structures increase **model risk** and **approval risk**. — [BIS Explanatory Note §3.2](https://www.dirittobancario.it/wp-content/uploads/sites/default/files/allegati/explanatory_note.pdf) |
| **Operational cost / FRTB complexity** | FRTB IMA already requires **many ES variants** (LH slices, constrained/unconstrained, stress/current); few banks plan full IMA adoption in EU. — [Numerix (2024–2025)](https://www.numerix.com/resources/blog/exploring-frtbs-fragmented-implementation-across-jurisdictions) |
| **Tail data scarcity for ES** | ES estimation error **worse than VaR** in short samples; multi-scale tail copulas compound the problem. — [CEPR VoxEU](http://cepr.org/index%2Ephp/voxeu/columns/why-risk-hard-measure); [PastPaperHero](https://www.pastpaperhero.com/resources/garp-frm-part2-advanced-var-and-es-expected-shortfall-properties-and-estimation) |
| **Methodological risk in crisis** | Linear correlation **breaks down** in stress; HS preserves history but **may miss unprecedented joint tails**; wavelet-copula adds **specification risk** (wavelet filter, copula family, band count). — [Physica A (2015)](https://www.sciencedirect.com/science/article/abs/pii/S0378437115004689); [EBA benchmarking on method homogeneity](https://www.eba.europa.eu/sites/default/files/documents/10180/15947/5c829f1b-b23a-477e-ad48-972b50a7de10/EBA%20Report%20results%20from%20the%202016%20market%20risk%20benchmarking%20%20-%20March%202017.pdf) |
| **No regulatory recognition** | Neither Basel SA nor IMA text references **wavelet decomposition**; capital models must map to **MAR33/MAR21** constructs. — [BIS MAR framework](https://www.bis.org/committees/bcbs/basel-framework/MAR/standard.pdf) |

### Inferences

- The **gap is institutional**, not purely statistical: wavelet-copula answers **research questions** (how λ_U differs at 5-day vs 60-day scales) while FRTB answers **capital accounting** with **finite LH buckets** and **stress windows**.
- Wavelet-copula is best positioned as an **internal overlay** (risk appetite, limits, stress design)—not a replacement for **regulatory ES** without years of validation.

### Gaps

- Limited **peer-reviewed studies** calibrating wavelet-copula outputs to **FRTB partial ES** mechanics (Q(p_i,j) nesting)—would be a strong bridge paper for competitions.
- **Quantitative cost/benefit** of wavelet-copula in **trading-book P&L attribution** not found in official sources.

---

## What concrete recommendation would a risk manager find actionable tomorrow regarding horizon-aware tail dependence?

### Takeaway
Implement a **“regulatory core + horizon-aware overlay”**: keep **FRTB-aligned 10-day ES / HS** as the capital anchor, and add a **same-day diagnostic** that compares **tail dependence at 10d vs desk-relevant LH (20–120d)** using **stress-period HS slices** or a **Student-t copula on GARCH-filtered residuals**—then tie decisions to **partial ES drivers, SA high-ρ scenario, and desk LH floors**.

### Cited Findings (building blocks for the recommendation)

- **Step 1 — Map horizon to regulation**: Assign each desk’s risk factors to **MAR33.12 LH**; identify **longest LH bucket** affecting the desk (drives partial ES subsets). — [BIS MAR33.12](https://www.bis.org/committees/bcbs/basel-framework/standard/mar/33/inforce/2023-01-01/published/2020-03-27)
- **Step 2 — Stress dependence without new machinery**: Re-run **historical simulation** using only observations from the **current FRTB stressed 12-month window** (same window as ES_R,S) to produce **joint scenarios**; compute **ES_97.5** at **10-day** and at **√t-scaled or native overlapping h-day** returns for **h ∈ {10,20,40,60,120}** relevant to the desk. HS preserves **empirical cross-factor dependence** by construction. — [BIS MAR33.7](https://www.bis.org/committees/bcbs/basel-framework/standard/mar/33/inforce/2023-01-01/published/2020-03-27); [Filtered HS (2026)](https://filteredhistoricalsimulation.com/downloads/GBA_FHS_Feb%202026_ssrn-6120707.pdf)
- **Step 3 — Tail dependence check**: On **GARCH/EWMA-filtered residuals**, fit a **Student-t copula** (or compare Gaussian vs t) for **10-day aggregated residuals** vs **longer LH aggregated residuals**; flag if **lower-tail dependence** rises with horizon (pattern consistent with wavelet-copula crisis findings). — [CEPR DP5652](http://cepr.org/index%2Ephp/publications/dp5652); [Energy Economics (2016) scale-dependent tail dependence](https://ideas.repec.org/a/eee/energy/v107y2016icp866-888.html)
- **Step 4 — Link to capital & limits**: If tail dependence **rises with LH**, **do not rely on unconstrained IMCC diversification**; stress **SA high-correlation scenario (ρ,γ ×1.25)** as a **limit multiplier** on netted delta/vega buckets. — [BIS MAR21.6](https://www.bis.org/committees/bcbs/basel-framework/standard/mar/21/inforce/2022-01-01/published/2019-12-15); [BIS MAR33.15 ρ=0.5 constraint](https://www.bis.org/committees/bcbs/basel-framework/standard/mar/33/inforce/2023-01-01/published/2020-03-27)
- **Step 5 — Governance**: Document when **desk-level LH increases** (MAR33.12 floor) to avoid **broken-hedge partial ES** artifacts (e.g. near-expiry futures vs cash equity). — [EBA LH RTS comment](https://www.eba.europa.eu/eba-response/7181)

**One-page “tomorrow” workflow (competition-ready)**

1. **Inventory** modellable factors → **LH bucket** (10/20/40/60/120).
2. **Extract** stressed 12m window (must include 2007 logic for IMA-style stress; for internal use, at minimum last crisis window + last 12m).
3. **Compute** desk **ES_97.5** at 10d with full joint HS; repeat for **longest desk LH** using overlapping returns.
4. **Report** `ES_long / ES_10d` and **Δ tail dependence** (t-copula ν̂, lower-tail λ_L) — if ratio **> 1.25** (rule-of-thumb aligned with SA correlation uplift), **tighten limits** or **require hedges at longest LH**.
5. **Escalate** to **partial ES decomposition** (which Q(p_i,j) drives capital) before adding exotic wavelet models.

### Inferences

- This path is **actionable** because it uses **tools banks already defend to supervisors** (HS, stressed windows, t-copula sanity checks) while incorporating the **core scientific insight** of wavelet-copula papers: **dependence is horizon-dependent**, especially in the **lower tail**.
- Full **wavelet-copula production** is a **Phase 2** research project (model risk approval, PLA stability)—not a next-day regulatory capital change.

### Gaps

- No industry-standard threshold for **ES_long/ES_10d** or **Δλ_L**—competition memos should present thresholds as **internal policy** calibrated to stress scenarios, not Basel minima.
- **Danielsson/VoxEU** caution: prefer **native h-day overlapping ES** over blind √h scaling when reporting internal horizon comparisons. — [CEPR VoxEU](http://cepr.org/index%2Ephp/voxeu/columns/why-risk-hard-measure)

---

## Quick reference table (competition crib sheet)

| Topic | Basel 2.5 | FRTB (IMA core) |
|-------|-----------|-----------------|
| Primary metric | 99% VaR + 99% stressed VaR | 97.5% ES (stress-calibrated) |
| Default holding period | 10 days (uniform) | **10-day base** + **LH scaling** (10–120d) |
| Dependence | Historical corr / VaR aggregation | Empirical corr **within class** + **stressed joint period** + **50% cross-class cap** |
| SA fallback | Old sensitivity rules | **Risk weights + ρ/γ** with **3 correlation scenarios** |
| Live capital (EU/US snapshot 2025–26) | Legacy | **EU → Jan 2027**; **US uncertain**; **UK IMA → 2028** |

**Primary official URLs**

- BIS FRTB standard hub: https://www.bis.org/bcbs/publ/d457.htm  
- MAR33 (IMA ES & LH): https://www.bis.org/committees/bcbs/basel-framework/standard/mar/33/inforce/2023-01-01/published/2020-03-27  
- MAR21 (SA correlations): https://www.bis.org/committees/bcbs/basel-framework/standard/mar/21/inforce/2022-01-01/published/2019-12-15  
- Explanatory note (ES vs VaR narrative): https://www.dirittobancario.it/wp-content/uploads/sites/default/files/allegati/explanatory_note.pdf  
