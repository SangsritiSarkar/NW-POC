# ot-crsd — X/Y cross-bucket consent set

This is a **parallel set** to the existing A/B demo. Sites **X** and **Y** share their own
JWT API and their own RSA key pair, forming an **isolated consent bucket** separate from A/B.

## Structure

```
jwt-api-xy/
  api/health.js
  api/login.js
  package.json
  vercel.json
setup/
  generate-keys-xy.sh
site-x/
  index.html        (Aurora Wealth Management — purple)
  vercel.json
site-y/
  index.html        (Aurora Health Portal — amber)
  vercel.json
```

## Deploy on Vercel (3 separate projects)

1. **Generate the X/Y key pair**
   ```sh
   cd setup
   sh generate-keys-xy.sh
   ```
   - Upload **only** `public-xy.pem` to the X/Y OneTrust configuration.
   - Copy the printed base64 string for the next step.

2. **Deploy `jwt-api-xy/`** as its own Vercel project. Set env vars:
   - `DEMO_USER_EMAIL`
   - `DEMO_ACCESS_CODE`
   - `JWT_PRIVATE_KEY_B64`  (the base64 string from step 1 — **different** from A/B)

3. **Deploy `site-x/`** and **`site-y/`** as their own Vercel projects.

4. In each site's `index.html`, update the `CONFIG` block:
   - `oneTrustTestId`  → the X/Y OneTrust Testing CDN ID (currently a placeholder)
   - `tokenApiUrl`     → the deployed `jwt-api-xy` URL
   - `otherSiteUrl`    → the sibling site's URL

## Why a separate key pair?

Because X and Y use a **different private/public key pair** (and their own JWT API),
their signed identity tokens validate against a different OneTrust public key than A/B.
This keeps X/Y consent isolated in its own bucket while still syncing between X and Y.
