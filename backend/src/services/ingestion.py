import logging
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from pydantic import BaseModel, HttpUrl

logger = logging.getLogger(__name__)


class StorageBackend(str, Enum):
    LOCAL = "local"
    GOOGLE_DRIVE = "google_drive"
    S3 = "s3"


class FilePriority(str, Enum):
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class FileIngestionRequest(BaseModel):
    file: UploadFile
    metadata: Optional[Dict[str, Any]] = None
    priority: FilePriority = FilePriority.NORMAL
    callback_url: Optional[str] = None
    storage_backends: List[StorageBackend] = [StorageBackend.LOCAL]


class FileIngestionResponse(BaseModel):
    ingestion_id: uuid.UUID
    status: str
    timestamp: datetime
    estimated_completion: Optional[datetime] = None
    storage_locations: Dict[StorageBackend, str] = {}
    presigned_urls: Dict[StorageBackend, str] = {}


class StorageBackendConfig(BaseModel):
    local_path: str = "./storage"
    google_drive_folder_id: Optional[str] = None
    google_credentials: Optional[Dict] = None
    s3_bucket: Optional[str] = None
    s3_region: Optional[str] = None
    s3_access_key: Optional[str] = None
    s3_secret_key: Optional[str] = None


class FileIngestionService:
    def __init__(self, config: StorageBackendConfig, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.config = config
        self._init_storage_clients()

    def _init_storage_clients(self):
        """Initialize clients for all storage backends"""
        # Google Drive client
        if self.config.google_credentials:
            credentials = service_account.Credentials.from_service_account_info(
                self.config.google_credentials,
                scopes=["https://www.googleapis.com/auth/drive"],
            )
            self.drive_service = build("drive", "v3", credentials=credentials)

        # S3 client
        if self.config.s3_access_key and self.config.s3_secret_key:
            self.s3_client = boto3.client(
                "s3",
                region_name=self.config.s3_region,
                aws_access_key_id=self.config.s3_access_key,
                aws_secret_access_key=self.config.s3_secret_key,
            )

    async def ingest_file(self, request: FileIngestionRequest) -> FileIngestionResponse:
        """Process file ingestion request to multiple storage backends"""
        ingestion_id = uuid.uuid4()
        response = FileIngestionResponse(
            ingestion_id=ingestion_id, status="queued", timestamp=datetime.utcnow()
        )

        # Submit to processing queue
        self.executor.submit(self._process_file, ingestion_id, request, response)

        return response

    def _process_file(
        self,
        ingestion_id: uuid.UUID,
        request: FileIngestionRequest,
        response: FileIngestionResponse,
    ):
        """Background processing of file to multiple storage backends"""
        try:
            file_content = request.file.file.read()
            filename = request.file.filename or "unnamed"
            content_type = request.file.content_type or "application/octet-stream"

            for backend in request.storage_backends:
                try:
                    if backend == StorageBackend.LOCAL:
                        self._store_local(ingestion_id, filename, file_content)
                        response.storage_locations[
                            backend
                        ] = f"{self.config.local_path}/{ingestion_id}"
                    elif backend == StorageBackend.GOOGLE_DRIVE:
                        file_id = self._store_google_drive(
                            ingestion_id, filename, file_content, content_type
                        )
                        response.storage_locations[backend] = file_id
                    elif backend == StorageBackend.S3:
                        self._store_s3(
                            ingestion_id, filename, file_content, content_type
                        )
                        response.storage_locations[
                            backend
                        ] = f"s3://{self.config.s3_bucket}/{ingestion_id}"

                    # Generate presigned URL if supported
                    if backend in [StorageBackend.S3, StorageBackend.GOOGLE_DRIVE]:
                        response.presigned_urls[backend] = self._generate_presigned_url(
                            backend, ingestion_id, filename
                        )

                except Exception as e:
                    logger.error(
                        f"Failed to store file {ingestion_id} in {backend}: {str(e)}"
                    )

            response.status = "completed"

        except Exception as e:
            logger.error(f"Failed to process file {ingestion_id}: {str(e)}")
            response.status = "failed"

    def _store_local(self, file_id: uuid.UUID, filename: Optional[str], content: bytes):
        """Store file in local filesystem"""
        Path(self.config.local_path).mkdir(exist_ok=True)
        with open(f"{self.config.local_path}/{file_id}", "wb") as f:
            f.write(content)

    def _store_google_drive(
        self,
        file_id: uuid.UUID,
        filename: Optional[str],
        content: bytes,
        content_type: Optional[str],
    ) -> str:
        """Store file in Google Drive"""
        file_metadata = {
            "name": filename,
            "parents": [self.config.google_drive_folder_id],
        }
        media = MediaIoBaseUpload(content, mimetype=content_type)
        file = (
            self.drive_service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )
        return file.get("id")

    def _store_s3(
        self,
        file_id: uuid.UUID,
        filename: Optional[str],
        content: bytes,
        content_type: Optional[str],
    ):
        """Store file in S3"""
        self.s3_client.put_object(
            Bucket=self.config.s3_bucket,
            Key=str(file_id),
            Body=content,
            ContentType=content_type,
        )

    def _generate_presigned_url(
        self, backend: StorageBackend, file_id: uuid.UUID, filename: Optional[str]
    ) -> str:
        """Generate presigned URL for accessing stored file"""
        if backend == StorageBackend.S3:
            return self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.config.s3_bucket, "Key": str(file_id)},
                ExpiresIn=3600,
            )
        elif backend == StorageBackend.GOOGLE_DRIVE:
            return f"https://drive.google.com/uc?export=download&id={file_id}"
        return ""

    async def shutdown(self):
        """Clean shutdown of service"""
        self.executor.shutdown(wait=True)
