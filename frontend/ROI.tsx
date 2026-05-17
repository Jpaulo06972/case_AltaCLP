// AltaCLP Intelligence — ROI & Economia
// The business case for the HomoDeus platform investment

import { DollarSign, TrendingUp, CheckCircle, Clock, Zap } from "lucide-react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
  LineChart, Line, Legend,
} from "recharts";
import { savingsProjection } from "@/lib/mockData";

const roiBreakdown = [
  { category: "Comissionamento (Anaclara)", value: 780000, type: "immediate", description: "Contrato em risco · entrega jun/2026" },
  { category: "Falsos Alertas (-65%)", value: 245000, type: "annual", description: "R$ 20.4k/mês em regime pleno" },
  { category: "Drift de Código (prevenção)", value: 240000, type: "annual", description: "Média 4 incidentes/ano · R$ 60k/incidente" },
  { category: "Cotação Rápida (+vendas)", value: 480000, type: "annual", description: "6 negócios/mês recuperados · R$ 40k ticket médio" },
  { category: "Retenção de Clientes (NPS)", value: 120000, type: "annual", description: "Redução de churn estimada em 1 cliente/ano" },
];

const monthlyProjection = [
  { month: "Jun", sem_ia: -31400, com_ia: 748600 },
  { month: "Jul", sem_ia: -31400, com_ia: 30000 },
  { month: "Ago", sem_ia: -31400, com_ia: 35000 },
  { month: "Set", sem_ia: -31400, com_ia: 35000 },
  { month: "Out", sem_ia: -31400, com_ia: 55000 },
  { month: "Nov", sem_ia: -31400, com_ia: 55000 },
  { month: "Dez", sem_ia: -31400, com_ia: 55000 },
];

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="p-3 rounded text-xs" style={{ background: "oklch(0.16 0.008 260)", border: "1px solid oklch(0.22 0.008 260)", fontFamily: "'JetBrains Mono', monospace", color: "oklch(0.85 0.005 260)" }}>
        <div className="font-semibold mb-1">{label}</div>
        {payload.map((p: any) => (
          <div key={p.name} style={{ color: p.color }}>
            {p.name}: R$ {Number(p.value).toLocaleString("pt-BR")}
          </div>
        ))}
      </div>
    );
  }
  return null;
};

