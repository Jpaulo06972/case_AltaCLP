/**
 * Drawer de execução do técnico — checklist, upload, submissão condicional por etapas.
 */

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import api, { projectsApi, tecnicoApi } from "@/services/api";
import { useToast } from "@/components/Toast";
import {
  Send,
  Loader2,
  X,
  UploadCloud,
  Cpu,
  CheckCircle,
  FileText,
  FileCheck,
  CheckCircle2,
  Clock
} from "lucide-react";
import AIChatWidget from "@/components/AIChatWidget";
import { useAuth } from "@/contexts/AuthContext";

interface Props {
  projetoId: string;
  onClose: () => void;
}

export default function TecnicoProjetoDrawer({ projetoId, onClose }: Props) {
  const { addToast } = useToast();
  const { user } = useAuth();
  const qc = useQueryClient();
  const [uploading, setUploading] = useState(false);
  
  // Stages local approvals
  const [docsReviewed, setDocsReviewed] = useState(false);
  const [invoiceApproved, setInvoiceApproved] = useState(false);

  const { data: projeto, isLoading: isLoadingProj } = useQuery({
    queryKey: ["projeto", projetoId],
    queryFn: () => projectsApi.get(projetoId).then((r) => r.data),
  });

  const { data: pendencias = [], isLoading: isLoadingTasks } = useQuery({
    queryKey: ["projeto-tasks", projetoId],
    queryFn: () => projectsApi.tasks(projetoId).then((r) => r.data),
  });

  const { data: documents = [], isLoading: isLoadingDocs } = useQuery({
    queryKey: ["projeto-documents", projetoId],
    queryFn: () => projectsApi.documents(projetoId).then((r) => r.data),
  });

  const { data: machines = [] } = useQuery({
    queryKey: ["projeto-machines", projetoId],
    queryFn: () => projectsApi.machines(projetoId).then((r) => r.data),
  });

  const isLoading = isLoadingProj || isLoadingTasks || isLoadingDocs;

  const getDocUrl = (url: string) => {
    if (url.startsWith("http")) return url;
    const baseUrl = (import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1").replace("/api/v1", "");
    return `${baseUrl}${url}`;
  };

  const handleDownloadScopeDoc = async () => {
    try {
      const response = await projectsApi.downloadScopeDocument(projetoId);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `Escopo_Tecnico_${projetoId}.md`);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
      addToast("Escopo técnico baixado com sucesso", "success");
    } catch {
      addToast("Erro ao baixar escopo técnico", "error");
    }
  };

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
      qc.invalidateQueries({ queryKey: ["projeto-documents", projetoId] });
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
      qc.invalidateQueries({ queryKey: ["projeto", projetoId] });
      addToast(
        r.data.new_status
          ? `Status atualizado: ${r.data.new_status}`
          : "Submetido com sucesso",
        "success"
      );
      onClose();
    } catch (err: any) {
      const errMsg = err.response?.data?.detail || "Erro na submissão";
      addToast(errMsg, "error");
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
              {projeto?.id} | Status: <span className="font-medium text-apple-blue">{projeto?.status}</span>
            </p>
          </div>
          <button type="button" onClick={onClose} className="p-2 rounded-full bg-black/5 hover:bg-black/10 transition-colors">
            <X size={16} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          
          {/* General Progress Card - Hide in Awaiting Data and Operator Training stages */}
          {projeto?.comiss_status !== "aguardando_dados" && projeto?.comiss_status !== "treinamento_operador" && (
            <div className="apple-card p-4 shadow-sm border border-black/5">
              <div className="flex justify-between items-end mb-2">
                <p className="text-[13px] font-medium text-apple-label">Progresso Geral</p>
                <p className="text-[12px] text-apple-tertiary">{projeto?.progresso ?? 0}%</p>
              </div>
              <div className="w-full h-2 bg-apple-surface-2 rounded-full overflow-hidden">
                <div className="h-full bg-apple-blue transition-all duration-500 ease-out" style={{ width: `${projeto?.progresso || 0}%` }} />
              </div>
            </div>
          )}

          {/* BOM Section - Always show if present */}
          {projeto?.bom_json && projeto.bom_json.length > 0 && (
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <h3 className="text-[14px] font-semibold text-apple-label flex items-center gap-2">
                  <FileText size={16} className="text-apple-blue" />
                  Lista de Materiais (BOM)
                </h3>
                <button
                  type="button"
                  onClick={handleDownloadScopeDoc}
                  className="text-[12px] text-apple-blue hover:underline flex items-center gap-1 font-medium bg-transparent border-none cursor-pointer"
                >
                  Download Escopo (.MD)
                </button>
              </div>
              <div className="bg-white rounded-2xl p-4 border border-black/5 divide-y divide-black/5 max-h-[220px] overflow-y-auto shadow-sm">
                {projeto.bom_json.map((item: any, idx: number) => (
                  <div key={idx} className="py-2 flex justify-between items-start text-[12px] first:pt-0 last:pb-0">
                    <div className="min-w-0 flex-1 pr-2">
                      <p className="font-semibold text-apple-label truncate">{item.descricao}</p>
                      <p className="text-[11px] text-apple-tertiary font-mono">{item.codigo}</p>
                    </div>
                    <div className="text-right flex-shrink-0">
                      <span className="inline-block px-1.5 py-0.5 bg-[#f5f5f7] text-apple-secondary rounded text-[11px] font-mono">
                        {item.quantidade}x {item.unidade || "pç"}
                      </span>
                      <p className="text-[11px] text-apple-secondary mt-0.5">
                        R$ {((item.valor_unit || 0) * (item.quantidade || 1)).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* STAGE 1: aguardando_dados */}
          {projeto?.comiss_status === "aguardando_dados" && (
            <div className="space-y-4">
              <div className="apple-card p-5 border border-apple-orange/20 bg-apple-orange/5 rounded-2xl shadow-sm space-y-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-apple-orange/10 flex items-center justify-center text-apple-orange flex-shrink-0">
                    <FileText size={20} />
                  </div>
                  <div>
                    <h4 className="text-[14px] font-bold text-apple-label">Aprovação de Documentação</h4>
                    <p className="text-[11px] text-apple-tertiary">Etapa Inicial de Validação</p>
                  </div>
                </div>
                
                <p className="text-[12px] text-apple-secondary leading-relaxed">
                  Confirme que a documentação técnica foi revisada e que todos os dados iniciais estão corretos para liberar a equipe de campo para o comissionamento físico.
                </p>

                <label className="flex gap-3 items-center p-3.5 bg-white hover:border-apple-orange/50 rounded-xl border border-black/5 transition-all cursor-pointer shadow-sm mt-2 select-none">
                  <input
                    type="checkbox"
                    className="w-4 h-4 rounded border-black/20 text-apple-orange focus:ring-apple-orange cursor-pointer"
                    checked={docsReviewed}
                    onChange={(e) => setDocsReviewed(e.target.checked)}
                  />
                  <span className="text-[12.5px] font-semibold text-apple-label leading-tight">
                    Confirmo que a documentação foi revisada e aprovada
                  </span>
                </label>
              </div>
            </div>
          )}

          {/* STAGE 2: em_andamento */}
          {(!projeto?.comiss_status || projeto?.comiss_status === "em_andamento") && (
            <>
              {/* Calibration Checklist */}
              <div className="space-y-3">
                <h3 className="text-[14px] font-semibold text-apple-label flex items-center gap-2">
                  <CheckCircle size={16} className="text-apple-blue" />
                  Checklist de Calibração ({concluidas}/{total})
                </h3>
                <div className="space-y-2">
                  {pendencias.map((p: any) => (
                    <label key={p.id} className="apple-card p-3 flex gap-3 items-center cursor-pointer hover:border-apple-blue/50 transition-colors border border-transparent shadow-sm">
                      <input type="checkbox" className="w-4 h-4 rounded border-black/20 text-apple-blue focus:ring-apple-blue cursor-pointer" checked={p.concluida} onChange={() => toggleTarefa(p.id, p.concluida)} />
                      <span className={`text-[13px] ${p.concluida ? "line-through text-apple-tertiary" : "text-apple-label"}`}>{p.titulo}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Handover Upload & Opinions */}
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

                {documents.length > 0 && (
                  <div className="space-y-2 mt-3">
                    <p className="text-[12px] font-semibold text-apple-secondary uppercase tracking-wider">Documentos Enviados</p>
                    <div className="space-y-2">
                      {documents.map((doc: any) => (
                        <a
                          key={doc.id}
                          href={getDocUrl(doc.url_documento)}
                          target="_blank"
                          rel="noreferrer"
                          className="apple-card p-3 flex items-center justify-between hover:border-apple-blue/50 transition-colors border border-transparent shadow-sm bg-white"
                        >
                          <div className="flex items-center gap-3 min-w-0">
                            <div className="w-8 h-8 rounded-lg bg-apple-blue/10 flex items-center justify-center flex-shrink-0">
                              <FileText size={16} className="text-apple-blue" />
                            </div>
                            <div className="min-w-0">
                              <p className="text-[12px] font-semibold text-apple-label truncate">{doc.nome_arquivo}</p>
                              <p className="text-[10px] text-apple-tertiary">
                                {doc.data ? new Date(doc.data).toLocaleDateString("pt-BR") : "Recém enviado"}
                              </p>
                            </div>
                          </div>
                          <span className="text-[11px] text-apple-blue font-medium hover:underline">Visualizar</span>
                        </a>
                      ))}
                    </div>
                  </div>
                )}

                <button type="button" onClick={submeter} className="w-full apple-btn apple-btn-secondary flex justify-center gap-2 items-center text-[13px]">
                  <Cpu size={16} /> Gerar Parecer de Engenharia (IA)
                </button>
              </div>

              {/* RAG Chat Assistant */}
              <div className="pt-4 border-t border-black/5">
                 <AIChatWidget
                    title="Assistente de Calibração"
                    placeholder="Como calibrar este equipamento?"
                    onSend={async (msg) => {
                      const res = await tecnicoApi.chatInstalacao({
                        mensagem: msg,
                        maquina_id: machines?.[0]?.id || undefined,
                        modo: "calibracao",
                      });
                      return res.data.resposta || res.data.texto || res.data;
                    }}
                  />
              </div>
            </>
          )}

          {/* STAGE 3: fat_pendente */}
          {projeto?.comiss_status === "fat_pendente" && (
            <div className="space-y-4">
              {user?.perfil === "engenharia" || user?.perfil === "ceo" ? (
                <div className="apple-card p-5 border border-apple-purple/20 bg-apple-purple/5 rounded-2xl shadow-sm space-y-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-apple-purple/10 flex items-center justify-center text-apple-purple flex-shrink-0">
                      <FileCheck size={20} />
                    </div>
                    <div>
                      <h4 className="text-[14px] font-bold text-apple-label">Aprovação de Engenharia</h4>
                      <p className="text-[11px] text-apple-tertiary">Fase de Faturamento & FAT</p>
                    </div>
                  </div>
                  
                  <p className="text-[12px] text-apple-secondary leading-relaxed">
                    Você tem permissão para aprovar esta etapa. Confirme a liberação do comissionamento técnico para prosseguir para o treinamento operacional da equipe do cliente.
                  </p>

                  <label className="flex gap-3 items-center p-3.5 bg-white hover:border-apple-purple/50 rounded-xl border border-black/5 transition-all cursor-pointer shadow-sm mt-2 select-none">
                    <input
                      type="checkbox"
                      className="w-4 h-4 rounded border-black/20 text-apple-purple focus:ring-apple-purple cursor-pointer"
                      checked={invoiceApproved}
                      onChange={(e) => setInvoiceApproved(e.target.checked)}
                    />
                    <span className="text-[12.5px] font-semibold text-apple-label leading-tight">
                      Aprovar Comissionamento e Avançar para Treinamento
                    </span>
                  </label>
                </div>
              ) : (
                <div className="apple-card p-6 border border-black/10 bg-white rounded-2xl shadow-sm flex flex-col items-center justify-center text-center py-8 gap-3">
                  <Clock size={36} className="text-apple-purple animate-pulse" />
                  <h4 className="text-[14.5px] font-bold text-apple-label">Validação de Faturamento Pendente</h4>
                  <p className="text-[12.5px] text-apple-secondary max-w-[280px] leading-relaxed">
                    Esta etapa aguarda a aprovação formal de um <strong>engenheiro da AltaCLP</strong> ou administrador para liberação financeira e início do treinamento do operador.
                  </p>
                </div>
              )}
            </div>
          )}

          {/* STAGE 4: treinamento_operador */}
          {projeto?.comiss_status === "treinamento_operador" && (
            <div className="apple-card p-6 border border-apple-green/20 bg-apple-green/5 rounded-2xl shadow-sm flex flex-col items-center justify-center text-center py-8 gap-3">
              <CheckCircle2 size={36} className="text-apple-green" />
              <h4 className="text-[15px] font-bold text-apple-label">Comissionamento Concluído</h4>
              <p className="text-[12.5px] text-apple-secondary max-w-[280px] leading-relaxed">
                O comissionamento físico e o faturamento foram totalmente validados. O projeto está atualmente na **fase de treinamento de operador**.
              </p>
            </div>
          )}

        </div>

        {projeto?.comiss_status !== "treinamento_operador" && (
          <div className="p-6 border-t border-black/5 bg-white">
            {projeto?.comiss_status === "aguardando_dados" ? (
              <button
                type="button"
                onClick={submeter}
                disabled={!docsReviewed}
                className="w-full apple-btn bg-apple-orange text-white hover:bg-apple-orange/90 flex justify-center gap-2 items-center disabled:opacity-50 disabled:cursor-not-allowed text-[14px]"
              >
                <Send size={16} /> Aprovar Documentação e Iniciar
              </button>
            ) : projeto?.comiss_status === "fat_pendente" ? (
              (user?.perfil === "engenharia" || user?.perfil === "ceo") ? (
                <button
                  type="button"
                  onClick={submeter}
                  disabled={!invoiceApproved}
                  className="w-full apple-btn bg-apple-purple text-white hover:bg-apple-purple/90 flex justify-center gap-2 items-center disabled:opacity-50 disabled:cursor-not-allowed text-[14px]"
                >
                  <Send size={16} /> Aprovar e Liberar Treinamento
                </button>
              ) : null
            ) : (
              <button
                type="button"
                onClick={submeter}
                className="w-full apple-btn apple-btn-primary flex justify-center gap-2 items-center text-[14px]"
              >
                <Send size={16} /> Submeter para Handover
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}