"""
AltaCLP Intelligence Platform — Modelos ORM (SQLAlchemy)
Todas as tabelas do sistema de inteligência operacional.
"""

import uuid
import enum
from datetime import datetime, date
from decimal import Decimal

from sqlalchemy import (
    Column, String, Integer, BigInteger, Float, Boolean, Text,
    DateTime, Date, ForeignKey, Numeric, JSON, Index, Enum as SAEnum,
    func, text, Uuid
)
from sqlalchemy.orm import relationship

from database.connection import Base

# Compatibilidade dialeto-agnóstica (SQLite e PostgreSQL)
class UUID(Uuid):
    def __init__(self, *args, **kwargs):
        kwargs.pop("as_uuid", None)
        super().__init__(*args, **kwargs)


# ============================================
# ENUMS — Tipos enumerados do domínio
# ============================================

class SetorCliente(str, enum.Enum):
    alimentos = "alimentos"
    cosmeticos = "cosméticos"
    farmaceutico = "farmacêutico"
    quimico = "químico"
    automotivo = "automotivo"
    textil = "têxtil"


class RiscoCancelamento(str, enum.Enum):
    baixo = "baixo"
    medio = "médio"
    alto = "alto"
    critico = "crítico"


class ModeloCLP(str, enum.Enum):
    allen_bradley = "allen_bradley"
    siemens_s7 = "siemens_s7"
    schneider = "schneider"
    weg = "weg"
    weintek = "weintek"


class ProtocoloCLP(str, enum.Enum):
    modbus_tcp = "modbus_tcp"
    opc_ua = "opc_ua"
    modbus_rtu = "modbus_rtu"


class StatusMaquina(str, enum.Enum):
    operando = "operando"
    alerta = "alerta"
    critico = "crítico"
    offline = "offline"
    em_comissionamento = "em_comissionamento"


class StatusOperacao(str, enum.Enum):
    ligada = "ligada"
    desligada = "desligada"
    standby = "standby"
    falha = "falha"


class Turno(str, enum.Enum):
    manha = "manhã"
    tarde = "tarde"
    noite = "noite"


class FonteLeitura(str, enum.Enum):
    modbus = "modbus"
    opc_ua = "opc_ua"
    simulado = "simulado"


class TipoAlerta(str, enum.Enum):
    temperatura_alta = "temperatura_alta"
    pressao_alta = "pressao_alta"
    vibracao_alta = "vibracao_alta"
    corrente_alta = "corrente_alta"
    drift_codigo = "drift_codigo"
    anomalia_ml = "anomalia_ml"
    sem_comunicacao = "sem_comunicacao"
    falso_alerta_confirmado = "falso_alerta_confirmado"


class SeveridadeAlerta(str, enum.Enum):
    info = "info"
    aviso = "aviso"
    critico = "crítico"
    emergencia = "emergência"


class StatusAlerta(str, enum.Enum):
    aberto = "aberto"
    em_investigacao = "em_investigação"
    resolvido = "resolvido"
    falso_alerta = "falso_alerta"


class OrigemAlerta(str, enum.Enum):
    threshold = "threshold"
    isolation_forest = "isolation_forest"
    gitops = "gitops"
    manual = "manual"


class TipoIncidente(str, enum.Enum):
    parada_producao = "parada_produção"
    transbordo = "transbordo"
    falha_equipamento = "falha_equipamento"
    drift_codigo = "drift_código"
    multa_contratual = "multa_contratual"
    quase_acidente = "quase_acidente"


class StatusIncidente(str, enum.Enum):
    aberto = "aberto"
    em_investigacao = "em_investigação"
    resolvido = "resolvido"
    fechado = "fechado"


class AcaoGitOps(str, enum.Enum):
    nenhuma = "nenhuma"
    alerta_enviado = "alerta_enviado"
    pr_criado = "pr_criado"
    revertido = "revertido"
    aprovado = "aprovado"


class StatusComissionamento(str, enum.Enum):
    aguardando_dados = "aguardando_dados"
    em_andamento = "em_andamento"
    fat_pendente = "fat_pendente"
    treinamento_operador = "treinamento_operador"
    concluido = "concluído"
    cancelado = "cancelado"


class StatusCotacao(str, enum.Enum):
    pendente = "pendente"
    processando = "processando"
    gerada = "gerada"
    aprovada = "aprovada"
    rejeitada = "rejeitada"


