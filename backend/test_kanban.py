from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, '.')

from main import app
from database.connection import SessionLocal
from database.models import Usuario

client = TestClient(app)

# Get a user to authenticate (e.g., Cláudia Santarém or Joelson/Anderson)
db = SessionLocal()
u = db.query(Usuario).filter(Usuario.email == "claudia.eng@altaclp.com.br").first()
db.close()

if u:
    # We can perform a request with authentication headers or bypass auth by calling the route function directly.
    # Let's call the route using the test client!
    # First we need a token. Let's do a login or just mock get_usuario_atual.
    # Actually, we can just call the endpoint with headers. But since we need a real token, let's login first.
    res = client.post("/api/v1/auth/login", json={"email": "claudia.eng@altaclp.com.br", "senha": "demo123"})
    token = res.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    res_kanban = client.get("/api/v1/comissionamentos/kanban", headers=headers)
    print("KANBAN KEYS:")
    data = res_kanban.json()
    print(list(data.keys()))
    
    for k, v in data.items():
        print(f"\nCOLUMN: {k} (Count: {len(v)})")
        for item in v[:3]:
            print(f"  ID: {item.get('id')}, maq_cod: {item.get('maquina_codigo')}, cli: {item.get('cliente_nome')}, proj: {item.get('id_projeto')}, resp: {item.get('engenheiro_responsavel')}")
else:
    print("User claudia.eng@altaclp.com.br not found!")
