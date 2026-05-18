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


# ============================================
# MODELOS ORM
# ============================================

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

    # Relacionamentos
    cliente = relationship("Cliente", back_populates="maquinas")
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

    # Relacionamentos
    maquina = relationship("Maquina", back_populates="alertas")
    cliente = relationship("Cliente", back_populates="alertas")

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

    # Relacionamentos
    maquina = relationship("Maquina", back_populates="auditorias_gitops")

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

    # Relacionamentos
    maquina = relationship("Maquina", back_populates="comissionamentos")
    cliente = relationship("Cliente", back_populates="comissionamentos")

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

    # Relacionamentos
    cliente = relationship("Cliente", back_populates="cotacoes")

    def __repr__(self):
        return f"<Cotacao {self.vendedor_nome} - {self.status.value}>"


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
