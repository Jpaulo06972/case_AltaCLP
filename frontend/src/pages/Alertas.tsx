/**
 * AltaCLP Intelligence — Alertas Page
 * Real-time alerts with SSE streaming + macOS notification toasts
 */

import { useQuery } from "@tanstack/react-query";
import { alertasApi } from "@/services/api";
import { useToast } from "@/components/Toast";
import { useEffect, useState } from "react";
import {
  Bell,
  AlertTriangle,
  CheckCircle,
  Eye,
  Filter,
  Loader2,
  Thermometer,
  Gauge,
  Activity,
  Zap,
  GitCompareArrows,
  WifiOff,
  Search,
} from "lucide-react";

const severidadeConfig: Record<string, { color: string; bg: string }> = {
  "emergência": { color: "text-apple-red", bg: "bg-apple-red/10" },
  emergencia: { color: "text-apple-red", bg: "bg-apple-red/10" },
  "crítico": { color: "text-apple-red", bg: "bg-apple-red/10" },
  critico: { color: "text-apple-red", bg: "bg-apple-red/10" },
  aviso: { color: "text-apple-orange", bg: "bg-apple-orange/10" },
  info: { color: "text-apple-blue", bg: "bg-apple-blue/10" },
};

const tipoIcons: Record<string, any> = {
  temperatura_alta: Thermometer,
  pressao_alta: Gauge,
  vibracao_alta: Activity,
  corrente_alta: Zap,
  drift_codigo: GitCompareArrows,
  sem_comunicacao: WifiOff,
  anomalia_ml: AlertTriangle,
};

