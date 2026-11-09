import openpyxl
import pandas as pd
from typing import Dict, Any, List

def parse_xlsx(file_path: str) -> Dict[str, Any]:
    """
    Parses Excel (.xlsx) workbooks preserving sheet names, table layouts,
    numeric formats, and column structures.
    """
    wb = openpyxl.load_workbook(file_path, data_only=True)
    sheet_names = wb.sheetnames

    metadata = {
        "sheets": sheet_names,
        "sheet_count": len(sheet_names),
        "format": "XLSX"
    }

    sheets_content: List[Dict[str, Any]] = []

    for name in sheet_names:
        try:
            df = pd.read_excel(file_path, sheet_name=name)
            # Remove entirely empty rows and columns
            df_cleaned = df.dropna(how="all").dropna(axis=1, how="all")

            # Convert to markdown representation
            table_md = df_cleaned.to_markdown(index=False) if not df_cleaned.empty else "Feuille vide"

            sheets_content.append({
                "sheet_name": name,
                "rows": len(df_cleaned),
                "columns": list(df_cleaned.columns) if not df_cleaned.empty else [],
                "text": f"### Feuille : {name}\n{table_md}",
                "summary": f"Feuille '{name}' : {len(df_cleaned)} lignes, {len(df_cleaned.columns)} colonnes"
            })
        except Exception as e:
            sheets_content.append({
                "sheet_name": name,
                "rows": 0,
                "columns": [],
                "text": f"Erreur de lecture de la feuille {name}: {str(e)}",
                "summary": f"Erreur feuille {name}"
            })

    wb.close()

    return {
        "metadata": metadata,
        "page_count": len(sheet_names),
        "is_scanned_likely": False,
        "sheets": sheets_content
    }

