# Case Study: Mutual Fund Investment Performance Analysis

## 1. Background

India's mutual fund industry has grown rapidly. Investors can now choose from more than a thousand open-ended schemes across **Equity, Debt and Hybrid** asset classes, each divided into SEBI-defined categories such as Large Cap, Small Cap, Liquid, Gilt, Arbitrage and Balanced Advantage. More choice also makes selection harder. Fund factsheets and screener tables are dense and inconsistent, and they rarely show both **return** and **risk** in one place. As a result, most retail investors fall back on "last year's top performer," which is a poor way to choose a fund.

## 2. Problem Statement

> How can an investor quickly compare mutual funds across asset classes, categories and timeframes, find the consistent performers, and see how much risk each fund takes to deliver its returns?

## 3. Objectives

1. Measure fund performance over standard trailing periods: **1W, 1M, 3M, 6M, YTD, 1Y, 2Y, 3Y, 5Y** (CAGR for periods longer than one year).
2. Compare performance **across asset classes** (Equity vs Debt vs Hybrid) and **within categories** (category averages, best and worst funds, spread).
3. Assess **risk** using NAV-based metrics (annualised volatility, maximum drawdown, Sharpe ratio) and classify funds as **Low / Medium / High Risk**.
4. Find the **top performers** in each category and check whether they stay consistent across timeframes.
5. Build an **interactive dashboard** (Power BI) with slicers for asset class, category, fund house, risk band and timeframe, plus drill-down from asset class to category to fund.

## 4. Scope: Fund Universe

**All open-ended Equity, Debt and Hybrid schemes that AMFI lists, Direct Plan with the Growth option only.** This gives 1,000 funds from every fund house in India.

| Asset Class | Funds | Categories |
|---|---:|---|
| **Equity** | 580 | Sectoral/Thematic (253), Flexi Cap (47), ELSS (39), Large & Mid Cap (36), Large Cap (35), Small Cap (35), Mid Cap (33), Multi Cap (33), Focused (28), Value (24), Dividend Yield (12), Contra (5) |
| **Debt** | 232 | Ultra Short to Short Term (25), Ultra Short Term (23), Short Term (22), Dynamic Term (21), Liquid (18), Banking and PSU Debt (15), Overnight (15), Medium to Long Term (13), Money Market (13), Floating Interest Rates (12), Gilt (12), Medium Term (12), Long Term (11), Corporate Bond (9), 10-year Constant Maturity Gilt (5), Credit Risk (5), Debt Sectoral (1) |
| **Hybrid** | 188 | Arbitrage (39), Multi Asset Allocation (37), Balanced Advantage (36), Aggressive Hybrid (30), Equity Savings (24), Conservative Hybrid (17), Balanced Hybrid (5) |
| **Total** | **1,000** | **36 categories** |

**Why Direct Plan – Growth only?** Every scheme has several variants: Regular or Direct plan, and Growth or IDCW option. They all hold the same portfolio. Keeping one variant per scheme avoids counting the same fund several times. The Growth option also reinvests all gains, so its NAV reflects the fund's true total return.

