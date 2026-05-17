// AltaCLP Intelligence — Command Center (Home Dashboard)
// Design: Industrial Precision — High-density operational overview
// Primary users: Marcos Tedesco (CEO), Roberto (CFO), Cláudia Santarém (Eng)

import { useState, useEffect } from "react";
import {
  AlertTriangle,
  ArrowDown,
  ArrowUp,
  CheckCircle,
  Clock,
  GitBranch,
  TrendingDown,
  TrendingUp,
  Wrench,
  Zap,
  Activity,
  DollarSign,
} from "lucide-react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell,
} from "recharts";
import {
  kpiData,
  machines,
  incidents,
  alertTrendData,
  savingsProjection,
  teamData,
} from "@/lib/mockData";
import { cn } from "@/lib/utils";

// Animated counter hook
function useCounter(target: number, duration = 800) {
  const [value, setValue] = useState(0);
  useEffect(() => {
    let start = 0;
    const step = target / (duration / 16);
    const timer = setInterval(() => {
      start += step;
      if (start >= target) {
        setValue(target);
        clearInterval(timer);
      } else {
        setValue(Math.floor(start));
      }
    }, 16);
    return () => clearInterval(timer);
  }, [target, duration]);
  return value;
}

function KpiCard({
  label,
  value,
  unit,
  trend,
  trendValue,
  status,
  sublabel,
  icon: Icon,
  animate = true,
}: {
  label: string;
  value: number | string;
  unit?: string;
  trend?: "up" | "down" | "neutral";
  trendValue?: string;
  status: "critical" | "warning" | "ok" | "neutral";
  sublabel?: string;
  icon: React.ElementType;
  animate?: boolean;
}) {
  const animatedValue = useCounter(typeof value === "number" ? value : 0, 900);
  const displayValue = animate && typeof value === "number" ? animatedValue : value;

  const statusColors = {
    critical: { border: "#EF4444", glow: "oklch(0.6 0.22 25 / 0.15)" },
    warning: { border: "#F59E0B", glow: "oklch(0.75 0.18 80 / 0.15)" },
    ok: { border: "#10B981", glow: "oklch(0.65 0.17 160 / 0.15)" },
    neutral: { border: "oklch(0.22 0.008 260)", glow: "transparent" },
  };

  const colors = statusColors[status];

  return (
    <div
      className="relative p-5 rounded overflow-hidden transition-all duration-200 hover:translate-y-[-1px]"
      style={{
        background: "oklch(0.13 0.008 260)",
        border: `1px solid ${colors.border}`,
        boxShadow: `0 0 20px ${colors.glow}, 0 1px 3px oklch(0 0 0 / 0.3)`,
      }}
    >
      <div
        className="absolute left-0 top-0 bottom-0 w-[3px]"
        style={{ background: colors.border }}
      />
      <div className="flex items-start justify-between mb-3">
        <span
          className="text-xs font-semibold uppercase tracking-wider"
          style={{ color: "oklch(0.55 0.012 260)", fontFamily: "'Space Grotesk', sans-serif" }}
        >
          {label}
        </span>
        <Icon size={16} style={{ color: colors.border }} />
      </div>
      <div className="flex items-end gap-2">
        <span
          className="text-4xl font-bold leading-none"
          style={{
            fontFamily: "'JetBrains Mono', monospace",
            color: "oklch(0.95 0.003 260)",
          }}
        >
          {typeof displayValue === "number"
            ? displayValue.toLocaleString("pt-BR")
            : displayValue}
        </span>
        {unit && (
          <span
            className="text-lg font-medium mb-0.5"
            style={{ color: "oklch(0.55 0.012 260)", fontFamily: "'JetBrains Mono', monospace" }}
          >
            {unit}
          </span>
        )}
      </div>
      {sublabel && (
        <div
          className="text-xs mt-1"
          style={{ color: "oklch(0.55 0.012 260)" }}
        >
          {sublabel}
        </div>
      )}
      {trend && trendValue && (
        <div className="flex items-center gap-1 mt-2">
          {trend === "up" ? (
            <ArrowUp size={12} style={{ color: "#EF4444" }} />
          ) : (
            <ArrowDown size={12} style={{ color: "#10B981" }} />
          )}
          <span
            className="text-xs font-medium"
            style={{
              color: trend === "up" ? "#EF4444" : "#10B981",
              fontFamily: "'JetBrains Mono', monospace",
            }}
          >
            {trendValue}
          </span>
        </div>
      )}
    </div>
  );
}

