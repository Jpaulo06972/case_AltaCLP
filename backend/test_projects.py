"""Quick test of projects endpoint via SQLAlchemy directly"""
import sys
sys.path.insert(0, '.')
from database.connection import SessionLocal
from database.models import Projeto, ProjetoPendencia

db = SessionLocal()

# Test PROJ-001 lookup (same as the endpoint does)
p = db.query(Projeto).filter(Projeto.id == 'PROJ-001').first()
if p:
    print(f"PROJ-001 found: {p.nome_contrato}")
    total = db.query(ProjetoPendencia).filter(ProjetoPendencia.id_projeto == p.id).count()
    done = db.query(ProjetoPendencia).filter(ProjetoPendencia.id_projeto == p.id, ProjetoPendencia.concluida == True).count()
    print(f"  Tasks: {total} total, {done} done")
    progresso = round((done / total * 100), 1) if total > 0 else 0
    print(f"  Progress: {progresso}%")
else:
    print("PROJ-001 NOT FOUND in DB")

db.close()
