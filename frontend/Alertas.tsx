// AltaCLP Intelligence — Alertas & Preditiva
// Shows the false alert problem and the hybrid solution (dynamic thresholds + AI)

import { useState } from "react";
import { Activity, AlertTriangle, CheckCircle, Filter, TrendingDown } from "lucide-react";
import { machines } from "@/lib/mockData";
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer, Tooltip } from "recharts";

const thresholdData = [
  { machine: "M-VH-118", type: "Temperatura", current: 85, suggested: 95, unit: "°C", client: "Vinhal Alimentos" },
  { machine: "M-BL-042", type: "Pressão", current: 5.0, suggested: 7.5, unit: "bar", client: "Belmare Cosméticos" },
  { machine: "M-PG-077", type: "Vibração", current: 4.0, suggested: 6.5, unit: "mm/s", client: "Pampulha Papel" },
  { machine: "M-AN-201", type: "Temperatura", current: 85, suggested: 72, unit: "°C", client: "Anaclara Alimentos" },
  { machine: "M-CB-015", type: "Temperatura", current: 85, suggested: 160, unit: "°C", client: "Cubatão Sódio" },
];

const radarData = [
  { subject: "Temperatura", falso: 78, real: 22 },
  { subject: "Pressão", falso: 65, real: 35 },
  { subject: "Vibração", falso: 71, real: 29 },
  { subject: "Fluxo", falso: 55, real: 45 },
  { subject: "Corrente", falso: 48, real: 52 },
];