function StatusDot({ status }: { status: "critical" | "warning" | "ok" | "offline" }) {
  const colors = {
    critical: "#EF4444",
    warning: "#F59E0B",
    ok: "#10B981",
    offline: "oklch(0.4 0.01 260)",
  };
  return (
    <span
      className={cn("inline-block w-2 h-2 rounded-full flex-shrink-0", {
        "status-dot critical": status === "critical",
        "status-dot warning": status === "warning",
        "status-dot ok": status === "ok",
      })}
      style={{ background: colors[status] }}
    />
  );
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div
        className="p-3 rounded text-xs"
        style={{
          background: "oklch(0.16 0.008 260)",
          border: "1px solid oklch(0.22 0.008 260)",
          fontFamily: "'JetBrains Mono', monospace",
          color: "oklch(0.85 0.005 260)",
        }}
      >
        <div className="font-semibold mb-1">{label}</div>
        {payload.map((p: any) => (
          <div key={p.name} style={{ color: p.color }}>
            {p.name}: {p.value}
          </div>
        ))}
      </div>
    );
  }
  return null;
};

export default function Home() {
  const unresolvedIncidents = incidents.filter((i) => !i.resolved);
  const criticalMachines = machines.filter((m) => m.status === "critical");
  const divergentMachines = machines.filter((m) => m.codeSync === "divergent");

  return (
    <div className="min-h-screen grid-bg">
      {/* Header */}
      <header
        className="sticky top-0 z-10 flex items-center justify-between px-6 h-14 border-b"
        style={{
          background: "oklch(0.11 0.008 260 / 0.95)",
          borderColor: "oklch(0.18 0.008 260)",
          backdropFilter: "blur(8px)",
        }}
      >
        <div className="flex items-center gap-3">
          <h1
            className="text-sm font-semibold"
            style={{ color: "oklch(0.95 0.003 260)", fontFamily: "'Space Grotesk', sans-serif" }}
          >
            Command Center
          </h1>
          <span
            className="text-xs px-2 py-0.5 rounded"
            style={{
              background: "oklch(0.75 0.18 80 / 0.15)",
              color: "#F59E0B",
              fontFamily: "'JetBrains Mono', monospace",
            }}
          >
            AO VIVO
          </span>
        </div>
        <div className="flex items-center gap-4">
          <div
            className="text-xs"
            style={{ color: "oklch(0.55 0.012 260)", fontFamily: "'JetBrains Mono', monospace" }}
          >
            17/05/2026 · 14:32:07
          </div>
          {unresolvedIncidents.length > 0 && (
            <div
              className="flex items-center gap-1.5 px-3 py-1 rounded text-xs font-semibold"
              style={{
                background: "oklch(0.6 0.22 25 / 0.15)",
                border: "1px solid oklch(0.6 0.22 25 / 0.4)",
                color: "#EF4444",
                fontFamily: "'Space Grotesk', sans-serif",
              }}
            >
              <AlertTriangle size={12} />
              {unresolvedIncidents.length} incidentes ativos
            </div>
          )}
        </div>
      </header>

      <div className="p-6 space-y-6">
        {/* Critical Alert Banner */}
        <div
          className="flex items-center gap-4 p-4 rounded"
          style={{
            background: "oklch(0.6 0.22 25 / 0.08)",
            border: "1px solid oklch(0.6 0.22 25 / 0.3)",
          }}
        >
          <AlertTriangle size={18} style={{ color: "#EF4444", flexShrink: 0 }} />
          <div className="flex-1 min-w-0">
            <span
              className="text-sm font-semibold"
              style={{ color: "#EF4444", fontFamily: "'Space Grotesk', sans-serif" }}
            >
              Risco Crítico:
            </span>{" "}
            <span
              className="text-sm"
              style={{ color: "oklch(0.85 0.005 260)", fontFamily: "'Space Grotesk', sans-serif" }}
            >
              Contrato Anaclara Alimentos — R$ 780.000 em risco. Prazo de entrega: 30/05/2026 (13 dias).
              Backlog atual impossibilita entrega sem intervenção imediata.
            </span>
          </div>
          <button
            className="flex-shrink-0 text-xs px-3 py-1.5 rounded font-semibold transition-opacity hover:opacity-80"
            style={{
              background: "#EF4444",
              color: "white",
              fontFamily: "'Space Grotesk', sans-serif",
            }}
          >
            Ver Plano
          </button>
        </div>

        {/* KPI Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <KpiCard
            label="Falsos Alertas"
            value={64}
            unit="%"
            trend="up"
            trendValue="+4pp vs. Q1"
            status="critical"
            sublabel="R$ 31.400/mês em visitas perdidas"
            icon={Activity}
          />
          <KpiCard
            label="Backlog Comissionamento"
            value={26}
            unit=" máq."
            trend="up"
            trendValue="+4 esta semana"
            status="critical"
            sublabel="13 com atraso contratual"
            icon={Wrench}
          />
          <KpiCard
            label="Drift de Código"
            value={8}
            unit=" máq."
            trend="up"
            trendValue="4 incidentes/ano"
            status="warning"
            sublabel="R$ 250k em prejuízo acumulado"
            icon={GitBranch}
          />
          <KpiCard
            label="NPS Operacional"
            value={68}
            trend="down"
            trendValue="-14 pts em 18 meses"
            status="warning"
            sublabel="Era 82 em nov/2024"
            icon={TrendingDown}
          />
        </div>

        {/* Second row KPIs */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <KpiCard
            label="Receita em Risco"
            value={780000}
            unit=""
            status="critical"
            sublabel="Anaclara Alimentos · jun/2026"
            icon={DollarSign}
            animate={false}
          />
          <KpiCard
            label="Custo Mensal Visitas"
            value={31400}
            unit=""
            status="warning"
            sublabel="R$/mês · +16% vs. Q1"
            icon={TrendingUp}
            animate={false}
          />
          <KpiCard
            label="Máquinas em Campo"
            value={50}
            unit=" total"
            status="neutral"
            sublabel={`${criticalMachines.length} críticas · ${divergentMachines.length} com drift`}
            icon={Activity}
          />
          <KpiCard
            label="Cotação Técnica"
            value={6}
            unit=" dias"
            status="warning"
            sublabel="Mecasul entrega em 24h"
            icon={Zap}
          />
        </div>

        {/* Main content grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Alert trend chart */}
          <div
            className="lg:col-span-2 p-5 rounded"
            style={{
              background: "oklch(0.13 0.008 260)",
              border: "1px solid oklch(0.22 0.008 260)",
            }}
          >
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2
                  className="text-sm font-semibold"
                  style={{ color: "oklch(0.95 0.003 260)", fontFamily: "'Space Grotesk', sans-serif" }}
                >
                  Histórico de Alertas
                </h2>
                <p className="text-xs mt-0.5" style={{ color: "oklch(0.55 0.012 260)" }}>
                  Alertas totais vs. falsos alarmes (últimos 7 meses)
                </p>
              </div>
              <div className="flex items-center gap-4 text-xs" style={{ fontFamily: "'JetBrains Mono', monospace" }}>
                <span className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full" style={{ background: "#EF4444" }} />
                  <span style={{ color: "oklch(0.55 0.012 260)" }}>Falsos</span>
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full" style={{ background: "#10B981" }} />
                  <span style={{ color: "oklch(0.55 0.012 260)" }}>Reais</span>
                </span>
              </div>
            </div>
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={alertTrendData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="falseGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#EF4444" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#EF4444" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="realGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10B981" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.22 0.008 260)" strokeOpacity={0.5} />
                <XAxis
                  dataKey="month"
                  tick={{ fill: "oklch(0.45 0.01 260)", fontSize: 10, fontFamily: "'JetBrains Mono', monospace" }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fill: "oklch(0.45 0.01 260)", fontSize: 10, fontFamily: "'JetBrains Mono', monospace" }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip content={<CustomTooltip />} />
                <Area
                  type="monotone"
                  dataKey="false"
                  name="Falsos"
                  stroke="#EF4444"
                  strokeWidth={2}
                  fill="url(#falseGrad)"
                />
                <Area
                  type="monotone"
                  dataKey="real"
                  name="Reais"
                  stroke="#10B981"
                  strokeWidth={2}
                  fill="url(#realGrad)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Team workload */}
          <div
            className="p-5 rounded"
            style={{
              background: "oklch(0.13 0.008 260)",
              border: "1px solid oklch(0.22 0.008 260)",
            }}
          >
            <h2
              className="text-sm font-semibold mb-1"
              style={{ color: "oklch(0.95 0.003 260)", fontFamily: "'Space Grotesk', sans-serif" }}
            >
              Carga da Engenharia
            </h2>
            <p className="text-xs mb-4" style={{ color: "oklch(0.55 0.012 260)" }}>
              4 engenheiros · backlog 26 máquinas
            </p>
            <div className="space-y-4">
              {teamData.map((member) => {
                const barColor =
                  member.workload >= 90
                    ? "#EF4444"
                    : member.workload >= 80
                    ? "#F59E0B"
                    : "#10B981";
                return (
                  <div key={member.name}>
                    <div className="flex items-center justify-between mb-1.5">
                      <div>
                        <div
                          className="text-xs font-semibold"
                          style={{ color: "oklch(0.85 0.005 260)", fontFamily: "'Space Grotesk', sans-serif" }}
                        >
                          {member.name.split(" ")[0]}
                        </div>
                        <div className="text-xs" style={{ color: "oklch(0.45 0.01 260)" }}>
                          {member.role}
                        </div>
                      </div>
                      <span
                        className="text-sm font-bold"
                        style={{ color: barColor, fontFamily: "'JetBrains Mono', monospace" }}
                      >
                        {member.workload}%
                      </span>
                    </div>
                    <div
                      className="h-1.5 rounded-full overflow-hidden"
                      style={{ background: "oklch(0.18 0.008 260)" }}
                    >
                      <div
                        className="h-full rounded-full transition-all duration-700"
                        style={{ width: `${member.workload}%`, background: barColor }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
            <div
              className="mt-4 p-3 rounded text-xs"
              style={{
                background: "oklch(0.6 0.22 25 / 0.08)",
                border: "1px solid oklch(0.6 0.22 25 / 0.2)",
                color: "#EF4444",
                fontFamily: "'Space Grotesk', sans-serif",
              }}
            >
              Júnior Almeida pediu demissão. Risco de concentração de conhecimento.
            </div>
          </div>
        </div>

        {/* Machines table + Incidents */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Machines list */}
          <div
            className="lg:col-span-2 rounded overflow-hidden"
            style={{
              background: "oklch(0.13 0.008 260)",
              border: "1px solid oklch(0.22 0.008 260)",
            }}
          >
            <div
              className="flex items-center justify-between px-5 py-3 border-b"
              style={{ borderColor: "oklch(0.18 0.008 260)" }}
            >
              <h2
                className="text-sm font-semibold"
                style={{ color: "oklch(0.95 0.003 260)", fontFamily: "'Space Grotesk', sans-serif" }}
              >
                Máquinas em Campo
              </h2>
              <span
                className="text-xs px-2 py-0.5 rounded"
                style={{
                  background: "oklch(0.18 0.008 260)",
                  color: "oklch(0.55 0.012 260)",
                  fontFamily: "'JetBrains Mono', monospace",
                }}
              >
                {machines.length} ativos
              </span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr style={{ borderBottom: "1px solid oklch(0.18 0.008 260)" }}>
                    {["ID", "Máquina / Cliente", "Status", "Alertas 30d", "Falsos", "Código", "Última Visita"].map(
                      (h) => (
                        <th
                          key={h}
                          className="px-4 py-2.5 text-left font-semibold uppercase tracking-wider"
                          style={{
                            color: "oklch(0.4 0.01 260)",
                            fontFamily: "'Space Grotesk', sans-serif",
                            fontSize: "10px",
                          }}
                        >
                          {h}
                        </th>
                      )
                    )}
                  </tr>
                </thead>
                <tbody>
                  {machines.map((m, i) => (
                    <tr
                      key={m.id}
                      className="transition-colors hover:bg-[oklch(0.16_0.008_260)]"
                      style={{
                        borderBottom: i < machines.length - 1 ? "1px solid oklch(0.16 0.008 260)" : "none",
                      }}
                    >
                      <td
                        className="px-4 py-3 font-medium"
                        style={{ color: "#F59E0B", fontFamily: "'JetBrains Mono', monospace" }}
                      >
                        {m.id}
                      </td>
                      <td className="px-4 py-3">
                        <div
                          className="font-medium"
                          style={{ color: "oklch(0.85 0.005 260)", fontFamily: "'Space Grotesk', sans-serif" }}
                        >
                          {m.name}
                        </div>
                        <div style={{ color: "oklch(0.45 0.01 260)" }}>{m.client}</div>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <StatusDot status={m.status} />
                          <span
                            style={{
                              color:
                                m.status === "critical"
                                  ? "#EF4444"
                                  : m.status === "warning"
                                  ? "#F59E0B"
                                  : m.status === "ok"
                                  ? "#10B981"
                                  : "oklch(0.4 0.01 260)",
                              fontFamily: "'JetBrains Mono', monospace",
                              textTransform: "capitalize",
                            }}
                          >
                            {m.status}
                          </span>
                        </div>
                      </td>
                      <td
                        className="px-4 py-3 font-bold"
                        style={{
                          color: m.alertCount30d > 10 ? "#EF4444" : m.alertCount30d > 5 ? "#F59E0B" : "#10B981",
                          fontFamily: "'JetBrains Mono', monospace",
                        }}
                      >
                        {m.alertCount30d}
                      </td>
                      <td
                        className="px-4 py-3"
                        style={{
                          color: m.falseAlertRate > 70 ? "#EF4444" : m.falseAlertRate > 50 ? "#F59E0B" : "#10B981",
                          fontFamily: "'JetBrains Mono', monospace",
                        }}
                      >
                        {m.falseAlertRate > 0 ? `${m.falseAlertRate}%` : "—"}
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className="px-2 py-0.5 rounded text-xs font-medium"
                          style={{
                            background:
                              m.codeSync === "divergent"
                                ? "oklch(0.6 0.22 25 / 0.15)"
                                : m.codeSync === "ok"
                                ? "oklch(0.65 0.17 160 / 0.15)"
                                : "oklch(0.4 0.01 260 / 0.3)",
                            color:
                              m.codeSync === "divergent"
                                ? "#EF4444"
                                : m.codeSync === "ok"
                                ? "#10B981"
                                : "oklch(0.55 0.012 260)",
                            fontFamily: "'JetBrains Mono', monospace",
                          }}
                        >
                          {m.codeSync === "divergent" ? "DRIFT" : m.codeSync === "ok" ? "SYNC" : "?"}
                        </span>
                      </td>
                      <td
                        className="px-4 py-3"
                        style={{ color: "oklch(0.55 0.012 260)", fontFamily: "'JetBrains Mono', monospace" }}
                      >
                        {m.lastVisit}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Recent incidents */}
          <div
            className="rounded overflow-hidden"
            style={{
              background: "oklch(0.13 0.008 260)",
              border: "1px solid oklch(0.22 0.008 260)",
            }}
          >
            <div
              className="flex items-center justify-between px-5 py-3 border-b"
              style={{ borderColor: "oklch(0.18 0.008 260)" }}
            >
              <h2
                className="text-sm font-semibold"
                style={{ color: "oklch(0.95 0.003 260)", fontFamily: "'Space Grotesk', sans-serif" }}
              >
                Incidentes Recentes
              </h2>
              <span
                className="text-xs px-2 py-0.5 rounded"
                style={{
                  background: "oklch(0.6 0.22 25 / 0.15)",
                  color: "#EF4444",
                  fontFamily: "'JetBrains Mono', monospace",
                }}
              >
                {unresolvedIncidents.length} abertos
              </span>
            </div>
            <div className="divide-y" style={{ borderColor: "oklch(0.16 0.008 260)" }}>
              {incidents.map((inc) => (
                <div
                  key={inc.id}
                  className="px-5 py-4 hover:bg-[oklch(0.16_0.008_260)] transition-colors"
                  style={{ borderColor: "oklch(0.16 0.008 260)" }}
                >
                  <div className="flex items-start gap-3">
                    <div
                      className="w-1.5 h-1.5 rounded-full mt-1.5 flex-shrink-0"
                      style={{
                        background:
                          inc.severity === "critical"
                            ? "#EF4444"
                            : inc.severity === "high"
                            ? "#F59E0B"
                            : "#10B981",
                      }}
                    />
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span
                          className="text-xs font-bold"
                          style={{ color: "#F59E0B", fontFamily: "'JetBrains Mono', monospace" }}
                        >
                          {inc.id}
                        </span>
                        {!inc.resolved && (
                          <span
                            className="text-xs px-1.5 py-0.5 rounded"
                            style={{
                              background: "oklch(0.6 0.22 25 / 0.15)",
                              color: "#EF4444",
                              fontFamily: "'JetBrains Mono', monospace",
                            }}
                          >
                            ABERTO
                          </span>
                        )}
                      </div>
                      <p
                        className="text-xs leading-relaxed mb-1"
                        style={{ color: "oklch(0.75 0.008 260)", fontFamily: "'Space Grotesk', sans-serif" }}
                      >
                        {inc.description.substring(0, 80)}...
                      </p>
                      <div className="flex items-center gap-3">
                        <span
                          className="text-xs"
                          style={{ color: "oklch(0.45 0.01 260)", fontFamily: "'JetBrains Mono', monospace" }}
                        >
                          {inc.date}
                        </span>
                        {inc.loss > 0 && (
                          <span
                            className="text-xs font-semibold"
                            style={{ color: "#EF4444", fontFamily: "'JetBrains Mono', monospace" }}
                          >
                            R$ {inc.loss.toLocaleString("pt-BR")}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Savings projection */}
        <div
          className="p-5 rounded"
          style={{
            background: "oklch(0.13 0.008 260)",
            border: "1px solid oklch(0.22 0.008 260)",
          }}
        >
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2
                className="text-sm font-semibold"
                style={{ color: "oklch(0.95 0.003 260)", fontFamily: "'Space Grotesk', sans-serif" }}
              >
                Projeção de Economia — Plataforma HomoDeus
              </h2>
              <p className="text-xs mt-0.5" style={{ color: "oklch(0.55 0.012 260)" }}>
                Acumulado ao longo das 3 fases de implementação (12 semanas)
              </p>
            </div>
            <div
              className="text-right"
              style={{ fontFamily: "'JetBrains Mono', monospace" }}
            >
              <div className="text-2xl font-bold" style={{ color: "#10B981" }}>
                R$ 1,32M
              </div>
              <div className="text-xs" style={{ color: "oklch(0.55 0.012 260)" }}>
                economia/ano em regime pleno
              </div>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={160}>
            <BarChart data={savingsProjection} margin={{ top: 0, right: 0, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.18 0.008 260)" strokeOpacity={0.5} />
              <XAxis
                dataKey="phase"
                tick={{ fill: "oklch(0.45 0.01 260)", fontSize: 9, fontFamily: "'JetBrains Mono', monospace" }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                tick={{ fill: "oklch(0.45 0.01 260)", fontSize: 9, fontFamily: "'JetBrains Mono', monospace" }}
                axisLine={false}
                tickLine={false}
                tickFormatter={(v) => `R$${(v / 1000).toFixed(0)}k`}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="accumulated" name="Economia Acumulada" radius={[3, 3, 0, 0]}>
                {savingsProjection.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={index === 0 ? "oklch(0.22 0.008 260)" : `oklch(${0.5 + index * 0.04} 0.17 160)`}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Footer */}
        <div
          className="flex items-center justify-between py-4 border-t text-xs"
          style={{
            borderColor: "oklch(0.18 0.008 260)",
            color: "oklch(0.4 0.01 260)",
            fontFamily: "'JetBrains Mono', monospace",
          }}
        >
          <span>AltaCLP Intelligence · MVP v0.1 · HomoDeus</span>
          <span>Dados simulados com base em levantamento real · 17/05/2026</span>
        </div>
      </div>
    </div>
  );
}
