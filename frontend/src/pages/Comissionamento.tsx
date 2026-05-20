/**
 * AltaCLP Intelligence — Comissionamento Page
 * Kanban-style commissioning backlog — dados ao vivo da API + WebSocket
 */

import { useState, useEffect, useRef } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { comissionamentoApi, tecnicoApi } from "@/services/api";
import { useTecnico } from "@/hooks/useTecnico";
import { useSearchParams } from "react-router-dom";
import { useAppData } from "@/contexts/AppDataContext";
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

const EMPTY_KANBAN: Record<string, unknown[]> = {
  aguardando_dados: [],
  em_andamento: [],
  fat_pendente: [],
  treinamento_operador: [],
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
  const { refresh: refreshAppData } = useAppData();
  const queryClient = useQueryClient();
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const projetoParam = searchParams.get("projeto");
    const openParam = searchParams.get("open");
    if (projetoParam && openParam === "true") {
      setProjetoAberto(projetoParam);
    }
  }, [searchParams]);

  const { data: kanban, isLoading: loadingKanban, isError: kanbanError, refetch } = useQuery({
    queryKey: ["comissionamento-kanban"],
    queryFn: () => comissionamentoApi.getKanban().then((r) => r.data),
    retry: 1,
    refetchOnMount: true,
    refetchInterval: 15000,
  });

  const { data: anaclara } = useQuery({
    queryKey: ["comissionamento-anaclara"],
    queryFn: () => comissionamentoApi.getRiscoAnaclara().then((r) => r.data).catch(() => null),
  });

  // WebSocket: engenharia recebe project:new em tempo real
  useEffect(() => {
    const perfil = user?.perfil;
    if (!perfil || !["engenharia", "ceo", "cfo"].includes(perfil)) return;

    const token = localStorage.getItem("altaclp_token");
    if (!token) return;

    const url = tecnicoApi.notificacoesWsUrl();
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data);
        if (msg.evento === "project:new") {
          console.log("[10] FRONTEND (Commissioning): project:new received —", msg.project?.id);
          refetch();
          refreshAppData();
          queryClient.invalidateQueries({ queryKey: ["comissionamento-kanban"] });
        }
        if (msg.evento === "project:status_changed") {
          refetch();
          refreshAppData();
        }
      } catch {
        /* ignore */
      }
    };

    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, [user?.perfil, refetch, refreshAppData, queryClient]);

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

  if (loadingKanban) {
    return (
      <MotionlessLoader />
    );
  }

  if (kanbanError) {
    return (
      <MotionlessError refetch={refetch} />
    );
  }

  const kanbanData =
    kanban && typeof kanban === "object" && !Array.isArray(kanban) ? kanban : EMPTY_KANBAN;

  const columns = [
    { key: "aguardando_dados", label: "Aguardando Dados", color: "#FF9500" },
    { key: "em_andamento", label: "Em Andamento", color: "#007AFF" },
    { key: "fat_pendente", label: "FAT Pendente", color: "#AF52DE" },
    { key: "treinamento_operador", label: "Treinamento", color: "#5AC8FA" },
  ];

  return (
    <MotionlessContent
      isTecnico={isTecnico}
      anaclara={anaclara}
      columns={columns}
      kanbanData={kanbanData}
      handleClick={handleClick}
      isEditable={isEditable}
      isTecnicoOrEng={isTecnico || user?.perfil === "engenharia"}
      isVendedor={isVendedor}
      projetoAberto={projetoAberto}
      setProjetoAberto={setProjetoAberto}
    />
  );
}

function MotionlessLoader() {
  return (
    <MotionlessLoaderInner />
  );
}

function MotionlessLoaderInner() {
  return (
    <MotionlessLoaderBlock />
  );
}

function MotionlessLoaderBlock() {
  return (
    <div className="flex flex-col items-center justify-center py-32 gap-4">
      <Loader2 className="animate-spin text-apple-blue" size={36} />
      <p className="text-[14px] text-apple-tertiary">Carregando painel de comissionamento…</p>
    </div>
  );
}

function MotionlessError({ refetch }: { refetch: () => void }) {
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
    </div>
  );
}

function MotionlessContent(props: {
  isTecnico: boolean;
  anaclara: any;
  columns: { key: string; label: string; color: string }[];
  kanbanData: Record<string, unknown[]>;
  handleClick: (item: any) => void;
  isEditable: (item: any) => boolean;
  isTecnicoOrEng: boolean;
  isVendedor: boolean;
  projetoAberto: string | null;
  setProjetoAberto: (id: string | null) => void;
}) {
  const {
    isTecnico,
    anaclara,
    columns,
    kanbanData,
    handleClick,
    isEditable,
    isTecnicoOrEng,
    isVendedor,
    projetoAberto,
    setProjetoAberto,
  } = props;

  return (
    <MotionlessContentInner
      isTecnico={isTecnico}
      anaclara={anaclara}
      columns={columns}
      kanbanData={kanbanData}
      handleClick={handleClick}
      isEditable={isEditable}
      isTecnicoOrEng={isTecnicoOrEng}
      isVendedor={isVendedor}
      projetoAberto={projetoAberto}
      setProjetoAberto={setProjetoAberto}
    />
  );
}

