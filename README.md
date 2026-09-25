# Mutual Fund Investment Performance Analysis

An end-to-end analysis of **1,000 Indian mutual funds** (Direct Plan, Growth) across **Equity, Debt and Hybrid** asset classes and **36 SEBI categories**. The project measures returns over 1W to 5Y, assesses risk, and presents the results in an interactive Power BI dashboard.

📄 **Full case study:** [CASE_STUDY.md](CASE_STUDY.md)

## Dataset at a Glance

| Asset Class | Funds | Categories |
|---|---:|---:|
| Equity | 580 | 12 |
| Debt | 232 | 17 |
| Hybrid | 188 | 7 |
| **Total** | **1,000** | **36** |

- **Source:** official AMFI (Association of Mutual Funds in India) data, with NAV history fetched through [mfapi.in](https://www.mfapi.in/)
- **Period:** last 5 years, **25 Sep 2021 to 25 Sep 2026**
- **Volume:** 968,578 daily NAV records

## Project Structure

```
├── CASE_STUDY.md                     # Problem statement, scope, data dictionary, analysis plan
├── config/
│   ├── fund_universe.csv             # All Direct-Growth Equity/Debt/Hybrid schemes (built by script 01)
│   └── reference_funds.csv           # 88-fund equity focus list (flagged in the data)
├── scripts/
│   ├── 01_build_fund_universe.py     # Builds the fund list from AMFI's NAV file and scheme master
│   └── 02_download_nav_history.py    # Downloads the last 5 years of daily NAVs
├── data/
│   └── raw/
│       ├── scheme_master.csv         # 1 row per fund: AMC, asset class, category, launch date, status ...
│       └── nav_history.csv           # 1 row per fund per day: scheme_code, date, nav
└── requirements.txt
```

## Refresh the Data

```bash
pip install -r requirements.txt
python scripts/01_build_fund_universe.py    # rebuilds the fund list from AMFI
python scripts/02_download_nav_history.py   # downloads the last 5 years of NAVs (takes about 3 minutes)
```

## Roadmap

- [x] Define case study and fund universe
- [x] Download raw NAV data from AMFI (Equity, Debt, Hybrid; 5 years)
- [ ] Data cleaning and return calculation (1W, 1M, 3M, 6M, YTD, 1Y, 2Y, 3Y, 5Y)
- [ ] Risk metrics (volatility, max drawdown, Sharpe) and Low / Medium / High classification
- [ ] Power BI dashboard (Overview, Performance, Risk vs Return, Fund Deep-Dive)
- [ ] Insights and recommendations

## Tools

Python · Excel / Power Query · Power BI (DAX) · Git

> *For educational purposes only. Not investment advice.*
