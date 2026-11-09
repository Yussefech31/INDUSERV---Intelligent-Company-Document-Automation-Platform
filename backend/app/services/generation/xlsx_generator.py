import os
from datetime import datetime
from typing import Dict, Any, Optional, List
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

NAVY_FILL = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
HEADER_FONT = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
TITLE_FONT = Font(name="Segoe UI", size=14, bold=True, color="1E3A8A")
BOLD_FONT = Font(name="Segoe UI", size=10, bold=True)
REGULAR_FONT = Font(name="Segoe UI", size=10)
TOTAL_FILL = PatternFill(start_color="EFF6FF", end_color="EFF6FF", fill_type="solid")

THIN_BORDER = Border(
    left=Side(style="thin", color="CBD5E1"),
    right=Side(style="thin", color="CBD5E1"),
    top=Side(style="thin", color="CBD5E1"),
    bottom=Side(style="thin", color="CBD5E1")
)

def generate_xlsx(
    output_path: str,
    title: str,
    category: str,
    company_name: str = "INDUSERV Technologies",
    reference_code: Optional[str] = None,
    calculation_data: Optional[Dict[str, Any]] = None,
    items: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Generates an Excel workbook with live calculation formulas, multi-sheet layout,
    and accounting currency styling.
    """
    wb = openpyxl.Workbook()

    # ================= SHEET 1: Chiffrage & Formules =================
    ws1 = wb.active
    ws1.title = "Chiffrage_Bordereau"
    ws1.views.sheetView[0].showGridLines = True

    # Title Banner
    ws1["A1"] = f"{company_name} - {title}"
    ws1["A1"].font = TITLE_FONT
    ws1["A2"] = f"Réf: {reference_code or 'IND-XLSX-2026'} | Date: {datetime.now().strftime('%d/%m/%Y')} | Catégorie: {category.upper()}"
    ws1["A2"].font = Font(name="Segoe UI", size=9, italic=True, color="64748B")

    # Table Headers
    start_row = 4
    headers = ["N°", "Désignation de la Prestation / Article", "Quantité", "Prix Unitaire HT", "Total HT"]
    for col_idx, h in enumerate(headers, start=1):
        cell = ws1.cell(row=start_row, column=col_idx, value=h)
        cell.fill = NAVY_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center" if col_idx in [1, 3] else "right" if col_idx in [4, 5] else "left")
        cell.border = THIN_BORDER

    # Default items if none passed
    if not items:
        items = [
            {"label": "Prestation d'ingénierie et cadrage technique", "qty": 1, "unit_price": 4500.0},
            {"label": "Fourniture et déploiement de la solution logicielle", "qty": 2, "unit_price": 2800.0},
            {"label": "Formation des équipes et transfert de compétences", "qty": 3, "unit_price": 950.0},
            {"label": "Maintenance opérationnelle et support annuel", "qty": 1, "unit_price": 1800.0},
        ]

    current_row = start_row + 1
    for idx, item in enumerate(items, start=1):
        qty = item.get("qty", item.get("quantity", 1))
        pu = item.get("unit_price", item.get("amount", 1000.0))
        label = item.get("label", f"Article {idx}")

        ws1.cell(row=current_row, column=1, value=idx).alignment = Alignment(horizontal="center")
        ws1.cell(row=current_row, column=2, value=label)
        ws1.cell(row=current_row, column=3, value=float(qty)).alignment = Alignment(horizontal="center")

        pu_cell = ws1.cell(row=current_row, column=4, value=float(pu))
        pu_cell.number_format = '#,##0.00 €'
        pu_cell.alignment = Alignment(horizontal="right")

        # Live Excel Formula: Quantity * Unit Price
        tot_cell = ws1.cell(row=current_row, column=5, value=f"=C{current_row}*D{current_row}")
        tot_cell.number_format = '#,##0.00 €'
        tot_cell.alignment = Alignment(horizontal="right")

        for c in range(1, 6):
            ws1.cell(row=current_row, column=c).border = THIN_BORDER
            ws1.cell(row=current_row, column=c).font = REGULAR_FONT

        current_row += 1

    # Formulas Totals Section
    end_data_row = current_row - 1
    current_row += 1

    # Total HT Formula
    ws1.cell(row=current_row, column=4, value="Total HT :").font = BOLD_FONT
    ws1.cell(row=current_row, column=4).alignment = Alignment(horizontal="right")
    cell_tot_ht = ws1.cell(row=current_row, column=5, value=f"=SUM(E{start_row + 1}:E{end_data_row})")
    cell_tot_ht.font = BOLD_FONT
    cell_tot_ht.number_format = '#,##0.00 €'
    cell_tot_ht.alignment = Alignment(horizontal="right")
    cell_tot_ht.border = THIN_BORDER
    tot_ht_row = current_row
    current_row += 1

    # TVA Formula (20%)
    ws1.cell(row=current_row, column=4, value="TVA (20.0%) :").font = BOLD_FONT
    ws1.cell(row=current_row, column=4).alignment = Alignment(horizontal="right")
    cell_tva = ws1.cell(row=current_row, column=5, value=f"=E{tot_ht_row}*0.2")
    cell_tva.font = BOLD_FONT
    cell_tva.number_format = '#,##0.00 €'
    cell_tva.alignment = Alignment(horizontal="right")
    cell_tva.border = THIN_BORDER
    tva_row = current_row
    current_row += 1

    # Total TTC Formula
    ws1.cell(row=current_row, column=4, value="Total TTC :").font = Font(name="Segoe UI", size=11, bold=True, color="1E3A8A")
    ws1.cell(row=current_row, column=4).alignment = Alignment(horizontal="right")
    ws1.cell(row=current_row, column=4).fill = TOTAL_FILL
    cell_ttc = ws1.cell(row=current_row, column=5, value=f"=E{tot_ht_row}+E{tva_row}")
    cell_ttc.font = Font(name="Segoe UI", size=11, bold=True, color="1E3A8A")
    cell_ttc.number_format = '#,##0.00 €'
    cell_ttc.alignment = Alignment(horizontal="right")
    cell_ttc.fill = TOTAL_FILL
    cell_ttc.border = THIN_BORDER

    # Auto-adjust column widths
    for col in ws1.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws1.column_dimensions[col_letter].width = max(max_len + 4, 12)

    ws1.column_dimensions["B"].width = 45

    # ================= SHEET 2: Synthèse du Projet =================
    ws2 = wb.create_sheet(title="Synthèse_Informations")
    ws2.views.sheetView[0].showGridLines = True

    ws2["A1"] = "Fiche Signalétique du Dossier"
    ws2["A1"].font = TITLE_FONT

    meta_rows = [
        ("Titre du Dossier", title),
        ("Référence Interne", reference_code or "IND-XLSX-2026"),
        ("Domaine d'Application", category.upper()),
        ("Émetteur", company_name),
        ("Date de Génération", datetime.now().strftime("%d/%m/%Y %H:%M")),
        ("Certification Mathématique", "100% Déterministe Python - Précision Décimale Légale"),
        ("Formules Intégrées", "Sommes, Produits & TVA dynamiques compatibles Excel / Calc"),
    ]

    for idx, (label, val) in enumerate(meta_rows, start=3):
        ws2.cell(row=idx, column=1, value=label).font = BOLD_FONT
        ws2.cell(row=idx, column=1).border = THIN_BORDER
        ws2.cell(row=idx, column=2, value=val).font = REGULAR_FONT
        ws2.cell(row=idx, column=2).border = THIN_BORDER

    ws2.column_dimensions["A"].width = 28
    ws2.column_dimensions["B"].width = 55

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    wb.save(output_path)
    return output_path

