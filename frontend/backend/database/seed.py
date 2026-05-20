"""
AltaCLP Intelligence Platform — Seed de Dados Simulados
Gera dados coerentes com a realidade operacional da AltaCLP.
Idempotente: verifica antes de inserir.
"""
import uuid, random, hashlib
import math
from datetime import datetime, timedelta, date
from decimal import Decimal
import bcrypt

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import engine, SessionLocal, Base
from database.models import *

# ============================================
# DADOS FIXOS
# ============================================
CLIENTES_DATA = [
    {"nome":"Anaclara Alimentos","setor":SetorCliente.alimentos,"cidade":"Boituva","estado":"SP","nps":61,"valor":780000,"risco":RiscoCancelamento.critico,"contato":"Gustavo Mendes","email":"gustavo@anaclara.com.br","tel":"(15)99812-3456"},
    {"nome":"Belmare Cosméticos","setor":SetorCliente.cosmeticos,"cidade":"Campinas","estado":"SP","nps":54,"valor":420000,"risco":RiscoCancelamento.alto,"contato":"Fernanda Reis","email":"fernanda@belmare.com.br","tel":"(19)99734-5678"},
    {"nome":"Cubatão Ind. Química","setor":SetorCliente.quimico,"cidade":"Cubatão","estado":"SP","nps":71,"valor":280000,"risco":RiscoCancelamento.medio,"contato":"Ricardo Lima","email":"ricardo@cubataoquim.com.br","tel":"(13)99645-7890"},
    {"nome":"Pampulha Pharma","setor":SetorCliente.farmaceutico,"cidade":"Belo Horizonte","estado":"MG","nps":78,"valor":640000,"risco":RiscoCancelamento.baixo,"contato":"Dra. Mariana Costa","email":"mariana@pampulha.com.br","tel":"(31)99567-8901"},
    {"nome":"Vinhal Alimentos","setor":SetorCliente.alimentos,"cidade":"Ribeirão Preto","estado":"SP","nps":69,"valor":195000,"risco":RiscoCancelamento.medio,"contato":"José Vinhal","email":"jose@vinhal.com.br","tel":"(16)99478-9012"},
    {"nome":"Aspáragos Alimentos","setor":SetorCliente.alimentos,"cidade":"Jundiaí","estado":"SP","nps":63,"valor":145000,"risco":RiscoCancelamento.alto,"contato":"Paulo Santos","email":"paulo@asparagos.com.br","tel":"(11)99389-0123"},
    {"nome":"Mecasul Componentes","setor":SetorCliente.automotivo,"cidade":"Curitiba","estado":"PR","nps":82,"valor":310000,"risco":RiscoCancelamento.baixo,"contato":"Carlos Mecasul","email":"carlos@mecasul.com.br","tel":"(41)99290-1234"},
    {"nome":"Nordeste Têxtil","setor":SetorCliente.textil,"cidade":"Fortaleza","estado":"CE","nps":74,"valor":220000,"risco":RiscoCancelamento.baixo,"contato":"Ana Textile","email":"ana@nordtextil.com.br","tel":"(85)99201-2345"},
    {"nome":"Sul Químicos","setor":SetorCliente.quimico,"cidade":"Porto Alegre","estado":"RS","nps":77,"valor":180000,"risco":RiscoCancelamento.baixo,"contato":"Pedro Sul","email":"pedro@sulquim.com.br","tel":"(51)99112-3456"},
    {"nome":"Centro-Oeste Agro","setor":SetorCliente.alimentos,"cidade":"Goiânia","estado":"GO","nps":80,"valor":160000,"risco":RiscoCancelamento.baixo,"contato":"Maria Agro","email":"maria@coagro.com.br","tel":"(62)99023-4567"},
]

COORDS = {
    "Boituva":(-23.28,-47.67),"Campinas":(-22.90,-47.06),"Cubatão":(-23.89,-46.42),
    "Belo Horizonte":(-19.92,-43.94),"Ribeirão Preto":(-21.17,-47.81),"Jundiaí":(-23.19,-46.88),
    "Curitiba":(-25.43,-49.27),"Fortaleza":(-3.72,-38.52),"Porto Alegre":(-30.03,-51.23),
    "Goiânia":(-16.68,-49.25),
}

