
VOLUME_NAME="backend-volume"
VOLUME_NAME2="alembic-volume"
IMAGE_NAME="fastapi-backend"
CONTAINER_NAME="fastapi-backend"

# Check if the volume exists
if ! sudo docker volume ls | grep -q $VOLUME_NAME; then
    echo "Creating Docker volume '$VOLUME_NAME'..."
    sudo docker volume create $VOLUME_NAME
fi

if [ "$(sudo docker ps -q -f name=$CONTAINER_NAME)" ]; then
    echo "Stopping running container '$CONTAINER_NAME'..."
    sudo docker stop $CONTAINER_NAME
fi

# Check if the container exists (even if stopped)
if [ "$(sudo docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    echo "Removing existing container '$CONTAINER_NAME'..."
    sudo docker rm $CONTAINER_NAME
fi

# Build the Docker image
echo "Building Docker image '$IMAGE_NAME'..."
sudo docker build -t $IMAGE_NAME . --rm --no-cache

# Check if the container is already running and stop it
if [ "$(sudo docker ps -q -f name=$CONTAINER_NAME)" ]; then
    echo "Stopping existing container '$CONTAINER_NAME'..."
    sudo docker stop $CONTAINER_NAME
    sudo docker rm $CONTAINER_NAME
fi

# Run the Docker container with the volume attached
echo "Running container '$CONTAINER_NAME'..."
sudo docker run -d \
  --name $CONTAINER_NAME \
  -v $VOLUME_NAME:/logs \
  -v $VOLUME_NAME2:/tose_backend/ \
  -p 8000:8000 \
  $IMAGE_NAME

echo "Container '$CONTAINER_NAME' is up and running on port 8000."
