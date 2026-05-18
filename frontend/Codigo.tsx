// AltaCLP Intelligence — Auditoria de Código (GitOps)
// Shows the code drift problem and the automated audit solution

import { GitBranch, AlertTriangle, CheckCircle, XCircle, HelpCircle } from "lucide-react";
import { machines, incidents } from "./mockData";
import { useState, useEffect } from "react";
import { api } from "./api";

export default function Codigo() {
  const [gitopsStats, setGitopsStats] = useState<any>(null);
  const [drifts, setDrifts] = useState<any>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const stats = await api.getGitOpsEstatisticas();
        const ativos = await api.getGitOpsDriftsAtivos();
        setGitopsStats(stats);
        setDrifts(ativos);
      } catch (err) {
        console.error(err);
      }
    }
    loadData();
  }, []);

  const driftCount = gitopsStats?.drifts_ativos || machines.filter((m) => m.codeSync === "divergent").length;
  const unknownCount = machines.filter((m) => m.codeSync === "unknown").length;
  const syncCount = gitopsStats ? 50 - gitopsStats.drifts_ativos : machines.filter((m) => m.codeSync === "ok").length;
  const codeIncidents = incidents.filter((i) => i.type === "code_drift");
  const totalLoss = gitopsStats?.prejuizo_historico || codeIncidents.reduce((sum, i) => sum + i.loss, 0);

  return (
    <div className="min-h-screen">
      <header
        className="sticky top-0 z-10 flex items-center justify-between px-6 h-14 border-b"
        style={{ background: "oklch(0.11 0.008 260 / 0.95)", borderColor: "oklch(0.18 0.008 260)", backdropFilter: "blur(8px)" }}
      >
        <div className="flex items-center gap-3">
          <GitBranch size={16} style={{ color: "#F59E0B" }} />
          <h1 className="text-sm font-semibold" style={{ color: "oklch(0.95 0.003 260)", fontFamily: "'Space Grotesk', sans-serif" }}>
            Auditoria de Código — Campo vs. Git
          </h1>
        </div>
        <div className="flex items-center gap-2 text-xs px-3 py-1 rounded" style={{ background: "oklch(0.6 0.22 25 / 0.15)", color: "#EF4444", fontFamily: "'JetBrains Mono', monospace" }}>
          <AlertTriangle size={12} />
          {driftCount} MÁQUINAS COM DRIFT
        </div>
      </header>

      <div className="p-6 space-y-6">
        {/* KPIs */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-5 rounded" style={{ background: "oklch(0.13 0.008 260)", border: "1px solid #EF444440" }}>
            <div className="flex items-center gap-2 mb-2">
              <XCircle size={14} style={{ color: "#EF4444" }} />
              <span className="text-xs font-semibold uppercase" style={{ color: "oklch(0.55 0.012 260)", fontFamily: "'Space Grotesk', sans-serif" }}>Drift Confirmado</span>
            </div>
            <div className="text-3xl font-bold" style={{ color: "#EF4444", fontFamily: "'JetBrains Mono', monospace" }}>{driftCount}</div>
            <div className="text-xs mt-1" style={{ color: "oklch(0.45 0.01 260)" }}>máquinas com código divergente</div>
          </div>
          <div className="p-5 rounded" style={{ background: "oklch(0.13 0.008 260)", border: "1px solid #F59E0B40" }}>
            <div className="flex items-center gap-2 mb-2">
              <HelpCircle size={14} style={{ color: "#F59E0B" }} />
              <span className="text-xs font-semibold uppercase" style={{ color: "oklch(0.55 0.012 260)", fontFamily: "'Space Grotesk', sans-serif" }}>Sem Verificação</span>
            </div>
            <div className="text-3xl font-bold" style={{ color: "#F59E0B", fontFamily: "'JetBrains Mono', monospace" }}>{unknownCount}</div>
            <div className="text-xs mt-1" style={{ color: "oklch(0.45 0.01 260)" }}>máquinas sem auditoria ativa</div>
          </div>
          <div className="p-5 rounded" style={{ background: "oklch(0.13 0.008 260)", border: "1px solid #10B98140" }}>
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle size={14} style={{ color: "#10B981" }} />
              <span className="text-xs font-semibold uppercase" style={{ color: "oklch(0.55 0.012 260)", fontFamily: "'Space Grotesk', sans-serif" }}>Sincronizadas</span>
            </div>
            <div className="text-3xl font-bold" style={{ color: "#10B981", fontFamily: "'JetBrains Mono', monospace" }}>{syncCount}</div>
            <div className="text-xs mt-1" style={{ color: "oklch(0.45 0.01 260)" }}>código campo = Git central</div>
          </div>
          <div className="p-5 rounded" style={{ background: "oklch(0.13 0.008 260)", border: "1px solid #EF444440" }}>
            <div className="flex items-center gap-2 mb-2">
              <AlertTriangle size={14} style={{ color: "#EF4444" }} />
              <span className="text-xs font-semibold uppercase" style={{ color: "oklch(0.55 0.012 260)", fontFamily: "'Space Grotesk', sans-serif" }}>Prejuízo Acumulado</span>
            </div>
            <div className="text-3xl font-bold" style={{ color: "#EF4444", fontFamily: "'JetBrains Mono', monospace" }}>R$ {(totalLoss / 1000).toFixed(0)}k</div>
            <div className="text-xs mt-1" style={{ color: "oklch(0.45 0.01 260)" }}>4 incidentes em 12 meses</div>
          </div>
        </div>

        {/* How it works */}
        <div className="p-5 rounded" style={{ background: "oklch(0.13 0.008 260)", border: "1px solid oklch(0.65 0.17 160 / 0.3)" }}>
          <div className="flex items-center gap-2 mb-4">
            <CheckCircle size={14} style={{ color: "#10B981" }} />
            <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: "#10B981", fontFamily: "'Space Grotesk', sans-serif" }}>
              Solução: Agente GitOps Automático
            </span>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 text-xs">
            {[
              { step: "01", title: "Hash do CLP", desc: "Agente edge calcula hash do código rodando no CLP a cada 6 horas via OPC UA." },
              { step: "02", title: "Comparação com Git", desc: "Hash é comparado com a versão oficial no repositório Git central da AltaCLP." },
              { step: "03", title: "Alerta de Divergência", desc: "Se divergência detectada, engenharia é alertada antes do próximo deploy." },
              { step: "04", title: "Pull Request Automático", desc: "Sistema sugere PR com o diff do hotfix de campo para revisão e merge." },
            ].map((s) => (
              <div key={s.step} className="p-3 rounded" style={{ background: "oklch(0.16 0.008 260)" }}>
                <div className="text-lg font-bold mb-1" style={{ color: "#F59E0B", fontFamily: "'JetBrains Mono', monospace" }}>{s.step}</div>
                <div className="font-semibold mb-1" style={{ color: "oklch(0.85 0.005 260)", fontFamily: "'Space Grotesk', sans-serif" }}>{s.title}</div>
                <p style={{ color: "oklch(0.55 0.012 260)", lineHeight: "1.5" }}>{s.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Incidents timeline */}
        <div className="rounded overflow-hidden" style={{ background: "oklch(0.13 0.008 260)", border: "1px solid oklch(0.22 0.008 260)" }}>
          <div className="px-5 py-3 border-b" style={{ borderColor: "oklch(0.18 0.008 260)" }}>
            <h2 className="text-sm font-semibold" style={{ color: "oklch(0.95 0.003 260)", fontFamily: "'Space Grotesk', sans-serif" }}>
              Incidentes por Drift de Código — 2026
            </h2>
            <p className="text-xs mt-0.5" style={{ color: "oklch(0.55 0.012 260)" }}>
              Marcos reportou 3 incidentes. Cláudia identificou 4. Prejuízo real: R$ {totalLoss.toLocaleString("pt-BR")}.
            </p>
          </div>
          <div className="divide-y" style={{ borderColor: "oklch(0.16 0.008 260)" }}>
            {codeIncidents.map((inc) => (
              <div key={inc.id} className="px-5 py-4 hover:bg-[oklch(0.16_0.008_260)] transition-colors">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 text-center">
                    <div className="text-xs font-bold" style={{ color: "#F59E0B", fontFamily: "'JetBrains Mono', monospace" }}>{inc.date}</div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-bold" style={{ color: "oklch(0.85 0.005 260)", fontFamily: "'Space Grotesk', sans-serif" }}>
                        {inc.machine} · {inc.client}
                      </span>
                      <span className="text-xs px-1.5 py-0.5 rounded" style={{
                        background: inc.severity === "critical" ? "oklch(0.6 0.22 25 / 0.15)" : "oklch(0.75 0.18 80 / 0.15)",
                        color: inc.severity === "critical" ? "#EF4444" : "#F59E0B",
                        fontFamily: "'JetBrains Mono', monospace",
                      }}>
                        {inc.severity.toUpperCase()}
                      </span>
                      {!inc.resolved && (
                        <span className="text-xs px-1.5 py-0.5 rounded" style={{ background: "oklch(0.6 0.22 25 / 0.15)", color: "#EF4444", fontFamily: "'JetBrains Mono', monospace" }}>
                          ABERTO
                        </span>
                      )}
                    </div>
                    <p className="text-xs mb-2" style={{ color: "oklch(0.65 0.008 260)", fontFamily: "'Space Grotesk', sans-serif", lineHeight: "1.5" }}>
                      {inc.description}
                    </p>
                    <div className="p-2 rounded text-xs" style={{ background: "oklch(0.16 0.008 260)" }}>
                      <span className="font-semibold" style={{ color: "#F59E0B" }}>Causa Raiz: </span>
                      <span style={{ color: "oklch(0.65 0.008 260)", fontFamily: "'Space Grotesk', sans-serif" }}>{inc.rootCause}</span>
                    </div>
                  </div>
                  <div className="flex-shrink-0 text-right">
                    {inc.loss > 0 ? (
                      <div className="text-sm font-bold" style={{ color: "#EF4444", fontFamily: "'JetBrains Mono', monospace" }}>
                        R$ {inc.loss.toLocaleString("pt-BR")}
                      </div>
                    ) : (
                      <div className="text-xs" style={{ color: "oklch(0.4 0.01 260)", fontFamily: "'JetBrains Mono', monospace" }}>
                        sem perda<br />declarada
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
