/**
 * AltaCLP Intelligence — API Service Layer
 * Axios instance with auth interceptors + React Query integration
 */

import axios from "axios";

/** Produção Vercel: backend em /_backend (ver vercel.json). Dev: localhost:8000 */
const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  (import.meta.env.PROD ? "/_backend/api/v1" : "http://localhost:8000/api/v1");

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// ━━ Request interceptor: inject Bearer token ━━
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("altaclp_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    try {
      const user = JSON.parse(localStorage.getItem("altaclp_user") || "{}");
      if (user?.id) {
        config.headers["X-Tecnico-Id"] = user.id;
      }
    } catch {
      /* ignore */
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ━━ Response interceptor: handle 401 → redirect to login ━━
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("altaclp_token");
      localStorage.removeItem("altaclp_user");
      // Only redirect if not already on login page
      if (!window.location.pathname.includes("/login")) {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

// ━━ API Methods ━━

// Auth
export const authApi = {
  login: (email: string, senha: string) =>
    api.post("/auth/login", { email, senha }),
  me: () => api.get("/auth/me"),
};

// Dashboard
export const dashboardApi = {
  getCEO: () => api.get("/dashboard/ceo"),
  getCFO: () => api.get("/dashboard/cfo"),
  getEngenharia: () => api.get("/dashboard/engenharia"),
  getCampo: () => api.get("/dashboard/campo"),
};

// Máquinas
export const maquinasApi = {
  list: (params?: Record<string, any>) => api.get("/maquinas", { params }),
  get: (id: string) => api.get(`/maquinas/${id}`),
  getTelemetria: (id: string, params?: { horas?: number; sensor?: string }) =>
    api.get(`/maquinas/${id}/telemetria`, { params }),
  getAlertas: (id: string, params?: { status?: string; limit?: number }) =>
    api.get(`/maquinas/${id}/alertas`, { params }),
  updateThresholds: (id: string, data: Record<string, number>) =>
    api.put(`/maquinas/${id}/thresholds`, data),
  getEstatisticas: () => api.get("/maquinas/estatisticas/resumo"),
};

// Alertas
export const alertasApi = {
  list: (params?: Record<string, any>) => api.get("/alertas", { params }),
  get: (id: string) => api.get(`/alertas/${id}`),
  resolver: (id: string, data: { resolucao: string; foi_falso_alerta: boolean; custo_visita?: number }) =>
    api.post(`/alertas/${id}/resolver`, data),
  getEstatisticas: () => api.get("/alertas/estatisticas"),
  // SSE stream URL (used with EventSource directly)
  streamUrl: `${API_BASE_URL}/alertas/stream`,
};

// GitOps
export const gitopsApi = {
  listAuditorias: (params?: Record<string, any>) => api.get("/gitops/auditorias", { params }),
  getHistorico: (maquinaId: string) => api.get(`/gitops/auditorias/${maquinaId}/historico`),
  getDriftsAtivos: () => api.get("/gitops/drifts/ativos"),
  verificar: (maquinaId: string) => api.post(`/gitops/verificar/${maquinaId}`),
  aprovarPR: (auditoriaId: string, data: { aprovado_por: string; comentario: string }) =>
    api.post(`/gitops/aprovar-pr/${auditoriaId}`, data),
  getEstatisticas: () => api.get("/gitops/estatisticas"),
};

// Comissionamento
export const comissionamentoApi = {
  list: (params?: Record<string, any>) => api.get("/comissionamentos", { params }),
  get: (id: string) => api.get(`/comissionamentos/${id}`),
  updateStatus: (id: string, data: { novo_status: string; observacao: string }) =>
    api.put(`/comissionamentos/${id}/status`, data),
  getKanban: () => api.get("/comissionamentos/kanban"),
  getRiscoAnaclara: () => api.get("/comissionamentos/risco/anaclara"),
};

// Cotação
export const cotacaoApi = {
  processar: (data: { transcricao_audio: string; vendedor: string; cliente_nome: string }) =>
    api.post("/cotacao/processar", data),
  processarAudio: (formData: FormData) =>
    api.post("/cotacao/processar-audio", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  list: () => api.get("/cotacao"),
  aprovar: (id: string) => api.post(`/cotacao/${id}/aprovar`),
};

// Quotations (draft + approve — persistência em cotacoes_draft / projetos)
export const quotationsApi = {
  saveDraft: (data: {
    texto_transcrito?: string;
    json_proposta_ia?: Record<string, unknown>;
    cliente_nome?: string;
    valor_estimado?: number;
    audio_raw_url?: string;
  }) => api.post("/quotations/draft", data),
  approve: (id: string, data?: { prazo?: string }) =>
    api.post(`/quotations/${id}/approve`, data ?? {}),
};

// IA
export const iaApi = {
  analisarPlanta: () => api.post("/ia/analisar-planta"),
  decisao: (data: { pergunta: string; contexto_adicional: string; perfil_usuario: string }) =>
    api.post("/ia/decisao", data),
  gerarRelatorio: (data: { tipo: string }) => api.post("/ia/gerar-relatorio", data),
  chat: (data: { mensagem: string; historico: Array<{ role: string; content: string }>; perfil: string }) =>
    api.post("/ia/chat", data),
};

// Engenharia IA
export const engIaApi = {
  resumoMensal: () => api.get("/engenharia/ia/resumo-mensal"),
  ragChat: (data: {
    mensagem: string;
    perfil?: string;
    equipamento_tag?: string;
    maquina_id?: string;
    projeto_id?: string;
  }) => api.post("/engenharia/ia/rag-chat", data),
};

// Equipamentos (árvore + MQTT)
export const equipamentosApi = {
  arvore: (maquinaId: string) => api.get(`/equipamentos/maquina/${maquinaId}/arvore`),
  telemetria: (equipamentoId: string) => api.get(`/equipamentos/${equipamentoId}/telemetria`),
  updateThreshold: (data: {
    parametro: string;
    valor_novo: number;
    origem?: string;
    equipamento_id?: string;
  }) => api.put("/equipamentos/threshold", data),
};

// Alertas IA + agendamento
export const alertasIaApi = {
  analise: (alertaId: string) => api.get(`/alertas/${alertaId}/analise-ia`),
  aprovarSugestao: (alertaId: string, data: { id_tecnico: string; data_agendada: string }) =>
    api.post(`/alertas/${alertaId}/aprovar-sugestao`, data),
  relatorioManual: (alertaId: string, data: { diretiva: string; id_tecnico: string; data_agendada: string }) =>
    api.post(`/alertas/${alertaId}/relatorio-manual`, data),
  agendamento: (alertaId: string) => api.get(`/alertas/${alertaId}/agendamento`),
};

// GitOps estendido
export const gitopsExtApi = {
  projetos: () => api.get("/gitops/projetos"),
  auditoriaLog: (params?: { id_projeto?: string }) => api.get("/gitops/auditoria-log", { params }),
  reviewIa: (auditoriaId: string) => api.get(`/gitops/review-ia/${auditoriaId}`),
  rejeitarPR: (auditoriaId: string, data: { motivo: string; rejeitado_por: string }) =>
    api.post(`/gitops/rejeitar-pr/${auditoriaId}`, data),
};

// Comissionamento estendido
export const projetoApi = {
  pipeline: () => api.get("/comissionamentos/pipeline/funil"),
  detalhe: (id: string) => api.get(`/comissionamentos/${id}/detalhe-projeto`),
  atualizarFase: (id: string, data: { fase: string; usuario?: string }) =>
    api.put(`/comissionamentos/${id}/fase`, data),
  atualizarSpecs: (id: string, data: { especificacoes: Record<string, unknown>; usuario?: string }) =>
    api.put(`/comissionamentos/${id}/especificacoes`, data),
  aprovarEspecificacao: (id: string) => api.post(`/comissionamentos/${id}/aprovar-especificacao`),
  togglePendencia: (data: { pendencia_id: string; concluida: boolean; usuario?: string }) =>
    api.put("/comissionamentos/pendencias/toggle", data),
};

// Biblioteca de equipamentos
export const equipmentLibraryApi = {
  list: (params?: { busca?: string; categoria?: string; page?: number }) =>
    api.get("/equipment-library", { params }),
  create: (data: { nome_equipamento: string; fabricante: string; categoria: string; url_manual: string }) =>
    api.post("/equipment-library", data),
  update: (id: string, data: Record<string, string>) => api.put(`/equipment-library/${id}`, data),
  delete: (id: string) => api.delete(`/equipment-library/${id}`),
};

// Técnico de campo (escopo isolado)
export const tecnicoApi = {
  atribuicoes: () => api.get("/tecnico/atribuicoes"),
  chatInstalacao: (data: {
    mensagem: string;
    maquina_id?: string;
    equipamento_tag?: string;
    modo?: "instalacao" | "calibracao";
  }) => api.post("/tecnico/ia/chat-instalacao", data),
  analiseAlerta: (alertaId: string) => api.get(`/tecnico/alertas/${alertaId}/analise`),
  registrarIntervencao: (
    alertaId: string,
    data: { tipo_acao: string; comentario_tecnico: string }
  ) => api.post(`/tecnico/alertas/${alertaId}/intervencao`, data),
  atualizarStatusTarefa: (pendenciaId: string, status_tarefa: string) =>
    api.patch(`/tecnico/pendencias/${pendenciaId}/status`, { status_tarefa }),
  uploadDocumento: (projetoId: string, formData: FormData) =>
    api.post(`/tecnico/projetos/${projetoId}/documentos`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  submeterValidacao: (projetoId: string) =>
    api.post(`/tecnico/projetos/${projetoId}/submeter-validacao`),
  calibrarEquipamento: (
    equipamentoId: string,
    params: { parametro: string; valor_novo: number }
  ) => api.put(`/tecnico/equipamentos/${equipamentoId}/calibrar`, null, { params }),
  notificacoesWsUrl: () => {
    const token = localStorage.getItem("altaclp_token");
    const base = (import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1").replace(/^http/, "ws");
    return `${base}/tecnico/notificacoes/ws?token=${token}`;
  },
};

// Projects (Commissioning Relational)
export const projectsApi = {
  list: (params?: { status?: string; id_engenheiro?: string; page?: number; limit?: number }) => 
    api.get("/projects", { params }),
  get: (id: string) => api.get(`/projects/${id}`),
  machines: (id: string) => api.get(`/projects/${id}/machines`),
  alerts: (id: string) => api.get(`/projects/${id}/alerts`),
  gitPrs: (id: string) => api.get(`/projects/${id}/git-prs`),
  tasks: (id: string) => api.get(`/projects/${id}/tasks`),
  updateTask: (id: string, taskId: string, payload: { concluida?: boolean; status_tarefa?: string }) => 
    api.patch(`/projects/${id}/tasks/${taskId}`, payload),
  documents: (id: string) => api.get(`/projects/${id}/documents`),
  uploadDocument: (id: string, formData: FormData) => 
    api.post(`/projects/${id}/documents`, formData, { headers: { "Content-Type": "multipart/form-data" } }),
  submitValidation: (id: string) => api.post(`/projects/${id}/submit-validation`),
  downloadScopeDocument: (id: string) => 
    api.get(`/projects/${id}/scope-document/download`, { responseType: "blob" }),
};

export const overviewApi = {
  kpis: () => api.get("/overview/kpis"),
};

// App State (global context hydration)
export const appStateApi = {
  snapshot: () => api.get("/app-state"),
  assignTechnician: (projectId: string, id_tecnico: string) =>
    api.post(`/app-state/projects/${projectId}/assign-technician`, { id_tecnico }),
};

export default api;
