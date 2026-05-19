"""
AltaCLP Intelligence Platform — Pydantic Schemas
Request/Response models para validação de dados na API.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Any
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID
import enum


# ============================================
# ENUMS para schemas (espelham os do ORM)
# ============================================

class SetorClienteEnum(str, enum.Enum):
    alimentos = "alimentos"
    cosmeticos = "cosméticos"
    farmaceutico = "farmacêutico"
    quimico = "químico"
    automotivo = "automotivo"
    textil = "têxtil"


class RiscoCancelamentoEnum(str, enum.Enum):
    baixo = "baixo"
    medio = "médio"
    alto = "alto"
    critico = "crítico"


class StatusMaquinaEnum(str, enum.Enum):
    operando = "operando"
    alerta = "alerta"
    critico = "crítico"
    offline = "offline"
    em_comissionamento = "em_comissionamento"


class StatusAlertaEnum(str, enum.Enum):
    aberto = "aberto"
    em_investigacao = "em_investigação"
    resolvido = "resolvido"
    falso_alerta = "falso_alerta"


class SeveridadeAlertaEnum(str, enum.Enum):
    info = "info"
    aviso = "aviso"
    critico = "crítico"
    emergencia = "emergência"


class StatusComissionamentoEnum(str, enum.Enum):
    aguardando_dados = "aguardando_dados"
    em_andamento = "em_andamento"
    fat_pendente = "fat_pendente"
    treinamento_operador = "treinamento_operador"
    concluido = "concluído"
    cancelado = "cancelado"


class PerfilUsuarioEnum(str, enum.Enum):
    ceo = "ceo"
    cfo = "cfo"
    engenharia = "engenharia"
    tecnico_campo = "tecnico_campo"
    vendedor = "vendedor"


# ============================================
# AUTH SCHEMAS
# ============================================

class LoginRequest(BaseModel):
    email: str
    senha: str


class LoginResponse(BaseModel):
    access_token: str
    perfil: str
    nome: str
    user_id: Optional[str] = None
    expires_in: int = 28800  # 8 horas em segundos


class UsuarioResponse(BaseModel):
    id: UUID
    nome: str
    email: str
    perfil: str
    ativo: bool
    ultimo_acesso: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================
# CLIENTE SCHEMAS
# ============================================

class ClienteResponse(BaseModel):
    id: UUID
    nome: str
    setor: str
    cidade: str
    estado: str
    cnpj: Optional[str] = None
    contato_nome: Optional[str] = None
    contato_email: Optional[str] = None
    contato_telefone: Optional[str] = None
    nps_score: Optional[int] = None
    valor_contrato: Optional[float] = None
    risco_cancelamento: Optional[str] = None
    data_criacao: Optional[datetime] = None
    ativo: bool = True

    class Config:
        from_attributes = True


# ============================================
# MÁQUINA SCHEMAS
# ============================================

class MaquinaResponse(BaseModel):
    id: UUID
    cliente_id: UUID
    codigo: str
    nome: str
    modelo_clp: str
    protocolo: str
    setor_planta: Optional[str] = None
    status: str
    taxa_falso_alerta: Optional[float] = None
    codigo_hash_campo: Optional[str] = None
    codigo_hash_git: Optional[str] = None
    codigo_sync: Optional[bool] = None
    ultima_verificacao_gitops: Optional[datetime] = None
    ultima_leitura: Optional[datetime] = None
    data_instalacao: Optional[date] = None
    responsavel_tecnico: Optional[str] = None
    dias_sem_incidente: Optional[int] = None
    threshold_temperatura_max: Optional[float] = None
    threshold_pressao_max: Optional[float] = None
    threshold_vibracao_max: Optional[float] = None
    threshold_corrente_max: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    observacoes: Optional[str] = None
    cliente_nome: Optional[str] = None  # Preenchido via join

    class Config:
        from_attributes = True


class MaquinaDetalheResponse(BaseModel):
    maquina: MaquinaResponse
    cliente: Optional[ClienteResponse] = None
    telemetria_24h: List[Any] = []
    alertas_recentes: List[Any] = []


class ThresholdUpdateRequest(BaseModel):
    temperatura_max: Optional[float] = None
    pressao_max: Optional[float] = None
    vibracao_max: Optional[float] = None
    corrente_max: Optional[float] = None


class ThresholdUpdateResponse(BaseModel):
    maquina_id: UUID
    thresholds_anteriores: dict
    thresholds_novos: dict
    reducao_estimada_falsos: float


class EstatisticasMaquinaResponse(BaseModel):
    total: int
    por_status: dict
    taxa_media_falso_alerta: float
    top_10_piores: List[dict]


# ============================================
# TELEMETRIA SCHEMAS
# ============================================

class LeituraSensorResponse(BaseModel):
    id: int
    maquina_id: UUID
    timestamp: datetime
    temperatura: Optional[float] = None
    pressao: Optional[float] = None
    vibracao: Optional[float] = None
    corrente: Optional[float] = None
    tensao: Optional[float] = None
    rpm: Optional[float] = None
    status_operacao: Optional[str] = None
    turno: Optional[str] = None
    temperatura_ambiente: Optional[float] = None
    is_anomalia_detectada: bool = False
    anomalia_score: Optional[float] = None
    fonte: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================
# ALERTA SCHEMAS
# ============================================

class AlertaResponse(BaseModel):
    id: UUID
    maquina_id: UUID
    cliente_id: UUID
    codigo_alerta: str
    tipo: str
    severidade: str
    titulo: str
    descricao: Optional[str] = None
    valor_sensor: Optional[float] = None
    threshold_configurado: Optional[float] = None
    timestamp_criacao: Optional[datetime] = None
    timestamp_resolucao: Optional[datetime] = None
    status: str
    foi_visita_gerada: bool = False
    custo_visita: Optional[float] = None
    tecnico_responsavel: Optional[str] = None
    resolucao_descricao: Optional[str] = None
    is_falso_alerta: Optional[bool] = None
    origem: Optional[str] = None
    maquina_codigo: Optional[str] = None
    cliente_nome: Optional[str] = None

    class Config:
        from_attributes = True


class ResolverAlertaRequest(BaseModel):
    resolucao: str
    foi_falso_alerta: bool = False
    custo_visita: Optional[float] = None


class EstatisticasAlertaResponse(BaseModel):
    total_abertos: int
    criticos: int
    custo_total_visitas_mes: float
    taxa_falso_alerta_geral: float
    por_tipo: dict
    por_cliente: dict


# ============================================
# GITOPS SCHEMAS
# ============================================

class GitOpsAuditoriaResponse(BaseModel):
    id: UUID
    maquina_id: UUID
    timestamp_verificacao: Optional[datetime] = None
    hash_campo: Optional[str] = None
    hash_git: Optional[str] = None
    em_sync: bool = True
    diff_linhas: Optional[int] = None
    diff_resumo: Optional[str] = None
    diff_detalhe: Optional[str] = None
    tecnico_suspeito: Optional[str] = None
    pr_sugerido: bool = False
    pr_url: Optional[str] = None
    acao_tomada: Optional[str] = None
    aprovado_por: Optional[str] = None
    maquina_codigo: Optional[str] = None
    cliente_nome: Optional[str] = None

    class Config:
        from_attributes = True


class AprovarPRRequest(BaseModel):
    aprovado_por: str
    comentario: Optional[str] = None


class GitOpsEstatisticasResponse(BaseModel):
    total_verificacoes_24h: int
    em_sync_pct: float
    drifts_ativos: int
    prejuizo_historico: float


# ============================================
# COMISSIONAMENTO SCHEMAS
# ============================================

class ComissionamentoResponse(BaseModel):
    id: UUID
    maquina_id: UUID
    cliente_id: UUID
    status: str
    engenheiro_responsavel: str
    data_inicio_prevista: Optional[date] = None
    data_inicio_real: Optional[date] = None
    data_conclusao_prevista: Optional[date] = None
    data_conclusao_real: Optional[date] = None
    dias_atraso: int = 0
    valor_contrato: Optional[float] = None
    multa_por_dia_atraso: Optional[float] = None
    multa_acumulada: Optional[float] = None
    risco_cancelamento: bool = False
    prazo_limite_cliente: Optional[date] = None
    observacoes: Optional[str] = None
    checklist_json: Optional[Any] = None
    bom_json: Optional[Any] = None
    maquina_codigo: Optional[str] = None
    cliente_nome: Optional[str] = None

    class Config:
        from_attributes = True


class AtualizarStatusComissionamentoRequest(BaseModel):
    novo_status: str
    observacao: Optional[str] = None


class KanbanResponse(BaseModel):
    aguardando_dados: List[ComissionamentoResponse] = []
    em_andamento: List[ComissionamentoResponse] = []
    fat_pendente: List[ComissionamentoResponse] = []
    treinamento_operador: List[ComissionamentoResponse] = []


# ============================================
# COTAÇÃO SCHEMAS
# ============================================

class CotacaoProcessarRequest(BaseModel):
    transcricao_audio: str
    vendedor: str
    cliente_nome: Optional[str] = None


class CotacaoResponse(BaseModel):
    id: UUID
    cliente_id: Optional[UUID] = None
    vendedor_nome: str
    audio_transcricao: Optional[str] = None
    audio_duracao_segundos: Optional[int] = None
    parametros_extraidos: Optional[Any] = None
    bom_gerada: Optional[Any] = None
    template_comissionamento: Optional[Any] = None
    status: str
    tempo_processamento_segundos: Optional[int] = None
    valor_estimado: Optional[float] = None
    data_criacao: Optional[datetime] = None
    data_aprovacao: Optional[datetime] = None

    class Config:
        from_attributes = True


class CotacaoResultadoResponse(BaseModel):
    cotacao_id: UUID
    parametros_extraidos: dict
    bom: List[dict]
    template_comissionamento: dict
    tempo_processamento_segundos: float


# ============================================
# DASHBOARD SCHEMAS
# ============================================

class KPIValor(BaseModel):
    valor: float
    delta: Optional[float] = None
    tendencia: Optional[str] = None
    meta: Optional[float] = None


class ROIProjeto(BaseModel):
    investimento: float
    retorno_ano1: float
    roi_multiplo: float
    payback_semanas: int


class DashboardCEOResponse(BaseModel):
    kpis: dict
    grafico_custos_6meses: List[dict]
    grafico_falso_alerta_evolucao: List[dict]
    alertas_criticos: List[dict]
    roi_projeto: ROIProjeto


class DashboardCFOResponse(BaseModel):
    kpis_valuation: dict
    roi_por_fase: List[dict]
    riscos_financeiros: List[dict]
    status_due_diligence: str


class DashboardEngenhariaResponse(BaseModel):
    kpis: dict
    maquinas_status_grid: List[dict]
    backlog_priorizado: List[dict]
    alertas_recentes: List[dict]
    qualidade_dados: dict


class DashboardCampoResponse(BaseModel):
    tecnico: str
    ordens_hoje: List[dict]
    alertas_maquinas_responsavel: List[dict]
    clps_drift_alerta: List[dict]


# ============================================
# IA SCHEMAS
# ============================================

class AnalisePlantaResponse(BaseModel):
    resumo_executivo: str
    riscos_criticos: List[dict]
    acoes_recomendadas: List[dict]
    projecao_sem_acao: str
    projecao_com_plano: str


class DecisaoRequest(BaseModel):
    pergunta: str
    contexto_adicional: Optional[str] = None
    perfil_usuario: Optional[str] = "ceo"


class DecisaoResponse(BaseModel):
    resposta: str
    dados_usados: List[str]
    confianca: str


class GerarRelatorioRequest(BaseModel):
    tipo: str = "ceo"


class GerarRelatorioResponse(BaseModel):
    relatorio: str
    secoes: List[str]
    data_geracao: datetime


class ChatRequest(BaseModel):
    mensagem: str
    historico: List[dict] = []
    perfil: str = "ceo"


class ChatResponse(BaseModel):
    resposta: str
    tokens_usados: int = 0


# ============================================
# PAGINAÇÃO E RESPOSTAS GENÉRICAS
# ============================================

class PaginatedResponse(BaseModel):
    dados: List[Any]
    total: int
    pagina: int
    por_pagina: int
    paginas: int


class ErroResponse(BaseModel):
    erro: bool = True
    codigo: str
    mensagem: str
    status: int
