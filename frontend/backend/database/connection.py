"""
AltaCLP Intelligence Platform — Conexão com o Banco de Dados
Engine SQLAlchemy + Session Factory para PostgreSQL.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://altaclp:altaclp123@localhost:5432/altaclp_db")

# Fallback automático para SQLite se PostgreSQL não estiver disponível
try:
    if DATABASE_URL.startswith("postgresql"):
        # Cria engine de teste com timeout curto de 2 segundos
        engine = create_engine(
            DATABASE_URL,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 2}
        )
        # Tenta realizar uma conexão teste
        conn = engine.connect()
        conn.close()
        print("[DB] Conectado ao PostgreSQL com sucesso.")
    else:
        raise ValueError("SQLite configurado via variável de ambiente.")
except Exception as e:
    print(f"[DB] PostgreSQL indisponível ou inacessível ({e}).")
    if os.getenv("VERCEL") == "1":
        print("[DB] [FALLBACK] Usando banco de dados local SQLite no /tmp (Vercel Writable)...")
        DATABASE_URL = "sqlite:////tmp/altaclp_db.db"
    else:
        print("[DB] [FALLBACK] Usando banco de dados local SQLite (altaclp_db.db)...")
        DATABASE_URL = "sqlite:///./altaclp_db.db"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False, "timeout": 30},
    )
    # Ativar WAL mode para permitir acesso simultâneo
    from sqlalchemy import event
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=10000")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()



def get_db():
    """
    Dependency injection para FastAPI.
    Garante que a sessão é fechada após cada request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Cria todas as tabelas definidas nos modelos ORM.
    Chamado no startup da aplicação.
    """
    import database.models  # noqa: F401 — registra todos os modelos no metadata

    Base.metadata.create_all(bind=engine)
    print("[DB] Tabelas criadas/verificadas com sucesso.")
