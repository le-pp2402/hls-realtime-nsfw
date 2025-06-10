#!/bin/bash

echo "HLS Uploader Container Starting..."

# Chờ MinIO sẵn sàng
while ! curl -f "$MINIO_ENDPOINT/minio/health/live" > /dev/null 2>&1; do
    echo "Waiting for MinIO to be ready..."
    sleep 2
done

echo "MinIO is ready. Starting file watcher..."

# Chạy script monitor
exec /scripts/watch-and-upload.sh