# Case Study: Mutual Fund Investment Performance Analysis

## 1. Background

India's mutual fund industry has grown rapidly. Investors can now choose from hundreds of equity schemes in categories such as ELSS, Flexi Cap, Large Cap, Mid Cap, Small Cap, Value and Sectoral/Thematic funds. More choice also makes selection harder. Fund factsheets and screener tables are dense and inconsistent, and they rarely show both **return** and **risk** in one place. As a result, most retail investors fall back on "last year's top performer," which is a poor way to choose a fund.

## 2. Problem Statement

> How can an investor quickly compare equity mutual funds across categories and timeframes, find the consistent performers, and see how much risk each fund takes to deliver its returns?

## 3. Objectives

1. Measure fund performance over standard trailing periods: **1W, 1M, 3M, 6M, YTD, 1Y, 2Y, 3Y, 5Y, 10Y** (CAGR for periods longer than one year).
2. Compare performance **within and across categories** (category averages, best and worst funds, spread).
3. Assess **risk** using NAV-based metrics (annualised volatility, maximum drawdown, Sharpe ratio) and classify funds as **Low / Medium / High Risk**.
4. Find the **top performers** and check whether they stay consistent across timeframes.
5. Build an **interactive dashboard** (Power BI) with slicers for category, fund house, risk band and timeframe, plus drill-down from category to fund.

## 4. Scope: Fund Universe

The study covers **88 open-ended equity mutual funds** (Direct Plan, Growth option) from **11 categories**.

| Category | Funds |
|---|---:|
| Sectoral/Thematic | 15 |
| ELSS | 12 |
| Large & Mid Cap | 11 |
| Mid Cap | 9 |
| Small Cap | 9 |
| Large Cap | 8 |
| Focused | 7 |
| Flexi Cap | 6 |
| Value | 5 |
| Multi Cap | 4 |
| Contra | 2 |
| **Total** | **88** |

The full list, with official AMFI scheme codes, is in [config/fund_universe.csv](config/fund_universe.csv).

## 5. Data Source

| Item | Detail |
|---|---|
| Publisher | **AMFI (Association of Mutual Funds in India)**, the official source of daily NAVs for all Indian mutual funds |
| Access | [mfapi.in](https://www.mfapi.in/), a free public JSON API that serves AMFI's scheme master and full NAV history |
| Granularity | Daily NAV per scheme |
| Coverage | January 2013 (when Direct plans started) to **25 Sep 2026** (download date) |
| Volume | 88 schemes, **251,688 NAV records** |

**Why NAV history instead of a screener snapshot?** The reference project used a one-time export from a fund screener, with returns already calculated. Downloading the underlying daily NAVs means:

- every return and risk number can be **recalculated and checked**;
- the data can be **refreshed at any time** by re-running the scripts;
- risk can be measured properly (volatility, drawdown, Sharpe) rather than with a rule of thumb.

## 6. Raw Datasets (in `data/raw/`)

### `scheme_master.csv`: one row per fund
| Column | Description |
|---|---|
| scheme_code | AMFI scheme code (primary key) |
| scheme_name | Fund name as used in this study |
| amfi_scheme_name | Current official name registered with AMFI |
| category | Study category (11 groups, see §4) |
| amfi_category | SEBI/AMFI category label |
| fund_house | Asset Management Company (AMC) |
| scheme_type | Open / close-ended |
| plan, option | Always Direct / Growth |
| isin_growth | ISIN of the growth option |
| first_nav_date, last_nav_date | Date range of available NAV history |
| nav_records | Number of daily NAV rows |
| latest_nav | NAV on `last_nav_date` |

### `nav_history_all.csv`: fact table, one row per fund per trading day
| Column | Description |
|---|---|
| scheme_code | Foreign key to `scheme_master` |
| date | NAV date (ISO `YYYY-MM-DD`) |
| nav | Net Asset Value (₹) |

### `nav/<scheme_code>.csv`
The same NAV history split into one file per fund (`date, nav`), for quick inspection.

## 7. Data Notes & Limitations

- **Renamed schemes:** many funds have been renamed since the reference study (for example *HDFC Top 100 → HDFC Large Cap Fund*, *ICICI Pru Bluechip → ICICI Pru Large Cap Fund*, *SBI Long Term Equity → SBI ELSS Tax Saver*). The study keeps the original names in `scheme_name`, and `amfi_scheme_name` holds the current name. 17 funds were mapped to their scheme codes by hand; they are listed with comments in `MANUAL_CODES` in [scripts/01_map_scheme_codes.py](scripts/01_map_scheme_codes.py). Every mapping was checked against AMFI's own category label.
- **Short histories:** some funds were launched recently, or their history under the current scheme code starts after a merger. Examples: *Sundaram Focused* (2022), *HSBC Value* and *HSBC Business Cycles* (Nov 2022), *Invesco India Flexi Cap* (2022). The 5Y and 10Y returns for these funds must be treated as **not available**, not as zero.
- **Last NAV date:** a few funds have their latest NAV on 24 Sep 2026 instead of 25 Sep 2026. This is normal publication lag. Use each fund's own last date, or a common as-of date, when calculating returns.
- **Not included:** AUM and CRISIL rank (both in the reference data) are not in the AMFI NAV feed. CRISIL ranks are proprietary. Monthly AUM can be added later from AMFI's AUM reports if needed.
- **Non-trading days:** NAVs exist only for business days. Trailing returns should use the latest NAV **on or before** the start date.

## 8. Planned Analysis (next steps)

1. **Data preparation:** clean types, remove duplicates, align to a common as-of date.
2. **Return metrics:** absolute returns for 1W–1Y and YTD; CAGR for 2Y, 3Y, 5Y and 10Y.
3. **Risk metrics** (3-year window where available): annualised volatility (std. dev. of daily returns × √252), maximum drawdown, and Sharpe ratio (risk-free rate ≈ 6.5%).
4. **Risk classification:** Low / Medium / High, based on volatility and drawdown percentiles within the universe.
5. **Power BI dashboard:**
   - *Overview:* KPI cards (number of funds, average 1Y/3Y/5Y return, best fund), return by category.
   - *Performance:* matrix of fund × timeframe with conditional formatting, and top/bottom 10 funds.
   - *Risk vs Return:* scatter plot of 3Y CAGR against volatility, and the distribution of risk bands.
   - *Fund Deep-Dive:* NAV trend line, drawdown chart and rolling returns for the selected fund.
6. **Insights & recommendations:** consistent outperformers, categories with the best risk-adjusted returns, and funds with high risk but weak returns.

## 9. Expected Outcomes

- A clean, refreshable dataset of 88 equity funds with returns and risk metrics.
- An interactive Power BI dashboard for comparing funds across categories and timeframes.
- A clear Low / Medium / High risk view to help investors match funds to their risk appetite.
- A short list of consistent top performers in each category.

## 10. Tools

| Tool | Use |
|---|---|
| Python (requests) | Downloading data from AMFI / mfapi.in |
| Excel / Power Query | Cleaning and shaping data |
| Power BI (DAX) | Data model, measures, dashboard |
| Git / GitHub | Version control |

> *Disclaimer: This project is for educational and analytical purposes only and is not investment advice. Past performance does not guarantee future returns.*
