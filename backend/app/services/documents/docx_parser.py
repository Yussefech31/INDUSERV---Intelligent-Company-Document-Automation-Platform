import docx
from typing import Dict, Any, List

def parse_docx(file_path: str) -> Dict[str, Any]:
    """
    Parses Word (.docx) documents preserving heading hierarchies, paragraphs, and tables.
    """
    doc = docx.Document(file_path)
    core_props = doc.core_properties

    metadata = {
        "title": core_props.title or "",
        "author": core_props.author or "",
        "created": str(core_props.created) if core_props.created else "",
        "format": "DOCX",
    }

    elements: List[Dict[str, Any]] = []
    current_section = "Introduction"

    # Extract paragraphs
    for p in doc.paragraphs:
        text = p.text.strip()
        if not text:
            continue

        style_name = p.style.name if p.style else ""
        if "Heading" in style_name or "Titre" in style_name:
            current_section = text
            elements.append({
                "type": "heading",
                "text": text,
                "section": current_section,
                "style": style_name
            })
        else:
            elements.append({
                "type": "paragraph",
                "text": text,
                "section": current_section,
            })

    # Extract tables
    for table_idx, table in enumerate(doc.tables):
        rows_data = []
        for row in table.rows:
            row_cells = [cell.text.strip().replace("\n", " ") for cell in row.cells]
            if any(row_cells):
                rows_data.append(" | ".join(row_cells))

        if rows_data:
            table_markdown = "\n".join(rows_data)
            elements.append({
                "type": "table",
                "text": f"--- TABLEAU {table_idx + 1} ---\n{table_markdown}",
                "section": current_section,
                "row_count": len(rows_data)
            })

    return {
        "metadata": metadata,
        "page_count": max(1, len(elements) // 8),  # Approximate page count for docx
        "is_scanned_likely": False,
        "elements": elements,
    }

