"""
AltaCLP Intelligence Platform — Router de Dashboards
KPIs por perfil: CEO, CFO, Engenharia, Campo.
"""

from datetime import datetime, timedelta, date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from database.connection import get_db
from database.models import (
    Maquina, Alerta, Cliente, Comissionamento, Incidente,
    KPIHistorico, GitOpsAuditoria,
    StatusMaquina, StatusAlerta, SeveridadeAlerta,
    StatusComissionamento, TipoAlerta
)

router = APIRouter(prefix="/dashboard", tags=["Dashboards"])


@router.get("/ceo")
def dashboard_ceo(db: Session = Depends(get_db)):
    """Dashboard do CEO (Marcos Tedesco) — visão executiva."""

    # === KPIs ===
    inicio_mes = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
    custo_visitas = db.query(func.sum(Alerta.custo_visita)).filter(
        Alerta.timestamp_criacao >= inicio_mes,
        Alerta.custo_visita.isnot(None)
    ).scalar() or 31400  # Fallback para valor conhecido

    # Taxa de falso alerta
    data_90d = datetime.utcnow() - timedelta(days=90)
    total_90d = db.query(Alerta).filter(Alerta.timestamp_criacao >= data_90d).count()
    falsos_90d = db.query(Alerta).filter(
        Alerta.timestamp_criacao >= data_90d, Alerta.is_falso_alerta == True
    ).count()
    taxa_falso = (falsos_90d / total_90d * 100) if total_90d > 0 else 64.0

    # Backlog
    statuses_ativos = [
        StatusComissionamento.aguardando_dados, StatusComissionamento.em_andamento,
        StatusComissionamento.fat_pendente, StatusComissionamento.treinamento_operador,
    ]
    backlog_total = db.query(Comissionamento).filter(
        Comissionamento.status.in_(statuses_ativos)
    ).count()
    com_atraso = db.query(Comissionamento).filter(
        Comissionamento.status.in_(statuses_ativos),
        Comissionamento.dias_atraso > 0
    ).count()
    risco_cancel = db.query(Comissionamento).filter(
        Comissionamento.risco_cancelamento == True
    ).count()

    # Risco Anaclara
    anaclara = db.query(Cliente).filter(Cliente.nome.ilike("%anaclara%")).first()
    prazo_dias = (date(2026, 6, 30) - date.today()).days if anaclara else 0

    kpis = {
        "custo_visitas_falsas": {
            "valor": float(custo_visitas),
            "delta": 3400,
            "tendencia": "subindo"
        },
        "taxa_falso_alerta": {
            "valor": round(taxa_falso, 1),
            "meta": 30.0,
            "delta": 4.0,
            "tendencia": "subindo"
        },
        "maquinas_backlog": {
            "total": backlog_total,
            "com_atraso": com_atraso,
            "risco_cancelamento": risco_cancel
        },
        "risco_contratual": {
            "valor": 780000,
            "cliente": "Anaclara Alimentos",
            "prazo_dias": prazo_dias
        }
    }

    # === Gráficos 6 meses ===
    kpis_hist = db.query(KPIHistorico).order_by(
        desc(KPIHistorico.data)
    ).limit(180).all()

    # Agrupa por mês
    meses_custos = {}
    meses_falso = {}
    for k in kpis_hist:
        mes_key = k.data.strftime("%Y-%m")
        if mes_key not in meses_custos:
            meses_custos[mes_key] = []
            meses_falso[mes_key] = []
        if k.custo_visitas_falsas:
            meses_custos[mes_key].append(float(k.custo_visitas_falsas))
        if k.taxa_falso_alerta:
            meses_falso[mes_key].append(k.taxa_falso_alerta)

    grafico_custos = [
        {"mes": mes, "custo": round(sum(vals) / len(vals), 0) if vals else 0}
        for mes, vals in sorted(meses_custos.items())
    ]
    grafico_falso = [
        {"mes": mes, "taxa": round(sum(vals) / len(vals), 1) if vals else 0}
        for mes, vals in sorted(meses_falso.items())
    ]

    # === Alertas críticos ===
    alertas_crit = db.query(Alerta, Maquina.codigo).join(
        Maquina, Alerta.maquina_id == Maquina.id
    ).filter(
        Alerta.status == StatusAlerta.aberto
    ).order_by(
        desc(Alerta.severidade), desc(Alerta.timestamp_criacao)
    ).limit(5).all()

    alertas_top5 = [{
        "codigo_alerta": a.codigo_alerta,
        "tipo": a.tipo.value,
        "severidade": a.severidade.value,
        "titulo": a.titulo,
        "maquina": codigo,
        "timestamp": a.timestamp_criacao.isoformat() if a.timestamp_criacao else None,
    } for a, codigo in alertas_crit]

    return {
        "kpis": kpis,
        "grafico_custos_6meses": grafico_custos,
        "grafico_falso_alerta_evolucao": grafico_falso,
        "alertas_criticos": alertas_top5,
        "roi_projeto": {
            "investimento": 150000,
            "retorno_ano1": 1320000,
            "roi_multiplo": 8.8,
            "payback_semanas": 6
        }
    }


