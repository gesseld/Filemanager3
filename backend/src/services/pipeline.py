import logging
from enum import Enum
from io import BytesIO
from typing import Any, Dict, Optional

from fastapi import UploadFile
from pydantic import BaseModel

from .clean_text import CleanTextService
from .ingestion import FileIngestionRequest, FileIngestionService
from .ocr import OCRService
from .text_extraction import TextExtractionService

logger = logging.getLogger(__name__)


class ProcessingStage(str, Enum):
    INGESTION = "ingestion"
    TEXT_EXTRACTION = "text_extraction"
    OCR = "ocr"
    CLEANING = "cleaning"
    COMPLETED = "completed"


class FileProcessingResult(BaseModel):
    file_id: str
    stage: ProcessingStage
    content: Optional[str] = None
    metadata: Dict[str, Any] = {}
    errors: Dict[str, str] = {}


class FileProcessingPipeline:
    def __init__(self):
        self.ingestion_service = FileIngestionService()
        self.text_extraction = TextExtractionService()
        self.ocr_service = OCRService()
        self.clean_text = CleanTextService()

    async def process_file(
        self, file_data: bytes, file_name: str, content_type: str
    ) -> FileProcessingResult:
        """Process file through all pipeline stages"""
        result = FileProcessingResult(
            file_id=str(hash(file_data)), stage=ProcessingStage.INGESTION
        )

        try:
            # Create UploadFile for ingestion
            upload_file = UploadFile(filename=file_name, file=BytesIO(file_data))
            upload_file.content_type = content_type

            # Stage 1: Ingestion
            ingestion_request = FileIngestionRequest(file=upload_file)
            await self.ingestion_service.ingest_file(ingestion_request)
            result.stage = ProcessingStage.TEXT_EXTRACTION

            # Stage 2: Text Extraction
            extracted = await self.text_extraction.extract_text(file_data, file_name)
            result.metadata.update(extracted.get("metadata", {}))
            result.content = extracted.get("content", "")
            result.stage = ProcessingStage.OCR

            # Stage 3: OCR if needed (for images)
            if not result.content:
                ocr_result = await self.ocr_service.extract_text(file_data)
                result.content = ocr_result.get("text", "")
                result.metadata.update(ocr_result.get("metadata", {}))

            result.stage = ProcessingStage.CLEANING

            # Stage 4: Clean text
            if result.content:
                result.content = self.clean_text.clean_text(result.content)
                quality = self.clean_text.assess_quality(result.content)
                result.metadata["text_quality"] = quality.dict()

            result.stage = ProcessingStage.COMPLETED

        except Exception as e:
            logger.error(f"Pipeline failed at stage {result.stage}: {str(e)}")
            result.errors[result.stage.value] = str(e)

        return result

    async def shutdown(self):
        """Clean shutdown of all services"""
        await self.ingestion_service.shutdown()
