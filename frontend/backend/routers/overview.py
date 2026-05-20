from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database.connection import get_db
from database.models import (
    Projeto, Alerta, LogAuditoriaGit
)

router = APIRouter(prefix="/overview", tags=["Overview"])

@router.get("/kpis")
def get_overview_kpis(db: Session = Depends(get_db)):
    # Backlog: COUNT(projetos) WHERE status IN ('AGUARDANDO_DADOS', 'EM_REVISAO')
    backlog = db.query(Projeto).filter(Projeto.status.in_(['AGUARDANDO_DADOS', 'EM_REVISAO'])).count()

    # Com Atraso: COUNT(projetos) WHERE dias_atraso > 0
    com_atraso = db.query(Projeto).filter(Projeto.dias_atraso > 0).count()

    # Tempo Médio: AVG(dias_atraso) FROM projetos WHERE status != 'CONCLUIDO'
    tempo_medio = db.query(func.avg(Projeto.dias_atraso)).filter(Projeto.status != 'CONCLUIDO').scalar() or 0

    # Alertas Ativos: COUNT(alertas) WHERE status_acao != 'RESOLVIDO'
    alertas_ativos = db.query(Alerta).filter(Alerta.status_acao != 'RESOLVIDO').count()

    # CLPs c/ Drift: COUNT(log_auditoria_git) WHERE acao = 'PR' AND status = 'PENDING'
    # using acao = 'PR' as an approximation
    clps_drift = db.query(LogAuditoriaGit).filter(LogAuditoriaGit.acao.ilike('%pr%')).count()

    return {
        "backlog": backlog,
        "com_atraso": com_atraso,
        "tempo_medio": round(float(tempo_medio), 1),
        "alertas_ativos": alertas_ativos,
        "clps_drift": clps_drift
    }
