import json
from pathlib import Path
from typing import Dict, Any, List
from app.services.documents.pdf_parser import parse_pdf
from app.services.documents.docx_parser import parse_docx
from app.services.documents.xlsx_parser import parse_xlsx
from app.services.documents.txt_parser import parse_txt_or_csv
from app.services.retrieval.chunker import build_document_chunks
from app.core.logging import logger

def extract_and_chunk_document(file_path: str, original_filename: str) -> Dict[str, Any]:
    """
    Unified extraction pipeline for INDUSERV.
    Validates file format, extracts structured content, metadata, and generates chunks.
    """
    path = Path(file_path)
    extension = path.suffix.lower().lstrip(".")

    try:
        if extension == "pdf":
            parsed = parse_pdf(file_path)
            file_type = "pdf"
        elif extension in ["docx", "doc"]:
            parsed = parse_docx(file_path)
            file_type = "docx"
        elif extension in ["xlsx", "xls"]:
            parsed = parse_xlsx(file_path)
            file_type = "xlsx"
        elif extension == "csv":
            parsed = parse_txt_or_csv(file_path, is_csv=True)
            file_type = "csv"
        else:
            parsed = parse_txt_or_csv(file_path, is_csv=False)
            file_type = "txt"

        # Generate indexed chunks
        chunks = build_document_chunks(parsed, file_type)

        return {
            "success": True,
            "file_type": file_type,
            "page_count": parsed.get("page_count", 1),
            "is_scanned_likely": parsed.get("is_scanned_likely", False),
            "metadata_json": json.dumps(parsed.get("metadata", {}), ensure_ascii=False),
            "chunks": chunks,
            "chunk_count": len(chunks)
        }
    except Exception as e:
        logger.error(f"Error extracting document {original_filename}: {e}", exc_info=True)
        return {
            "success": False,
            "file_type": extension,
            "error_message": str(e),
            "page_count": 1,
            "is_scanned_likely": False,
            "metadata_json": json.dumps({"error": str(e)}),
            "chunks": [],
            "chunk_count": 0
        }

