#!/bin/bash

# Define your image and container names
IMAGE_NAME="tose-frontend"
CONTAINER_NAME="tose-frontend"

# Build the Docker image
sudo docker build -t $IMAGE_NAME .

# Stop the existing container, if it's running
if [ "$(sudo docker ps -q -f name=$CONTAINER_NAME)" ]; then
    sudo docker stop $CONTAINER_NAME
fi

# Remove the existing container, if it exists
if [ "$(sudo docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    sudo docker rm $CONTAINER_NAME
fi

# Run the container
sudo docker run -d -p 80:5000 --name $CONTAINER_NAME $IMAGE_NAME
