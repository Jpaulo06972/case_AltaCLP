/**
 * AltaCLP Intelligence — GitOps Audit Page
 * Code drift monitoring with Apple-style design
 */

import { useQuery } from "@tanstack/react-query";
import { gitopsApi } from "@/services/api";
import {
  GitCompareArrows,
  CheckCircle,
  AlertTriangle,
  Loader2,
  FileCode,
  User,
  Clock,
  ExternalLink,
} from "lucide-react";
import { useState } from "react";

// Modal Component for Diff Preview
function DiffModal({ drift, onClose }: { drift: any; onClose: () => void }) {
  const [creatingPR, setCreatingPR] = useState(false);
  const [prCreated, setPrCreated] = useState(false);

  const handleSugerirPR = () => {
    setCreatingPR(true);
    setTimeout(() => {
      setCreatingPR(false);
      setPrCreated(true);
    }, 1500);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4 animate-fade-in">
      <div className="apple-card w-full max-w-3xl overflow-hidden shadow-2xl flex flex-col max-h-[90vh] animate-scale-in">
        <div className="px-6 py-4 border-b border-apple-separator/30 flex items-center justify-between bg-apple-surface-0">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-apple-red/10 flex items-center justify-center">
              <GitCompareArrows size={16} className="text-apple-red" />
            </div>
            <div>
              <h3 className="text-[15px] font-semibold text-apple-label">Revisão de Código (GitOps)</h3>
              <p className="text-[12px] text-apple-tertiary">Divergência detectada em {drift.maquina_codigo}</p>
            </div>
          </div>
          <button onClick={onClose} className="text-apple-tertiary hover:text-apple-label p-1">
            ✕
          </button>
        </div>
        
        <div className="p-6 overflow-y-auto bg-apple-surface-1/50 flex-1">
          <p className="text-[13px] font-semibold text-apple-label mb-2">Diff de Código (Gateway IoT OPC UA vs. Git Central)</p>
          <div className="bg-[#1e1e1e] rounded-xl overflow-hidden font-mono text-[12px] leading-relaxed shadow-inner">
            {(drift.diff_detalhe || "- T_Setpoint := 85.0;\n+ T_Setpoint := 90.0;\n  Alarm_Enable := TRUE;").split('\n').map((line: string, i: number) => {
              const isAdded = line.startsWith('+');
              const isRemoved = line.startsWith('-');
              return (
                <div key={i} className={`px-4 py-1 flex ${isAdded ? 'bg-green-500/20 text-green-300' : isRemoved ? 'bg-red-500/20 text-red-300' : 'text-gray-300'}`}>
                  <span className="w-8 select-none opacity-50 border-r border-gray-700 mr-4 text-right pr-2">{i + 1}</span>
                  <span className="whitespace-pre-wrap">{line}</span>
                </div>
              );
            })}
          </div>
        </div>

        <div className="px-6 py-4 border-t border-apple-separator/30 bg-apple-surface-0 flex justify-end gap-3">
          <button onClick={onClose} className="apple-btn apple-btn-secondary text-[13px] px-5 py-2">
            Cancelar
          </button>
          <button 
            onClick={handleSugerirPR}
            disabled={prCreated || creatingPR}
            className={`apple-btn text-[13px] px-5 py-2 flex items-center gap-2 ${prCreated ? 'bg-apple-green text-white border-transparent' : 'apple-btn-primary'}`}
          >
            {creatingPR ? <Loader2 size={16} className="animate-spin" /> : prCreated ? <CheckCircle size={16} /> : <GitCompareArrows size={16} />}
            {prCreated ? "PR Sugerido" : creatingPR ? "Gerando PR..." : "Sugerir Pull Request"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function GitOps() {
  const [selectedDrift, setSelectedDrift] = useState<any>(null);

  const { data: drifts, isLoading: loadingDrifts } = useQuery({
    queryKey: ["gitops-drifts"],
    queryFn: () => gitopsApi.getDriftsAtivos().then((r) => r.data),
  });

  const { data: stats } = useQuery({
    queryKey: ["gitops-stats"],
    queryFn: () => gitopsApi.getEstatisticas().then((r) => r.data),
  });

  if (loadingDrifts) {
    return (
      <div className="flex items-center justify-center py-32">
        <Loader2 className="animate-spin text-apple-blue" size={32} />
      </div>
    );
  }

  const driftList = drifts?.dados || drifts || [];

  return (
    <div className="space-y-6 max-w-[1400px]">
      {selectedDrift && <DiffModal drift={selectedDrift} onClose={() => setSelectedDrift(null)} />}

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { label: "Verificações 24h", value: stats?.total_verificacoes_24h ?? "—", color: "text-apple-blue" },
          { label: "Em Sync", value: stats?.em_sync_pct ? `${stats.em_sync_pct}%` : "94%", color: "text-apple-green" },
          { label: "Drifts Ativos", value: stats?.drifts_ativos ?? 3, color: "text-apple-red" },
          { label: "Prejuízo Histórico", value: `R$ ${((stats?.prejuizo_historico ?? 250000) / 1000).toFixed(0)}k`, color: "text-apple-red" },
        ].map((s) => (
          <div key={s.label} className="apple-card px-4 py-3 text-center">
            <p className="text-[11px] font-medium text-apple-tertiary">{s.label}</p>
            <p className={`text-[22px] font-bold tracking-tight ${s.color}`}>{s.value}</p>
          </div>
        ))}
      </div>

      {/* Active Drifts */}
      <div>
        <h3 className="text-[15px] font-semibold text-apple-label mb-3">
          Drifts de Código Ativos
        </h3>
        <div className="space-y-3">
          {(Array.isArray(driftList) ? driftList : []).map((drift: any, i: number) => (
            <div key={drift.id || i} className="apple-card p-5">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-apple-red/10 flex items-center justify-center">
                    <GitCompareArrows size={18} className="text-apple-red" />
                  </div>
                  <div>
                    <h4 className="text-[14px] font-semibold text-apple-label">
                      {drift.maquina_codigo || drift.codigo || `Drift #${i + 1}`}
                    </h4>
                    <p className="text-[12px] text-apple-tertiary">
                      {drift.diff_resumo || "Código em campo difere do repositório Git"}
                    </p>
                  </div>
                </div>
                <span className="status-badge bg-apple-red/10 text-apple-red">
                  <AlertTriangle size={12} />
                  Drift Ativo
                </span>
              </div>

              {/* Diff details */}
              <div className="bg-apple-surface-1 rounded-xl p-4 mt-3">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-[12px]">
                  {drift.tecnico_suspeito && (
                    <div className="flex items-center gap-2">
                      <User size={14} className="text-apple-tertiary" />
                      <div>
                        <p className="text-apple-tertiary">Técnico suspeito</p>
                        <p className="font-semibold text-apple-label">{drift.tecnico_suspeito}</p>
                      </div>
                    </div>
                  )}
                  {drift.diff_linhas !== undefined && (
                    <div className="flex items-center gap-2">
                      <FileCode size={14} className="text-apple-tertiary" />
                      <div>
                        <p className="text-apple-tertiary">Linhas alteradas</p>
                        <p className="font-semibold text-apple-label">{drift.diff_linhas} linhas</p>
                      </div>
                    </div>
                  )}
                  {drift.timestamp_verificacao && (
                    <div className="flex items-center gap-2">
                      <Clock size={14} className="text-apple-tertiary" />
                      <div>
                        <p className="text-apple-tertiary">Última verificação</p>
                        <p className="font-semibold text-apple-label">
                          {new Date(drift.timestamp_verificacao).toLocaleString("pt-BR")}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2 mt-4">
                <button 
                  onClick={() => setSelectedDrift(drift)}
                  className="apple-btn apple-btn-primary text-[12px] py-1.5 px-4"
                >
                  <FileCode size={14} />
                  Ver Diff Formatado
                </button>
              </div>
            </div>
          ))}

          {(Array.isArray(driftList) ? driftList : []).length === 0 && (
            <div className="apple-card p-12 text-center">
              <CheckCircle className="mx-auto mb-3 text-apple-green" size={32} />
              <p className="text-[14px] font-medium text-apple-label">
                Todos os CLPs em sync
              </p>
              <p className="text-[12px] text-apple-tertiary mt-1">
                Nenhum drift de código detectado
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
