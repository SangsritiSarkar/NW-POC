"""
OneTrust - Bulk delete websites (Cookie Consent), keeping ONLY 4 protected sites.

What it does
  1. Gets an access token.
  2. Lists ALL websites via GET /api/cmp/v1/webscans (100 per page).
  3. Splits them into KEEP (only the 4 exact protected sites; subdomains ARE deleted)
     and DELETE lists, and saves a plan CSV.
  4. DRY RUN by default - nothing is deleted unless you run with --delete
     AND type the confirmation text.
  5. Deletes one by one via DELETE /api/cmp/v1/domains/{domainId}, logs results,
     then re-lists websites to confirm the protected sites still exist.

Usage (in the Codespaces terminal)
  python ot_bulk_delete_websites_v3.py            # dry run (safe, deletes nothing)
  python ot_bulk_delete_websites_v3.py --delete   # real delete (asks to confirm)
"""

import csv
import sys
import time
from datetime import datetime

import requests

# ---------------------------------------------------------------------------
# SETTINGS
# ---------------------------------------------------------------------------
OT_HOST = "app.onetrust.com"
CLIENT_ID = "c0b1e9e846144927a8f581207848e0fa"
CLIENT_SECRET = "UW4V7rJZlpEmuM93jxSJq1fl0DUeIYFt"

# Sites that must NEVER be deleted (exact match; "www." is ignored).
# Subdomains such as espanol.nationwide.com are NOT protected and WILL be deleted.
PROTECTED = {
    "nationwide.com",
    "nrsforu.com",
    "nationwiderealtyinvestors.com",
    "220vine.com",
}

DELAY_SECONDS = 1.0   # pause between deletes to avoid 429 rate limits
PAGE_SIZE = 100       # API maximum

BASE = f"https://{OT_HOST}"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
def normalize(url: str) -> str:
    """'https://www.Nationwide.com/' -> 'nationwide.com'"""
    u = (url or "").strip().lower()
    for prefix in ("https://", "http://"):
        if u.startswith(prefix):
            u = u[len(prefix):]
    u = u.split("/")[0].split("?")[0].split(":")[0]
    if u.startswith("www."):
        u = u[4:]
    return u


def is_protected(url: str) -> bool:
    return normalize(url) in PROTECTED


def get_token() -> str:
    r = requests.post(
        f"{BASE}/api/access/v1/oauth/token",
        params={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
        timeout=60,
    )
    if r.status_code != 200:
        sys.exit(f"Token request failed: HTTP {r.status_code}\n{r.text[:500]}")
    print("Access token received.")
    return r.json()["access_token"]


def extract_items(body):
    """The list of websites may be the body itself or nested under a key."""
    if isinstance(body, list):
        return body
    if isinstance(body, dict):
        for key in ("content", "data", "items", "results", "domains", "webscans"):
            if isinstance(body.get(key), list):
                return body[key]
    return []


URL_KEYS = ("url", "Url", "domain", "domainName", "domainUrl", "name", "websiteUrl")
ID_KEYS = ("domainId", "DomainId", "id", "Id", "domainID")


def pick(item: dict, keys):
    for k in keys:
        if item.get(k):
            return str(item[k])
    return ""


def list_websites(token: str):
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    all_items, page = [], 0
    while True:
        r = requests.get(
            f"{BASE}/api/cmp/v1/webscans",
            headers=headers,
            params={"page": page, "size": PAGE_SIZE, "sortBy": "Url", "direction": "ASC"},
            timeout=60,
        )
        if r.status_code != 200:
            sys.exit(f"List websites failed (page {page}): HTTP {r.status_code}\n{r.text[:500]}")
        items = extract_items(r.json())
        if page == 0 and items:
            print(f"Fields found in the response: {list(items[0].keys())}")
        if not items:
            break
        all_items.extend(items)
        print(f"Page {page}: {len(items)} websites")
        if len(items) < PAGE_SIZE:
            break
        page += 1

    sites = []
    for it in all_items:
        url, dom_id = pick(it, URL_KEYS), pick(it, ID_KEYS)
        if not url or not dom_id:
            sys.exit(
                "Could not read the website URL / Domain ID from this item:\n"
                f"{it}\nStopping for safety - nothing was deleted. "
                "Share this output so the field names can be fixed."
            )
        sites.append({"url": url, "domainId": dom_id})
    return sites


def write_csv(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    do_delete = "--delete" in sys.argv
    token = get_token()
    sites = list_websites(token)
    print(f"\nTotal websites found: {len(sites)}")

    keep, delete = [], []
    for s in sites:
        if is_protected(s["url"]):
            keep.append({**s, "action": "KEEP (protected)"})
        else:
            delete.append({**s, "action": "DELETE"})

    found = {normalize(k["url"]) for k in keep}
    missing = PROTECTED - found
    if missing:
        print(f"\nWARNING: protected site(s) not found in the list: {sorted(missing)}")

    plan_file = f"delete_plan_{STAMP}.csv"
    write_csv(plan_file, keep + delete, ["url", "domainId", "action"])

    print("\n=== KEEP (protected) ===")
    for k in keep:
        print(f"  {k['url']}  ({k['domainId']})")
    print(f"\n=== TO DELETE: {len(delete)} websites ===")
    for d in delete:
        print(f"  {d['url']}  ({d['domainId']})")
    print(f"\nPlan saved to: {plan_file}")

    if not do_delete:
        print("\nDRY RUN - nothing was deleted. Review the plan, then run again with --delete")
        return
    if not delete:
        print("Nothing to delete.")
        return

    confirm_text = f"DELETE {len(delete)}"
    typed = input(f"\nThis permanently deletes {len(delete)} websites. Type '{confirm_text}' to continue: ")
    if typed.strip() != confirm_text:
        print("Confirmation did not match. Nothing was deleted.")
        return

    results = []
    for i, d in enumerate(delete, 1):
        # Final safety check right before each delete
        if is_protected(d["url"]):
            print(f"[{i}] SKIPPED (protected): {d['url']}")
            results.append({**d, "status": "SKIPPED_PROTECTED", "detail": ""})
            continue

        url = f"{BASE}/api/cmp/v1/domains/{d['domainId']}"
        for attempt in range(4):
            r = requests.delete(url, headers={"Authorization": f"Bearer {token}"}, timeout=60)
            if r.status_code == 401:            # token expired -> refresh and retry
                token = get_token()
                continue
            if r.status_code == 429:            # rate limited -> wait and retry
                wait = 10 * (attempt + 1)
                print(f"    429 rate limit, waiting {wait}s...")
                time.sleep(wait)
                continue
            break

        ok = r.status_code in (200, 204)
        print(f"[{i}/{len(delete)}] {'DELETED' if ok else 'FAILED'} HTTP {r.status_code}: {d['url']}")
        results.append({**d, "status": r.status_code, "detail": "" if ok else r.text[:300]})
        time.sleep(DELAY_SECONDS)

    log_file = f"delete_log_{STAMP}.csv"
    write_csv(log_file, results, ["url", "domainId", "action", "status", "detail"])
    failed = [x for x in results if x["status"] not in (200, 204)]
    print(f"\nDone. Deleted: {len(results) - len(failed)}  Failed/Skipped: {len(failed)}")
    print(f"Log saved to: {log_file}")

    print("\nChecking protected sites are still present...")
    remaining = {normalize(s["url"]) for s in list_websites(token)}
    for p in sorted(PROTECTED):
        print(f"  {p}: {'still present' if p in remaining else 'NOT FOUND - check OneTrust'}")


if __name__ == "__main__":
    main()
