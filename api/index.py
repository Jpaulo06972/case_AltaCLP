import sys
import os

# Adiciona o diretório 'backend' ao python path para os imports funcionarem
backend_path = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.insert(0, os.path.abspath(backend_path))

# Força variável VERCEL para detecção em runtime
os.environ.setdefault("VERCEL", "1")

from main import app  # noqa: E402 — FastAPI app instance (handler da Vercel)
