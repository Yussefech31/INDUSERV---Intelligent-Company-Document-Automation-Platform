from typing import List, Dict, Any

def approximate_tokens(text: str) -> int:
    """Rough estimation: ~1 token per 4 characters in French/English."""
    return max(1, len(text) // 4)

def split_text_into_chunks(text: str, max_chars: int = 1500, overlap_chars: int = 200) -> List[str]:
    """Sliding window chunking with paragraph-boundary preference."""
    if len(text) <= max_chars:
        return [text] if text.strip() else []

    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        if end >= len(text):
            chunks.append(text[start:].strip())
            break

        # Look for line break or period near the end
        break_pos = text.rfind("\n\n", start, end)
        if break_pos == -1 or break_pos < start + (max_chars // 2):
            break_pos = text.rfind(". ", start, end)
        if break_pos == -1 or break_pos < start + (max_chars // 2):
            break_pos = text.rfind("\n", start, end)
        if break_pos == -1 or break_pos < start + (max_chars // 2):
            break_pos = end

        chunks.append(text[start:break_pos].strip())
        start = max(start + 1, break_pos - overlap_chars)

    return [c for c in chunks if c]

def build_document_chunks(parsed_doc: Dict[str, Any], file_type: str) -> List[Dict[str, Any]]:
    """
    Constructs indexed chunks preserving document hierarchy and metadata.
    """
    raw_chunks: List[Dict[str, Any]] = []

    if file_type == "pdf":
        for page in parsed_doc.get("pages", []):
            page_text = page.get("text", "")
            page_num = page.get("page_number", 1)
            sub_chunks = split_text_into_chunks(page_text)
            for sub in sub_chunks:
                raw_chunks.append({
                    "text_content": sub,
                    "page_number": page_num,
                    "sheet_name": None,
                    "section_title": f"Page {page_num}",
                    "token_count": approximate_tokens(sub)
                })

    elif file_type == "docx":
        current_section = "Document"
        buffer_text = ""
        for elem in parsed_doc.get("elements", []):
            if elem.get("type") == "heading":
                if buffer_text:
                    sub_chunks = split_text_into_chunks(buffer_text)
                    for sub in sub_chunks:
                        raw_chunks.append({
                            "text_content": sub,
                            "page_number": None,
                            "sheet_name": None,
                            "section_title": current_section,
                            "token_count": approximate_tokens(sub)
                        })
                    buffer_text = ""
                current_section = elem.get("text", "")
            else:
                buffer_text += "\n" + elem.get("text", "")

        if buffer_text:
            sub_chunks = split_text_into_chunks(buffer_text)
            for sub in sub_chunks:
                raw_chunks.append({
                    "text_content": sub,
                    "page_number": None,
                    "sheet_name": None,
                    "section_title": current_section,
                    "token_count": approximate_tokens(sub)
                })

    elif file_type == "xlsx":
        for sheet in parsed_doc.get("sheets", []):
            sheet_name = sheet.get("sheet_name", "Feuille")
            text = sheet.get("text", "")
            sub_chunks = split_text_into_chunks(text)
            for sub in sub_chunks:
                raw_chunks.append({
                    "text_content": sub,
                    "page_number": None,
                    "sheet_name": sheet_name,
                    "section_title": f"Feuille Excel : {sheet_name}",
                    "token_count": approximate_tokens(sub)
                })

    else:  # txt or csv
        full_text = parsed_doc.get("text", "")
        sub_chunks = split_text_into_chunks(full_text)
        for idx, sub in enumerate(sub_chunks):
            raw_chunks.append({
                "text_content": sub,
                "page_number": None,
                "sheet_name": None,
                "section_title": f"Section {idx + 1}",
                "token_count": approximate_tokens(sub)
            })

    # Add chunk_index
    for idx, c in enumerate(raw_chunks):
        c["chunk_index"] = idx

    return raw_chunks