class PerfilUsuario(str, enum.Enum):
    ceo = "ceo"
    cfo = "cfo"
    engenharia = "engenharia"
    tecnico_campo = "tecnico_campo"
    vendedor = "vendedor"


class FaseProjeto(str, enum.Enum):
    awaiting_engineering = "AWAITING_ENGINEERING"
    vendor_quote = "VENDOR_QUOTE"
    in_execution = "IN_EXECUTION"
    post_sale = "POST_SALE"


class TipoEquipamento(str, enum.Enum):
    sensor = "sensor"
    motor = "motor"
    inversor = "inversor"


class AcaoAuditoriaGit(str, enum.Enum):
    pull = "Pull"
    pr = "PR"
    commit = "Commit"
    reject = "Reject"


class CategoriaEquipamento(str, enum.Enum):
    plc = "PLC"
    sensor = "Sensor"
    inversor = "Inverter"
    motor = "Motor"


class TipoAcaoTecnico(str, enum.Enum):
    visita_campo = "visita_campo"
    acesso_remoto = "acesso_remoto"
    falso_alarme = "falso_alarme"


class StatusRevisaoEng(str, enum.Enum):
    pendente = "pendente"
    aprovado = "aprovado"
    rejeitado = "rejeitado"


class StatusTarefaPendencia(str, enum.Enum):
    pendente = "pendente"
    em_revisao = "em_revisao"
    concluida = "concluida"


# ============================================
# MODELOS ORM
# ============================================

class Projeto(Base):
    __tablename__ = "projetos"

    id = Column(String(50), primary_key=True)
    nome_contrato = Column(String(300), nullable=False)
    id_vendedor = Column(String(100), nullable=True)
    id_engenheiro = Column(String(100), nullable=True)
    valor_contrato = Column(Numeric(12, 2), nullable=True)
    status = Column(String(50), nullable=False)
    prazo = Column(Date, nullable=True)
    dias_atraso = Column(Integer, default=0)
    risco = Column(String(50), nullable=True)

    # Relacionamentos
    maquinas = relationship("Maquina", back_populates="projeto", lazy="dynamic")
    alertas = relationship("Alerta", back_populates="projeto", lazy="dynamic")
    auditorias_git = relationship("LogAuditoriaGit", back_populates="projeto", lazy="dynamic")
    pendencias = relationship("ProjetoPendencia", back_populates="projeto_ref", lazy="dynamic")

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(200), nullable=False)
    setor = Column(SAEnum(SetorCliente, name="setor_cliente_enum", create_constraint=False), nullable=False)
    cidade = Column(String(100), nullable=False)
    estado = Column(String(2), nullable=False)
    cnpj = Column(String(18), nullable=True)
    contato_nome = Column(String(200), nullable=True)
    contato_email = Column(String(200), nullable=True)
    contato_telefone = Column(String(20), nullable=True)
    nps_score = Column(Integer, nullable=True)
    valor_contrato = Column(Numeric(12, 2), nullable=True)
    risco_cancelamento = Column(SAEnum(RiscoCancelamento, name="risco_cancelamento_enum", create_constraint=False), nullable=True)
    data_criacao = Column(DateTime, default=datetime.utcnow)
    ativo = Column(Boolean, default=True)

    # Relacionamentos
    maquinas = relationship("Maquina", back_populates="cliente", lazy="dynamic")
    alertas = relationship("Alerta", back_populates="cliente", lazy="dynamic")
    incidentes = relationship("Incidente", back_populates="cliente", lazy="dynamic")
    comissionamentos = relationship("Comissionamento", back_populates="cliente", lazy="dynamic")
    cotacoes = relationship("Cotacao", back_populates="cliente", lazy="dynamic")

    def __repr__(self):
        return f"<Cliente {self.nome} ({self.estado})>"


