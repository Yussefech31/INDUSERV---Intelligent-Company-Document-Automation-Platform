import os
import openpyxl
from pathlib import Path
from app.core.config import settings
from app.services.generation.docx_generator import generate_docx
from app.services.generation.pdf_generator import generate_pdf
from app.services.generation.xlsx_generator import generate_xlsx
from app.services.documents.extractor import extract_and_chunk_document
from app.database.session import SessionLocal
from app.models.entities import Document, DocumentChunk

def create_sample_files():
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    settings.TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Sample PDF: Tender DCE
    pdf_path = settings.UPLOAD_DIR / "DCE_Appel_Offres_Infrastructures_2026.pdf"
    if not pdf_path.exists():
        pdf_content = (
            "## REGLEMENT DE LA CONSULTATION (RC) - APPEL D'OFFRES N° AO-2026-IND-042\n"
            "**Autorité Contractante :** Direction Générale des Infrastructures Industrielles (DGII)\n"
            "**Date limite de remise des offres :** 25/03/2026 à 12h00 précises.\n\n"
            "### 1. Objet de la consultation\n"
            "Le présent marché a pour objet la modernisation et l'automatisation des installations techniques "
            "et de la documentation opérationnelle des sites industriels.\n\n"
            "### 2. Pièces administratives obligatoires (sous peine d'irrecevabilité)\n"
            "- Formulaire DC1 (Lettre de candidature et désignation du mandataire)\n"
            "- Formulaire DC2 (Déclaration du candidat individuel ou du membre du groupement)\n"
            "- Extrait du registre du commerce et des sociétés (Kbis) datant de moins de 3 mois\n"
            "- Attestations fiscales et sociales de régularité (URSSAF, Impôts)\n"
            "- Certificat de conformité aux normes ISO 9001 et ISO 14001\n"
            "- Attestation d'assurance responsabilité civile professionnelle en cours de validité\n\n"
            "### 3. Exigences financières et techniques minimales\n"
            "- Chiffre d'affaires annuel moyen sur les 3 derniers exercices supérieur à 1 500 000 € HT\n"
            "- Au moins 3 références probantes sur des prestations industrielles similaires exécutées au cours des 5 dernières années\n"
            "- Équipe dédiée comprenant au minimum 1 Chef de Projet certifié et 2 Ingénieurs d'application\n\n"
            "### 4. Critères de jugement des offres\n"
            "- Valeur technique de la proposition (méthodologie, planning et qualifications) : 60%\n"
            "- Prix des prestations (bordereau des prix unitaires et montant global) : 40%"
        )
        generate_pdf(
            output_path=str(pdf_path),
            title="Dossier de Consultation - Appel d'Offres AO-2026-IND-042",
            category="procurement",
            content=pdf_content,
            company_name="DGII - Direction Générale des Infrastructures",
            company_details="Ministère de l'Industrie, 75007 Paris",
            reference_code="AO-2026-IND-042"
        )

    # 2. Sample DOCX: Technical Proposal
    docx_path = settings.UPLOAD_DIR / "Offre_Technique_INDUSERV_Technologies.docx"
    if not docx_path.exists():
        docx_content = (
            "## 1. Présentation de la Société et Capacités Techniques\n"
            "INDUSERV Technologies est spécialisée depuis 15 ans dans l'ingénierie, "
            "la maintenance industrielle et l'automatisation des processus documentaires critiques.\n\n"
            "## 2. Moyens Humains Dédiés au Marché\n"
            "- 1 Chef de Projet Senior : 14 années d'expérience en management de projets industriels\n"
            "- 3 Ingénieurs Systèmes certifiés en automatisation et conformité\n"
            "- 2 Techniciens d'intervention sur site habilités risques chimiques et électriques\n\n"
            "## 3. Références Similaires Vérifiées\n"
            "- Projet AERO-2024 : Modernisation documentaire pour équipementier aéronautique (budget 450 000 € HT)\n"
            "- Projet ENERGIE-2023 : Déploiement de procédures d'exploitation sur 4 centrales thermiques (budget 820 000 € HT)\n"
            "- Projet CHIM-2025 : Automatisation de la gestion documentaire QHSE (budget 310 000 € HT)\n\n"
            "## 4. Engagements RSE et Délais\n"
            "INDUSERV s'engage à respecter un délai de mobilisation de 10 jours ouvrés dès notification de l'ordre de service."
        )
        generate_docx(
            output_path=str(docx_path),
            title="Mémoire Technique & Dossier de Compétences",
            category="procurement",
            content=docx_content,
            company_name="INDUSERV Technologies",
            company_details="123 Bd Industriel, 75008 Paris - SIRET 892 451 098 00014",
            reference_code="IND-TECH-2026"
        )

    # 3. Sample XLSX: Price Schedule
    xlsx_path = settings.UPLOAD_DIR / "Bordereau_Prix_Devis_Equipements.xlsx"
    if not xlsx_path.exists():
        sample_items = [
            {"label": "Audit préalable des installations et diagnostic documentaire", "qty": 1, "unit_price": 4800.0},
            {"label": "Conception de l'architecture d'automatisation logicielle", "qty": 1, "unit_price": 9500.0},
            {"label": "Fourniture de licences logicielles et modules de calcul", "qty": 4, "unit_price": 1250.0},
            {"label": "Session de formation utilisateurs et administrateurs (par jour)", "qty": 5, "unit_price": 850.0},
            {"label": "Maintenance préventive et support technique annuel (niveau 2 & 3)", "qty": 1, "unit_price": 3600.0},
        ]
        generate_xlsx(
            output_path=str(xlsx_path),
            title="Bordereau des Prix Unitaires & Décomposition du Prix Global",
            category="financial",
            company_name="INDUSERV Technologies",
            reference_code="BPU-2026-IND",
            items=sample_items
        )

    # Ingest into DB if not present
    from app.database.session import engine, Base
    from app.database.seed import seed_database
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
        sample_files = [pdf_path, docx_path, xlsx_path]
        for fpath in sample_files:
            existing = db.query(Document).filter(Document.filename == fpath.name).first()
            if not existing and fpath.exists():
                res = extract_and_chunk_document(str(fpath), fpath.name)
                doc = Document(
                    filename=fpath.name,
                    original_filename=fpath.name,
                    file_path=str(fpath),
                    file_type=res["file_type"],
                    file_size=fpath.stat().st_size,
                    mime_type="application/pdf" if fpath.suffix == ".pdf" else "application/octet-stream",
                    page_count=res.get("page_count", 1),
                    chunk_count=res.get("chunk_count", 0),
                    status="processed",
                    metadata_json=res.get("metadata_json", "{}"),
                    is_scanned_likely=False
                )
                db.add(doc)
                db.commit()
                db.refresh(doc)

                for c in res.get("chunks", []):
                    chunk_record = DocumentChunk(
                        document_id=doc.id,
                        chunk_index=c["chunk_index"],
                        text_content=c["text_content"],
                        page_number=c.get("page_number"),
                        sheet_name=c.get("sheet_name"),
                        section_title=c.get("section_title"),
                        token_count=c.get("token_count", 0)
                    )
                    db.add(chunk_record)
                db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_files()
    print("Sample documents generated and indexed successfully.")
