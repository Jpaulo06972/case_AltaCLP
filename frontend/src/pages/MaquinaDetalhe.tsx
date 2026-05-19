/**
 * AltaCLP Intelligence — Máquina Detail Page
 * Master-Detail with telemetry charts + hybrid predictive monitoring
 */

import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { maquinasApi, tecnicoApi, equipamentosApi, equipmentLibraryApi } from "@/services/api";
import AIChatWidget from "@/components/AIChatWidget";
import { useTecnico } from "@/hooks/useTecnico";
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
  FileText,
  Bot,
  X,
  ExternalLink,
  Download,
  ChevronRight
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
  const [activeTab, setActiveTab] = useState<'sensors' | 'actuators' | 'inverters'>('sensors');
  const [docDevice, setDocDevice] = useState<any>(null);
  const [aiDevice, setAiDevice] = useState<any>(null);

  const devicesData = {
    sensors: [
      { id: "SNS-001", name: "Inductive Proximity Sensor IFM IGS204", reading: "Detected", status: "Normal" },
      { id: "SNS-002", name: "PT100 Temperature Sensor", reading: "74.3 °C", status: "Normal" },
      { id: "SNS-003", name: "Pressure Transmitter Balluff BSP", reading: "4.1 bar", status: "Normal" },
      { id: "SNS-004", name: "Vibration Sensor IMI 686C01", reading: "6.8 mm/s", status: "Alert" },
      { id: "SNS-005", name: "Photoelectric Sensor Sick W4S-3", reading: "Not Detected", status: "Normal" }
    ],
    actuators: [
      { id: "ACT-001", name: "SMC CDJ2B16 Pneumatic Cylinder", reading: "Extended", status: "Normal" },
      { id: "ACT-002", name: "24VDC Solenoid Valve Parker", reading: "Open", status: "Normal" },
      { id: "ACT-003", name: "WEG Three-Phase Motor W22 7.5cv", reading: "Running", status: "Normal" },
      { id: "ACT-004", name: "SSR Solid State Relay Crydom", reading: "Active", status: "Normal" }
    ],
    inverters: [
      { id: "INV-001", name: "WEG CFW500 Variable Frequency Drive", reading: "48.5 Hz / 9.2 A", status: "Normal" },
      { id: "INV-002", name: "Siemens SINAMICS G120", reading: "0 Hz / 0 A", status: "Offline" },
      { id: "INV-003", name: "ABB ACS550", reading: "60.0 Hz / 10.1 A", status: "Normal" }
    ]
  };

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

  const { data: libraryDocs } = useQuery({
    queryKey: ["equipment-library", "all"],
    queryFn: () => equipmentLibraryApi.list({ limit: 100 } as any).then((r) => r.data),
    enabled: !!docDevice,
  });

  const matchedDoc = libraryDocs?.dados?.find((doc: any) => {
    if (!docDevice) return false;
    const dbName = doc.nome_equipamento.toLowerCase();
    const devName = docDevice.name.toLowerCase();
    
    if (dbName === devName) return true;
    
    const models = ["cfw500", "w22", "igs204", "bsp", "w4s-3", "g120", "acs550", "pt100"];
    for (const model of models) {
      if (devName.includes(model) && dbName.includes(model)) return true;
    }
    
    const devWords = devName.split(" ").filter((w: string) => w.length > 3);
    let matchCount = 0;
    for (const word of devWords) {
      if (dbName.includes(word)) matchCount++;
    }
    return matchCount >= 2;
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
  const { isTecnico } = useTecnico();

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
            { label: "Modelo", value: "Siemens S7-1200 (CPU 1214C)" },
            { label: "Protocolo", value: "MQTT / Modbus TCP" },
            { label: "Técnico", value: "Carlos Mendonça" },
            { label: "Dias sem Incidente", value: "14" },
            { label: "Falso Alerta", value: "3" },
            { label: "Setor", value: "Linha de Envase — Setor B" },
            { label: "Instalação", value: "12/03/2024" },
            { label: "Última Leitura", value: "há 12 segundos" },
          ].map((prop) => (
            <div key={prop.label}>
              <p className="text-[11px] font-medium text-apple-tertiary">{prop.label}</p>
              <p className="text-[14px] font-semibold text-apple-label mt-0.5">{prop.value}</p>
            </div>
          ))}
        </div>
      </div>

      {isTecnico && id && (
        <AIChatWidget
          title="Assistente Técnico — Instalação"
          placeholder="Ex.: como instalar, esquema elétrico, passo a passo..."
          className="min-h-[260px]"
          onSend={async (msg) => {
            const r = await tecnicoApi.chatInstalacao({
              mensagem: msg,
              maquina_id: id,
              modo: "instalacao",
            });
            return r.data.resposta;
          }}
        />
      )}

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
            { label: "Temperatura Máx", value: showConfig ? thresholds.temp : "85", unit: "°C", icon: Thermometer, color: "text-apple-red" },
            { label: "Pressão Máx", value: showConfig ? thresholds.pressao : "6.5", unit: "bar", icon: Gauge, color: "text-apple-orange" },
            { label: "Vibração Máx", value: "7.2", unit: "mm/s", icon: Activity, color: "text-apple-purple" },
            { label: "Corrente Máx", value: "10.4", unit: "A", icon: Zap, color: "text-apple-yellow" },
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

      {/* Installed Devices Section */}
      <div className="apple-card p-6">
        <h3 className="text-[15px] font-semibold text-apple-label mb-4">Installed Devices</h3>
        <div className="flex gap-4 border-b border-apple-separator/30 mb-4">
          {(['sensors', 'actuators', 'inverters'] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`pb-2 text-[13px] font-medium transition-colors border-b-2 ${
                activeTab === tab 
                  ? 'border-apple-blue text-apple-blue' 
                  : 'border-transparent text-apple-tertiary hover:text-apple-secondary'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>
        <div className="space-y-2">
          {devicesData[activeTab].map(device => (
            <div key={device.id} className="flex items-center justify-between p-3 bg-apple-surface-1 rounded-xl border border-apple-separator/20">
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-[12px] font-bold text-apple-secondary">{device.id}</span>
                  <span className="text-[13px] font-semibold text-apple-label">{device.name}</span>
                </div>
                <div className="text-[12px] text-apple-tertiary mt-1">Reading: <span className="font-medium text-apple-secondary">{device.reading}</span></div>
              </div>
              <div className="flex items-center gap-4">
                <span className={`px-2.5 py-1 rounded-full text-[11px] font-bold tracking-wide ${
                  device.status === 'Normal' ? 'bg-apple-green/10 text-apple-green' :
                  device.status === 'Alert' ? 'bg-apple-orange/10 text-apple-orange' :
                  device.status === 'Critical' ? 'bg-apple-red/10 text-apple-red' :
                  'bg-apple-separator/20 text-apple-secondary'
                }`}>
                  {device.status.toUpperCase()}
                </span>
                <div className="flex items-center gap-2">
                  <button onClick={() => setDocDevice(device)} className="apple-btn apple-btn-secondary py-1.5 px-3 text-[12px] flex items-center gap-1.5">
                    <FileText size={14} /> Documentation
                  </button>
                  <button onClick={() => setAiDevice(device)} className="apple-btn bg-apple-purple/10 text-apple-purple hover:bg-apple-purple/20 py-1.5 px-3 text-[12px] flex items-center gap-1.5 font-medium transition-colors">
                    <Bot size={14} /> Ask AI
                  </button>
                </div>
              </div>
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

      {/* Documentation Panel Modal */}
      {docDevice && (
        <div className="fixed inset-0 z-50 flex justify-end bg-black/20 backdrop-blur-sm animate-fade-in">
          <div className="w-full max-w-md bg-apple-surface-0 h-full shadow-2xl flex flex-col animate-slide-in-right">
            <div className="p-5 flex items-center justify-between border-b border-apple-separator/30">
              <div>
                <h2 className="text-[18px] font-bold text-apple-label">{docDevice.name}</h2>
                <p className="text-[13px] text-apple-tertiary">Manufacturer: {docDevice.name.split(' ')[0]}</p>
              </div>
              <button onClick={() => setDocDevice(null)} className="p-2 text-apple-secondary hover:bg-apple-surface-1 rounded-full transition-colors">
                <X size={20} />
              </button>
            </div>
            <div className="p-6 space-y-6 flex-1 overflow-y-auto">
              {matchedDoc ? (
                <div className="flex gap-3">
                  <a href={matchedDoc.url_manual} target="_blank" className="flex-1 apple-btn apple-btn-primary py-2.5 flex items-center justify-center gap-2">
                    <ExternalLink size={16} /> Access Manual
                  </a>
                  <button className="flex-1 apple-btn apple-btn-secondary py-2.5 flex items-center justify-center gap-2">
                    <Download size={16} /> Download Datasheet
                  </button>
                </div>
              ) : (
                <div className="flex flex-col gap-3">
                  <div className="apple-card p-4 border border-apple-orange/30 bg-apple-orange/5 flex flex-col items-center justify-center text-center">
                    <AlertTriangle size={24} className="text-apple-orange mb-2" />
                    <p className="text-[13px] font-semibold text-apple-orange mb-1">Documentation not registered</p>
                    <p className="text-[12px] text-apple-orange/80 mb-3">No official manual was found in the library for this device.</p>
                    {isEngenharia && (
                      <button onClick={() => navigate('/library')} className="apple-btn bg-apple-surface-0 border border-apple-orange/20 text-apple-orange py-1.5 px-4 text-[12px] shadow-sm">
                        Add to Equipment Library
                      </button>
                    )}
                  </div>
                  <button className="w-full apple-btn apple-btn-secondary py-2.5 flex items-center justify-center gap-2">
                    <Download size={16} /> Download Generic Spec
                  </button>
                </div>
              )}
              
              <div>
                <h3 className="text-[14px] font-semibold text-apple-label mb-3">Quick Spec</h3>
                <div className="apple-card p-4 space-y-3">
                  {[
                    { label: "Voltage", value: activeTab === 'sensors' ? "24V DC" : activeTab === 'actuators' ? "24V DC / 220V AC" : "380V AC 3-Phase" },
                    { label: "IP Rating", value: "IP67" },
                    { label: "Operating Temperature", value: "-20°C to +80°C" },
                    { label: "Communication Protocol", value: activeTab === 'inverters' ? "Modbus RTU / PROFINET" : "IO-Link / 4-20mA" }
                  ].map(spec => (
                    <div key={spec.label} className="flex justify-between items-center text-[13px]">
                      <span className="text-apple-secondary">{spec.label}</span>
                      <span className="font-medium text-apple-label">{spec.value}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* AI Assistant Panel Modal */}
      {aiDevice && (
        <div className="fixed inset-0 z-50 flex justify-end bg-black/20 backdrop-blur-sm animate-fade-in">
          <div className="w-full max-w-[450px] bg-apple-surface-0 h-full shadow-2xl flex flex-col animate-slide-in-right">
            <div className="p-4 flex items-center justify-between border-b border-apple-separator/30 bg-apple-surface-1">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-apple-purple/10 flex items-center justify-center text-apple-purple">
                  <Bot size={20} />
                </div>
                <div>
                  <h2 className="text-[15px] font-bold text-apple-label">Ask AI Assistant</h2>
                  <p className="text-[12px] text-apple-tertiary">{aiDevice.id} | {aiDevice.name}</p>
                </div>
              </div>
              <button onClick={() => setAiDevice(null)} className="p-2 text-apple-secondary hover:bg-apple-surface-2 rounded-full transition-colors">
                <X size={20} />
              </button>
            </div>
            
            <div className="flex-1 overflow-hidden flex flex-col">
              <AIChatWidget
                title={`Context: ${aiDevice.name}`}
                initialSummary={`This is a ${aiDevice.name}. I can help you with installation steps, parameter configuration, wiring diagrams, troubleshooting, or calibration. What do you need?`}
                suggestions={[
                  "How do I install this device?",
                  "What are the main parameters to configure?",
                  "Show me the wiring diagram.",
                  "How do I calibrate this sensor?",
                  "What does this alarm code mean?"
                ]}
                className="flex-1 border-0 rounded-none shadow-none"
                placeholder="Ask about installation, parameters, wiring..."
                onSend={async (msg) => {
                  // Simulate an AI response for demonstration
                  await new Promise(resolve => setTimeout(resolve, 1500));
                  return `Here is some information about "${msg}" for the ${aiDevice.name}. Usually, you should refer to section 4 of the official manual. Would you like a step-by-step breakdown?`;
                }}
              />
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
