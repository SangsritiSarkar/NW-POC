# Separate OneTrust M/N Demo

This package is independent from the existing X/Y demo.

## Vercel projects
Deploy these as three separate projects:
1. `site-m` (root directory: `site-m`)
2. `site-n` (root directory: `site-n`)
3. `jwt-api-mn` (root directory: `jwt-api-mn`)

## JWT API environment variables
Set these in the `jwt-api-mn` Vercel project:
- `DEMO_USER_EMAIL`
- `DEMO_ACCESS_CODE`
- `JWT_PRIVATE_KEY_B64`
- `JWT_KEY_ID` (must match the Key ID configured with the uploaded M/N public key in OneTrust)

## OneTrust and URL placeholders
- Replace `PASTE_MN_ONETRUST_TEST_ID_HERE` in all four HTML files.
- Update `tokenApiUrl` in both landing pages if the API Vercel URL differs.
- Update each account page's `otherSiteUrl` if the site Vercel URLs differ.

## Flow
- Landing page loads OneTrust anonymously and contains the login form.
- Valid login stores UID/JWT briefly in same-origin sessionStorage and opens `account.html`.
- Account page sets `dataSubjectParams` before loading OneTrust as the known user.

## Visual identification
- Site M: sunny yellow (`#facc15`)
- Site N: vibrant coral-pink (`#f43f5e`)

All application logic, API configuration, RSA key setup, and Vercel deployment structure remain unchanged.
