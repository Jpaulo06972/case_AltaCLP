"""
AltaCLP Intelligence Platform — Router de Cotação
Processamento de transcrição de áudio → BOM + template de comissionamento.
"""

import uuid
import math
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from database.connection import get_db
from database.models import Cotacao, Cliente, StatusCotacao
from schemas.schemas import CotacaoProcessarRequest
from services.bom_generator import gerar_bom_da_transcricao

router = APIRouter(prefix="/cotacao", tags=["Cotação Técnica"])


@router.post("/processar")
async def processar_cotacao(
    body: CotacaoProcessarRequest,
    db: Session = Depends(get_db)
):
    """
    Processa transcrição de áudio do vendedor e gera BOM + template.
    Tempo médio: 2-5s (com IA) ou <1s (heurístico).
    """
    # Busca cliente se informado
    cliente = None
    if body.cliente_nome:
        cliente = db.query(Cliente).filter(
            Cliente.nome.ilike(f"%{body.cliente_nome}%")
        ).first()

    # Processa com o serviço de BOM
    try:
        resultado = await gerar_bom_da_transcricao(
            transcricao=body.transcricao_audio,
            vendedor=body.vendedor,
            cliente_nome=body.cliente_nome
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar cotação: {str(e)}")

    # Calcula valor estimado da BOM
    valor_total = 0
    bom_items = resultado.get("bom", [])
    for item in bom_items:
        valor_total += item.get("valor_unit", 0) * item.get("quantidade", 1)

    # Estima duração do áudio baseado no tamanho do texto (~150 palavras/min)
    palavras = len(body.transcricao_audio.split())
    duracao_estimada = int(palavras / 2.5)  # ~150 palavras/min falando

    # Persiste no banco
    cotacao = Cotacao(
        id=uuid.uuid4(),
        cliente_id=cliente.id if cliente else None,
        vendedor_nome=body.vendedor,
        audio_transcricao=body.transcricao_audio,
        audio_duracao_segundos=duracao_estimada,
        parametros_extraidos=resultado.get("parametros_extraidos"),
        bom_gerada=resultado.get("bom"),
        template_comissionamento=resultado.get("template_comissionamento"),
        status=StatusCotacao.gerada,
        tempo_processamento_segundos=int(resultado.get("tempo_processamento_segundos", 0)),
        valor_estimado=valor_total,
        data_criacao=datetime.utcnow(),
    )

    try:
        db.add(cotacao)
        db.commit()
        db.refresh(cotacao)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao salvar cotação: {str(e)}")

    return {
        "cotacao_id": str(cotacao.id),
        "parametros_extraidos": resultado.get("parametros_extraidos"),
        "bom": resultado.get("bom"),
        "template_comissionamento": resultado.get("template_comissionamento"),
        "valor_estimado": valor_total,
        "tempo_processamento_segundos": resultado.get("tempo_processamento_segundos"),
        "status": "gerada",
    }


@router.get("")
def listar_cotacoes(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Lista cotações geradas (histórico)."""
    query = db.query(Cotacao)
    total = query.count()
    offset = (page - 1) * limit
    cotacoes = query.order_by(desc(Cotacao.data_criacao)).offset(offset).limit(limit).all()

    dados = [{
        "id": str(c.id),
        "cliente_id": str(c.cliente_id) if c.cliente_id else None,
        "vendedor_nome": c.vendedor_nome,
        "status": c.status.value,
        "valor_estimado": float(c.valor_estimado) if c.valor_estimado else None,
        "tempo_processamento_segundos": c.tempo_processamento_segundos,
        "data_criacao": c.data_criacao.isoformat() if c.data_criacao else None,
        "data_aprovacao": c.data_aprovacao.isoformat() if c.data_aprovacao else None,
        "parametros_extraidos": c.parametros_extraidos,
        "bom_gerada": c.bom_gerada,
    } for c in cotacoes]

    return {
        "dados": dados,
        "total": total,
        "pagina": page,
        "por_pagina": limit,
        "paginas": math.ceil(total / limit) if limit > 0 else 0,
    }
