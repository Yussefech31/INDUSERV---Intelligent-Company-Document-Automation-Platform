import uuid
from pathlib import Path
from typing import Dict, Any, Optional
from app.core.config import settings
from app.services.generation.docx_generator import generate_docx
from app.services.generation.pdf_generator import generate_pdf
from app.services.generation.xlsx_generator import generate_xlsx

def create_document(
    format_type: str,
    title: str,
    category: str,
    content: str = "",
    company_name: str = "INDUSERV Technologies",
    company_details: str = "",
    reference_code: Optional[str] = None,
    calculation_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Unified entry point for generating corporate documents (DOCX, PDF, XLSX).
    """
    settings.GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    clean_title = "".join(c for c in title if c.isalnum() or c in (" ", "-", "_")).strip()
    safe_name_base = f"{clean_title[:30]}_{uuid.uuid4().hex[:8]}"

    if format_type.lower() == "docx":
        filename = f"{safe_name_base}.docx"
        output_path = settings.GENERATED_DIR / filename
        generate_docx(
            output_path=str(output_path),
            title=title,
            category=category,
            content=content,
            company_name=company_name,
            company_details=company_details,
            reference_code=reference_code,
            calculation_data=calculation_data
        )

    elif format_type.lower() == "pdf":
        filename = f"{safe_name_base}.pdf"
        output_path = settings.GENERATED_DIR / filename
        generate_pdf(
            output_path=str(output_path),
            title=title,
            category=category,
            content=content,
            company_name=company_name,
            company_details=company_details,
            reference_code=reference_code,
            calculation_data=calculation_data
        )

    elif format_type.lower() in ["xlsx", "excel"]:
        filename = f"{safe_name_base}.xlsx"
        output_path = settings.GENERATED_DIR / filename
        generate_xlsx(
            output_path=str(output_path),
            title=title,
            category=category,
            company_name=company_name,
            reference_code=reference_code,
            calculation_data=calculation_data
        )

    else:
        raise ValueError(f"Format de document non supporté: {format_type}. Formats valides: docx, pdf, xlsx")

    file_size = output_path.stat().st_size if output_path.exists() else 0

    return {
        "filename": filename,
        "file_path": str(output_path),
        "format": format_type.lower(),
        "file_size": file_size,
        "title": title,
        "category": category
    }

