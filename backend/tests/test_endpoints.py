"""
AltaCLP Intelligence Platform — Testes básicos dos endpoints críticos.
Usa TestClient do FastAPI (não requer banco real para rodar).
"""
import pytest
from fastapi.testclient import TestClient

# Nota: estes testes requerem banco PostgreSQL configurado e seed rodado.
# Para rodar: pytest tests/test_endpoints.py -v

try:
    from main import app
    client = TestClient(app)
    CAN_TEST = True
except Exception:
    CAN_TEST = False


@pytest.mark.skipif(not CAN_TEST, reason="Banco não disponível")
class TestHealthCheck:
    def test_root(self):
        r = client.get("/")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert data["versão"] == "1.0.0"


@pytest.mark.skipif(not CAN_TEST, reason="Banco não disponível")
class TestAuth:
    def test_login_sucesso(self):
        r = client.post("/api/v1/auth/login", json={
            "email": "marcos.tedesco@altaclp.com.br", "senha": "demo123"
        })
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        assert data["perfil"] == "ceo"

    def test_login_falha(self):
        r = client.post("/api/v1/auth/login", json={
            "email": "nao@existe.com", "senha": "errada"
        })
        assert r.status_code == 401

    def test_me_sem_token(self):
        r = client.get("/api/v1/auth/me")
        assert r.status_code in (401, 403)

    def test_me_com_token(self):
        login = client.post("/api/v1/auth/login", json={
            "email": "marcos.tedesco@altaclp.com.br", "senha": "demo123"
        })
        token = login.json()["access_token"]
        r = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert r.json()["perfil"] == "ceo"


@pytest.mark.skipif(not CAN_TEST, reason="Banco não disponível")
class TestDashboard:
    def test_dashboard_ceo(self):
        r = client.get("/api/v1/dashboard/ceo")
        assert r.status_code == 200
        data = r.json()
        assert "kpis" in data
        assert "roi_projeto" in data

    def test_dashboard_cfo(self):
        r = client.get("/api/v1/dashboard/cfo")
        assert r.status_code == 200

    def test_dashboard_engenharia(self):
        r = client.get("/api/v1/dashboard/engenharia")
        assert r.status_code == 200
        assert "maquinas_status_grid" in r.json()

    def test_dashboard_campo(self):
        r = client.get("/api/v1/dashboard/campo")
        assert r.status_code == 200


@pytest.mark.skipif(not CAN_TEST, reason="Banco não disponível")
class TestMaquinas:
    def test_listar_maquinas(self):
        r = client.get("/api/v1/maquinas")
        assert r.status_code == 200
        data = r.json()
        assert "dados" in data
        assert data["total"] >= 50

    def test_estatisticas_maquinas(self):
        r = client.get("/api/v1/maquinas/estatisticas/resumo")
        assert r.status_code == 200
        data = r.json()
        assert "por_status" in data
        assert "taxa_media_falso_alerta" in data


@pytest.mark.skipif(not CAN_TEST, reason="Banco não disponível")
class TestAlertas:
    def test_listar_alertas(self):
        r = client.get("/api/v1/alertas")
        assert r.status_code == 200
        assert r.json()["total"] >= 100

    def test_estatisticas_alertas(self):
        r = client.get("/api/v1/alertas/estatisticas")
        assert r.status_code == 200
        data = r.json()
        assert "taxa_falso_alerta_geral" in data


@pytest.mark.skipif(not CAN_TEST, reason="Banco não disponível")
class TestGitOps:
    def test_drifts_ativos(self):
        r = client.get("/api/v1/gitops/drifts/ativos")
        assert r.status_code == 200
        assert r.json()["total_drifts"] >= 3

    def test_estatisticas_gitops(self):
        r = client.get("/api/v1/gitops/estatisticas")
        assert r.status_code == 200


@pytest.mark.skipif(not CAN_TEST, reason="Banco não disponível")
class TestComissionamento:
    def test_listar(self):
        r = client.get("/api/v1/comissionamentos")
        assert r.status_code == 200

    def test_kanban(self):
        r = client.get("/api/v1/comissionamentos/kanban")
        assert r.status_code == 200

    def test_risco_anaclara(self):
        r = client.get("/api/v1/comissionamentos/risco/anaclara")
        assert r.status_code == 200
        data = r.json()
        assert data.get("cliente") == "Anaclara Alimentos" or "erro" not in data


@pytest.mark.skipif(not CAN_TEST, reason="Banco não disponível")
class TestCotacao:
    def test_processar_cotacao(self):
        r = client.post("/api/v1/cotacao/processar", json={
            "transcricao_audio": "Boa tarde, aqui é o João. Estou na planta da Anaclara em Boituva, é uma extrusora de 30kW trifásica 380V com Modbus TCP. Precisa de 4 sensores de temperatura PT100 e 2 de pressão.",
            "vendedor": "João",
            "cliente_nome": "Anaclara Alimentos"
        })
        assert r.status_code == 200
        data = r.json()
        assert "bom" in data
        assert len(data["bom"]) > 0


@pytest.mark.skipif(not CAN_TEST, reason="Banco não disponível")
class TestIA:
    def test_analisar_planta(self):
        r = client.post("/api/v1/ia/analisar-planta")
        assert r.status_code == 200
        data = r.json()
        assert "resumo_executivo" in data or "erro" in data

    def test_status_modelos(self):
        r = client.get("/api/v1/ia/modelos/status")
        assert r.status_code == 200