function MotionlessContentInner(props: {
  isTecnico: boolean;
  anaclara: any;
  columns: { key: string; label: string; color: string }[];
  kanbanData: Record<string, unknown[]>;
  handleClick: (item: any) => void;
  isEditable: (item: any) => boolean;
  isTecnicoOrEng: boolean;
  isVendedor: boolean;
  projetoAberto: string | null;
  setProjetoAberto: (id: string | null) => void;
}) {
  const {
    isTecnico,
    anaclara,
    columns,
    kanbanData,
    handleClick,
    isEditable,
    isTecnicoOrEng,
    isVendedor,
    projetoAberto,
    setProjetoAberto,
  } = props;

  return (
    <div className="space-y-6">
      {isTecnico && (
        <p className="text-[12px] text-apple-tertiary px-1">
          Visualização somente leitura — fases gerenciadas pela engenharia. Clique em um projeto para executar tarefas.
        </p>
      )}

      {anaclara && !isTecnico && (
        <MotionlessAnaclara anaclara={anaclara} />
      )}

      <MotionlessKanban
        columns={columns}
        kanbanData={kanbanData}
        handleClick={handleClick}
        isEditable={isEditable}
        isTecnicoOrEng={isTecnicoOrEng}
        isVendedor={isVendedor}
        isTecnico={isTecnico}
      />

      {projetoAberto && (
        <TecnicoProjetoDrawer projetoId={projetoAberto} onClose={() => setProjetoAberto(null)} />
      )}
    </div>
  );
}

function MotionlessAnaclara({ anaclara }: { anaclara: any }) {
  return (
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
  );
}

function MotionlessKanban(props: {
  columns: { key: string; label: string; color: string }[];
  kanbanData: Record<string, unknown[]>;
  handleClick: (item: any) => void;
  isEditable: (item: any) => boolean;
  isTecnicoOrEng: boolean;
  isVendedor: boolean;
  isTecnico: boolean;
}) {
  const { columns, kanbanData, handleClick, isEditable, isTecnicoOrEng, isVendedor, isTecnico } = props;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
      {columns.map((col) => {
        const items: any[] = Array.isArray(kanbanData?.[col.key]) ? (kanbanData[col.key] as any[]) : [];

        return (
          <div key={col.key} className="space-y-2">
            <div className="flex items-center justify-between px-1 mb-1">
              <MotionlessColHeader col={col} />
              <span className="text-[12px] font-semibold text-apple-tertiary bg-apple-surface-2 px-2 py-0.5 rounded-full">
                {items.length}
              </span>
            </div>

            <div className="space-y-2">
              {items.map((item: any, i: number) => (
                <button
                  type="button"
                  key={item.id ?? item.id_projeto ?? i}
                  onClick={() => handleClick(item)}
                  className={`w-full text-left apple-card p-4 hover:shadow-md transition-shadow ${
                    item.id_projeto && (isTecnico || isTecnicoOrEng || (isVendedor && isEditable(item)))
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

                  <MotionlessCardMeta item={item} />
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
  );
}

function MotionlessColHeader({ col }: { col: { label: string; color: string } }) {
  return (
    <div className="flex items-center gap-2">
      <MotionlessDot color={col.color} />
      <span className="text-[13px] font-semibold text-apple-label">{col.label}</span>
    </div>
  );
}

function MotionlessDot({ color }: { color: string }) {
  return <MotionlessDotInner color={color} />;
}

function MotionlessDotInner({ color }: { color: string }) {
  return (
    <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: color }} />
  );
}

function MotionlessCardMeta({ item }: { item: any }) {
  return (
    <div className="space-y-1.5 text-[11px]">
      {item.engenheiro_responsavel && (
        <div className="flex items-center gap-1.5 text-apple-secondary">
          <User size={11} className="text-apple-quaternary" />
          {item.engenheiro_responsavel}
        </div>
      )}
      {(item.dias_atraso ?? 0) > 0 && (
        <MotionlessAtraso dias={item.dias_atraso} />
      )}
      {item.valor_contrato != null && (
        <div className="flex items-center gap-1.5 text-apple-secondary">
          <DollarSign size={11} className="text-apple-quaternary" />
          R$ {Number(item.valor_contrato).toLocaleString("pt-BR")}
        </div>
      )}
    </div>
  );
}

function MotionlessAtraso({ dias }: { dias: number }) {
  return (
    <div className="flex items-center gap-1.5 text-apple-red font-semibold">
      <Clock size={11} />
      {dias} dias de atraso
    </div>
  );
}
