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
    StatusComissionamento, FaseProjeto,
    ProjetoPendencia, ProjetoHistorico, PerfilUsuario, Projeto
)
from schemas.schemas import AtualizarStatusComissionamentoRequest
from pydantic import BaseModel
import uuid as uuid_mod
from routers.auth import get_usuario_atual
from database.models import Usuario
from services.tecnico_scope import is_tecnico, get_projeto_ids_atribuidos, assert_projeto_acesso

router = APIRouter(prefix="/comissionamentos", tags=["Comissionamento"])


def _filtrar_projetos_acesso(query, db: Session, usuario: Usuario):
    if usuario.perfil == PerfilUsuario.vendedor:
        # Vendedores só veem projetos que eles criaram (id_vendedor armazenado como string UUID)
        return query.join(Projeto, Maquina.id_projeto == Projeto.id).filter(
            Projeto.id_vendedor == str(usuario.id)
        )
    if not is_tecnico(usuario):
        # Engenharia, CEO e CFO veem todos os projetos (nenhum filtro aplicado)
        return query
    
    # Técnicos de campo só veem projetos atribuídos
    ids = get_projeto_ids_atribuidos(db, usuario.id)
    if not ids:
        return query.filter(Comissionamento.id == None)  # noqa: E711
    return query.filter(Comissionamento.id.in_(ids))


def assert_editable_by_vendedor(comiss: Comissionamento, usuario: Usuario):
    if usuario.perfil == PerfilUsuario.vendedor:
        if comiss.fase_projeto not in [FaseProjeto.awaiting_engineering, FaseProjeto.vendor_quote]:
            raise HTTPException(status_code=403, detail="Projeto aceito pela engenharia. Acesso restrito apenas para leitura.")


def _enriquecer_comissionamento(c, maq_codigo, cli_nome, id_projeto=None) -> dict:
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
        "id_projeto": id_projeto,  # PROJ-xxx string from Maquina.id_projeto
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
        "fase_projeto": c.fase_projeto.value if c.fase_projeto else None,
        "especificacoes_tecnicas": c.especificacoes_tecnicas,
        "resumo_cotacao": c.resumo_cotacao,
    }


