import os
from datetime import datetime
from typing import Dict, Any, Optional, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable,
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas that dynamically counts total pages and writes 'Page X sur Y'
    along with running header and footer.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Running Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(2 * cm, 28.5 * cm, "INDUSERV Technologies | Document d'Entreprise")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(2 * cm, 28.3 * cm, 19 * cm, 28.3 * cm)

        # Running Footer
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(2 * cm, 1.8 * cm, 19 * cm, 1.8 * cm)

        footer_text = f"Page {self._pageNumber} sur {page_count}"
        self.drawRightString(19 * cm, 1.3 * cm, footer_text)
        self.drawString(2 * cm, 1.3 * cm, "Document confidentiel à usage exclusif - Certifié INDUSERV 2026")

        self.restoreState()

def generate_pdf(
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
    Generates an executive-ready PDF report using ReportLab with French UTF-8 typography,
    accented characters, structured layout, and calculation summaries.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2.2 * cm,
        bottomMargin=2.2 * cm,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    style_company = ParagraphStyle(
        "CompanyHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#1E3A8A"),
    )
    style_details = ParagraphStyle(
        "CompanyDetails",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#475569"),
    )
    style_meta = ParagraphStyle(
        "MetaDate",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        alignment=2,  # Right align
        textColor=colors.HexColor("#334155"),
    )
    style_title = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1E3A8A"),
        spaceAfter=10,
    )
    style_h2 = ParagraphStyle(
        "Heading2Custom",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#2563EB"),
        spaceBefore=12,
        spaceAfter=6,
    )
    style_h3 = ParagraphStyle(
        "Heading3Custom",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#334155"),
        spaceBefore=8,
        spaceAfter=4,
    )
    style_body = ParagraphStyle(
        "BodyCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=6,
    )
    style_bullet = ParagraphStyle(
        "BulletCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        leftIndent=15,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=3,
    )

    story = []

    # 1. Company Letterhead Header Table
    clean_details = company_details.replace("\n", "<br/>") if company_details else "123 Bd Industriel - Paris"
    left_header = Paragraph(f"<b>{company_name}</b><br/>{clean_details}", style_details)
    right_header = Paragraph(
        f"<b>Réf :</b> {reference_code or 'IND-2026-DOC'}<br/>"
        f"<b>Date :</b> {datetime.now().strftime('%d/%m/%Y')}<br/>"
        f"<b>Catégorie :</b> {category.upper()}",
        style_meta
    )

    hdr_table = Table([[left_header, right_header]], colWidths=[10 * cm, 7 * cm])
    hdr_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(hdr_table)
    story.append(Spacer(1, 15))

    # Divider bar
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563EB"), spaceAfter=15))

    # 2. Title
    story.append(Paragraph(title, style_title))
    story.append(Spacer(1, 8))

    # 3. Content body parsing
    lines = content.strip().splitlines()
    for line in lines:
        l = line.strip()
        if not l:
            story.append(Spacer(1, 4))
            continue

        if l.startswith("### "):
            story.append(Paragraph(l[4:], style_h3))
        elif l.startswith("## "):
            story.append(Paragraph(l[3:], style_h2))
        elif l.startswith("# "):
            story.append(Paragraph(l[2:], style_h2))
        elif l.startswith(("- ", "* ")):
            story.append(Paragraph(f"• {l[2:]}", style_bullet))
        elif l.startswith("> "):
            callout = Paragraph(f"<i>{l[2:]}</i>", style_details)
            t_callout = Table([[callout]], colWidths=[17 * cm])
            t_callout.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LINEBEFORE", (0, 0), (-1, -1), 3, colors.HexColor("#3B82F6")),
            ]))
            story.append(t_callout)
            story.append(Spacer(1, 4))
        else:
            # Safe HTML escape for XML-based Paragraph
            safe_text = l.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(safe_text, style_body))

    # 4. Calculation Summary Table (if provided)
    if calculation_data:
        story.append(Spacer(1, 14))
        story.append(Paragraph("<b>RÉCAPITULATIF FINANCIER CERTIFIÉ</b>", style_h2))

        details = calculation_data.get("details", {})
        currency = calculation_data.get("currency", "EUR")

        data_rows = [
            [Paragraph("<b>Désignation</b>", style_details), Paragraph("<b>Montant</b>", style_details)]
        ]

        items = [
            ("Montant Total HT", details.get("net_ht") or details.get("gross_ht") or calculation_data.get("inputs", {}).get("ht_amount")),
            ("Remise Commerciale", details.get("discount_amount")),
            ("TVA Légale", details.get("tva_amount") or details.get("total_tva")),
            ("Total Général TTC", calculation_data.get("result")),
        ]

        for label, val in items:
            if val is not None:
                val_str = f"{float(val):,.2f} {currency}".replace(",", " ")
                data_rows.append([Paragraph(label, style_body), Paragraph(f"<b>{val_str}</b>", style_body)])

        calc_tbl = Table(data_rows, colWidths=[11 * cm, 6 * cm])
        calc_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ]))
        story.append(calc_tbl)

    # 5. Signatures
    story.append(Spacer(1, 20))
    sig_data = [
        [
            Paragraph("<b>Pour le Client / L'Autorité :</b><br/><br/><br/><br/>Nom et Signature", style_details),
            Paragraph(f"<b>Pour {company_name} :</b><br/><br/><br/><br/>Direction Générale", style_details)
        ]
    ]
    sig_table = Table(sig_data, colWidths=[8.5 * cm, 8.5 * cm])
    sig_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBEFORE", (0, 0), (0, 0), 1, colors.HexColor("#E2E8F0")),
        ("LINEBEFORE", (1, 0), (1, 0), 1, colors.HexColor("#E2E8F0")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(KeepTogether(sig_table))

    # Build PDF with NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    return output_path

