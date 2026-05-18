"""
AltaCLP Intelligence Platform — Router de Comissionamento
Backlog + kanban + risco Anaclara + atualização de status.
"""

import math
from uuid import UUID
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from database.connection import get_db
from database.models import (
    Comissionamento, Maquina, Cliente,
    StatusComissionamento
)
from schemas.schemas import AtualizarStatusComissionamentoRequest

router = APIRouter(prefix="/comissionamentos", tags=["Comissionamento"])


def _enriquecer_comissionamento(c, maq_codigo, cli_nome) -> dict:
    """Converte comissionamento ORM para dict com cálculos."""
    # Calcula dias de atraso dinâmicamente
    dias_atraso = c.dias_atraso or 0
    if c.data_conclusao_prevista and not c.data_conclusao_real:
        hoje = date.today()
        if hoje > c.data_conclusao_prevista:
            dias_atraso = (hoje - c.data_conclusao_prevista).days

    multa_acumulada = 0
    if dias_atraso > 0 and c.multa_por_dia_atraso:
        multa_acumulada = float(c.multa_por_dia_atraso) * dias_atraso

    return {
        "id": str(c.id),
        "maquina_id": str(c.maquina_id),
        "cliente_id": str(c.cliente_id),
        "maquina_codigo": maq_codigo,
        "cliente_nome": cli_nome,
        "status": c.status.value,
        "engenheiro_responsavel": c.engenheiro_responsavel,
        "data_inicio_prevista": c.data_inicio_prevista.isoformat() if c.data_inicio_prevista else None,
        "data_inicio_real": c.data_inicio_real.isoformat() if c.data_inicio_real else None,
        "data_conclusao_prevista": c.data_conclusao_prevista.isoformat() if c.data_conclusao_prevista else None,
        "data_conclusao_real": c.data_conclusao_real.isoformat() if c.data_conclusao_real else None,
        "dias_atraso": dias_atraso,
        "valor_contrato": float(c.valor_contrato) if c.valor_contrato else None,
        "multa_por_dia_atraso": float(c.multa_por_dia_atraso) if c.multa_por_dia_atraso else None,
        "multa_acumulada": multa_acumulada,
        "risco_cancelamento": c.risco_cancelamento,
        "prazo_limite_cliente": c.prazo_limite_cliente.isoformat() if c.prazo_limite_cliente else None,
        "observacoes": c.observacoes,
        "checklist_json": c.checklist_json,
        "bom_json": c.bom_json,
    }


