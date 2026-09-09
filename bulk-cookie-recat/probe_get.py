"""
Find the READ endpoint for a tracking technology record.

Why this exists: the URL we captured from the UI works for PUT (saving) but
returns 404 for GET, so it is write-only. Before we can safely update records
we need a way to read one first - that lets us change only the two purpose
fields and put everything else back untouched.

This script tries several likely GET shapes against one real record and
reports which ones your tenant recognises.

Read-only. Sends GET requests only. Nothing is modified.

Usage
    export OT_HOSTNAME="uat.onetrust.com"
    export OT_TOKEN="your-key"
    python probe_get.py
"""

import os
import sys

import pandas as pd
import requests

HOSTNAME = os.environ.get("OT_HOSTNAME", "uat.onetrust.com")
TOKEN = os.environ.get("OT_TOKEN", "")

if not TOKEN:
    sys.exit("ERROR: OT_TOKEN not set.")

# Take a real in-scope record ID from the plan.
df = pd.read_excel("UAT_recategorisation_plan.xlsx")
row = df[df["Change needed"].astype(str).str.upper() == "YES"].iloc[0]
RID = str(row["ID"])

print(f"  probing with: {row['Technology']} on {row['Website or app']}")
print(f"  record id   : {RID}\n")

BASE = f"https://{HOSTNAME}/api/cookiemanager/v1"

CANDIDATES = [
    f"{BASE}/tracking-technologies/{RID}",
    f"{BASE}/tracking-technologies/{RID}?type=COOKIE",
    f"{BASE}/tracking-technologies/{RID}/language/en?type=COOKIE",
    f"{BASE}/tracking-technologies/{RID}/language/en/details?type=COOKIE",
    f"{BASE}/tracking-technologies/{RID}/instance-details?type=COOKIE",
    f"{BASE}/tracking-technologies/{RID}/language/en/instance-details?type=COOKIE",
    f"{BASE}/tracking-technologies/{RID}/language/en/instance-details"
    f"?countryCode=null&type=COOKIE",
    f"{BASE}/tracking-technologies/details/{RID}?type=COOKIE",
]

HEADERS = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/json"}

hits = []
for url in CANDIDATES:
    short = url.replace(f"https://{HOSTNAME}/api/cookiemanager/v1", "")
    try:
        r = requests.get(url, headers=HEADERS, timeout=25)
        print(f"  {r.status_code}   {short}")
        if r.status_code == 200:
            hits.append(url)
            body = r.text
            print(f"        has categoryId: "
                  f"{'YES' if 'categoryId' in body else 'no'}")
            print(f"        {body[:220]}")
    except Exception as e:
        print(f"  ERR   {short}")
        print(f"        {str(e)[:90]}")
    print()

print("=" * 66)
if hits:
    print("  WORKING READ ENDPOINT(S):\n")
    for h in hits:
        print(f"    {h}")
    print("\n  Send me the one that shows categoryId: YES")
else:
    print("  None worked. Capture it from the UI instead:")
    print("    open a cookie detail page -> F12 -> Network -> Fetch/XHR")
    print("    -> refresh the page (F5)")
    print("    -> find the GET whose URL contains 'tracking-technologies'")
    print("    -> send me its Request URL")
print("=" * 66)
