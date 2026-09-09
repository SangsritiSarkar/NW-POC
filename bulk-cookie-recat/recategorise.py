"""
OneTrust UAT - bulk cookie re-categorisation (Tracking Technologies API).

Endpoint captured from the OneTrust UI itself:
    PUT https://{host}/api/cookiemanager/v1/tracking-technologies
        /{recordId}/language/en/instance-details?countryCode=null&type=COOKIE

Two things this API requires that the older cookies API did not:
  * categoryId is an internal GUID, NOT C0001/C0003/C0004
  * isInheritingGlobalPurpose must be set to false, otherwise the record
    falls back to the global purpose and your change does not stick

Safety design: for each record we GET the current instance-details, change
ONLY categoryId and isInheritingGlobalPurpose, then PUT the whole object
back. Every other field - description, provenance, status, owners,
vendorServiceId - is preserved exactly as it was.

Usage
    python get_category_ids.py          # once, to discover the GUIDs
    python recategorise.py --dry-run    # preview, sends no writes
    python recategorise.py              # apply
"""

import os
import sys
import csv
import json
import time
import argparse

import pandas as pd
import requests

# ---------------------------------------------------------------- settings --
PLAN_FILE    = "UAT_recategorisation_plan.xlsx"
GUID_FILE    = "category_guids.json"
RESULTS_FILE = "results.csv"

HOSTNAME = os.environ.get("OT_HOSTNAME", "uat.onetrust.com")
TOKEN    = os.environ.get("OT_TOKEN", "")

BASE = f"https://{HOSTNAME}/api/cookiemanager/v1/tracking-technologies"

# Filled by get_category_ids.py, or paste them here manually.
CATEGORY_GUIDS = {
    "Required Cookies":    "",
    "Functional Cookies":  "",
    "Advertising Cookies": "",
}

PAUSE_SECONDS = 0.3


# ------------------------------------------------------------------ helpers --
def instance_url(record_id):
    return (f"{BASE}/{record_id}/language/en/instance-details"
            f"?countryCode=null&type=COOKIE")


def load_guids():
    """Prefer category_guids.json if get_category_ids.py produced one."""
    guids = dict(CATEGORY_GUIDS)
    if os.path.exists(GUID_FILE):
        with open(GUID_FILE) as fh:
            guids.update(json.load(fh))
        print(f"  loaded category GUIDs from {GUID_FILE}")
    missing = [k for k, v in guids.items() if not v]
    if missing:
        sys.exit(f"\nERROR: no category GUID for: {missing}\n"
                 f"Run  python get_category_ids.py  first.")
    return guids


def main(dry_run):
    if not os.path.exists(PLAN_FILE):
        sys.exit(f"ERROR: {PLAN_FILE} not found.")
    if not TOKEN:
        sys.exit("ERROR: OT_TOKEN not set.  export OT_TOKEN='your-key'")

    df = pd.read_excel(PLAN_FILE)
    todo = df[df["Change needed"].astype(str).str.upper() == "YES"]
    guids = load_guids()

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    print("=" * 68)
    print(f"  plan rows          : {len(df)}")
    print(f"  updates to send    : {len(todo)}")
    print(f"  tenant             : {HOSTNAME}")
    print(f"  method             : GET current -> patch 2 fields -> PUT back")
    print("=" * 68)
    print("\n  category GUIDs in use:")
    for k, v in guids.items():
        print(f"    {k:<22}{v}")

    if dry_run:
        print(f"\n  DRY RUN - reading {min(3, len(todo))} records to prove the "
              f"endpoint works. No writes.\n")
        for _, r in todo.head(3).iterrows():
            rid = str(r["ID"])
            try:
                resp = requests.get(instance_url(rid), headers=headers, timeout=30)
                print(f"    GET {r['Technology']:<24}{r['Website or app']:<34}"
                      f"{resp.status_code}")
                if resp.status_code == 200:
                    d = resp.json()
                    print(f"        current categoryId      : {d.get('categoryId')}")
                    print(f"        would become            : {guids[r['New Purpose']]}")
                    print(f"        isInheritingGlobalPurpose -> false")
                else:
                    print(f"        {resp.text[:160]}")
            except Exception as e:
                print(f"        ERROR {str(e)[:100]}")
            print()
            time.sleep(PAUSE_SECONDS)
        print("  If those returned 200, re-run without --dry-run.")
        return

    ok = fail = 0
    print(f"\n  Applying {len(todo)} updates ...\n")

    with open(RESULTS_FILE, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["recordId", "cookieName", "website", "from", "to",
                    "getStatus", "putStatus", "response"])

        for i, (_, r) in enumerate(todo.iterrows(), 1):
            rid    = str(r["ID"])
            target = str(r["New Purpose"]).strip()
            gstat = pstat = ""
            note = ""

            try:
                # 1. read the record as it stands
                g = requests.get(instance_url(rid), headers=headers, timeout=30)
                gstat = g.status_code
                if gstat != 200:
                    note = g.text[:300]
                    fail += 1
                else:
                    body = g.json()
                    # 2. change only what we mean to change
                    body["categoryId"] = guids[target]
                    body["isInheritingGlobalPurpose"] = False
                    # 3. write it back whole
                    p = requests.put(instance_url(rid), headers=headers,
                                     json=body, timeout=30)
                    pstat = p.status_code
                    note = p.text[:300]
                    if pstat in (200, 204):
                        ok += 1
                    else:
                        fail += 1
                    if pstat == 429:
                        print("    rate limited - pausing 10s")
                        time.sleep(10)

            except Exception as e:
                note = str(e)[:300]
                fail += 1

            w.writerow([rid, r["Technology"], r["Website or app"],
                        r["Current Purpose"], target, gstat, pstat, note])

            if i % 25 == 0 or i == len(todo):
                print(f"    {i}/{len(todo)}   ok={ok}  failed={fail}")

            time.sleep(PAUSE_SECONDS)

    print("\n" + "=" * 68)
    print(f"  Done.   success={ok}   failed={fail}")
    print(f"  Log: {RESULTS_FILE}")
    print("=" * 68)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    main(ap.parse_args().dry_run)
