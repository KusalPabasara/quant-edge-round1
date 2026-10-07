# Financial tail dependence across investment horizons (wavelet–copula evidence)

**Scope:** Worldwide empirical studies combining wavelet (or VMD) decomposition with copula-based tail dependence (λ_L, λ_U or Patton τ_L, τ_U), contrasted with multi-scale **correlation** contagion literature. Emphasis on equity/portfolio risk for competition briefs.

**Methodological note for synthesis:** Most finance papers label **D1 = highest frequency (shortest horizon)** and **D6/S_J = lowest frequency (longest horizon)** under MODWT/DWT (e.g., D1 ≈ 2–4 days, D6 ≈ 64–128 days in daily data). A few older papers reverse level numbering; always check the paper’s scale–day mapping before comparing λ across studies.

---

## Does λ_L typically increase or decrease with coarser wavelet scales?

### Takeaway
There is **no single universal sign**, but the **dominant pattern in wavelet–copula work is that average and tail dependence rise with horizon** (fine → coarse scales), especially for oil–equity and oil–commodity links. **Crisis episodes often flatten or reverse this** by spiking short-horizon tail dependence while long-run levels stay high or change little. Asset-class and pair-specific asymmetry (λ_L vs λ_U) is the norm, not the exception.

### Cited Findings
- **Oil–stock (global sample, Haar à trous + copulas):** Before Lehman (15 Sep 2008), dependence was **weak at fine scales and “increased considerably as the time scale lengthened”**; after Lehman, dependence **rose at all scales** (contagion + interdependence). Pre-crisis **asymmetric tail dependence mainly at long run**; post-crisis **both upper and lower tail dependence**. Short-horizon diversification/downside benefits existed pre-crisis but **shrank at coarser scales**; post-crisis benefits **fell sharply, especially long run**. — [Jammazi & Reboredo (2016), *Energy*](https://ideas.repec.org/a/eee/energy/v107y2016icp866-888.html)
- **Crude oil vs East Asian equities (Japan, China, Korea; MODWT D1–D6 + SJC):** Oil–stock dependence **“increase[s] and become[s] more significant as the time scales increase.”** SJC fits best; **significant tail dependence except at D1 (very short term)**; dynamic figures show **“very weak tail dependence in the short term”** rising at mid/long scales, with **level and fluctuation of dependencies increasing with scale**. Oil can hedge equities **especially short- and mid-term**, but hedging **weakens over long run**. — [Cai et al. (2020), *Energies*](https://www.mdpi.com/1996-1073/13/2/294); [open PDF](https://da.lib.kobe-u.ac.jp/da/kernel/90007002/90007002.pdf)
- **Oil vs 10 agricultural commodities (MODWT + DCC–Student-t copula):** Post-2006 connectedness **rises at all frequencies**, but **“rate of increase is higher for longer investment horizons”**; pre-2006 horizon–connectedness slope **negative**, post-2006 **positive** (stronger long-run link). — [Pal & Mitra (2019), *Energy Economics*](https://www.sciencedirect.com/science/article/abs/pii/S014098831930026X)
- **Greece vs 11 European equity markets (HTW/VMD + TVP SJC):** **Long-run lower/upper tail dependence generally higher and less volatile than short-run**; **long-term dependence paths peak around 0.6** for Greece pairs; short-run paths **jump in crises**. Wavelet (HTW) sometimes shows **no significant tail dependence** for specific pairs (e.g., Greece–Ireland, Greece–Germany lower tail) where VMD shows significance—**decomposition choice matters**. — [Shahzad et al. (2016), *Physica A*](https://eprints.qut.edu.au/94816/1/1-s2.0-S0378437116300462-main.pdf)
- **Commodity implied volatilities (oil, wheat, corn; wavelet + copula):** **Time-varying asymmetric tail dependence** differs across **short, medium, long** horizons (not uniform across pairs). — [Mensi et al. (2017), *Energy Economics*](https://ideas.repec.org/a/eee/eneeco/v66y2017icp122-139.html)
- **Agricultural commodities vs macro risk factors (rates, USD/EUR, world equity; wavelet + copula):** Dependence and **tail dependence on FX and world stock index are scale-dependent and often asymmetric**; USD/EUR and world equity dominate. — [Aloui et al. (2013), DEPOCEN WP](https://ideas.repec.org/p/dpc/wpaper/0413.html)
- **Oil–US equity / oil uncertainty (wavelet + quantile-on-quantile):** Tail linkage **“not uniform or symmetric across all horizons”**; sign and strength **flip by scale** (e.g., long horizons D4–D8 often inverse for OVX vs DJI). — [Frontiers in Physics (2024)](https://www.frontiersin.org/journals/physics/articles/10.3389/fphy.2024.1357366/full)
- **Contrast (correlation-only, not copula tails):** Gallegati-style wavelet **correlation** often **strengthens at intermediate/coarse scales** vs finest scales (e.g., stock returns vs industrial production). — [Gallegati, wavelet stock–activity](https://iris.univpm.it/handle/11566/35189)

### Inferences
- For **competition/portfolio briefs**, the safe prior is: **λ and linear ρ both tend to be lower at daily/noise scales and higher at monthly/quarterly scales** for macro-linked pairs (oil, FX, regional equity).
- **Tail asymmetry:** Lower-tail co-movement often **dominates in stress** (equities, commodities), but **upper tail can dominate** for some crypto pairs (non-wavelet copula evidence).
- **Hedging narrative:** Several oil–equity studies find **better hedge/safe-haven behavior at short/medium scales** even when **long-run tail dependence is high**—horizon mismatch can make “oil diversifies equities” both true and false depending on holding period.

### Gaps
- Few papers report **λ_L, λ_U on the same 0–1 scale across ≥4 scales for a **global equity portfolio** (most are pairwise or regional).
- **Direct comparison** of Patton λ vs copula-parameter tail indices across papers is rarely done.

---

## How do crises (GFC 2008, COVID-2020) change scale-specific tail dependence?

### Takeaway
**GFC:** Persistent **elevation of dependence and tail dependence across short and long scales** (contagion plus lasting interdependence), not only high-frequency spikes. **COVID:** Strong **short-horizon “pure contagion”** (roughly 2–64 days in WC-GARCH studies) with **pre-crisis tail correlation often low ≤16 days and high at 32–128 days**; during COVID, **tail dependence jumps at D1–D2 (2–8 days)** while **long scales (D5–D6) often unchanged or lower**—a **different scale profile than GFC**.

### Cited Findings
- **GFC – oil & stocks:** Watershed **15 Sep 2008**; post-Lehman **all-scale dependence increase** and **upper + lower tail dependence** (see Jammazi & Reboredo above). — [Energy (2016)](https://ideas.repec.org/a/eee/energy/v107y2016icp866-888.html)
- **GFC – US equities (29 DJIA stocks, wavelet + copulas):** Post-Lehman **higher correlation and tail dependence at all time scales**, not only short-run contagion. — [Berger (2015), *Physica A*](https://www.sciencedirect.com/science/article/abs/pii/S0378437115004689)
- **GFC – Greece/Europe:** **Short-run lower tail dependence paths show sudden GFC increase**; **long-run interdependence with Greece remains high**. — [Shahzad et al. (2016)](https://eprints.qut.edu.au/94816/1/1-s2.0-S0378437116300462-main.pdf)
- **GFC – global equity coherence (wavelet coherence, not copula):** **Strong positive co-movement with US across frequency bands during GFC**; contagion from US to others. — [HAL working paper GFC/COVID/Ukraine sample](https://hal.science/hal-05050180v1/file/EB-25-V45-I1-P15.pdf)
- **GFC – international contagion test (wavelet correlation):** Subprime crisis contagion **scale-dependent**; **Brazil and Japan exceptions** where contagion not uniform across scales. — [Gallegati (2012), *Computational Statistics & Data Analysis*](https://www.sciencedirect.com/science/article/abs/pii/S0167947310004317)
- **COVID – six major markets, WC-GARCH (Clayton on scale components):** Pre-COVID: tail correlation **“rather low up to 16 days”** (D1–D3), **higher at 32–128 days** (D5–D6)—e.g. US–Japan **~0.5 (D5) to ~0.8 (D6)**; US–Hong Kong **~0.4–0.6**. COVID subperiod: **tail dependency rises at D1–D2 (2–8 days) for all markets** (“pure contagion”); **D3–D4 up to ~32 days** still elevated; **D5–D6 smaller or similar** vs pre-COVID → **crisis mainly reweights dependence to high frequencies**. — [Alqaralleh & Canepa (2021), *J. Risk Financial Manag.*](https://doi.org/10.3390/jrfm14070329)
- **COVID – wavelet-copula-GARCH (SSR/working paper):** **Strong contagion** across six major markets during pandemic (frequency–time decomposition). — [SSRN 3631067](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3631067)
- **COVID – US sectors (copula tails, not wavelet):** Pandemic **increases tail dependence**, **λ_L more than λ_U** for S&P 500 vs sectors. — [Kim & Jung (2023), *Applied Economics Letters*](https://ideas.repec.org/a/taf/apeclt/v30y2023i4p510-515.html)
- **COVID – tail networks (quantile coherency, 1-day frequency focus):** Left/right tail networks at **5%/95%** quantiles; emphasizes **instantaneous** tail linkage rather than multi-scale λ. — [Bilkent repository PDF](https://repository.bilkent.edu.tr/server/api/core/bitstreams/2c60c982-4554-400a-a66d-a8e9e08c3f86/content)

### Inferences
- **GFC** fits **“interdependence ratchet”**: long-horizon λ stays elevated after shock; short-horizon also rises.
- **COVID** fits **“panic at high frequency”**: portfolio models using **only long-run copulas** can **miss the contagion channel** that dominated early 2020.
- For briefs: stress-test **both** (i) **long-run strategic asset mix** and (ii) **weekly/daily rebalance horizons** separately.

### Gaps
- Few papers estimate **the same copula family pre/post COVID on identical scales for GFC and COVID** in one panel.
- **λ_L numeric tables** for COVID wavelet-copula papers are often in figures, not summary tables.

---

## Are findings consistent across equities, commodities, and FX?

### Takeaway
**Partially consistent:** **Scale-dependent tails are ubiquitous**; **direction of scale gradient** depends on pair type. **Equity–equity (developed)** often shows **strong long-run tail/interdependence**; **commodity–equity** often **weak tails at finest scale, stronger at coarse scales**; **FX/agriculture** shows **strong scale effects with USD/EUR dominant**. **Crypto** multi-scale work is rich on **correlation/coherence** but **pure wavelet–copula tail papers are thinner**.

### Cited Findings
- **Equities – Europe/Greece:** Significant **upper and lower tail** dependence; crisis spikes in **short-run λ_L**; long-run **high interdependence**. — [Shahzad et al. (2016)](https://eprints.qut.edu.au/94816/1/1-s2.0-S0378437116300462-main.pdf)
- **Equities – US DJIA cross-section:** Tail dependence **varies by scale**; post-2008 **all scales elevated**. — [Berger (2015)](https://www.sciencedirect.com/science/article/abs/pii/S0378437115004689)
- **Equities – Asia-Pacific (wavelet, mostly correlation/contagion):** **Low short-run co-movement**, crisis transmission via **excessive linkages** at specific horizons; subprime **fundamentals-based contagion** with Japan leading. — [Dewandaru et al. (2016), *Int. Rev. Econ. Finance*](https://ideas.repec.org/a/eee/reveco/v43y2016icp363-377.html)
- **Commodities – oil/agriculture:** Stronger **long-horizon** connectedness post-2006; diversification **worse at long holding periods**. — [Pal & Mitra (2019)](https://www.sciencedirect.com/science/article/abs/pii/S014098831930026X)
- **Commodities – ag vs macro factors:** **Scale-dependent tail** dependence on **USD/EUR** and **world stock** factors. — [Aloui et al. (2013)](https://ideas.repec.org/p/dpc/wpaper/0413.html)
- **FX – oil vs major USD exchange rates (wavelet-EGARCH, wavelet-copula, wavelet-EVT):** Denoised wavelet models **improve VaR and ES** vs raw series for oil–FX portfolios. — [Aloui & Jammazi (2015), *Physica A*](https://ideas.repec.org/a/eee/phsmap/v436y2015icp62-86.html)
- **Crypto – high-frequency multiscale:** **Positive co-movements** especially BTC–ETH–Monero; **scale-specific Granger causality** (some pairs non-causal at D1/D2 → hedging at those scales). — [Financial Innovation (2021)](https://link.springer.com/article/10.1186/s40854-021-00290-w)
- **Crypto – tail dependence (daily copula, not wavelet):** **Strong upper and lower tail** among major coins; pair-specific **λ_U vs λ_L** dominance. — [Economics & Finance (2020)](https://ideas.repec.org/a/eee/ecofin/v51y2020ics1062940818305497.html)
- **International PCC + wavelet (US, Germany, Brazil, Hong Kong):** **Fine scales (levels 6–9, ~≤2 weeks)** used for contagion copulas; **Kendall τ** often **0.05–0.66** depending on pair/scale/crisis subperiod. — [WSEAS wavelet–PCC (2014)](https://wseas.com/journals/bae/2014/a165707-278.pdf)

### Inferences
- **Equity portfolios:** Ignore scale → **overstate diversification at daily horizon, understate at monthly** (or vice versa in COVID shock weeks).
- **Commodity/FX overlays:** Risk factors **change rank by scale** (FX/stock index dominate ag tails at some scales only).
- **Crypto:** Treat as **separate asset class**; multi-scale **correlation** is high but **tail copula-by-scale** evidence is still **sparse** vs oil/equity.

### Gaps
- **Unified global panel** (e.g., MSCI regions + Brent + DXY + BTC) with **harmonized λ_L/λ_U by D1–D6** is not found in open literature reviewed here.
- **FX spot pairs (non-commodity-linked)** with wavelet–copula tails are less common than oil–FX or oil–equity.

---

## What happens to measured portfolio risk (VaR/ES) if one ignores scale-varying tail dependence?

### Takeaway
Ignoring multi-scale dependence typically **biases VaR/ES downward in calm periods (too optimistic)** or **fails Kupiec/backtests when crises concentrate tail risk at short scales**. Wavelet–copula or wavelet-denoised models **often improve VaR/ES accuracy vs single-scale copula/GARCH**, though **published % improvements are rarely standardized**—most evidence is **qualitative + backtest pass rates**.

### Cited Findings
- **Agricultural commodities vs macro factors:** Wavelet–copula **“improves the accuracy of VaR estimates, compared to traditional approaches.”** — [Aloui et al. (2013)](https://ideas.repec.org/p/dpc/wpaper/0413.html)
- **Oil–exchange rate portfolios:** Models on **denoised wavelet series outperform** raw-series models for **VaR and ES**; better **extreme event detection**. — [Aloui & Jammazi (2015)](https://www.sciencedirect.com/science/article/abs/pii/S0378437115004513)
- **Greece–Europe:** **Scale-by-scale VaR ratios** used to show portfolio implications; **two-asset VaR** identifies diversification partners; **country VaR splits “two groups.”** — [Shahzad et al. (2016)](https://eprints.qut.edu.au/221032/)
- **East Asia oil–stock:** **Time-varying hedging and tail-risk hedging performance differ by horizon**; long-run hedging **reduced**. — [Cai et al. (2020)](https://www.mdpi.com/1996-1073/13/2/294)
- **COVID WC-GARCH:** Ignoring **short-horizon contagion tail dependence** **“may underestimate the level of systematic risk”** during global distress. — [Alqaralleh & Canepa (2021)](https://doi.org/10.3390/jrfm14070329)
- **DJIA minimum-variance:** Portfolios built from **short-scale (noise) covariance** can **outperform** classical full-series min-var on **risk-adjusted performance**—implies **scale matters for construction**, not only VaR. — [Berger (2015)](https://www.sciencedirect.com/science/article/abs/pii/S0378437115004689)
- **Brazilian equity factor copulas (Haar, daily):** **Out-of-sample VaR** “consistent” when using **short and short–medium components**; **small tail-dependence increments at lower frequencies** after COVID in intraday D-Vine study. — [UFLA thesis summary](https://repositorio.ufla.br/items/a44b7ef3-6d7e-4b0d-b74b-a9cd89a974e0/full)
- **Asian copula VaR (non-wavelet):** **Normal copula VaR more aggressive** than tail-aware copulas; **SJC/RGC backtests** differ in exceedance rates. — [Asian markets dynamic copula (2015)](https://exa.ai/library/publication/zvrdd20xsfb)

### Inferences
- For **competition briefs**, cite **mechanism** rather than a single %: **single-scale t-copula VaR treats tail co-movement as constant across holding periods**; when **true λ_L is scale-specific**, ES for a **10-day horizon portfolio** can be **materially wrong** if estimated from **daily noise or from long-run trend only**.
- **Practical mitigation:** Multi-scale **ES as weighted sum of scale components**, or **horizon-matched copula** on MODWT detail level matching rebalance frequency (literature supports concept; **no universal calibration constant** found).

### Gaps
- **Quantified % VaR/ES underestimation** from ignoring scale (e.g., “15% ES shortfall”) is **rare in peer-reviewed abstracts**; mostly **backtest failure rates** or **directional “improves accuracy.”**
- Few papers link **Basel expected shortfall** multi-horizon capital directly to wavelet–copula.

---

## Dissenting or nuance papers (weak / no scale effect / decomposition sensitivity)

### Takeaway
**“No scale effect” is uncommon**; stronger dissent is **(a) scale effects differ by pair/crisis, (b) decomposition method changes tail inference, (c) long-memory filtering masks or inflates dependence, (d) some horizons show zero tail dependence (e.g., oil–Asia D1).**

### Cited Findings
- **Oil–East Asia D1:** **No significant tail dependence** at very short term despite significance from D2 upward. — [Cai et al. (2020)](https://www.mdpi.com/1996-1073/13/2/294)
- **Greece pairs:** **HTW wavelet** → **no upper/lower tail** for some pairs (Ireland, Germany λ_L) while **VMD shows significant tails**—**scale + method sensitivity**, not “no effect globally.” — [Shahzad et al. (2016)](https://eprints.qut.edu.au/94816/1/1-s2.0-S0378437116300462-main.pdf)
- **Oil–China A-shares (rolling copula, firm level, not wavelet):** Tail dependence **persistent short-term but deteriorates as duration increases**—**disagrees with “λ_L always rises with horizon”** for that market structure. — [Fang & Egan (2021)](https://ideas.repec.org/a/wly/ijfiec/v26y2021/i1/p1469-1487.html)
- **Long memory / filtering (DJ Islamic sub-indexes, vine copulas):** **Filtered vs raw** returns give **opposite bivariate vs conditional dependence**—**true tail dependence can be masked** by long-memory preprocessing. — [SSRN 3100890](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3100890)
- **Asia-Pacific wavelet (correlation):** **Low short-run co-movement** across JP/HK/AU—suggests **diversification at high frequency** even when long-run linked. — [Dewandaru et al. (2016)](https://ideas.repec.org/a/eee/reveco/v43y2016icp363-377.html)
- **Gallegati contagion:** Contagion **not uniform across scales** for **Brazil and Japan** during subprime. — [Gallegati (2012)](https://www.sciencedirect.com/science/article/abs/pii/S0167947310004317)
- **Oil–agriculture dynamics:** Post-2006 higher connectedness partly **level effect**; **dynamic connectedness** pre/post-2006 **similar**—scale pattern in **correlation** may be **stable** while **levels shift**. — [Pal & Mitra (2019)](https://www.sciencedirect.com/science/article/abs/pii/S014098831930026X)

### Inferences
- **Do not overclaim** “λ_L always increases with scale” in a brief; present as **empirical regularity with crisis- and pair-specific exceptions**.
- **Robustness:** Show **two decompositions** (MODWT vs VMD) or **horizon bands** (short/medium/long) rather than a single λ curve.

### Gaps
- Explicit papers titled **“no scale effect in tail dependence”** were **not found**; null results appear as **pair-specific insignificance** or **D1-only zeros**.

---

## Quick reference – illustrative quantitative anchors (competition-ready)

| Study | Context | Scale / horizon | Quantitative snippet |
|-------|---------|-----------------|----------------------|
| Alqaralleh & Canepa (2021) | US vs 5 markets, pre-COVID | D5–D6 (~64–128d) | Tail corr US–Japan **~0.5 → ~0.8**; US–HK **~0.4–0.6** |
| Alqaralleh & Canepa (2021) | COVID | D1–D2 (2–8d) | **Tail dependence up** for all; long scales **flat/down** |
| Shahzad et al. (2016) | Greece–Europe | Long-run λ paths | **Peak ~0.6**; short-run **crisis spikes** |
| Cai et al. (2020) | Oil–East Asia | D1 vs D2+ | **τ_L ≈ 0 / insignificant at D1**; significant beyond |
| Jammazi & Reboredo (2016) | Oil–stock | Pre/post Lehman | **Weak fine-scale** pre-crisis; **all scales up** post |

---

## Suggested citations for brief narrative (equity risk focus)

1. **Horizon matters for tails:** [Cai et al. (2020)](https://www.mdpi.com/1996-1073/13/2/294), [Jammazi & Reboredo (2016)](https://ideas.repec.org/a/eee/energy/v107y2016icp866-888.html), [Shahzad et al. (2016)](https://eprints.qut.edu.au/94816/1/1-s2.0-S0378437116300462-main.pdf)
2. **GFC vs COVID scale profile:** [Berger (2015)](https://www.sciencedirect.com/science/article/abs/pii/S0378437115004689), [Alqaralleh & Canepa (2021)](https://doi.org/10.3390/jrfm14070329)
3. **VaR/ES if ignored:** [Aloui & Jammazi (2015)](https://ideas.repec.org/a/eee/phsmap/v436y2015icp62-86.html), [Aloui et al. (2013)](https://ideas.repec.org/p/dpc/wpaper/0413.html), COVID discussion in [JRFM 2021](https://doi.org/10.3390/jrfm14070329)
4. **Conceptual contagion vs interdependence by frequency:** [Gallegati (2012)](https://www.sciencedirect.com/science/article/abs/pii/S0167947310004317), [Forbes & Rigobon (2002)](https://ideas.repec.org/a/bla/jfinan/v57y2002i5p2223-2261.html) (baseline, non-wavelet)

---

*Research compiled for report synthesis; all claims tied to linked sources. Where numeric % VaR improvements were unavailable in accessible abstracts/full text, noted under Gaps rather than imputed.*
