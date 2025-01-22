#!/bin/bash
set -e

# Function to generate random password
generate_password() {
    openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 32
}

# Create directories
mkdir -p config/nats

# Generate passwords
ADMIN_PASSWORD=$(generate_password)
CLIENTA_PASSWORD=$(generate_password)
CLIENTB_PASSWORD=$(generate_password)

# Print passwords for verification
echo "Generated passwords:"
echo "ADMIN_PASSWORD: ${ADMIN_PASSWORD}"
echo "CLIENTA_PASSWORD: ${CLIENTA_PASSWORD}"
echo "CLIENTB_PASSWORD: ${CLIENTB_PASSWORD}"
echo "-------------------"

# Generate .env file for docker-compose
cat > config/nats/.env << EOF
ADMIN_PASSWORD=${ADMIN_PASSWORD}
CLIENTA_PASSWORD=${CLIENTA_PASSWORD}
CLIENTB_PASSWORD=${CLIENTB_PASSWORD}
EOF

# Export the variables for envsubst
export ADMIN_PASSWORD
export CLIENTA_PASSWORD
export CLIENTB_PASSWORD

# Debug: Print the environment variables
echo "Environment variables:"
env | grep PASSWORD
echo "-------------------"

# Copy and update the base config with ALL variables
envsubst '${ADMIN_PASSWORD} ${CLIENTA_PASSWORD} ${CLIENTB_PASSWORD}' \
    < config/nats-server.conf \
    > config/nats/nats-server.conf

# Debug: Print the generated config
echo "Generated config:"
cat config/nats/nats-server.conf
echo "-------------------"

echo "all jobs succeeded"