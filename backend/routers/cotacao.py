"""
AltaCLP Intelligence Platform — Router de Cotação
Processamento de transcrição de áudio → BOM + template de comissionamento.
"""

import uuid
import math
import tempfile
import os
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import desc

from database.connection import get_db
from database.models import Cotacao, Cliente, StatusCotacao, PerfilUsuario, Projeto, Maquina, Comissionamento, StatusComissionamento, FaseProjeto, ModeloCLP, ProtocoloCLP
from schemas.schemas import CotacaoProcessarRequest
from services.bom_generator import gerar_bom_da_transcricao
from middleware.rbac import require_roles
from routers.auth import get_usuario_atual

router = APIRouter(prefix="/cotacao", tags=["Cotação Técnica"])

_cotacao_roles = require_roles(
    PerfilUsuario.vendedor.value,
    PerfilUsuario.ceo.value,
)


async def _salvar_e_retornar_cotacao(transcricao: str, vendedor: str, cliente_nome: str, db: Session):
    cliente = None
    if cliente_nome:
        cliente = db.query(Cliente).filter(
            Cliente.nome.ilike(f"%{cliente_nome}%")
        ).first()

    try:
        resultado = await gerar_bom_da_transcricao(
            transcricao=transcricao,
            vendedor=vendedor,
            cliente_nome=cliente_nome
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar cotação: {str(e)}")

    valor_total = sum(item.get("valor_unit", 0) * item.get("quantidade", 1) for item in resultado.get("bom", []))
    palavras = len(transcricao.split())
    duracao_estimada = int(palavras / 2.5)

    cotacao = Cotacao(
        id=uuid.uuid4(),
        cliente_id=cliente.id if cliente else None,
        vendedor_nome=vendedor,
        audio_transcricao=transcricao,
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
        "transcricao_gerada": transcricao,
        "parametros_extraidos": resultado.get("parametros_extraidos"),
        "bom": resultado.get("bom"),
        "template_comissionamento": resultado.get("template_comissionamento"),
        "valor_estimado": valor_total,
        "tempo_processamento_segundos": resultado.get("tempo_processamento_segundos"),
        "status": "gerada",
    }


@router.post("/processar")
async def processar_cotacao(
    body: CotacaoProcessarRequest,
    db: Session = Depends(get_db),
    _user=Depends(_cotacao_roles),
):
    """Processa texto digitado ou transcrição mockada diretamente."""
    return await _salvar_e_retornar_cotacao(body.transcricao_audio, body.vendedor, body.cliente_nome, db)


@router.post("/processar-audio")
async def processar_audio(
    audio: UploadFile = File(...),
    vendedor: str = Form(...),
    cliente_nome: str = Form(None),
    db: Session = Depends(get_db),
    _user=Depends(_cotacao_roles),
):
    """
    Recebe um arquivo de áudio, transcreve usando Groq Whisper (whisper-large-v3) 
    e em seguida gera a BOM via inteligência artificial.
    """
    try:
        from services.groq_client import get_groq_client, DEFAULT_AUDIO_MODEL
        client = get_groq_client()
        
        # Salva o áudio temporariamente
        suffix = os.path.splitext(audio.filename)[1] if audio.filename else ".m4a"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            conteudo = await audio.read()
            tmp.write(conteudo)
            tmp_path = tmp.name

        transcricao = ""
        if client:
            with open(tmp_path, "rb") as f:
                transcription = client.audio.transcriptions.create(
                    file=(audio.filename or "audio.m4a", f.read()),
                    model=DEFAULT_AUDIO_MODEL,
                    response_format="json"
                )
                transcricao = transcription.text
        else:
            transcricao = "[Modo Offline] Áudio recebido, mas a chave GROQ_API_KEY não foi configurada para a transcrição."
            
        # Cleanup temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

        return await _salvar_e_retornar_cotacao(transcricao, vendedor, cliente_nome, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao transcrever áudio: {str(e)}")


@router.post("/{cotacao_id}/aprovar")
def aprovar_cotacao(
    cotacao_id: str,
    db: Session = Depends(get_db),
    _user=Depends(_cotacao_roles),
):
    """Aprova a cotação e cria o projeto de comissionamento e máquina associada."""
    try:
        c_uuid = uuid.UUID(cotacao_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de cotação inválido")
        
    cotacao = db.query(Cotacao).filter(Cotacao.id == c_uuid).first()
    if not cotacao:
        raise HTTPException(status_code=404, detail="Cotação não encontrada")
    
    if cotacao.status == StatusCotacao.aprovada:
        raise HTTPException(status_code=400, detail="Cotação já foi aprovada")
        
    cliente_id = cotacao.cliente_id
    if not cliente_id:
        # Create a dummy client
        novo_cliente = Cliente(
            id=uuid.uuid4(),
            nome=cotacao.cliente_nome if hasattr(cotacao, 'cliente_nome') and cotacao.cliente_nome else "Cliente IA",
            setor="alimentos",
            cidade="indefinida",
            estado="SP"
        )
        db.add(novo_cliente)
        db.flush()
        cliente_id = novo_cliente.id
        
    # Generate unique codes
    proj_id = f"PROJ-{str(uuid.uuid4())[:6].upper()}"
    maq_codigo = f"CLP-{str(uuid.uuid4())[:4].upper()}"
    
    projeto = Projeto(
        id=proj_id,
        nome_contrato=f"Automação {cotacao.vendedor_nome or 'IA'} - {proj_id}",
        id_vendedor="VND-01",
        id_engenheiro="ENG-01",
        valor_contrato=cotacao.valor_estimado,
        status="AGUARDANDO_ENGENHARIA",
    )
    db.add(projeto)
    db.flush()
    
    maquina = Maquina(
        id=uuid.uuid4(),
        id_projeto=proj_id,
        codigo=maq_codigo,
        nome=f"Linha {proj_id}",
        modelo_clp=ModeloCLP.siemens_s7,
        protocolo=ProtocoloCLP.modbus_tcp,
        status="offline",
        cliente_id=cliente_id
    )
    db.add(maquina)
    db.flush()
    
    comiss = Comissionamento(
        id=uuid.uuid4(),
        maquina_id=maquina.id,
        cliente_id=cliente_id,
        status=StatusComissionamento.aguardando_dados,
        fase_projeto=FaseProjeto.awaiting_engineering,
        engenheiro_responsavel="ENG-01",
        valor_contrato=cotacao.valor_estimado,
        checklist_json=cotacao.template_comissionamento,
        bom_json=cotacao.bom_gerada,
        resumo_cotacao={"transcricao": cotacao.audio_transcricao}
    )
    db.add(comiss)
    
    cotacao.status = StatusCotacao.aprovada
    cotacao.data_aprovacao = datetime.utcnow()
    
    db.commit()
    return {"message": "Cotação aprovada e projeto criado", "projeto_id": proj_id}


@router.get("")
def listar_cotacoes(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _user=Depends(_cotacao_roles),
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
