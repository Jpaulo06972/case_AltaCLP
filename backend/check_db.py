import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.connection import SessionLocal
from database.models import Cliente, LeituraSensor

db = SessionLocal()
try:
    clientes = db.query(Cliente).count()
    leituras = db.query(LeituraSensor).count()
    print(f"CLIENTES: {clientes}")
    print(f"LEITURAS: {leituras}")
except Exception as e:
    print(f"ERRO: {e}")
finally:
    db.close()
