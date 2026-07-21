"""Tesseract OCR adapter."""
from __future__ import annotations

import io
import logging
from PIL import Image
import pytesseract

log = logging.getLogger(__name__)


async def extract_text(image_or_pdf_bytes: bytes) -> str:
    """Uses Tesseract OCR to extract text from images and pdf2image for PDFs."""
    if not image_or_pdf_bytes:
        return ""
        
    try:
        # Check if PDF magic number
        if image_or_pdf_bytes.startswith(b"%PDF"):
            from pdf2image import convert_from_bytes
            # Convert PDF bytes to a list of PIL Images
            images = convert_from_bytes(image_or_pdf_bytes)
            text_parts = []
            for i, img in enumerate(images):
                log.info(f"Running OCR on PDF page {i+1}")
                text_parts.append(pytesseract.image_to_string(img))
            return "\n\n".join(text_parts)
        else:
            # Assume image (JPEG, PNG, etc)
            img = Image.open(io.BytesIO(image_or_pdf_bytes))
            log.info("Running OCR on image")
            return pytesseract.image_to_string(img)
            
    except Exception as e:
        log.error("Tesseract OCR failed: %s", e)
        return f"[OCR Failed] Ensure tesseract-ocr and poppler-utils are installed. Error: {e}"
