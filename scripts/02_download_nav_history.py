"""
Step 2 - Download the full daily NAV history of every fund in config/fund_universe.csv.

Source : AMFI (Association of Mutual Funds in India) NAV data, via https://api.mfapi.in/mf/<scheme_code>
Output :
    data/raw/nav/<scheme_code>.csv     one file per fund  (date, nav)
    data/raw/nav_history_all.csv       all funds stacked  (scheme_code, date, nav)
    data/raw/scheme_master.csv         fund metadata      (AMC, AMFI category, ISIN, date range ...)
"""
import csv
import time
from datetime import datetime
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
UNIVERSE = ROOT / "config" / "fund_universe.csv"
RAW = ROOT / "data" / "raw"
NAV_DIR = RAW / "nav"
API = "https://api.mfapi.in/mf/{}"


def fetch(code, retries=3):
    for attempt in range(retries):
        try:
            r = requests.get(API.format(code), timeout=60)
            r.raise_for_status()
            return r.json()
        except requests.RequestException:
            if attempt == retries - 1:
                raise
            time.sleep(2 * (attempt + 1))


def main():
    NAV_DIR.mkdir(parents=True, exist_ok=True)
    with UNIVERSE.open(encoding="utf-8") as f:
        funds = list(csv.DictReader(f))

    master_rows, all_rows = [], []
    for i, fund in enumerate(funds, 1):
        code = fund["scheme_code"]
        payload = fetch(code)
        meta = payload["meta"]
        # API returns newest first, dd-mm-yyyy -> store oldest first, ISO dates
        navs = sorted(
            (datetime.strptime(d["date"], "%d-%m-%Y").date().isoformat(), float(d["nav"]))
            for d in payload["data"]
        )

        with (NAV_DIR / f"{code}.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["date", "nav"])
            w.writerows(navs)
        all_rows.extend((code, d, n) for d, n in navs)

        master_rows.append({
            "scheme_code": code,
            "scheme_name": fund["scheme_name"],
            "amfi_scheme_name": meta["scheme_name"],
            "category": fund["category"],
            "amfi_category": meta["scheme_category"],
            "fund_house": meta["fund_house"],
            "scheme_type": meta["scheme_type"],
            "plan": "Direct",
            "option": "Growth",
            "isin_growth": meta.get("isin_growth") or "",
            "first_nav_date": navs[0][0],
            "last_nav_date": navs[-1][0],
            "nav_records": len(navs),
            "latest_nav": navs[-1][1],
        })
        print(f"[{i:>2}/{len(funds)}] {code}  {len(navs):>5} rows  {navs[0][0]} -> {navs[-1][0]}  {fund['scheme_name']}")
        time.sleep(0.3)  # be polite to the free API

    with (RAW / "scheme_master.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(master_rows[0]))
        w.writeheader()
        w.writerows(master_rows)

    with (RAW / "nav_history_all.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["scheme_code", "date", "nav"])
        w.writerows(all_rows)

    print(f"\nDone: {len(master_rows)} funds, {len(all_rows):,} NAV records -> {RAW}")


if __name__ == "__main__":
    main()
