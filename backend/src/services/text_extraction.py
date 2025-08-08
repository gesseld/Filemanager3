import io
import logging
from enum import Enum
from typing import Any, Dict, Optional

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class TextExtractionService:
    def __init__(self, tika_server_url: str = "http://localhost:9998"):
        self.tika_server_url = tika_server_url

    async def extract_text(self, file_content: bytes, file_name: str) -> Dict[str, Any]:
        """Extract text and metadata from document using Tika"""
        try:
            async with httpx.AsyncClient() as client:
                # Extract text content
                text_response = await client.put(
                    f"{self.tika_server_url}/tika",
                    headers={"Accept": "text/plain"},
                    content=file_content,
                )
                text_response.raise_for_status()

                # Extract metadata
                meta_response = await client.put(
                    f"{self.tika_server_url}/meta",
                    headers={"Accept": "application/json"},
                    content=file_content,
                )
                meta_response.raise_for_status()

                return {
                    "content": text_response.text,
                    "metadata": meta_response.json(),
                    "file_name": file_name,
                }

        except httpx.HTTPError as e:
            logger.error(f"Tika extraction failed: {str(e)}")
            raise

    async def detect_language(self, text: str) -> Optional[str]:
        """Detect language of extracted text"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{self.tika_server_url}/language/string",
                    headers={"Accept": "text/plain"},
                    content=text.encode("utf-8"),
                )
                response.raise_for_status()
                return response.text.strip()
        except httpx.HTTPError as e:
            logger.error(f"Language detection failed: {str(e)}")
            return None

    async def validate_file_type(self, file_content: bytes) -> bool:
        """Validate file type using Tika detection"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{self.tika_server_url}/detect/stream", content=file_content
                )
                response.raise_for_status()
                return response.text.strip() != "application/octet-stream"
        except httpx.HTTPError as e:
            logger.error(f"File type validation failed: {str(e)}")
            return False
