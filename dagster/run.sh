#!/bin/bash
echo "Starting Dagster server"
# Build the Dagster image and start the container stop old container rebuild image and start new container
docker-compose -f compose.yaml down
# Build image
docker-compose -f compose.yaml build
# Start container
docker-compose -f compose.yaml up -d
echo "✨ Dagster server started"
