import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.entities import SystemPrompt, AIProviderSetting, TaskHistory, DocumentChunk, Document
from app.schemas.schemas import WorkspaceChatRequest, WorkspaceChatResponse
from app.services.ai.factory import get_ai_provider

router = APIRouter(prefix="/workspace", tags=["AI Workspace"])

@router.post("/chat", response_model=WorkspaceChatResponse)
async def chat_workspace(req: WorkspaceChatRequest, db: Session = Depends(get_db)):
    """
    Execute an AI task in the AI Workspace with selected prompt, provider, and document context.
    """
    start_time = time.time()

    # 1. Resolve System Prompt
    system_prompt_content = None
    if req.prompt_id:
        p = db.query(SystemPrompt).filter(SystemPrompt.id == req.prompt_id).first()
        if p:
            system_prompt_content = p.content

    if not system_prompt_content:
        default_p = db.query(SystemPrompt).filter(SystemPrompt.is_default == True).first()
        system_prompt_content = default_p.content if default_p else "You are an enterprise document assistant."

    # 2. Resolve AI Provider
    provider_setting = None
    if req.provider_id:
        provider_setting = db.query(AIProviderSetting).filter(AIProviderSetting.id == req.provider_id).first()
    if not provider_setting:
        provider_setting = db.query(AIProviderSetting).filter(AIProviderSetting.is_active == True).first()

    provider = get_ai_provider(provider_id=req.provider_id, db=db)

    # 3. Retrieve relevant document context if document_ids provided
    referenced_chunks_data = []
    context_text = ""
    if req.document_ids:
        raw_chunks = (
            db.query(DocumentChunk, Document)
            .join(Document, DocumentChunk.document_id == Document.id)
            .filter(DocumentChunk.document_id.in_(req.document_ids))
            .all()
        )
        if raw_chunks:
            from app.services.retrieval.search import KeywordRetriever
            retriever = KeywordRetriever()

            chunk_dicts = [
                {
                    "id": chunk.id,
                    "document_id": doc.id,
                    "filename": doc.original_filename,
                    "text_content": chunk.text_content,
                    "page_number": chunk.page_number,
                    "sheet_name": chunk.sheet_name,
                    "section_title": chunk.section_title
                }
                for chunk, doc in raw_chunks
            ]

            # Rank chunks using BM25 against the user message
            ranked_chunks = retriever.rank_chunks(req.message, chunk_dicts, top_k=8)

            context_blocks = []
            for c in ranked_chunks:
                ref = f"[Fichier: {c['filename']}"
                if c.get("page_number"):
                    ref += f", Page {c['page_number']}"
                if c.get("sheet_name"):
                    ref += f", Feuille {c['sheet_name']}"
                if c.get("section_title"):
                    ref += f", Section: {c['section_title']}"
                ref += "]"
                context_blocks.append(f"{ref}\n{c['text_content']}")
                referenced_chunks_data.append({
                    "document_id": c["document_id"],
                    "filename": c["filename"],
                    "page_number": c.get("page_number"),
                    "sheet_name": c.get("sheet_name"),
                    "content_snippet": c["text_content"][:200] + "..." if len(c["text_content"]) > 200 else c["text_content"]
                })
            context_text = "\n\n---\nDOCUMENTS DE RÉFÉRENCE FOURNIS :\n" + "\n\n".join(context_blocks) + "\n---\n"

    # 4. Assemble augmented prompt
    augmented_prompt = req.message
    if context_text:
        augmented_prompt = f"{context_text}\n\nINSTRUCTION DE L'UTILISATEUR :\n{req.message}"

    # 5. Execute generation
    response_text = await provider.generate_text(
        prompt=augmented_prompt,
        system_prompt=system_prompt_content,
        temperature=req.temperature if req.temperature is not None else (provider_setting.temperature if provider_setting else 0.2)
    )

    elapsed_ms = int((time.time() - start_time) * 1000)

    # 6. Save task history
    task = TaskHistory(
        title=req.message[:80] + ("..." if len(req.message) > 80 else ""),
        workflow_type="ai_workspace_query",
        system_prompt_used=system_prompt_content,
        user_instructions=req.message,
        response_text=response_text,
        referenced_doc_ids=",".join(str(d) for d in req.document_ids),
        status="completed",
        execution_time_ms=elapsed_ms
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    return WorkspaceChatResponse(
        response=response_text,
        referenced_chunks=referenced_chunks_data,
        calculation_audits=[],
        task_id=task.id,
        execution_time_ms=elapsed_ms,
        provider_name=provider_setting.name if provider_setting else "Default Provider",
        model_name=provider.model_name
    )
