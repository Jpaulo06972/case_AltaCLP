"""
AltaCLP Intelligence Platform — Router de Alertas
Alertas em tempo real + estatísticas + SSE streaming.
"""

import math
import json
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from database.connection import get_db
from database.models import (
    Alerta, Maquina, Cliente, Usuario, Projeto,
    StatusAlerta, SeveridadeAlerta, TipoAlerta,
    AnaliseAlarme, AgendamentoManutencao, ProjetoTecnico,
)
from routers.auth import get_usuario_atual
from services.tecnico_scope import filtrar_alertas_query, is_tecnico
from schemas.schemas import ResolverAlertaRequest
from services.simulator import TelemetriaSimulator
from services.eng_rag import analisar_causa_raiz_alarme
from pydantic import BaseModel
import uuid as uuid_mod

router = APIRouter(prefix="/alertas", tags=["Alertas"])


@router.get("")
def listar_alertas(
    severidade: str = None,
    status: str = None,
    cliente_id: UUID = None,
    tipo: str = None,
    data_inicio: str = None,
    data_fim: str = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    """Lista alertas com filtros completos e paginação."""
    query = db.query(Alerta, Maquina.codigo, Cliente.nome).join(
        Maquina, Alerta.maquina_id == Maquina.id
    ).join(
        Cliente, Alerta.cliente_id == Cliente.id
    )
    query = filtrar_alertas_query(query, db, usuario)

    if severidade:
        query = query.filter(Alerta.severidade == severidade)
    if status:
        query = query.filter(Alerta.status == status)
    if cliente_id:
        query = query.filter(Alerta.cliente_id == cliente_id)
    if tipo:
        query = query.filter(Alerta.tipo == tipo)
    if data_inicio:
        try:
            dt_inicio = datetime.fromisoformat(data_inicio)
            query = query.filter(Alerta.timestamp_criacao >= dt_inicio)
        except ValueError:
            pass
    if data_fim:
        try:
            dt_fim = datetime.fromisoformat(data_fim)
            query = query.filter(Alerta.timestamp_criacao <= dt_fim)
        except ValueError:
            pass

    total = query.count()
    offset = (page - 1) * limit
    resultados = query.order_by(desc(Alerta.timestamp_criacao)).offset(offset).limit(limit).all()

    dados = []
    for alerta, maquina_codigo, cliente_nome in resultados:
        # Fetch linked project via machine
        maq = db.query(Maquina).filter(Maquina.codigo == maquina_codigo).first()
        id_proj = maq.id_projeto if maq else None
        nome_proj = None
        if id_proj:
            proj = db.query(Projeto).filter(Projeto.id == id_proj).first()
            nome_proj = proj.nome_contrato if proj else None

        dados.append({
            "id": str(alerta.id),
            "maquina_id": str(alerta.maquina_id),
            "cliente_id": str(alerta.cliente_id),
            "codigo_alerta": alerta.codigo_alerta,
            "tipo": alerta.tipo.value,
            "severidade": alerta.severidade.value,
            "titulo": alerta.titulo,
            "descricao": alerta.descricao,
            "valor_sensor": alerta.valor_sensor,
            "threshold_configurado": alerta.threshold_configurado,
            "timestamp_criacao": alerta.timestamp_criacao.isoformat() if alerta.timestamp_criacao else None,
            "timestamp_resolucao": alerta.timestamp_resolucao.isoformat() if alerta.timestamp_resolucao else None,
            "status": alerta.status.value,
            "status_acao": alerta.status.value,
            "foi_visita_gerada": alerta.foi_visita_gerada,
            "custo_visita": float(alerta.custo_visita) if alerta.custo_visita else None,
            "tecnico_responsavel": alerta.tecnico_responsavel,
            "is_falso_alerta": alerta.is_falso_alerta,
            "origem": alerta.origem.value if alerta.origem else None,
            "maquina_codigo": maquina_codigo,
            "nome_maquina": maquina_codigo,
            "cliente_nome": cliente_nome,
            "id_projeto": id_proj,
            "nome_projeto": nome_proj,
        })

    return {
        "dados": dados,
        "total": total,
        "pagina": page,
        "por_pagina": limit,
        "paginas": math.ceil(total / limit) if limit > 0 else 0,
    }


@router.get("/estatisticas")
def estatisticas_alertas(db: Session = Depends(get_db)):
    """Estatísticas completas de alertas."""
    # Total abertos
    total_abertos = db.query(Alerta).filter(
        Alerta.status == StatusAlerta.aberto
    ).count()

    # Críticos abertos
    criticos = db.query(Alerta).filter(
        Alerta.status == StatusAlerta.aberto,
        Alerta.severidade == SeveridadeAlerta.critico
    ).count()

    # Custo total visitas no mês atual
    inicio_mes = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
    custo_mes = db.query(func.sum(Alerta.custo_visita)).filter(
        Alerta.timestamp_criacao >= inicio_mes,
        Alerta.custo_visita.isnot(None)
    ).scalar() or 0

    # Taxa de falso alerta geral (últimos 90 dias)
    data_90d = datetime.utcnow() - timedelta(days=90)
    total_90d = db.query(Alerta).filter(
        Alerta.timestamp_criacao >= data_90d
    ).count()
    falsos_90d = db.query(Alerta).filter(
        Alerta.timestamp_criacao >= data_90d,
        Alerta.is_falso_alerta == True
    ).count()
    taxa_falso = (falsos_90d / total_90d * 100) if total_90d > 0 else 0

    # Por tipo
    por_tipo = {}
    for tipo in TipoAlerta:
        count = db.query(Alerta).filter(
            Alerta.tipo == tipo,
            Alerta.timestamp_criacao >= data_90d
        ).count()
        if count > 0:
            por_tipo[tipo.value] = count

    # Por cliente (top 5)
    por_cliente_raw = db.query(
        Cliente.nome, func.count(Alerta.id)
    ).join(
        Cliente, Alerta.cliente_id == Cliente.id
    ).filter(
        Alerta.timestamp_criacao >= data_90d
    ).group_by(Cliente.nome).order_by(
        desc(func.count(Alerta.id))
    ).limit(5).all()

    por_cliente = {nome: count for nome, count in por_cliente_raw}

    return {
        "total_abertos": total_abertos,
        "criticos": criticos,
        "custo_total_visitas_mes": float(custo_mes),
        "taxa_falso_alerta_geral": round(taxa_falso, 1),
        "por_tipo": por_tipo,
        "por_cliente": por_cliente,
    }


@router.get("/stream")
async def stream_alertas():
    """
    SSE (Server-Sent Events) — envia novo alerta simulado a cada 15 segundos.
    Conecte com EventSource no frontend.
    """
    return StreamingResponse(
        TelemetriaSimulator.gerar_evento_sse(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.get("/{alerta_id}")
def detalhe_alerta(alerta_id: UUID, db: Session = Depends(get_db)):
    """Alerta completo + histórico da máquina + sugestão de ação."""
    result = db.query(Alerta, Maquina, Cliente).join(
        Maquina, Alerta.maquina_id == Maquina.id
    ).join(
        Cliente, Alerta.cliente_id == Cliente.id
    ).filter(Alerta.id == alerta_id).first()

    if not result:
        raise HTTPException(status_code=404, detail={
            "erro": True,
            "codigo": "ALERTA_NAO_ENCONTRADO",
            "mensagem": f"Alerta {alerta_id} não existe",
            "status": 404
        })

    alerta, maquina, cliente = result

    # Sugestão de ação baseada no tipo
    sugestoes = {
        TipoAlerta.temperatura_alta: "Verificar sistema de refrigeração e ventilação. Considerar redução de carga no turno atual.",
        TipoAlerta.pressao_alta: "Inspecionar válvulas de alívio e conexões. Verificar se há obstrução na linha.",
        TipoAlerta.vibracao_alta: "Verificar alinhamento do eixo e estado dos rolamentos. Possível desbalanceamento.",
        TipoAlerta.corrente_alta: "Verificar carga mecânica do motor. Possível travamento ou sobrecarga.",
        TipoAlerta.drift_codigo: "URGENTE: Código do CLP diverge do repositório. Verificar com engenharia antes de operar.",
        TipoAlerta.anomalia_ml: "Padrão anômalo detectado pelo modelo ML. Inspeção preventiva recomendada.",
        TipoAlerta.sem_comunicacao: "Verificar conexão de rede/gateway. Pode ser queda de energia ou falha no switch.",
    }

    return {
        "alerta": {
            "id": str(alerta.id),
            "codigo_alerta": alerta.codigo_alerta,
            "tipo": alerta.tipo.value,
            "severidade": alerta.severidade.value,
            "titulo": alerta.titulo,
            "descricao": alerta.descricao,
            "valor_sensor": alerta.valor_sensor,
            "threshold_configurado": alerta.threshold_configurado,
            "timestamp_criacao": alerta.timestamp_criacao.isoformat() if alerta.timestamp_criacao else None,
            "timestamp_resolucao": alerta.timestamp_resolucao.isoformat() if alerta.timestamp_resolucao else None,
            "status": alerta.status.value,
            "foi_visita_gerada": alerta.foi_visita_gerada,
            "custo_visita": float(alerta.custo_visita) if alerta.custo_visita else None,
            "tecnico_responsavel": alerta.tecnico_responsavel,
            "resolucao_descricao": alerta.resolucao_descricao,
            "is_falso_alerta": alerta.is_falso_alerta,
            "origem": alerta.origem.value if alerta.origem else None,
        },
        "maquina": {
            "codigo": maquina.codigo,
            "nome": maquina.nome,
            "status": maquina.status.value,
            "taxa_falso_alerta": maquina.taxa_falso_alerta,
        },
        "cliente": {
            "nome": cliente.nome,
            "nps_score": cliente.nps_score,
            "risco_cancelamento": cliente.risco_cancelamento.value if cliente.risco_cancelamento else None,
        },
        "sugestao_acao": sugestoes.get(alerta.tipo, "Inspeção técnica recomendada."),
    }


@router.post("/{alerta_id}/resolver")
def resolver_alerta(
    alerta_id: UUID,
    body: ResolverAlertaRequest,
    db: Session = Depends(get_db)
):
    """Resolve um alerta com descrição e marcação de falso alerta."""
    alerta = db.query(Alerta).filter(Alerta.id == alerta_id).first()
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")

    try:
        alerta.status = StatusAlerta.resolvido if not body.foi_falso_alerta else StatusAlerta.falso_alerta
        alerta.resolucao_descricao = body.resolucao
        alerta.is_falso_alerta = body.foi_falso_alerta
        alerta.timestamp_resolucao = datetime.utcnow()

        if body.custo_visita is not None:
            alerta.custo_visita = body.custo_visita
            alerta.foi_visita_gerada = True

        db.commit()
        db.refresh(alerta)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao resolver: {str(e)}")

    return {
        "mensagem": "Alerta resolvido com sucesso",
        "alerta_id": str(alerta.id),
        "status": alerta.status.value,
        "foi_falso_alerta": alerta.is_falso_alerta,
    }


class AprovarSugestaoRequest(BaseModel):
    id_tecnico: str
    data_agendada: str
    notificar_cliente: bool = True


class RelatorioManualRequest(BaseModel):
    diretiva: str
    id_tecnico: str
    data_agendada: str


@router.get("/{alerta_id}/analise-ia")
async def obter_analise_ia(alerta_id: UUID, db: Session = Depends(get_db)):
    """Retorna análise de causa raiz (pré-gerada ou sob demanda)."""
    existente = db.query(AnaliseAlarme).filter(AnaliseAlarme.alerta_id == alerta_id).first()
    if existente:
        return {
            "alerta_id": str(alerta_id),
            "texto_analise": existente.texto_analise,
            "sugestao_acao": existente.sugestao_acao,
            "gerado_em": existente.gerado_em.isoformat() if existente.gerado_em else None,
            "cache": True,
        }
    texto = await analisar_causa_raiz_alarme(db, str(alerta_id))
    analise = AnaliseAlarme(
        id=uuid_mod.uuid4(),
        alerta_id=alerta_id,
        texto_analise=texto,
        sugestao_acao="Despachar técnico para inspeção in loco nas próximas 24h.",
    )
    db.add(analise)
    db.commit()
    return {
        "alerta_id": str(alerta_id),
        "texto_analise": texto,
        "sugestao_acao": analise.sugestao_acao,
        "cache": False,
    }


def _simular_notificacoes(alerta: Alerta, tecnico: str, data_ag: datetime, cliente_nome: str):
    return {
        "whatsapp_cliente": f"Alerta {alerta.codigo_alerta} registrado — equipe acionada.",
        "email_tecnico": f"OS #{alerta.codigo_alerta} — agendado {data_ag.strftime('%d/%m/%Y %H:%M')} — {cliente_nome}",
        "enviado": True,
    }


@router.post("/{alerta_id}/aprovar-sugestao")
async def aprovar_sugestao_ia(
    alerta_id: UUID,
    body: AprovarSugestaoRequest,
    db: Session = Depends(get_db),
):
    """Aprova sugestão IA e agenda técnico automaticamente."""
    alerta = db.query(Alerta).filter(Alerta.id == alerta_id).first()
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    data_ag = datetime.fromisoformat(body.data_agendada.replace("Z", ""))
    ag = AgendamentoManutencao(
        id=uuid_mod.uuid4(),
        alerta_id=alerta_id,
        id_tecnico=body.id_tecnico,
        id_cliente=alerta.cliente_id,
        data_agendada=data_ag,
        aprovado_ia=True,
        notificacao_enviada=True,
    )
    alerta.status = StatusAlerta.em_investigacao
    alerta.tecnico_responsavel = body.id_tecnico
    db.add(ag)
    cliente = db.query(Cliente).filter(Cliente.id == alerta.cliente_id).first()
    db.commit()
    notif = _simular_notificacoes(alerta, body.id_tecnico, data_ag, cliente.nome if cliente else "")
    return {
        "agendamento_id": str(ag.id),
        "data_agendada": data_ag.isoformat(),
        "tecnico": body.id_tecnico,
        "notificacoes": notif,
    }


@router.post("/{alerta_id}/relatorio-manual")
def relatorio_manual(
    alerta_id: UUID,
    body: RelatorioManualRequest,
    db: Session = Depends(get_db),
):
    """Engenheiro envia diretiva manual ao técnico."""
    alerta = db.query(Alerta).filter(Alerta.id == alerta_id).first()
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    data_ag = datetime.fromisoformat(body.data_agendada.replace("Z", ""))
    ag = AgendamentoManutencao(
        id=uuid_mod.uuid4(),
        alerta_id=alerta_id,
        id_tecnico=body.id_tecnico,
        id_cliente=alerta.cliente_id,
        data_agendada=data_ag,
        diretiva_manual=body.diretiva,
        aprovado_ia=False,
        notificacao_enviada=True,
    )
    alerta.tecnico_responsavel = body.id_tecnico
    alerta.status = StatusAlerta.em_investigacao
    db.add(ag)
    db.commit()
    return {
        "agendamento_id": str(ag.id),
        "diretiva": body.diretiva,
        "data_agendada": data_ag.isoformat(),
    }


@router.get("/{alerta_id}/agendamento")
def obter_agendamento(alerta_id: UUID, db: Session = Depends(get_db)):
    ag = (
        db.query(AgendamentoManutencao)
        .filter(AgendamentoManutencao.alerta_id == alerta_id)
        .order_by(desc(AgendamentoManutencao.criado_em))
        .first()
    )
    if not ag:
        return {"agendado": False}
    return {
        "agendado": True,
        "id_tecnico": ag.id_tecnico,
        "data_agendada": ag.data_agendada.isoformat(),
        "aprovado_ia": ag.aprovado_ia,
        "diretiva_manual": ag.diretiva_manual,
        "status": ag.status,
    }
