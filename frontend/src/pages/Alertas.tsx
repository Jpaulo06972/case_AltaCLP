/**
 * AltaCLP Intelligence — Alertas Page
 * Real-time alerts with SSE streaming + macOS notification toasts
 * Fixes: relational data (id_projeto, nome_projeto), inline modal, 
 *        AI analysis text rendering, cross-screen navigation links.
 */

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { alertasApi, alertasIaApi } from "@/services/api";
import { useTecnico } from "@/hooks/useTecnico";
import TecnicoAlertPanel from "@/components/tecnico/TecnicoAlertPanel";
import { useToast } from "@/components/Toast";
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Bell,
  AlertTriangle,
  Eye,
  Loader2,
  Thermometer,
  Gauge,
  Activity,
  Zap,
  GitCompareArrows,
  WifiOff,
  Search,
  X,
  Send,
  ExternalLink,
  Building2,
  Cpu,
} from "lucide-react";

const severidadeConfig: Record<string, { color: string; bg: string }> = {
  "emergência": { color: "text-apple-red", bg: "bg-apple-red/10" },
  emergencia: { color: "text-apple-red", bg: "bg-apple-red/10" },
  "crítico": { color: "text-apple-red", bg: "bg-apple-red/10" },
  critico: { color: "text-apple-red", bg: "bg-apple-red/10" },
  aviso: { color: "text-apple-orange", bg: "bg-apple-orange/10" },
  info: { color: "text-apple-blue", bg: "bg-apple-blue/10" },
};

const tipoIcons: Record<string, any> = {
  temperatura_alta: Thermometer,
  pressao_alta: Gauge,
  vibracao_alta: Activity,
  corrente_alta: Zap,
  drift_codigo: GitCompareArrows,
  sem_comunicacao: WifiOff,
  anomalia_ml: AlertTriangle,
};

// ── Manual Report Modal ────────────────────────────────────────────────────────
interface ManualReportModalProps {
  alerta: any;
  onClose: () => void;
  onSend: (diretiva: string) => Promise<void>;
}

function ManualReportModal({ alerta, onClose, onSend }: ManualReportModalProps) {
  const [diretiva, setDiretiva] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!diretiva.trim()) return;
    setLoading(true);
    await onSend(diretiva);
    setLoading(false);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center">
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg p-6 space-y-5 animate-fade-in">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="text-[17px] font-semibold text-apple-label">Relatório Manual</h3>
            <p className="text-[12px] text-apple-tertiary mt-0.5">
              {alerta?.titulo}
              {alerta?.nome_projeto && (
                <span className="ml-2 px-1.5 py-0.5 bg-apple-blue/10 text-apple-blue rounded text-[11px]">
                  {alerta.nome_projeto}
                </span>
              )}
            </p>
          </div>
          <button type="button" onClick={onClose} className="p-2 rounded-full hover:bg-black/5">
            <X size={18} />
          </button>
        </div>

        <div className="space-y-1.5">
          <label className="text-[12px] font-semibold text-apple-secondary">
            Diretiva para o técnico
          </label>
          <textarea
            value={diretiva}
            onChange={(e) => setDiretiva(e.target.value)}
            placeholder="Descreva a ação a ser tomada pelo técnico. Ex: Verificar rolamentos e temperatura do motor..."
            rows={5}
            className="w-full px-3 py-2.5 text-[13px] bg-apple-surface-1 border border-apple-separator rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-apple-blue/30 text-apple-label placeholder:text-apple-quaternary"
          />
        </div>

        <div className="grid grid-cols-2 gap-3 pt-2">
          <button type="button" onClick={onClose} className="apple-btn apple-btn-secondary text-[13px]">
            Cancelar
          </button>
          <button
            type="button"
            onClick={handleSend}
            disabled={loading || !diretiva.trim()}
            className="apple-btn apple-btn-primary text-[13px] flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {loading ? <Loader2 size={14} className="animate-spin" /> : <Send size={14} />}
            Enviar Diretiva
          </button>
        </div>
      </div>
    </div>
  );
}

