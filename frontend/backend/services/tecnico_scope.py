"""
AltaCLP — Isolamento de escopo para perfil Técnico de Campo.
Garante que queries retornem apenas projetos/máquinas atribuídos.
"""

from uuid import UUID
from typing import List, Set, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from database.models import (
    Usuario, PerfilUsuario, ProjetoTecnico, Comissionamento, Maquina, Alerta,
)


def is_tecnico(usuario: Usuario) -> bool:
    perfil = usuario.perfil.value if hasattr(usuario.perfil, "value") else str(usuario.perfil)
    return perfil == PerfilUsuario.tecnico_campo.value


def get_projeto_ids_atribuidos(db: Session, id_tecnico: UUID) -> List[UUID]:
    rows = (
        db.query(ProjetoTecnico.id_projeto)
        .filter(ProjetoTecnico.id_tecnico == id_tecnico, ProjetoTecnico.ativo == True)
        .all()
    )
    return [r[0] for r in rows]


def get_maquina_ids_atribuidas(db: Session, id_tecnico: UUID) -> List[UUID]:
    projeto_ids = get_projeto_ids_atribuidos(db, id_tecnico)
    if not projeto_ids:
        return []
    rows = (
        db.query(Comissionamento.maquina_id)
        .filter(Comissionamento.id.in_(projeto_ids))
        .distinct()
        .all()
    )
    return [r[0] for r in rows if r[0]]


def filtrar_maquinas_query(query, db: Session, usuario: Usuario):
    """Aplica JOIN/filtro obrigatório para técnico."""
    if not is_tecnico(usuario):
        return query
    maquina_ids = get_maquina_ids_atribuidas(db, usuario.id)
    if not maquina_ids:
        return query.filter(Maquina.id == None)  # noqa: E711 — lista vazia
    return query.filter(Maquina.id.in_(maquina_ids))


def filtrar_alertas_query(query, db: Session, usuario: Usuario):
    if not is_tecnico(usuario):
        return query
    maquina_ids = get_maquina_ids_atribuidas(db, usuario.id)
    if not maquina_ids:
        return query.filter(Alerta.id == None)  # noqa: E711
    return query.filter(Alerta.maquina_id.in_(maquina_ids))


def assert_maquina_acesso(db: Session, usuario: Usuario, maquina_id: UUID):
    if not is_tecnico(usuario):
        return
    allowed = get_maquina_ids_atribuidas(db, usuario.id)
    if maquina_id not in allowed:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=403,
            detail={
                "erro": True,
                "codigo": "ESCOPO_NEGADO",
                "mensagem": "Máquina fora dos projetos atribuídos ao técnico",
                "status": 403,
            },
        )


def assert_projeto_acesso(db: Session, usuario: Usuario, projeto_id: UUID):
    if not is_tecnico(usuario):
        return
    allowed = get_projeto_ids_atribuidos(db, usuario.id)
    if projeto_id not in allowed:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=403,
            detail={
                "erro": True,
                "codigo": "ESCOPO_NEGADO",
                "mensagem": "Projeto não atribuído a este técnico",
                "status": 403,
            },
        )
