// AltaCLP Intelligence — Comissionamento
// Shows the backlog crisis and the AI-assisted commissioning solution

import { useState, useEffect } from "react";
import { Wrench, AlertTriangle, Clock, CheckCircle, DollarSign } from "lucide-react";
import { commissioningBacklog } from "./mockData";
import { api } from "./api";

const statusConfig = {
  fine: { label: "MULTA ATIVA", color: "#EF4444", bg: "oklch(0.6 0.22 25 / 0.15)" },
  delayed: { label: "ATRASADO", color: "#F59E0B", bg: "oklch(0.75 0.18 80 / 0.15)" },
  at_risk: { label: "EM RISCO", color: "#F59E0B", bg: "oklch(0.75 0.18 80 / 0.1)" },
  scheduled: { label: "AGENDADO", color: "#10B981", bg: "oklch(0.65 0.17 160 / 0.15)" },
};

export default function Comissionamento() {
  const [comissionamentos, setComissionamentos] = useState<any[]>([]);

  useEffect(() => {
    api.getComissionamentos().then(res => setComissionamentos(res.dados || [])).catch(console.error);
  }, []);

  const dataToShow = comissionamentos.length > 0 ? comissionamentos.map((c, i) => ({
    id: `OS-${c.id.substring(0, 4).toUpperCase()}`,
    machine: "CLP (Comissionamento)",
    client: "Cliente da API", // A API retorna apenas cliente_id, ideal seria join, mas p/ MVP é mock
    status: c.dias_atraso > 15 ? "fine" : c.dias_atraso > 0 ? "delayed" : "scheduled",
    daysWaiting: c.dias_atraso,
    contractualDeadline: c.prazo_limite_cliente || "Sem prazo definido",
    engineer: c.engenheiro_responsavel,
    revenue: c.valor_contrato
  })) : commissioningBacklog;

  const totalRevenue = dataToShow.reduce((sum, i) => sum + i.revenue, 0);
  const fineCount = dataToShow.filter((i) => i.status === "fine").length;
  const delayedCount = dataToShow.filter((i) => i.status === "delayed" || i.status === "fine").length;

  return (
    <div className="min-h-screen">
      <header
        className="sticky top-0 z-10 flex items-center justify-between px-6 h-14 border-b"
        style={{ background: "oklch(0.11 0.008 260 / 0.95)", borderColor: "oklch(0.18 0.008 260)", backdropFilter: "blur(8px)" }}
      >
        <div className="flex items-center gap-3">
          <Wrench size={16} style={{ color: "#F59E0B" }} />
          <h1 className="text-sm font-semibold" style={{ color: "oklch(0.95 0.003 260)", fontFamily: "'Space Grotesk', sans-serif" }}>
            Backlog de Comissionamento
          </h1>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs px-2 py-1 rounded font-semibold" style={{ background: "oklch(0.6 0.22 25 / 0.15)", color: "#EF4444", fontFamily: "'JetBrains Mono', monospace" }}>
            {fineCount} COM MULTA
          </span>
          <span className="text-xs px-2 py-1 rounded font-semibold" style={{ background: "oklch(0.75 0.18 80 / 0.15)", color: "#F59E0B", fontFamily: "'JetBrains Mono', monospace" }}>
            {delayedCount} ATRASADAS
          </span>
        </div>
      </header>

      <div className="p-6 space-y-6">
        {/* KPIs */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { label: "Máquinas no Backlog", value: "26", unit: "", color: "#EF4444", icon: Wrench, sub: "2 novas esta semana" },
            { label: "Atraso Contratual", value: "13", unit: " máq.", color: "#EF4444", icon: AlertTriangle, sub: "4 com multa ativa" },
            { label: "Receita Bloqueada", value: "R$ 962k", unit: "", color: "#F59E0B", icon: DollarSign, sub: "aguardando comissionamento" },
            { label: "Tempo Médio/Máquina", value: "6", unit: " dias", color: "#F59E0B", icon: Clock, sub: "Marcos diz 3-4 (otimista)" },
          ].map((k) => (
            <div key={k.label} className="p-5 rounded" style={{ background: "oklch(0.13 0.008 260)", border: `1px solid ${k.color}40` }}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: "oklch(0.55 0.012 260)", fontFamily: "'Space Grotesk', sans-serif" }}>{k.label}</span>
                <k.icon size={14} style={{ color: k.color }} />
              </div>
              <div className="text-3xl font-bold" style={{ color: k.color, fontFamily: "'JetBrains Mono', monospace" }}>{k.value}<span className="text-lg">{k.unit}</span></div>
              <div className="text-xs mt-1" style={{ color: "oklch(0.45 0.01 260)" }}>{k.sub}</div>
            </div>
          ))}
        </div>

        {/* AI Solution preview */}
        <div className="p-5 rounded" style={{ background: "oklch(0.13 0.008 260)", border: "1px solid oklch(0.65 0.17 160 / 0.4)" }}>
          <div className="flex items-center gap-2 mb-3">
            <CheckCircle size={14} style={{ color: "#10B981" }} />
            <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: "#10B981", fontFamily: "'Space Grotesk', sans-serif" }}>
              Solução: Assistente de Comissionamento com IA
            </span>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 text-xs">
            <div className="p-3 rounded" style={{ background: "oklch(0.16 0.008 260)" }}>
              <div className="font-semibold mb-1" style={{ color: "oklch(0.85 0.005 260)", fontFamily: "'Space Grotesk', sans-serif" }}>1. Áudio do Vendedor → Especificação</div>
              <p style={{ color: "oklch(0.55 0.012 260)", lineHeight: "1.5" }}>Whisper transcreve o áudio do WhatsApp. GPT-4o extrai parâmetros da fábrica e gera BOM preliminar em minutos.</p>
            </div>
            <div className="p-3 rounded" style={{ background: "oklch(0.16 0.008 260)" }}>
              <div className="font-semibold mb-1" style={{ color: "oklch(0.85 0.005 260)", fontFamily: "'Space Grotesk', sans-serif" }}>2. Template Pré-Preenchido</div>
              <p style={{ color: "oklch(0.55 0.012 260)", lineHeight: "1.5" }}>Sistema busca máquinas similares já comissionadas e sugere configuração base. Engenheiro recebe 90% pronto.</p>
            </div>
            <div className="p-3 rounded" style={{ background: "oklch(0.16 0.008 260)" }}>
              <div className="font-semibold mb-1" style={{ color: "oklch(0.85 0.005 260)", fontFamily: "'Space Grotesk', sans-serif" }}>3. Resultado: 6 dias → 2 dias</div>
              <p style={{ color: "oklch(0.55 0.012 260)", lineHeight: "1.5" }}>104 dias de engenharia liberados. Backlog zerado em 8 semanas. Anaclara entregue em junho.</p>
            </div>
          </div>
        </div>

        {/* Backlog table */}
        <div className="rounded overflow-hidden" style={{ background: "oklch(0.13 0.008 260)", border: "1px solid oklch(0.22 0.008 260)" }}>
          <div className="px-5 py-3 border-b" style={{ borderColor: "oklch(0.18 0.008 260)" }}>
            <h2 className="text-sm font-semibold" style={{ color: "oklch(0.95 0.003 260)", fontFamily: "'Space Grotesk', sans-serif" }}>
              Backlog Atual — {dataToShow.length} Máquinas
            </h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr style={{ borderBottom: "1px solid oklch(0.18 0.008 260)" }}>
                  {["OS", "Máquina", "Cliente", "Status", "Dias Parado", "Prazo Contratual", "Engenheiro", "Receita"].map((h) => (
                    <th key={h} className="px-4 py-2.5 text-left font-semibold uppercase tracking-wider"
                      style={{ color: "oklch(0.4 0.01 260)", fontFamily: "'Space Grotesk', sans-serif", fontSize: "10px" }}>
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {dataToShow.map((item, i) => {
                  const sc = statusConfig[item.status as keyof typeof statusConfig] || statusConfig.scheduled;
                  return (
                    <tr key={item.id} className="hover:bg-[oklch(0.16_0.008_260)] transition-colors"
                      style={{ borderBottom: i < dataToShow.length - 1 ? "1px solid oklch(0.16 0.008 260)" : "none" }}>
                      <td className="px-4 py-3 font-bold" style={{ color: "#F59E0B", fontFamily: "'JetBrains Mono', monospace" }}>{item.id}</td>
                      <td className="px-4 py-3" style={{ color: "oklch(0.85 0.005 260)", fontFamily: "'Space Grotesk', sans-serif" }}>{item.machine}</td>
                      <td className="px-4 py-3" style={{ color: "oklch(0.65 0.008 260)", fontFamily: "'Space Grotesk', sans-serif" }}>{item.client}</td>
                      <td className="px-4 py-3">
                        <span className="px-2 py-0.5 rounded text-xs font-semibold" style={{ background: sc.bg, color: sc.color, fontFamily: "'JetBrains Mono', monospace" }}>
                          {sc.label}
                        </span>
                      </td>
                      <td className="px-4 py-3 font-bold" style={{ color: item.daysWaiting > 45 ? "#EF4444" : item.daysWaiting > 30 ? "#F59E0B" : "oklch(0.65 0.008 260)", fontFamily: "'JetBrains Mono', monospace" }}>
                        {item.daysWaiting}d
                      </td>
                      <td className="px-4 py-3" style={{ color: "oklch(0.65 0.008 260)", fontFamily: "'JetBrains Mono', monospace" }}>{item.contractualDeadline}</td>
                      <td className="px-4 py-3" style={{ color: "oklch(0.75 0.008 260)", fontFamily: "'Space Grotesk', sans-serif" }}>{item.engineer.split(" ")[0]}</td>
                      <td className="px-4 py-3 font-semibold" style={{ color: "#10B981", fontFamily: "'JetBrains Mono', monospace" }}>
                        R$ {item.revenue.toLocaleString("pt-BR")}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
              <tfoot>
                <tr style={{ borderTop: "1px solid oklch(0.22 0.008 260)" }}>
                  <td colSpan={7} className="px-4 py-3 text-right font-semibold text-xs" style={{ color: "oklch(0.55 0.012 260)", fontFamily: "'Space Grotesk', sans-serif" }}>
                    Total Receita Bloqueada:
                  </td>
                  <td className="px-4 py-3 font-bold text-sm" style={{ color: "#10B981", fontFamily: "'JetBrains Mono', monospace" }}>
                    R$ {totalRevenue.toLocaleString("pt-BR")}
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
