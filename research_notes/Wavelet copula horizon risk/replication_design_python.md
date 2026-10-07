# Wavelet–Copula Portfolio Risk: Python Replication Design (US Sector ETFs)

Dense design notes for a same-day, laptop-scale replication: equal-weight portfolio of **SPY, XLE, XLF, XLK, XLV, XLI, XLU** via Yahoo Finance, with MODWT → GARCH marginals → copula dependence → Monte Carlo VaR/ES and standard out-of-sample backtests.

---

## Python libraries: GARCH, wavelets, copulas (and margins)

### Takeaway
Use **`arch`** for GARCH/GJR/eGARCH and built-in VaR-from-volatility recipes; **`modwtpy`** (or vendored `modwt.py`) for MATLAB-compatible MODWT/MRA; **`copulae`** as the primary multivariate parametric copula fitter (Clayton, Gaussian/Normal, Student-t) with explicit `log_lik()` for AIC. Reserve **`pyvinecopulib`** only if you need fast bivariate tail statistics or a truncated vine; skip full vine forests for competition scope. **`scipy`** / **`statsmodels`** cover marginal diagnostics, distributions, and optimization already pulled in by `arch` and `copulae`.

### Cited Findings
- **`arch`**: `arch_model()` defaults to constant mean + GARCH(1,1) + normal errors; GJR/TARCH via `GARCH(p,o,q)` with `o=1` or `power=1.0`; distributions include Normal and Student-t; VaR documented as \( \mathrm{VaR}_{t+1|t} = -\mu_{t+1|t} - \sigma_{t+1|t}\, q_\alpha \) with `res.forecast(align="target")` and `am.distribution.ppf()` — [ARCH volatility forecasting / VaR](https://arch.readthedocs.io/en/stable/univariate/univariate_volatility_forecasting.html)
- **`arch`**: Multi-step forecasts support `method="analytic"`, `"simulation"`, or `"bootstrap"` with default `simulations=1000` in the volatility forecast API — [ARCH forecasting](https://arch.readthedocs.io/en/latest/univariate/forecasting.html)
- **`arch`**: License **NCSA**; Python **≥3.10** on current PyPI — [arch on PyPI](https://pypi.org/project/arch/)
- **PyWavelets**: DWT, SWT (stationary), CWT; **no native MODWT** — [PyWavelets SWT docs](https://pywavelets.readthedocs.io/en/stable/ref/swt-stationary-wavelet-transform.html)
- **`modwtpy`**: `modwt` / `modwtmra` implemented with PyWavelets filters, aligned to MathWorks MODWT/MRA docs — [modwtpy GitHub](https://github.com/pistonly/modwtpy)
- **`copulae`**: `ClaytonCopula`, `GaussianCopula`, `StudentCopula` with ML fit, `log_lik()`, pseudo-observations (`to_pobs=True`) — [Clayton](https://copulae.readthedocs.io/en/latest/api_reference/copulae/archimedean/clayton.html), [Gaussian](https://copulae.readthedocs.io/en/stable/api_reference/copulae/elliptical/gaussian.html), [Student](https://copulae.readthedocs.io/en/latest/api_reference/copulae/elliptical/student.html)
- **`copulae`**: Depends on **numpy, pandas, scipy, statsmodels, scikit-learn**; custom permissive license; Python **≥3.10** — [copulae on PyPI](https://pypi.org/project/copulae/)
- **SDV `copulas`**: `GaussianMultivariate`, `VineCopula`, `log_probability_density()` on multivariate base class — useful if you want vine structure with Python-native API — [Copulas multivariate API](https://sdv.dev/Copulas/api/copulas.multivariate.html), [Copulas overview](https://sdv.dev/Copulas/)
- **`pyvinecopulib`**: C++ vinecopulib bindings; `Bicop` / `Vinecop` with pseudo-observations; **`pip install pyvinecopulib`** for wheels — [pyvinecopulib README](https://vinecopulib.github.io/pyvinecopulib/README.html)
- **Tail dependence (for reporting, not always in-library)**: Gaussian λ_L = λ_U = 0; Clayton λ_L = 2^{-1/θ}, λ_U = 0 (bivariate); Student-t symmetric λ from ρ and ν — [VineCopula BiCopPar2TailDep](https://tnagler.github.io/VineCopula/reference/BiCopPar2TailDep.html), [Tinbergen copula comparison](https://papers.tinbergen.nl/08105.pdf)
- **Reference copula–GARCH portfolio stack (sector ETFs XLK/XLF/XLI/XLV)**: [quant-copula-risk GitHub](https://github.com/zzovcharov/quant-copula-risk) (Gaussian copula + t marginals; not wavelet)

### Inferences
- **AIC for copula selection (competition-simple)**: For each candidate copula `c`, after `c.fit(u)` on pseudo-observations `u` (or standardized GARCH residuals mapped to uniforms): `AIC = -2 * c.log_lik(u) + 2 * k`, with `k = 1` for Clayton (Archimedean generator), `k = d(d-1)/2` for Gaussian, `k = d(d-1)/2 + 1` if Student df is estimated (`fix_df=False`). Compare Clayton vs Gaussian vs Student on the **same** `u` matrix — pattern matches applied copula papers using AIC — [PMC copula AIC example](https://pmc.ncbi.nlm.nih.gov/articles/PMC9415648/)
- **Margins**: Fit per-asset (or per-scale) GARCH in `arch` with `dist="t"` or `"skewt"`; convert residuals to uniforms via `scipy.stats.rankdata` / `copulae` `pobs()` before copula ML — [Clayton fit docs](https://copulae.readthedocs.io/en/latest/api_reference/copulae/archimedean/clayton.html)
- **7-dimensional copula**: `copulae` supports `dim=7` elliptical copulas directly; Clayton as exchangeable Archimedean is feasible but only lower-tail dependent — [copulae PyPI description](https://pypi.org/project/copulae/)
- **pyvinecopulib** for competition: use **`Bicop`** on each pair for tail-λ tables and optional AIC via `loglik`; full **`Vinecop`** is overkill unless you truncate aggressively (`truncated=1` or pair-copula only) — [pyvinecopulib features](https://vinecopulib.github.io/pyvinecopulib/features.html)

### Gaps
- **`copulae` does not document a built-in `aic()` helper or tail-dependence method** on fitted objects; tail λ must be computed from estimated parameters using published formulas — [VineCopula tail table](https://tnagler.github.io/VineCopula/reference/BiCopPar2TailDep.html)
- **SDV Copulas** vine “best copula per edge” is powerful but slower and heavier than a single 7-D elliptical/Clayton fit; no single cited benchmark for your exact ETF set.

---

## MODWT in Python when PyWavelets only exposes DWT/SWT

### Takeaway
For replication fidelity to wavelet–VaR papers, prefer **`modwtpy`**’s `modwt` + `modwtmra` (db2/sym4/haar). Treat **`pywt.swt(..., norm=True)`** as a related but **not identical** MODWT implementation with length constraints (`len % 2**level == 0`). Do **not** use decimated **`pywt.wavedec`** for rolling OOS VaR if the paper cites shift-invariance and variance preservation.

### Cited Findings
- PyWavelets **SWT** with `norm=True` is “closely related” to MODWT but “implementation slightly different”; requires signal length multiple of `2**level` — [PyWavelets SWT](https://pywavelets.readthedocs.io/en/stable/ref/swt-stationary-wavelet-transform.html)
- PyWavelets maintainers: **MODWT ≠ SWT**; MODWT not in core library — [PyWavelets issue #200](https://github.com/PyWavelets/pywt/issues/200)
- **`modwtpy`**: circular convolution MODWT, filters from PyWavelets, MRA reconstruction — [modwt.py source](https://github.com/pistonly/modwtpy/blob/master/modwt.py)
- MODWT **preserves variance** and is **shift-invariant** (critical for rolling windows) — [BRE MODWT–VaR paper PDF](https://periodicos.fgv.br/bre/article/download/77437/78201/175571)
- Empirical finance replication using **db2 MODWT**, multi-level decomposition, MRA, then GARCH on reconstructed scales — same paper; **8 decomposition levels** on daily stock returns — [BRE MODWT–VaR paper PDF](https://periodicos.fgv.br/bre/article/download/77437/78201/175571)
- Wavelet–copula–GARCH contagion paper uses **DWT** (not MODWT) in step 1, then copula–GJR on scale components — [WC-GARCH publication summary](https://exa.ai/library/publication/b5tzxxt180k)

### Inferences
- **Competition-acceptable approximations** (in order of preference): (1) vendored **`modwtpy`** (~100 LOC dependency + PyWavelets); (2) **`pywt.swt`** with `norm=True` after **padding** daily returns to `2**J` (e.g. `numpy.pad` as PyWavelets suggests), document deviation from MATLAB MODWT; (3) **aggregate scales in MRA** to short/medium/long bands (sum detail coefficients + final scaling) to reduce copula dimensionality and runtime — [BRE paper MRA motivation](https://periodicos.fgv.br/bre/article/download/77437/78201/175571)
- **Filter choice**: **Daubechies db2** appears repeatedly in MODWT finance work — [BRE paper](https://periodicos.fgv.br/bre/article/download/77437/78201/175571), [Springer MODWT intraday vine paper](https://link.springer.com/content/pdf/10.1007/s43546-021-00080-7.pdf)
- **Levels `J`**: With ~5,000+ daily obs (1998–present), `J=5` or `6` is typical; papers using **8 levels** on single stocks imply checking that effective sample at coarsest scale still supports GARCH — [BRE paper](https://periodicos.fgv.br/bre/article/download/77437/78201/175571)

### Gaps
- No PyPI package with MathWorks-identical MODWT besides **`modwtpy`** (unmaintained since ~2016, 102 GitHub stars) — [modwtpy](https://github.com/pistonly/modwtpy)
- **`modwtpy` is not on PyPI** in search results; plan **`pip install PyWavelets`** + copy `modwt.py` or install from GitHub URL in `requirements.txt` (verify install path in your environment).

---

## Out-of-sample VaR backtests (Kupiec, Christoffersen) and ES tests

### Takeaway
Report **Kupiec LR-UC** (unconditional coverage), **Christoffersen LR-IND** (violation clustering), and **LR-CC = LR-UC + LR-IND ~ χ²(2)**. For ES, the fastest defensible add-on is **McNeil–Frey exceedance-residual bootstrap** on VaR violation days; full **Bayer–Dimitriadis ES regression** tests are R-first (`esback`).

### Cited Findings
- **Kupiec POF (1995)**: Tests whether empirical violation rate equals nominal α; LR statistic asymptotically **χ²(1)** — [Kupiec (1995) abstract](https://www.pm-research.com/content/iijderiv/3/2/73), [R kupiec reference](https://search.r-project.org/CRAN/refmans/segMGarch/html/kupiec-methods.html)
- **Christoffersen (1998) conditional coverage**: Joint test of correct coverage and **first-order Markov independence** of violations; LR_CC combines UC and independence — [NY Fed VaR evaluation primer](https://www.newyorkfed.org/medialibrary/media/research/epr/98v04n3/9810lope.pdf), [Value-at-Risk.net independence test](https://www.value-at-risk.net/backtesting-independence-tests/)
- **Hit rule (returns)**: Exception when **realized return < −VaR forecast** (or `< VaR` if VaR stored as negative quantile); align **t** forecast with **t** return (no look-ahead) — [xfinlink Kupiec/Christoffersen script](https://github.com/xfinlink/xfinlink-examples/blob/main/scripts/econometric-research/value-at-risk-backtest-kupiec-christoffersen-python.py)
- Reference implementations: [BayerSe/VaR-Backtesting `backtest.py`](https://github.com/BayerSe/VaR-Backtesting/blob/master/backtest.py), PyPI **`risk-backtest`** (Kupiec, Christoffersen, joint) — [risk-backtest](https://pypi.org/project/risk-backtest/1.0.1/)
- **McNeil–Frey (2000) ES**: On VaR exceedance days, residuals \(R_t = X_t - \widehat{ES}_t\) (optionally standardized) should have **mean zero**; test via **bootstrap** — [McNeil–Frey PDF](https://faculty.washington.edu/ezivot/econ589/EVT_Mcneil_Frey_2000.pdf)
- **ES backtest R package `esback`**: McNeil–Frey, Nolde–Ziegel, Bayer–Dimitriadis ES regression variants — [esback CRAN](https://cran.r-project.org/web/packages/esback/esback.pdf)
- **Implicit ES via multi-level VaR** (multinomial / chi-square on binned exceedances) — [Kratz–Lok–McNeil arXiv PDF](https://arxiv.org/pdf/1611.04851)
- Wavelet–VaR empirical papers apply **standard backtesting** on rolling forecasts (dynamic consistency) — [BRE MODWT–VaR paper](https://periodicos.fgv.br/bre/article/download/77437/78201/175571)

### Inferences
- **Minimum OOS length**: Kupiec notes **1% VaR tests have poor power in small samples**; aim for **≥250–500** OOS trading days for 95% VaR, **≥500–1000** for 99% if reporting 99% — [Kupiec PDF excerpt via PMR](https://www.pm-research.com/content/iijderiv%3A%3A%3A3%3A%3A%3A2%3A%3A%3A73.full.pdf?implicit-login=true&sigma-token=7szISvUUGUNBgb5jbmkQcZH9DP1qLuzjYRXt5mkGYPo)
- **Christoffersen edge case**: Undefined or weak when **no consecutive violations**; common in 95% tests — [Value-at-Risk.net](https://www.value-at-risk.net/backtesting-independence-tests/)
- **Quick Python ES check (~30 lines)**: (1) hits = `(r < -VaR)`; (2) on hit days, `resid = r - ES` (ES forecast negative of expected shortfall loss); (3) bootstrap mean(resid) with one-sided p-value — [McNeil–Frey PDF](https://faculty.washington.edu/ezivot/econ589/EVT_Mcneil_Frey_2000.pdf)
- **Sign convention**: Keep **returns** (not losses) throughout; store VaR as **positive number** meaning loss magnitude, or document `VaR = -quantile(r, α)` consistently — [arch VaR section](https://arch.readthedocs.io/en/stable/univariate/univariate_volatility_forecasting.html)

### Gaps
- **No widely adopted pure-Python package** for Bayer–Dimitriadis ES-only backtests equivalent to `esback` — [esback](https://cran.r-project.org/web/packages/esback/esback.pdf)
- **Basel traffic-light** regime for market risk is **not** the same as statistical Kupiec/Christoffersen; cite separately if mentioning regulatory zones — [risk-backtest docs mention zones](https://pypi.org/project/risk-backtest/1.0.1/)

---

## Yahoo Finance data: adjusted closes, survivorship, ETF history

### Takeaway
Download **daily `interval="1d"`** with **`auto_adjust=True`** (default) for **total-return-style** log returns on ETFs, **or** `auto_adjust=False` + explicit dividend handling if you need trade prices. Align all tickers on **common dates** from **1998-12-22** (sector SPDR listing) onward—not SPY’s 1993 start unless SPY is optional. Survivorship bias is **low for live sector ETF tickers** but **index rebalancing/GICS changes** (e.g. **XLC 2018**) affect economic interpretation, not ticker existence.

### Cited Findings
- **`auto_adjust=True`**: OHLC replaced by dividend/split-adjusted series derived from Yahoo **Adj Close** — [yfinance issue #1749](https://github.com/ranaroussi/yfinance/issues/1749), [yfinance utils.py](https://github.com/ranaroussi/yfinance/blob/6e52c83d9affc7a8a6a209f83d7482c64b24d67b/yfinance/utils.py)
- **Adjusted close ≠ Yahoo “total return” UI** in all cases; dividend reinvestment assumptions differ — [yfinance issue #2070](https://github.com/ranaroussi/yfinance/issues/2070)
- **Weekly/monthly** Yahoo adjustment can be wrong; **use daily and resample** — [yfinance issue #1273](https://github.com/ranaroussi/yfinance/issues/1273)
- **Sector SPDRs XLE, XLF, XLK, XLV, XLI, XLU**: **Inception 1998-12-16**, **NYSE Arca listing 1998-12-22** — [SSGA XLE](https://www.ssga.com/us/en/intermediary/etfs/state-street-energy-select-sector-spdr-etf-xle), [SSGA XLK](https://www.ssga.com/us/en/intermediary/etfs/state-street-technology-select-sector-spdr-etf-xlk)
- **SPY**: **Inception 1993-01-22**, first trade **1993-01-29** — [SSGA SPY](https://www.ssga.com/us/en/intermediary/etfs/state-street-spdr-sp-500-etf-trust-spy), [SEC SPY history](https://www.sec.gov/Archives/edgar/data/1222333/000119312513023294/d473476dfwp.htm)
- **Select Sector SPDR trust** organized **1998-06-10**; eleven sector funds listed in SEC filings — [SEC 497](https://www.sec.gov/Archives/edgar/data/1064641/000119312524055178/d788397d497.htm)
- **GICS / sector lineup changes**: **XLRE** (2015), **XLC** (2018) reclassifications; original nine sectors share **1998** launch — [ValuEngine sector ETF comparison](http://blog.valuengine.com/index.php/sector-etf-major-provider-comparisons/)

### Inferences
- **Replication sample**: `start='1999-01-01'` (or first full month after listing) through `end=today` for **7 sector ETFs + SPY**; **inner join** on calendar dates; drop rows with any missing ticker.
- **Returns**: `r_t = log(P_t / P_{t-1})` on adjusted close; for equal-weight portfolio, `r_p,t = (1/7) Σ r_i,t` on the six sectors **or** include SPY as eighth asset if brief requires—competition text says equal-weight sector ETF portfolio (clarify whether SPY is benchmark only).
- **Survivorship**: Using **current ETF tickers** avoids classic single-stock delisting bias; remaining issue is **synthetic history** if Yahoo backfills are revised—pin download timestamp in submission.
- **Alternative public data**: **`arch.data.sp500`** bundled dataset for method debugging only (not sector portfolio) — [arch docs use `arch.data.sp500`](https://arch.readthedocs.io/en/stable/univariate/univariate_volatility_forecasting.html)

### Gaps
- **yfinance license/terms**: Open-source **MIT** library but **Yahoo data is not a guaranteed API**; no vendor SLA for competition reproducibility — [yfinance GitHub](https://github.com/ranaroussi/yfinance/issues/1749)
- Exact **first valid Yahoo bar** per ticker should be verified at runtime (SSGA dates are authoritative for inception).

---

## Train/test split, Monte Carlo size, numerical stability

### Takeaway
Use a **published-style split**: long **in-sample / estimation** window (e.g. 10–15 years daily), **OOS backtest** on the most recent **1–3 years** or crisis windows; inside OOS, **rolling** estimation (250–750 days) for GARCH+copula refit at **weekly or monthly** frequency to stay overnight-runnable. Monte Carlo **10,000–50,000** paths usually stabilizes 95% VaR; **100,000+** for 99% ES tail; fix **`numpy` RNG seed** and use **`float64`**.

### Cited Findings
- Copula–GARCH portfolio study: estimation **2014–2021**, OOS **2022 / 2023 / 2024** regimes — [Frontiers copula-GARCH](https://www.frontiersin.org/journals/applied-mathematics-and-statistics/articles/10.3389/fams.2025.1675120/full)
- **`arch` bootstrap/simulation forecasts**: default **`simulations=1000`** in low-level forecast API — [arch volatility source](https://arch.readthedocs.io/en/stable/_modules/arch/univariate/volatility.html)
- MC VaR convergence example: **200k** simulations within **0.02** of parametric VaR — [var-lab README](https://github.com/sauloduttra/var-lab)
- MODWT rolling VaR: **rolling window** on reconstructed series after wavelet decomposition — [BRE MODWT–VaR paper](https://periodicos.fgv.br/bre/article/download/77437/78201/175571)
- Oil–FX wavelet–copula–VaR: compare models with **VaR and ES** on equal-weight portfolio — [Physica A abstract](https://www.sciencedirect.com/science/article/abs/pii/S0378437115004513)

### Inferences
- **Suggested competition pipeline**:
  - **Train**: 1999-01-01 → 2019-12-31 (or 2014–2021 analog)
  - **OOS evaluate**: 2020-01-01 → latest (≥500 days post-COVID inclusive)
  - **Rolling refit**: every **20 trading days**, estimation window **750 days** (~3y) for GARCH; copula on same window’s pseudo-observations; MODWT on window (boundary effects at window start—prefer **expanding** MODWT on full history then slice MRA components if runtime allows)
- **MC VaR/ES (1-day horizon)**:
  - Simulate **joint uniforms** from fitted copula → **inverse marginal** (t-GARCH or empirical quantile) → build **equal-weight portfolio return** per path
  - **N = 20_000** baseline; **N = 100_000** sensitivity for 99% ES; report whether estimates change < 1 bp
  - **ES_α** = mean of portfolio returns **≤ VaR_α** (loss tail); check **ES ≥ VaR** coherence — [var-lab](https://github.com/sauloduttra/var-lab)
- **Numerical stability**:
  - **`copulae` `scale` parameter** on fit (optimizer sensitivity) — [Gaussian fit docs](https://copulae.readthedocs.io/en/stable/api_reference/copulae/elliptical/gaussian.html)
  - Clip pseudo-observations to **(ε, 1−ε)** with ε ≈ 1e-6 before Clayton/t copula (avoid ∞ density at 0)
  - **`arch`**: use `disp="off"`, `update_freq=5`; if fit fails, fall back to **constant-vol t** marginal for that asset-day
  - MODWT: use **same length** across assets; **demean returns** before transform optional but document
- **Runtime budget (7 assets, laptop overnight)**:
  - Avoid daily **full** vine fit: single **StudentCopula(7)** or **GaussianCopula(7)** + AIC vs Clayton
  - **Parallelize** by date blocks only if needed; bottleneck is **rolling GARCH × 7 × refits**

### Gaps
- No single canonical **rolling window length** for wavelet–copula–VaR papers; FIGARCH + rolling used but window size not surfaced in excerpt — [BRE paper full text search inconclusive in excerpt](https://periodicos.fgv.br/bre/article/download/77437/78201/175571)
- **PyWavelets 1.10.0** PyPI metadata shows **Python ≥3.12** — verify compatibility with your env; older **1.5.x** supports 3.10 — [PyWavelets PyPI](https://pypi.org/project/PyWavelets/)

---

## Licenses, installs, and minimal `requirements.txt` sketch

### Takeaway
Pin **`arch`, `copulae`, `PyWavelets`, `yfinance`, `pandas`, `numpy`, `scipy`, `statsmodels`**; add **`modwtpy`** via GitHub or vendor; treat **`pyvinecopulib`** as optional binary wheel. **`copulae` 0.8** requires **numpy ≥2** — watch conflicts with older stacks.

### Cited Findings
- **arch**: NCSA — [PyPI](https://pypi.org/project/arch/)
- **PyWavelets**: MIT — [PyPI](https://pypi.org/project/PyWavelets/)
- **copulae**: custom MIT-like — [PyPI](https://pypi.org/project/copulae/)
- **pyvinecopulib**: `pip install pyvinecopulib`; source build needs **C++17, Eigen, Boost** — [pyvinecopulib PyPI](https://pypi.org/project/pyvinecopulib/)
- **SDV copulas**: `pip install copulas` — [GitHub Copulas](https://github.com/sdv-dev/Copulas)

### Inferences
- Example install lines for README: `pip install arch copulae PyWavelets yfinance scipy statsmodels pandas numpy` + `pip install git+https://github.com/pistonly/modwtpy.git` (confirm) or submodule `modwt.py`.
- **Conda** alternative: `conda install -c conda-forge arch-py pywavelets copulae` — [arch PyPI conda note](https://pypi.org/project/arch/)

### Gaps
- **`modwtpy` packaging** not verified on PyPI in this research pass — confirm before automating CI.

---

## Academic / GitHub replication anchors (wavelet + copula + VaR)

### Takeaway
Methodological templates: **MODWT/MRA → scale-wise volatility → copula on residuals → portfolio VaR/ES**; code templates split between **copula-only** (`quant-copula-risk`) and **wavelet-only risk bridge** (`wavelet-crypto-risk`), not a single canonical wavelet–copula Python repo.

### Cited Findings
- **MODWT + FIGARCH + rolling VaR + backtests** — [BRE 2020 PDF](https://periodicos.fgv.br/bre/article/download/77437/78201/175571)
- **Wavelet + copula + VaR/ES** (oil–FX portfolio) — [Physica A 2015](https://www.sciencedirect.com/science/article/abs/pii/S0378437115004513)
- **WC-GARCH**: DWT decomposition then **copula–GJR** — [WC-GARCH](https://exa.ai/library/publication/b5tzxxt180k)
- **UFSC thesis**: wavelet decompositions + **GARCH–copula**, VaR and failure proportion — [UFSC repository](https://repositorio.ufsc.br/handle/123456789/215678)
- **GitHub**: [quant-copula-risk](https://github.com/zzovcharov/quant-copula-risk), [wavelet-crypto-risk](https://github.com/povarovf-star/wavelet-crypto-risk/blob/main/README.md) (SWT scale VaR, not copula), [copula-portfolio-simulation](https://github.com/simonedisabella/copula-portfolio-simulation) (Gaussian copula MC)

### Inferences
- Competition narrative can cite **BRE 2020** for MODWT shift-invariance and **Physica A 2015** for wavelet–copula–VaR/ES workflow without claiming identical specification.
- **Equal-weight sector basket** aligns with [quant-copula-risk](https://github.com/zzovcharov/quant-copula-risk) ticker choice (partial overlap).

### Gaps
- **No peer-reviewed paper found** with public Python appendix matching **MODWT + Clayton/t/Gaussian AIC + sector SPDR equal-weight** exactly; expect to document defensible deviations.

---

## End-to-end reproducible workflow (checklist)

1. **Download**: `yf.download(tickers, start="1999-01-01", auto_adjust=True, progress=False)` → daily adjusted close.
2. **Panel**: inner-join dates; log returns; drop NaNs.
3. **MODWT/MRA** per asset (db2, level J); optionally sum bands → 3 series per asset or model **full portfolio return** per band via equal weights.
4. **GARCH(1,1)-t** per series/band via `arch_model(..., vol="Garch", p=1, q=1, dist="t")`; store standardized residuals.
5. **Copula**: map to **U(0,1)**; fit Clayton, Gaussian, Student; pick min **AIC**; record tail λ formulas.
6. **MC**: simulate **U**, invert margins, portfolio return; **VaR/ES** at 95% and 99%.
7. **OOS loop**: rolling refit; collect **VaR/ES** forecasts.
8. **Backtest**: Kupiec, Christoffersen IND, LR-CC; McNeil–Frey bootstrap on ES for violation days.
9. **Artifacts**: frozen CSV of prices, `requirements.txt`, random seed, run timestamp.

---

*Research compiled for report synthesis; all factual claims above carry inline source URLs per assignment spec.*
