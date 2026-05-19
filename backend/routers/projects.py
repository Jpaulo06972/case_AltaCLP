"""
AltaCLP Intelligence Platform — Projects Router
Commissioning relational data: projects, tasks, machines, alerts, git PRs.
"""

import uuid as uuid_mod
import os
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select

from database.connection import get_db
from database.models import (
    Projeto,
    Maquina,
    Alerta,
    LogAuditoriaGit,
    ProjetoPendencia,
    DocumentoComissionamento,
    ProjetoHistorico,
    Comissionamento,
    ProjetoTecnico,
    PerfilUsuario,
    StatusTarefaPendencia,
    Usuario,
)
from routers.auth import get_usuario_atual
from services.notificacoes_ws import notification_hub
from services.tecnico_scope import get_projeto_ids_atribuidos, is_tecnico

router = APIRouter(prefix="/projects", tags=["Projects"])


class TaskUpdatePayload(BaseModel):
    concluida: bool | None = None
    status_tarefa: str | None = None


def _projects_query(db: Session, usuario: Usuario):
    query = db.query(Projeto)
    perfil = usuario.perfil.value if hasattr(usuario.perfil, "value") else str(usuario.perfil)

    if perfil == PerfilUsuario.vendedor.value:
        query = query.filter(Projeto.id_vendedor == str(usuario.id))
    elif is_tecnico(usuario):
        assigned_comiss = get_projeto_ids_atribuidos(db, usuario.id)
        if not assigned_comiss:
            return query.filter(Projeto.id == None)  # noqa: E711
        maq_proj_ids = (
            db.query(Maquina.id_projeto)
            .join(Comissionamento, Comissionamento.maquina_id == Maquina.id)
            .filter(Comissionamento.id.in_(assigned_comiss))
            .distinct()
            .all()
        )
        proj_ids = [r[0] for r in maq_proj_ids if r[0]]
        if not proj_ids:
            return query.filter(Projeto.id == None)  # noqa: E711
        query = query.filter(Projeto.id.in_(proj_ids))

    return query


def _serialize_project(db: Session, p: Projeto) -> dict:
    total_tasks = db.query(ProjetoPendencia).filter(ProjetoPendencia.id_projeto == p.id).count()
    done_tasks = db.query(ProjetoPendencia).filter(
        ProjetoPendencia.id_projeto == p.id, ProjetoPendencia.concluida == True
    ).count()
    progresso = round((done_tasks / total_tasks) * 100, 1) if total_tasks > 0 else 0

    proj_machine_ids = select(Maquina.id).where(Maquina.id_projeto == p.id)
    alert_count = db.query(Alerta).filter(Alerta.maquina_id.in_(proj_machine_ids)).count()
    pr_count = db.query(LogAuditoriaGit).filter(LogAuditoriaGit.id_projeto == p.id).count()

    return {
        "id": p.id,
        "nome_contrato": p.nome_contrato,
        "id_vendedor": p.id_vendedor,
        "id_engenheiro": p.id_engenheiro,
        "valor_contrato": float(p.valor_contrato) if p.valor_contrato else 0,
        "status": p.status,
        "prazo": p.prazo.isoformat() if p.prazo else None,
        "dias_atraso": p.dias_atraso,
        "risco": p.risco,
        "progresso": progresso,
        "alert_count": alert_count,
        "pr_count": pr_count,
    }


