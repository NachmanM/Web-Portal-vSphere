#!/bin/bash

docker network create shared-bridge 

docker compose -f ./appsmith/docker-compose.yaml up  -d
docker compose -f ./FastAPI/docker-compose.yaml up  -d