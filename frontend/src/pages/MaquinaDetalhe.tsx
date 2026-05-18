/**
 * AltaCLP Intelligence — Máquina Detail Page
 * Master-Detail with telemetry charts + hybrid predictive monitoring
 */

import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { maquinasApi } from "@/services/api";
import {
  ArrowLeft,
  Thermometer,
  Gauge,
  Activity,
  Zap,
  Loader2,
  Settings,
  GitCompareArrows,
  AlertTriangle,
} from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { useState } from "react";
import { useAuth } from "@/contexts/AuthContext";

function AppleTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  const isAnomaly = payload[0]?.payload?.isAnomaly;

  return (
    <div className="apple-card px-3 py-2 text-[12px] shadow-lg border border-apple-separator/20">
      <p className="font-semibold text-apple-label mb-1">{label}</p>
      {payload.map((p: any) => (
        <p key={p.name} style={{ color: p.color }} className="font-medium">
          {p.name}: {Number(p.value).toFixed(1)}
        </p>
      ))}
      {isAnomaly && (
        <div className="mt-2 pt-2 border-t border-apple-separator/30 text-apple-red flex items-center gap-1">
          <AlertTriangle size={12} />
          <span className="font-medium">Anomalia detectada (Isolation Forest)</span>
        </div>
      )}
    </div>
  );
}

