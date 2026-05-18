/**
 * AltaCLP Intelligence — API Service Layer
 * Axios instance with auth interceptors + React Query integration
 */

import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

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
  list: () => api.get("/cotacao"),
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

export default api;
