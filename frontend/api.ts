const API_BASE_URL = "http://localhost:8000/api/v1";

export const api = {
  getDashboardCEO: async () => {
    const res = await fetch(`${API_BASE_URL}/dashboard/ceo`);
    if (!res.ok) throw new Error("Erro ao buscar dados do CEO");
    return res.json();
  },
  getDashboardCFO: async () => {
    const res = await fetch(`${API_BASE_URL}/dashboard/cfo`);
    if (!res.ok) throw new Error("Erro ao buscar dados do CFO");
    return res.json();
  },
  getDashboardEngenharia: async () => {
    const res = await fetch(`${API_BASE_URL}/dashboard/engenharia`);
    if (!res.ok) throw new Error("Erro ao buscar dados da Engenharia");
    return res.json();
  },
  getMaquinas: async () => {
    const res = await fetch(`${API_BASE_URL}/maquinas`);
    if (!res.ok) throw new Error("Erro ao buscar máquinas");
    return res.json();
  },
  getAlertas: async () => {
    const res = await fetch(`${API_BASE_URL}/alertas`);
    if (!res.ok) throw new Error("Erro ao buscar alertas");
    return res.json();
  },
  getGitOpsDriftsAtivos: async () => {
    const res = await fetch(`${API_BASE_URL}/gitops/drifts/ativos`);
    if (!res.ok) throw new Error("Erro ao buscar drifts");
    return res.json();
  },
  getGitOpsEstatisticas: async () => {
    const res = await fetch(`${API_BASE_URL}/gitops/estatisticas`);
    if (!res.ok) throw new Error("Erro ao buscar estatísticas do gitops");
    return res.json();
  },
  getComissionamentos: async () => {
    const res = await fetch(`${API_BASE_URL}/comissionamentos`);
    if (!res.ok) throw new Error("Erro ao buscar comissionamentos");
    return res.json();
  },
  getComissionamentosKanban: async () => {
    const res = await fetch(`${API_BASE_URL}/comissionamentos/kanban`);
    if (!res.ok) throw new Error("Erro ao buscar kanban de comissionamentos");
    return res.json();
  },
  getCotacoes: async () => {
    const res = await fetch(`${API_BASE_URL}/cotacao`);
    if (!res.ok) throw new Error("Erro ao buscar cotações");
    return res.json();
  },
  processarCotacao: async (data: { transcricao_audio: string, vendedor: string, cliente_nome: string }) => {
    const res = await fetch(`${API_BASE_URL}/cotacao/processar`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error("Erro ao processar cotação");
    return res.json();
  }
};
