#!/bin/sh
set -eu
openssl genrsa -out private.pem 2048
openssl rsa -in private.pem -pubout -out public.pem
printf '\nCreated private.pem and public.pem.\n'
printf 'Upload only public.pem to OneTrust. Never commit private.pem.\n'
printf '\nBase64 private key for Vercel JWT_PRIVATE_KEY_B64:\n'
base64 -w 0 private.pem
printf '\n'
