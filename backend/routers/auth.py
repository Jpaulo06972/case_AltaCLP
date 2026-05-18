"""
AltaCLP Intelligence Platform — Router de Autenticação
Login JWT + perfis de usuário (CEO, CFO, Engenharia, Campo).
"""

import os
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt, JWTError
import bcrypt as _bcrypt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from database.connection import get_db
from database.models import Usuario
from schemas.schemas import LoginRequest, LoginResponse, UsuarioResponse

router = APIRouter(prefix="/auth", tags=["Autenticação"])

# Configuração JWT
SECRET_KEY = os.getenv("SECRET_KEY", "altaclp-secret-key-dev-mode-2026-homodeus")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 8

security = HTTPBearer()


def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    try:
        return _bcrypt.checkpw(senha_plana.encode("utf-8"), senha_hash.encode("utf-8"))
    except Exception:
        return False


def criar_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_usuario_atual(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Usuario:
    """Dependency injection — extrai e valida o usuário do token JWT."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token expirado ou inválido")

    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    if not usuario.ativo:
        raise HTTPException(status_code=403, detail="Conta desativada")

    return usuario


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """
    Autentica um usuário e retorna um token JWT.
    Contas de demo: marcos.tedesco@altaclp.com.br / demo123
    """
    usuario = db.query(Usuario).filter(Usuario.email == body.email).first()

    if not usuario or not verificar_senha(body.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=401,
            detail={
                "erro": True,
                "codigo": "CREDENCIAIS_INVALIDAS",
                "mensagem": "E-mail ou senha incorretos",
                "status": 401
            }
        )

    if not usuario.ativo:
        raise HTTPException(status_code=403, detail="Conta desativada")

    # Atualiza último acesso
    try:
        usuario.ultimo_acesso = datetime.utcnow()
        db.commit()
    except Exception:
        db.rollback()

    token = criar_token({"sub": usuario.email, "perfil": usuario.perfil.value})

    return LoginResponse(
        access_token=token,
        perfil=usuario.perfil.value,
        nome=usuario.nome,
        expires_in=TOKEN_EXPIRE_HOURS * 3600
    )


@router.get("/me", response_model=UsuarioResponse)
def me(usuario: Usuario = Depends(get_usuario_atual)):
    """Retorna dados do usuário autenticado."""
    return UsuarioResponse(
        id=usuario.id,
        nome=usuario.nome,
        email=usuario.email,
        perfil=usuario.perfil.value,
        ativo=usuario.ativo,
        ultimo_acesso=usuario.ultimo_acesso
    )