**Excluded:** index funds, ETFs, fund-of-funds, solution-oriented (retirement/children's) schemes, close-ended and interval schemes, IDCW options, segregated portfolios, and unclaimed-redemption plans.

**Focus list:** the 88 equity funds from this project's original focus list ([config/reference_funds.csv](config/reference_funds.csv)) are all included and flagged with `in_reference_study = Yes`.

## 5. Data Source

| Item | Detail |
|---|---|
| Publisher | **AMFI (Association of Mutual Funds in India)**, the official source of daily NAVs for all Indian mutual funds |
| Fund list | [AMFI NAVAll.txt](https://portal.amfiindia.com/spages/NAVAll.txt) (every active scheme, by category) and the AMFI scheme master (full plan/option name, launch date) |
| NAV history | [mfapi.in](https://www.mfapi.in/), a free public API that serves AMFI's historical NAVs |
| Granularity | Daily NAV per scheme |
| Period | **Last 5 years: 25 Sep 2021 to 25 Sep 2026** |
| Volume | 1,000 schemes, **968,578 NAV records** |

**Why NAV history instead of a screener snapshot?** A screener export is a one-time snapshot with returns already calculated. Downloading the underlying daily NAVs means:

- every return and risk number can be **recalculated and checked**;
- the data can be **refreshed at any time** by re-running the scripts;
- risk can be measured properly (volatility, drawdown, Sharpe) rather than with a rule of thumb.

## 6. Raw Datasets (in `data/raw/`)

### `scheme_master.csv`: dimension table, one row per fund
| Column | Description |
|---|---|
| scheme_code | AMFI scheme code (primary key) |
| scheme_name | Scheme name |
| scheme_nav_name | Full AMFI name including plan and option |
| fund_house | Asset Management Company (AMC) |
| asset_class | Equity / Debt / Hybrid |
| category | Cleaned SEBI category (36 values, see §4) |
| amfi_category | Category label exactly as AMFI publishes it |
| launch_date | Scheme launch date (AMFI scheme master) |
| isin_growth | ISIN of the Direct-Growth option |
| in_reference_study | Yes if the fund is on the 88-fund equity focus list |
| first_nav_date, last_nav_date | First and last NAV dates within the 5-year window |
| nav_records | Number of daily NAV rows |
| latest_nav | NAV on `last_nav_date` |
| status | **Active**, or **Inactive** if the fund stopped publishing NAVs (merged or wound up) |

### `nav_history.csv`: fact table, one row per fund per NAV date
| Column | Description |
|---|---|
| scheme_code | Foreign key to `scheme_master` |
| date | NAV date (ISO `YYYY-MM-DD`) |
| nav | Net Asset Value (₹) |

The two tables join on `scheme_code` in a star schema. Add a Date table in Power BI for time intelligence.

## 7. Data Notes & Limitations

- **Short histories:** only 595 of the 1,000 funds have the full 5 years of data. The rest were launched after Sep 2021 (`launch_date` shows when). Their 3Y and 5Y returns must be treated as **not available**, not as zero.
- **Inactive funds:** 6 funds stopped publishing NAVs during the window, for example *HDFC Long Term Advantage*, *Tata Quant* and *Navi ELSS Tax Saver*. They are marked `status = Inactive`. Include them for history, or exclude them for "investable today" views.
- **Unit split:** *UTI Liquid Fund* (scheme 120304) changed its face value on 20 Jun 2026. Its NAV falls by exactly 10× (₹4,589 → ₹459) in one day. This is not a loss, so returns spanning that date must be adjusted (multiply NAVs from 20 Jun 2026 onwards by 10).
- **NAV frequency differs:** Liquid and Overnight funds publish a NAV every calendar day; other funds publish only on business days. Trailing returns should use the latest NAV **on or before** the start date.
- **Last NAV date:** a few active funds have their latest NAV one business day earlier than others. This is normal publication lag. Use a common as-of date when calculating returns.
- **Renamed schemes:** many of the 88 focus-list funds have been renamed since the list was made (for example *HDFC Top 100 → HDFC Large Cap Fund*). The data always uses the current AMFI name.
- **Not included:** AUM, expense ratio and CRISIL rank are not in the AMFI NAV feed. Monthly AUM can be added later from AMFI's AUM reports if needed.

## 8. Planned Analysis (next steps)

1. **Data preparation:** clean types, adjust the UTI Liquid unit split, choose how to treat inactive funds, and align to a common as-of date.
2. **Return metrics:** absolute returns for 1W–1Y and YTD; CAGR for 2Y, 3Y and 5Y.
3. **Risk metrics:** annualised volatility (std. dev. of daily returns × √252), maximum drawdown, and Sharpe ratio (risk-free rate ≈ 6.5%).
4. **Risk classification:** Low / Medium / High, based on volatility and drawdown percentiles **within each asset class**, since debt and equity risk levels are not comparable.
5. **Power BI dashboard:**
   - *Overview:* KPI cards (funds, fund houses, average 1Y/3Y/5Y return) and return by asset class and category.
   - *Performance:* matrix of fund × timeframe with conditional formatting, and top/bottom 10 funds per category.
   - *Risk vs Return:* scatter plot of 3Y CAGR against volatility, coloured by asset class, and the distribution of risk bands.
   - *Fund Deep-Dive:* NAV trend, drawdown chart and rolling returns for the selected fund.
6. **Insights & recommendations:** consistent outperformers, categories with the best risk-adjusted returns, Equity vs Debt vs Hybrid trade-offs, and funds with high risk but weak returns.

## 9. Expected Outcomes

- A clean, refreshable dataset of 1,000 funds with returns and risk metrics.
- An interactive Power BI dashboard for comparing funds across asset classes, categories and timeframes.
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
