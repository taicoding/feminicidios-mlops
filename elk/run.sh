#!/bin/bash
echo "Starting ELK services"
docker-compose -f compose.yaml up -d
echo "✨ ELK services started"
