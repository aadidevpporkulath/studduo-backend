from typing import List, Dict, Any
import os
from pathlib import Path
import logging

from pypdf import PdfReader
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

from langchain.text_splitter import RecursiveCharacterTextSplitter
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Process PDFs with OCR support for scanned documents."""

    def __init__(self):
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap
        self.ocr_dpi = getattr(settings, "ocr_dpi", 200)
        self.ocr_grayscale = getattr(settings, "ocr_grayscale", True)

        # Set Tesseract path for Windows
        if os.path.exists(settings.tesseract_cmd):
            pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len,
        )

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF, with OCR fallback for scanned pages."""
        text = ""
        try:
            # Try digital text extraction first
            reader = PdfReader(pdf_path)
            digital_text = ""

            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    digital_text += page_text + "\n\n"

            # If we got substantial text, it's a digital PDF
            if len(digital_text.strip()) > 100:
                text = digital_text
                logger.info(f"Extracted digital text from {pdf_path}")
            else:
                # Likely a scanned PDF, use OCR
                logger.info(f"Attempting OCR on {pdf_path}")
                text = self._ocr_pdf(pdf_path)

        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {str(e)}")
            # Fallback to OCR if digital extraction fails
            try:
                text = self._ocr_pdf(pdf_path)
            except Exception as ocr_error:
                logger.error(
                    f"OCR also failed for {pdf_path}: {str(ocr_error)}")
                text = ""

        return text

    def _ocr_pdf(self, pdf_path: str) -> str:
        """Perform OCR on scanned PDF."""
        text = ""
        try:
            reader = PdfReader(pdf_path)
            total_pages = len(reader.pages)

            for page_index in range(total_pages):
                # Convert one page at a time to avoid loading the whole PDF into memory
                images = convert_from_path(
                    pdf_path,
                    dpi=self.ocr_dpi,
                    first_page=page_index + 1,
                    last_page=page_index + 1,
                    grayscale=self.ocr_grayscale,
                )

                if not images:
                    logger.warning(
                        f"No image produced for page {page_index + 1} of {pdf_path}")
                    continue

                image = images[0]
                page_text = pytesseract.image_to_string(image, lang='eng')
                text += f"\n\n--- Page {page_index + 1} ---\n\n{page_text}"

                # Explicitly release memory for this page
                image.close()
                del image
                logger.info(
                    f"OCR completed for page {page_index + 1} of {pdf_path} ({page_index + 1}/{total_pages})")

        except Exception as e:
            logger.error(f"OCR failed for {pdf_path}: {str(e)}")
            raise

        return text

    def process_document(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Process a PDF document and return chunks with metadata."""
        filename = Path(pdf_path).name
        text = self.extract_text_from_pdf(pdf_path)

        if not text or len(text.strip()) < 50:
            logger.warning(f"Insufficient text extracted from {filename}")
            return []

        # Split into chunks
        chunks = self.text_splitter.split_text(text)

        # Create documents with metadata
        documents = []
        for i, chunk in enumerate(chunks):
            if len(chunk.strip()) > 20:  # Skip very small chunks
                documents.append({
                    "text": chunk,
                    "metadata": {
                        "source": filename,
                        "chunk_id": i,
                        "total_chunks": len(chunks),
                        "file_path": pdf_path
                    }
                })

        logger.info(f"Processed {filename}: {len(documents)} chunks created")
        return documents

    def process_directory(self, directory: str = None) -> List[Dict[str, Any]]:
        """Process all PDFs in a directory."""
        if directory is None:
            directory = settings.knowledge_dir

        all_documents = []
        pdf_files = list(Path(directory).glob("*.pdf"))

        logger.info(f"Found {len(pdf_files)} PDF files to process")

        for pdf_path in pdf_files:
            try:
                docs = self.process_document(str(pdf_path))
                all_documents.extend(docs)
            except Exception as e:
                logger.error(f"Failed to process {pdf_path.name}: {str(e)}")
                continue

        logger.info(f"Total documents created: {len(all_documents)}")
        return all_documents


# Singleton instance
document_processor = DocumentProcessor()