@router.get("")
def listar_comissionamentos(
    status: str = None,
    cliente_id: UUID = None,
    com_atraso: bool = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    """Lista comissionamentos com filtros e paginação."""
    query = db.query(Comissionamento, Maquina.codigo, Cliente.nome).join(
        Maquina, Comissionamento.maquina_id == Maquina.id
    ).join(
        Cliente, Comissionamento.cliente_id == Cliente.id
    )
    query = _filtrar_projetos_acesso(query, db, usuario)

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
def kanban(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    """Retorna comissionamentos agrupados por status para o kanban."""
    result = {}
    for status_val in [
        StatusComissionamento.aguardando_dados,
        StatusComissionamento.em_andamento,
        StatusComissionamento.fat_pendente,
        StatusComissionamento.treinamento_operador,
    ]:
        q = db.query(Comissionamento, Maquina.codigo, Cliente.nome, Maquina.id_projeto).join(
            Maquina, Comissionamento.maquina_id == Maquina.id
        ).join(
            Cliente, Comissionamento.cliente_id == Cliente.id
        )
        q = _filtrar_projetos_acesso(q, db, usuario)
        itens = q.filter(
            Comissionamento.status == status_val
        ).order_by(
            desc(Comissionamento.risco_cancelamento),
            desc(Comissionamento.dias_atraso)
        ).all()

        result[status_val.value] = [
            _enriquecer_comissionamento(c, maq, cli, id_projeto=id_proj)
            for c, maq, cli, id_proj in itens
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
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual)
):
    """Atualiza status do comissionamento."""
    comiss = db.query(Comissionamento).filter(
        Comissionamento.id == comissionamento_id
    ).first()

    if not comiss:
        raise HTTPException(status_code=404, detail="Comissionamento não encontrado")

    assert_editable_by_vendedor(comiss, usuario)

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


class FaseUpdateRequest(BaseModel):
    fase: str
    usuario: str = "engenharia"


class SpecsUpdateRequest(BaseModel):
    especificacoes: dict
    usuario: str = "engenharia"


class PendenciaToggleRequest(BaseModel):
    pendencia_id: str
    concluida: bool
    usuario: str = "engenharia"


@router.get("/pipeline/funil")
def pipeline_funil(db: Session = Depends(get_db), usuario: Usuario = Depends(get_usuario_atual)):
    """Visão funnel/kanban por fase de projeto."""
    fases = [f.value for f in FaseProjeto]
    resultado = {f: [] for f in fases}
    query = db.query(Comissionamento, Maquina.codigo, Cliente.nome).join(
        Maquina, Comissionamento.maquina_id == Maquina.id
    ).join(Cliente, Comissionamento.cliente_id == Cliente.id)
    query = _filtrar_projetos_acesso(query, db, usuario)
    items = query.all()
    for c, maq, cli in items:
        fase = c.fase_projeto.value if c.fase_projeto else FaseProjeto.awaiting_engineering.value
        if fase not in resultado:
            fase = FaseProjeto.awaiting_engineering.value
        resultado[fase].append(_enriquecer_comissionamento(c, maq, cli))
    return {"fases": fases, "pipeline": resultado}


@router.get("/{comissionamento_id}/detalhe-projeto")
def detalhe_projeto(
    comissionamento_id: UUID,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    assert_projeto_acesso(db, usuario, comissionamento_id)
    result = db.query(Comissionamento, Maquina.codigo, Cliente.nome).join(
        Maquina, Comissionamento.maquina_id == Maquina.id
    ).join(
        Cliente, Comissionamento.cliente_id == Cliente.id
    ).filter(Comissionamento.id == comissionamento_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    c, maq, cli = result
    pendencias = db.query(ProjetoPendencia).filter(
        ProjetoPendencia.comissionamento_id == comissionamento_id
    ).order_by(ProjetoPendencia.ordem).all()
    historico = db.query(ProjetoHistorico).filter(
        ProjetoHistorico.comissionamento_id == comissionamento_id
    ).order_by(desc(ProjetoHistorico.data_hora)).all()
    total = len(pendencias) or 1
    concluidas = sum(1 for p in pendencias if p.concluida)
    return {
        "projeto": _enriquecer_comissionamento(c, maq, cli),
        "resumo_cotacao": c.resumo_cotacao or {"itens": c.bom_json or [], "origem": "vendas"},
        "pendencias": [
            {
                "id": str(p.id),
                "titulo": p.titulo,
                "descricao": p.descricao,
                "ordem": p.ordem,
                "concluida": p.concluida,
                "status_tarefa": p.status_tarefa.value if p.status_tarefa else "pendente",
                "fase": p.fase,
            }
            for p in pendencias
        ],
        "progresso_pct": round(concluidas / total * 100, 1),
        "historico": [
            {
                "acao_realizada": h.acao_realizada,
                "id_usuario": h.id_usuario,
                "data_hora": h.data_hora.isoformat() if h.data_hora else None,
            }
            for h in historico
        ],
    }


@router.put("/{comissionamento_id}/fase")
def atualizar_fase(
    comissionamento_id: UUID,
    body: FaseUpdateRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual)
):
    comiss = db.query(Comissionamento).filter(Comissionamento.id == comissionamento_id).first()
    if not comiss:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    assert_editable_by_vendedor(comiss, usuario)
    
    comiss.fase_projeto = body.fase
    db.add(ProjetoHistorico(
        comissionamento_id=comissionamento_id,
        acao_realizada=f"Transição de fase → {body.fase}",
        id_usuario=body.usuario,
    ))
    db.commit()
    return {"fase": body.fase}


@router.put("/{comissionamento_id}/especificacoes")
def atualizar_especificacoes(
    comissionamento_id: UUID,
    body: SpecsUpdateRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual)
):
    comiss = db.query(Comissionamento).filter(Comissionamento.id == comissionamento_id).first()
    if not comiss:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    assert_editable_by_vendedor(comiss, usuario)
    
    comiss.especificacoes_tecnicas = body.especificacoes
    db.add(ProjetoHistorico(
        comissionamento_id=comissionamento_id,
        acao_realizada="Especificações técnicas atualizadas",
        id_usuario=body.usuario,
    ))
    db.commit()
    return {"mensagem": "Especificações salvas"}


@router.post("/{comissionamento_id}/aprovar-especificacao")
def aprovar_especificacao(comissionamento_id: UUID, db: Session = Depends(get_db), usuario: Usuario = Depends(get_usuario_atual)):
    comiss = db.query(Comissionamento).filter(Comissionamento.id == comissionamento_id).first()
    if not comiss:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    assert_editable_by_vendedor(comiss, usuario)
    
    comiss.fase_projeto = FaseProjeto.in_execution
    db.add(ProjetoHistorico(
        comissionamento_id=comissionamento_id,
        acao_realizada="Especificação aprovada pela engenharia",
        id_usuario="engenharia",
    ))
    db.commit()
    return {"fase": FaseProjeto.in_execution.value}


@router.put("/pendencias/toggle")
def toggle_pendencia(body: PendenciaToggleRequest, db: Session = Depends(get_db)):
    from uuid import UUID as U

    p = db.query(ProjetoPendencia).filter(ProjetoPendencia.id == U(body.pendencia_id)).first()
    if not p:
        raise HTTPException(status_code=404, detail="Pendência não encontrada")
    p.concluida = body.concluida
    if body.concluida:
        p.data_conclusao = datetime.utcnow()
    db.add(ProjetoHistorico(
        comissionamento_id=p.comissionamento_id,
        acao_realizada=f"Pendência '{p.titulo}' {'concluída' if body.concluida else 'reaberta'}",
        id_usuario=body.usuario,
    ))
    db.commit()
    return {"concluida": body.concluida}
