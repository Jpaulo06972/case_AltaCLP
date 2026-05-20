import sys
import os

# Adiciona o diretório 'backend' ao python path para os imports funcionarem
backend_path = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.append(backend_path)

from main import app
