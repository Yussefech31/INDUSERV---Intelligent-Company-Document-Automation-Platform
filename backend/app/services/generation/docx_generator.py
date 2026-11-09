import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex: str):
    """Set background color of a docx table cell."""
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def generate_docx(
    output_path: str,
    title: str,
    category: str,
    content: str,
    company_name: str = "INDUSERV Technologies",
    company_details: str = "",
    reference_code: Optional[str] = None,
    calculation_data: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generates a professional corporate Word (.docx) document with headers,
    metadata table, styled headings, content sections, calculation tables, and signature blocks.
    """
    doc = docx.Document()

    # Set 1-inch margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

        # Header: Company Name & Confidentiality
        header = section.header
        hp = header.paragraphs[0]
        hp.text = f"{company_name} | Document Officiel d'Entreprise"
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        if hp.runs:
            hp.runs[0].font.size = Pt(8.5)
            hp.runs[0].font.color.rgb = RGBColor(120, 120, 120)

        # Footer: Reference and Page Notice
        footer = section.footer
        fp = footer.paragraphs[0]
        fp.text = f"Réf: {reference_code or 'IND-DOC-2026'} | Strictement Confidentiel | Page 1"
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if fp.runs:
            fp.runs[0].font.size = Pt(8.5)
            fp.runs[0].font.color.rgb = RGBColor(140, 140, 140)

    # 1. Company Information Block (Letterhead)
    header_table = doc.add_table(rows=1, cols=2)
    header_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    header_table.autofit = False
    header_table.columns[0].width = Inches(3.5)
    header_table.columns[1].width = Inches(3.0)

    # Left cell: Company details
    cell_left = header_table.cell(0, 0)
    p_comp = cell_left.paragraphs[0]
    r_name = p_comp.add_run(f"{company_name}\n")
    r_name.font.size = Pt(13)
    r_name.font.bold = True
    r_name.font.color.rgb = RGBColor(30, 58, 138)  # Deep Navy

    if company_details:
        r_det = p_comp.add_run(company_details)
        r_det.font.size = Pt(8.5)
        r_det.font.color.rgb = RGBColor(80, 80, 80)

    # Right cell: Reference and Date
    cell_right = header_table.cell(0, 1)
    p_date = cell_right.paragraphs[0]
    p_date.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_date = p_date.add_run(
        f"Date : {datetime.now().strftime('%d/%m/%Y')}\n"
        f"Réf. Dossier : {reference_code or 'IND-2026-DOC'}\n"
        f"Domaine : {category.upper()}"
    )
    r_date.font.size = Pt(9)
    r_date.font.color.rgb = RGBColor(100, 100, 100)

    doc.add_paragraph()  # Spacing

    # 2. Document Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r_title = p_title.add_run(title)
    r_title.font.size = Pt(18)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(30, 58, 138)

    # Accent divider line below title
    p_line = doc.add_paragraph()
    p_line.paragraph_format.space_after = Pt(14)
    r_line = p_line.add_run("―" * 45)
    r_line.font.color.rgb = RGBColor(37, 99, 235)  # Blue 600

    # 3. Main Content Rendering
    # Parse markdown paragraphs, headings (#, ##), and bullet points
    lines = content.strip().splitlines()
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            doc.add_paragraph()
            continue

        if line_clean.startswith("### "):
            h = doc.add_paragraph()
            h.paragraph_format.space_before = Pt(10)
            h.paragraph_format.space_after = Pt(4)
            r = h.add_run(line_clean[4:])
            r.font.size = Pt(12)
            r.font.bold = True
            r.font.color.rgb = RGBColor(51, 65, 85)
        elif line_clean.startswith("## "):
            h = doc.add_paragraph()
            h.paragraph_format.space_before = Pt(14)
            h.paragraph_format.space_after = Pt(4)
            r = h.add_run(line_clean[3:])
            r.font.size = Pt(13)
            r.font.bold = True
            r.font.color.rgb = RGBColor(37, 99, 235)
        elif line_clean.startswith("# "):
            h = doc.add_paragraph()
            h.paragraph_format.space_before = Pt(18)
            h.paragraph_format.space_after = Pt(6)
            r = h.add_run(line_clean[2:])
            r.font.size = Pt(14)
            r.font.bold = True
            r.font.color.rgb = RGBColor(30, 58, 138)
        elif line_clean.startswith(("- ", "* ")):
            p = doc.add_paragraph(style="List Bullet")
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(line_clean[2:])
            r.font.size = Pt(10)
        elif line_clean.startswith("> "):
            # Callout box style
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.4)
            r = p.add_run(line_clean[2:])
            r.font.size = Pt(9.5)
            r.font.italic = True
            r.font.color.rgb = RGBColor(71, 85, 105)
        else:
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.15
            r = p.add_run(line_clean)
            r.font.size = Pt(10)

    # 4. Calculation Summary Table (if calculation data provided)
    if calculation_data:
        doc.add_paragraph()
        h_calc = doc.add_paragraph()
        r_calc_title = h_calc.add_run("RÉCAPITULATIF FINANCIER CERTIFIÉ")
        r_calc_title.font.bold = True
        r_calc_title.font.size = Pt(12)
        r_calc_title.font.color.rgb = RGBColor(30, 58, 138)

        calc_table = doc.add_table(rows=1, cols=2)
        calc_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        calc_table.columns[0].width = Inches(4.0)
        calc_table.columns[1].width = Inches(2.5)

        hdr_cells = calc_table.rows[0].cells
        hdr_cells[0].text = "Élément / Désignation"
        hdr_cells[1].text = "Montant Certifié"
        for c in hdr_cells:
            set_cell_background(c, "1E3A8A")
            for p in c.paragraphs:
                for run in p.runs:
                    run.font.bold = True
                    run.font.color.rgb = RGBColor(255, 255, 255)

        details = calculation_data.get("details", {})
        currency = calculation_data.get("currency", "EUR")

        items_to_display = [
            ("Montant Total HT", details.get("net_ht") or details.get("gross_ht") or calculation_data.get("inputs", {}).get("ht_amount")),
            ("Remise Déduite", details.get("discount_amount")),
            ("Total TVA Légale", details.get("tva_amount") or details.get("total_tva")),
            ("Total Général TTC", calculation_data.get("result")),
        ]

        for label, val in items_to_display:
            if val is not None:
                row = calc_table.add_row()
                row.cells[0].text = label
                row.cells[1].text = f"{float(val):,.2f} {currency}".replace(",", " ")
                if "TTC" in label:
                    set_cell_background(row.cells[0], "EFF6FF")
                    set_cell_background(row.cells[1], "EFF6FF")
                    for c in row.cells:
                        for p in c.paragraphs:
                            for r in p.runs:
                                r.font.bold = True

    # 5. Formal Signature Block
    doc.add_paragraph()
    sig_table = doc.add_table(rows=1, cols=2)
    sig_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    sig_table.columns[0].width = Inches(3.2)
    sig_table.columns[1].width = Inches(3.2)

    c0 = sig_table.cell(0, 0)
    p0 = c0.paragraphs[0]
    p0.add_run("Pour le Client / L'Autorité Contractante :\n\n\n\nNom, Date et Signature précédés de 'Bon pour accord'")
    p0.runs[0].font.size = Pt(8.5)

    c1 = sig_table.cell(0, 1)
    p1 = c1.paragraphs[0]
    p1.add_run(f"Pour {company_name} :\n\n\n\nDirection Générale / Mandataire Habilité")
    p1.runs[0].font.size = Pt(8.5)

    # Save to disk
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    return output_path

