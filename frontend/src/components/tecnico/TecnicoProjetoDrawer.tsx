/**
 * Drawer de execução do técnico — checklist, upload, submissão.
 */

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { projectsApi } from "@/services/api";
import { useToast } from "@/components/Toast";
import { Send, Loader2, X, UploadCloud, Cpu, CheckCircle } from "lucide-react";
import AIChatWidget from "@/components/AIChatWidget";

interface Props {
  projetoId: string;
  onClose: () => void;
}

export default function TecnicoProjetoDrawer({ projetoId, onClose }: Props) {
  const { addToast } = useToast();
  const qc = useQueryClient();
  const [uploading, setUploading] = useState(false);

  const { data: projeto, isLoading: isLoadingProj } = useQuery({
    queryKey: ["projeto", projetoId],
    queryFn: () => projectsApi.get(projetoId).then((r) => r.data),
  });

  const { data: pendencias = [], isLoading: isLoadingTasks } = useQuery({
    queryKey: ["projeto-tasks", projetoId],
    queryFn: () => projectsApi.tasks(projetoId).then((r) => r.data),
  });

  const isLoading = isLoadingProj || isLoadingTasks;

  const toggleTarefa = async (pendenciaId: string, current: boolean) => {
    try {
      await projectsApi.updateTask(projetoId, pendenciaId, { concluida: !current });
      qc.invalidateQueries({ queryKey: ["projeto-tasks", projetoId] });
      qc.invalidateQueries({ queryKey: ["projeto", projetoId] });
      addToast(current ? "Tarefa reaberta" : "Tarefa concluída", "success");
    } catch {
      addToast("Erro ao atualizar tarefa", "error");
    }
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    const fd = new FormData();
    fd.append("file", file);
    try {
      await projectsApi.uploadDocument(projetoId, fd);
      addToast("Documento enviado", "success");
    } catch {
      addToast("Falha no upload", "error");
    } finally {
      setUploading(false);
    }
  };

  const submeter = async () => {
    try {
      const r = await projectsApi.submitValidation(projetoId);
      qc.invalidateQueries({ queryKey: ["comissionamento-kanban"] });
      qc.invalidateQueries({ queryKey: ["app-state"] });
      addToast(
        r.data.new_status
          ? `Projeto submetido (${r.data.new_status})`
          : "Submetido para validação",
        "success"
      );
      onClose();
    } catch {
      addToast("Erro na submissão", "error");
    }
  };

  if (isLoading) {
    return (
      <div className="fixed inset-0 z-50 bg-black/20 flex justify-end">
        <div className="w-full max-w-[400px] bg-[#f5f5f7] h-full flex items-center justify-center">
          <Loader2 className="animate-spin text-apple-blue" size={32} />
        </div>
      </div>
    );
  }

  const concluidas = pendencias.filter((p: any) => p.concluida).length;
  const total = pendencias.length;

  return (
    <div className="fixed inset-0 z-50 bg-black/20 flex justify-end">
      <div className="w-full max-w-[400px] bg-[#f5f5f7] h-full overflow-y-auto shadow-2xl flex flex-col">
        <div className="p-6 pb-4 border-b border-black/5 bg-white flex justify-between items-start">
          <div>
            <h2 className="text-[18px] font-semibold text-apple-label leading-tight">{projeto?.nome_contrato}</h2>
            <p className="text-[12px] text-apple-tertiary mt-1">
              {projeto?.id} | Status: <span className="font-medium">{projeto?.status}</span>
            </p>
          </div>
          <button type="button" onClick={onClose} className="p-2 rounded-full bg-black/5 hover:bg-black/10 transition-colors">
            <X size={16} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          <div className="apple-card p-4 shadow-sm border border-black/5">
            <div className="flex justify-between items-end mb-2">
              <p className="text-[13px] font-medium text-apple-label">Progresso Geral</p>
              <p className="text-[12px] text-apple-tertiary">{projeto?.progresso ?? 0}%</p>
            </div>
            <div className="w-full h-2 bg-apple-surface-2 rounded-full overflow-hidden">
              <div className="h-full bg-apple-blue transition-all duration-500 ease-out" style={{ width: `${projeto?.progresso || 0}%` }} />
            </div>
          </div>

          <div className="space-y-3">
            <h3 className="text-[14px] font-semibold text-apple-label flex items-center gap-2">
              <CheckCircle size={16} className="text-apple-blue" />
              Checklist de Calibração ({concluidas}/{total})
            </h3>
            <div className="space-y-2">
              {pendencias.map((p: any) => (
                <label key={p.id} className="apple-card p-3 flex gap-3 items-center cursor-pointer hover:border-apple-blue/50 transition-colors border border-transparent shadow-sm">
                  <input type="checkbox" className="w-4 h-4 rounded border-black/20 text-apple-blue focus:ring-apple-blue" checked={p.concluida} onChange={() => toggleTarefa(p.id, p.concluida)} />
                  <span className={`text-[13px] ${p.concluida ? "line-through text-apple-tertiary" : "text-apple-label"}`}>{p.titulo}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="space-y-3">
            <h3 className="text-[14px] font-semibold text-apple-label">Validação & Handover</h3>
            <div className="apple-card p-5 border border-dashed border-black/10 flex flex-col items-center justify-center gap-2 hover:bg-black/5 transition-colors cursor-pointer relative">
              <input type="file" accept="image/*,.pdf" onChange={handleUpload} disabled={uploading} className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" />
              <UploadCloud size={24} className="text-apple-tertiary" />
              <div className="text-center">
                <p className="text-[13px] font-medium text-apple-label">Anexar Documento</p>
                <p className="text-[11px] text-apple-tertiary">Certificados, relatórios ou laudos</p>
              </div>
            </div>

            <button type="button" onClick={submeter} className="w-full apple-btn apple-btn-secondary flex justify-center gap-2 items-center text-[13px]">
              <Cpu size={16} /> Gerar Parecer de Engenharia (IA)
            </button>
          </div>

          <div className="pt-4 border-t border-black/5">
             <AIChatWidget
                title="Assistente de Calibração"
                placeholder="Como calibrar este equipamento?"
                onSend={async (msg) => {
                  return "Com base no manual técnico oficial, o processo é o seguinte...";
                }}
              />
          </div>
        </div>

        <div className="p-6 border-t border-black/5 bg-white">
          <button type="button" onClick={submeter} className="w-full apple-btn apple-btn-primary flex justify-center gap-2 items-center">
            <Send size={16} /> Submeter para Handover
          </button>
        </div>
      </div>
    </div>
  );
}