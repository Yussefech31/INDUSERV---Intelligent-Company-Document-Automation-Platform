import csv
from typing import Dict, Any, List

def parse_txt_or_csv(file_path: str, is_csv: bool = False) -> Dict[str, Any]:
    """
    Parses plain text, markdown, or CSV files with robust multi-encoding fallback.
    """
    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
    content = ""

    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc) as f:
                content = f.read()
            break
        except UnicodeDecodeError:
            continue

    if is_csv:
        # Format CSV cleanly
        lines = content.strip().splitlines()
        csv_reader = csv.reader(lines)
        formatted_rows = [" | ".join(row) for row in csv_reader]
        text_formatted = "\n".join(formatted_rows)
        return {
            "metadata": {"format": "CSV", "line_count": len(lines)},
            "page_count": max(1, len(lines) // 40),
            "is_scanned_likely": False,
            "text": text_formatted
        }

    return {
        "metadata": {"format": "TXT", "character_count": len(content)},
        "page_count": max(1, len(content) // 2500),
        "is_scanned_likely": False,
        "text": content
    }