export default function Alertas() {
  const { addToast } = useToast();
  const [filtroSeveridade, setFiltroSeveridade] = useState<string>("todos");
  const [filtroStatus, setFiltroStatus] = useState<string>("todos");
  const [busca, setBusca] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["alertas"],
    queryFn: () => alertasApi.list().then((r) => r.data),
    refetchInterval: 15000,
  });

  const { data: stats } = useQuery({
    queryKey: ["alertas-stats"],
    queryFn: () => alertasApi.getEstatisticas().then((r) => r.data),
  });

  // ━━ SSE Real-time Stream ━━
  useEffect(() => {
    let eventSource: EventSource | null = null;
    try {
      eventSource = new EventSource(alertasApi.streamUrl);
      eventSource.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          if (parsed.evento === "novo_alerta" && parsed.alerta) {
            addToast(
              `⚠️ ${parsed.alerta.titulo || "Novo alerta detectado"}`,
              parsed.alerta.severidade === "emergência" || parsed.alerta.severidade === "crítico"
                ? "error"
                : "warning"
            );
          }
        } catch {}
      };
      eventSource.onerror = () => {
        eventSource?.close();
      };
    } catch {}

    return () => {
      eventSource?.close();
    };
  }, [addToast]);

  const alertas = data?.dados || data || [];
  const filteredAlertas = (Array.isArray(alertas) ? alertas : []).filter((a: any) => {
    if (filtroSeveridade !== "todos" && a.severidade !== filtroSeveridade) return false;
    if (filtroStatus !== "todos" && a.status !== filtroStatus) return false;
    if (busca && !(a.titulo?.toLowerCase().includes(busca.toLowerCase()) || a.codigo_alerta?.toLowerCase().includes(busca.toLowerCase()))) return false;
    return true;
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-32">
        <Loader2 className="animate-spin text-apple-blue" size={32} />
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-[1400px]">
      {/* ━━ Stats Strip ━━ */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { label: "Total Abertos", value: stats?.total_abertos ?? 43, color: "text-apple-orange" },
          { label: "Críticos", value: stats?.criticos ?? 8, color: "text-apple-red" },
          { label: "Custo/Mês (Visitas)", value: `R$ ${((stats?.custo_total_visitas_mes ?? 31400) / 1000).toFixed(1)}k`, color: "text-apple-red" },
          { label: "Taxa Falso Alerta", value: `${stats?.taxa_falso_alerta_geral ?? 64}%`, color: "text-apple-orange" },
        ].map((s) => (
          <div key={s.label} className="apple-card px-4 py-3 text-center">
            <p className="text-[11px] font-medium text-apple-tertiary">{s.label}</p>
            <p className={`text-[22px] font-bold tracking-tight ${s.color}`}>{s.value}</p>
          </div>
        ))}
      </div>

      {/* ━━ Filters ━━ */}
      <div className="apple-card p-4 flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-apple-tertiary" />
          <input
            type="text"
            placeholder="Buscar alertas..."
            value={busca}
            onChange={(e) => setBusca(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-apple-surface-1 border border-apple-separator rounded-lg text-[13px] text-apple-label placeholder:text-apple-quaternary focus:outline-none focus:ring-2 focus:ring-apple-blue/30"
          />
        </div>
        <select
          value={filtroSeveridade}
          onChange={(e) => setFiltroSeveridade(e.target.value)}
          className="px-3 py-2 bg-apple-surface-1 border border-apple-separator rounded-lg text-[13px] text-apple-label focus:outline-none focus:ring-2 focus:ring-apple-blue/30"
        >
          <option value="todos">Todas Severidades</option>
          <option value="emergência">Emergência</option>
          <option value="crítico">Crítico</option>
          <option value="aviso">Aviso</option>
          <option value="info">Info</option>
        </select>
        <select
          value={filtroStatus}
          onChange={(e) => setFiltroStatus(e.target.value)}
          className="px-3 py-2 bg-apple-surface-1 border border-apple-separator rounded-lg text-[13px] text-apple-label focus:outline-none focus:ring-2 focus:ring-apple-blue/30"
        >
          <option value="todos">Todos Status</option>
          <option value="aberto">Aberto</option>
          <option value="em_investigacao">Em Investigação</option>
          <option value="resolvido">Resolvido</option>
          <option value="falso_alerta">Falso Alerta</option>
        </select>
      </div>

      {/* ━━ Alert List ━━ */}
      <div className="space-y-2">
        {filteredAlertas.map((alerta: any, i: number) => {
          const sev = severidadeConfig[alerta.severidade] || severidadeConfig.info;
          const Icon = tipoIcons[alerta.tipo] || Bell;

          return (
            <div
              key={alerta.id || i}
              className="apple-card p-4 flex items-start gap-4 hover:shadow-md transition-shadow animate-fade-in"
            >
              {/* Icon */}
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${sev.bg}`}>
                <Icon size={18} className={sev.color} />
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-0.5">
                  <h4 className="text-[14px] font-semibold text-apple-label truncate">
                    {alerta.titulo || "Alerta"}
                  </h4>
                  <span className={`status-badge ${sev.bg} ${sev.color}`}>
                    {alerta.severidade}
                  </span>
                </div>
                <p className="text-[12px] text-apple-tertiary line-clamp-1">
                  {alerta.descricao || "Sem descrição"}
                </p>
                <div className="flex items-center gap-4 mt-2 text-[11px] text-apple-quaternary">
                  <span>{alerta.codigo_alerta}</span>
                  <span>
                    {alerta.timestamp_criacao
                      ? new Date(alerta.timestamp_criacao).toLocaleDateString("pt-BR")
                      : "—"}
                  </span>
                  {alerta.is_falso_alerta && (
                    <span className="text-apple-orange font-semibold">Falso alerta confirmado</span>
                  )}
                </div>
              </div>

              {/* Status badge */}
              <div className="flex-shrink-0">
                <span
                  className={`status-badge ${
                    alerta.status === "aberto"
                      ? "bg-apple-orange/10 text-apple-orange"
                      : alerta.status === "resolvido"
                      ? "bg-apple-green/10 text-apple-green"
                      : "bg-apple-surface-2 text-apple-tertiary"
                  }`}
                >
                  {alerta.status?.replace(/_/g, " ")}
                </span>
              </div>
            </div>
          );
        })}

        {filteredAlertas.length === 0 && (
          <div className="apple-card p-12 text-center">
            <Bell className="mx-auto mb-3 text-apple-quaternary" size={32} />
            <p className="text-[14px] font-medium text-apple-tertiary">
              Nenhum alerta encontrado com os filtros aplicados
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
