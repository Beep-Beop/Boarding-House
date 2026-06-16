import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from src.config import settings
from src.logger import logger

class StorageService:
    def __init__(self, s3_client=None, bucket_name=settings.R2_BUCKET_NAME):
        self.bucket_name = bucket_name
        
        if s3_client:
            self.client = s3_client
        else:
            endpoint_url = f"https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com"
            self.client = boto3.client(
                's3',
                endpoint_url=endpoint_url,
                aws_access_key_id=settings.R2_ACCESS_KEY_ID,
                aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
                config=Config(signature_version='s3v4')
            )

    def upload_file(self, file_content: bytes, object_name: str) -> bool:
        try:
            self.client.put_object(Bucket=self.bucket_name, Key=object_name, Body=file_content)
            return True
        except ClientError as e:
            logger.error("Failed to upload to R2: %s", e)
            return False

    def list_files(self) -> list:
        try:
            response = self.client.list_objects_v2(Bucket=self.bucket_name)
            return [obj['Key'] for obj in response.get('Contents', [])]
        except ClientError as e:
            logger.warning("Failed to list files from R2: %s", e)
            return []

    def get_public_url(self, object_name: str, folder: str = None) -> str:
        path = f"{folder}/{object_name}" if folder else object_name
        return f"https://r2.beepboops.app/{path}"

    def delete_file(self, object_name: str) -> bool:
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=object_name)
            return True
        except ClientError as e:
            logger.warning("Failed to delete file from R2: %s", e)
            return False