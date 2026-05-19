"""
AltaCLP Intelligence Platform — Router de Máquinas (CLPs)
CRUD + telemetria + alertas + thresholds + estatísticas.
"""

import math
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from database.connection import get_db
from database.models import (
    Maquina, Cliente, LeituraSensor, Alerta, Usuario,
    StatusMaquina, StatusAlerta, LogThreshold,
)
from routers.auth import get_usuario_atual
from services.tecnico_scope import filtrar_maquinas_query, assert_maquina_acesso
from schemas.schemas import (
    MaquinaResponse, MaquinaDetalheResponse, LeituraSensorResponse,
    AlertaResponse, ThresholdUpdateRequest, ThresholdUpdateResponse,
    EstatisticasMaquinaResponse, PaginatedResponse
)
from services.threshold_engine import ThresholdEngine

router = APIRouter(prefix="/maquinas", tags=["Máquinas (CLPs)"])


def _maquina_to_response(m: Maquina, cliente_nome: str = None) -> dict:
    """Converte ORM Maquina para dict de resposta."""
    return {
        "id": m.id,
        "cliente_id": m.cliente_id,
        "codigo": m.codigo,
        "nome": m.nome,
        "modelo_clp": m.modelo_clp.value if m.modelo_clp else None,
        "protocolo": m.protocolo.value if m.protocolo else None,
        "setor_planta": m.setor_planta,
        "status": m.status.value if m.status else None,
        "taxa_falso_alerta": m.taxa_falso_alerta,
        "codigo_hash_campo": m.codigo_hash_campo,
        "codigo_hash_git": m.codigo_hash_git,
        "codigo_sync": m.codigo_sync,
        "ultima_verificacao_gitops": m.ultima_verificacao_gitops,
        "ultima_leitura": m.ultima_leitura,
        "data_instalacao": m.data_instalacao,
        "responsavel_tecnico": m.responsavel_tecnico,
        "dias_sem_incidente": m.dias_sem_incidente,
        "threshold_temperatura_max": m.threshold_temperatura_max,
        "threshold_pressao_max": m.threshold_pressao_max,
        "threshold_vibracao_max": m.threshold_vibracao_max,
        "threshold_corrente_max": m.threshold_corrente_max,
        "latitude": m.latitude,
        "longitude": m.longitude,
        "observacoes": m.observacoes,
        "cliente_nome": cliente_nome,
    }


