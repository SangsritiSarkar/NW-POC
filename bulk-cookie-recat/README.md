# OneTrust UAT — Bulk Cookie Re-categorisation

Applies the client's final cookie categories to **270 cookie records** in the
OneTrust UAT tenant (`uat.onetrust.com`), across 17 in-scope Nationwide domains.

---

## Files

| File | What it is |
|---|---|
| `UAT_recategorisation_plan.xlsx` | The plan. 446 matched rows, 270 flagged `YES`. **Review this first.** |
| `recategorise.py` | Sends the updates to OneTrust |
| `verify.py` | Summarises the results afterwards |
| `requirements.txt` | Python packages needed |
| `.env.example` | Template for your credentials |
| `.gitignore` | Stops your token and results from being committed |

---

## Setup in GitHub Codespaces

### 1. Upload the files

Create a repo, then drag all these files in. Open it in Codespaces
(green **Code** button → **Codespaces** → **Create codespace on main**).

### 2. Install the packages

In the Codespace terminal:

```bash
pip install -r requirements.txt
```

### 3. Set your credentials

```bash
export OT_HOSTNAME="uat.onetrust.com"
export OT_TOKEN="paste-your-uat-api-key-here"
```

These last only for the current terminal session. If you close it and come
back, run them again.

> **Never** put the token in a file you commit. `.env` and `results.csv` are
> already gitignored.

### 4. Dry run — sends nothing

```bash
python recategorise.py --dry-run
```

You should see:

```
plan rows           : 446
updates to send     : 270
unique cookie IDs   : 270
target tenant       : uat.onetrust.com
token               : set
```

plus a breakdown by category and five sample payloads.

### 5. Get sign-off

Send `UAT_recategorisation_plan.xlsx` to your manager or the client and get a
written yes before writing anything — even in UAT.

### 6. Run it

```bash
python recategorise.py
```

Takes a few minutes. Progress prints every 25 records. Writes `results.csv`.

### 7. Check what happened

```bash
python verify.py
```

### 8. Confirm in the UI

Open **Tracking Technologies** in UAT, search a cookie you know changed
(e.g. `_ga`), and check the **Purpose** column now shows Functional Cookies.

### 9. Republish

Changing a category does **not** update the live banner. Republish the
affected sites' scripts.

---

## Understanding the plan file

| Column | Meaning |
|---|---|
| `ID` | OneTrust's record ID — this is what gets updated |
| `Technology` | Cookie name |
| `Website or app` | Which of the 17 sites it's on |
| `Current Purpose` | What it is now |
| `Matched client rule` | Which line in the client's file it came from |
| `New Purpose` | What it becomes |
| `Change needed` | `YES` = will be updated, `NO` = already correct, skipped |

**Why 121 client cookies became 446 rows:** OneTrust stores a cookie once per
website. `_ga` on 14 sites is 14 separate records, each with its own ID and
each needing its own update.

---

## What gets touched

**Only cookies in the client's file.** 46 cookie names found on the in-scope
domains but absent from the client list are untouched. `71586` and `uni_ct`
are skipped — the client marked them "No GTM tag match".

**Nothing is set to Performance Cookies.** The client's list only uses
Required / Functional / Advertising. 100 cookies currently in Performance move
out of it — 93 → Functional, 5 → Required, 2 → Advertising.

---

## Category IDs

| Category | ID |
|---|---|
| Required Cookies | `C0001` |
| Functional Cookies | `C0003` |
| Advertising Cookies | `C0004` |

---

## API details

```
PUT https://uat.onetrust.com/api/cookiemanager/v1/cookies
Authorization: Bearer <token>

{
  "cookieId": "019fd31b-c742-7dde-8710-dca03049235f",
  "cookieName": "QSI_SI_xxx_intercept",
  "customCategoryName": "C0003"
}
```

`customCategoryName` takes the **category ID**, not the display name.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `401` on everything | Token wrong or expired | Regenerate the API key |
| `403` on everything | Token lacks Cookie Consent scope, or wrong org | Recreate the key with the right scope, in the right org |
| `404` on everything | Hostname or path wrong | Confirm the URL in your browser matches `OT_HOSTNAME` |
| `400` on everything | Cookie IDs don't exist in this tenant | You're using a prod export against UAT |
| `429` occasionally | Rate limited | Script pauses 10s automatically |
| `200` but nothing changed | Response body has `errorMessages` | Run `verify.py` — it flags these |

**Re-running is safe.** Setting a cookie to the category it's already in does
no harm, so fix the cause and run again.

---

## Moving to Production later

Do **not** reuse this plan file. Production cookie IDs are completely
different from UAT ones.

1. Export **Tracking Technologies** fresh from the production tenant
2. Rebuild the plan against that export
3. Get sign-off again
4. Point `OT_HOSTNAME` at production and use a **production** token
