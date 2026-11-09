from sqlalchemy.orm import Session
from app.models.entities import SystemPrompt, AIProviderSetting, UserSetting, Template
from app.core.config import settings

DEFAULT_SYSTEM_PROMPT = (
    "You are a professional company document automation assistant. Your role is to analyze company documents, "
    "understand business requirements, extract reliable information, perform accurate calculations using available tools, "
    "and generate professional administrative, financial, commercial, HR, procurement, and operational documents.\n\n"
    "Always use the provided documents as your primary sources of information. Never invent company details, figures, dates, "
    "certifications, legal references, or financial values.\n\n"
    "Clearly distinguish between verified information, assumptions, and missing information.\n\n"
    "When information is insufficient, ask the user for clarification rather than fabricating content.\n\n"
    "Write professionally, using the language requested by the user. Default to professional French.\n\n"
    "For calculations, use deterministic Python functions rather than mental arithmetic. Explain the calculation method "
    "and preserve traceability to the source data."
)

TENDER_SYSTEM_PROMPT = (
    "Vous êtes un expert senior en analyse d'appels d'offres (AO) et passation de marchés publics et privés. "
    "Votre mission consiste à analyser rigoureusement les règlements de consultation (RC), cahiers des clauses administratives (CCAP) "
    "et techniques (CCTP).\n\n"
    "Règles impératives :\n"
    "1. Extrayez systématiquement la référence du marché, l'autorité contractante, la date limite de remise des plis, "
    "et les critères d'attribution.\n"
    "2. Générez une matrice de conformité administrative et technique exhaustive.\n"
    "3. Identifiez avec exactitude les pièces manquantes ou non vérifiées dans les documents de l'entreprise.\n"
    "4. Ne certifiez JAMAIS qu'une candidature est conforme si des pièces probantes manquent."
)

FINANCIAL_SYSTEM_PROMPT = (
    "Vous êtes un analyste financier et contrôleur de gestion d'entreprise. "
    "Vous préparez des synthèses financières, factures, devis, budgets et états de trésorerie.\n\n"
    "Règles impératives :\n"
    "1. N'effectuez JAMAIS de calculs arithmétiques mentaux : appuyez-vous strictement sur les résultats vérifiés fournis par le moteur de calcul Python.\n"
    "2. Précisez systématiquement les montants HT, les taux de TVA applicables (20%, 14%, 10%, 5.5%) et le montant TTC.\n"
    "3. Exposez clairement la formule de calcul, la devise et le statut de validation."
)

CATALOG_TEMPLATES = [
    {
        "category": "administrative",
        "name": "Lettre d'Accompagnement Officielle",
        "code": "admin_transmittal_letter",
        "description": "Lettre de transmission officielle pour envoi de dossiers administratifs, rapports ou livrables.",
        "supported_formats": "docx,pdf",
        "default_prompt": "Rédigez une lettre d'accompagnement officielle élégante en français, avec en-tête, objet précis, bordereau des pièces jointes et formule de politesse protocolaire.",
    },
    {
        "category": "administrative",
        "name": "Attestation de Réalisation & Fin de Mission",
        "code": "admin_completion_certificate",
        "description": "Attestation formelle confirmant la bonne exécution et conformité d'une prestation de services ou d'un contrat.",
        "supported_formats": "docx,pdf",
        "default_prompt": "Générez une attestation certifiant l'achèvement complet et conforme des prestations contractuelles, avec dates, références et signataires légaux.",
    },
    {
        "category": "procurement",
        "name": "Rapport d'Analyse d'Appel d'Offres & Matrice de Conformité",
        "code": "tender_compliance_matrix",
        "description": "Extraction des exigences du dossier de consultation, matrice de conformité et détection des pièces administratives et techniques manquantes.",
        "supported_formats": "docx,pdf,xlsx",
        "default_prompt": "Analysez le dossier d'appel d'offres fourni. Dressez le récapitulatif du marché, la matrice d'éligibilité, les exigences administratives, techniques et financières, et le tableau des pièces obligatoires.",
    },
    {
        "category": "procurement",
        "name": "Lettre de Soumission & Déclaration de Candidature",
        "code": "tender_submission_letter",
        "description": "Lettre formelle de soumission d'offre conforme aux standards de la commande publique (DC1/DC2).",
        "supported_formats": "docx,pdf",
        "default_prompt": "Rédigez la lettre formelle de candidature et de soumission à l'appel d'offres en reprenant les références exactes et l'engagement ferme sur l'offre.",
    },
    {
        "category": "financial",
        "name": "Facture Commerciale & Détail TVA",
        "code": "finance_invoice",
        "description": "Facture professionnelle normée avec tableau d'articles, calculs déterministes HT, TVA et TTC, et mentions légales.",
        "supported_formats": "docx,pdf,xlsx",
        "default_prompt": "Établissez une facture détaillée avec désignation des prestations, prix unitaires, quantités, totaux HT, ventilation de TVA et total TTC certifié.",
    },
    {
        "category": "financial",
        "name": "Rapport de Suivi Budgétaire & Écarts",
        "code": "finance_budget_variance",
        "description": "Analyse comparative entre budget prévisionnel et dépenses réelles avec calcul des écarts en valeur et pourcentage.",
        "supported_formats": "docx,pdf,xlsx",
        "default_prompt": "Générez un état d'analyse budgétaire comparant le budget alloué et les dépenses réelles, avec analyse des dépassements et recommandations d'arbitrage.",
    },
    {
        "category": "commercial",
        "name": "Proposition Commerciale & Offre de Services",
        "code": "commercial_proposal",
        "description": "Dossier d'offre commerciale complet : contexte client, méthodologie, calendrier de déploiement et chiffrage des prestations.",
        "supported_formats": "docx,pdf",
        "default_prompt": "Rédigez une proposition commerciale convaincante et structurée, incluant la compréhension du besoin, notre solution proposée, la valeur ajoutée et le budget.",
    },
    {
        "category": "hr",
        "name": "Ordre de Mission & Lettre de Détachement",
        "code": "hr_mission_letter",
        "description": "Document officiel habilitant un collaborateur à réaliser une mission sur site client ou à l'étranger.",
        "supported_formats": "docx,pdf",
        "default_prompt": "Éditez un ordre de mission officiel précisant le collaborateur, le lieu de déplacement, l'objet de la mission, la durée et la prise en charge des frais.",
    },
    {
        "category": "operations",
        "name": "Procès-Verbal de Réception de Chantier / Recette",
        "code": "ops_acceptance_report",
        "description": "PV formel de recette de projet ou de livraison de travaux avec ou sans réserves.",
        "supported_formats": "docx,pdf",
        "default_prompt": "Rédigez un procès-verbal officiel de réception de travaux / recette de livrables, listant les intervenants, le constat de conformité et les éventuelles réserves.",
    }
]

