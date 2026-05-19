/**
 * AltaCLP Intelligence — Máquinas Page (List + Detail)
 * Apple HomeKit master-detail view
 */

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { maquinasApi } from "@/services/api";
import { useNavigate } from "react-router-dom";
import {
  Cpu,
  CheckCircle,
  AlertTriangle,
  WifiOff,
  Wrench,
  Search,
  Loader2,
  ChevronRight,
  GitCompareArrows,
} from "lucide-react";

const statusConfig: Record<string, { label: string; color: string; dot: string }> = {
  operando: { label: "Operando", color: "text-apple-green", dot: "bg-apple-green" },
  alerta: { label: "Alerta", color: "text-apple-orange", dot: "bg-apple-orange" },
  "crítico": { label: "Crítico", color: "text-apple-red", dot: "bg-apple-red" },
  critico: { label: "Crítico", color: "text-apple-red", dot: "bg-apple-red" },
  offline: { label: "Offline", color: "text-apple-tertiary", dot: "bg-apple-tertiary" },
  em_comissionamento: { label: "Comissionando", color: "text-apple-blue", dot: "bg-apple-blue" },
};

const PLC_LABELS: Record<string, string> = {
  siemens_s7: "Siemens S7",
  allen_bradley: "Allen-Bradley",
  schneider: "Schneider",
  weg: "WEG",
  weintek: "Weintek",
};

const STATUS_FILTER = [
  { value: "", label: "Todos os status" },
  { value: "operando", label: "Operando" },
  { value: "alerta", label: "Alerta" },
  { value: "crítico", label: "Parado / Crítico" },
  { value: "offline", label: "Offline" },
  { value: "em_comissionamento", label: "Manutenção" },
];

export default function Maquinas() {
  const navigate = useNavigate();
  const [statusFilter, setStatusFilter] = useState("");
  const { data, isLoading } = useQuery({
    queryKey: ["maquinas", statusFilter],
    queryFn: () => maquinasApi.list(statusFilter ? { status: statusFilter } : {}).then((r) => r.data),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-32">
        <Loader2 className="animate-spin text-apple-blue" size={32} />
      </div>
    );
  }

  const maquinas = data?.dados || data || [];

  return (
    <div className="space-y-4 max-w-[1400px]">
      <div className="apple-card p-4 flex items-center gap-4">
        <label className="text-[12px] font-medium text-apple-tertiary">Filtrar status</label>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-3 py-2 rounded-lg bg-apple-surface-1 text-[13px] min-w-[200px]"
        >
          {STATUS_FILTER.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
      </div>
      {/* Stats */}
      <div className="apple-card p-4 flex items-center justify-between">
        <div className="flex items-center gap-6">
          {Object.entries(
            (Array.isArray(maquinas) ? maquinas : []).reduce((acc: any, m: any) => {
              const s = m.status || "operando";
              acc[s] = (acc[s] || 0) + 1;
              return acc;
            }, {})
          ).map(([status, count]) => {
            const cfg = statusConfig[status] || statusConfig.operando;
            return (
              <div key={status} className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${cfg.dot}`} />
                <span className="text-[12px] font-medium text-apple-secondary">
                  {String(count)} {cfg.label}
                </span>
              </div>
            );
          })}
        </div>
        <span className="text-[13px] font-semibold text-apple-tertiary">
          {Array.isArray(maquinas) ? maquinas.length : 0} CLPs
        </span>
      </div>

      {/* Machine List */}
      <div className="apple-card overflow-hidden">
        {(Array.isArray(maquinas) ? maquinas : []).map((m: any, i: number) => {
          const status = statusConfig[m.status] || statusConfig.operando;

          return (
            <button
              key={m.id || i}
              onClick={() => m.id && navigate(`/maquinas/${m.id}`)}
              className={`w-full flex items-center gap-4 px-6 py-4 text-left hover:bg-apple-surface-1/50 transition-colors ${
                i > 0 ? "border-t border-apple-separator/30" : ""
              }`}
            >
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                m.status === "operando" ? "bg-apple-green/10" :
                m.status === "alerta" ? "bg-apple-orange/10" :
                m.status === "crítico" || m.status === "critico" ? "bg-apple-red/10" :
                "bg-apple-surface-2"
              }`}>
                <Cpu size={18} className={status.color} />
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-[14px] font-semibold text-apple-label">
                    {m.codigo}
                  </span>
                  {m.codigo_sync === false && (
                    <GitCompareArrows size={13} className="text-apple-red" />
                  )}
                </div>
                <p className="text-[12px] text-apple-tertiary truncate">
                  {m.nome || m.setor_planta || "—"}
                </p>
                {m.modelo_clp && (
                  <span className="inline-block mt-1 text-[10px] font-semibold px-2 py-0.5 rounded-md bg-apple-blue/10 text-apple-blue">
                    {PLC_LABELS[m.modelo_clp] || m.modelo_clp}
                  </span>
                )}
              </div>

              <div className="text-right flex-shrink-0">
                <span className={`status-badge ${
                  m.status === "operando" ? "bg-apple-green/10 text-apple-green" :
                  m.status === "alerta" ? "bg-apple-orange/10 text-apple-orange" :
                  m.status === "crítico" || m.status === "critico" ? "bg-apple-red/10 text-apple-red" :
                  "bg-apple-surface-2 text-apple-tertiary"
                }`}>
                  {status.label}
                </span>
              </div>

              <ChevronRight size={16} className="text-apple-quaternary flex-shrink-0" />
            </button>
          );
        })}
      </div>
    </div>
  );
}
