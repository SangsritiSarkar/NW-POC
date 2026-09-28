SCENARIO B: SAME PAGE + DELIBERATE RELOAD

Folder layout:
  site-one/index.html, vercel.json
  site-two/index.html, vercel.json
  jwt-api/api/login.js, health.js, package.json, vercel.json
  setup/generate-keys-scenario-b.sh
  gtm/onetrust-loader.html

No account.html is used. Both sites contain login and signed-in panels in index.html.

SETUP
1. Deploy the separate JWT API; set DEMO_USER_EMAIL, DEMO_ACCESS_CODE,
   JWT_PRIVATE_KEY_B64, JWT_KEY_ID (if required by OneTrust), and
   CONSENT_GROUP_NAMESPACE (e.g. scenario-b).
2. Generate a NEW RSA key pair with setup/generate-keys-scenario-b.sh;
   upload only the public key to the matching OneTrust configuration.
3. Replace the API URL and otherSiteUrl in both index.html files.
4. Replace GTM-XXXXXXX twice in each index.html with the same GTM container ID.
5. Replace both hostname placeholders and the OneTrust script ID in
   gtm/onetrust-loader.html. Both hostnames must belong to the same intended
   consent group. Paste the tag into GTM Custom HTML, trigger Consent
   Initialization - All Pages, Once per page, no additional consent checks.
6. Preview anonymous load, login + SAME URL reload, signed-in identity,
   cross-domain preference, logout. Publish GTM and retest outside Preview.

DEMO SECURITY: The login endpoint uses permissive CORS from the supplied
demo API; do not use it as a production authentication system. The page
stores a short-lived browser-readable JWT only for a controlled demo.
Use separate backend authenticated sessions and a security-reviewed token
handoff for a real client. The page's signed-in panel is not access control.
