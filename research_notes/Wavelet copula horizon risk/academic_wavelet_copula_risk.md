# Wavelet–Copula Methods for Market / Portfolio Risk (Literature Notes)

Scope: peer-reviewed and working papers (≈2010–2026) combining wavelets with copulas for dependence, VaR/ES, and portfolio risk—not pure signal processing. Seminal pre-2010 wavelet finance (Gençay et al.; Mallat) is cited only where papers anchor scale interpretation or MODWT rationale.

---

## Which wavelet transforms are standard for daily financial returns (MODWT vs DWT vs Haar à trous)?

### Takeaway
For **daily return dependence and risk**, **MODWT (maximal overlap discrete wavelet transform)** is the dominant choice because it is **shift-invariant**, preserves variance, and avoids the dyadic sample-length restriction of decimated DWT; **Haar à trous (HTW / redundant Haar)** appears where **boundary effects** and **exact time alignment** of detail coefficients matter (oil–stock, Greece–Europe); **DWT** is still defined in methodology sections but often replaced by MODWT in implementation. **Continuous wavelet (CWT/Morlet)** is auxiliary (event detection, denoising), rarely the core of copula fitting on standardized residuals.

### Cited Findings
- Cai et al. (2020, *Energies*): explicitly choose **MODWT over DWT** for oil–East Asian stock dependence because MODWT is defined for any sample size, is shift-invariant, and MODWT coefficient variance matches the original series variance (Percival & Walden rationale). — [MDPI Energies 13(2) 294](https://www.mdpi.com/2071-1050/13/2/294)
- Shahzad et al. (2016, *Physica A*): state that **MODWT is the most widely used DWT variant** in financial multiresolution work, but implement **Haar à trous wavelet (HTW, Murtagh et al.)** for VMD/wavelet copula on European equities because HTW avoids MODWT boundary bias and keeps detail/smooth length equal to the original series. — [Physica A 457, 8–33](https://doi.org/10.1016/j.physa.2016.03.048)
- Jammazi & Reboredo (2016, *Energy*): decompose oil and stock returns with **Haar à trous** before static and time-varying copulas for scale-specific tail dependence and diversification. — [Energy 107, 866–888](https://ideas.repec.org/a/eee/energy/v107y2016icp866-888.html)
- Jammazi (2012, *Energy*): **HTW** selected over traditional DWT to handle boundary conditions when linking crude oil shocks to developed-market stock returns (redundant, translation-invariant filtering). — [Energy 47](https://www.sciencedirect.com/science/article/abs/pii/S0360544212003969)
- Berger (2015, *Physica A*): uses **discrete wavelet decomposition** (non-decimated / Percival–Walden framework) on **29 DJIA stocks**, then **Archimedean and elliptical copulas** per scale for tail dependence and portfolio implications. — [Physica A 436, 338–350](https://doi.org/10.1016/j.physa.2015.05.053)
- Carvalho et al. (2021, *SN Business & Economics*): **MODWT + Daubechies (db2)** on **15-minute** Brazilian equities; **D-vine + BB7** on standardized ARIMA-APARCH residuals at scales mapped to 15 min–1 week. — [PMC8150631](https://pmc.ncbi.nlm.nih.gov/articles/PMC8150631/)
- Aloui & Jammazi (2015, *Physica A*): combine **CWT (Morlet)** for extreme-move detection with **two DWT variants** for denoising before **wavelet-copula**, wavelet-DCC-EGARCH, and wavelet-EVT on **monthly** oil–FX data. — [Physica A 436, 62–86](https://doi.org/10.1016/j.physa.2015.05.036)
- Gallegati (2012, *Computational Statistics & Data Analysis*): foundational **wavelet correlation** contagion test on **raw returns** (not copula); defines contagion vs interdependence by scale. — [CSDA 56(11), 3491–3497](https://ideas.repec.org/a/eee/csdana/v56y2012i11p3491-3497.html)
- Berger & Gençay (2019) and FGV BRE paper on VaR: compare **MODWT (Haar, Db2, Sym2)** vs **CWT** filters for frequency components affecting **FIGARCH-based VaR** on Ibovespa/DJIA stocks (8 decomposition levels). — [FGV BRE PDF](https://periodicos.fgv.br/bre/article/download/77437/78201/175571)

### Inferences
- **Equity multi-horizon dependence / copula**: MODWT + Daubechies or LA filters is the default; HTW is the main alternative when authors stress **no boundary trimming** and **coefficient alignment at time t**.
- **Intraday**: MODWT is standard; scale labels are tied to **sampling interval** (not calendar days).
- **Univariate VaR/ES by scale**: wavelet MRA on returns (Yang & Hamori 2020 uses **J = 8** MODWT-style details D1–D8) can be **copula-free**; multivariate tail work still tends to pair scales with copulas.

### Gaps
- Few papers run a **controlled horse race** MODWT vs HTW vs DWT on the **same** copula–VaR backtest for daily equities; choice is usually justified by boundary/shift-invariance arguments, not out-of-sample VaR deltas between transforms.

---

## Typical number of scales and mapping to investment horizons (days / weeks / months)?

### Takeaway
With **daily** data, **J = 6** or **J = 8** MODWT levels is typical. Detail **D_j** is interpreted as fluctuations over **≈ 2^j days** (band-pass), with common narrative bands **2–4 d (D1), 4–8 d (D2), 8–16 d (D3), 16–32 d (D4), 32–64 d (D5), 64–128 d (D6)** when J = 6; **D7–D8** extend toward **quarterly-ish** low frequency. Authors map these to **short / medium / long** investment horizons rather than literal calendar weeks/months, except when they reconstruct **S_J** as “trend.”

### Cited Findings
- Cai et al. (2020): **J = 6** on daily standardized GJR-GARCH shocks → local variance horizons **2, 4, 8, 16, 32, 64 days** for details; smooth **S_6** for longest scale. — [MDPI Energies 13(2) 294](https://www.mdpi.com/2071-1050/13/2/294)
- European lead/lag / MODWT study (LA8 filter, **J₀ = 6**): scale τ₁ **2–4 days**, τ₂ **4–8**, τ₃ **8–16**, τ₄ **16–32**, τ₅ **32–64**, τ₆ **64–128**; notes most index volatility in τ₁ and τ₂. — [Interdependence European stock markets (wavelet lead/lag)](https://exa.ai/library/publication/cps0nk65snh)
- Yang & Hamori (2020, *Energies*): **J = 8** wavelet details **D1–D8** for WTI/Brent **VaR and ES** forecasting; rank best model **by detail scale** (short = D1–D2, mid/long = D4–D8 hybrid wins). — [Energies 13(14) 3700](https://ideas.repec.org/a/gam/jeners/v13y2020i14p3700-d386267.html)
- Mensi et al. (2017, *Energy Economics*): **MODWT J = 8** on implied vol indices (OVX, WIV, CIV); **D1–D8** for tail dependence across **short / medium / long** horizons. — [Energy Economics 66, 122–139](https://doi.org/10.1016/j.eneco.2017.06.007)
- WC-GARCH COVID paper: decomposes returns into scales labeled **D1, D2, …**; reports tail dependence rises on **D1–D2 (roughly 2–8 day dynamics)** during COVID vs pre-crisis. — [J. Risk Financial Manag. 14(7) 329](https://www.mdpi.com/1911-8074/14/7/329)
- Shanghai–Shenzhen tail spillover: **MODWT → three scales** (d1, d2, d3 + approximation a3), Clayton time-varying copula per scale. — [MODWT + Clayton spillover study](https://exa.ai/library/publication/z8tlyzpx20v)
- Carvalho et al. (2021): on **15-min** data, MODWT scales mapped to **15 min, 1 h, 1 day, 1 week** (horizon scales follow **sampling period × 2^j**, not calendar daily mapping). — [PMC8150631](https://pmc.ncbi.nlm.nih.gov/articles/PMC8150631/)
- Gallegati (2012): contagion effects **not uniform across scales**; Brazil/Japan show contagion at **all** scales in subprime episode. — [CSDA 56(11)](https://ideas.repec.org/a/eee/csdana/v56y2012i11p3491-3497.html)

### Inferences
- For **SAIFA-style multi-horizon equity tail dependence**: a **6-level MODWT on daily residuals** gives interpretable buckets from **~2 days to ~2 months** on details, plus smooth for **>64-day** comovement; **8 levels** are used when papers push to **~256-day** bands or want finer short-end split.
- **Week/month labels** in prose usually mean **D1–D2 ≈ “weekly” noise**, **D4–D5 ≈ “monthly–quarterly”**, not fixed calendar weeks.

### Gaps
- **J selection** is rarely formal (AIC on copula fit across J); more often **fixed J** for sample length (N/(2^J) rule-of-thumb). Entropy-based MODWT level choice appears in some *Physica A* entropy papers but not consistently in copula–VaR studies.

---

## Which copula families are selected for lower / upper tail dependence?

### Takeaway
**Lower tail**: **Clayton**, **rotated Gumbel**, **Joe–Clayton / symmetrized Joe–Clayton (SJC)**, sometimes **BB7** (asymmetric tails in vines). **Upper tail**: **rotated Clayton / Gumbel**, **Joe**, **SJC**, **BB7**. **Both tails / asymmetry**: **SJC**, **time-varying Joe–Clayton**, **Student t** (symmetric tails), **BB7** in vine frameworks. **Gaussian / normal copula** is a benchmark and often **rejected** when tail dependence matters. **Vine (C/D/R-vine)** extensions appear for **3+ assets** (oil, clean energy, stocks; intraday Brazilian book).

### Cited Findings
- Cai et al. (2020): candidate set **normal, Student t, rotated Gumbel, Clayton, SJC**; **SJC** wins on log-likelihood and GOF for oil–stock pairs at most scales; **time-varying SJC** preferred over constant copulas. — [MDPI Energies 13(2) 294](https://www.mdpi.com/2071-1050/13/2/294)
- Shahzad et al. (2016): compare multiple copulas on **HTW/VMD** decomposed residuals; select **time-varying Joe–Clayton** for tail dependence; emphasize **short-run lower tail** paths jumping in GFC. — [Physica A 457](https://doi.org/10.1016/j.physa.2016.03.048)
- Jammazi & Reboredo (2016): **wide range of static and time-varying copulas** on Haar à trous scales; document **asymmetric lower tail** pre-crisis and **both tails** post-15 Sep 2008 for oil–stock. — [Energy 107](https://ideas.repec.org/a/eee/energy/v107y2016icp866-888.html)
- Berger (2015): follows Boubaker & Sghaier (2013) in using **elliptical + Archimedean** copulas for **symmetric and asymmetric tail dependence** on each DJIA wavelet scale, pre/post-Lehman. — [Physica A 436](https://doi.org/10.1016/j.physa.2015.05.053)
- Shanghai–Shenzhen: **time-varying Clayton** per MODWT scale for **lower-tail** spillover strength. — [Clayton spillover paper](https://exa.ai/library/publication/z8tlyzpx20v)
- Carvalho et al. (2021): **BB7** in **D-vine** for **asymmetric upper/lower** tail dependence across intraday scales. — [PMC8150631](https://pmc.ncbi.nlm.nih.gov/articles/PMC8150631/)
- COVID WC-GARCH: **copula on wavelet-decomposed returns** with **GARCH-skew-t margins** (Jondeau–Rockinger style); tail dependence analyzed on **D1–D2** scales. — [JRFM 14(7) 329](https://www.mdpi.com/1911-8074/14/7/329)
- Khalfaoui et al. (2025, *Research in International Business and Finance*): **MODWT–vine-copula** for **extreme risk contagion** oil / clean energy / US stocks; asymmetric upside/downside contagion by scale. — [RePEc RIIBAF 75](https://ideas.repec.org/a/eee/riibaf/v75y2025ics0275531925000467.html)
- Boubaker & Sghaier (2013, *Journal of Banking & Finance*): **wavelets used to visualize copula density** and select copula for **long-memory** portfolios (CVaR optimization)—foundational link of wavelets to copula **specification**, not per-scale decomposition. — [JBF 37(2)](https://ideas.repec.org/a/eee/jbfina/v37y2013i2p361-377.html)

### Inferences
- **Lower-tail portfolio risk (equity drawdowns)**: Clayton / Joe–Clayton / SJC / BB7 dominate published choices; **Gaussian copula is inadequate** when papers focus on crisis comovement.
- **Upper-tail (momentum / joint rallies)**: BB7 and SJC explicitly separate τ_U vs τ_L; Brazilian intraday study finds **stronger upper-tail dependence in upturns** across scales.

### Gaps
- **t-copula** is common in **single-scale** MC-GARCH–copula VaR papers but less often the **winner** in **scale-by-scale** energy–equity studies (SJC/Clayton preferred). Head-to-head **SJC vs t-vine** for **equity portfolio ES** at each MODWT level is sparse.

---

## Do wavelet–copula models improve VaR/ES accuracy vs single-scale correlation or Gaussian copula?

### Takeaway
Evidence splits by **task**: (A) **Multivariate dependence / portfolio construction**—wavelet–copula mainly improves **economic risk metrics** (hedge ratios, variance/ES **reduction**, tail-aware diversification), not always formal Kupiec backtests vs Gaussian copula on the **same** horizon. (B) **VaR/ES forecasting**—**wavelet denoising or wavelet-scale univariate models** often **beat** DCC-GARCH/EWMA/Gaussian margins on **loss functions**; **wavelet + copula** jointly beating **single-scale Gaussian copula** is supported qualitatively and via **ES level differences**, with **some numeric magnitudes** below. Direct “wavelet-copula vs Gaussian copula VaR” backtests on **daily equity portfolios** remain limited in the papers reviewed.

### Cited Findings
- Aloui & Jammazi (2015): on **monthly** oil–FX portfolios, models using **wavelet-denoised** series **outperform** models on raw series for **VaR and ES accuracy**; wavelet-copula among three wavelet hybrids (with wavelet-DCC-EGARCH, wavelet-EVT). — [Physica A 436](https://doi.org/10.1016/j.physa.2015.05.036)
- Khalfaoui & Boutahar (2012, *Energies*): **multivariate wavelet-denoising PVaR** **outperforms EWMA and DCC-GARCH** on conventional reliability criteria for crude oil portfolios. — [Energies 5(4)](https://ideas.repec.org/a/gam/jeners/v5y2012i4p1018-1043d17268.html)
- Yang & Hamori (2020): **wavelet-based semiparametric** VaR/ES on WTI/Brent; **overall semiparametric wavelet models outperform** rolling-window and distribution-based GARCH for **all scales**; on **raw** returns **GARCH-FZ** best (avg rank **1**), on **D6** **hybrid** best (avg rank **~1.5–2**); FZ0 average loss at α=0.05 for raw WTI **GARCH-FZ 1.605** vs **GARCH-N 1.613** (marginal). — [Energies 13(14) 3700](https://ideas.repec.org/a/gam/jeners/v13y2020i14p3700-d386267.html)
- Cai et al. (2020): with **time-varying SJC** on MODWT scales, **portfolio variance reduction** (oil hedge vs stock-only) **RR_PV ≈ 0.28–0.30** on raw returns (e.g. Japan **0.295**, China **0.295**, Korea **0.280**); **D1** similar (**~0.27–0.30**); benefits **decline** toward **D4–D6** (e.g. Japan D6 **0.063**). **ES reduction** raw Japan **0.176**, D1 **0.159**, D6 **0.043**. — [MDPI Energies 13(2) 294](https://www.mdpi.com/2071-1050/13/2/294)
- Copula-GARCH vs variance–covariance (Romanian BET-FI proxy, 2012): **ES from copula-GARCH ~1.54–2.00%** vs **VaR variance–covariance ~1.46–1.83%**—Gaussian/i.i.d. **understates** tail risk. — [Revista FS PDF](https://www.icfm.ro/RePEc/vls/vls_pdf/vol19i2p8-16.pdf)
- Berger (2015): portfolios minimizing **short-horizon (noise) scale covariance** **outperform** classical minimum-variance on **raw returns** in risk-adjusted terms (no Gaussian-copula VaR table in abstract). — [Physica A 436](https://doi.org/10.1016/j.physa.2015.05.053)
- Shahzad et al. (2016): **country VaR** and **two-asset portfolio VaR** computed **scale-by-scale** to rank **Greece diversification** partners—uses copula dependence, not a single Gaussian correlation matrix. — [Physica A 457](https://doi.org/10.1016/j.physa.2016.03.048)
- Simulation literature (copula VaR, 2021): **Gaussian copula tends to underestimate VaR**; **t** slightly better; **vine** best in-sample but **overfits** out-of-sample—warns that **tail copula complexity ≠ better VaR** without scale decomposition. — [Communications for Statistical Applications and Methods 28(1)](http://www.csam.or.kr/journal/view.html?doi=10.29220%2FCSAM.2021.28.1.059)

### Inferences
- For **portfolio tail risk**, wavelet–copula’s value is often **heterogeneous horizons**: using **short-scale weak dependence** improves **hedge effectiveness** (Cai et al. PV/ES ratios), while **long scales** show **stronger tail dependence** but **lower diversification benefit**.
- **VaR backtest “win” vs Gaussian** is clearest in **wavelet-denoised univariate/multivariate** pipelines (Aloui & Jammazi; Khalfaoui) and **univariate scale-wise semiparametric** oil forecasts (Yang & Hamori), not in a large table of **equity portfolio Kupiec tests for wavelet-SJC vs Gaussian copula**.

### Gaps
- Few published **equally weighted equity portfolio** studies report **Christoffersen / FZ loss** for **MODWT-scale copula** vs **one Gaussian copula on full-sample residuals** with identical GARCH margins.
- Magnitudes are **market-specific** (oil–Asia, oil–FX, BET-FI); **direct % VaR breach rate improvement** for US/EU equity baskets is rarely quoted.

---

## Canonical pipeline: GARCH margins → wavelet decompose → copula per scale → risk measure?

### Takeaway
The **dominant econometric pipeline** is: **(1)** fit **ARMA–GARCH / GJR-GARCH / APARCH** (often **skew-t** or Hansen skew-t) to each return series; **(2)** take **standardized residuals** (sometimes PIT uniforms **u = F(ẑ)**); **(3)** **MODWT/MRA** decompose **residuals or shocks** into **{D₁,…,D_J, S_J}**; **(4)** fit **static or time-varying copula** **separately per scale** (bivariate or vine for multivariate); **(5)** derive **tail dependence**, **simulated portfolio returns**, **VaR/ES**, **CoVaR/ΔCoVaR**, or **hedge ratios**. Variants: decompose **raw returns** then copula (WC-GARCH COVID); **VMD + HTW denoise** then copula (Shahzad); **wavelet denoise then single copula** on smoothed series (Aloui & Jammazi).

### Cited Findings
- Cai et al. (2020) explicit order: **GJR-GARCH + Hansen skew-t → MODWT on ẑ → conditional copula (incl. DCC-type κ_t ARMA on transformed uniforms) → tail τ_U, τ_L → simulate portfolios for PV/ES reduction**. — [MDPI Energies 13(2) 294](https://www.mdpi.com/2071-1050/13/2/294)
- Shahzad et al. (2016): **ARMA–GARCH skew-t margins → HTW + VMD on standardized residuals → copula selection (Joe–Clayton TV) → scale-wise portfolio VaR**. — [Physica A 457](https://doi.org/10.1016/j.physa.2016.03.048)
- Jammazi & Reboredo (2016): **margins (GARCH-type) → Haar à trous decomposition → copula (static/TV) per scale → diversification / downside risk of mixed oil–stock portfolios**. — [Energy 107](https://ideas.repec.org/a/eee/energy/v107y2016icp866-888.html)
- Berger (2015): **wavelet decomposition of returns → dependence (Pearson + copula tails) by scale → minimum-variance portfolios using scale-specific covariance**. — [Physica A 436](https://doi.org/10.1016/j.physa.2015.05.053)
- WC-GARCH (COVID): **Step 1 wavelet decompose returns; Step 2 copula + GARCH margins on components** (“WC-GARCH”). — [JRFM 14(7) 329](https://www.mdpi.com/1911-8074/14/7/329)
- Carvalho et al. (2021): **ARIMA-APARCH → MODWT → D-vine BB7 on standardized residuals** at intraday-labeled scales. — [PMC8150631](https://pmc.ncbi.nlm.nih.gov/articles/PMC8150631/)
- Yang & Hamori (2020) (**univariate** risk): **MODWT on returns → semiparametric GARCH-FZ or hybrid on each detail** → forecast **VaR/ES** (no copula step). — [Energies 13(14) 3700](https://ideas.repec.org/a/gam/jeners/v13y2020i14p3700-d386267.html)
### Inferences
- For **SAIFA Quant Edge (multi-horizon equity tail dependence)**: implement **GJR-GARCH-skew-t → MODWT(J=6) on standardized residuals → time-varying SJC or Joe–Clayton per (D_j, asset pair)**; aggregate to portfolio via **simulation** or **vine** if **N > 2**; report **τ_L, τ_U by j** and **ES reduction** vs single-scale t-copula baseline.
- **Order sensitivity**: most dependence papers decompose **residuals** (preserve volatility modeling); WC-GARCH decomposes **returns first**—material for comparing to literature.
- Equity-focused work (Berger 2015; Gallegati 2012; Shahzad 2016; Dewandaru et al. 2015/2016) stresses **contagion on D1–D2** vs **long-run interdependence on high scales**; **monitor τ_L on D1–D3** for tactical risk and **D5–S_J** for strategic correlation breakdown.

### Gaps
- No consensus on **summarizing multi-scale copulas into one portfolio VaR** (sum of details vs copula on reconstructed series vs worst-scale ES); papers usually report **scale-by-scale** risk or **economic hedge ratios**, not a single Basel-style 1-day 99% number from fused scales.
- Limited **US/EU multi-asset equity basket** papers combine **MODWT-scale copula** with **regulatory ES backtesting**; energy–FX and oil–stock domains supply most numeric risk comparisons.
- Dewandaru et al. (2015, *Physica A* 419) and (2016, *IREF* 43) document **Asia-Pacific multi-scale contagion** with wavelets but **not copula–VaR pipelines**—relevant for equity horizon heterogeneity only as dependence background. — [Physica A 419](https://doi.org/10.1016/j.physa.2014.10.046); [IREF 43](https://ideas.repec.org/a/eee/reveco/v43y2016icp363-377.html)
