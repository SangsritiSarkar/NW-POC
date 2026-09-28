#!/bin/sh
set -eu
# Generates a completely separate RSA key pair for the Scenario B consent demo.
openssl genrsa -out private-scenario-b.pem 2048
openssl rsa -in private-scenario-b.pem -pubout -out public-scenario-b.pem
printf '
Created private-scenario-b.pem and public-scenario-b.pem.
'
printf 'Upload only public-scenario-b.pem to the Scenario B OneTrust configuration. Never commit private-scenario-b.pem.
'
printf '
Base64 value for the JWT_PRIVATE_KEY_B64 Vercel variable:
'
if base64 --help 2>/dev/null | grep -q -- '-w'; then
  base64 -w 0 private-scenario-b.pem
else
  base64 private-scenario-b.pem | tr -d '
'
fi
printf '
'