class Maquina(Base):
    __tablename__ = "maquinas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=False, index=True)
    codigo = Column(String(20), unique=True, nullable=False)
    nome = Column(String(200), nullable=False)
    modelo_clp = Column(SAEnum(ModeloCLP, name="modelo_clp_enum", create_constraint=False), nullable=False)
    protocolo = Column(SAEnum(ProtocoloCLP, name="protocolo_clp_enum", create_constraint=False), nullable=False)
    setor_planta = Column(String(200), nullable=True)
    status = Column(SAEnum(StatusMaquina, name="status_maquina_enum", create_constraint=False), nullable=False, default=StatusMaquina.operando)
    taxa_falso_alerta = Column(Float, nullable=True, default=0.0)

    # GitOps — hashes de código
    codigo_hash_campo = Column(String(64), nullable=True)
    codigo_hash_git = Column(String(64), nullable=True)
    codigo_sync = Column(Boolean, default=True)
    ultima_verificacao_gitops = Column(DateTime, nullable=True)

    ultima_leitura = Column(DateTime, nullable=True)
    data_instalacao = Column(Date, nullable=True)
    responsavel_tecnico = Column(String(200), nullable=True)
    dias_sem_incidente = Column(Integer, default=0)

    # Thresholds por máquina
    threshold_temperatura_max = Column(Float, nullable=True, default=85.0)
    threshold_pressao_max = Column(Float, nullable=True, default=4.5)
    threshold_vibracao_max = Column(Float, nullable=True, default=3.5)
    threshold_corrente_max = Column(Float, nullable=True, default=15.0)

    # Geolocalização
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    observacoes = Column(Text, nullable=True)
    id_projeto = Column(String(50), ForeignKey("projetos.id"), nullable=True)

    # Relacionamentos
    cliente = relationship("Cliente", back_populates="maquinas")
    projeto = relationship("Projeto", back_populates="maquinas")
    leituras = relationship("LeituraSensor", back_populates="maquina", lazy="dynamic")
    alertas = relationship("Alerta", back_populates="maquina", lazy="dynamic")
    incidentes = relationship("Incidente", back_populates="maquina", lazy="dynamic")
    auditorias_gitops = relationship("GitOpsAuditoria", back_populates="maquina", lazy="dynamic")
    comissionamentos = relationship("Comissionamento", back_populates="maquina", lazy="dynamic")

    def __repr__(self):
        return f"<Maquina {self.codigo} - {self.nome}>"


