#!/bin/bash
echo "Starting MLflow server"
docker-compose -f compose.yaml up -d
echo "✨ Mlflow server started"