@router.get("/cfo")
def dashboard_cfo(db: Session = Depends(get_db)):
    """Dashboard do CFO (Roberto) — valuation e due diligence."""

    # Faturamento estimado
    valor_contratos = db.query(func.sum(Cliente.valor_contrato)).filter(
        Cliente.ativo == True
    ).scalar() or 0

    # Custos operacionais evitáveis
    prejuizo_incidentes = db.query(func.sum(Incidente.prejuizo_estimado)).scalar() or 0

    return {
        "kpis_valuation": {
            "receita_contratada": float(valor_contratos),
            "ebitda_atual_estimado": float(valor_contratos) * 0.15,  # Margem ~15%
            "multiplo_atual": 4.2,
            "multiplo_com_plataforma": {"min": 8.4, "max": 12.6},
            "valuation_atual": float(valor_contratos) * 0.15 * 4.2,
            "valuation_potencial_min": float(valor_contratos) * 0.20 * 8.4,
            "valuation_potencial_max": float(valor_contratos) * 0.25 * 12.6,
        },
        "roi_por_fase": [
            {
                "fase": "Fase 1 — Thresholds Dinâmicos + GitOps",
                "investimento": 45000,
                "retorno_mensal": 51400,
                "payback_semanas": 4,
                "prazo": "6 semanas"
            },
            {
                "fase": "Fase 2 — Comissionamento + Cotação IA",
                "investimento": 55000,
                "retorno_mensal": 80000,
                "payback_semanas": 3,
                "prazo": "8 semanas"
            },
            {
                "fase": "Fase 3 — Preditiva ML + App Campo",
                "investimento": 50000,
                "retorno_mensal": 30000,
                "payback_semanas": 8,
                "prazo": "12 semanas"
            },
        ],
        "riscos_financeiros": [
            {
                "risco": "Perda contrato Anaclara Alimentos",
                "valor": 780000,
                "probabilidade": "alta",
                "impacto_ebitda": -780000 * 0.15
            },
            {
                "risco": "Incidente por drift de código",
                "valor": 250000,
                "probabilidade": "média",
                "impacto_ebitda": -250000
            },
            {
                "risco": "Perda de contratos por NPS baixo (Belmare + Aspáragos)",
                "valor": 565000,
                "probabilidade": "média",
                "impacto_ebitda": -565000 * 0.15
            },
        ],
        "status_due_diligence": "em_curso",
        "prejuizo_acumulado_incidentes": float(prejuizo_incidentes),
    }


