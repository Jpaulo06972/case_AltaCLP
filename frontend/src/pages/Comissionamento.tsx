/**
 * AltaCLP Intelligence — Comissionamento Page
 * Kanban-style commissioning backlog
 */

import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { comissionamentoApi } from "@/services/api";
import { useTecnico } from "@/hooks/useTecnico";
import { useSearchParams } from "react-router-dom";
import TecnicoProjetoDrawer from "@/components/tecnico/TecnicoProjetoDrawer";
import {
  Wrench,
  AlertTriangle,
  Clock,
  Loader2,
  DollarSign,
  User,
  RefreshCw,
} from "lucide-react";

// MOCK DATA — remove when API is stable
const MOCK_KANBAN = {
  aguardando_dados: [
    { id: "m1", id_projeto: "PROJ-001", maquina_codigo: "CLP-001", cliente_nome: "Anaclara Alimentos", engenheiro_responsavel: "Cláudia Santarém", dias_atraso: 12, valor_contrato: 780000, risco_cancelamento: true, fase_projeto: "AWAITING_ENGINEERING" },
    { id: "m2", id_projeto: "PROJ-004", maquina_codigo: "CLP-011", cliente_nome: "Nordeste Têxtil", engenheiro_responsavel: "Rafael Braga", dias_atraso: 0, valor_contrato: 340000, risco_cancelamento: false, fase_projeto: "AWAITING_ENGINEERING" },
  ],
  em_andamento: [
    { id: "m3", id_projeto: "PROJ-002", maquina_codigo: "CLP-007", cliente_nome: "Sul Químicos", engenheiro_responsavel: "Cláudia Santarém", dias_atraso: 5, valor_contrato: 520000, risco_cancelamento: false, fase_projeto: "VENDOR_QUOTE" },
    { id: "m4", id_projeto: "PROJ-005", maquina_codigo: "CLP-017", cliente_nome: "Mecasul Componentes", engenheiro_responsavel: "Rafael Braga", dias_atraso: 0, valor_contrato: 215000, risco_cancelamento: false, fase_projeto: "VENDOR_QUOTE" },
  ],
  fat_pendente: [
    { id: "m5", id_projeto: "PROJ-003", maquina_codigo: "CLP-003", cliente_nome: "Pampulha Pharma", engenheiro_responsavel: "Cláudia Santarém", dias_atraso: 3, valor_contrato: 680000, risco_cancelamento: false, fase_projeto: "VENDOR_QUOTE" },
  ],
  treinamento_operador: [
    { id: "m6", id_projeto: "PROJ-006", maquina_codigo: "CLP-020", cliente_nome: "Borracharia Goiás", engenheiro_responsavel: "Rafael Braga", dias_atraso: 0, valor_contrato: 175000, risco_cancelamento: false, fase_projeto: "VENDOR_QUOTE" },
  ],
};

const statusLabels: Record<string, { label: string; color: string; bg: string }> = {
  aguardando_dados: { label: "Aguardando Dados", color: "text-apple-orange", bg: "bg-apple-orange/10" },
  em_andamento: { label: "Em Andamento", color: "text-apple-blue", bg: "bg-apple-blue/10" },
  fat_pendente: { label: "FAT Pendente", color: "text-apple-purple", bg: "bg-apple-purple/10" },
  treinamento_operador: { label: "Treinamento", color: "text-apple-teal", bg: "bg-apple-teal/10" },
  concluido: { label: "Concluído", color: "text-apple-green", bg: "bg-apple-green/10" },
  cancelado: { label: "Cancelado", color: "text-apple-red", bg: "bg-apple-red/10" },
};