NOMES_MAQUINAS = [
    "Extrusora Principal L1","Extrusora Secundária L2","Válvula Proporcional VH-118",
    "Compressor de Ar CA-01","Bomba Dosadora BD-05","Esteira Transportadora ET-03",
    "Misturador Industrial MI-02","Reator Químico RQ-01","Caldeira a Vapor CV-04",
    "Prensa Hidráulica PH-07","Forno Industrial FI-03","Centrífuga CF-02",
    "Torre de Resfriamento TR-01","Secador Rotativo SR-05","Embaladora EM-04",
]

TECNICOS = ["Anderson Vasconcellos","Sebastião Oliveira","Marcos Figueiredo","Rafael Costa",
            "Joelson Pereira","Thiago Santos","Bruno Almeida","Leonardo Matos"]
ENGENHEIROS = ["Cláudia Santarém","Júnior Almeida","Felipe Rodrigues","Carolina Duarte"]

# Distribuição de máquinas por cliente (índice no CLIENTES_DATA, quantidade)
DIST_MAQUINAS = [(0,8),(1,6),(2,5),(3,5),(4,4),(5,4),(6,6),(7,4),(8,4),(9,4)]


def run_seed():
    print("[SEED] Limpando e recriando tabelas (forçado)...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(Cliente).count() > 0:
        print("[SEED] Banco já possui dados. Pulando seed.")
        db.close()
        return

    print("[SEED] Inserindo dados simulados...")

    # === CLIENTES ===
    clientes = []
    for cd in CLIENTES_DATA:
        c = Cliente(id=uuid.uuid4(), nome=cd["nome"], setor=cd["setor"], cidade=cd["cidade"],
                    estado=cd["estado"], cnpj=f"{random.randint(10,99)}.{random.randint(100,999)}.{random.randint(100,999)}/0001-{random.randint(10,99)}",
                    contato_nome=cd["contato"], contato_email=cd["email"], contato_telefone=cd["tel"],
                    nps_score=cd["nps"], valor_contrato=Decimal(str(cd["valor"])),
                    risco_cancelamento=cd["risco"], data_criacao=datetime(2024,1,1), ativo=True)
        db.add(c)
        clientes.append(c)
    db.flush()
    print(f"  [OK] {len(clientes)} clientes")

    # === MÁQUINAS (50 CLPs) ===
    maquinas = []
    status_dist = ([StatusMaquina.operando]*32 + [StatusMaquina.alerta]*8 +
                   [StatusMaquina.critico]*4 + [StatusMaquina.em_comissionamento]*4 + [StatusMaquina.offline]*2)
    random.shuffle(status_dist)

    clp_num = 1
    for cli_idx, qty in DIST_MAQUINAS:
        cliente = clientes[cli_idx]
        coords = COORDS.get(cliente.cidade, (-23.5, -46.6))
        for j in range(qty):
            codigo = f"CLP-{clp_num:03d}"
            status = status_dist[clp_num - 1] if clp_num - 1 < len(status_dist) else StatusMaquina.operando

            # Forçar status específicos
            if codigo in ("CLP-001","CLP-007"):
                status = StatusMaquina.critico
            elif codigo == "CLP-019":
                status = StatusMaquina.alerta

            modelo = random.choice(list(ModeloCLP))
            proto = ProtocoloCLP.opc_ua if cliente.setor == SetorCliente.farmaceutico else random.choice([ProtocoloCLP.modbus_tcp, ProtocoloCLP.opc_ua])

            # Taxa de falso alerta realista
            if cli_idx == 0:  # Anaclara
                taxa = random.uniform(0.72, 0.85)
            elif cli_idx == 1:  # Belmare
                taxa = random.uniform(0.55, 0.68)
            elif cli_idx == 3:  # Pampulha
                taxa = random.uniform(0.45, 0.58)
            else:
                taxa = random.uniform(0.35, 0.65)

            # Drift de código
            drift_clps = {"CLP-007": True, "CLP-019": True, "CLP-034": True}
            in_sync = codigo not in drift_clps

            hash_base = hashlib.sha256(f"{codigo}-base".encode()).hexdigest()[:16]
            hash_campo = hashlib.sha256(f"{codigo}-campo-drift".encode()).hexdigest()[:16] if not in_sync else hash_base

            m = Maquina(
                id=uuid.uuid4(), cliente_id=cliente.id, codigo=codigo,
                nome=random.choice(NOMES_MAQUINAS) + f" ({codigo})",
                modelo_clp=modelo, protocolo=proto,
                setor_planta=f"Linha {j+1} - Produção", status=status,
                taxa_falso_alerta=round(taxa, 3),
                codigo_hash_campo=hash_campo, codigo_hash_git=hash_base,
                codigo_sync=in_sync,
                ultima_verificacao_gitops=datetime.utcnow() - timedelta(hours=random.randint(1,72)),
                ultima_leitura=datetime.utcnow() - timedelta(minutes=random.randint(1,60)),
                data_instalacao=date(2024, random.randint(1,12), random.randint(1,28)),
                responsavel_tecnico=random.choice(TECNICOS),
                dias_sem_incidente=random.randint(5,180),
                threshold_temperatura_max=85.0, threshold_pressao_max=4.5,
                threshold_vibracao_max=3.5, threshold_corrente_max=15.0,
                latitude=coords[0]+random.uniform(-0.05,0.05),
                longitude=coords[1]+random.uniform(-0.05,0.05),
            )
            db.add(m)
            maquinas.append(m)
            clp_num += 1
    db.flush()
    print(f"  [OK] {len(maquinas)} maquinas (CLPs)")

    # === TELEMETRIA (90 dias × 24h × 50 máquinas) ===
    print("  [RUN] Gerando telemetria (isso pode levar 30-60s)...")
    now = datetime.utcnow()
    batch = []
    total_leituras = 0
    leitura_id = 1

    for m in maquinas:
        if m.status == StatusMaquina.offline:
            continue
        is_critical = m.status in (StatusMaquina.critico, StatusMaquina.alerta)
        temp_base = 82.0 if is_critical else 72.0
        press_base = 4.0 if is_critical else 3.2
        vib_base = 3.2 if is_critical else 2.1

        for day_offset in range(90, 0, -1):
            for hour in range(24):
                ts = now - timedelta(days=day_offset, hours=-hour)
                turno = Turno.manha if 6<=hour<14 else (Turno.tarde if 14<=hour<22 else Turno.noite)
                t_off = 2.0 if turno==Turno.manha else (0.0 if turno==Turno.tarde else -3.0)

                temp = random.gauss(temp_base, 3.5) + t_off
                pres = max(0, random.gauss(press_base, 0.4))
                vib = max(0, random.gauss(vib_base, 0.6))
                corr = max(0, random.gauss(8.5, 1.2))

                batch.append(LeituraSensor(
                    id=uuid.uuid4(),
                    maquina_id=m.id, timestamp=ts,
                    temperatura=round(float(temp),2), pressao=round(float(pres),2),
                    vibracao=round(float(vib),2), corrente=round(float(corr),2),
                    tensao=round(float(random.gauss(380,5)),1),
                    rpm=round(float(max(0,random.gauss(1750,30))),0),
                    status_operacao=StatusOperacao.ligada, turno=turno,
                    temperatura_ambiente=round(float(28+5*math.sin((hour-6)/24*2*math.pi)),1),
                    is_anomalia_detectada=False, anomalia_score=None,
                    fonte=FonteLeitura.simulado,
                ))
                total_leituras += 1
                leitura_id += 1

                if len(batch) >= 5000:
                    db.add_all(batch)
                    db.flush()
                    batch = []

    if batch:
        db.add_all(batch)
        db.flush()
    print(f"  [OK] {total_leituras:,} leituras de telemetria")

    # === ALERTAS (500) ===
    alert_batch = []
    tipos_sensor = [TipoAlerta.temperatura_alta, TipoAlerta.pressao_alta, TipoAlerta.vibracao_alta, TipoAlerta.corrente_alta]
    for i in range(500):
        maq = random.choice(maquinas)
        is_falso = i < 320
        dias_atras = random.randint(0, 90)
        ts = now - timedelta(days=dias_atras, hours=random.randint(0,23))
        tipo = random.choice(tipos_sensor) if i < 496 else TipoAlerta.drift_codigo
        sev = random.choice([SeveridadeAlerta.aviso, SeveridadeAlerta.critico]) if not is_falso else SeveridadeAlerta.aviso

        custo = Decimal(str(random.randint(350,550))) if is_falso and random.random()<0.7 else None
        status_a = StatusAlerta.falso_alerta if is_falso else random.choice([StatusAlerta.aberto, StatusAlerta.resolvido])

        alert_batch.append(Alerta(
            id=uuid.uuid4(), maquina_id=maq.id, cliente_id=maq.cliente_id,
            codigo_alerta=f"ALT-2026-{i+1:06d}", tipo=tipo, severidade=sev,
            titulo=f"{tipo.value.replace('_',' ').title()} em {maq.codigo}",
            descricao=f"Alerta {'falso confirmado' if is_falso else 'real'} detectado",
            valor_sensor=round(random.uniform(80,100),2),
            threshold_configurado=85.0,
            timestamp_criacao=ts,
            timestamp_resolucao=ts+timedelta(hours=random.randint(1,48)) if status_a!=StatusAlerta.aberto else None,
            status=status_a, foi_visita_gerada=is_falso and random.random()<0.7,
            custo_visita=custo, tecnico_responsavel=random.choice(TECNICOS),
            is_falso_alerta=is_falso,
            origem=OrigemAlerta.threshold,
        ))
    db.add_all(alert_batch)
    db.flush()
    print(f"  [OK] 500 alertas (320 falsos)")

    # === INCIDENTES (4 documentados) ===
    # Busca máquinas por código
    maq_map = {m.codigo: m for m in maquinas}
    cli_map = {c.nome: c for c in clientes}

    incidentes_data = [
        {"maq":"CLP-019","cli":"Belmare Cosméticos","tipo":TipoIncidente.transbordo,
         "desc":"Tanque transbordou — válvula VH-221 travou em 100%",
         "causa":"Drift código: coeficiente de válvula alterado em campo sem documentar",
         "tec":"Anderson Vasconcellos","prejuizo":140000,"horas":36,
         "data":datetime(2026,3,14,8,30),"hotfix":True,"doc":False},
        {"maq":"CLP-034","cli":"Pampulha Pharma","tipo":TipoIncidente.parada_producao,
         "desc":"Parada de produção por dosagem fora de especificação",
         "causa":"Drift código: parâmetros de dosagem alterados sem aprovação GxP",
         "tec":"Júnior Almeida","prejuizo":70000,"horas":18,
         "data":datetime(2026,1,2,14,0),"hotfix":True,"doc":False},
        {"maq":"CLP-022","cli":"Vinhal Alimentos","tipo":TipoIncidente.falha_equipamento,
         "desc":"Falha de equipamento após falso alerta ignorado",
         "causa":"Threshold incorreto gerou tantos falsos alertas que o real foi ignorado",
         "tec":"Sebastião Oliveira","prejuizo":25000,"horas":8,
         "data":datetime(2025,9,8,6,15),"hotfix":False,"doc":False},
        {"maq":"CLP-007","cli":"Anaclara Alimentos","tipo":TipoIncidente.parada_producao,
         "desc":"Parada linha 3 — setpoint de temperatura alterado em campo",
         "causa":"Drift código: Anderson alterou setpoint de 78.5°C para 82.0°C sem documentar",
         "tec":"Anderson Vasconcellos","prejuizo":15000,"horas":4,
         "data":datetime(2026,4,22,11,0),"hotfix":True,"doc":False},
    ]
    for inc in incidentes_data:
        maq = maq_map.get(inc["maq"])
        cli = cli_map.get(inc["cli"])
        if maq and cli:
            db.add(Incidente(
                id=uuid.uuid4(), maquina_id=maq.id, cliente_id=cli.id,
                tipo=inc["tipo"], descricao=inc["desc"], causa_raiz=inc["causa"],
                tecnico_campo=inc["tec"], prejuizo_estimado=Decimal(str(inc["prejuizo"])),
                horas_parada=inc["horas"], data_ocorrencia=inc["data"],
                data_resolucao=inc["data"]+timedelta(hours=int(inc["horas"])),
                hotfix_aplicado=inc["hotfix"], hotfix_documentado=inc["doc"],
                status=StatusIncidente.fechado,
            ))
    db.flush()
    print("  [OK] 4 incidentes historicos")

    # === GITOPS AUDITORIAS ===
    for codigo in ["CLP-007","CLP-019","CLP-034"]:
        maq = maq_map.get(codigo)
        if not maq: continue
        from services.gitops_agent import DIFFS_SIMULADOS
        drift = DIFFS_SIMULADOS.get(codigo, {})
        db.add(GitOpsAuditoria(
            id=uuid.uuid4(), maquina_id=maq.id,
            timestamp_verificacao=datetime.utcnow()-timedelta(hours=random.randint(1,24)),
            hash_campo=maq.codigo_hash_campo, hash_git=maq.codigo_hash_git,
            em_sync=False, diff_linhas=drift.get("linhas",0),
            diff_resumo=drift.get("resumo",""), diff_detalhe=drift.get("detalhe",""),
            tecnico_suspeito=drift.get("tecnico",""), pr_sugerido=True,
            acao_tomada=AcaoGitOps.alerta_enviado,
        ))
    db.flush()
    print("  [OK] 3 auditorias GitOps (drifts)")

    # === COMISSIONAMENTOS (26) ===
    statuses_com = ([StatusComissionamento.aguardando_dados]*5+[StatusComissionamento.em_andamento]*8+
                    [StatusComissionamento.fat_pendente]*7+[StatusComissionamento.treinamento_operador]*6)
    random.shuffle(statuses_com)

    # 4 da Anaclara primeiro
    anaclara_maqs = [m for m in maquinas if m.cliente_id==clientes[0].id][:4]
    for i, maq in enumerate(anaclara_maqs):
        dias_atraso = random.randint(18, 26)
        db.add(Comissionamento(
            id=uuid.uuid4(), maquina_id=maq.id, cliente_id=clientes[0].id,
            status=statuses_com[i],
            engenheiro_responsavel=random.choice(ENGENHEIROS),
            data_inicio_prevista=date(2026,3,1)+timedelta(days=i*7),
            data_conclusao_prevista=date(2026,4,15)+timedelta(days=i*5),
            dias_atraso=dias_atraso, valor_contrato=Decimal("195000"),
            multa_por_dia_atraso=Decimal("2500"),
            multa_acumulada=Decimal(str(2500*dias_atraso)),
            risco_cancelamento=True,
            prazo_limite_cliente=date(2026,6,30),
            observacoes="CRÍTICO: Prazo Anaclara junho/2026",
            checklist_json={"etapas":["Inspeção","I/O","Comunicação","Calibração","Testes","Treinamento"],"concluidas":random.randint(0,3)},
        ))

    # Restante (22)
    other_maqs = [m for m in maquinas if m.cliente_id!=clientes[0].id]
    random.shuffle(other_maqs)
    for i in range(22):
        maq = other_maqs[i % len(other_maqs)]
        cli = [c for c in clientes if c.id==maq.cliente_id][0]
        dias_atraso = random.randint(0, 15)
        db.add(Comissionamento(
            id=uuid.uuid4(), maquina_id=maq.id, cliente_id=cli.id,
            status=statuses_com[4+i] if 4+i<len(statuses_com) else StatusComissionamento.em_andamento,
            engenheiro_responsavel=random.choice(ENGENHEIROS),
            data_inicio_prevista=date(2026,2,1)+timedelta(days=random.randint(0,60)),
            data_conclusao_prevista=date(2026,4,1)+timedelta(days=random.randint(0,60)),
            dias_atraso=dias_atraso,
            valor_contrato=Decimal(str(random.randint(50000,200000))),
            multa_por_dia_atraso=Decimal(str(random.randint(500,2000))),
            risco_cancelamento=random.random()<0.2,
            checklist_json={"etapas":["Inspeção","I/O","Comunicação","Calibração","Testes","Treinamento"],"concluidas":random.randint(0,6)},
        ))
    db.flush()
    print("  [OK] 26 comissionamentos")

    # === KPIs HISTÓRICOS (180 dias) ===
    meses_kpi = {
        11:(28000,60,18), 12:(29200,61,20), 1:(30100,62,21),
        2:(29800,63,23), 3:(31000,63,24), 4:(31400,64,26),
    }
    kpi_batch = []
    kpi_id = 1
    for day_offset in range(180, 0, -1):
        d = (now - timedelta(days=day_offset)).date()
        mes = d.month
        base = meses_kpi.get(mes, (30000, 62, 22))
        kpi_batch.append(KPIHistorico(
            id=uuid.uuid4(),
            data=d,
            custo_visitas_falsas=Decimal(str(base[0]+random.randint(-1000,1000))),
            taxa_falso_alerta=base[1]+random.uniform(-1,1),
            maquinas_em_alerta=random.randint(6,12),
            maquinas_criticas=random.randint(2,5),
            maquinas_backlog=base[2]+random.randint(-1,1),
            nps_medio=70+random.uniform(-3,3),
            receita_perdida_cotacao=Decimal(str(random.randint(60000,100000))),
            custo_incidentes=Decimal(str(random.randint(5000,30000))),
            maquinas_drift=random.randint(2,4),
        ))
        kpi_id += 1
    db.add_all(kpi_batch)
    db.flush()
    print("  [OK] 180 registros KPI historico")

    # === USUÁRIOS ===
    users = [
        ("Marcos Tedesco","marcos.tedesco@altaclp.com.br",PerfilUsuario.ceo),
        ("Roberto CFO","roberto.cfo@altaclp.com.br",PerfilUsuario.cfo),
        ("Cláudia Santarém","claudia.eng@altaclp.com.br",PerfilUsuario.engenharia),
        ("Anderson Vasconcellos","anderson.campo@altaclp.com.br",PerfilUsuario.tecnico_campo),
        ("João Vendedor","joao.vendas@altaclp.com.br",PerfilUsuario.vendedor),
    ]
    for nome, email, perfil in users:
        db.add(Usuario(
            id=uuid.uuid4(), nome=nome, email=email,
            senha_hash=bcrypt.hashpw(b"demo123", bcrypt.gensalt()).decode("utf-8"),
            perfil=perfil, ativo=True,
        ))
    db.flush()
    print("  [OK] 5 usuarios")

    # === ATRIBUIÇÃO TÉCNICOS ↔ PROJETOS ===
    anderson = db.query(Usuario).filter(Usuario.email == "anderson.campo@altaclp.com.br").first()
    coms_ativos = db.query(Comissionamento).filter(
        Comissionamento.status.in_([
            StatusComissionamento.em_andamento,
            StatusComissionamento.fat_pendente,
            StatusComissionamento.aguardando_dados,
        ])
    ).limit(8).all()
    if anderson:
        for com in coms_ativos:
            db.add(ProjetoTecnico(
                id=uuid.uuid4(),
                id_projeto=com.id,
                id_tecnico=anderson.id,
                ativo=True,
            ))
        db.flush()
        print(f"  [OK] {len(coms_ativos)} atribuicoes projeto_tecnicos (Anderson)")

    # === VISITAS TÉCNICAS + CUSTOS (IA queries) ===
    for i in range(40):
        cli = random.choice(clientes)
        db.add(VisitaTecnica(
            id=uuid.uuid4(),
            cliente_id=cli.id,
            tecnico_nome=random.choice(TECNICOS),
            custo=Decimal(str(random.randint(800, 3500))),
            motivo="Inspeção por alerta",
            foi_falso_alerta=random.random() < 0.6,
            data_visita=now - timedelta(days=random.randint(0, 45)),
        ))
    for i in range(20):
        db.add(CustoOperacional(
            id=uuid.uuid4(),
            cliente_id=random.choice(clientes).id,
            categoria=random.choice(["manutenção", "peças", "deslocamento"]),
            valor=Decimal(str(random.randint(500, 8000))),
            data_referencia=now - timedelta(days=random.randint(0, 30)),
        ))
    db.flush()
    print("  [OK] visitas tecnicas + custos operacionais")

    # === PENDÊNCIAS DE PROJETO (comissionamento Anaclara) ===
    com_anaclara = db.query(Comissionamento).join(Cliente).filter(Cliente.nome.ilike("%anaclara%")).first()
    if com_anaclara:
        etapas = [
            "Aprovar especificação técnica",
            "FAT — teste de fábrica",
            "Instalação I/O",
            "Comunicação Modbus/OPC UA",
            "Treinamento operador",
            "Pós-venda — documentação",
        ]
        for i, titulo in enumerate(etapas):
            db.add(ProjetoPendencia(
                id=uuid.uuid4(),
                comissionamento_id=com_anaclara.id,
                titulo=titulo,
                ordem=i,
                concluida=i < 2,
                status_tarefa=StatusTarefaPendencia.concluida if i < 2 else StatusTarefaPendencia.pendente,
                fase="IN_EXECUTION" if i < 4 else "POST_SALE",
            ))
        com_anaclara.fase_projeto = FaseProjeto.in_execution
        com_anaclara.resumo_cotacao = {"cliente": "Anaclara", "valor": 195000, "itens": 12}
    db.flush()

    db.commit()
    db.close()
    print("\n[SEED] [OK] Seed concluido com sucesso!")


if __name__ == "__main__":
    run_seed()