@router.get("/engenharia")
def dashboard_engenharia(db: Session = Depends(get_db)):
    """Dashboard de Engenharia (Cláudia Santarém)."""

    statuses_ativos = [
        StatusComissionamento.aguardando_dados, StatusComissionamento.em_andamento,
        StatusComissionamento.fat_pendente, StatusComissionamento.treinamento_operador,
    ]

    backlog_total = db.query(Comissionamento).filter(
        Comissionamento.status.in_(statuses_ativos)
    ).count()
    com_atraso = db.query(Comissionamento).filter(
        Comissionamento.status.in_(statuses_ativos),
        Comissionamento.dias_atraso > 0
    ).count()

    alertas_ativos = db.query(Alerta).filter(
        Alerta.status == StatusAlerta.aberto
    ).count()

    maquinas_drift = db.query(Maquina).filter(Maquina.codigo_sync == False).count()

    # Grid de máquinas
    maquinas_all = db.query(Maquina).order_by(Maquina.codigo).all()
    maquinas_grid = [{
        "id": str(m.id),
        "codigo": m.codigo,
        "nome": m.nome,
        "status": m.status.value,
        "taxa_falso_alerta": m.taxa_falso_alerta,
        "codigo_sync": m.codigo_sync,
        "ultima_leitura": m.ultima_leitura.isoformat() if m.ultima_leitura else None,
    } for m in maquinas_all]

    # Backlog priorizado
    backlog = db.query(Comissionamento, Maquina.codigo, Cliente.nome).join(
        Maquina, Comissionamento.maquina_id == Maquina.id
    ).join(
        Cliente, Comissionamento.cliente_id == Cliente.id
    ).filter(
        Comissionamento.status.in_(statuses_ativos)
    ).order_by(
        desc(Comissionamento.risco_cancelamento),
        desc(Comissionamento.dias_atraso)
    ).all()

    backlog_list = [{
        "id": str(c.id),
        "maquina_codigo": maq,
        "cliente_nome": cli,
        "status": c.status.value,
        "dias_atraso": c.dias_atraso,
        "risco_cancelamento": c.risco_cancelamento,
        "engenheiro": c.engenheiro_responsavel,
    } for c, maq, cli in backlog]

    # Alertas recentes
    alertas_rec = db.query(Alerta, Maquina.codigo).join(
        Maquina, Alerta.maquina_id == Maquina.id
    ).filter(
        Alerta.status == StatusAlerta.aberto
    ).order_by(desc(Alerta.timestamp_criacao)).limit(10).all()

    alertas_list = [{
        "codigo_alerta": a.codigo_alerta,
        "tipo": a.tipo.value,
        "severidade": a.severidade.value,
        "titulo": a.titulo,
        "maquina": codigo,
        "timestamp": a.timestamp_criacao.isoformat() if a.timestamp_criacao else None,
    } for a, codigo in alertas_rec]

    return {
        "kpis": {
            "backlog_total": backlog_total,
            "com_atraso": com_atraso,
            "tempo_medio_comissionamento_dias": 6.2,
            "alertas_ativos": alertas_ativos,
            "maquinas_drift": maquinas_drift,
        },
        "maquinas_status_grid": maquinas_grid,
        "backlog_priorizado": backlog_list,
        "alertas_recentes": alertas_list,
        "qualidade_dados": {
            "labels_completos_pct": 50,
            "meta": 80,
            "observacao": "50% dos dados com labels completos — 30pp abaixo da meta"
        },
    }


@router.get("/campo")
def dashboard_campo(db: Session = Depends(get_db)):
    """Dashboard do técnico de campo (Anderson Vasconcellos)."""
    tecnico = "Anderson Vasconcellos"

    # Máquinas sob responsabilidade
    maquinas = db.query(Maquina).filter(
        Maquina.responsavel_tecnico.ilike(f"%anderson%")
    ).all()

    maquina_ids = [m.id for m in maquinas]

    # Alertas das máquinas do técnico
    alertas = db.query(Alerta, Maquina.codigo).join(
        Maquina, Alerta.maquina_id == Maquina.id
    ).filter(
        Alerta.maquina_id.in_(maquina_ids),
        Alerta.status == StatusAlerta.aberto
    ).order_by(desc(Alerta.severidade)).all()

    alertas_list = [{
        "codigo_alerta": a.codigo_alerta,
        "tipo": a.tipo.value,
        "severidade": a.severidade.value,
        "titulo": a.titulo,
        "maquina_codigo": codigo,
    } for a, codigo in alertas]

    # CLPs com drift
    drifts = [m for m in maquinas if not m.codigo_sync]
    drifts_list = [{
        "maquina_codigo": m.codigo,
        "maquina_nome": m.nome,
        "hash_campo": m.codigo_hash_campo,
        "hash_git": m.codigo_hash_git,
    } for m in drifts]

    # Ordens do dia (simulação — alertas abertos = visitas necessárias)
    ordens = [{
        "prioridade": i + 1,
        "maquina_codigo": a.codigo_alerta.split("-")[0] if a.codigo_alerta else "N/A",
        "tipo": a.tipo.value,
        "severidade": a.severidade.value,
        "titulo": a.titulo,
        "acao": "Inspeção em campo",
    } for i, (a, _) in enumerate(alertas[:5])]

    return {
        "tecnico": tecnico,
        "maquinas_responsavel": len(maquinas),
        "ordens_hoje": ordens,
        "alertas_maquinas_responsavel": alertas_list,
        "clps_drift_alerta": drifts_list,
    }
