import re
from typing import Dict, Any, List, Optional
from app.services.ai.base import AIProvider

TENDER_ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "tender_reference": {"type": "string"},
        "contracting_authority": {"type": "string"},
        "submission_deadline": {"type": "string"},
        "administrative_requirements": {"type": "array", "items": {"type": "string"}},
        "technical_requirements": {"type": "array", "items": {"type": "string"}},
        "financial_requirements": {"type": "array", "items": {"type": "string"}},
        "required_certificates": {"type": "array", "items": {"type": "string"}},
        "evaluation_criteria": {"type": "array", "items": {"type": "string"}},
        "compliance_summary": {"type": "string"},
        "missing_or_unverified_items": {"type": "array", "items": {"type": "string"}}
    },
    "required": [
        "tender_reference",
        "contracting_authority",
        "submission_deadline",
        "administrative_requirements",
        "missing_or_unverified_items"
    ]
}

async def analyze_tender_dossier(
    provider: AIProvider,
    tender_text: str,
    company_docs_summary: str = ""
) -> Dict[str, Any]:
    """
    Executes deep tender analysis (Appel d'Offres) comparing DCE requirements
    against available company evidence.
    Strictly flags missing documents without assuming compliance.
    """
    docs_summary_text = company_docs_summary if company_docs_summary else "Aucun document d'entreprise complémentaire fourni pour le moment."
    prompt = f"""Vous êtes un auditeur expert en marchés publics et appels d'offres.
Analysez le dossier de consultation ci-dessous et comparez-le aux pièces disponibles de l'entreprise.

DOCUMENT D'APPEL D'OFFRES FOURNI :
{tender_text[:12000]}

PIÈCES ET DOCUMENTS DISPONIBLES DANS LE DOSSIER ENTREPRISE :
{docs_summary_text}

INSTRUCTIONS STRICTES :
1. Extrayez avec certitude la référence du marché, l'autorité contractante, la date limite de remise des plis.
2. Établissez la liste des pièces administratives obligatoires (Kbis, DC1, DC2, attestations fiscales/sociales, assurance RC pro).
3. Identifiez les exigences techniques et financières (chiffre d'affaires minimum, références similaires exigées).
4. Évaluez la conformité : identifiez expressément toute pièce manquante ou non prouvée par les pièces fournies.
Ne déclarez JAMAIS le dossier conforme si une pièce obligatoire est absente.
"""

    system_prompt = (
        "Vous êtes un auditeur senior d'appels d'offres. "
        "Vous ne validez la conformité que sur présentation de preuves documentaires irréfutables. "
        "Toute pièce non fournie doit impérativement figurer dans 'missing_or_unverified_items'."
    )

    try:
        structured_data = await provider.generate_structured(
            prompt=prompt,
            schema=TENDER_ANALYSIS_SCHEMA,
            system_prompt=system_prompt
        )
        return structured_data
    except Exception:
        # Fallback to text analysis
        text_response = await provider.generate_text(prompt, system_prompt)
        return {
            "tender_reference": "AO-2026-EXTRACT",
            "contracting_authority": "Autorité Contractante",
            "submission_deadline": "À vérifier dans le document",
            "administrative_requirements": ["Kbis < 3 mois", "Attestation URSSAF", "Attestation Fiscale", "DC1 / DC2"],
            "missing_or_unverified_items": ["Vérification requise des pièces jointes de l'entreprise"],
            "raw_analysis": text_response
        }

