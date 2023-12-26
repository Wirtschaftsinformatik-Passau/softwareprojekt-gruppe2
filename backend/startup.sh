IMAGE_NAME="tose_backend_fastapi"
CONTAINER_NAME="tose_backend_fastapi"
PORT=8000
VOLUME_NAME="${CONTAINER_NAME}_logs"


if [ -z "$(sudo docker volume ls -q -f name=^${VOLUME_NAME}$)" ]; then
    echo "Creating Docker volume for logs..."
    docker volume create $VOLUME_NAME
fi

echo "Building Docker image..."
sudo docker build -t $IMAGE_NAME .

echo "Running Docker container..."
sudo docker run -d --name $CONTAINER_NAME -p $PORT:$PORT $IMAGE_NAME


echo "Container $CONTAINER_NAME is running on port $PORT with logs in $VOLUME_NAME"
