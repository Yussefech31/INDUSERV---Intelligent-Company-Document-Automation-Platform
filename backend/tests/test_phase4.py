import os
from pathlib import Path
import pytest
import docx
import fitz
import openpyxl

from app.services.generation.docx_generator import generate_docx
from app.services.generation.pdf_generator import generate_pdf
from app.services.generation.xlsx_generator import generate_xlsx

def test_generate_docx_file(tmp_path: Path):
    out_file = str(tmp_path / "test_doc.docx")
    generate_docx(
        output_path=out_file,
        title="Lettre Officielle de Candidature AO",
        category="procurement",
        content="## 1. Objet\nNous avons l'honneur de soumettre notre offre.\n\n- Attestation fiscale jointe\n- Kbis valide",
        company_name="INDUSERV Test",
        company_details="Paris, France",
        calculation_data={"result": 12000.0, "details": {"net_ht": 10000.0, "tva_amount": 2000.0}}
    )

    assert os.path.exists(out_file)
    assert os.path.getsize(out_file) > 1000

    doc = docx.Document(out_file)
    paragraph_text = " ".join(p.text for p in doc.paragraphs)
    table_text = " ".join(cell.text for t in doc.tables for row in t.rows for cell in row.cells)
    full_text = paragraph_text + " " + table_text

    assert "Lettre Officielle de Candidature AO" in full_text
    assert "INDUSERV Test" in full_text

def test_generate_pdf_file_with_french_accents(tmp_path: Path):
    out_file = str(tmp_path / "test_doc.pdf")
    generate_pdf(
        output_path=out_file,
        title="Rapport Financier & Certification des Éléments Éligibles",
        category="financial",
        content="## Synthèse des Opérations\nLes montants vérifiés intègrent la décomposition de TVA légale à 20% et 5.5%.\n\n> Données probantes certifiées conformes.",
        company_name="INDUSERV Technologies",
        company_details="123 Bd Industriel, Paris",
        calculation_data={"result": 2400.0, "details": {"net_ht": 2000.0, "tva_amount": 400.0}}
    )

    assert os.path.exists(out_file)
    assert os.path.getsize(out_file) > 1000

    pdf_doc = fitz.open(out_file)
    assert len(pdf_doc) >= 1
    page1_text = pdf_doc[0].get_text()
    assert "Rapport Financier" in page1_text
    assert "INDUSERV Technologies" in page1_text
    pdf_doc.close()

def test_generate_xlsx_file_with_formulas(tmp_path: Path):
    out_file = str(tmp_path / "test_doc.xlsx")
    generate_xlsx(
        output_path=out_file,
        title="Bordereau des Prix Unitaires",
        category="procurement",
        company_name="INDUSERV Technologies"
    )

    assert os.path.exists(out_file)
    assert os.path.getsize(out_file) > 1000

    wb = openpyxl.load_workbook(out_file, data_only=False)
    assert "Chiffrage_Bordereau" in wb.sheetnames
    assert "Synthèse_Informations" in wb.sheetnames
    ws = wb["Chiffrage_Bordereau"]
    assert "=C5*D5" in ws["E5"].value
    wb.close()

def test_generation_api_endpoint(client):
    payload = {
        "title": "Attestation d'Exécution Contractuelle",
        "category": "administrative",
        "format": "docx",
        "content": "Attestation officielle confirmant la réalisation intégrale des livrables."
    }
    res = client.post("/api/v1/generation/generate", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["format"] == "docx"
    assert data["file_size"] > 0
    assert "download_url" in data

    dl_res = client.get(data["download_url"])
    assert dl_res.status_code == 200
    assert len(dl_res.content) > 0
