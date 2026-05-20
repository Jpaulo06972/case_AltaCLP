import sys
import os

# Adiciona o diretório 'backend' (que é ../backend relativo a frontend/api/)
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
sys.path.insert(0, backend_path)

# Força variável VERCEL para detecção em runtime
os.environ.setdefault("VERCEL", "1")

from main import app  # noqa: E402 — FastAPI app instance (handler da Vercel)
