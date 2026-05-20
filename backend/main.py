"""
AltaCLP Intelligence Platform — Entry Point (FastAPI)
API principal da plataforma de inteligência operacional.
"""
import asyncio
import os
import traceback
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

load_dotenv()

from database.connection import init_db, SessionLocal
from database.models import Cliente
from services.simulator import TelemetriaSimulator
from middleware.request_log import RouteLogMiddleware
from services.notificacoes_ws import notification_hub


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: cria tabelas, roda seed se vazio, inicia simulador."""
    print("[API] Iniciando AltaCLP Intelligence Platform...")
    _ensure_db_ready()

    # Inicia simulador de telemetria em background
    task = asyncio.create_task(TelemetriaSimulator.loop_simulacao())
    print("[API] [OK] Plataforma pronta!")

    yield

    TelemetriaSimulator.parar()
    task.cancel()
    print("[API] Plataforma encerrada.")


# ── Inicialização sob demanda (essencial para Vercel Serverless) ──────────
# Na Vercel, o lifespan ASGI NÃO é executado. Este flag + middleware
# garantem que o banco é criado e populado no primeiro request (cold start).
_db_initialized = False


def _ensure_db_ready():
    """Cria tabelas e roda seed se banco estiver vazio. Idempotente."""
    global _db_initialized
    if _db_initialized:
        return
    print("[API] _ensure_db_ready: inicializando banco de dados...")
    init_db()

    db = SessionLocal()
    try:
        if db.query(Cliente).count() == 0:
            print("[API] Banco vazio — executando seed...")
            from database.seed import run_seed
            run_seed()
    except Exception as e:
        print(f"[API] Erro no seed automático: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
    _db_initialized = True
    print("[API] _ensure_db_ready: banco pronto!")


app = FastAPI(
    title="AltaCLP Intelligence API",
    description="Plataforma de Inteligência Operacional — HomoDeus × AltaCLP",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — inclui domínio Vercel automaticamente em produção
origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]
vercel_url = os.getenv("VERCEL_URL")
if vercel_url:
    origins.extend([f"https://{vercel_url}", f"https://www.{vercel_url}"])
vercel_project = os.getenv("VERCEL_PROJECT_PRODUCTION_URL")
if vercel_project:
    origins.append(f"https://{vercel_project}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if os.getenv("ENVIRONMENT") == "development" else (origins or ["*"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RouteLogMiddleware)
app.state.notification_hub = notification_hub


# ── Middleware de inicialização (garante DB pronto na Vercel) ──────────────
# Na Vercel Serverless, o lifespan ASGI não é chamado. Este middleware
# garante que init_db() + seed rodem antes de qualquer request.
# Graças ao flag _db_initialized, só executa de verdade uma vez (cold start).
@app.middleware("http")
async def ensure_db_middleware(request: Request, call_next):
    _ensure_db_ready()
    return await call_next(request)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    print(f"[UNHANDLED ERROR] {request.method} {request.url.path}: {exc}")
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={
            "error": str(exc),
            "stack": traceback.format_exc() if os.getenv("ENVIRONMENT") == "development" else None,
        },
    )


# Registra routers
from routers import (
    auth, dashboard, maquinas, alertas, gitops, comissionamento, cotacao, ia,
    engenharia_ia, equipment_library, equipamentos, tecnico,
    projects, overview, app_state, quotations,
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(maquinas.router, prefix="/api/v1")
app.include_router(alertas.router, prefix="/api/v1")
app.include_router(gitops.router, prefix="/api/v1")
app.include_router(comissionamento.router, prefix="/api/v1")
app.include_router(cotacao.router, prefix="/api/v1")
app.include_router(quotations.router, prefix="/api/v1")
app.include_router(ia.router, prefix="/api/v1")
app.include_router(engenharia_ia.router, prefix="/api/v1")
app.include_router(equipment_library.router, prefix="/api/v1")
app.include_router(equipamentos.router, prefix="/api/v1")
app.include_router(tecnico.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(overview.router, prefix="/api/v1")
app.include_router(app_state.router, prefix="/api/v1")

_uploads = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(_uploads, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=_uploads), name="uploads")


@app.get("/")
def root():
    return {"status": "ok", "versão": "1.0.0", "docs": "/docs",
            "plataforma": "AltaCLP Intelligence Platform"}