export default function ROI() {
  const totalAnnual = roiBreakdown.reduce((sum, r) => sum + r.value, 0);

  return (
    <div className="min-h-screen">
      <header
        className="sticky top-0 z-10 flex items-center justify-between px-6 h-14 border-b"
        style={{ background: "oklch(0.11 0.008 260 / 0.95)", borderColor: "oklch(0.18 0.008 260)", backdropFilter: "blur(8px)" }}
      >
        <div className="flex items-center gap-3">
          <DollarSign size={16} style={{ color: "#10B981" }} />
          <h1 className="text-sm font-semibold" style={{ color: "oklch(0.95 0.003 260)", fontFamily: "'Space Grotesk', sans-serif" }}>
            ROI & Projeção de Economia
          </h1>
        </div>
        <div className="text-xs font-bold px-3 py-1 rounded" style={{ background: "oklch(0.65 0.17 160 / 0.15)", color: "#10B981", fontFamily: "'JetBrains Mono', monospace" }}>
          ROI ESTIMADO: 8.8x em 12 meses
        </div>
      </header>

      <div className="p-6 space-y-6">
        {/* Hero ROI */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2 p-6 rounded" style={{ background: "oklch(0.13 0.008 260)", border: "1px solid oklch(0.65 0.17 160 / 0.4)" }}>
            <div className="flex items-start justify-between mb-4">
              <div>
                <h2 className="text-lg font-bold mb-1" style={{ color: "oklch(0.95 0.003 260)", fontFamily: "'Space Grotesk', sans-serif" }}>
                  Retorno sobre Investimento
                </h2>
                <p className="text-xs" style={{ color: "oklch(0.55 0.012 260)" }}>
                  Baseado em dados reais extraídos das operações da AltaCLP
                </p>
              </div>
              <div className="text-right">
                <div className="text-4xl font-bold" style={{ color: "#10B981", fontFamily: "'JetBrains Mono', monospace" }}>
                  8.8x
                </div>
                <div className="text-xs" style={{ color: "oklch(0.55 0.012 260)" }}>ROI em 12 meses</div>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-4">
              {[
                { label: "Investimento", value: "R$ 150k", sub: "3 meses · 12 semanas", color: "#F59E0B" },
                { label: "Retorno Ano 1", value: "R$ 1,32M", sub: "economia + receita", color: "#10B981" },
                { label: "Payback", value: "< 6 sem.", sub: "só com Anaclara", color: "#10B981" },
              ].map((m) => (
                <div key={m.label} className="p-3 rounded text-center" style={{ background: "oklch(0.16 0.008 260)" }}>
                  <div className="text-xs mb-1" style={{ color: "oklch(0.55 0.012 260)", fontFamily: "'Space Grotesk', sans-serif" }}>{m.label}</div>
                  <div className="text-xl font-bold" style={{ color: m.color, fontFamily: "'JetBrains Mono', monospace" }}>{m.value}</div>
                  <div className="text-xs mt-0.5" style={{ color: "oklch(0.45 0.01 260)" }}>{m.sub}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="p-5 rounded" style={{ background: "oklch(0.13 0.008 260)", border: "1px solid oklch(0.22 0.008 260)" }}>
            <h3 className="text-sm font-semibold mb-3" style={{ color: "oklch(0.95 0.003 260)", fontFamily: "'Space Grotesk', sans-serif" }}>
              O que está incluído
            </h3>
            <div className="space-y-2 text-xs">
              {[
                "3 módulos de IA integrados",
                "Dashboard executivo unificado",
                "App mobile para técnicos",
                "Integração PostgreSQL + MQTT",
                "Agente GitOps de auditoria",
                "Assistente de cotação (WhatsApp)",
                "12 semanas de implementação",
                "Suporte por 6 meses pós-entrega",
              ].map((item) => (
                <div key={item} className="flex items-center gap-2">
                  <CheckCircle size={12} style={{ color: "#10B981", flexShrink: 0 }} />
                  <span style={{ color: "oklch(0.75 0.008 260)", fontFamily: "'Space Grotesk', sans-serif" }}>{item}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Breakdown chart */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="p-5 rounded" style={{ background: "oklch(0.13 0.008 260)", border: "1px solid oklch(0.22 0.008 260)" }}>
            <h3 className="text-sm font-semibold mb-1" style={{ color: "oklch(0.95 0.003 260)", fontFamily: "'Space Grotesk', sans-serif" }}>
              Economia por Categoria
            </h3>
            <p className="text-xs mb-4" style={{ color: "oklch(0.55 0.012 260)" }}>Total: R$ {totalAnnual.toLocaleString("pt-BR")}</p>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={roiBreakdown} layout="vertical" margin={{ top: 0, right: 20, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.18 0.008 260)" strokeOpacity={0.5} horizontal={false} />
                <XAxis type="number" tick={{ fill: "oklch(0.45 0.01 260)", fontSize: 9, fontFamily: "'JetBrains Mono', monospace" }}
                  axisLine={false} tickLine={false} tickFormatter={(v) => `R$${(v / 1000).toFixed(0)}k`} />
                <YAxis type="category" dataKey="category" tick={{ fill: "oklch(0.55 0.012 260)", fontSize: 9, fontFamily: "'Space Grotesk', sans-serif" }}
                  axisLine={false} tickLine={false} width={160} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="value" name="Valor" radius={[0, 3, 3, 0]}>
                  {roiBreakdown.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.type === "immediate" ? "#EF4444" : `oklch(${0.55 + index * 0.02} 0.17 160)`} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="p-5 rounded" style={{ background: "oklch(0.13 0.008 260)", border: "1px solid oklch(0.22 0.008 260)" }}>
            <h3 className="text-sm font-semibold mb-1" style={{ color: "oklch(0.95 0.003 260)", fontFamily: "'Space Grotesk', sans-serif" }}>
              Fluxo Mensal: Sem vs. Com Plataforma
            </h3>
            <p className="text-xs mb-4" style={{ color: "oklch(0.55 0.012 260)" }}>Jun/2026 inclui R$ 780k da Anaclara</p>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={monthlyProjection} margin={{ top: 0, right: 0, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.18 0.008 260)" strokeOpacity={0.5} />
                <XAxis dataKey="month" tick={{ fill: "oklch(0.45 0.01 260)", fontSize: 10, fontFamily: "'JetBrains Mono', monospace" }}
                  axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: "oklch(0.45 0.01 260)", fontSize: 9, fontFamily: "'JetBrains Mono', monospace" }}
                  axisLine={false} tickLine={false} tickFormatter={(v) => `R$${(v / 1000).toFixed(0)}k`} />
                <Tooltip content={<CustomTooltip />} />
                <Legend wrapperStyle={{ fontSize: "10px", fontFamily: "'JetBrains Mono', monospace", color: "oklch(0.55 0.012 260)" }} />
                <Line type="monotone" dataKey="sem_ia" name="Sem Plataforma" stroke="#EF4444" strokeWidth={2} dot={false} strokeDasharray="4 4" />
                <Line type="monotone" dataKey="com_ia" name="Com Plataforma" stroke="#10B981" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Pricing */}
        <div className="p-6 rounded" style={{ background: "oklch(0.13 0.008 260)", border: "1px solid oklch(0.75 0.18 80 / 0.4)" }}>
          <h3 className="text-sm font-semibold mb-4" style={{ color: "oklch(0.95 0.003 260)", fontFamily: "'Space Grotesk', sans-serif" }}>
            Estrutura de Investimento
          </h3>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {[
              {
                phase: "Fase 1",
                weeks: "Semanas 1–4",
                price: "R$ 45.000",
                items: ["Thresholds dinâmicos", "Assistente de cotação", "Integração MQTT/PostgreSQL"],
                highlight: true,
                badge: "PAYBACK IMEDIATO",
              },
              {
                phase: "Fase 2",
                weeks: "Semanas 5–8",
                price: "R$ 55.000",
                items: ["Auditoria GitOps", "App mobile técnicos", "Dashboard executivo"],
                highlight: false,
              },
              {
                phase: "Fase 3",
                weeks: "Semanas 9–12",
                price: "R$ 50.000",
                items: ["Modelo IA preditiva", "Retreinamento automático", "Suporte 6 meses"],
                highlight: false,
              },
            ].map((p) => (
              <div key={p.phase} className="p-5 rounded" style={{
                background: p.highlight ? "oklch(0.75 0.18 80 / 0.08)" : "oklch(0.16 0.008 260)",
                border: p.highlight ? "1px solid oklch(0.75 0.18 80 / 0.4)" : "1px solid oklch(0.22 0.008 260)",
              }}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-bold" style={{ color: p.highlight ? "#F59E0B" : "oklch(0.65 0.008 260)", fontFamily: "'Space Grotesk', sans-serif" }}>{p.phase}</span>
                  {p.badge && (
                    <span className="text-xs px-2 py-0.5 rounded font-semibold" style={{ background: "#F59E0B", color: "oklch(0.1 0.008 260)", fontFamily: "'JetBrains Mono', monospace" }}>
                      {p.badge}
                    </span>
                  )}
                </div>
                <div className="text-xs mb-2" style={{ color: "oklch(0.45 0.01 260)", fontFamily: "'JetBrains Mono', monospace" }}>{p.weeks}</div>
                <div className="text-2xl font-bold mb-3" style={{ color: "oklch(0.95 0.003 260)", fontFamily: "'JetBrains Mono', monospace" }}>{p.price}</div>
                <div className="space-y-1.5">
                  {p.items.map((item) => (
                    <div key={item} className="flex items-center gap-2 text-xs">
                      <CheckCircle size={11} style={{ color: "#10B981", flexShrink: 0 }} />
                      <span style={{ color: "oklch(0.65 0.008 260)", fontFamily: "'Space Grotesk', sans-serif" }}>{item}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 flex items-center justify-between p-4 rounded" style={{ background: "oklch(0.16 0.008 260)", border: "1px solid oklch(0.22 0.008 260)" }}>
            <div className="text-sm" style={{ color: "oklch(0.75 0.008 260)", fontFamily: "'Space Grotesk', sans-serif" }}>
              Investimento total (3 fases):
            </div>
            <div className="text-2xl font-bold" style={{ color: "#10B981", fontFamily: "'JetBrains Mono', monospace" }}>
              R$ 150.000
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
