import fitz  # PyMuPDF
from typing import Dict, Any, List
from app.core.logging import logger

def parse_pdf(file_path: str) -> Dict[str, Any]:
    """
    High-fidelity extraction of PDF documents using PyMuPDF (fitz).
    Preserves page numbers, extracts metadata, detects scanned pages needing OCR.
    """
    doc = fitz.open(file_path)
    metadata = {
        "title": doc.metadata.get("title") or "",
        "author": doc.metadata.get("author") or "",
        "subject": doc.metadata.get("subject") or "",
        "keywords": doc.metadata.get("keywords") or "",
        "page_count": len(doc),
        "format": "PDF",
    }

    pages_content: List[Dict[str, Any]] = []
    scanned_pages_count = 0

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text").strip()
        image_list = page.get_images(full=True)

        is_scanned = False
        # If very little text but contains image(s), flag as scanned page
        if len(text) < 50 and len(image_list) > 0:
            is_scanned = True
            scanned_pages_count += 1

        pages_content.append({
            "page_number": page_num + 1,
            "text": text,
            "is_scanned": is_scanned,
            "image_count": len(image_list),
        })

    doc.close()

    is_scanned_likely = scanned_pages_count > (len(pages_content) / 2) if pages_content else False

    return {
        "metadata": metadata,
        "page_count": len(pages_content),
        "is_scanned_likely": is_scanned_likely,
        "pages": pages_content,
    }