@router.get("")
def listar_maquinas(
    status: str = None,
    cliente_id: UUID = None,
    protocolo: str = None,
    codigo_sync: bool = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    """Lista máquinas com filtros e paginação."""
    query = db.query(Maquina, Cliente.nome).join(Cliente, Maquina.cliente_id == Cliente.id)
    query = filtrar_maquinas_query(query, db, usuario)

    if status:
        query = query.filter(Maquina.status == status)
    if cliente_id:
        query = query.filter(Maquina.cliente_id == cliente_id)
    if protocolo:
        query = query.filter(Maquina.protocolo == protocolo)
    if codigo_sync is not None:
        query = query.filter(Maquina.codigo_sync == codigo_sync)

    total = query.count()
    offset = (page - 1) * limit
    resultados = query.order_by(Maquina.codigo).offset(offset).limit(limit).all()

    dados = [_maquina_to_response(m, nome) for m, nome in resultados]

    return {
        "dados": dados,
        "total": total,
        "pagina": page,
        "por_pagina": limit,
        "paginas": math.ceil(total / limit) if limit > 0 else 0
    }


@router.get("/estatisticas/resumo")
def estatisticas_resumo(db: Session = Depends(get_db)):
    """Contagem por status, taxa média de falso alerta, top 10 piores máquinas."""
    # Contagem por status
    por_status = {}
    for status in StatusMaquina:
        count = db.query(Maquina).filter(Maquina.status == status).count()
        por_status[status.value] = count

    # Taxa média de falso alerta
    taxa_media = db.query(func.avg(Maquina.taxa_falso_alerta)).scalar() or 0

    # Top 10 piores máquinas (maior taxa de falso alerta)
    top10 = db.query(Maquina, Cliente.nome).join(
        Cliente, Maquina.cliente_id == Cliente.id
    ).order_by(
        desc(Maquina.taxa_falso_alerta)
    ).limit(10).all()

    top10_list = [
        {
            "codigo": m.codigo,
            "nome": m.nome,
            "status": m.status.value,
            "taxa_falso_alerta": m.taxa_falso_alerta,
            "cliente": nome,
            "dias_sem_incidente": m.dias_sem_incidente,
        }
        for m, nome in top10
    ]

    return {
        "total": sum(por_status.values()),
        "por_status": por_status,
        "taxa_media_falso_alerta": round(float(taxa_media), 1),
        "top_10_piores": top10_list
    }


@router.get("/{maquina_id}")
def detalhe_maquina(
    maquina_id: UUID,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    assert_maquina_acesso(db, usuario, maquina_id)
    """Máquina completa + últimas 24h de telemetria + alertas recentes."""
    result = db.query(Maquina, Cliente.nome).join(
        Cliente, Maquina.cliente_id == Cliente.id
    ).filter(Maquina.id == maquina_id).first()

    if not result:
        raise HTTPException(status_code=404, detail={
            "erro": True,
            "codigo": "MAQUINA_NAO_ENCONTRADA",
            "mensagem": f"Máquina {maquina_id} não existe",
            "status": 404
        })

    maquina, cliente_nome = result
    cliente = db.query(Cliente).filter(Cliente.id == maquina.cliente_id).first()

    # Últimas 24h de telemetria
    data_24h = datetime.utcnow() - timedelta(hours=24)
    leituras = db.query(LeituraSensor).filter(
        LeituraSensor.maquina_id == maquina_id,
        LeituraSensor.timestamp >= data_24h
    ).order_by(desc(LeituraSensor.timestamp)).limit(100).all()

    telemetria = [{
        "timestamp": l.timestamp.isoformat() if l.timestamp else None,
        "temperatura": l.temperatura,
        "pressao": l.pressao,
        "vibracao": l.vibracao,
        "corrente": l.corrente,
        "tensao": l.tensao,
        "turno": l.turno.value if l.turno else None,
    } for l in leituras]

    # Alertas recentes
    alertas = db.query(Alerta).filter(
        Alerta.maquina_id == maquina_id
    ).order_by(desc(Alerta.timestamp_criacao)).limit(10).all()

    alertas_list = [{
        "id": str(a.id),
        "codigo_alerta": a.codigo_alerta,
        "tipo": a.tipo.value,
        "severidade": a.severidade.value,
        "titulo": a.titulo,
        "status": a.status.value,
        "timestamp": a.timestamp_criacao.isoformat() if a.timestamp_criacao else None,
    } for a in alertas]

    return {
        "maquina": _maquina_to_response(maquina, cliente_nome),
        "cliente": {
            "id": cliente.id,
            "nome": cliente.nome,
            "setor": cliente.setor.value,
            "nps_score": cliente.nps_score,
            "risco_cancelamento": cliente.risco_cancelamento.value if cliente.risco_cancelamento else None,
        } if cliente else None,
        "telemetria_24h": telemetria,
        "alertas_recentes": alertas_list,
    }


@router.get("/{maquina_id}/telemetria")
def telemetria_maquina(
    maquina_id: UUID,
    horas: int = Query(24, ge=1, le=720),
    sensor: str = Query("todos"),
    db: Session = Depends(get_db)
):
    """Série temporal de leituras de uma máquina."""
    maquina = db.query(Maquina).filter(Maquina.id == maquina_id).first()
    if not maquina:
        raise HTTPException(status_code=404, detail="Máquina não encontrada")

    data_inicio = datetime.utcnow() - timedelta(hours=horas)
    leituras = db.query(LeituraSensor).filter(
        LeituraSensor.maquina_id == maquina_id,
        LeituraSensor.timestamp >= data_inicio
    ).order_by(LeituraSensor.timestamp).all()

    dados = []
    for l in leituras:
        ponto = {"timestamp": l.timestamp.isoformat() if l.timestamp else None}
        if sensor == "todos" or sensor == "temperatura":
            ponto["temperatura"] = l.temperatura
        if sensor == "todos" or sensor == "pressao":
            ponto["pressao"] = l.pressao
        if sensor == "todos" or sensor == "vibracao":
            ponto["vibracao"] = l.vibracao
        if sensor == "todos" or sensor == "corrente":
            ponto["corrente"] = l.corrente
        if sensor == "todos":
            ponto["tensao"] = l.tensao
            ponto["rpm"] = l.rpm
            ponto["turno"] = l.turno.value if l.turno else None
        dados.append(ponto)

    return {
        "maquina_codigo": maquina.codigo,
        "periodo_horas": horas,
        "sensor": sensor,
        "total_leituras": len(dados),
        "dados": dados
    }


@router.get("/{maquina_id}/alertas")
def alertas_maquina(
    maquina_id: UUID,
    status: str = None,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Histórico de alertas da máquina."""
    query = db.query(Alerta).filter(Alerta.maquina_id == maquina_id)
    if status:
        query = query.filter(Alerta.status == status)

    alertas = query.order_by(desc(Alerta.timestamp_criacao)).limit(limit).all()

    return {
        "maquina_id": str(maquina_id),
        "total": len(alertas),
        "alertas": [{
            "id": str(a.id),
            "codigo_alerta": a.codigo_alerta,
            "tipo": a.tipo.value,
            "severidade": a.severidade.value,
            "titulo": a.titulo,
            "descricao": a.descricao,
            "valor_sensor": a.valor_sensor,
            "threshold_configurado": a.threshold_configurado,
            "status": a.status.value,
            "is_falso_alerta": a.is_falso_alerta,
            "timestamp": a.timestamp_criacao.isoformat() if a.timestamp_criacao else None,
        } for a in alertas]
    }


@router.put("/{maquina_id}/thresholds")
def atualizar_thresholds(
    maquina_id: UUID,
    body: ThresholdUpdateRequest,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_atual),
):
    """Atualiza thresholds da máquina + previsão de redução de falsos alertas."""
    maquina = db.query(Maquina).filter(Maquina.id == maquina_id).first()
    if not maquina:
        raise HTTPException(status_code=404, detail="Máquina não encontrada")

    anteriores = {
        "temperatura_max": maquina.threshold_temperatura_max,
        "pressao_max": maquina.threshold_pressao_max,
        "vibracao_max": maquina.threshold_vibracao_max,
        "corrente_max": maquina.threshold_corrente_max,
    }

    novos = {}
    if body.temperatura_max is not None:
        maquina.threshold_temperatura_max = body.temperatura_max
        novos["temperatura_max"] = body.temperatura_max
    if body.pressao_max is not None:
        maquina.threshold_pressao_max = body.pressao_max
        novos["pressao_max"] = body.pressao_max
    if body.vibracao_max is not None:
        maquina.threshold_vibracao_max = body.vibracao_max
        novos["vibracao_max"] = body.vibracao_max
    if body.corrente_max is not None:
        maquina.threshold_corrente_max = body.corrente_max
        novos["corrente_max"] = body.corrente_max

    # Calcula redução estimada
    reducao = ThresholdEngine.projetar_reducao_falsos(db, maquina_id, {**anteriores, **novos})

    for param, novo_val in novos.items():
        ant = anteriores.get(param)
        if ant is not None and ant != novo_val:
            db.add(LogThreshold(
                maquina_id=maquina_id,
                parametro_alterado=param,
                valor_antigo=ant,
                valor_novo=novo_val,
                id_usuario=str(usuario.id),
                origem="manual",
            ))

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar: {str(e)}")

    return {
        "maquina_id": str(maquina_id),
        "thresholds_anteriores": anteriores,
        "thresholds_novos": {**anteriores, **novos},
        "reducao_estimada_falsos": reducao
    }