class LeituraSensor(Base):
    __tablename__ = "leituras_sensor"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    maquina_id = Column(UUID(as_uuid=True), ForeignKey("maquinas.id"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    temperatura = Column(Float, nullable=True)
    pressao = Column(Float, nullable=True)
    vibracao = Column(Float, nullable=True)
    corrente = Column(Float, nullable=True)
    tensao = Column(Float, nullable=True)
    rpm = Column(Float, nullable=True)
    status_operacao = Column(SAEnum(StatusOperacao, name="status_operacao_enum", create_constraint=False), nullable=True)
    turno = Column(SAEnum(Turno, name="turno_enum", create_constraint=False), nullable=True)
    temperatura_ambiente = Column(Float, nullable=True)
    is_anomalia_detectada = Column(Boolean, default=False)
    anomalia_score = Column(Float, nullable=True)
    fonte = Column(SAEnum(FonteLeitura, name="fonte_leitura_enum", create_constraint=False), default=FonteLeitura.simulado)

    # Relacionamentos
    maquina = relationship("Maquina", back_populates="leituras")

    # Índice composto para queries de telemetria
    __table_args__ = (
        Index("ix_leituras_maquina_timestamp", "maquina_id", timestamp.desc()),
    )

    def __repr__(self):
        return f"<Leitura {self.maquina_id} @ {self.timestamp}>"


class Alerta(Base):
    __tablename__ = "alertas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    maquina_id = Column(UUID(as_uuid=True), ForeignKey("maquinas.id"), nullable=False, index=True)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=False, index=True)
    codigo_alerta = Column(String(20), nullable=False)
    tipo = Column(SAEnum(TipoAlerta, name="tipo_alerta_enum", create_constraint=False), nullable=False)
    severidade = Column(SAEnum(SeveridadeAlerta, name="severidade_alerta_enum", create_constraint=False), nullable=False)
    titulo = Column(String(300), nullable=False)
    descricao = Column(Text, nullable=True)
    valor_sensor = Column(Float, nullable=True)
    threshold_configurado = Column(Float, nullable=True)
    timestamp_criacao = Column(DateTime, default=datetime.utcnow)
    timestamp_resolucao = Column(DateTime, nullable=True)
    status = Column(SAEnum(StatusAlerta, name="status_alerta_enum", create_constraint=False), default=StatusAlerta.aberto)
    foi_visita_gerada = Column(Boolean, default=False)
    custo_visita = Column(Numeric(10, 2), nullable=True)
    tecnico_responsavel = Column(String(200), nullable=True)
    resolucao_descricao = Column(Text, nullable=True)
    is_falso_alerta = Column(Boolean, nullable=True)
    origem = Column(SAEnum(OrigemAlerta, name="origem_alerta_enum", create_constraint=False), default=OrigemAlerta.threshold)
    id_projeto = Column(String(50), ForeignKey("projetos.id"), nullable=True)
    status_acao = Column(String(50), default="AGUARDANDO_TECNICO")
    texto_analise_ia = Column(Text, nullable=True)
    impacto_financeiro_estimado = Column(Numeric(12, 2), nullable=True)

    # Relacionamentos
    maquina = relationship("Maquina", back_populates="alertas")
    cliente = relationship("Cliente", back_populates="alertas")
    projeto = relationship("Projeto", back_populates="alertas")

    def __repr__(self):
        return f"<Alerta {self.codigo_alerta} - {self.tipo.value}>"


class Incidente(Base):
    __tablename__ = "incidentes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    maquina_id = Column(UUID(as_uuid=True), ForeignKey("maquinas.id"), nullable=False, index=True)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=False, index=True)
    alerta_id = Column(UUID(as_uuid=True), ForeignKey("alertas.id"), nullable=True)
    tipo = Column(SAEnum(TipoIncidente, name="tipo_incidente_enum", create_constraint=False), nullable=False)
    descricao = Column(Text, nullable=True)
    causa_raiz = Column(Text, nullable=True)
    tecnico_campo = Column(String(200), nullable=True)
    prejuizo_estimado = Column(Numeric(12, 2), nullable=True)
    horas_parada = Column(Float, nullable=True)
    data_ocorrencia = Column(DateTime, nullable=False)
    data_resolucao = Column(DateTime, nullable=True)
    hotfix_aplicado = Column(Boolean, default=False)
    hotfix_documentado = Column(Boolean, default=False)
    relatorio_rca = Column(Text, nullable=True)
    status = Column(SAEnum(StatusIncidente, name="status_incidente_enum", create_constraint=False), default=StatusIncidente.aberto)

    # Relacionamentos
    maquina = relationship("Maquina", back_populates="incidentes")
    cliente = relationship("Cliente", back_populates="incidentes")

    def __repr__(self):
        return f"<Incidente {self.tipo.value} - R${self.prejuizo_estimado}>"


class GitOpsAuditoria(Base):
    __tablename__ = "gitops_auditorias"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    maquina_id = Column(UUID(as_uuid=True), ForeignKey("maquinas.id"), nullable=False, index=True)
    timestamp_verificacao = Column(DateTime, default=datetime.utcnow)
    hash_campo = Column(String(64), nullable=True)
    hash_git = Column(String(64), nullable=True)
    em_sync = Column(Boolean, default=True)
    diff_linhas = Column(Integer, nullable=True)
    diff_resumo = Column(Text, nullable=True)
    diff_detalhe = Column(Text, nullable=True)
    tecnico_suspeito = Column(String(200), nullable=True)
    pr_sugerido = Column(Boolean, default=False)
    pr_url = Column(String(500), nullable=True)
    acao_tomada = Column(SAEnum(AcaoGitOps, name="acao_gitops_enum", create_constraint=False), default=AcaoGitOps.nenhuma)
    aprovado_por = Column(String(200), nullable=True)
    id_projeto = Column(String(50), ForeignKey("projetos.id"), nullable=True)

    # Relacionamentos
    maquina = relationship("Maquina", back_populates="auditorias_gitops")
    projeto = relationship("Projeto", backref="gitops_auditorias")

    def __repr__(self):
        return f"<GitOpsAuditoria {self.maquina_id} - sync={self.em_sync}>"


class Comissionamento(Base):
    __tablename__ = "comissionamentos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    maquina_id = Column(UUID(as_uuid=True), ForeignKey("maquinas.id"), nullable=False, index=True)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=False, index=True)
    status = Column(SAEnum(StatusComissionamento, name="status_comissionamento_enum", create_constraint=False), nullable=False)
    engenheiro_responsavel = Column(String(200), nullable=False)
    data_inicio_prevista = Column(Date, nullable=True)
    data_inicio_real = Column(Date, nullable=True)
    data_conclusao_prevista = Column(Date, nullable=True)
    data_conclusao_real = Column(Date, nullable=True)
    dias_atraso = Column(Integer, default=0)
    valor_contrato = Column(Numeric(12, 2), nullable=True)
    multa_por_dia_atraso = Column(Numeric(10, 2), nullable=True)
    multa_acumulada = Column(Numeric(12, 2), default=0)
    risco_cancelamento = Column(Boolean, default=False)
    prazo_limite_cliente = Column(Date, nullable=True)
    observacoes = Column(Text, nullable=True)
    checklist_json = Column(JSON, nullable=True)
    bom_json = Column(JSON, nullable=True)
    template_comissionamento_url = Column(String(500), nullable=True)
    fase_projeto = Column(
        SAEnum(FaseProjeto, name="fase_projeto_enum", create_constraint=False),
        nullable=True,
        default=FaseProjeto.awaiting_engineering,
    )
    especificacoes_tecnicas = Column(JSON, nullable=True)
    resumo_cotacao = Column(JSON, nullable=True)
    documentos_projeto = Column(JSON, nullable=True)
    id_vendedor = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True, index=True)
    escopo_tecnico_detalhado = Column(JSON, nullable=True)

    # Relacionamentos
    maquina = relationship("Maquina", back_populates="comissionamentos")
    cliente = relationship("Cliente", back_populates="comissionamentos")
    pendencias = relationship("ProjetoPendencia", back_populates="comissionamento", lazy="dynamic")
    historico = relationship("ProjetoHistorico", back_populates="comissionamento", lazy="dynamic")

    def __repr__(self):
        return f"<Comissionamento {self.maquina_id} - {self.status.value}>"


class Cotacao(Base):
    __tablename__ = "cotacoes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=True)
    vendedor_nome = Column(String(200), nullable=False)
    audio_transcricao = Column(Text, nullable=True)
    audio_duracao_segundos = Column(Integer, nullable=True)
    parametros_extraidos = Column(JSON, nullable=True)
    bom_gerada = Column(JSON, nullable=True)
    template_comissionamento = Column(JSON, nullable=True)
    status = Column(SAEnum(StatusCotacao, name="status_cotacao_enum", create_constraint=False), default=StatusCotacao.pendente)
    tempo_processamento_segundos = Column(Integer, nullable=True)
    engenheiro_revisor = Column(String(200), nullable=True)
    valor_estimado = Column(Numeric(12, 2), nullable=True)
    data_criacao = Column(DateTime, default=datetime.utcnow)
    data_aprovacao = Column(DateTime, nullable=True)
    id_vendedor = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True, index=True)

    # Relacionamentos
    cliente = relationship("Cliente", back_populates="cotacoes")

    def __repr__(self):
        return f"<Cotacao {self.vendedor_nome} - {self.status.value}>"


