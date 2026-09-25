"""
Step 1 - Build the fund universe from AMFI's official files.

Sources (AMFI - Association of Mutual Funds in India):
    NAVAll.txt              every currently active scheme, grouped by category & fund house
    DownloadSchemeData_Po   scheme master: full NAV name (plan/option), launch date
Filter : Open-ended schemes, asset class Equity / Debt / Hybrid, Direct Plan - Growth option only.
         (Index funds, ETFs, Fund-of-Funds and Solution-oriented schemes are excluded.)
Output : config/fund_universe.csv
"""
import csv
import io
import re
from collections import Counter
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "config" / "fund_universe.csv"
REFERENCE = ROOT / "config" / "reference_funds.csv"
NAV_ALL_URLS = [
    "https://portal.amfiindia.com/spages/NAVAll.txt",
    "https://www.amfiindia.com/spages/NAVAll.txt",
]
SCHEME_MASTER_URL = "https://portal.amfiindia.com/DownloadSchemeData_Po.aspx?mf=0"

# AMFI uses two spellings for the same category ("Equity Scheme - ELSS" vs "Equity Schemes - ELSS- Tax Saver Fund")
CATEGORY_ALIASES = {
    "ELSS- Tax Saver": "ELSS",
    "Sectoral/ Thematic": "Sectoral/Thematic",
    "Sectoral": "Sectoral/Thematic",
    "Thematic": "Sectoral/Thematic",
    "Dynamic Asset Allocation or Balanced Advantage": "Balanced Advantage",
    "Balanced Advantage Fund/ Dynamic Asset Allocation": "Balanced Advantage",
}
NOT_GROWTH = re.compile(r"idcw|dividend(?! yield)|income distribution|bonus|payout|reinvest|segregat|regular|"
                        r"institutional|unclaimed|withheld|brokerage|refund|\bSG ?\d", re.I)


def download(urls) -> str:
    for url in urls:
        try:
            r = requests.get(url, timeout=(20, 180), headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            return r.text
        except requests.RequestException as e:
            print(f"Could not reach {url}: {e.__class__.__name__}")
    raise SystemExit("AMFI file unavailable - try again later.")


def asset_class(amfi_category: str):
    if re.match(r"Equity Schemes? -", amfi_category):
        return "Equity"
    if amfi_category.startswith("Income/Debt Oriented Schemes -"):
        return "Debt"
    if re.match(r"Hybrid Schemes? -", amfi_category):
        return "Hybrid"
    return None


def clean_category(amfi_category: str, asset: str) -> str:
    sub = re.sub(r"\s*Fund$", "", amfi_category.split(" - ", 1)[1].strip())
    sub = CATEGORY_ALIASES.get(sub, sub)
    return "Debt Sectoral" if asset == "Debt" and sub == "Sectoral/Thematic" else sub


def is_direct_growth(text: str) -> bool:
    t = text.lower()
    return "direct" in t and "growth" in t and not NOT_GROWTH.search(text)


def load_scheme_master() -> dict:
    """scheme_code -> {nav_name, launch_date} from AMFI's scheme master."""
    rows = csv.DictReader(io.StringIO(download([SCHEME_MASTER_URL])))
    return {r["Code"].strip(): {"nav_name": (r.get("Scheme NAV Name") or "").strip(),
                                "launch_date": (r.get("Launch Date") or "").strip()} for r in rows}


def main():
    nav_all = download(NAV_ALL_URLS)
    master = load_scheme_master()
    reference_codes = set()
    if REFERENCE.exists():
        with REFERENCE.open(encoding="utf-8") as f:
            reference_codes = {r["scheme_code"] for r in csv.DictReader(f)}

    funds, seen = [], set()
    amfi_category = fund_house = None
    for raw in nav_all.splitlines():
        line = raw.strip()
        if not line or line.startswith("Scheme Code"):
            continue
        header = re.match(r"(Open Ended|Close Ended|Interval Fund) Schemes?\s*\((.*)\)$", line)
        if header:
            amfi_category = header.group(2).strip() if header.group(1) == "Open Ended" else None
            continue
        parts = [p.strip() for p in line.split(";")]
        if len(parts) < 8:
            fund_house = line            # fund house (AMC) name line
            continue
        if not amfi_category or not parts[0].isdigit():
            continue
        code, isin, isin_reinvest, name, plan, option, nav, nav_date = parts[:8]
        asset = asset_class(amfi_category)
        if not asset or code in seen:
            continue
        # NAVAll's Plan/Option columns are blank for some AMCs and occasionally mislabel IDCW plans as
        # "Growth", so the scheme master's full NAV name is used first. A Growth option never has a
        # dividend-reinvestment ISIN.
        nav_name = master.get(code, {}).get("nav_name", "")
        label = nav_name or f"{plan} {option} {name}"
        if not is_direct_growth(label) or isin_reinvest not in ("-", ""):
            continue
        seen.add(code)
        funds.append({
            "scheme_code": code,
            "scheme_name": name,
            "scheme_nav_name": nav_name,
            "fund_house": fund_house,
            "asset_class": asset,
            "category": clean_category(amfi_category, asset),
            "amfi_category": amfi_category,
            "launch_date": master.get(code, {}).get("launch_date", ""),
            "isin_growth": isin if isin not in ("-", "") else "",
            "in_reference_study": "Yes" if code in reference_codes else "No",
        })

    funds.sort(key=lambda r: (r["asset_class"], r["category"], r["scheme_name"].lower()))
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(funds[0]))
        w.writeheader()
        w.writerows(funds)

    for (asset, cat), n in sorted(Counter((r["asset_class"], r["category"]) for r in funds).items()):
        print(f"{asset:<7} {cat:<35} {n:>4}")
    print(Counter(r["asset_class"] for r in funds))
    print(f"\nTotal: {len(funds)} schemes -> {OUT}  "
          f"(reference funds found: {sum(r['in_reference_study'] == 'Yes' for r in funds)}/{len(reference_codes)})")


if __name__ == "__main__":
    main()
