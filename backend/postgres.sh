#!/bin/bash

# Define the PostgreSQL version to use
POSTGRES_VERSION="12-alpine"

# Define the Docker volume name
DOCKER_VOLUME="postgres_data"

# Define the container name
CONTAINER_NAME="postgres_container"

# Define the port on which PostgreSQL will be accessible
HOST_PORT="5432"
CONTAINER_PORT="5432"

# Create the Docker volume (this will do nothing if the volume already exists)
docker volume create "$DOCKER_VOLUME"

# Pull the latest PostgreSQL image
docker pull postgres:"$POSTGRES_VERSION"

# Run the PostgreSQL container
docker run --name "$CONTAINER_NAME" \
           -e POSTGRES_PASSWORD=mysecretpassword \
           -v "$DOCKER_VOLUME":/var/lib/postgresql/data \
           -p "$HOST_PORT":"$CONTAINER_PORT" \
           -d postgres:"$POSTGRES_VERSION"

echo "PostgreSQL is running on port $HOST_PORT"
