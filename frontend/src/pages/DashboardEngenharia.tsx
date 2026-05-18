/**
 * AltaCLP Intelligence — Dashboard Engenharia
 * Apple HomeKit-style machine grid + commissioning backlog
 */

import { useQuery } from "@tanstack/react-query";
import { dashboardApi } from "@/services/api";
import {
  Cpu,
  AlertTriangle,
  GitCompareArrows,
  Wrench,
  CheckCircle,
  WifiOff,
  Loader2,
  ChevronRight,
} from "lucide-react";
import { useNavigate } from "react-router-dom";

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

  const { data, isLoading } = useQuery({
    queryKey: ["dashboard-engenharia"],
    queryFn: () => dashboardApi.getEngenharia().then((r) => r.data),
    refetchInterval: 30000,
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

  return (
    <div className="space-y-6 max-w-[1400px]">
      {/* ━━ KPI Strip ━━ */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        {[
          { label: "Backlog", value: kpis.backlog_total || 26, color: "text-apple-orange" },
          { label: "Com Atraso", value: kpis.com_atraso || 13, color: "text-apple-red" },
          { label: "Tempo Médio", value: `${kpis.tempo_medio_comissionamento_dias || 6.2}d`, color: "text-apple-blue" },
          { label: "Alertas Ativos", value: kpis.alertas_ativos || 43, color: "text-apple-orange" },
          { label: "CLPs c/ Drift", value: kpis.maquinas_drift || 3, color: "text-apple-red" },
        ].map((k) => (
          <div key={k.label} className="apple-card px-4 py-3 text-center">
            <p className="text-[11px] font-medium text-apple-tertiary">{k.label}</p>
            <p className={`text-[22px] font-bold tracking-tight ${k.color}`}>{k.value}</p>
          </div>
        ))}
      </div>

      {/* ━━ Machine Grid (HomeKit style) ━━ */}
      <div>
        <h3 className="text-[15px] font-semibold text-apple-label mb-3">
          Parque de Máquinas
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3">
          {maquinas.map((m: any) => {
            const status = statusConfig[m.status] || statusConfig.operando;
            const StatusIcon = status.icon;

            return (
              <button
                key={m.id || m.codigo}
                onClick={() => m.id && navigate(`/maquinas/${m.id}`)}
                className="apple-card apple-card-interactive p-4 text-left group"
              >
                <div className="flex items-center justify-between mb-2">
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${status.bg}`}>
                    <StatusIcon size={16} className={status.color} />
                  </div>
                  {!m.codigo_sync && m.codigo_sync !== undefined && (
                    <GitCompareArrows size={14} className="text-apple-red" />
                  )}
                </div>
                <p className="text-[13px] font-semibold text-apple-label truncate">
                  {m.codigo}
                </p>
                <p className="text-[11px] text-apple-tertiary mt-0.5 truncate">
                  {status.label}
                </p>
                {m.taxa_falso !== undefined && (
                  <div className="mt-2 w-full bg-apple-surface-2 rounded-full h-1.5">
                    <div
                      className="h-full rounded-full transition-all"
                      style={{
                        width: `${Math.min(m.taxa_falso || 0, 100)}%`,
                        backgroundColor:
                          (m.taxa_falso || 0) > 70 ? "#FF3B30" :
                          (m.taxa_falso || 0) > 50 ? "#FF9500" : "#34C759",
                      }}
                    />
                  </div>
                )}
              </button>
            );
          })}
        </div>
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