@router.get("")
def listar_comissionamentos(
    status: str = None,
    cliente_id: UUID = None,
    com_atraso: bool = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Lista comissionamentos com filtros e paginação."""
    query = db.query(Comissionamento, Maquina.codigo, Cliente.nome).join(
        Maquina, Comissionamento.maquina_id == Maquina.id
    ).join(
        Cliente, Comissionamento.cliente_id == Cliente.id
    )

    # Filtra apenas os que não estão concluídos/cancelados por padrão
    statuses_ativos = [
        StatusComissionamento.aguardando_dados,
        StatusComissionamento.em_andamento,
        StatusComissionamento.fat_pendente,
        StatusComissionamento.treinamento_operador,
    ]

    if status:
        query = query.filter(Comissionamento.status == status)
    else:
        query = query.filter(Comissionamento.status.in_(statuses_ativos))

    if cliente_id:
        query = query.filter(Comissionamento.cliente_id == cliente_id)
    if com_atraso:
        query = query.filter(Comissionamento.dias_atraso > 0)

    total = query.count()
    offset = (page - 1) * limit
    resultados = query.order_by(
        desc(Comissionamento.risco_cancelamento),
        desc(Comissionamento.dias_atraso)
    ).offset(offset).limit(limit).all()

    dados = [_enriquecer_comissionamento(c, maq, cli) for c, maq, cli in resultados]

    return {
        "dados": dados,
        "total": total,
        "pagina": page,
        "por_pagina": limit,
        "paginas": math.ceil(total / limit) if limit > 0 else 0,
    }


@router.get("/kanban")
def kanban(db: Session = Depends(get_db)):
    """Retorna comissionamentos agrupados por status para o kanban."""
    result = {}
    for status_val in [
        StatusComissionamento.aguardando_dados,
        StatusComissionamento.em_andamento,
        StatusComissionamento.fat_pendente,
        StatusComissionamento.treinamento_operador,
    ]:
        itens = db.query(Comissionamento, Maquina.codigo, Cliente.nome).join(
            Maquina, Comissionamento.maquina_id == Maquina.id
        ).join(
            Cliente, Comissionamento.cliente_id == Cliente.id
        ).filter(
            Comissionamento.status == status_val
        ).order_by(
            desc(Comissionamento.risco_cancelamento),
            desc(Comissionamento.dias_atraso)
        ).all()

        result[status_val.value] = [
            _enriquecer_comissionamento(c, maq, cli) for c, maq, cli in itens
        ]

    return result


@router.get("/risco/anaclara")
def risco_anaclara(db: Session = Depends(get_db)):
    """Detalhamento das máquinas Anaclara com countdown de dias."""
    anaclara = db.query(Cliente).filter(
        Cliente.nome.ilike("%anaclara%")
    ).first()

    if not anaclara:
        return {"erro": "Cliente Anaclara não encontrado"}

    comissionamentos = db.query(Comissionamento, Maquina.codigo).join(
        Maquina, Comissionamento.maquina_id == Maquina.id
    ).filter(
        Comissionamento.cliente_id == anaclara.id,
        Comissionamento.status.in_([
            StatusComissionamento.aguardando_dados,
            StatusComissionamento.em_andamento,
            StatusComissionamento.fat_pendente,
            StatusComissionamento.treinamento_operador,
        ])
    ).all()

    prazo_limite = date(2026, 6, 30)
    dias_restantes = (prazo_limite - date.today()).days

    maquinas = []
    for c, maq_codigo in comissionamentos:
        dias_atraso = c.dias_atraso or 0
        if c.data_conclusao_prevista and date.today() > c.data_conclusao_prevista:
            dias_atraso = (date.today() - c.data_conclusao_prevista).days

        maquinas.append({
            "maquina_codigo": maq_codigo,
            "status": c.status.value,
            "engenheiro": c.engenheiro_responsavel,
            "dias_atraso": dias_atraso,
            "valor_contrato": float(c.valor_contrato) if c.valor_contrato else None,
            "multa_acumulada": float(c.multa_por_dia_atraso or 0) * dias_atraso,
        })

    valor_total = float(anaclara.valor_contrato or 0)
    multa_total = sum(m["multa_acumulada"] for m in maquinas)

    return {
        "cliente": "Anaclara Alimentos",
        "valor_contrato_total": valor_total,
        "prazo_limite": prazo_limite.isoformat(),
        "dias_restantes": dias_restantes,
        "status_geral": "CRÍTICO" if dias_restantes < 30 else "ATENÇÃO",
        "maquinas_pendentes": len(maquinas),
        "multa_acumulada_total": multa_total,
        "maquinas": maquinas,
        "contato": {
            "nome": anaclara.contato_nome,
            "email": anaclara.contato_email,
            "telefone": anaclara.contato_telefone,
        },
        "recomendacao": (
            f"Com {dias_restantes} dias restantes, é necessário concluir {len(maquinas)} "
            f"máquinas. Priorizar engenheiros dedicados e eliminar dependências de dados."
        ),
    }


@router.get("/{comissionamento_id}")
def detalhe_comissionamento(comissionamento_id: UUID, db: Session = Depends(get_db)):
    """Comissionamento completo + checklist + BOM."""
    result = db.query(Comissionamento, Maquina.codigo, Cliente.nome).join(
        Maquina, Comissionamento.maquina_id == Maquina.id
    ).join(
        Cliente, Comissionamento.cliente_id == Cliente.id
    ).filter(Comissionamento.id == comissionamento_id).first()

    if not result:
        raise HTTPException(status_code=404, detail="Comissionamento não encontrado")

    c, maq_codigo, cli_nome = result
    return _enriquecer_comissionamento(c, maq_codigo, cli_nome)


@router.put("/{comissionamento_id}/status")
def atualizar_status(
    comissionamento_id: UUID,
    body: AtualizarStatusComissionamentoRequest,
    db: Session = Depends(get_db)
):
    """Atualiza status do comissionamento."""
    comiss = db.query(Comissionamento).filter(
        Comissionamento.id == comissionamento_id
    ).first()

    if not comiss:
        raise HTTPException(status_code=404, detail="Comissionamento não encontrado")

    try:
        comiss.status = body.novo_status
        if body.observacao:
            obs_anterior = comiss.observacoes or ""
            timestamp = datetime.utcnow().strftime("%d/%m/%Y %H:%M")
            comiss.observacoes = f"{obs_anterior}\n[{timestamp}] {body.observacao}".strip()

        # Se concluído, registra data real
        if body.novo_status == StatusComissionamento.concluido.value:
            comiss.data_conclusao_real = date.today()

        db.commit()
        db.refresh(comiss)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar: {str(e)}")

    return {
        "mensagem": f"Status atualizado para '{body.novo_status}'",
        "comissionamento_id": str(comissionamento_id),
        "novo_status": body.novo_status,
    }
