"""
AltaCLP — Quotations (draft + approve) com persistência real no banco.
"""

import uuid
from datetime import datetime, date
from typing import Optional, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import CotacaoDraft, Usuario, PerfilUsuario
from middleware.rbac import require_roles
from routers.auth import get_usuario_atual
from services.project_factory import create_project_from_quotation
from services.notificacoes_ws import notification_hub
from services.bom_generator import gerar_bom_da_transcricao

router = APIRouter(prefix="/quotations", tags=["Quotations"])

_quotation_roles = require_roles(
    PerfilUsuario.vendedor.value,
    PerfilUsuario.ceo.value,
)


class DraftCreateRequest(BaseModel):
    texto_transcrito: Optional[str] = None
    json_proposta_ia: Optional[dict[str, Any]] = None
    cliente_nome: Optional[str] = ""
    valor_estimado: float = 0
    audio_raw_url: Optional[str] = None


class ApproveRequest(BaseModel):
    prazo: Optional[date] = None


def _draft_to_dict(d: CotacaoDraft) -> dict:
    proposta = d.json_proposta_ia if isinstance(d.json_proposta_ia, dict) else {}
    return {
        "id_cotacao": str(d.id_cotacao),
        "id_vendedor": str(d.id_vendedor),
        "audio_raw_url": d.audio_raw_url,
        "texto_transcrito": d.texto_transcrito,
        "json_proposta_ia": proposta,
        "cliente_nome": proposta.get("cliente_nome", ""),
        "valor_estimado": proposta.get("valor_estimado", 0),
        "status": d.status,
    }


@router.post("/draft")
async def create_draft(
    body: DraftCreateRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(_quotation_roles),
):
    print(f"[ROUTE HIT] POST /quotations/draft — body: {body.model_dump()}")

    if not body.texto_transcrito and not body.json_proposta_ia:
        raise HTTPException(
            status_code=400,
            detail="texto_transcrito or json_proposta_ia is required",
        )

    try:
        proposta = dict(body.json_proposta_ia or {})

        # Immediate AI Analysis if transcrito text is provided
        if body.texto_transcrito:
            print(f"[AI ANALYSIS] Triggering immediate analysis for text length: {len(body.texto_transcrito)}")
            try:
                cliente_nome = body.cliente_nome or proposta.get("cliente_nome", "")
                resultado = await gerar_bom_da_transcricao(
                    transcricao=body.texto_transcrito,
                    vendedor=usuario.nome,
                    cliente_nome=cliente_nome
                )
                # Save results to json_proposta_ia
                proposta["bom"] = resultado.get("bom", [])
                proposta["template_comissionamento"] = resultado.get("template_comissionamento", {})
                proposta["parametros_extraidos"] = resultado.get("parametros_extraidos", {})

                # Calculate valor_estimado from the BOM items
                valor_total = sum(item.get("valor_unit", 0) * item.get("quantidade", 1) for item in proposta["bom"])
                proposta["valor_estimado"] = valor_total if valor_total > 0 else (body.valor_estimado or 0.0)

                if not cliente_nome:
                    cliente_nome = resultado.get("parametros_extraidos", {}).get("outros", {}).get("cliente", "")

                if cliente_nome:
                    proposta["cliente_nome"] = cliente_nome

            except Exception as ai_err:
                print(f"[AI ANALYSIS ERROR] {ai_err}")
                if body.cliente_nome:
                    proposta["cliente_nome"] = body.cliente_nome
                if body.valor_estimado:
                    proposta["valor_estimado"] = body.valor_estimado
        else:
            if body.cliente_nome:
                proposta["cliente_nome"] = body.cliente_nome
            if body.valor_estimado:
                proposta["valor_estimado"] = body.valor_estimado

        draft = CotacaoDraft(
            id_cotacao=uuid.uuid4(),
            id_vendedor=usuario.id,
            audio_raw_url=body.audio_raw_url,
            texto_transcrito=body.texto_transcrito or "",
            json_proposta_ia=proposta,
            status="RASCUNHO",
        )
        db.add(draft)
        db.commit()
        db.refresh(draft)

        saved = db.query(CotacaoDraft).filter(CotacaoDraft.id_cotacao == draft.id_cotacao).first()
        if not saved:
            raise RuntimeError("Database write failed — record not found after insert")

        print(f"[DB WRITE CONFIRMED] cotacoes_draft id: {saved.id_cotacao}")
        return _draft_to_dict(saved)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"[ERROR] POST /quotations/draft: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{draft_id}/approve")
async def approve_draft(
    draft_id: str,
    body: ApproveRequest = None,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(_quotation_roles),
):
    print(f"[ROUTE HIT] POST /quotations/{draft_id}/approve")

    try:
        d_uuid = uuid.UUID(draft_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid draft id")

    draft = db.query(CotacaoDraft).filter(CotacaoDraft.id_cotacao == d_uuid).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    perfil = usuario.perfil.value if hasattr(usuario.perfil, "value") else str(usuario.perfil)
    if draft.id_vendedor != usuario.id and perfil != PerfilUsuario.ceo.value:
        raise HTTPException(status_code=403, detail="Forbidden")

    cliente_nome = ""
    valor = 0.0
    bom_json = None
    template_comiss = None
    if isinstance(draft.json_proposta_ia, dict):
        cliente_nome = draft.json_proposta_ia.get("cliente_nome", "") or ""
        valor = float(draft.json_proposta_ia.get("valor_estimado", 0) or 0)
        bom_json = draft.json_proposta_ia.get("bom", None)
        template_comiss = draft.json_proposta_ia.get("template_comissionamento", None)

    try:
        draft.status = "APROVADO"
        db.flush()

        project = create_project_from_quotation(
            db,
            usuario,
            cliente_nome=cliente_nome or "Novo Cliente",
            valor_estimado=valor,
            texto_transcrito=draft.texto_transcrito or "",
            json_proposta_ia=draft.json_proposta_ia,
            bom_json=bom_json,
            template_comissionamento=template_comiss,
            prazo=body.prazo if body else None,
        )
        db.commit()

        saved = db.query(CotacaoDraft).filter(CotacaoDraft.id_cotacao == d_uuid).first()
        if not saved or saved.status != "APROVADO":
            raise RuntimeError("Draft status update failed")

        print(f"[DB WRITE CONFIRMED] projetos id: {project['id']}")

        await notification_hub.notificar_novo_projeto(project)

        return project

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print(f"[ERROR] POST /quotations/{draft_id}/approve: {e}")
        raise HTTPException(status_code=500, detail=str(e))
