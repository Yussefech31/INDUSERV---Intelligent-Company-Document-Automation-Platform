import pytest
from app.services.ai.free_provider import FreeAPIProvider
from app.services.workflows.tender_workflow import analyze_tender_dossier

def test_templates_catalog_listing_and_filtering(client):
    res = client.get("/api/v1/templates/")
    assert res.status_code == 200
    all_tpls = res.json()
    assert len(all_tpls) >= 8

    res_proc = client.get("/api/v1/templates/?category=procurement")
    assert res_proc.status_code == 200
    proc_tpls = res_proc.json()
    assert len(proc_tpls) >= 2
    for tpl in proc_tpls:
        assert tpl["category"] == "procurement"

def test_custom_template_creation(client):
    new_tpl = {
        "name": "Accord de Confidentialité NDA",
        "category": "legal",
        "code": "legal_nda_custom_2026",
        "description": "Modèle d'accord bilatéral de non-divulgation et secret des affaires.",
        "default_prompt": "Rédigez un accord de confidentialité bilatéral entre deux sociétés...",
        "supported_formats": "docx,pdf"
    }
    res = client.post(
        f"/api/v1/templates/?name={new_tpl['name']}&category={new_tpl['category']}&code={new_tpl['code']}&description={new_tpl['description']}&default_prompt={new_tpl['default_prompt']}&supported_formats={new_tpl['supported_formats']}"
    )
    assert res.status_code == 201
    created = res.json()
    assert created["code"] == new_tpl["code"]
    assert created["is_custom"] is True

@pytest.mark.asyncio
async def test_tender_analysis_workflow_execution():
    provider = FreeAPIProvider()
    tender_dce = (
        "APPEL D'OFFRES OUVERT N° AO-2026-IND-042\n"
        "Autorité Contractante : Direction Générale des Infrastructures Industrielles (DGII)\n"
        "Date limite de remise des offres : 25/03/2026 à 12h00\n"
        "Pièces obligatoires à joindre sous peine de rejet :\n"
        "- Déclaration de candidature DC1 et DC2\n"
        "- Extrait Kbis de moins de 3 mois\n"
        "- Attestation de vigilance URSSAF à jour\n"
        "- Certificat de qualification professionnelle ISO 9001\n"
        "- Chiffre d'affaires moyen des 3 dernières années supérieur à 2 000 000 €\n"
    )

    company_docs = "Dossier entreprise : Kbis valide, attestations URSSAF. Certificat ISO 9001 non fourni."

    result = await analyze_tender_dossier(provider, tender_dce, company_docs)
    assert "tender_reference" in result or "raw_analysis" in result
    assert "missing_or_unverified_items" in result

def test_task_history_endpoints(client):
    res = client.get("/api/v1/history/")
    assert res.status_code == 200
    assert isinstance(res.json(), list)
