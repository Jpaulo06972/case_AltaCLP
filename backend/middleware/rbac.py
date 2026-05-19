"""
AltaCLP — Role-Based Access Control dependencies for FastAPI routers.
"""

from typing import List, Callable
from fastapi import Depends, HTTPException
from database.models import Usuario, PerfilUsuario
from routers.auth import get_usuario_atual


def require_roles(*roles: str) -> Callable:
    """Dependency factory: permite apenas perfis listados."""

    def checker(usuario: Usuario = Depends(get_usuario_atual)) -> Usuario:
        allowed = {r.value if hasattr(r, "value") else r for r in roles}
        allowed.update({PerfilUsuario.ceo.value, PerfilUsuario.cfo.value})
        perfil = usuario.perfil.value if hasattr(usuario.perfil, "value") else str(usuario.perfil)
        if perfil not in allowed:
            raise HTTPException(
                status_code=403,
                detail={
                    "erro": True,
                    "codigo": "ACESSO_NEGADO",
                    "mensagem": f"Perfil '{perfil}' não autorizado para este recurso",
                    "status": 403,
                },
            )
        return usuario

    return checker


# Atalhos por perfil
require_engenharia = require_roles(PerfilUsuario.engenharia.value, PerfilUsuario.ceo.value)
require_vendas = require_roles(PerfilUsuario.vendedor.value)
require_eng_or_vendas_cotacao = require_roles(
    PerfilUsuario.vendedor.value,
    PerfilUsuario.engenharia.value,
    PerfilUsuario.ceo.value,
)
require_cotacao_only_vendas = require_roles(PerfilUsuario.vendedor.value)
require_tecnico_read = require_roles(
    PerfilUsuario.tecnico_campo.value,
    PerfilUsuario.engenharia.value,
    PerfilUsuario.ceo.value,
    PerfilUsuario.cfo.value,
)
require_equipment_write = require_roles(PerfilUsuario.engenharia.value)
