#!/bin/sh
set -eu
# Generates a completely separate RSA key pair for the P/Q consent demo.
openssl genrsa -out private-pq.pem 2048
openssl rsa -in private-pq.pem -pubout -out public-pq.pem
printf '
Created private-pq.pem and public-pq.pem.
'
printf 'Upload only public-pq.pem to the P/Q OneTrust configuration. Never commit private-pq.pem.
'
printf '
Base64 value for the JWT_PRIVATE_KEY_B64 Vercel variable:
'
if base64 --help 2>/dev/null | grep -q -- '-w'; then
  base64 -w 0 private-pq.pem
else
  base64 private-pq.pem | tr -d '
'
fi
printf '
'