class CotacaoDraft(Base):
    __tablename__ = "cotacoes_draft"

    id_cotacao = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_vendedor = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False, index=True)
    audio_raw_url = Column(String(1000), nullable=True)
    texto_transcrito = Column(Text, nullable=True)
    json_proposta_ia = Column(JSON, nullable=True)
    status = Column(String(50), default="draft")


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(200), nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    senha_hash = Column(String(200), nullable=False)
    perfil = Column(SAEnum(PerfilUsuario, name="perfil_usuario_enum", create_constraint=False), nullable=False)
    ativo = Column(Boolean, default=True)
    ultimo_acesso = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Usuario {self.email} - {self.perfil.value}>"


class KPIHistorico(Base):
    __tablename__ = "kpis_historico"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    data = Column(Date, nullable=False, index=True)
    custo_visitas_falsas = Column(Numeric(10, 2), nullable=True)
    taxa_falso_alerta = Column(Float, nullable=True)
    maquinas_em_alerta = Column(Integer, nullable=True)
    maquinas_criticas = Column(Integer, nullable=True)
    maquinas_backlog = Column(Integer, nullable=True)
    nps_medio = Column(Float, nullable=True)
    receita_perdida_cotacao = Column(Numeric(10, 2), nullable=True)
    custo_incidentes = Column(Numeric(12, 2), nullable=True)
    maquinas_drift = Column(Integer, nullable=True)

    def __repr__(self):
        return f"<KPI {self.data}>"


