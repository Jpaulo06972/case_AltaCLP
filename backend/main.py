"""
AltaCLP Intelligence Platform — Entry Point (FastAPI)
API principal da plataforma de inteligência operacional.
"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

from database.connection import init_db, SessionLocal
from database.models import Cliente
from services.simulator import TelemetriaSimulator


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: cria tabelas, roda seed se vazio, inicia simulador."""
    print("[API] Iniciando AltaCLP Intelligence Platform...")
    init_db()

    # Seed automático se banco vazio
    db = SessionLocal()
    try:
        if db.query(Cliente).count() == 0:
            print("[API] Banco vazio — executando seed...")
            from database.seed import run_seed
            run_seed()
    except Exception as e:
        print(f"[API] Erro no seed automático: {e}")
    finally:
        db.close()

    # Inicia simulador de telemetria em background
    task = asyncio.create_task(TelemetriaSimulator.loop_simulacao())
    print("[API] [OK] Plataforma pronta!")

    yield

    TelemetriaSimulator.parar()
    task.cancel()
    print("[API] Plataforma encerrada.")


app = FastAPI(
    title="AltaCLP Intelligence API",
    description="Plataforma de Inteligência Operacional — HomoDeus × AltaCLP",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if os.getenv("ENVIRONMENT") == "development" else origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra routers
from routers import auth, dashboard, maquinas, alertas, gitops, comissionamento, cotacao, ia

app.include_router(auth.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(maquinas.router, prefix="/api/v1")
app.include_router(alertas.router, prefix="/api/v1")
app.include_router(gitops.router, prefix="/api/v1")
app.include_router(comissionamento.router, prefix="/api/v1")
app.include_router(cotacao.router, prefix="/api/v1")
app.include_router(ia.router, prefix="/api/v1")


@app.get("/")
def root():
    return {"status": "ok", "versão": "1.0.0", "docs": "/docs",
            "plataforma": "AltaCLP Intelligence Platform"}
