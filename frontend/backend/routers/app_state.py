"""
AltaCLP Intelligence Platform — App State Router
Full denormalized snapshot for AppDataContext hydration.
Also: assign-technician endpoint.
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import BaseModel

from database.connection import get_db
from database.models import (
    Projeto, Maquina, Alerta, GitOpsAuditoria,
    Usuario, ProjetoPendencia, PerfilUsuario,
)
from routers.auth import get_usuario_atual
from routers.projects import _projects_query

router = APIRouter(prefix="/app-state", tags=["AppState"])


@router.get("")
def get_app_state(db: Session = Depends(get_db), usuario: Usuario = Depends(get_usuario_atual)):
    """
    Returns a full denormalized snapshot of projects + machines + alerts
    for AppDataContext hydration on app load.
    """
    projetos = _projects_query(db, usuario).all()
    proj_list = []
    for p in projetos:
        total_tasks = db.query(ProjetoPendencia).filter(ProjetoPendencia.id_projeto == p.id).count()
        done_tasks = db.query(ProjetoPendencia).filter(
            ProjetoPendencia.id_projeto == p.id, ProjetoPendencia.concluida == True
        ).count()
        progresso = round((done_tasks / total_tasks) * 100, 1) if total_tasks > 0 else 0
        # Count alerts via machines linked to this project
        proj_machine_ids = select(Maquina.id).where(Maquina.id_projeto == p.id)
        alert_count = db.query(Alerta).filter(Alerta.maquina_id.in_(proj_machine_ids)).count()
        proj_list.append({
            "id": p.id,
            "nome_contrato": p.nome_contrato,
            "status": p.status,
            "valor_contrato": float(p.valor_contrato) if p.valor_contrato else 0,
            "prazo": p.prazo.isoformat() if p.prazo else None,
            "dias_atraso": p.dias_atraso,
            "risco": p.risco,
            "progresso": progresso,
            "alert_count": alert_count,
        })

    maquinas = db.query(Maquina).all()
    maq_list = [{
        "id": str(m.id),
        "codigo": m.codigo,
        "nome": m.nome,
        "status": m.status.value,
        "id_projeto": m.id_projeto,
        "ultima_leitura": m.ultima_leitura.isoformat() if m.ultima_leitura else None,
    } for m in maquinas]

    # Build a maquina_id -> id_projeto map for quick lookup
    maq_proj_map = {str(m.id): m.id_projeto for m in maquinas}

    alertas = db.query(Alerta).limit(200).all()
    alerta_list = [{
        "id": str(a.id),
        "codigo_alerta": a.codigo_alerta,
        "titulo": a.titulo,
        "severidade": a.severidade.value,
        "status": a.status.value,
        "maquina_id": str(a.maquina_id),
        "id_projeto": maq_proj_map.get(str(a.maquina_id)),
        "timestamp_criacao": a.timestamp_criacao.isoformat() if a.timestamp_criacao else None,
    } for a in alertas]

    git_logs = db.query(GitOpsAuditoria).order_by(GitOpsAuditoria.timestamp_verificacao.desc()).limit(100).all()
    git_list = [{
        "id": str(g.id),
        "id_projeto": g.id_projeto,
        "diff_resumo": g.diff_resumo,
        "em_sync": g.em_sync,
        "timestamp": g.timestamp_verificacao.isoformat() if g.timestamp_verificacao else None,
    } for g in git_logs]

    return {
        "projects": proj_list,
        "machines": maq_list,
        "alerts": alerta_list,
        "git_logs": git_list,
        "current_user": {
            "id": str(usuario.id),
            "nome": usuario.nome,
            "perfil": usuario.perfil.value if hasattr(usuario.perfil, "value") else usuario.perfil,
        },
        "fetched_at": datetime.utcnow().isoformat(),
    }


class AssignTechnicianRequest(BaseModel):
    id_tecnico: str


@router.post("/projects/{id}/assign-technician")
def assign_technician(
    id: str,
    body: AssignTechnicianRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    """Assigns a technician to a project and updates status to TECNICO_ESCALADO."""
    proj = db.query(Projeto).filter(Projeto.id == id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")

    tecnico = db.query(Usuario).filter(
        Usuario.id == body.id_tecnico,
        Usuario.perfil == PerfilUsuario.tecnico_campo,
    ).first()
    if not tecnico:
        raise HTTPException(status_code=404, detail="Technician not found")

    proj.status = "TECNICO_ESCALADO"
    db.commit()

    return {
        "message": f"Technician {tecnico.nome} assigned to {proj.nome_contrato}",
        "id_projeto": id,
        "id_tecnico": body.id_tecnico,
        "status": proj.status,
    }