def seed_database(db: Session):
    """Seed initial system prompts, providers, and default templates if empty."""
    # 1. System Prompts
    if db.query(SystemPrompt).count() == 0:
        default_prompt = SystemPrompt(
            name="Prompt par Défaut INDUSERV",
            description="Assistant documentaire d'entreprise universel avec stricte véracité des données.",
            content=DEFAULT_SYSTEM_PROMPT,
            category="general",
            is_default=True
        )
        tender_prompt = SystemPrompt(
            name="Spécialiste Appels d'Offres & Marchés",
            description="Analyse rigoureuse de dossiers de consultation et matrices de conformité.",
            content=TENDER_SYSTEM_PROMPT,
            category="procurement",
            is_default=False
        )
        fin_prompt = SystemPrompt(
            name="Expert Financier & Facturation",
            description="Contrôle de gestion, calculs de TVA, factures et analyses d'écarts.",
            content=FINANCIAL_SYSTEM_PROMPT,
            category="financial",
            is_default=False
        )
        db.add_all([default_prompt, tender_prompt, fin_prompt])
        db.commit()

    # 2. AI Provider Settings
    if db.query(AIProviderSetting).count() == 0:
        free_provider = AIProviderSetting(
            provider_type="free_api",
            name="OpenRouter API (Modèles Gratuits)",
            base_url=settings.FREE_API_BASE_URL,
            api_key=settings.FREE_API_KEY,
            model_name=settings.FREE_API_DEFAULT_MODEL,
            is_active=True,
            temperature=0.2,
            max_tokens=4096
        )
        ollama_provider = AIProviderSetting(
            provider_type="ollama",
            name="Ollama Local (100% Hors-Ligne & Privé)",
            base_url=settings.OLLAMA_BASE_URL,
            api_key="",
            model_name=settings.OLLAMA_DEFAULT_MODEL,
            is_active=False,
            temperature=0.2,
            max_tokens=4096
        )
        openai_provider = AIProviderSetting(
            provider_type="openai_compatible",
            name="OpenAI Compatible API (Groq / Mistral / DeepSeek)",
            base_url="https://api.groq.com/openai/v1",
            api_key="",
            model_name="llama-3.3-70b-versatile",
            is_active=False,
            temperature=0.2,
            max_tokens=4096
        )
        db.add_all([free_provider, ollama_provider, openai_provider])
        db.commit()

    # 3. User Settings
    if db.query(UserSetting).count() == 0:
        user_setting = UserSetting(
            company_name="INDUSERV Technologies",
            company_details="123 Boulevard Industriel, 75008 Paris - France\nSIRET: 892 451 098 00014 - TVA: FR 34 892451098\nEmail: contact@induserv.com - Tél: +33 1 42 68 55 00",
            default_language="fr",
            active_prompt_id=1,
            active_provider_id=1
        )
        db.add(user_setting)
        db.commit()

    # 4. Catalog Templates
    if db.query(Template).count() == 0:
        for tpl in CATALOG_TEMPLATES:
            t = Template(
                category=tpl["category"],
                name=tpl["name"],
                code=tpl["code"],
                description=tpl["description"],
                supported_formats=tpl["supported_formats"],
                default_prompt=tpl["default_prompt"],
                is_custom=False
            )
            db.add(t)
        db.commit()