// ── Main Component ─────────────────────────────────────────────────────────────
export default function Alertas() {
  const { addToast } = useToast();
  const { isTecnico } = useTecnico();
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [filtroSeveridade, setFiltroSeveridade] = useState<string>("todos");
  const [filtroStatus, setFiltroStatus] = useState<string>("todos");
  const [busca, setBusca] = useState("");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [showManualModal, setShowManualModal] = useState(false);

  const { data: analiseIa } = useQuery({
    queryKey: ["alerta-analise", selectedId],
    queryFn: () => alertasIaApi.analise(selectedId!).then((r) => r.data),
    enabled: !!selectedId,
  });

  const { data, isLoading } = useQuery({
    queryKey: ["alertas"],
    queryFn: () => alertasApi.list().then((r) => r.data),
    refetchInterval: 15000,
  });

  const { data: stats } = useQuery({
    queryKey: ["alertas-stats"],
    queryFn: () => alertasApi.getEstatisticas().then((r) => r.data),
  });

  // ── SSE Real-time Stream ─────────────────────────────────────────────────────
  useEffect(() => {
    let eventSource: EventSource | null = null;
    try {
      eventSource = new EventSource(alertasApi.streamUrl);
      eventSource.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          if (parsed.evento === "novo_alerta" && parsed.alerta) {
            addToast(
              `⚠️ ${parsed.alerta.titulo || "Novo alerta detectado"}`,
              parsed.alerta.severidade === "emergência" || parsed.alerta.severidade === "crítico"
                ? "error"
                : "warning"
            );
            qc.invalidateQueries({ queryKey: ["alertas"] });
          }
        } catch {}
      };
      eventSource.onerror = () => eventSource?.close();
    } catch {}
    return () => eventSource?.close();
  }, [addToast, qc]);

  const alertas = data?.dados || data || [];
  const filteredAlertas = (Array.isArray(alertas) ? alertas : []).filter((a: any) => {
    if (filtroSeveridade !== "todos" && a.severidade !== filtroSeveridade) return false;
    if (filtroStatus !== "todos" && a.status !== filtroStatus) return false;
    if (busca && !(
      a.titulo?.toLowerCase().includes(busca.toLowerCase()) ||
      a.codigo_alerta?.toLowerCase().includes(busca.toLowerCase()) ||
      a.nome_projeto?.toLowerCase().includes(busca.toLowerCase()) ||
      a.maquina_codigo?.toLowerCase().includes(busca.toLowerCase())
    )) return false;
    return true;
  });

  const selectedAlerta = filteredAlertas.find((a: any) => a.id === selectedId) || null;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-32">
        <Loader2 className="animate-spin text-apple-blue" size={32} />
      </div>
    );
  }

  return (
    <div className="flex gap-4 max-w-[1600px]">
      <div className={`space-y-6 flex-1 min-w-0 ${selectedId ? "max-w-[calc(100%-400px)]" : ""}`}>
        {/* ── Stats Strip ── */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            { label: "Total Abertos", value: stats?.total_abertos ?? 43, color: "text-apple-orange" },
            { label: "Críticos", value: stats?.criticos ?? 8, color: "text-apple-red" },
            { label: "Custo/Mês (Visitas)", value: `R$ ${((stats?.custo_total_visitas_mes ?? 31400) / 1000).toFixed(1)}k`, color: "text-apple-red" },
            { label: "Taxa Falso Alerta", value: `${stats?.taxa_falso_alerta_geral ?? 64}%`, color: "text-apple-orange" },
          ].map((s) => (
            <div key={s.label} className="apple-card px-4 py-3 text-center">
              <p className="text-[11px] font-medium text-apple-tertiary">{s.label}</p>
              <p className={`text-[22px] font-bold tracking-tight ${s.color}`}>{s.value}</p>
            </div>
          ))}
        </div>

        {/* ── Filters ── */}
        <div className="apple-card p-4 flex flex-wrap items-center gap-3">
          <div className="relative flex-1 min-w-[200px]">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-apple-tertiary" />
            <input
              type="text"
              placeholder="Buscar alertas, projetos, máquinas..."
              value={busca}
              onChange={(e) => setBusca(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-apple-surface-1 border border-apple-separator rounded-lg text-[13px] text-apple-label placeholder:text-apple-quaternary focus:outline-none focus:ring-2 focus:ring-apple-blue/30"
            />
          </div>
          <select
            value={filtroSeveridade}
            onChange={(e) => setFiltroSeveridade(e.target.value)}
            className="px-3 py-2 bg-apple-surface-1 border border-apple-separator rounded-lg text-[13px] text-apple-label focus:outline-none focus:ring-2 focus:ring-apple-blue/30"
          >
            <option value="todos">Todas Severidades</option>
            <option value="emergência">Emergência</option>
            <option value="crítico">Crítico</option>
            <option value="aviso">Aviso</option>
            <option value="info">Info</option>
          </select>
          <select
            value={filtroStatus}
            onChange={(e) => setFiltroStatus(e.target.value)}
            className="px-3 py-2 bg-apple-surface-1 border border-apple-separator rounded-lg text-[13px] text-apple-label focus:outline-none focus:ring-2 focus:ring-apple-blue/30"
          >
            <option value="todos">Todos Status</option>
            <option value="aberto">Aberto</option>
            <option value="em_investigacao">Em Investigação</option>
            <option value="resolvido">Resolvido</option>
            <option value="falso_alerta">Falso Alerta</option>
          </select>
        </div>

        {/* ── Alert List ── */}
        <div className="space-y-2">
          {filteredAlertas.map((alerta: any, i: number) => {
            const sev = severidadeConfig[alerta.severidade] || severidadeConfig.info;
            const Icon = tipoIcons[alerta.tipo] || Bell;

            return (
              <button
                type="button"
                key={alerta.id || i}
                onClick={() => alerta.id && setSelectedId(alerta.id === selectedId ? null : alerta.id)}
                className={`w-full text-left apple-card p-4 flex items-start gap-4 hover:shadow-md transition-shadow animate-fade-in ${
                  selectedId === alerta.id ? "ring-2 ring-apple-blue" : ""
                }`}
              >
                {/* Icon */}
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${sev.bg}`}>
                  <Icon size={18} className={sev.color} />
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-0.5">
                    <h4 className="text-[14px] font-semibold text-apple-label truncate">
                      {alerta.titulo || "Alerta"}
                    </h4>
                    <span className={`status-badge ${sev.bg} ${sev.color}`}>
                      {alerta.severidade}
                    </span>
                  </div>

                  {/* Cross-screen relational links */}
                  <div className="flex items-center gap-3 mb-1 flex-wrap">
                    {alerta.maquina_codigo && (
                      <Link
                        to={`/maquinas/${alerta.maquina_id}`}
                        onClick={(e) => e.stopPropagation()}
                        className="flex items-center gap-1 text-[11px] text-apple-blue hover:underline"
                      >
                        <Cpu size={10} />
                        {alerta.maquina_codigo}
                      </Link>
                    )}
                    {alerta.nome_projeto && alerta.id_projeto && (
                      <Link
                        to={`/comissionamento?projeto=${alerta.id_projeto}&open=true`}
                        onClick={(e) => e.stopPropagation()}
                        className="flex items-center gap-1 text-[11px] text-apple-purple hover:underline"
                      >
                        <Building2 size={10} />
                        {alerta.nome_projeto}
                        <ExternalLink size={9} className="opacity-60" />
                      </Link>
                    )}
                  </div>

                  <p className="text-[12px] text-apple-tertiary line-clamp-1">
                    {alerta.descricao || "Sem descrição"}
                  </p>
                  <div className="flex items-center gap-4 mt-2 text-[11px] text-apple-quaternary">
                    <span>{alerta.codigo_alerta}</span>
                    <span>
                      {alerta.timestamp_criacao
                        ? new Date(alerta.timestamp_criacao).toLocaleDateString("pt-BR")
                        : "—"}
                    </span>
                    {alerta.is_falso_alerta && (
                      <span className="text-apple-orange font-semibold">Falso alerta confirmado</span>
                    )}
                  </div>
                </div>

                {/* Status badge */}
                <div className="flex-shrink-0">
                  <span
                    className={`status-badge ${
                      alerta.status === "aberto"
                        ? "bg-apple-orange/10 text-apple-orange"
                        : alerta.status === "resolvido"
                        ? "bg-apple-green/10 text-apple-green"
                        : "bg-apple-surface-2 text-apple-tertiary"
                    }`}
                  >
                    {alerta.status?.replace(/_/g, " ")}
                  </span>
                </div>
              </button>
            );
          })}

          {filteredAlertas.length === 0 && (
            <div className="apple-card p-12 text-center">
              <Bell className="mx-auto mb-3 text-apple-quaternary" size={32} />
              <p className="text-[14px] font-medium text-apple-tertiary">
                Nenhum alerta encontrado com os filtros aplicados
              </p>
            </div>
          )}
        </div>
      </div>

      {/* ── Right Panel ── */}
      {selectedId && isTecnico && (
        <TecnicoAlertPanel alertaId={selectedId} onClose={() => setSelectedId(null)} />
      )}

      {selectedId && !isTecnico && (
        <aside className="w-[380px] flex-shrink-0 apple-card p-5 space-y-4 sticky top-4 self-start max-h-[calc(100vh-120px)] overflow-y-auto">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="text-[15px] font-semibold text-apple-label">Análise de Causa Raiz (IA)</h3>
              {selectedAlerta?.nome_projeto && (
                <Link
                  to={`/comissionamento?projeto=${selectedAlerta.id_projeto}&open=true`}
                  className="flex items-center gap-1 text-[11px] text-apple-blue hover:underline mt-0.5"
                >
                  <Building2 size={10} /> {selectedAlerta.nome_projeto}
                  <ExternalLink size={9} className="opacity-60" />
                </Link>
              )}
            </div>
            <button
              type="button"
              onClick={() => setSelectedId(null)}
              className="p-1.5 rounded-full hover:bg-black/5"
            >
              <X size={16} />
            </button>
          </div>

          {/* AI analysis — plain text, not markdown */}
          <div className="text-[13px] text-apple-secondary leading-relaxed space-y-2">
            {(analiseIa?.texto_analise || analiseIa?.texto_analise_ia || "Gerando análise…")
              .split("\n")
              .map((line: string, i: number) => {
                // Simple markdown: **bold** → <strong>
                const parts = line.split(/\*\*(.+?)\*\*/g);
                return (
                  <p key={i}>
                    {parts.map((part, j) =>
                      j % 2 === 1 ? (
                        <strong key={j} className="font-semibold text-apple-label">
                          {part}
                        </strong>
                      ) : (
                        part
                      )
                    )}
                  </p>
                );
              })}
          </div>

          {analiseIa?.sugestao_acao && (
            <p className="text-[12px] text-apple-blue bg-apple-blue/5 p-3 rounded-lg">
              {analiseIa.sugestao_acao}
            </p>
          )}

          <div className="space-y-2 pt-2 border-t border-apple-separator/30">
            <button
              type="button"
              className="w-full apple-btn apple-btn-primary text-[12px]"
              onClick={async () => {
                const d = new Date();
                d.setDate(d.getDate() + 1);
                await alertasIaApi.aprovarSugestao(selectedId, {
                  id_tecnico: "Anderson Vasconcellos",
                  data_agendada: d.toISOString(),
                });
                addToast("Técnico despachado — notificações enviadas", "success");
                qc.invalidateQueries({ queryKey: ["alertas"] });
              }}
            >
              Aprovar Sugestão IA
            </button>
            <button
              type="button"
              className="w-full apple-btn apple-btn-secondary text-[12px]"
              onClick={() => setShowManualModal(true)}
            >
              Relatório Manual
            </button>
          </div>
        </aside>
      )}

      {/* ── Manual Report Modal ── */}
      {showManualModal && selectedAlerta && (
        <ManualReportModal
          alerta={selectedAlerta}
          onClose={() => setShowManualModal(false)}
          onSend={async (diretiva) => {
            const d = new Date();
            d.setHours(d.getHours() + 4);
            await alertasIaApi.relatorioManual(selectedId!, {
              diretiva,
              id_tecnico: "Anderson Vasconcellos",
              data_agendada: d.toISOString(),
            });
            addToast("Relatório manual enviado", "success");
            qc.invalidateQueries({ queryKey: ["alertas"] });
          }}
        />
      )}
    </div>
  );
}
