#!/bin/bash
set -e  # Exit on error

echo "Cleaning up NATS container and generated files..."

# Stop and remove NATS container
docker stop nats || true
docker rm nats || true

# Remove only the generated files and directories
rm -rf config/nats/nsc
rm -rf config/nats/jwt
rm -rf config/nats/keys
rm -f config/nats/nats-server.conf
rm -f config/nats/.env

echo "NATS cleanup complete" 