export default function Comissionamento() {
  const { isTecnico, user } = useTecnico();
  const isVendedor = user?.perfil === "vendedor";
  const [projetoAberto, setProjetoAberto] = useState<string | null>(null);
  const [searchParams] = useSearchParams();

  // Deep-link: /comissionamento?projeto=PROJ-001&open=true
  useEffect(() => {
    const projetoParam = searchParams.get("projeto");
    const openParam = searchParams.get("open");
    if (projetoParam && openParam === "true") {
      setProjetoAberto(projetoParam);
    }
  }, [searchParams]);

  const isEditable = (item: any) => {
    if (!isVendedor) return true;
    return ["AWAITING_ENGINEERING", "VENDOR_QUOTE"].includes(item.fase_projeto);
  };

  const handleClick = (item: any) => {
    const targetId = item.id_projeto || null;
    if (targetId && (isTecnico || user?.perfil === "engenharia" || (isVendedor && isEditable(item)))) {
      setProjetoAberto(targetId);
    }
  };

  const { data: kanban, isLoading: loadingKanban, isError: kanbanError, refetch } = useQuery({
    queryKey: ["comissionamento-kanban"],
    queryFn: () => comissionamentoApi.getKanban().then((r) => r.data),
    retry: 1,
    refetchOnMount: true,
    refetchInterval: 5000, // Poll every 5 seconds for real-time updates
  });

  const { data: anaclara } = useQuery({
    queryKey: ["comissionamento-anaclara"],
    queryFn: () => comissionamentoApi.getRiscoAnaclara().then((r) => r.data).catch(() => null),
  });

  // ── Loading State ──────────────────────────────────────────────────────────
  if (loadingKanban) {
    return (
      <div className="flex flex-col items-center justify-center py-32 gap-4">
        <Loader2 className="animate-spin text-apple-blue" size={36} />
        <p className="text-[14px] text-apple-tertiary">Carregando painel de comissionamento…</p>
      </div>
    );
  }

  // ── Error State ────────────────────────────────────────────────────────────
  if (kanbanError) {
    return (
      <div className="flex flex-col items-center justify-center py-32 gap-4">
        <AlertTriangle size={36} className="text-apple-red" />
        <p className="text-[16px] font-semibold text-apple-label">Erro ao carregar o painel</p>
        <p className="text-[13px] text-apple-tertiary">Não foi possível conectar à API de comissionamento.</p>
        <button
          type="button"
          onClick={() => refetch()}
          className="apple-btn apple-btn-primary flex items-center gap-2 mt-2"
        >
          <RefreshCw size={16} /> Tentar Novamente
        </button>
        <p className="text-[11px] text-apple-quaternary mt-4">
          Exibindo dados de demonstração abaixo.
        </p>
      </div>
    );
  }

  // Use API data if available, fall back to mock data
  const kanbanData = (kanban && typeof kanban === "object") ? kanban : MOCK_KANBAN;

  const columns = [
    { key: "aguardando_dados", label: "Aguardando Dados", color: "#FF9500" },
    { key: "em_andamento", label: "Em Andamento", color: "#007AFF" },
    { key: "fat_pendente", label: "FAT Pendente", color: "#AF52DE" },
    { key: "treinamento_operador", label: "Treinamento", color: "#5AC8FA" },
  ];

  return (
    <div className="space-y-6">
      {/* Tecnico hint */}
      {isTecnico && (
        <p className="text-[12px] text-apple-tertiary px-1">
          Visualização somente leitura — fases gerenciadas pela engenharia. Clique em um projeto para executar tarefas.
        </p>
      )}

      {/* Anaclara Risk Alert */}
      {anaclara && !isTecnico && (
        <div className="apple-card p-5 border-l-4 border-apple-red">
          <div className="flex items-center gap-3 mb-2">
            <AlertTriangle size={18} className="text-apple-red" />
            <h3 className="text-[15px] font-semibold text-apple-label">
              Risco Crítico: Anaclara Alimentos
            </h3>
          </div>
          <p className="text-[13px] text-apple-secondary">
            R$ 780.000 em risco contratual · Prazo: junho/2026 · {anaclara.dias_restantes ?? 44} dias restantes
          </p>
        </div>
      )}

      {/* Kanban Board */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {columns.map((col) => {
          const items: any[] = Array.isArray(kanbanData?.[col.key]) ? kanbanData[col.key] : [];

          return (
            <div key={col.key} className="space-y-2">
              {/* Column header */}
              <div className="flex items-center justify-between px-1 mb-1">
                <div className="flex items-center gap-2">
                  <div
                    className="w-2.5 h-2.5 rounded-full"
                    style={{ backgroundColor: col.color }}
                  />
                  <span className="text-[13px] font-semibold text-apple-label">
                    {col.label}
                  </span>
                </div>
                <span className="text-[12px] font-semibold text-apple-tertiary bg-apple-surface-2 px-2 py-0.5 rounded-full">
                  {items.length}
                </span>
              </div>

              {/* Cards */}
              <div className="space-y-2">
                {items.map((item: any, i: number) => (
                  <button
                    type="button"
                    key={item.id ?? i}
                    onClick={() => handleClick(item)}
                    className={`w-full text-left apple-card p-4 hover:shadow-md transition-shadow ${
                      (item.id_projeto && (isTecnico || user?.perfil === "engenharia" || (isVendedor && isEditable(item))))
                        ? "cursor-pointer"
                        : "cursor-not-allowed opacity-80"
                    }`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <p className="text-[13px] font-semibold text-apple-label">
                        {item.maquina_codigo ?? `COM-${i + 1}`}
                      </p>
                      {item.risco_cancelamento && (
                        <AlertTriangle size={14} className="text-apple-red flex-shrink-0" />
                      )}
                    </div>

                    <p className="text-[12px] text-apple-tertiary mb-3 truncate">
                      {item.cliente_nome ?? "—"}
                    </p>

                    <div className="space-y-1.5 text-[11px]">
                      {item.engenheiro_responsavel && (
                        <div className="flex items-center gap-1.5 text-apple-secondary">
                          <User size={11} className="text-apple-quaternary" />
                          {item.engenheiro_responsavel}
                        </div>
                      )}
                      {(item.dias_atraso ?? 0) > 0 && (
                        <div className="flex items-center gap-1.5 text-apple-red font-semibold">
                          <Clock size={11} />
                          {item.dias_atraso} dias de atraso
                        </div>
                      )}
                      {item.valor_contrato && (
                        <div className="flex items-center gap-1.5 text-apple-secondary">
                          <DollarSign size={11} className="text-apple-quaternary" />
                          R$ {Number(item.valor_contrato).toLocaleString("pt-BR")}
                        </div>
                      )}
                    </div>
                  </button>
                ))}

                {items.length === 0 && (
                  <div className="p-6 rounded-2xl border-2 border-dashed border-apple-separator text-center">
                    <p className="text-[12px] text-apple-quaternary">Nenhum item</p>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {projetoAberto && (
        <TecnicoProjetoDrawer projetoId={projetoAberto} onClose={() => setProjetoAberto(null)} />
      )}
    </div>
  );
}
