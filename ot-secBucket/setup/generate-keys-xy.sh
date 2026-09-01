#!/bin/sh
set -eu
# Generates a SEPARATE RSA key pair for the X/Y consent bucket.
# This is intentionally distinct from the A/B pair so that X/Y form
# an isolated cross-bucket consent group.
openssl genrsa -out private-xy.pem 2048
openssl rsa -in private-xy.pem -pubout -out public-xy.pem
printf '\nCreated private-xy.pem and public-xy.pem.\n'
printf 'Upload only public-xy.pem to the X/Y OneTrust configuration. Never commit private-xy.pem.\n'
printf '\nBase64 private key for the X/Y Vercel JWT_PRIVATE_KEY_B64:\n'
base64 -w 0 private-xy.pem
printf '\n'