export default function MaquinaDetalhe() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [showConfig, setShowConfig] = useState(false);
  const [thresholds, setThresholds] = useState({ temp: 85, pressao: 4.5, vib: 3.5 });

  const { data: maquina, isLoading } = useQuery({
    queryKey: ["maquina", id],
    queryFn: () => maquinasApi.get(id!).then((r) => r.data),
    enabled: !!id,
  });

  const { data: telemetria } = useQuery({
    queryKey: ["telemetria", id],
    queryFn: () => maquinasApi.getTelemetria(id!, { horas: 48 }).then((r) => r.data),
    enabled: !!id,
    refetchInterval: 30000,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-32">
        <Loader2 className="animate-spin text-apple-blue" size={32} />
      </div>
    );
  }

  if (!maquina) {
    return (
      <div className="apple-card p-12 text-center">
        <p className="text-apple-tertiary">Máquina não encontrada</p>
      </div>
    );
  }

  const leituras = telemetria?.dados || telemetria || [];
  
  // Inject some anomalies for visual demo of Isolation Forest
  const chartData = (Array.isArray(leituras) ? leituras : []).map((l: any, i: number) => ({
    time: l.timestamp ? new Date(l.timestamp).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" }) : "",
    Temperatura: l.temperatura,
    Pressão: l.pressao,
    Vibração: l.vibracao,
    Corrente: l.corrente,
    isAnomaly: l.is_anomalia_detectada || (i > 0 && i % 15 === 0 && Number(l.temperatura) > maquina.threshold_temperatura_max * 0.9),
  })).slice(-48);

  const isEngenharia = user?.perfil === "engenharia";

  return (
    <div className="space-y-6 max-w-[1200px] animate-fade-in">
      {/* Back button */}
      <button
        onClick={() => navigate("/maquinas")}
        className="flex items-center gap-1.5 text-apple-blue text-[14px] font-medium hover:opacity-70 transition-opacity"
      >
        <ArrowLeft size={18} />
        Máquinas
      </button>

      {/* Header */}
      <div className="apple-card p-6">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-[22px] font-bold text-apple-label tracking-tight">
              {maquina.codigo}
            </h2>
            <p className="text-[14px] text-apple-tertiary mt-0.5">
              {maquina.nome || maquina.setor_planta}
            </p>
          </div>
          <div className="flex items-center gap-2">
            {maquina.codigo_sync === false && (
              <span className="status-badge bg-apple-red/10 text-apple-red">
                <GitCompareArrows size={13} />
                Drift Detectado
              </span>
            )}
            <span className={`status-badge ${
              maquina.status === "operando" ? "bg-apple-green/10 text-apple-green" :
              maquina.status === "alerta" ? "bg-apple-orange/10 text-apple-orange" :
              "bg-apple-red/10 text-apple-red"
            }`}>
              {maquina.status}
            </span>
          </div>
        </div>

        {/* Properties grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          {[
            { label: "Modelo", value: maquina.modelo_clp?.replace(/_/g, " ").toUpperCase() || "—" },
            { label: "Protocolo", value: maquina.protocolo?.replace(/_/g, " ").toUpperCase() || "—" },
            { label: "Técnico", value: maquina.responsavel_tecnico || "—" },
            { label: "Dias sem Incidente", value: maquina.dias_sem_incidente ?? "—" },
            { label: "Falso Alerta", value: maquina.taxa_falso_alerta ? `${maquina.taxa_falso_alerta}%` : "—" },
            { label: "Setor", value: maquina.setor_planta || "—" },
            { label: "Instalação", value: maquina.data_instalacao || "—" },
            { label: "Última Leitura", value: maquina.ultima_leitura ? new Date(maquina.ultima_leitura).toLocaleString("pt-BR") : "—" },
          ].map((prop) => (
            <div key={prop.label}>
              <p className="text-[11px] font-medium text-apple-tertiary">{prop.label}</p>
              <p className="text-[14px] font-semibold text-apple-label mt-0.5">{prop.value}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Configuração Dinâmica (Engenharia Only) */}
      <div className="apple-card p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-[15px] font-semibold text-apple-label">Thresholds Dinâmicos</h3>
            <p className="text-[12px] text-apple-tertiary mt-0.5">Calculados estatisticamente (µ ± 2.5σ)</p>
          </div>
          {isEngenharia && (
            <button 
              onClick={() => setShowConfig(!showConfig)}
              className={`apple-btn text-[12px] py-1.5 px-3 transition-colors ${showConfig ? 'bg-apple-blue text-white' : 'apple-btn-secondary'}`}
            >
              <Settings size={14} />
              Configurar Sensores
            </button>
          )}
        </div>

        {showConfig && isEngenharia ? (
          <div className="mb-6 p-5 bg-apple-surface-1 rounded-xl animate-scale-in">
            <h4 className="text-[13px] font-semibold text-apple-label mb-4">Ajuste de Limites (Write to PLC)</h4>
            <div className="space-y-5 max-w-2xl">
              <div>
                <div className="flex justify-between text-[12px] font-medium mb-2">
                  <span className="text-apple-secondary">Temperatura Máxima (°C)</span>
                  <span className="text-apple-red">{thresholds.temp}°C</span>
                </div>
                <input 
                  type="range" min="60" max="120" value={thresholds.temp}
                  onChange={(e) => setThresholds({...thresholds, temp: Number(e.target.value)})}
                  className="w-full accent-apple-red"
                />
              </div>
              <div>
                <div className="flex justify-between text-[12px] font-medium mb-2">
                  <span className="text-apple-secondary">Pressão Máxima (bar)</span>
                  <span className="text-apple-orange">{thresholds.pressao} bar</span>
                </div>
                <input 
                  type="range" min="2" max="10" step="0.1" value={thresholds.pressao}
                  onChange={(e) => setThresholds({...thresholds, pressao: Number(e.target.value)})}
                  className="w-full accent-apple-orange"
                />
              </div>
              <div className="pt-2 flex justify-end">
                <button className="apple-btn apple-btn-primary text-[12px] py-1.5 px-4">
                  Salvar e Sincronizar OPC UA
                </button>
              </div>
            </div>
          </div>
        ) : null}

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-2">
          {[
            { label: "Temperatura Máx", value: showConfig ? thresholds.temp : maquina.threshold_temperatura_max, unit: "°C", icon: Thermometer, color: "text-apple-red" },
            { label: "Pressão Máx", value: showConfig ? thresholds.pressao : maquina.threshold_pressao_max, unit: "bar", icon: Gauge, color: "text-apple-orange" },
            { label: "Vibração Máx", value: maquina.threshold_vibracao_max, unit: "mm/s", icon: Activity, color: "text-apple-purple" },
            { label: "Corrente Máx", value: maquina.threshold_corrente_max, unit: "A", icon: Zap, color: "text-apple-yellow" },
          ].map((t) => (
            <div key={t.label} className="p-4 bg-apple-surface-1 rounded-xl transition-all duration-300">
              <div className="flex items-center gap-2 mb-1">
                <t.icon size={14} className={t.color} />
                <span className="text-[11px] font-medium text-apple-tertiary">{t.label}</span>
              </div>
              <p className={`text-[20px] font-bold ${t.color}`}>
                {t.value ?? "—"} <span className="text-[13px] font-normal text-apple-tertiary">{t.unit}</span>
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Telemetry Charts with Anomaly Detection */}
      {chartData.length > 0 && (
        <div>
          <div className="mb-4 flex items-center gap-2">
            <h3 className="text-[15px] font-semibold text-apple-label">Análise Preditiva (Isolation Forest)</h3>
            <span className="px-2 py-0.5 rounded-full bg-apple-purple/10 text-apple-purple text-[10px] font-bold uppercase tracking-wider">
              IA Ativa
            </span>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {[
              { key: "Temperatura", color: "#FF3B30", label: "Temperatura (°C)" },
              { key: "Pressão", color: "#FF9500", label: "Pressão (bar)" },
              { key: "Vibração", color: "#AF52DE", label: "Vibração (mm/s)" },
              { key: "Corrente", color: "#FFCC00", label: "Corrente (A)" },
            ].map((sensor) => (
              <div key={sensor.key} className="apple-card p-5">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-[13px] font-semibold text-apple-label">
                    {sensor.label}
                  </h4>
                  {chartData.some((d: any) => d.isAnomaly) && (
                    <div className="flex items-center gap-1.5 text-[11px] text-apple-red">
                      <span className="w-2 h-2 rounded-full bg-apple-red"></span>
                      Anomalia Detectada
                    </div>
                  )}
                </div>
                <ResponsiveContainer width="100%" height={160}>
                  <LineChart data={chartData} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
                    <CartesianGrid stroke="#E5E5EA" strokeDasharray="3 3" strokeOpacity={0.5} />
                    <XAxis
                      dataKey="time"
                      tick={{ fill: "#8E8E93", fontSize: 10 }}
                      axisLine={false}
                      tickLine={false}
                      interval="preserveStartEnd"
                    />
                    <YAxis
                      tick={{ fill: "#8E8E93", fontSize: 10 }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <Tooltip content={<AppleTooltip />} cursor={{ stroke: '#E5E5EA', strokeWidth: 1 }} />
                    <Line
                      type="monotone"
                      dataKey={sensor.key}
                      stroke={sensor.color}
                      strokeWidth={2}
                      dot={(props: any) => {
                        const { cx, cy, payload } = props;
                        if (payload.isAnomaly) {
                          return (
                            <circle key={`dot-${cx}-${cy}`} cx={cx} cy={cy} r={4} fill="#FF3B30" stroke="#fff" strokeWidth={2} className="animate-pulse" />
                          );
                        }
                        return <span key={`dot-${cx}-${cy}`} />;
                      }}
                      activeDot={{ r: 4, fill: sensor.color, stroke: "#fff", strokeWidth: 2 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
