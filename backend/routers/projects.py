"""
AltaCLP Intelligence Platform — Projects Router
Commissioning relational data: projects, tasks, machines, alerts, git PRs.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from datetime import datetime

from database.connection import get_db
from database.models import (
    Projeto, Maquina, Alerta, LogAuditoriaGit, GitOpsAuditoria,
    ProjetoPendencia, DocumentoComissionamento, Comissionamento, StatusComissionamento
)
import uuid as uuid_mod

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("")
def list_projects(
    status: str = None,
    id_engenheiro: str = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Projeto)
    if status:
        query = query.filter(Projeto.status == status)
    if id_engenheiro:
        query = query.filter(Projeto.id_engenheiro == id_engenheiro)

    total = query.count()
    offset = (page - 1) * limit
    projetos = query.offset(offset).limit(limit).all()

    result = []
    for p in projetos:
        # Compute dynamic values
        progresso = 0
        total_tasks = db.query(ProjetoPendencia).filter(ProjetoPendencia.id_projeto == p.id).count()
        if total_tasks > 0:
            done_tasks = db.query(ProjetoPendencia).filter(
                ProjetoPendencia.id_projeto == p.id, ProjetoPendencia.concluida == True
            ).count()
            progresso = round((done_tasks / total_tasks) * 100, 1)

        # Count alerts via machines linked to this project
        proj_machine_ids = select(Maquina.id).where(Maquina.id_projeto == p.id)
        alert_count = db.query(Alerta).filter(Alerta.maquina_id.in_(proj_machine_ids)).count()

        # Count PRs from LogAuditoriaGit
        pr_count = db.query(LogAuditoriaGit).filter(
            LogAuditoriaGit.id_projeto == p.id
        ).count()

        result.append({
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
            "pr_count": pr_count
        })

    return {
        "dados": result,
        "total": total,
        "page": page,
        "limit": limit
    }


@router.get("/{id}")
def get_project_detail(id: str, db: Session = Depends(get_db)):
    p = db.query(Projeto).filter(Projeto.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")

    total_tasks = db.query(ProjetoPendencia).filter(ProjetoPendencia.id_projeto == p.id).count()
    done_tasks = db.query(ProjetoPendencia).filter(
        ProjetoPendencia.id_projeto == p.id, ProjetoPendencia.concluida == True
    ).count()
    progresso = round((done_tasks / total_tasks) * 100, 1) if total_tasks > 0 else 0

    return {
        "id": p.id,
        "nome_contrato": p.nome_contrato,
        "valor_contrato": float(p.valor_contrato) if p.valor_contrato else 0,
        "prazo": p.prazo.isoformat() if p.prazo else None,
        "dias_atraso": p.dias_atraso,
        "progresso": progresso,
        "status": p.status,
        "id_engenheiro": p.id_engenheiro
    }


@router.get("/{id}/machines")
def get_project_machines(id: str, db: Session = Depends(get_db)):
    machines = db.query(Maquina).filter(Maquina.id_projeto == id).all()
    return [{
        "codigo": m.codigo,
        "nome": m.nome,
        "status": m.status.value,
        "modelo_clp": m.modelo_clp.value if m.modelo_clp else None,
    } for m in machines]


@router.get("/{id}/alerts")
def get_project_alerts(id: str, db: Session = Depends(get_db)):
    """Return alerts for machines linked to this project."""
    proj_machine_ids = select(Maquina.id).where(Maquina.id_projeto == id)
    alerts = db.query(Alerta).filter(
        Alerta.maquina_id.in_(proj_machine_ids)
    ).all()
    return [{
        "id": a.codigo_alerta,
        "descricao": a.titulo,
        "severidade": a.severidade.value,
        "maquina_id": str(a.maquina_id),
    } for a in alerts]


@router.get("/{id}/git-prs")
def get_project_prs(id: str, db: Session = Depends(get_db)):
    prs = db.query(LogAuditoriaGit).filter(LogAuditoriaGit.id_projeto == id).all()
    return [{
        "id": str(pr.id),
        "resumo": pr.diff_resumo,
        "usuario": pr.id_usuario,
        "risco_ia": pr.risco_ia,
    } for pr in prs]


@router.get("/{id}/tasks")
def get_project_tasks(id: str, db: Session = Depends(get_db)):
    tasks = db.query(ProjetoPendencia).filter(
        ProjetoPendencia.id_projeto == id
    ).order_by(ProjetoPendencia.ordem).all()
    return [{
        "id": str(t.id),  # convert UUID to string for frontend
        "titulo": t.titulo,
        "tecnico": t.id_tecnico_atribuido,
        "concluida": t.concluida,
        "status_tarefa": t.status_tarefa.value if t.status_tarefa else "pendente",
    } for t in tasks]


@router.patch("/{id}/tasks/{task_id}")
def update_task_status(id: str, task_id: str, payload: dict, db: Session = Depends(get_db)):
    # Convert task_id string to UUID for query
    try:
        task_uuid = uuid_mod.UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid task UUID: {task_id}")

    task = db.query(ProjetoPendencia).filter(
        ProjetoPendencia.id == task_uuid,
        ProjetoPendencia.id_projeto == id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if "concluida" in payload:
        task.concluida = payload["concluida"]
        if payload["concluida"]:
            task.data_conclusao = datetime.utcnow()
    if "status_tarefa" in payload:
        task.status_tarefa = payload["status_tarefa"]
    db.commit()
    return {"message": "Task updated"}


@router.get("/{id}/documents")
def get_project_docs(id: str, db: Session = Depends(get_db)):
    docs = db.query(DocumentoComissionamento).filter(
        DocumentoComissionamento.id_projeto == id
    ).all()
    return [{
        "id": str(d.id),
        "nome_arquivo": d.nome_arquivo,
        "data": d.data_upload.isoformat() if d.data_upload else None,
    } for d in docs]


@router.post("/{id}/documents")
def upload_document(id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    doc = DocumentoComissionamento(
        id=uuid_mod.uuid4(),
        id_projeto=id,
        id_tecnico="ENG-01",  # mock
        nome_arquivo=file.filename,
        url_documento=f"/uploads/{file.filename}"
    )
    db.add(doc)
    db.commit()
    return {"message": "Upload successful", "id": str(doc.id)}


@router.post("/{id}/submit-validation")
def submit_validation(id: str, db: Session = Depends(get_db)):
    projeto = db.query(Projeto).filter(Projeto.id == id).first()
    if not projeto:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
        
    maq_ids = db.query(Maquina.id).filter(Maquina.id_projeto == id).all()
    maq_ids = [m[0] for m in maq_ids]
    
    comiss = db.query(Comissionamento).filter(Comissionamento.maquina_id.in_(maq_ids)).first()
    
    if comiss:
        if comiss.status == StatusComissionamento.aguardando_dados:
            comiss.status = StatusComissionamento.em_andamento
        elif comiss.status == StatusComissionamento.em_andamento:
            comiss.status = StatusComissionamento.fat_pendente
        elif comiss.status == StatusComissionamento.fat_pendente:
            comiss.status = StatusComissionamento.treinamento_operador
        elif comiss.status == StatusComissionamento.treinamento_operador:
            comiss.status = StatusComissionamento.concluido
            comiss.data_conclusao_real = datetime.utcnow()
    
    db.commit()
    return {"message": f"Projeto avançado para {comiss.status.value if comiss else 'próxima etapa'} com sucesso."}