export default function Alertas() {
  const [activeTab, setActiveTab] = useState<"overview" | "thresholds" | "ai">("overview");

  const tabs = [
    { id: "overview", label: "Visão Geral" },
    { id: "thresholds", label: "Thresholds Dinâmicos" },
    { id: "ai", label: "Modelo de IA" },
  ] as const;

  return (
    <div className="min-h-screen">
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
          <Activity size={16} style={{ color: "#F59E0B" }} />
          <h1 className="text-sm font-semibold" style={{ color: "oklch(0.95 0.003 260)", fontFamily: "'Space Grotesk', sans-serif" }}>
            Alertas & Manutenção Preditiva
          </h1>
        </div>
        <div
          className="text-xs px-3 py-1 rounded font-semibold"
          style={{ background: "oklch(0.6 0.22 25 / 0.15)", color: "#EF4444", fontFamily: "'JetBrains Mono', monospace" }}
        >
          64% FALSOS ALARMES
        </div>
      </header>

      <div className="p-6 space-y-6">
        {/* Problem statement */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="p-5 rounded" style={{ background: "oklch(0.13 0.008 260)", border: "1px solid oklch(0.6 0.22 25 / 0.4)" }}>
            <div className="flex items-center gap-2 mb-3">
              <AlertTriangle size={14} style={{ color: "#EF4444" }} />
              <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: "#EF4444", fontFamily: "'Space Grotesk', sans-serif" }}>
                Problema Atual
              </span>
            </div>
            <div className="text-3xl font-bold mb-1" style={{ color: "#EF4444", fontFamily: "'JetBrains Mono', monospace" }}>64%</div>
            <div className="text-xs" style={{ color: "oklch(0.55 0.012 260)" }}>das visitas técnicas são falso alarme</div>
            <div className="text-2xl font-bold mt-3" style={{ color: "#EF4444", fontFamily: "'JetBrains Mono', monospace" }}>R$ 31.400</div>
            <div className="text-xs" style={{ color: "oklch(0.55 0.012 260)" }}>custo mensal em deslocamento perdido</div>
          </div>

          <div className="p-5 rounded" style={{ background: "oklch(0.13 0.008 260)", border: "1px solid oklch(0.75 0.18 80 / 0.4)" }}>
            <div className="flex items-center gap-2 mb-3">
              <Filter size={14} style={{ color: "#F59E0B" }} />
              <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: "#F59E0B", fontFamily: "'Space Grotesk', sans-serif" }}>
                Fase 1: Thresholds Dinâmicos
              </span>
            </div>
            <div className="text-3xl font-bold mb-1" style={{ color: "#F59E0B", fontFamily: "'JetBrains Mono', monospace" }}>-30%</div>
            <div className="text-xs" style={{ color: "oklch(0.55 0.012 260)" }}>redução imediata · 1 semana de trabalho</div>
            <div className="text-2xl font-bold mt-3" style={{ color: "#F59E0B", fontFamily: "'JetBrains Mono', monospace" }}>R$ 9.420</div>
            <div className="text-xs" style={{ color: "oklch(0.55 0.012 260)" }}>economia mensal · sem IA</div>
          </div>

          <div className="p-5 rounded" style={{ background: "oklch(0.13 0.008 260)", border: "1px solid oklch(0.65 0.17 160 / 0.4)" }}>
            <div className="flex items-center gap-2 mb-3">
              <CheckCircle size={14} style={{ color: "#10B981" }} />
              <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: "#10B981", fontFamily: "'Space Grotesk', sans-serif" }}>
                Fase 3: IA Preditiva
              </span>
            </div>
            <div className="text-3xl font-bold mb-1" style={{ color: "#10B981", fontFamily: "'JetBrains Mono', monospace" }}>-65%</div>
            <div className="text-xs" style={{ color: "oklch(0.55 0.012 260)" }}>redução total · 12 semanas</div>
            <div className="text-2xl font-bold mt-3" style={{ color: "#10B981", fontFamily: "'JetBrains Mono', monospace" }}>R$ 20.410</div>
            <div className="text-xs" style={{ color: "oklch(0.55 0.012 260)" }}>economia mensal em regime pleno</div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 p-1 rounded" style={{ background: "oklch(0.13 0.008 260)", border: "1px solid oklch(0.22 0.008 260)", width: "fit-content" }}>
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className="px-4 py-2 rounded text-xs font-semibold transition-all duration-150"
              style={{
                background: activeTab === tab.id ? "#F59E0B" : "transparent",
                color: activeTab === tab.id ? "oklch(0.1 0.008 260)" : "oklch(0.55 0.012 260)",
                fontFamily: "'Space Grotesk', sans-serif",
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {activeTab === "overview" && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Radar chart */}
            <div className="p-5 rounded" style={{ background: "oklch(0.13 0.008 260)", border: "1px solid oklch(0.22 0.008 260)" }}>
              <h3 className="text-sm font-semibold mb-1" style={{ color: "oklch(0.95 0.003 260)", fontFamily: "'Space Grotesk', sans-serif" }}>
                Taxa de Falsos por Tipo de Sensor
              </h3>
              <p className="text-xs mb-4" style={{ color: "oklch(0.55 0.012 260)" }}>
                Temperatura e vibração são os maiores geradores de falsos alarmes
              </p>
              <ResponsiveContainer width="100%" height={220}>
                <RadarChart data={radarData}>
                  <PolarGrid stroke="oklch(0.22 0.008 260)" />
                  <PolarAngleAxis
                    dataKey="subject"
                    tick={{ fill: "oklch(0.55 0.012 260)", fontSize: 10, fontFamily: "'JetBrains Mono', monospace" }}
                  />
                  <Radar name="Falsos %" dataKey="falso" stroke="#EF4444" fill="#EF4444" fillOpacity={0.2} />
                  <Radar name="Reais %" dataKey="real" stroke="#10B981" fill="#10B981" fillOpacity={0.2} />
                  <Tooltip
                    contentStyle={{
                      background: "oklch(0.16 0.008 260)",
                      border: "1px solid oklch(0.22 0.008 260)",
                      fontFamily: "'JetBrains Mono', monospace",
                      fontSize: "11px",
                      color: "oklch(0.85 0.005 260)",
                    }}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </div>

            {/* Machine list with alert rates */}
            <div className="p-5 rounded" style={{ background: "oklch(0.13 0.008 260)", border: "1px solid oklch(0.22 0.008 260)" }}>
              <h3 className="text-sm font-semibold mb-4" style={{ color: "oklch(0.95 0.003 260)", fontFamily: "'Space Grotesk', sans-serif" }}>
                Máquinas por Taxa de Falso Alarme
              </h3>
              <div className="space-y-3">
                {machines
                  .filter((m) => m.falseAlertRate > 0)
                  .sort((a, b) => b.falseAlertRate - a.falseAlertRate)
                  .map((m) => (
                    <div key={m.id}>
                      <div className="flex items-center justify-between mb-1">
                        <div>
                          <span className="text-xs font-bold" style={{ color: "#F59E0B", fontFamily: "'JetBrains Mono', monospace" }}>
                            {m.id}
                          </span>
                          <span className="text-xs ml-2" style={{ color: "oklch(0.65 0.008 260)", fontFamily: "'Space Grotesk', sans-serif" }}>
                            {m.client}
                          </span>
                        </div>
                        <span
                          className="text-xs font-bold"
                          style={{
                            color: m.falseAlertRate > 70 ? "#EF4444" : m.falseAlertRate > 50 ? "#F59E0B" : "#10B981",
                            fontFamily: "'JetBrains Mono', monospace",
                          }}
                        >
                          {m.falseAlertRate}%
                        </span>
                      </div>
                      <div className="h-1.5 rounded-full overflow-hidden" style={{ background: "oklch(0.18 0.008 260)" }}>
                        <div
                          className="h-full rounded-full"
                          style={{
                            width: `${m.falseAlertRate}%`,
                            background: m.falseAlertRate > 70 ? "#EF4444" : m.falseAlertRate > 50 ? "#F59E0B" : "#10B981",
                          }}
                        />
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === "thresholds" && (
          <div className="rounded overflow-hidden" style={{ background: "oklch(0.13 0.008 260)", border: "1px solid oklch(0.22 0.008 260)" }}>
            <div className="px-5 py-3 border-b" style={{ borderColor: "oklch(0.18 0.008 260)" }}>
              <h3 className="text-sm font-semibold" style={{ color: "oklch(0.95 0.003 260)", fontFamily: "'Space Grotesk', sans-serif" }}>
                Ajuste de Thresholds por Máquina
              </h3>
              <p className="text-xs mt-0.5" style={{ color: "oklch(0.55 0.012 260)" }}>
                Thresholds genéricos causam 64% dos falsos alarmes. Ajuste contextualizado reduz 30% imediatamente.
              </p>
            </div>
            <table className="w-full text-xs">
              <thead>
                <tr style={{ borderBottom: "1px solid oklch(0.18 0.008 260)" }}>
                  {["Máquina", "Cliente", "Sensor", "Threshold Atual (Genérico)", "Threshold Sugerido (Contextual)", "Impacto"].map((h) => (
                    <th key={h} className="px-4 py-3 text-left font-semibold uppercase tracking-wider"
                      style={{ color: "oklch(0.4 0.01 260)", fontFamily: "'Space Grotesk', sans-serif", fontSize: "10px" }}>
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {thresholdData.map((t, i) => (
                  <tr key={i} className="hover:bg-[oklch(0.16_0.008_260)] transition-colors"
                    style={{ borderBottom: i < thresholdData.length - 1 ? "1px solid oklch(0.16 0.008 260)" : "none" }}>
                    <td className="px-4 py-3 font-bold" style={{ color: "#F59E0B", fontFamily: "'JetBrains Mono', monospace" }}>{t.machine}</td>
                    <td className="px-4 py-3" style={{ color: "oklch(0.75 0.008 260)", fontFamily: "'Space Grotesk', sans-serif" }}>{t.client}</td>
                    <td className="px-4 py-3" style={{ color: "oklch(0.65 0.008 260)", fontFamily: "'Space Grotesk', sans-serif" }}>{t.type}</td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-1 rounded" style={{ background: "oklch(0.6 0.22 25 / 0.15)", color: "#EF4444", fontFamily: "'JetBrains Mono', monospace" }}>
                        {t.current} {t.unit}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-1 rounded" style={{ background: "oklch(0.65 0.17 160 / 0.15)", color: "#10B981", fontFamily: "'JetBrains Mono', monospace" }}>
                        {t.suggested} {t.unit}
                      </span>
                    </td>
                    <td className="px-4 py-3" style={{ color: "#10B981", fontFamily: "'JetBrains Mono', monospace" }}>
                      ~{Math.round(Math.abs(t.suggested - t.current) / t.current * 100 * 0.4)}% menos falsos
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === "ai" && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="p-5 rounded" style={{ background: "oklch(0.13 0.008 260)", border: "1px solid oklch(0.22 0.008 260)" }}>
              <h3 className="text-sm font-semibold mb-3" style={{ color: "oklch(0.95 0.003 260)", fontFamily: "'Space Grotesk', sans-serif" }}>
                Modelo de IA: Isolation Forest
              </h3>
              <div className="space-y-3 text-xs" style={{ color: "oklch(0.75 0.008 260)", fontFamily: "'Space Grotesk', sans-serif", lineHeight: "1.6" }}>
                <p>O modelo de <strong style={{ color: "oklch(0.85 0.005 260)" }}>Anomaly Detection</strong> aprende o padrão normal de cada máquina individualmente, considerando contexto de turno, temperatura ambiente e histórico de manutenção.</p>
                <p>Diferente de thresholds fixos, o modelo detecta <strong style={{ color: "#F59E0B" }}>combinações anômalas</strong> de sensores — ex: temperatura 78°C é normal, mas temperatura 78°C + vibração 6mm/s + pressão 4.2bar simultaneamente é anomalia real.</p>
                <div className="p-3 rounded mt-2" style={{ background: "oklch(0.75 0.18 80 / 0.08)", border: "1px solid oklch(0.75 0.18 80 / 0.2)" }}>
                  <div className="font-semibold mb-1" style={{ color: "#F59E0B" }}>Limitação atual dos dados</div>
                  <p style={{ color: "oklch(0.65 0.008 260)" }}>Labels de incidente a 50% de completude. Por isso, a Fase 1 usa thresholds dinâmicos (sem IA) para ganho imediato enquanto coletamos dados limpos para treinar o modelo.</p>
                </div>
              </div>
            </div>
            <div className="p-5 rounded" style={{ background: "oklch(0.13 0.008 260)", border: "1px solid oklch(0.22 0.008 260)" }}>
              <h3 className="text-sm font-semibold mb-3" style={{ color: "oklch(0.95 0.003 260)", fontFamily: "'Space Grotesk', sans-serif" }}>
                Cronograma de Treinamento
              </h3>
              <div className="space-y-3">
                {[
                  { week: "Sem 1-4", task: "Thresholds dinâmicos ativos. Coleta de labels limpos.", status: "active" },
                  { week: "Sem 5-8", task: "Baseline de dados suficiente. Treinamento inicial do Isolation Forest.", status: "pending" },
                  { week: "Sem 9-12", task: "Deploy do modelo. A/B test vs. thresholds. Ajuste de hiperparâmetros.", status: "pending" },
                  { week: "Mês 4+", task: "Modelo em produção. Retreinamento mensal automático.", status: "future" },
                ].map((item) => (
                  <div key={item.week} className="flex gap-3">
                    <div className="flex flex-col items-center">
                      <div className="w-2 h-2 rounded-full flex-shrink-0 mt-0.5"
                        style={{ background: item.status === "active" ? "#F59E0B" : item.status === "pending" ? "oklch(0.3 0.008 260)" : "oklch(0.22 0.008 260)" }} />
                      {item.week !== "Mês 4+" && <div className="w-px flex-1 mt-1" style={{ background: "oklch(0.22 0.008 260)" }} />}
                    </div>
                    <div className="pb-3">
                      <div className="text-xs font-bold mb-0.5" style={{ color: item.status === "active" ? "#F59E0B" : "oklch(0.55 0.012 260)", fontFamily: "'JetBrains Mono', monospace" }}>
                        {item.week}
                      </div>
                      <div className="text-xs" style={{ color: "oklch(0.65 0.008 260)", fontFamily: "'Space Grotesk', sans-serif" }}>
                        {item.task}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
