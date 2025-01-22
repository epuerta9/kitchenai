#!/bin/bash
set -e

# Check if .env file exists
ENV_FILE="config/nats/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: NATS .env file not found at $ENV_FILE"
    echo "Please run setup_nats_operator.sh first"
    exit 1
fi

# Source the .env file
set -a  # automatically export all variables
source "$ENV_FILE"
set +a  # disable auto-export

# Print the exported variables
echo "Exported NATS environment variables:"
echo "ADMIN_PASSWORD=${ADMIN_PASSWORD}"
echo "CLIENTA_PASSWORD=${CLIENTA_PASSWORD}"
echo "CLIENTB_PASSWORD=${CLIENTB_PASSWORD}"
echo "-------------------"

echo "To use these variables in your current shell, run:"
echo "source ./scripts/export_nats_env.sh" 