/**
 * AltaCLP Intelligence — ROI & Economia Page
 * Investment breakdown with Apple-style visuals
 */

import {
  DollarSign,
  TrendingUp,
  CheckCircle,
  Sparkles,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  LineChart,
  Line,
  Legend,
  CartesianGrid,
} from "recharts";

const roiBreakdown = [
  { category: "Anaclara (comissionamento)", value: 780000, type: "immediate" },
  { category: "Falsos Alertas (-65%)", value: 245000, type: "annual" },
  { category: "Drift de Código (prevenção)", value: 240000, type: "annual" },
  { category: "Cotação Rápida (+vendas)", value: 480000, type: "annual" },
  { category: "Retenção (NPS)", value: 120000, type: "annual" },
];

const monthlyProjection = [
  { month: "Jun", sem: -31400, com: 748600 },
  { month: "Jul", sem: -31400, com: 30000 },
  { month: "Ago", sem: -31400, com: 35000 },
  { month: "Set", sem: -31400, com: 35000 },
  { month: "Out", sem: -31400, com: 55000 },
  { month: "Nov", sem: -31400, com: 55000 },
  { month: "Dez", sem: -31400, com: 55000 },
];

function AppleTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="apple-card px-3 py-2 text-[12px] shadow-lg">
      <p className="font-semibold text-apple-label mb-1">{label}</p>
      {payload.map((p: any) => (
        <p key={p.name} style={{ color: p.color }} className="font-medium">
          {p.name}: R$ {Number(p.value).toLocaleString("pt-BR")}
        </p>
      ))}
    </div>
  );
}

export default function ROI() {
  const totalAnnual = roiBreakdown.reduce((sum, r) => sum + r.value, 0);

  return (
    <div className="space-y-6 max-w-[1400px]">
      {/* Hero */}
      <div className="apple-card p-8 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-60 h-60 bg-gradient-to-bl from-apple-green/8 to-transparent rounded-bl-full" />
        <div className="relative flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div>
            <h2 className="text-[22px] font-bold text-apple-label tracking-tight mb-1">
              Retorno sobre Investimento
            </h2>
            <p className="text-[14px] text-apple-tertiary">
              Projeção baseada nos dados operacionais reais da AltaCLP
            </p>
          </div>
          <div className="flex gap-8">
            {[
              { label: "Investimento", value: "R$ 150k", color: "text-apple-blue" },
              { label: "Retorno Ano 1", value: "R$ 2.52M", color: "text-apple-green" },
              { label: "ROI", value: "16.8x", color: "text-apple-green" },
              { label: "Payback", value: "< 6 sem.", color: "text-apple-blue" },
            ].map((m) => (
              <div key={m.label} className="text-center">
                <p className="text-[11px] font-medium text-apple-tertiary">{m.label}</p>
                <p className={`text-[24px] font-bold tracking-tight ${m.color}`}>{m.value}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="apple-card p-6">
          <h3 className="text-[15px] font-semibold text-apple-label mb-1">
            Economia por Categoria
          </h3>
          <p className="text-[12px] text-apple-tertiary mb-4">
            Total: R$ {totalAnnual.toLocaleString("pt-BR")}
          </p>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={roiBreakdown} layout="vertical" margin={{ left: 0, right: 20 }}>
              <XAxis
                type="number"
                tick={{ fill: "#8E8E93", fontSize: 10 }}
                axisLine={false}
                tickLine={false}
                tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`}
              />
              <YAxis
                type="category"
                dataKey="category"
                tick={{ fill: "#3C3C43", fontSize: 11 }}
                axisLine={false}
                tickLine={false}
                width={160}
              />
              <Tooltip content={<AppleTooltip />} />
              <Bar dataKey="value" name="Valor" radius={[0, 6, 6, 0]}>
                {roiBreakdown.map((entry, i) => (
                  <Cell
                    key={i}
                    fill={entry.type === "immediate" ? "#FF3B30" : "#34C759"}
                    fillOpacity={0.85}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="apple-card p-6">
          <h3 className="text-[15px] font-semibold text-apple-label mb-1">
            Fluxo Mensal: Sem vs. Com Plataforma
          </h3>
          <p className="text-[12px] text-apple-tertiary mb-4">
            Jun/2026 inclui R$ 780k da Anaclara
          </p>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={monthlyProjection} margin={{ left: -10, right: 0 }}>
              <CartesianGrid stroke="#E5E5EA" strokeDasharray="3 3" strokeOpacity={0.5} />
              <XAxis
                dataKey="month"
                tick={{ fill: "#8E8E93", fontSize: 11 }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                tick={{ fill: "#8E8E93", fontSize: 10 }}
                axisLine={false}
                tickLine={false}
                tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`}
              />
              <Tooltip content={<AppleTooltip />} />
              <Legend
                wrapperStyle={{ fontSize: "11px" }}
              />
              <Line type="monotone" dataKey="sem" name="Sem Plataforma" stroke="#FF3B30" strokeWidth={2} dot={false} strokeDasharray="5 5" />
              <Line type="monotone" dataKey="com" name="Com Plataforma" stroke="#34C759" strokeWidth={2.5} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Pricing Phases */}
      <div className="apple-card p-6">
        <h3 className="text-[15px] font-semibold text-apple-label mb-4">
          Estrutura de Investimento
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
            },
            {
              phase: "Fase 3",
              weeks: "Semanas 9–12",
              price: "R$ 50.000",
              items: ["Modelo IA preditiva", "Retreinamento automático", "Suporte 6 meses"],
            },
          ].map((p) => (
            <div
              key={p.phase}
              className={`p-5 rounded-2xl ${
                p.highlight
                  ? "bg-apple-blue/5 border-2 border-apple-blue/20"
                  : "bg-apple-surface-1 border border-apple-separator/50"
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className={`text-[13px] font-bold ${p.highlight ? "text-apple-blue" : "text-apple-secondary"}`}>
                  {p.phase}
                </span>
                {p.badge && (
                  <span className="text-[10px] font-bold text-white bg-apple-blue px-2 py-0.5 rounded-full">
                    {p.badge}
                  </span>
                )}
              </div>
              <p className="text-[11px] text-apple-tertiary mb-2">{p.weeks}</p>
              <p className="text-[22px] font-bold text-apple-label mb-3">{p.price}</p>
              <div className="space-y-1.5">
                {p.items.map((item) => (
                  <div key={item} className="flex items-center gap-2 text-[12px]">
                    <CheckCircle size={13} className="text-apple-green flex-shrink-0" />
                    <span className="text-apple-secondary">{item}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-4 p-4 bg-apple-surface-1 rounded-xl flex items-center justify-between">
          <span className="text-[14px] font-medium text-apple-secondary">
            Investimento total (3 fases):
          </span>
          <span className="text-[22px] font-bold text-apple-green">R$ 150.000</span>
        </div>
      </div>
    </div>
  );
}