class VisitaTecnica(Base):
    __tablename__ = "visitas_tecnicas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=False, index=True)
    maquina_id = Column(UUID(as_uuid=True), ForeignKey("maquinas.id"), nullable=True, index=True)
    alerta_id = Column(UUID(as_uuid=True), ForeignKey("alertas.id"), nullable=True)
    tecnico_nome = Column(String(200), nullable=False)
    custo = Column(Numeric(10, 2), nullable=False, default=0)
    motivo = Column(Text, nullable=True)
    foi_falso_alerta = Column(Boolean, default=False)
    data_visita = Column(DateTime, nullable=False, index=True)
    data_criacao = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index("ix_visitas_data", "data_visita"),)


class CustoOperacional(Base):
    __tablename__ = "custos_operacionais"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=True, index=True)
    categoria = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=True)
    valor = Column(Numeric(12, 2), nullable=False)
    data_referencia = Column(DateTime, nullable=False, index=True)
    data_criacao = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index("ix_custos_data", "data_referencia"),)


class EquipamentoPlanta(Base):
    __tablename__ = "equipamentos_planta"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    maquina_id = Column(UUID(as_uuid=True), ForeignKey("maquinas.id"), nullable=False, index=True)
    tag = Column(String(50), nullable=False)
    nome = Column(String(200), nullable=False)
    tipo = Column(SAEnum(TipoEquipamento, name="tipo_equipamento_enum", create_constraint=False), nullable=False)
    unidade = Column(String(20), nullable=True)
    valor_atual = Column(Float, nullable=True)
    threshold_min = Column(Float, nullable=True)
    threshold_max = Column(Float, nullable=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("equipamentos_planta.id"), nullable=True)
    ativo = Column(Boolean, default=True)
    ultima_atualizacao = Column(DateTime, default=datetime.utcnow)

    maquina = relationship("Maquina", backref="equipamentos")


class LogThreshold(Base):
    __tablename__ = "log_thresholds"

    id_registro = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_equipamento = Column(UUID(as_uuid=True), ForeignKey("equipamentos_planta.id"), nullable=True)
    maquina_id = Column(UUID(as_uuid=True), ForeignKey("maquinas.id"), nullable=True)
    parametro_alterado = Column(String(100), nullable=False)
    valor_antigo = Column(Float, nullable=True)
    valor_novo = Column(Float, nullable=False)
    id_usuario = Column(String(200), nullable=False)
    origem = Column(String(20), default="manual")
    data_hora = Column(DateTime, default=datetime.utcnow, index=True)


class AnaliseAlarme(Base):
    __tablename__ = "analise_alarmes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alerta_id = Column(UUID(as_uuid=True), ForeignKey("alertas.id"), unique=True, nullable=False, index=True)
    texto_analise = Column(Text, nullable=False)
    sugestao_acao = Column(Text, nullable=True)
    gerado_em = Column(DateTime, default=datetime.utcnow)
    modelo_ia = Column(String(50), default="heuristic")


class AgendamentoManutencao(Base):
    __tablename__ = "agendamentos_manutencao"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alerta_id = Column(UUID(as_uuid=True), ForeignKey("alertas.id"), nullable=False, index=True)
    id_tecnico = Column(String(200), nullable=False)
    id_cliente = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=False)
    data_agendada = Column(DateTime, nullable=False)
    diretiva_manual = Column(Text, nullable=True)
    aprovado_ia = Column(Boolean, default=False)
    notificacao_enviada = Column(Boolean, default=False)
    status = Column(String(30), default="agendado")
    criado_em = Column(DateTime, default=datetime.utcnow)


class LogAuditoriaGit(Base):
    __tablename__ = "log_auditoria_git"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_projeto = Column(String(50), ForeignKey("projetos.id"), nullable=True, index=True)
    acao = Column(SAEnum(AcaoAuditoriaGit, name="acao_auditoria_git_enum", create_constraint=False), nullable=False)
    id_usuario = Column(String(200), nullable=False)
    diff_resumo = Column(Text, nullable=True)
    risco_ia = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    projeto = relationship("Projeto", back_populates="auditorias_git")


