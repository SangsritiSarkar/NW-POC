"""
Step 1 of 2 - discover the internal category GUIDs for this tenant.

The Tracking Technologies API does NOT use C0001 / C0003 / C0004.
It uses internal GUIDs, e.g.
    Advertising Cookies -> 990002ff-ee5b-4f0e-93cf-62da7286cde0

Those GUIDs are tenant-specific, so they have to be read from your tenant.
This script reads the CURRENT category of cookies already sitting in each
target purpose, and reports the GUID it finds.

Read-only: sends GET requests only. Nothing is modified.

Usage
    export OT_HOSTNAME="uat.onetrust.com"
    export OT_TOKEN="your-key"
    python get_category_ids.py
"""

import os
import sys
import json
import time

import pandas as pd
import requests

PLAN_FILE = "UAT_recategorisation_plan.xlsx"

HOSTNAME = os.environ.get("OT_HOSTNAME", "uat.onetrust.com")
TOKEN    = os.environ.get("OT_TOKEN", "")

if not TOKEN:
    sys.exit("ERROR: OT_TOKEN not set.")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json",
}

WANTED = ["Required Cookies", "Functional Cookies", "Advertising Cookies"]


def detail_url(record_id):
    return (f"https://{HOSTNAME}/api/cookiemanager/v1/tracking-technologies/"
            f"{record_id}/language/en/instance-details?countryCode=null&type=COOKIE")


df = pd.read_excel(PLAN_FILE)

print("=" * 70)
print("  Reading category GUIDs from cookies already in each purpose")
print("=" * 70 + "\n")

found = {}

for purpose in WANTED:
    # Cookies whose CURRENT purpose is this one - read their categoryId.
    sample = df[df["Current Purpose"].astype(str).str.strip() == purpose]
    if sample.empty:
        print(f"  {purpose:<24} no cookie currently in this purpose - skipping")
        continue

    for _, row in sample.head(3).iterrows():
        rid = str(row["ID"])
        try:
            r = requests.get(detail_url(rid), headers=HEADERS, timeout=30)
            if r.status_code != 200:
                print(f"  {purpose:<24} {r.status_code} on {rid[:8]}...")
                continue
            data = r.json()
            cid = data.get("categoryId")
            if cid:
                found[purpose] = cid
                print(f"  {purpose:<24} {cid}")
                print(f"      (from {row['Technology']} on {row['Website or app']})")
                break
        except Exception as e:
            print(f"  {purpose:<24} ERROR {str(e)[:60]}")
        time.sleep(0.3)
    print()

print("=" * 70)
if len(found) == len(WANTED):
    print("  All three found. Paste this into recategorise.py -> CATEGORY_GUIDS:\n")
    print("CATEGORY_GUIDS = {")
    for k, v in found.items():
        print(f'    "{k}": "{v}",')
    print("}")
    with open("category_guids.json", "w") as fh:
        json.dump(found, fh, indent=2)
    print("\n  Also saved to category_guids.json (the script reads this "
          "automatically).")
else:
    missing = [p for p in WANTED if p not in found]
    print(f"  Could not find: {missing}")
    print("\n  Get them manually: open a cookie already in that purpose in the")
    print("  UI, F12 -> Network -> Edit settings -> Save, and read categoryId")
    print("  from the Payload tab.")
print("=" * 70)
