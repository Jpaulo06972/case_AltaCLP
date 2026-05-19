/**
 * AltaCLP Intelligence — Dashboard Engenharia
 * Apple HomeKit-style machine grid + commissioning backlog
 */

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { dashboardApi, engIaApi, overviewApi } from "@/services/api";
import InfoCards from "@/components/InfoCards";
import AIChatWidget from "@/components/AIChatWidget";
import { useAuth } from "@/contexts/AuthContext";
import {
  Cpu,
  AlertTriangle,
  GitCompareArrows,
  Wrench,
  CheckCircle,
  WifiOff,
  Loader2,
  ChevronRight,
  Search,
  Filter,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { useNavigate, Link } from "react-router-dom";

const statusConfig: Record<string, { label: string; color: string; bg: string; icon: any }> = {
  operando: { label: "Operando", color: "text-apple-green", bg: "bg-apple-green/10", icon: CheckCircle },
  alerta: { label: "Alerta", color: "text-apple-orange", bg: "bg-apple-orange/10", icon: AlertTriangle },
  "crítico": { label: "Crítico", color: "text-apple-red", bg: "bg-apple-red/10", icon: AlertTriangle },
  critico: { label: "Crítico", color: "text-apple-red", bg: "bg-apple-red/10", icon: AlertTriangle },
  offline: { label: "Offline", color: "text-apple-tertiary", bg: "bg-apple-surface-2", icon: WifiOff },
  em_comissionamento: { label: "Comissionando", color: "text-apple-blue", bg: "bg-apple-blue/10", icon: Wrench },
};

export default function DashboardEngenharia() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [isFilterExpanded, setIsFilterExpanded] = useState(false);
  const [filterStatus, setFilterStatus] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["dashboard-engenharia"],
    queryFn: () => dashboardApi.getEngenharia().then((r) => r.data),
    refetchInterval: 30000,
  });

  const { data: resumoIa } = useQuery({
    queryKey: ["resumo-mensal-ia"],
    queryFn: () => engIaApi.resumoMensal().then((r) => r.data),
    staleTime: 300000,
  });

  const { data: overviewKpis } = useQuery({
    queryKey: ["overview-kpis"],
    queryFn: () => overviewApi.kpis().then((r) => r.data),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-32">
        <Loader2 className="animate-spin text-apple-blue" size={32} />
      </div>
    );
  }

  const kpis = data?.kpis || {};
  const maquinas = data?.maquinas_status_grid || [];
  const backlog = data?.backlog_priorizado || [];

  const totalMaquinas = maquinas.length;
  const countOperando = maquinas.filter((m: any) => m.status === 'operando').length;
  const countAlerta = maquinas.filter((m: any) => m.status === 'alerta').length;
  const countCritico = maquinas.filter((m: any) => m.status === 'crítico' || m.status === 'critico').length;
  const countOffline = maquinas.filter((m: any) => m.status === 'offline').length;
  const countComissionamento = maquinas.filter((m: any) => m.status === 'em_comissionamento').length;

  const pct = (val: number) => totalMaquinas ? Math.round((val / totalMaquinas) * 100) : 0;

  const filteredMaquinas = maquinas.filter((m: any) => {
    const matchStatus = filterStatus === "all" || m.status === filterStatus || (filterStatus === "crítico" && m.status === "critico");
    const matchSearch = (m.codigo || "").toLowerCase().includes(searchQuery.toLowerCase());
    return matchStatus && matchSearch;
  });

  return (
    <div className="space-y-6 max-w-[1400px]">
      <InfoCards cards={data?.info_cards || []} />

      <AIChatWidget
        title="Resumo Mensal — Custos & Manutenção"
        initialSummary={resumoIa?.resumo}
        className="min-h-[320px]"
        onSend={async (msg) => {
          const r = await engIaApi.ragChat({
            mensagem: msg,
            perfil: user?.perfil || "engenharia",
          });
          return r.data.resposta || r.data.mensagem || JSON.stringify(r.data);
        }}
      />

      {/* ━━ KPI Strip ━━ */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        {[
          { label: "Backlog", value: overviewKpis?.backlog || 26, color: "text-apple-orange" },
          { label: "Com Atraso", value: overviewKpis?.com_atraso || 13, color: "text-apple-red" },
          { label: "Tempo Médio", value: `${overviewKpis?.tempo_medio || 6.2}d`, color: "text-apple-blue" },
          { label: "Alertas Ativos", value: overviewKpis?.alertas_ativos || 43, color: "text-apple-orange" },
          { label: "CLPs c/ Drift", value: overviewKpis?.clps_drift || 3, color: "text-apple-red" },
        ].map((k) => (
          <div key={k.label} className="apple-card px-4 py-3 text-center">
            <p className="text-[11px] font-medium text-apple-tertiary">{k.label}</p>
            <p className={`text-[22px] font-bold tracking-tight ${k.color}`}>{k.value}</p>
          </div>
        ))}
      </div>

      {/* ━━ Summarized Equipment Status Panel ━━ */}
      <div className="apple-card p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-[15px] font-semibold text-apple-label">
            Resumo do Parque de Máquinas
          </h3>
          <Link
            to="/maquinas"
            className="flex items-center gap-1 text-[13px] font-medium text-apple-blue hover:text-apple-blue/80 transition-colors"
          >
            Ver Todas as Máquinas <ChevronRight size={14} />
          </Link>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
          <div className="text-center md:text-left md:border-r border-apple-separator/30 px-2">
            <p className="text-[12px] text-apple-tertiary font-medium mb-1">Total Monitorado</p>
            <p className="text-[24px] font-bold text-apple-label">{totalMaquinas}</p>
          </div>
          <div className="text-center md:text-left md:border-r border-apple-separator/30 px-2">
            <p className="text-[12px] text-apple-tertiary font-medium mb-1 flex items-center gap-1 justify-center md:justify-start">
              <span className="w-2 h-2 rounded-full bg-apple-green"></span> Operando
            </p>
            <p className="text-[20px] font-bold text-apple-green">{countOperando} <span className="text-[12px] font-medium text-apple-tertiary">({pct(countOperando)}%)</span></p>
          </div>
          <div className="text-center md:text-left md:border-r border-apple-separator/30 px-2">
            <p className="text-[12px] text-apple-tertiary font-medium mb-1 flex items-center gap-1 justify-center md:justify-start">
              <span className="w-2 h-2 rounded-full bg-apple-orange"></span> Em Alerta
            </p>
            <p className="text-[20px] font-bold text-apple-orange">{countAlerta} <span className="text-[12px] font-medium text-apple-tertiary">({pct(countAlerta)}%)</span></p>
          </div>
          <div className="text-center md:text-left md:border-r border-apple-separator/30 px-2">
            <p className="text-[12px] text-apple-tertiary font-medium mb-1 flex items-center gap-1 justify-center md:justify-start">
              <span className="w-2 h-2 rounded-full bg-apple-red"></span> Crítico
            </p>
            <p className="text-[20px] font-bold text-apple-red">{countCritico} <span className="text-[12px] font-medium text-apple-tertiary">({pct(countCritico)}%)</span></p>
          </div>
          <div className="text-center md:text-left md:border-r border-apple-separator/30 px-2">
            <p className="text-[12px] text-apple-tertiary font-medium mb-1 flex items-center gap-1 justify-center md:justify-start">
              <span className="w-2 h-2 rounded-full bg-apple-tertiary"></span> Offline
            </p>
            <p className="text-[20px] font-bold text-apple-secondary">{countOffline}</p>
          </div>
          <div className="text-center md:text-left px-2">
            <p className="text-[12px] text-apple-tertiary font-medium mb-1 flex items-center gap-1 justify-center md:justify-start">
              <span className="w-2 h-2 rounded-full bg-apple-blue"></span> Comissionamento
            </p>
            <p className="text-[20px] font-bold text-apple-blue">{countComissionamento}</p>
          </div>
        </div>
      </div>

      {/* ━━ Filtered Equipment Quick-View ━━ */}
      <div className="apple-card overflow-hidden">
        <button
          onClick={() => setIsFilterExpanded(!isFilterExpanded)}
          className="w-full px-6 py-4 flex items-center justify-between bg-apple-surface-0 hover:bg-apple-surface-1/50 transition-colors"
        >
          <div className="flex items-center gap-2">
            <Search size={16} className="text-apple-tertiary" />
            <h3 className="text-[15px] font-semibold text-apple-label">
              Busca Rápida de Equipamento
            </h3>
          </div>
          {isFilterExpanded ? (
            <ChevronUp size={18} className="text-apple-tertiary" />
          ) : (
            <ChevronDown size={18} className="text-apple-tertiary" />
          )}
        </button>
        
        {isFilterExpanded && (
          <div className="p-6 border-t border-apple-separator/30 animate-fade-in">
            <div className="flex flex-col md:flex-row gap-4 mb-6">
              <div className="flex-1 relative">
                <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-apple-tertiary" />
                <input
                  type="text"
                  placeholder="Buscar equipamento por ID (ex: CLP-001)..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-9 pr-4 py-2 text-[13px] bg-apple-surface-1 border border-apple-separator/50 rounded-lg focus:outline-none focus:ring-2 focus:ring-apple-blue/50 text-apple-label"
                />
              </div>
              <div className="relative min-w-[200px]">
                <Filter size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-apple-tertiary" />
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="w-full pl-9 pr-8 py-2 text-[13px] bg-apple-surface-1 border border-apple-separator/50 rounded-lg focus:outline-none focus:ring-2 focus:ring-apple-blue/50 text-apple-label appearance-none cursor-pointer"
                >
                  <option value="all">Todos os Status</option>
                  <option value="operando">Operando</option>
                  <option value="alerta">Em Alerta</option>
                  <option value="crítico">Crítico</option>
                  <option value="offline">Offline</option>
                  <option value="em_comissionamento">Em Comissionamento</option>
                </select>
                <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-apple-tertiary pointer-events-none" />
              </div>
            </div>

            <div className="bg-apple-surface-1/30 rounded-xl border border-apple-separator/30 overflow-hidden">
              {filteredMaquinas.length > 0 ? (
                <div className="divide-y divide-apple-separator/30 max-h-[300px] overflow-y-auto">
                  {filteredMaquinas.map((m: any) => {
                    const status = statusConfig[m.status] || statusConfig.operando;
                    return (
                      <div key={m.id || m.codigo} className="flex items-center justify-between p-3 hover:bg-apple-surface-1 transition-colors">
                        <div className="flex items-center gap-3">
                          <div className={`w-2 h-2 rounded-full ${status.bg.replace('/10', '')}`}></div>
                          <span className="text-[14px] font-semibold text-apple-label">{m.codigo}</span>
                          <span className={`status-badge text-[11px] px-2 py-0.5 ${status.bg} ${status.color}`}>
                            {status.label}
                          </span>
                        </div>
                        <Link
                          to={`/maquinas/${m.id}`}
                          className="apple-btn apple-btn-secondary py-1 px-3 text-[11px]"
                        >
                          Ver Detalhes
                        </Link>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="p-8 text-center text-apple-tertiary text-[13px]">
                  Nenhum equipamento encontrado com estes filtros.
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* ━━ Backlog Table ━━ */}
      <div className="apple-card overflow-hidden">
        <div className="px-6 py-4 border-b border-apple-separator/50">
          <h3 className="text-[15px] font-semibold text-apple-label">
            Backlog de Comissionamento
          </h3>
          <p className="text-[12px] text-apple-tertiary mt-0.5">
            Priorizado por risco contratual
          </p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-[13px]">
            <thead>
              <tr className="border-b border-apple-separator/30">
                {["Máquina", "Cliente", "Status", "Engenheiro", "Atraso", "Risco"].map((h) => (
                  <th
                    key={h}
                    className="px-6 py-3 text-left text-[11px] font-semibold text-apple-tertiary uppercase tracking-wider"
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {backlog.slice(0, 10).map((item: any, i: number) => (
                <tr
                  key={item.id || i}
                  className="border-b border-apple-separator/20 hover:bg-apple-surface-1/50 transition-colors"
                >
                  <td className="px-6 py-3 font-semibold text-apple-label">
                    {item.maquina_codigo || `COM-${i + 1}`}
                  </td>
                  <td className="px-6 py-3 text-apple-secondary">
                    {item.cliente_nome || "—"}
                  </td>
                  <td className="px-6 py-3">
                    <span className="status-badge bg-apple-blue/10 text-apple-blue">
                      {item.status?.replace(/_/g, " ") || "—"}
                    </span>
                  </td>
                  <td className="px-6 py-3 text-apple-secondary">
                    {item.engenheiro_responsavel || "—"}
                  </td>
                  <td className="px-6 py-3">
                    <span
                      className={`font-semibold ${
                        (item.dias_atraso || 0) > 15
                          ? "text-apple-red"
                          : (item.dias_atraso || 0) > 0
                          ? "text-apple-orange"
                          : "text-apple-green"
                      }`}
                    >
                      {item.dias_atraso > 0 ? `${item.dias_atraso}d` : "Em dia"}
                    </span>
                  </td>
                  <td className="px-6 py-3">
                    {item.risco_cancelamento ? (
                      <span className="status-badge bg-apple-red/10 text-apple-red">
                        Alto Risco
                      </span>
                    ) : (
                      <span className="text-apple-tertiary">Normal</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
