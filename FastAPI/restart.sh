#!/bin/bash

docker compose kill fastapi-fast-api-1

docker compose build --no-cache

docker compose up -d

