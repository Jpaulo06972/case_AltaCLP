import sys
import os

# Caminho em produção na Vercel (onde Root Directory = 'frontend')
backend_prod = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
# Caminho em desenvolvimento local (se rodar fora)
backend_local = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

if os.path.exists(os.path.join(backend_prod, "main.py")):
    sys.path.insert(0, backend_prod)
else:
    sys.path.insert(0, backend_local)

# Força variável VERCEL para detecção em runtime
os.environ.setdefault("VERCEL", "1")

from main import app  # noqa: E402
