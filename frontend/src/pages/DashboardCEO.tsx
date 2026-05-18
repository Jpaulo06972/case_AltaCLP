/**
 * AltaCLP Intelligence — Dashboard CEO
 * Apple "Stocks" / "Weather" app-inspired executive dashboard
 */

import { useQuery } from "@tanstack/react-query";
import { dashboardApi, iaApi } from "@/services/api";
import {
  TrendingDown,
  TrendingUp,
  AlertTriangle,
  DollarSign,
  Sparkles,
  Users,
  Timer,
  Loader2,
  ArrowUpRight,
  ArrowDownRight,
} from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
} from "recharts";
import { useState } from "react";

// ━━ Custom Tooltip (Apple style) ━━
function AppleTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="apple-card px-3 py-2 text-[12px] shadow-lg">
      <p className="font-semibold text-apple-label mb-1">{label}</p>
      {payload.map((p: any) => (
        <p key={p.name} style={{ color: p.color }} className="font-medium">
          {p.name}: {typeof p.value === "number" ? `R$ ${p.value.toLocaleString("pt-BR")}` : p.value}
        </p>
      ))}
    </div>
  );
}

// ━━ KPI Card Component ━━
function KPICard({
  title,
  value,
  subtitle,
  delta,
  trend,
  color,
  icon: Icon,
}: {
  title: string;
  value: string;
  subtitle?: string;
  delta?: string;
  trend?: "up" | "down";
  color: string;
  icon: any;
}) {
  const colorMap: Record<string, string> = {
    red: "bg-apple-red/10 text-apple-red",
    green: "bg-apple-green/10 text-apple-green",
    orange: "bg-apple-orange/10 text-apple-orange",
    blue: "bg-apple-blue/10 text-apple-blue",
    purple: "bg-apple-purple/10 text-apple-purple",
  };
  const iconBg = colorMap[color] || colorMap.blue;

  return (
    <div className="apple-card p-5 apple-card-interactive">
      <div className="flex items-start justify-between mb-3">
        <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${iconBg}`}>
          <Icon size={20} />
        </div>
        {delta && (
          <span
            className={`flex items-center gap-1 text-[12px] font-semibold px-2 py-0.5 rounded-full ${
              trend === "down"
                ? "bg-apple-green/10 text-apple-green"
                : "bg-apple-red/10 text-apple-red"
            }`}
          >
            {trend === "up" ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />}
            {delta}
          </span>
        )}
      </div>
      <p className="text-[12px] font-medium text-apple-tertiary mb-0.5">{title}</p>
      <p className="text-[28px] font-bold text-apple-label tracking-tight leading-tight">
        {value}
      </p>
      {subtitle && (
        <p className="text-[12px] text-apple-tertiary mt-1">{subtitle}</p>
      )}
    </div>
  );
}

export default function DashboardCEO() {
  const [aiInsight, setAiInsight] = useState<string | null>(null);
  const [aiLoading, setAiLoading] = useState(false);

  const { data, isLoading, error } = useQuery({
    queryKey: ["dashboard-ceo"],
    queryFn: () => dashboardApi.getCEO().then((r) => r.data),
    refetchInterval: 60000,
  });

  const loadAiInsight = async () => {
    setAiLoading(true);
    try {
      const res = await iaApi.analisarPlanta();
      setAiInsight(res.data.resumo_executivo || JSON.stringify(res.data));
    } catch {
      setAiInsight(
        "Análise indisponível no momento. Verifique se a chave da API Anthropic está configurada no backend."
      );
    } finally {
      setAiLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-32">
        <Loader2 className="animate-spin text-apple-blue" size={32} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="apple-card p-8 text-center">
        <AlertTriangle className="mx-auto mb-3 text-apple-orange" size={32} />
        <p className="text-apple-label font-semibold">Erro ao carregar dashboard</p>
        <p className="text-apple-tertiary text-[13px] mt-1">
          Verifique se o backend está rodando em localhost:8000
        </p>
      </div>
    );
  }

  const kpis = data?.kpis || {};
  const graficoCustos = data?.grafico_custos_6meses || [];
  const graficoFalso = data?.grafico_falso_alerta_evolucao || [];
  const alertasCriticos = data?.alertas_criticos || [];
  const roi = data?.roi_projeto || {};

  return (
    <div className="space-y-6 max-w-[1400px]">
      {/* ━━ KPI Cards Row ━━ */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Custo Visitas Falsas"
          value={`R$ ${(kpis.custo_visitas_falsas?.valor || 31400).toLocaleString("pt-BR")}`}
          subtitle="Este mês"
          delta={`+R$ ${(kpis.custo_visitas_falsas?.delta || 3400).toLocaleString("pt-BR")}`}
          trend="up"
          color="red"
          icon={DollarSign}
        />
        <KPICard
          title="Taxa Falso Alerta"
          value={`${kpis.taxa_falso_alerta?.valor || 64}%`}
          subtitle={`Meta: ${kpis.taxa_falso_alerta?.meta || 30}%`}
          delta={`+${kpis.taxa_falso_alerta?.delta || 4}%`}
          trend="up"
          color="orange"
          icon={TrendingDown}
        />
        <KPICard
          title="Backlog Comissionamento"
          value={`${kpis.maquinas_backlog?.total || 26}`}
          subtitle={`${kpis.maquinas_backlog?.com_atraso || 13} com atraso · ${kpis.maquinas_backlog?.risco_cancelamento || 4} em risco`}
          color="orange"
          icon={Timer}
        />
        <KPICard
          title="Risco Contratual"
          value={`R$ ${((kpis.risco_contratual?.valor || 780000) / 1000).toFixed(0)}k`}
          subtitle={`${kpis.risco_contratual?.cliente || "Anaclara Alimentos"} · ${kpis.risco_contratual?.prazo_dias || 44} dias`}
          color="red"
          icon={AlertTriangle}
        />
      </div>

      {/* ━━ Charts Row ━━ */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Custo de Visitas Falsas — 6 meses */}
        <div className="apple-card p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-[15px] font-semibold text-apple-label">
                Custo de Visitas Falsas
              </h3>
              <p className="text-[12px] text-apple-tertiary">Últimos 6 meses</p>
            </div>
            <span className="flex items-center gap-1 text-apple-red text-[12px] font-semibold">
              <TrendingUp size={14} />
              Subindo
            </span>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={graficoCustos} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="gradCusto" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#FF3B30" stopOpacity={0.15} />
                  <stop offset="100%" stopColor="#FF3B30" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis
                dataKey="mes"
                tick={{ fill: "#8E8E93", fontSize: 11, fontFamily: "Inter" }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                tick={{ fill: "#8E8E93", fontSize: 10, fontFamily: "Inter" }}
                axisLine={false}
                tickLine={false}
                tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`}
              />
              <Tooltip content={<AppleTooltip />} />
              <Area
                type="monotone"
                dataKey="custo"
                stroke="#FF3B30"
                strokeWidth={2.5}
                fill="url(#gradCusto)"
                dot={false}
                activeDot={{ r: 4, fill: "#FF3B30", stroke: "#fff", strokeWidth: 2 }}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Taxa de Falso Alerta — evolução */}
        <div className="apple-card p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-[15px] font-semibold text-apple-label">
                Evolução Falsos Alertas
              </h3>
              <p className="text-[12px] text-apple-tertiary">Tendência de piora</p>
            </div>
            <span className="text-[22px] font-bold text-apple-orange">64%</span>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={graficoFalso} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="gradFalso" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#FF9500" stopOpacity={0.15} />
                  <stop offset="100%" stopColor="#FF9500" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis
                dataKey="mes"
                tick={{ fill: "#8E8E93", fontSize: 11, fontFamily: "Inter" }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                tick={{ fill: "#8E8E93", fontSize: 10, fontFamily: "Inter" }}
                axisLine={false}
                tickLine={false}
                tickFormatter={(v) => `${v}%`}
                domain={[50, 70]}
              />
              <Tooltip content={<AppleTooltip />} />
              <Area
                type="monotone"
                dataKey="taxa"
                stroke="#FF9500"
                strokeWidth={2.5}
                fill="url(#gradFalso)"
                dot={false}
                activeDot={{ r: 4, fill: "#FF9500", stroke: "#fff", strokeWidth: 2 }}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* ━━ AI Insight + Alertas Críticos ━━ */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* AI Insight */}
        <div className="lg:col-span-2 apple-card p-6 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-40 h-40 bg-gradient-to-bl from-apple-purple/5 to-transparent rounded-bl-full" />
          <div className="relative">
            <div className="flex items-center gap-2.5 mb-4">
              <div className="w-8 h-8 rounded-lg ai-gradient flex items-center justify-center">
                <Sparkles size={16} className="text-white" />
              </div>
              <div>
                <h3 className="text-[15px] font-semibold text-apple-label">
                  Inteligência Operacional
                </h3>
                <p className="text-[12px] text-apple-tertiary">
                  Análise em tempo real com IA
                </p>
              </div>
            </div>

            {aiInsight ? (
              <p className="text-[14px] text-apple-secondary leading-relaxed whitespace-pre-line">
                {aiInsight}
              </p>
            ) : (
              <div>
                <p className="text-[13px] text-apple-tertiary mb-4 leading-relaxed">
                  A IA pode analisar o estado completo da operação em tempo real,
                  identificar riscos críticos e recomendar ações prioritárias
                  com estimativas de impacto financeiro.
                </p>
                <button
                  onClick={loadAiInsight}
                  disabled={aiLoading}
                  className="apple-btn apple-btn-secondary text-[13px]"
                >
                  {aiLoading ? (
                    <Loader2 size={16} className="animate-spin" />
                  ) : (
                    <Sparkles size={16} />
                  )}
                  {aiLoading ? "Analisando..." : "Gerar Análise Completa"}
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Alertas Críticos */}
        <div className="apple-card p-5">
          <h3 className="text-[15px] font-semibold text-apple-label mb-3">
            Alertas Críticos
          </h3>
          <div className="space-y-2.5">
            {alertasCriticos.length > 0 ? (
              alertasCriticos.slice(0, 5).map((alerta: any, i: number) => (
                <div
                  key={alerta.id || i}
                  className="flex items-start gap-3 p-3 rounded-xl bg-apple-surface-1/60 hover:bg-apple-surface-1 transition-colors"
                >
                  <div
                    className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${
                      alerta.severidade === "emergência" || alerta.severidade === "crítico"
                        ? "bg-apple-red"
                        : "bg-apple-orange"
                    }`}
                  />
                  <div className="min-w-0 flex-1">
                    <p className="text-[13px] font-medium text-apple-label truncate">
                      {alerta.titulo || `Alerta ${alerta.codigo_alerta}`}
                    </p>
                    <p className="text-[11px] text-apple-tertiary mt-0.5">
                      {alerta.codigo_alerta}
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-6">
                <AlertTriangle className="mx-auto mb-2 text-apple-quaternary" size={24} />
                <p className="text-[13px] text-apple-tertiary">
                  Sem alertas críticos
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ━━ ROI Summary ━━ */}
      <div className="apple-card p-6">
        <h3 className="text-[15px] font-semibold text-apple-label mb-4">
          ROI do Projeto
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {[
            {
              label: "Investimento",
              value: `R$ ${((roi.investimento || 150000) / 1000).toFixed(0)}k`,
              color: "text-apple-blue",
            },
            {
              label: "Retorno Ano 1",
              value: `R$ ${((roi.retorno_ano1 || 1320000) / 1000000).toFixed(2)}M`,
              color: "text-apple-green",
            },
            {
              label: "Múltiplo ROI",
              value: `${roi.roi_multiplo || 8.8}x`,
              color: "text-apple-green",
            },
            {
              label: "Payback",
              value: `${roi.payback_semanas || 6} semanas`,
              color: "text-apple-blue",
            },
          ].map((item) => (
            <div key={item.label} className="text-center">
              <p className="text-[12px] text-apple-tertiary font-medium mb-1">
                {item.label}
              </p>
              <p className={`text-[24px] font-bold tracking-tight ${item.color}`}>
                {item.value}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
