# Backend Services Documentation

## Implemented Services

1. **CleanTextService** (clean_text.py)
   - Provides text cleaning and quality assessment functionality
   - Methods: clean_text(), fix_encoding(), remove_noise(), normalize_text(), detect_duplicates(), assess_quality()

2. **FileIngestionService** (ingestion.py)
   - Handles file ingestion to multiple storage backends
   - Methods: ingest_file(), _process_file(), _store_local(), _store_google_drive(), _store_s3(), _generate_presigned_url()

3. **OCRService** (ocr.py)
   - Provides OCR text extraction from images
   - Methods: extract_text(), _extract_with_tesseract(), _extract_with_mistral(), assess_quality()

4. **FileProcessingPipeline** (pipeline.py)
   - Orchestrates file processing through multiple stages
   - Methods: process_file()

5. **TextExtractionService** (text_extraction.py)
   - Extracts text and metadata from documents
   - Methods: extract_text(), detect_language(), validate_file_type()
