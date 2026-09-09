"""
Run AFTER recategorise.py.

Summarises results.csv so you can tell at a glance whether the run landed,
and lists anything needing a second look.

Usage
    python verify.py
"""

import os
import sys

import pandas as pd

RESULTS_FILE = "results.csv"

if not os.path.exists(RESULTS_FILE):
    sys.exit(f"{RESULTS_FILE} not found - run recategorise.py first.")

df = pd.read_csv(RESULTS_FILE)
for col in ("getStatus", "putStatus"):
    if col in df.columns:
        df[col] = df[col].fillna("").astype(str)

MEANING = {
    "200": "OK",
    "204": "OK (no content)",
    "400": "bad request - check the payload",
    "401": "token invalid or expired",
    "403": "token lacks permission, or wrong org",
    "404": "record not found on this tenant",
    "429": "rate limited",
    "": "not attempted (the GET failed first)",
}

print("=" * 66)
print(f"  total records attempted : {len(df)}")
print("=" * 66)

print("\n  GET (reading the record):")
for code, n in df["getStatus"].value_counts().items():
    print(f"    {str(code):<8}{n:>5}   {MEANING.get(str(code), '')}")

print("\n  PUT (writing it back):")
for code, n in df["putStatus"].value_counts().items():
    print(f"    {str(code):<8}{n:>5}   {MEANING.get(str(code), '')}")

good = df[df["putStatus"].isin(["200", "204"])]
bad = df[~df["putStatus"].isin(["200", "204"])]

if len(bad):
    print(f"\n  {len(bad)} did not succeed:\n")
    for _, r in bad.head(10).iterrows():
        print(f"    {str(r['cookieName'])[:22]:<24}{str(r['website'])[:28]:<30}"
              f"get={r['getStatus']} put={r['putStatus']}")
        print(f"      {str(r['response'])[:100]}")
    if len(bad) > 10:
        print(f"    ... and {len(bad) - 10} more - see {RESULTS_FILE}")

if len(good):
    print(f"\n  changes applied, by target category:")
    for cat, n in good["to"].value_counts().items():
        print(f"    {cat:<24}{n:>5}")

print("\n" + "=" * 66)
if len(bad) == 0:
    print("  All updates succeeded.")
    print("  Next: spot-check a cookie in the UAT UI, then republish.")
else:
    print(f"  {len(good)}/{len(df)} succeeded.")
    print("  Fix the cause and re-run - re-running is safe, setting a")
    print("  category to the value it already has does no harm.")
print("=" * 66)
