/**
 * Painel lateral do técnico — análise IA + registro de intervenção.
 */

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { tecnicoApi } from "@/services/api";
import { useToast } from "@/components/Toast";
import { Loader2 } from "lucide-react";

const TIPOS_ACAO = [
  { value: "visita_campo", label: "Visita em Campo" },
  { value: "acesso_remoto", label: "Acesso Remoto" },
  { value: "falso_alarme", label: "Falso Alarme" },
];

interface Props {
  alertaId: string;
  titulo?: string;
  onClose: () => void;
}

export default function TecnicoAlertPanel({ alertaId, titulo, onClose }: Props) {
  const { addToast } = useToast();
  const [tipoAcao, setTipoAcao] = useState("visita_campo");
  const [comentario, setComentario] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const { data: analise, isLoading } = useQuery({
    queryKey: ["tecnico-alerta-analise", alertaId],
    queryFn: () => tecnicoApi.analiseAlerta(alertaId).then((r) => r.data),
  });

  const registrar = async () => {
    if (!comentario.trim()) {
      addToast("Descreva a ação planejada", "warning");
      return;
    }
    setSubmitting(true);
    try {
      await tecnicoApi.registrarIntervencao(alertaId, {
        tipo_acao: tipoAcao,
        comentario_tecnico: comentario,
      });
      addToast("Ação registrada para revisão da engenharia", "success");
      onClose();
    } catch {
      addToast("Erro ao registrar ação", "error");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <aside className="w-[360px] flex-shrink-0 apple-card p-5 space-y-4 sticky top-4 self-start max-h-[calc(100vh-120px)] overflow-y-auto">
      <div className="flex justify-between items-start">
        <h3 className="text-[15px] font-semibold text-apple-label">Análise do Alarme</h3>
        <button type="button" onClick={onClose} className="text-[12px] text-apple-tertiary">
          Fechar
        </button>
      </div>
      {titulo && <p className="text-[13px] font-medium text-apple-secondary">{titulo}</p>}
      {isLoading ? (
        <Loader2 className="animate-spin text-apple-blue mx-auto" size={24} />
      ) : (
        <p className="text-[13px] text-apple-secondary leading-relaxed whitespace-pre-wrap">
          {analise?.texto_analise}
        </p>
      )}
      <div className="pt-3 border-t border-apple-separator/30 space-y-3">
        <p className="text-[12px] font-semibold text-apple-label">Registrar Ação</p>
        <select
          value={tipoAcao}
          onChange={(e) => setTipoAcao(e.target.value)}
          className="w-full px-3 py-2 rounded-lg bg-apple-surface-1 text-[13px]"
        >
          {TIPOS_ACAO.map((t) => (
            <option key={t.value} value={t.value}>
              {t.label}
            </option>
          ))}
        </select>
        <textarea
          value={comentario}
          onChange={(e) => setComentario(e.target.value)}
          placeholder="Descreva a ação planejada..."
          rows={4}
          className="w-full px-3 py-2 rounded-lg bg-apple-surface-1 text-[13px] resize-none"
        />
        <button
          type="button"
          disabled={submitting}
          onClick={registrar}
          className="w-full apple-btn apple-btn-primary text-[13px] disabled:opacity-50"
        >
          {submitting ? "Registrando..." : "Registrar Ação"}
        </button>
      </div>
    </aside>
  );
}
