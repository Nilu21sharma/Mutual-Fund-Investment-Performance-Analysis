"""
Step 2 - Download the last 5 years of daily NAV for every fund in config/fund_universe.csv.

Source : AMFI NAV history, via https://api.mfapi.in/mf/<scheme_code>
Window : 5 years back from the run date (e.g. 2021-09-25 -> 2026-09-25)
Output :
    data/raw/nav_history.csv     fact table   (scheme_code, date, nav)
    data/raw/scheme_master.csv   fund details (fund universe + NAV date range, record count, latest NAV)
"""
import csv
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
UNIVERSE = ROOT / "config" / "fund_universe.csv"
RAW = ROOT / "data" / "raw"
API = "https://api.mfapi.in/mf/{}"
YEARS = 5
WORKERS = 6
ACTIVE_WITHIN_DAYS = 15

END = date.today()
try:
    START = END.replace(year=END.year - YEARS)
except ValueError:                      # 29 Feb
    START = END.replace(year=END.year - YEARS, day=28)


def fetch(code, retries=4):
    for attempt in range(retries):
        try:
            r = requests.get(API.format(code), timeout=(15, 90))
            r.raise_for_status()
            return r.json()
        except (requests.RequestException, ValueError):
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)


def download(fund):
    payload = fetch(fund["scheme_code"])
    navs = []
    for d in payload.get("data", []):
        day = datetime.strptime(d["date"], "%d-%m-%Y").date()
        nav = float(d["nav"])
        if START <= day <= END and nav > 0:          # zero NAVs appear after a scheme is wound up
            navs.append((day.isoformat(), nav))
    navs.sort()
    return fund, navs


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    with UNIVERSE.open(encoding="utf-8") as f:
        funds = list(csv.DictReader(f))
    print(f"Downloading {len(funds)} funds, NAVs from {START} to {END} ...")

    results, failed = {}, []
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(download, f): f for f in funds}
        for i, fut in enumerate(as_completed(futures), 1):
            fund = futures[fut]
            try:
                _, navs = fut.result()
                results[fund["scheme_code"]] = navs
            except Exception as e:
                failed.append(fund["scheme_code"])
                print(f"  FAILED {fund['scheme_code']} {fund['scheme_name']}: {e}")
            if i % 100 == 0:
                print(f"  {i}/{len(funds)} done")

    master_rows, nav_rows = [], 0
    with (RAW / "nav_history.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["scheme_code", "date", "nav"])
        for fund in funds:                                  # keep universe order
            navs = results.get(fund["scheme_code"])
            if not navs:
                continue
            w.writerows((fund["scheme_code"], d, n) for d, n in navs)
            nav_rows += len(navs)
            master_rows.append({
                **fund,
                "first_nav_date": navs[0][0],
                "last_nav_date": navs[-1][0],
                "nav_records": len(navs),
                "latest_nav": navs[-1][1],
                # merged / wound-up schemes stay in AMFI's list but stop publishing NAVs
                "status": "Active" if (END - date.fromisoformat(navs[-1][0])).days <= ACTIVE_WITHIN_DAYS
                else "Inactive",
            })

    with (RAW / "scheme_master.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(master_rows[0]))
        w.writeheader()
        w.writerows(master_rows)

    no_data = [f["scheme_code"] for f in funds if f["scheme_code"] in results and not results[f["scheme_code"]]]
    print(f"\nDone: {len(master_rows)} funds, {nav_rows:,} NAV records -> {RAW}")
    if no_data:
        print(f"No NAV inside the window (skipped): {no_data}")
    if failed:
        print(f"Download failed (re-run to retry): {failed}")


if __name__ == "__main__":
    main()
