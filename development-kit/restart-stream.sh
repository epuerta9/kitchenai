#!/bin/bash

# Define the containers to restart
STREAM_CONTAINER="kitchenai-stream"
QCLUSTER_CONTAINER="kitchenai-qcluster"

echo "🔄 Restarting KitchenAI Streaming Container and QCluster..."

# Stop the containers if they are running
docker compose stop $STREAM_CONTAINER $QCLUSTER_CONTAINER

# Remove the stopped containers to avoid issues with cached volumes or old containers
docker compose rm -f $STREAM_CONTAINER $QCLUSTER_CONTAINER

# Start the containers with a clean state
docker compose up -d $STREAM_CONTAINER $QCLUSTER_CONTAINER

# Check the status to confirm they are running
docker compose ps

# Provide feedback to the user
echo "✅ Streaming container and QCluster restarted successfully!"
