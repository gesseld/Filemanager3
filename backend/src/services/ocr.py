import io
import logging
from typing import Any, Dict, Optional

import httpx
import pytesseract
from PIL import Image
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class OCRService:
    def __init__(
        self,
        tesseract_path: Optional[str] = None,
        mistral_api_key: Optional[str] = None,
    ):
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        self.mistral_api_key = mistral_api_key

    async def extract_text(
        self, image_data: bytes, language: str = "eng", use_mistral: bool = False
    ) -> Dict[str, Any]:
        """Extract text from image using OCR"""
        try:
            if use_mistral and self.mistral_api_key:
                return await self._extract_with_mistral(image_data)
            return self._extract_with_tesseract(image_data, language)
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            raise

    def _extract_with_tesseract(
        self, image_data: bytes, language: str
    ) -> Dict[str, Any]:
        """Use Tesseract OCR for text extraction"""
        image = Image.open(io.BytesIO(image_data))
        text = pytesseract.image_to_string(image, lang=language)

        return {
            "text": text,
            "engine": "tesseract",
            "language": language,
            "confidence": None,  # Tesseract doesn't provide overall confidence
        }

    async def _extract_with_mistral(self, image_data: bytes) -> Dict[str, Any]:
        """Use Mistral OCR API for complex documents"""
        if not self.mistral_api_key:
            raise ValueError("Mistral API key not configured")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.mistral.ai/v1/ocr",
                headers={"Authorization": f"Bearer {self.mistral_api_key}"},
                files={"file": image_data},
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()

    def get_supported_languages(self) -> list[str]:
        """Get list of supported languages"""
        return pytesseract.get_languages(config="")

    def assess_quality(self, image_data: bytes) -> float:
        """Assess OCR quality confidence score (0-1)"""
        try:
            image = Image.open(io.BytesIO(image_data))
            # Simple quality assessment based on image properties
            width, height = image.size
            area = width * height
            return min(1.0, area / (1000 * 1000))  # Normalize to 0-1 range
        except Exception as e:
            logger.error(f"Quality assessment failed: {str(e)}")
            return 0.0
