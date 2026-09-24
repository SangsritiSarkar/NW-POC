# OT Demo - Site P / Site Q

Isolated copy of the M/N cross-domain consent demo, with its own colours,
its own JWT API, its own RSA key pair and its own handoff key.

## Structure
- `jwt-api-pq/` - Vercel serverless API (`/api/login`, `/api/health`)
- `setup/generate-keys-pq.sh` - generates `private-pq.pem` / `public-pq.pem`
- `site-p/` - teal branded site (index + account)
- `site-q/` - indigo branded site (index + account)

## What must be set before deploying
1. Replace `PASTE_PQ_ONETRUST_TEST_ID` in all four HTML files with the
   Testing CDN ID of the P/Q OneTrust Consent Group.
2. Deploy `jwt-api-pq/` and set the environment variables:
   `DEMO_USER_EMAIL`, `DEMO_ACCESS_CODE`, `JWT_PRIVATE_KEY_B64`,
   `JWT_KEY_ID`, `CONSENT_GROUP_NAMESPACE` (use something like `pq`).
3. Upload only `public-pq.pem` to the P/Q OneTrust configuration.
4. Update the deployed URLs in the HTML `CONFIG` blocks if they differ from
   `ot-jwt-pq.vercel.app`, `ot-site-p.vercel.app`, `ot-site-q.vercel.app`.
