IMAGE_NAME="tose_backend"
CONTAINER_NAME="tose_backend"
PORT=8000
VOLUME_NAME="${CONTAINER_NAME}_logs"


if [ -z "$(docker volume ls -q -f name=^${VOLUME_NAME}$)" ]; then
    echo "Creating Docker volume for logs..."
    docker volume create $VOLUME_NAME
fi

echo "Building Docker image..."
docker build -t $IMAGE_NAME .

echo "Running Docker container..."
docker run -d --name $CONTAINER_NAME \
    -p $PORT:$PORT $IMAGE_NAME


echo "Container $CONTAINER_NAME is running on port $PORT with logs in $VOLUME_NAME"
