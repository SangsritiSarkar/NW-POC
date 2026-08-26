#!/bin/bash

# Move to the project root
cd "$(dirname "$0")/.."

echo "Generating RSA private key..."
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out private.pem

echo "Generating RSA public key..."
openssl pkey -in private.pem -pubout -out public.pem

echo ""
echo "Key pair generated successfully!"
echo ""
echo "Private key: private.pem"
echo "Public key:  public.pem"