class ProjetoTecnico(Base):
    __tablename__ = "projeto_tecnicos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_projeto = Column(UUID(as_uuid=True), ForeignKey("comissionamentos.id"), nullable=False, index=True)
    id_tecnico = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False, index=True)
    data_atribuicao = Column(DateTime, default=datetime.utcnow)
    ativo = Column(Boolean, default=True)

    __table_args__ = (
        Index("ix_projeto_tecnicos_par", "id_projeto", "id_tecnico"),
    )


class ProjetoPendencia(Base):
    __tablename__ = "projeto_pendencias"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    comissionamento_id = Column(UUID(as_uuid=True), ForeignKey("comissionamentos.id"), nullable=True, index=True)
    id_projeto = Column(String(50), ForeignKey("projetos.id"), nullable=True, index=True)
    id_tecnico_atribuido = Column(String(100), nullable=True)
    titulo = Column(String(300), nullable=False)
    descricao = Column(Text, nullable=True)
    ordem = Column(Integer, default=0)
    concluida = Column(Boolean, default=False)
    status_tarefa = Column(
        SAEnum(StatusTarefaPendencia, name="status_tarefa_enum", create_constraint=False),
        default=StatusTarefaPendencia.pendente,
    )
    fase = Column(String(50), nullable=True)
    data_conclusao = Column(DateTime, nullable=True)

    comissionamento = relationship("Comissionamento", back_populates="pendencias")
    projeto_ref = relationship("Projeto", back_populates="pendencias")
    documentos = relationship("DocumentoComissionamento", back_populates="pendencia", lazy="dynamic")
    documentos = relationship("DocumentoComissionamento", back_populates="pendencia", lazy="dynamic")


class ProjetoHistorico(Base):
    __tablename__ = "projeto_historico"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    comissionamento_id = Column(UUID(as_uuid=True), ForeignKey("comissionamentos.id"), nullable=False, index=True)
    acao_realizada = Column(String(500), nullable=False)
    id_usuario = Column(String(200), nullable=False)
    data_hora = Column(DateTime, default=datetime.utcnow, index=True)

    comissionamento = relationship("Comissionamento", back_populates="historico")


class IntervencaoTecnica(Base):
    __tablename__ = "intervencoes_tecnicas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_alarme = Column(UUID(as_uuid=True), ForeignKey("alertas.id"), nullable=False, index=True)
    id_tecnico = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False, index=True)
    tipo_acao = Column(
        SAEnum(TipoAcaoTecnico, name="tipo_acao_tecnico_enum", create_constraint=False),
        nullable=False,
    )
    comentario_tecnico = Column(Text, nullable=False)
    data_hora = Column(DateTime, default=datetime.utcnow, index=True)
    status_revisao_eng = Column(
        SAEnum(StatusRevisaoEng, name="status_revisao_eng_enum", create_constraint=False),
        default=StatusRevisaoEng.pendente,
    )


class DocumentoComissionamento(Base):
    __tablename__ = "documentos_comissionamento"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_projeto = Column(String(50), ForeignKey("projetos.id"), nullable=True, index=True)
    id_pendencia = Column(UUID(as_uuid=True), ForeignKey("projeto_pendencias.id"), nullable=True)
    id_tecnico = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    nome_arquivo = Column(String(300), nullable=False)
    url_documento = Column(String(1000), nullable=False)
    tipo_mime = Column(String(100), nullable=True)
    data_upload = Column(DateTime, default=datetime.utcnow, index=True)

    pendencia = relationship("ProjetoPendencia", back_populates="documentos")


class SubmissaoValidacao(Base):
    __tablename__ = "submissoes_validacao"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_projeto = Column(UUID(as_uuid=True), ForeignKey("comissionamentos.id"), nullable=False, index=True)
    id_tecnico = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    resumo_ia = Column(Text, nullable=True)
    status = Column(String(30), default="aguardando_engenharia")
    data_submissao = Column(DateTime, default=datetime.utcnow)


class PortfolioEquipamento(Base):
    __tablename__ = "portfolio_equipamentos"

    id_equipamento = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome_equipamento = Column(String(300), nullable=False)
    fabricante = Column(String(100), nullable=False)
    categoria = Column(String(50), nullable=False, index=True)
    url_manual = Column(String(1000), nullable=False)
    data_cadastro = Column(DateTime, default=datetime.utcnow)
    cadastrado_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