@router.get("")
def list_projects(
    status: str = None,
    id_engenheiro: str = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    print(f"[ROUTE HIT] GET /projects — user {usuario.id} ({usuario.perfil})")
    try:
        query = _projects_query(db, usuario)
        if status:
            query = query.filter(Projeto.status == status)
        if id_engenheiro:
            query = query.filter(Projeto.id_engenheiro == id_engenheiro)

        total = query.count()
        offset = (page - 1) * limit
        projetos = query.order_by(Projeto.id.desc()).offset(offset).limit(limit).all()
        result = [_serialize_project(db, p) for p in projetos]

        print(f"[DB READ] GET /projects — returned {len(result)} rows")
        return {"dados": result, "total": total, "page": page, "limit": limit}
    except Exception as e:
        print(f"[ERROR] GET /projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{id}")
def get_project_detail(
    id: str,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    p = _projects_query(db, usuario).filter(Projeto.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    return _serialize_project(db, p)


@router.get("/{id}/machines")
def get_project_machines(id: str, db: Session = Depends(get_db), usuario: Usuario = Depends(get_usuario_atual)):
    if not _projects_query(db, usuario).filter(Projeto.id == id).first():
        raise HTTPException(status_code=404, detail="Project not found")
    machines = db.query(Maquina).filter(Maquina.id_projeto == id).all()
    return [{
        "codigo": m.codigo,
        "nome": m.nome,
        "status": m.status.value,
        "modelo_clp": m.modelo_clp.value if m.modelo_clp else None,
    } for m in machines]


@router.get("/{id}/alerts")
def get_project_alerts(id: str, db: Session = Depends(get_db), usuario: Usuario = Depends(get_usuario_atual)):
    if not _projects_query(db, usuario).filter(Projeto.id == id).first():
        raise HTTPException(status_code=404, detail="Project not found")
    proj_machine_ids = select(Maquina.id).where(Maquina.id_projeto == id)
    alerts = db.query(Alerta).filter(Alerta.maquina_id.in_(proj_machine_ids)).all()
    return [{
        "id": a.codigo_alerta,
        "descricao": a.titulo,
        "severidade": a.severidade.value,
        "maquina_id": str(a.maquina_id),
    } for a in alerts]


@router.get("/{id}/git-prs")
def get_project_prs(id: str, db: Session = Depends(get_db), usuario: Usuario = Depends(get_usuario_atual)):
    if not _projects_query(db, usuario).filter(Projeto.id == id).first():
        raise HTTPException(status_code=404, detail="Project not found")
    prs = db.query(LogAuditoriaGit).filter(LogAuditoriaGit.id_projeto == id).all()
    return [{
        "id": str(pr.id),
        "resumo": pr.diff_resumo,
        "usuario": pr.id_usuario,
        "risco_ia": pr.risco_ia,
    } for pr in prs]


@router.get("/{id}/tasks")
def get_project_tasks(id: str, db: Session = Depends(get_db), usuario: Usuario = Depends(get_usuario_atual)):
    if not _projects_query(db, usuario).filter(Projeto.id == id).first():
        raise HTTPException(status_code=404, detail="Project not found")
    tasks = db.query(ProjetoPendencia).filter(
        ProjetoPendencia.id_projeto == id
    ).order_by(ProjetoPendencia.ordem).all()
    return [{
        "id": str(t.id),
        "titulo": t.titulo,
        "tecnico": t.id_tecnico_atribuido,
        "concluida": t.concluida,
        "status_tarefa": t.status_tarefa.value if t.status_tarefa else "pendente",
    } for t in tasks]


@router.patch("/{id}/tasks/{task_id}")
def update_task_status(
    id: str,
    task_id: str,
    payload: TaskUpdatePayload,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    print(f"[ROUTE HIT] PATCH /projects/{id}/tasks/{task_id}")

    if payload.status_tarefa and payload.status_tarefa not in ("pendente", "em_revisao", "concluida", "PENDENTE", "EM_REVISAO", "CONCLUIDO"):
        raise HTTPException(status_code=400, detail="Invalid status_tarefa value")

    try:
        task_uuid = uuid_mod.UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid task UUID: {task_id}")

    if not _projects_query(db, usuario).filter(Projeto.id == id).first():
        raise HTTPException(status_code=404, detail="Project not found")

    task = db.query(ProjetoPendencia).filter(
        ProjetoPendencia.id == task_uuid,
        ProjetoPendencia.id_projeto == id,
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    status_norm = (payload.status_tarefa or "").lower()
    if payload.concluida is not None:
        task.concluida = payload.concluida
    if status_norm:
        mapping = {
            "pendente": StatusTarefaPendencia.pendente,
            "em_revisao": StatusTarefaPendencia.em_revisao,
            "concluida": StatusTarefaPendencia.concluida,
            "concluido": StatusTarefaPendencia.concluida,
        }
        task.status_tarefa = mapping.get(status_norm, task.status_tarefa)
        task.concluida = status_norm in ("concluida", "concluido")
    if task.concluida:
        task.data_conclusao = datetime.utcnow()
    else:
        task.data_conclusao = None

    comiss = db.query(Comissionamento).filter(Comissionamento.id == task.comissionamento_id).first()
    if comiss:
        db.add(ProjetoHistorico(
            id=uuid_mod.uuid4(),
            comissionamento_id=comiss.id,
            acao_realizada="TASK_COMPLETED",
            id_usuario=str(usuario.id),
            data_hora=datetime.utcnow(),
        ))

    db.commit()

    total = db.query(ProjetoPendencia).filter(ProjetoPendencia.id_projeto == id).count()
    done = db.query(ProjetoPendencia).filter(
        ProjetoPendencia.id_projeto == id, ProjetoPendencia.concluida == True
    ).count()
    progress = round((done / total) * 100) if total else 0

    print(f"[DB WRITE CONFIRMED] task {task_id} → {task.status_tarefa} | progress: {progress}%")
    return {
        "id_pendencia": task_id,
        "status_tarefa": task.status_tarefa.value if task.status_tarefa else None,
        "progress": progress,
    }


@router.get("/{id}/documents")
def get_project_docs(id: str, db: Session = Depends(get_db), usuario: Usuario = Depends(get_usuario_atual)):
    if not _projects_query(db, usuario).filter(Projeto.id == id).first():
        raise HTTPException(status_code=404, detail="Project not found")
    docs = db.query(DocumentoComissionamento).filter(
        DocumentoComissionamento.id_projeto == id
    ).all()
    return [{
        "id": str(d.id),
        "nome_arquivo": d.nome_arquivo,
        "data": d.data_upload.isoformat() if d.data_upload else None,
    } for d in docs]


@router.post("/{id}/documents")
def upload_document(
    id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    if not _projects_query(db, usuario).filter(Projeto.id == id).first():
        raise HTTPException(status_code=404, detail="Project not found")

    uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    safe_name = f"{uuid_mod.uuid4().hex}_{file.filename}"
    path = os.path.join(uploads_dir, safe_name)
    content = file.file.read()
    with open(path, "wb") as f:
        f.write(content)

    doc = DocumentoComissionamento(
        id=uuid_mod.uuid4(),
        id_projeto=id,
        id_tecnico=usuario.id,
        nome_arquivo=file.filename,
        url_documento=f"/uploads/{safe_name}",
    )
    db.add(doc)
    db.commit()
    return {"message": "Upload successful", "id": str(doc.id)}


@router.post("/{id}/submit-validation")
async def submit_validation(
    id: str,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    print(f"[ROUTE HIT] POST /projects/{id}/submit-validation")

    projeto = _projects_query(db, usuario).filter(Projeto.id == id).first()
    if not projeto:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        incomplete = db.query(ProjetoPendencia).filter(
            ProjetoPendencia.id_projeto == id,
            ProjetoPendencia.concluida == False,
        ).count()
        if incomplete > 0:
            raise HTTPException(
                status_code=400,
                detail=f"{incomplete} tasks still pending. Complete all tasks before submitting.",
            )

        projeto.status = "AGUARDANDO_VALIDACAO"
        db.flush()

        comiss = (
            db.query(Comissionamento)
            .join(Maquina, Comissionamento.maquina_id == Maquina.id)
            .filter(Maquina.id_projeto == id)
            .first()
        )
        if comiss:
            db.add(ProjetoHistorico(
                id=uuid_mod.uuid4(),
                comissionamento_id=comiss.id,
                acao_realizada="HANDOVER_SUBMITTED",
                id_usuario=str(usuario.id),
                data_hora=datetime.utcnow(),
            ))

        db.commit()
        await notification_hub.notificar_status_projeto(id, "AGUARDANDO_VALIDACAO")

        print(f"[DB WRITE CONFIRMED] project {id} advanced to AGUARDANDO_VALIDACAO")
        return {"id_projeto": id, "new_status": "AGUARDANDO_VALIDACAO"}

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print(f"[ERROR] POST /projects/{id}/submit-validation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
