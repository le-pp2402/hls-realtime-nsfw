#!/bin/bash

WATCH_DIR="${WATCH_DIR:-/watch/hls}"
MINIO_ENDPOINT="${MINIO_ENDPOINT:-http://minio:9000}"
MINIO_ACCESS_KEY="${MINIO_ACCESS_KEY:-phat_guest}"
MINIO_SECRET_KEY="${MINIO_SECRET_KEY:-MatKhau24CuaP02hatD123aiLam}"
MINIO_BUCKET="hlsbucket"

echo "Starting HLS file watcher..."
echo "Watch directory: $WATCH_DIR"
echo "MinIO endpoint: $MINIO_ENDPOINT"

mc alias set minio "$MINIO_ENDPOINT" "$MINIO_ACCESS_KEY" "$MINIO_SECRET_KEY"
mc mb --ignore-existing "minio/$MINIO_BUCKET"

echo "Monitoring $WATCH_DIR for new HLS files..."

inotifywait -m -r -e create,moved_to,close_write --format '%w%f %e' "$WATCH_DIR" | while read file event
do
    if [[ "$file" == *.tmp ]] || [[ "$file" == *~ ]] || [[ -d "$file" ]]; then
        continue
    fi
    
    # Chỉ xử lý file .ts và .m3u8
    if [[ "$file" == *.ts ]] || [[ "$file" == *.m3u8 ]]; then
        echo "[$event] Detected: $file"
        
        # Chờ một chút để đảm bảo file được ghi hoàn chỉnh
        sleep 0.5
        
        # Kiểm tra file có tồn tại không
        if [[ ! -f "$file" ]]; then
            echo "File not found: $file"
            continue
        fi
        
        # Tính toán đường dẫn tương đối từ watch directory
        relative_path=${file#$WATCH_DIR/}
        
        # Upload file lên MinIO
        if mc cp "$file" "minio/$MINIO_BUCKET/$relative_path"; then
            echo "✓ Successfully uploaded: $relative_path"
        else
            echo "✗ Failed to upload: $relative_path"
        fi
    fi
done