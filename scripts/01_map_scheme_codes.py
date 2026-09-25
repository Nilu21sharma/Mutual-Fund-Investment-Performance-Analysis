"""
Step 1 - Map every fund in config/fund_universe.csv to its official AMFI scheme code.

Source: AMFI scheme master, served as JSON by https://api.mfapi.in/mf
Only "Direct Plan - Growth" variants are considered (same as the case study).
Output : config/fund_universe.csv (adds scheme_code + amfi_scheme_name columns)
"""
import csv
import re
from difflib import SequenceMatcher
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
UNIVERSE = ROOT / "config" / "fund_universe.csv"
MASTER_URL = "https://api.mfapi.in/mf"

# Names that were renamed by the AMC and can't be matched by similarity alone
MANUAL_CODES = {
    "HDFC Top 100 Fund - Direct Plan - Growth": 119018,                        # now HDFC Large Cap Fund
    "Bandhan Core Equity Fund - Direct Plan - Growth": 118419,                 # now Bandhan Large & Mid Cap Fund
    "Sundaram Consumption Fund - Direct Plan - Growth": 119595,
    "Bandhan Sterling Value Fund - Direct Plan - Growth": 118481,              # now Bandhan Value Fund
    "Sundaram Focused Fund - Direct Plan - Growth": 149533,                    # ex Principal Focused Multicap
    "HDFC Mid-Cap Opportunities Fund - Direct Plan - Growth": 118989,          # now HDFC Mid Cap Fund
    "Tata Focused Equity Fund - Direct Plan - Growth": 147757,                 # now Tata Focused Fund
    "SBI Long Term Equity Fund - Direct Plan - Growth": 119723,                # now SBI ELSS Tax Saver Fund
    "Axis Growth Opportunities Fund - Direct Plan - Growth": 145110,           # now Axis Large & Mid Cap Fund
    "Franklin India Smaller Companies Fund - Direct - Growth": 118525,         # now Franklin India Small Cap Fund
    "Aditya Birla Sun Life India GenNext Fund - Direct Plan - Growth": 119591, # now ABSL Consumption Fund
    "ICICI Prudential Bluechip Fund - Direct Plan - Growth": 120586,           # now ICICI Pru Large Cap Fund
    "Motilal Oswal Midcap Fund - Direct Plan - Growth": 127042,                # ISIN INF247L01445
    "Nippon India Growth Fund - Direct Plan - Growth": 118668,                 # now Nippon India Growth Mid Cap
    "Invesco India ESG Equity Fund - Direct Plan - Growth": 148751,            # now ESG Integration Strategy
    "ICICI Prudential Focused Equity Fund - Direct Plan - Growth": 120722,
    "HDFC Focused 30 Fund - Direct Plan - Growth": 118950,                     # now HDFC Focused Fund
}

NOISE = r"\b(direct|plan|growth|option|fund|the|scheme|regular)\b|[^a-z0-9 ]"


def normalize(name: str) -> str:
    name = name.lower().replace("&", " and ").replace("largecap", "large cap") \
        .replace("midcap", "mid cap").replace("smallcap", "small cap").replace("multicap", "multi cap")
    return re.sub(r"\s+", " ", re.sub(NOISE, " ", name)).strip()


def is_direct_growth(name: str) -> bool:
    n = name.lower()
    bad = ("idcw", "dividend", "bonus", "payout", "reinvest", "regular", "segregated")
    return "direct" in n and "growth" in n and not any(b in n for b in bad)


def main():
    full_master = requests.get(MASTER_URL, timeout=60).json()
    master = [s for s in full_master if is_direct_growth(s["schemeName"])]
    master_norm = [(s, normalize(s["schemeName"])) for s in master]

    with UNIVERSE.open(encoding="utf-8") as f:
        funds = list(csv.DictReader(f))

    for fund in funds:
        name = fund["scheme_name"]
        if name in MANUAL_CODES:
            code = MANUAL_CODES[name]
            hit = next(s for s in full_master if s["schemeCode"] == code)
            score = 1.0
        else:
            target = normalize(name)
            amc = target.split()[0]
            candidates = [(s, n) for s, n in master_norm if n.split()[0] == amc] or master_norm
            hit, score = max(((s, SequenceMatcher(None, target, n).ratio()) for s, n in candidates),
                             key=lambda t: t[1])
        fund["scheme_code"] = hit["schemeCode"]
        fund["amfi_scheme_name"] = hit["schemeName"]
        fund["match_score"] = round(score, 3)
        flag = "  <-- CHECK" if score < 0.85 else ""
        print(f"{score:.2f}  {name}  =>  {hit['schemeName']} ({hit['schemeCode']}){flag}")

    with UNIVERSE.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["scheme_name", "category", "scheme_code", "amfi_scheme_name", "match_score"])
        w.writeheader()
        w.writerows(funds)


if __name__ == "__main__":
    main()
