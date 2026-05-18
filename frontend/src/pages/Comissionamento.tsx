/**
 * AltaCLP Intelligence — Comissionamento Page
 * Kanban-style commissioning backlog
 */

import { useQuery } from "@tanstack/react-query";
import { comissionamentoApi } from "@/services/api";
import {
  Wrench,
  AlertTriangle,
  Clock,
  CheckCircle,
  Loader2,
  Calendar,
  DollarSign,
  User,
} from "lucide-react";

const statusLabels: Record<string, { label: string; color: string; bg: string }> = {
  aguardando_dados: { label: "Aguardando Dados", color: "text-apple-orange", bg: "bg-apple-orange/10" },
  em_andamento: { label: "Em Andamento", color: "text-apple-blue", bg: "bg-apple-blue/10" },
  fat_pendente: { label: "FAT Pendente", color: "text-apple-purple", bg: "bg-apple-purple/10" },
  treinamento_operador: { label: "Treinamento", color: "text-apple-teal", bg: "bg-apple-teal/10" },
  concluido: { label: "Concluído", color: "text-apple-green", bg: "bg-apple-green/10" },
  cancelado: { label: "Cancelado", color: "text-apple-red", bg: "bg-apple-red/10" },
};

export default function Comissionamento() {
  const { data: kanban, isLoading: loadingKanban } = useQuery({
    queryKey: ["comissionamento-kanban"],
    queryFn: () => comissionamentoApi.getKanban().then((r) => r.data),
  });

  const { data: anaclara } = useQuery({
    queryKey: ["comissionamento-anaclara"],
    queryFn: () => comissionamentoApi.getRiscoAnaclara().then((r) => r.data).catch(() => null),
  });

  if (loadingKanban) {
    return (
      <div className="flex items-center justify-center py-32">
        <Loader2 className="animate-spin text-apple-blue" size={32} />
      </div>
    );
  }

  // Extract kanban columns
  const columns = [
    { key: "aguardando_dados", label: "Aguardando Dados", color: "#FF9500" },
    { key: "em_andamento", label: "Em Andamento", color: "#007AFF" },
    { key: "fat_pendente", label: "FAT Pendente", color: "#AF52DE" },
    { key: "treinamento_operador", label: "Treinamento", color: "#5AC8FA" },
  ];

  return (
    <div className="space-y-6">
      {/* Anaclara Risk Alert */}
      {anaclara && (
        <div className="apple-card p-5 border-l-4 border-apple-red">
          <div className="flex items-center gap-3 mb-2">
            <AlertTriangle size={18} className="text-apple-red" />
            <h3 className="text-[15px] font-semibold text-apple-label">
              Risco Crítico: Anaclara Alimentos
            </h3>
          </div>
          <p className="text-[13px] text-apple-secondary">
            R$ 780.000 em risco contratual · Prazo: junho/2026 · {anaclara.dias_restantes || 44} dias restantes
          </p>
        </div>
      )}

      {/* Kanban Board */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {columns.map((col) => {
          const items = kanban?.[col.key] || [];

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
                  {Array.isArray(items) ? items.length : 0}
                </span>
              </div>

              {/* Cards */}
              <div className="space-y-2">
                {(Array.isArray(items) ? items : []).map((item: any, i: number) => (
                  <div
                    key={item.id || i}
                    className="apple-card p-4 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <p className="text-[13px] font-semibold text-apple-label">
                        {item.maquina_codigo || `COM-${i + 1}`}
                      </p>
                      {item.risco_cancelamento && (
                        <AlertTriangle size={14} className="text-apple-red flex-shrink-0" />
                      )}
                    </div>

                    <p className="text-[12px] text-apple-tertiary mb-3 truncate">
                      {item.cliente_nome || "—"}
                    </p>

                    <div className="space-y-1.5 text-[11px]">
                      {item.engenheiro_responsavel && (
                        <div className="flex items-center gap-1.5 text-apple-secondary">
                          <User size={11} className="text-apple-quaternary" />
                          {item.engenheiro_responsavel}
                        </div>
                      )}
                      {(item.dias_atraso !== undefined && item.dias_atraso > 0) && (
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
                  </div>
                ))}

                {(!Array.isArray(items) || items.length === 0) && (
                  <div className="p-6 rounded-2xl border-2 border-dashed border-apple-separator text-center">
                    <p className="text-[12px] text-apple-quaternary">Nenhum item</p>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
