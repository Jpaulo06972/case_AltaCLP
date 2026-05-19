import sys
import os
import json
import uuid
from datetime import datetime, date
from decimal import Decimal

sys.path.append(os.path.join(os.getcwd(), 'backend'))

from database.connection import SessionLocal, Base, engine
from database.models import (
    Projeto, Maquina, Alerta, LogAuditoriaGit, 
    ProjetoPendencia, Cliente, StatusMaquina,
    TipoAlerta, SeveridadeAlerta, StatusAlerta,
    AcaoAuditoriaGit, ModeloCLP, ProtocoloCLP
)

db = SessionLocal()

def seed_data():
    # 1. Master Contracts
    master_contracts = [
        {
            "id_projeto": "PROJ-001",
            "nome_contrato": "Anaclara Alimentos — Linha de Envase Automatizada",
            "id_vendedor": "VND-01",
            "id_engenheiro": "ENG-01",
            "valor_contrato": 780000.00,
            "status": "EM_ANDAMENTO",
            "prazo": date(2026, 6, 30),
            "dias_atraso": 43,
            "risco": "CRITICO"
        },
        {
            "id_projeto": "PROJ-002",
            "nome_contrato": "Sul Químicos — Automação de Reatores",
            "id_vendedor": "VND-02",
            "id_engenheiro": "ENG-02",
            "valor_contrato": 320000.00,
            "status": "AGUARDANDO_DADOS",
            "prazo": date(2026, 8, 15),
            "dias_atraso": 32,
            "risco": "ALTO"
        },
        {
            "id_projeto": "PROJ-003",
            "nome_contrato": "Pampulha Pharma — Controle de Temperatura Crítica",
            "id_vendedor": "VND-01",
            "id_engenheiro": "ENG-03",
            "valor_contrato": 195000.00,
            "status": "FAT_PENDENTE",
            "prazo": date(2026, 5, 20),
            "dias_atraso": 12,
            "risco": "MEDIO"
        },
        {
            "id_projeto": "PROJ-004",
            "nome_contrato": "Nordeste Têxtil — Sistema de Supervisão SCADA",
            "id_vendedor": "VND-03",
            "id_engenheiro": "ENG-01",
            "valor_contrato": 154500.00,
            "status": "EM_ANDAMENTO",
            "prazo": date(2026, 7, 10),
            "dias_atraso": 17,
            "risco": "MEDIO"
        },
        {
            "id_projeto": "PROJ-005",
            "nome_contrato": "Mecasul Componentes — Retrofit CLP Linha 3",
            "id_vendedor": "VND-02",
            "id_engenheiro": "ENG-02",
            "valor_contrato": 67395.00,
            "status": "AGUARDANDO_DADOS",
            "prazo": date(2026, 9, 1),
            "dias_atraso": 17,
            "risco": "BAIXO"
        },
        {
            "id_projeto": "PROJ-006",
            "nome_contrato": "Belmare Cosméticos — Monitoramento de Utilidades",
            "id_vendedor": "VND-03",
            "id_engenheiro": "ENG-03",
            "valor_contrato": 195679.00,
            "status": "AGUARDANDO_DADOS",
            "prazo": date(2026, 6, 5),
            "dias_atraso": 27,
            "risco": "ALTO"
        },
        {
            "id_projeto": "PROJ-007",
            "nome_contrato": "Vinhal Alimentos — Automação de Silos",
            "id_vendedor": "VND-01",
            "id_engenheiro": "ENG-02",
            "valor_contrato": 143773.00,
            "status": "FAT_PENDENTE",
            "prazo": date(2026, 5, 25),
            "dias_atraso": 3,
            "risco": "BAIXO"
        },
        {
            "id_projeto": "PROJ-008",
            "nome_contrato": "Aspáragos Alimentos — Controle de Produção",
            "id_vendedor": "VND-02",
            "id_engenheiro": "ENG-01",
            "valor_contrato": 149924.00,
            "status": "EM_ANDAMENTO",
            "prazo": date(2026, 7, 22),
            "dias_atraso": 12,
            "risco": "MEDIO"
        },
        {
            "id_projeto": "PROJ-009",
            "nome_contrato": "Centro-Oeste Agro — Irrigação Automatizada",
            "id_vendedor": "VND-03",
            "id_engenheiro": "ENG-03",
            "valor_contrato": 79291.00,
            "status": "AGUARDANDO_DADOS",
            "prazo": date(2026, 8, 30),
            "dias_atraso": 24,
            "risco": "MEDIO"
        },
        {
            "id_projeto": "PROJ-010",
            "nome_contrato": "Cubatão Petroquímica — Segurança e Intertravamentos",
            "id_vendedor": "VND-01",
            "id_engenheiro": "ENG-02",
            "valor_contrato": 310000.00,
            "status": "TREINAMENTO",
            "prazo": date(2026, 5, 30),
            "dias_atraso": 31,
            "risco": "CRITICO"
        }
    ]

    for p in master_contracts:
        db.merge(Projeto(
            id=p["id_projeto"],
            nome_contrato=p["nome_contrato"],
            id_vendedor=p["id_vendedor"],
            id_engenheiro=p["id_engenheiro"],
            valor_contrato=p["valor_contrato"],
            status=p["status"],
            prazo=p["prazo"],
            dias_atraso=p["dias_atraso"],
            risco=p["risco"]
        ))
    db.commit()

    # Get a default cliente
    cliente = db.query(Cliente).first()
    if not cliente:
        print("No Cliente found, creating default...")
        cliente = Cliente(id=uuid.uuid4(), nome="Default Cliente", setor="químico", cidade="SP", estado="SP")
        db.add(cliente)
        db.commit()
    cliente_id = cliente.id

    # 2.1 Machines
    machines = [
        {"id": "CLP-001", "proj": "PROJ-001", "model": "siemens_s7", "status": "crítico"},
        {"id": "CLP-002", "proj": "PROJ-001", "model": "siemens_s7", "status": "alerta"},
        {"id": "CLP-003", "proj": "PROJ-003", "model": "weg", "status": "operando"},
        {"id": "CLP-004", "proj": "PROJ-003", "model": "weg", "status": "operando"},
        {"id": "CLP-007", "proj": "PROJ-002", "model": "schneider", "status": "crítico"},
        {"id": "CLP-011", "proj": "PROJ-002", "model": "schneider", "status": "crítico"},
        {"id": "CLP-014", "proj": "PROJ-006", "model": "siemens_s7", "status": "operando"},
        {"id": "CLP-017", "proj": "PROJ-010", "model": "siemens_s7", "status": "em_comissionamento"},
        {"id": "CLP-018", "proj": "PROJ-005", "model": "allen_bradley", "status": "offline"},
        {"id": "CLP-020", "proj": "PROJ-003", "model": "weg", "status": "operando"},
        {"id": "CLP-027", "proj": "PROJ-001", "model": "siemens_s7", "status": "alerta"},
        {"id": "CLP-044", "proj": "PROJ-002", "model": "siemens_s7", "status": "em_comissionamento"},
    ]

    for m in machines:
        existing = db.query(Maquina).filter(Maquina.codigo == m["id"]).first()
        if existing:
            existing.id_projeto = m["proj"]
            existing.status = m["status"]
            existing.modelo_clp = m["model"]
        else:
            db.add(Maquina(
                id=uuid.uuid4(),
                cliente_id=cliente_id,
                codigo=m["id"],
                nome=f"Máquina {m['id']}",
                modelo_clp=m["model"],
                protocolo="modbus_tcp",
                status=m["status"],
                id_projeto=m["proj"]
            ))
    db.commit()

    # 2.2 Alerts
    alertas_data = [
        {"id": "ALR-001", "maq": "CLP-001", "proj": "PROJ-001", "desc": "Temperatura excedendo limite — 91°C", "sev": "crítico", "ia": "Provável falha no sistema de resfriamento. Verificar válvula solenoide VA-03 e fluxo do circuito de água gelada."},
        {"id": "ALR-002", "maq": "CLP-007", "proj": "PROJ-002", "desc": "Vibração anormal no eixo do motor", "sev": "crítico", "ia": "Desbalanceamento mecânico detectado. Verificar acoplamento e rolamentos do motor M-07."},
        {"id": "ALR-003", "maq": "CLP-011", "proj": "PROJ-002", "desc": "Falha de comunicação Modbus TCP", "sev": "emergência", "ia": "Timeout na comunicação. Verificar cabo de rede e configuração de IP do slave."},
        {"id": "ALR-004", "maq": "CLP-002", "proj": "PROJ-001", "desc": "Pressão abaixo do setpoint — 2.1 bar", "sev": "aviso", "ia": "Possível vazamento na linha pneumática entre válvulas V-04 e V-06."},
        {"id": "ALR-005", "maq": "CLP-027", "proj": "PROJ-001", "desc": "Corrente do motor acima do nominal", "sev": "emergência", "ia": "Sobrecarga detectada. Verificar carga mecânica e parâmetros do inversor CFW500."},
        {"id": "ALR-006", "maq": "CLP-044", "proj": "PROJ-002", "desc": "Sensor de nível sem leitura", "sev": "aviso", "ia": "Falso alarme provável — sensor em comissionamento. Confirmar calibração inicial."}
    ]

    for a in alertas_data:
        maq = db.query(Maquina).filter(Maquina.codigo == a["maq"]).first()
        if maq:
            existing_alerta = db.query(Alerta).filter(Alerta.codigo_alerta == a["id"]).first()
            if not existing_alerta:
                db.add(Alerta(
                    id=uuid.uuid4(),
                    maquina_id=maq.id,
                    cliente_id=cliente_id,
                    codigo_alerta=a["id"],
                    tipo="temperatura_alta",  # Dummy type
                    severidade=a["sev"],
                    titulo=a["desc"],
                    id_projeto=a["proj"],
                    texto_analise_ia=a["ia"],
                    status_acao="AGUARDANDO_TECNICO",
                    impacto_financeiro_estimado=250.00
                ))
    db.commit()

    # 2.3 Git Audit
    git_audits = [
        {"proj": "PROJ-001", "repo": "anaclara-envase-clp001", "hash": "a3f9c12", "resumo": "feat: add temperature PID control loop", "user": "ENG-01", "acao": "Commit", "status": "approved"},
        {"proj": "PROJ-001", "repo": "anaclara-envase-clp001", "hash": "PR-4", "resumo": "fix: correct Modbus address mapping for sensor SNS-002", "user": "TEC-01", "acao": "PR", "status": "pending"},
        {"proj": "PROJ-001", "repo": "anaclara-envase-clp001", "hash": "PR-5", "resumo": "refactor: threshold logic for overheat alarm ALR-001", "user": "TEC-01", "acao": "PR", "status": "pending"},
        
        {"proj": "PROJ-002", "repo": "sul-quimicos-clp044", "hash": "b7d2e45", "resumo": "init: project scaffold and IO mapping", "user": "ENG-02", "acao": "Commit", "status": "approved"},
        {"proj": "PROJ-002", "repo": "sul-quimicos-clp044", "hash": "c1a8f33", "resumo": "feat: implement emergency stop interlock routine", "user": "ENG-02", "acao": "Commit", "status": "approved"},
        {"proj": "PROJ-002", "repo": "sul-quimicos-clp044", "hash": "PR-2", "resumo": "fix: vibration threshold adjustment for motor M-07", "user": "TEC-02", "acao": "PR", "status": "pending"},
        
        {"proj": "PROJ-004", "repo": "nordeste-textil-scada", "hash": "d4b6091", "resumo": "feat: SCADA screen layout v1", "user": "ENG-01", "acao": "Commit", "status": "approved"},
        {"proj": "PROJ-004", "repo": "nordeste-textil-scada", "hash": "PR-3", "resumo": "feat: add shift production counter widget", "user": "TEC-03", "acao": "PR", "status": "pending"},

        {"proj": "PROJ-003", "repo": "pampulha-pharma-temp", "hash": "e9c3a77", "resumo": "feat: critical temperature interlock — FDA compliance", "user": "ENG-03", "acao": "Commit", "status": "approved"},
        {"proj": "PROJ-003", "repo": "pampulha-pharma-temp", "hash": "f2d1b88", "resumo": "fix: alarm deadband tuning", "user": "ENG-03", "acao": "Commit", "status": "approved"},
        {"proj": "PROJ-003", "repo": "pampulha-pharma-temp", "hash": "PR-1", "resumo": "docs: add calibration certificates to repo", "user": "TEC-01", "acao": "PR", "status": "approved"},
    ]

    for g in git_audits:
        # Check if exists by diff_resumo just to avoid massive dupes
        existing = db.query(LogAuditoriaGit).filter(LogAuditoriaGit.diff_resumo == g["resumo"]).first()
        if not existing:
            db.add(LogAuditoriaGit(
                id=uuid.uuid4(),
                id_projeto=g["proj"],
                acao=g["acao"],
                id_usuario=g["user"],
                diff_resumo=g["resumo"],
                risco_ia="High" if "flagged risk" in g["resumo"] else "Low"
            ))
    db.commit()

    # Checklist for PROJ-002 (Sul Químicos) as requested
    tasks = [
        {"title": "Validar malha de controle PID", "tecnico": "TEC-02", "done": True},
        {"title": "Calibrar sensor SNS-004", "tecnico": "TEC-01", "done": False},
        {"title": "Ajustar threshold de vibração INV-001", "tecnico": "TEC-02", "done": False},
        {"title": "Comissionar inversor CFW500", "tecnico": "TEC-03", "done": False},
    ]

    existing_tasks = db.query(ProjetoPendencia).filter(ProjetoPendencia.id_projeto == "PROJ-002").count()
    if existing_tasks == 0:
        for t in tasks:
            db.add(ProjetoPendencia(
                id=uuid.uuid4(),
                id_projeto="PROJ-002",
                titulo=t["title"],
                id_tecnico_atribuido=t["tecnico"],
                concluida=t["done"]
            ))
        db.commit()

if __name__ == "__main__":
    seed_data()
    print("Seeding complete.")
