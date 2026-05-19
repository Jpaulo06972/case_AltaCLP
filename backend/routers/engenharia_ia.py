"""
AltaCLP — IA para camada de Engenharia (resumo mensal + RAG).
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database.connection import get_db
from middleware.rbac import require_roles
from database.models import PerfilUsuario
from services.eng_rag import compilar_resumo_mensal, rag_chat_engenharia

router = APIRouter(prefix="/engenharia/ia", tags=["Engenharia — IA"])


class RAGChatRequest(BaseModel):
    mensagem: str
    perfil: str = "engenharia"
    equipamento_tag: str | None = None
    maquina_id: str | None = None
    projeto_id: str | None = None


@router.get("/resumo-mensal")
async def resumo_mensal(
    db: Session = Depends(get_db),
    _user=Depends(require_roles(PerfilUsuario.ceo.value, PerfilUsuario.engenharia.value, PerfilUsuario.cfo.value)),
):
    """Resumo mensal automático de custos de visita e manutenção."""
    return await compilar_resumo_mensal(db)


@router.post("/rag-chat")
async def rag_chat(
    body: RAGChatRequest,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(PerfilUsuario.ceo.value, PerfilUsuario.engenharia.value, PerfilUsuario.cfo.value)),
):
    """Chat RAG com dados operacionais."""
    result = await rag_chat_engenharia(
        db=db,
        pergunta=body.mensagem,
        perfil=body.perfil,
        equipamento_tag=body.equipamento_tag,
        maquina_id=body.maquina_id,
        projeto_id=body.projeto_id,
    )
    if isinstance(result, dict) and "resposta" not in result:
        result["resposta"] = result.get("mensagem") or str(result)
    return result
