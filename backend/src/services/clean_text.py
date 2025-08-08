import logging
import re
import unicodedata
from difflib import SequenceMatcher
from enum import Enum
from typing import Dict, Optional

import ftfy
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class TextQualityScore(BaseModel):
    overall: float
    encoding: float
    noise: float
    duplicates: float
    structure: float


class CleanTextService:
    def __init__(self, min_similarity: float = 0.9):
        self.min_similarity = min_similarity

    def clean_text(self, text: str) -> str:
        """Apply all cleaning steps to text"""
        text = self.fix_encoding(text)
        text = self.remove_noise(text)
        text = self.normalize_text(text)
        return text

    def fix_encoding(self, text: str) -> str:
        """Fix encoding issues and normalize Unicode"""
        try:
            return ftfy.fix_text(text)
        except Exception as e:
            logger.error(f"Encoding fix failed: {str(e)}")
            return text

    def remove_noise(self, text: str) -> str:
        """Remove special characters and formatting artifacts"""
        # Remove non-printable chars except newlines
        text = re.sub(r"[^\x20-\x7E\n\r\t]", "", text)
        # Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def normalize_text(self, text: str) -> str:
        """Normalize text to standard form"""
        text = unicodedata.normalize("NFKC", text)
        text = text.lower()
        return text

    def detect_duplicates(self, text: str) -> Dict[str, float]:
        """Find duplicate sections in text"""
        lines = text.split("\n")
        duplicates = {}

        for i in range(len(lines)):
            for j in range(i + 1, len(lines)):
                ratio = SequenceMatcher(None, lines[i], lines[j]).ratio()
                if ratio > self.min_similarity:
                    duplicates[f"line_{i+1}-{j+1}"] = ratio

        return duplicates

    def assess_quality(self, text: str) -> TextQualityScore:
        """Assess overall text quality"""
        if not text:
            return TextQualityScore(
                overall=0.0, encoding=0.0, noise=0.0, duplicates=0.0, structure=0.0
            )

        # Encoding quality
        fixed_text = self.fix_encoding(text)
        encoding_score = 1.0 - (abs(len(fixed_text) - len(text)) / max(len(text), 1))

        # Noise score
        clean_text = self.remove_noise(text)
        noise_score = len(clean_text) / max(len(text), 1)

        # Duplicate score
        duplicates = self.detect_duplicates(text)
        duplicate_score = 1.0 - (len(duplicates) / max(len(text.split("\n")), 1))

        # Structure score (simple heuristic)
        line_count = len(text.split("\n"))
        word_count = len(text.split())
        structure_score = min(1.0, word_count / max(line_count, 1) / 10)

        return TextQualityScore(
            overall=(encoding_score + noise_score + duplicate_score + structure_score)
            / 4,
            encoding=encoding_score,
            noise=noise_score,
            duplicates=duplicate_score,
            structure=structure_score,
        )
