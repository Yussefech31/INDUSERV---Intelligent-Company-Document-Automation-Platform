import io
import pytest
from pathlib import Path
import docx
import openpyxl
import fitz

from app.services.documents.pdf_parser import parse_pdf
from app.services.documents.docx_parser import parse_docx
from app.services.documents.xlsx_parser import parse_xlsx
from app.services.retrieval.chunker import build_document_chunks
from app.services.retrieval.search import KeywordRetriever

def test_pdf_extraction(tmp_path: Path):
    pdf_path = tmp_path / "test_sample.pdf"
    doc = fitz.open()
    page1 = doc.new_page()
    page1.insert_text((50, 72), "INDUSERV Technologies - Cahier des Charges Appel d'Offres AO-2026-09.")
    page2 = doc.new_page()
    page2.insert_text((50, 72), "Exigences administratives : Kbis de moins de 3 mois, Attestation fiscale URSSAF.")
    doc.save(str(pdf_path))
    doc.close()

    parsed = parse_pdf(str(pdf_path))
    assert parsed["page_count"] == 2
    assert "INDUSERV" in parsed["pages"][0]["text"]
    assert "URSSAF" in parsed["pages"][1]["text"]

def test_docx_extraction(tmp_path: Path):
    docx_path = tmp_path / "test_sample.docx"
    doc = docx.Document()
    doc.add_heading("Candidature Marché Public", level=1)
    doc.add_paragraph("Présentation technique des moyens humains et matériels.")
    table = doc.add_table(rows=2, cols=2)
    table.cell(0, 0).text = "Poste"
    table.cell(0, 1).text = "Expérience"
    table.cell(1, 0).text = "Chef de Projet Senior"
    table.cell(1, 1).text = "12 ans"
    doc.save(str(docx_path))

    parsed = parse_docx(str(docx_path))
    assert len(parsed["elements"]) >= 2
    assert any("Candidature" in e["text"] for e in parsed["elements"])
    assert any("Chef de Projet" in e["text"] for e in parsed["elements"])

def test_xlsx_extraction(tmp_path: Path):
    xlsx_path = tmp_path / "test_sample.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Bordereau_Prix"
    ws.append(["Article", "Quantité", "Prix_Unitaire_HT", "Total_HT"])
    ws.append(["Serveur Calcul IA", 2, 4500, 9000])
    ws.append(["Maintenance Annuelle", 1, 1800, 1800])
    wb.save(str(xlsx_path))

    parsed = parse_xlsx(str(xlsx_path))
    assert parsed["metadata"]["sheet_count"] == 1
    assert "Bordereau_Prix" in parsed["metadata"]["sheets"]
    assert "Serveur Calcul IA" in parsed["sheets"][0]["text"]

def test_bm25_keyword_retriever():
    chunks = [
        {"id": 1, "text_content": "La société INDUSERV réalise la maintenance préventive des turbines.", "section_title": "Maintenance"},
        {"id": 2, "text_content": "Les conditions de paiement sont fixées à 30 jours fin de mois avec TVA 20%.", "section_title": "Paiement"},
        {"id": 3, "text_content": "La conformité administrative exige une attestation de vigilance et un Kbis valide.", "section_title": "Conformité"}
    ]

    retriever = KeywordRetriever()
    ranked = retriever.rank_chunks("Kbis attestation vigilance", chunks, top_k=2)
    assert len(ranked) >= 1
    assert ranked[0]["id"] == 3
    assert "_relevance_score" in ranked[0]
    assert ranked[0]["_relevance_score"] > 0

def test_document_upload_api(client):
    txt_content = b"Document de demonstration INDUSERV avec clause de confidentialite."
    files = [("files", ("charte_confidentialite.txt", txt_content, "text/plain"))]

    res = client.post("/api/v1/documents/upload", files=files)
    assert res.status_code == 201
    docs = res.json()
    assert len(docs) == 1
    doc_id = docs[0]["id"]
    assert docs[0]["original_filename"] == "charte_confidentialite.txt"
    assert docs[0]["chunk_count"] > 0

    detail_res = client.get(f"/api/v1/documents/{doc_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert len(detail["chunks"]) > 0
    assert "confidentialite" in detail["chunks"][0]["text_content"]
