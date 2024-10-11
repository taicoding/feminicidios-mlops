#!/bin/bash

# Create a Docker network
if [ ! "$(docker network ls | grep web)" ]; then
    echo "Creating Docker network"
    docker network create web
fi

echo "Docker network created"

cd mlflow
./run.sh

cd ..
cd dagster
./run.sh

cd ..
cd elk
./run.sh

echo "Finished running all servers"
#click anykey to continue
read -n 1 -s -r -p "Press any key to continue"