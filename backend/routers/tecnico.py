"""
AltaCLP — Router do perfil Técnico de Campo (escopo isolado por projeto).
"""

import os
import uuid
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database.connection import get_db
from database.models import (
    Usuario, PerfilUsuario, ProjetoTecnico, Comissionamento, Maquina, Cliente,
    ProjetoPendencia, DocumentoComissionamento, IntervencaoTecnica,
    SubmissaoValidacao, StatusTarefaPendencia, TipoAcaoTecnico, StatusRevisaoEng,
    EquipamentoPlanta, LogThreshold,
)
from routers.auth import get_usuario_atual
from services.tecnico_scope import (
    is_tecnico,
    get_projeto_ids_atribuidos,
    assert_projeto_acesso,
    assert_maquina_acesso,
)
from services.tecnico_rag import chat_instalacao_tecnico, revisar_submissao_ia
from services.notificacoes_ws import notification_hub
from services.eng_rag import analisar_causa_raiz_alarme

router = APIRouter(prefix="/tecnico", tags=["Técnico de Campo"])


def _require_tecnico(usuario: Usuario = Depends(get_usuario_atual)) -> Usuario:
    perfil = usuario.perfil.value if hasattr(usuario.perfil, "value") else str(usuario.perfil)
    if perfil in (PerfilUsuario.ceo.value, PerfilUsuario.cfo.value):
        return usuario
    if not is_tecnico(usuario):
        raise HTTPException(status_code=403, detail="Endpoint exclusivo para técnico de campo")
    return usuario


@router.get("/atribuicoes")
def minhas_atribuicoes(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(_require_tecnico),
):
    projeto_ids = get_projeto_ids_atribuidos(db, usuario.id)
    projetos = (
        db.query(Comissionamento, Maquina.codigo, Cliente.nome)
        .join(Maquina, Comissionamento.maquina_id == Maquina.id)
        .join(Cliente, Comissionamento.cliente_id == Cliente.id)
        .filter(Comissionamento.id.in_(projeto_ids))
        .all()
        if projeto_ids
        else []
    )
    return {
        "id_tecnico": str(usuario.id),
        "projetos": [
            {
                "id_projeto": str(c.id),
                "maquina_codigo": maq,
                "cliente_nome": cli,
                "fase_projeto": c.fase_projeto.value if c.fase_projeto else None,
                "status": c.status.value,
            }
            for c, maq, cli in projetos
        ],
    }


class ChatInstalacaoRequest(BaseModel):
    mensagem: str
    maquina_id: str | None = None
    equipamento_tag: str | None = None
    modo: str = "instalacao"


@router.post("/ia/chat-instalacao")
async def ia_chat_instalacao(
    body: ChatInstalacaoRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(_require_tecnico),
):
    if body.maquina_id:
        assert_maquina_acesso(db, usuario, UUID(body.maquina_id))
    return await chat_instalacao_tecnico(
        db=db,
        pergunta=body.mensagem,
        maquina_id=body.maquina_id,
        equipamento_tag=body.equipamento_tag,
        modo=body.modo,
    )


class IntervencaoRequest(BaseModel):
    tipo_acao: str
    comentario_tecnico: str


@router.post("/alertas/{alerta_id}/intervencao")
async def registrar_intervencao(
    alerta_id: UUID,
    body: IntervencaoRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(_require_tecnico),
):
    from database.models import Alerta
    from services.tecnico_scope import get_maquina_ids_atribuidas

    alerta = db.query(Alerta).filter(Alerta.id == alerta_id).first()
    if not alerta:
        raise HTTPException(status_code=404, detail="Alarme não encontrado")
    if alerta.maquina_id not in get_maquina_ids_atribuidas(db, usuario.id):
        raise HTTPException(status_code=403, detail="Alarme fora do escopo atribuído")

    try:
        tipo = TipoAcaoTecnico(body.tipo_acao)
    except ValueError:
        raise HTTPException(status_code=400, detail="tipo_acao inválido")

    interv = IntervencaoTecnica(
        id=uuid.uuid4(),
        id_alarme=alerta_id,
        id_tecnico=usuario.id,
        tipo_acao=tipo,
        comentario_tecnico=body.comentario_tecnico,
        status_revisao_eng=StatusRevisaoEng.pendente,
    )
    db.add(interv)
    db.commit()
    return {
        "id": str(interv.id),
        "mensagem": "Ação registrada — aguardando revisão da engenharia",
        "status_revisao_eng": interv.status_revisao_eng.value,
    }


@router.get("/alertas/{alerta_id}/analise")
async def analise_alarme_tecnico(
    alerta_id: UUID,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(_require_tecnico),
):
    from database.models import Alerta
    from services.tecnico_scope import get_maquina_ids_atribuidas

    alerta = db.query(Alerta).filter(Alerta.id == alerta_id).first()
    if not alerta or alerta.maquina_id not in get_maquina_ids_atribuidas(db, usuario.id):
        raise HTTPException(status_code=403, detail="Alarme fora do escopo")
    texto = await analisar_causa_raiz_alarme(db, str(alerta_id))
    return {"texto_analise": texto, "titulo": alerta.titulo}


class StatusTarefaBody(BaseModel):
    status_tarefa: str


