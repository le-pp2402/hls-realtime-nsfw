class MinIOClient:
    def __init__(self, endpoint: str, access_key: str, secret_key: str):
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key

    def get_client(self):
        from minio import Minio
        return Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=False
        )
    
    def download_file(self, bucket_name: str, object_name: str, file_path: str):
        """
        Download a file from MinIO bucket to local path.
        
        Args:
            bucket_name: Name of the MinIO bucket.
            object_name: Name of the object in the bucket.
            file_path: Local path where the file will be saved.
        """
        client = self.get_client()
        client.fget_object(bucket_name, object_name, file_path)
        logging.info(f"Downloaded {object_name} from bucket {bucket_name} to {file_path}")