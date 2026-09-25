# Mutual Fund Investment Performance Analysis

An end-to-end analysis of **88 Indian equity mutual funds** (Direct Plan, Growth) across **11 categories**: ELSS, Flexi Cap, Large Cap, Large & Mid Cap, Mid Cap, Small Cap, Multi Cap, Focused, Value, Contra and Sectoral/Thematic. The project measures returns over 1W to 10Y, assesses risk, and presents the results in an interactive Power BI dashboard.

📄 **Full case study:** [CASE_STUDY.md](CASE_STUDY.md)

## Data Source

Daily NAV history comes from **AMFI (Association of Mutual Funds in India)** via the free [mfapi.in](https://www.mfapi.in/) API.

- **Coverage:** Jan 2013 to 25 Sep 2026
- **Volume:** 88 funds, 251,688 daily NAV records

## Project Structure

```
├── CASE_STUDY.md                     # Problem statement, scope, data dictionary, analysis plan
├── config/
│   └── fund_universe.csv             # 88 funds: name, category, AMFI scheme code
├── scripts/
│   ├── 01_map_scheme_codes.py        # Maps fund names to AMFI scheme codes
│   └── 02_download_nav_history.py    # Downloads full daily NAV history
├── data/
│   └── raw/
│       ├── scheme_master.csv         # Fund metadata (AMC, category, ISIN, date range)
│       ├── nav_history_all.csv       # All NAVs: scheme_code, date, nav
│       └── nav/<scheme_code>.csv     # One NAV file per fund
└── requirements.txt
```

## Refresh the Data

```bash
pip install -r requirements.txt
python scripts/01_map_scheme_codes.py      # only needed if config/fund_universe.csv changes
python scripts/02_download_nav_history.py  # re-downloads the latest NAVs
```

## Roadmap

- [x] Define case study and fund universe
- [x] Download raw NAV data from AMFI
- [ ] Data cleaning and return calculation (1W, 1M, 3M, 6M, YTD, 1Y, 2Y, 3Y, 5Y, 10Y)
- [ ] Risk metrics (volatility, max drawdown, Sharpe) and Low / Medium / High classification
- [ ] Power BI dashboard (Overview, Performance, Risk vs Return, Fund Deep-Dive)
- [ ] Insights and recommendations

## Tools

Python · Excel / Power Query · Power BI (DAX) · Git



> *For educational purposes only. Not investment advice.*
