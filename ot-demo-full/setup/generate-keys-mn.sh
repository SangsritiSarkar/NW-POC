#!/bin/sh
set -eu
# Generates a completely separate RSA key pair for the M/N consent demo.
openssl genrsa -out private-mn.pem 2048
openssl rsa -in private-mn.pem -pubout -out public-mn.pem
printf '
Created private-mn.pem and public-mn.pem.
'
printf 'Upload only public-mn.pem to the M/N OneTrust configuration. Never commit private-mn.pem.
'
printf '
Base64 value for the JWT_PRIVATE_KEY_B64 Vercel variable:
'
if base64 --help 2>/dev/null | grep -q -- '-w'; then
  base64 -w 0 private-mn.pem
else
  base64 private-mn.pem | tr -d '
'
fi
printf '
'