@router.patch("/pendencias/{pendencia_id}/status")
def atualizar_status_tarefa(
    pendencia_id: UUID,
    body: StatusTarefaBody,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(_require_tecnico),
):
    status_tarefa = body.status_tarefa
    p = db.query(ProjetoPendencia).filter(ProjetoPendencia.id == pendencia_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Pendência não encontrada")
    assert_projeto_acesso(db, usuario, p.comissionamento_id)

    allowed = {s.value for s in StatusTarefaPendencia}
    if status_tarefa not in allowed:
        raise HTTPException(status_code=400, detail=f"Use: {', '.join(allowed)}")

    p.status_tarefa = status_tarefa
    p.concluida = status_tarefa in (StatusTarefaPendencia.em_revisao.value, StatusTarefaPendencia.concluida.value)
    if p.concluida and not p.data_conclusao:
        p.data_conclusao = datetime.utcnow()
    db.commit()
    return {"status_tarefa": status_tarefa, "concluida": p.concluida}


@router.post("/projetos/{projeto_id}/documentos")
async def upload_documento(
    projeto_id: UUID,
    nome_arquivo: str = Form(...),
    id_pendencia: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(_require_tecnico),
):
    assert_projeto_acesso(db, usuario, projeto_id)
    upload_dir = os.path.join(os.path.dirname(__file__), "..", "uploads", "comissionamento")
    os.makedirs(upload_dir, exist_ok=True)
    ext = os.path.splitext(file.filename or nome_arquivo)[1]
    fname = f"{uuid.uuid4()}{ext}"
    path = os.path.join(upload_dir, fname)
    content = await file.read()
    with open(path, "wb") as f:
        f.write(content)
    url = f"/uploads/comissionamento/{fname}"

    doc = DocumentoComissionamento(
        id=uuid.uuid4(),
        id_projeto=projeto_id,
        id_pendencia=UUID(id_pendencia) if id_pendencia else None,
        id_tecnico=usuario.id,
        nome_arquivo=nome_arquivo or file.filename or fname,
        url_documento=url,
        tipo_mime=file.content_type,
    )
    db.add(doc)
    db.commit()
    return {"id": str(doc.id), "url_documento": url}


@router.post("/projetos/{projeto_id}/submeter-validacao")
async def submeter_validacao(
    projeto_id: UUID,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(_require_tecnico),
):
    assert_projeto_acesso(db, usuario, projeto_id)
    docs = db.query(DocumentoComissionamento).filter(
        DocumentoComissionamento.id_projeto == projeto_id,
        DocumentoComissionamento.id_tecnico == usuario.id,
    ).all()
    resumo = await revisar_submissao_ia(db, str(projeto_id), [{"url": d.url_documento} for d in docs])

    sub = SubmissaoValidacao(
        id=uuid.uuid4(),
        id_projeto=projeto_id,
        id_tecnico=usuario.id,
        resumo_ia=resumo,
        status="aguardando_engenharia",
    )
    db.add(sub)
    pendencias = db.query(ProjetoPendencia).filter(
        ProjetoPendencia.comissionamento_id == projeto_id,
        ProjetoPendencia.status_tarefa == StatusTarefaPendencia.pendente,
    ).all()
    for p in pendencias:
        p.status_tarefa = StatusTarefaPendencia.em_revisao
    db.commit()

    await notification_hub.notificar_submissao_validacao(str(projeto_id), usuario.nome)
    return {
        "submissao_id": str(sub.id),
        "resumo_ia": resumo,
        "mensagem": "Submetido para validação — engenheiro será notificado",
        "status_projeto_inalterado": True,
    }


@router.put("/equipamentos/{equipamento_id}/calibrar")
def calibrar_equipamento(
    equipamento_id: UUID,
    parametro: str = Query(...),
    valor_novo: float = Query(...),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(_require_tecnico),
):
    eq = db.query(EquipamentoPlanta).filter(EquipamentoPlanta.id == equipamento_id).first()
    if not eq:
        raise HTTPException(status_code=404, detail="Equipamento não encontrado")
    assert_maquina_acesso(db, usuario, eq.maquina_id)

    valor_antigo = eq.threshold_max if "max" in parametro.lower() else eq.threshold_min
    if "max" in parametro.lower():
        eq.threshold_max = valor_novo
    else:
        eq.threshold_min = valor_novo
    eq.ultima_atualizacao = datetime.utcnow()

    log = LogThreshold(
        id_equipamento=eq.id,
        maquina_id=eq.maquina_id,
        parametro_alterado=parametro,
        valor_antigo=valor_antigo,
        valor_novo=valor_novo,
        id_usuario=str(usuario.id),
        origem="tecnico_calibracao",
    )
    db.add(log)
    db.commit()
    return {"sucesso": True, "id_registro": str(log.id_registro)}


@router.websocket("/notificacoes/ws")
async def ws_notificacoes(websocket: WebSocket, token: str = None):
    """WebSocket: ?token=JWT — técnico recebe alertas do escopo; engenheiro recebe todos."""
    from jose import jwt, JWTError
    from routers.auth import SECRET_KEY, ALGORITHM
    from database.connection import SessionLocal

    if not token:
        await websocket.close(code=4001)
        return
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
    except JWTError:
        await websocket.close(code=4001)
        return

    db = SessionLocal()
    try:
        usuario = db.query(Usuario).filter(Usuario.email == email).first()
        if not usuario:
            await websocket.close(code=4001)
            return
        perfil = usuario.perfil.value
        if perfil == PerfilUsuario.tecnico_campo.value:
            await notification_hub.connect_tecnico(str(usuario.id), websocket)
            try:
                while True:
                    await websocket.receive_text()
            except WebSocketDisconnect:
                await notification_hub.disconnect_tecnico(str(usuario.id), websocket)
        elif perfil == PerfilUsuario.engenharia.value:
            await notification_hub.connect_engenheiro(websocket)
            try:
                while True:
                    await websocket.receive_text()
            except WebSocketDisconnect:
                await notification_hub.disconnect_engenheiro(websocket)
        else:
            await websocket.close(code=4003)
    finally:
        db.close()
