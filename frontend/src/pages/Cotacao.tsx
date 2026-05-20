/**
 * AltaCLP Intelligence — Cotação Inteligente & Comissionamento
 * WhatsApp audio → AI-powered BOM & Checklist generation
 */

import { useState, useCallback } from "react";
import { cotacaoApi, quotationsApi } from "@/services/api";
import { useQueryClient } from "@tanstack/react-query";
import { useToast } from "@/components/Toast";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { useAppData } from "@/contexts/AppDataContext";
import {
  Zap,
  Mic,
  CheckCircle,
  FileText,
  ArrowRight,
  Loader2,
  Sparkles,
  UploadCloud,
  ClipboardList,
} from "lucide-react";

const mockTranscription = `"Oi Cláudia, é o João. Então, o cliente da Anápolis, a Cerâmica Branco, eles querem automatizar a linha de prensagem deles. São três prensas hidráulicas, cada uma com motor de 75kW, precisam de controle de pressão e posição. Temperatura do molde tem que ser monitorada, faixa de 180 a 220 graus. Eles têm um supervisório antigo da Wonderware que querem manter, então precisa de comunicação OPC. Ah, e o cliente é do setor cerâmico, então tem bastante poeira, precisa de IP65 no mínimo nos CLPs. Prazo deles é setembro. Me faz uma cotação?"`;

const mockChecklist = [
  { id: 1, text: "Verificar fixação física do CLP IP65 no painel da prensa" },
  { id: 2, text: "Garantir aterramento dos 3 motores de 75kW" },
  { id: 3, text: "Calibrar transdutores de pressão (faixa 0-400 bar)" },
  { id: 4, text: "Configurar sensores PT100 para alerta em > 220°C" },
  { id: 5, text: "Testar comunicação OPC UA com o supervisório Wonderware" },
  { id: 6, text: "Validar intertravamento de segurança das prensas" },
];

export default function Cotacao() {
  const qc = useQueryClient();
  const { addToast } = useToast();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { refresh: refreshAppData } = useAppData();

  const [step, setStep] = useState<"upload" | "processing" | "done">("upload");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [manualText, setManualText] = useState("");
  const [proposalText, setProposalText] = useState("");

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleProcess = async () => {
    setLoading(true);
    setStep("processing");
    const vendedorNome = user?.nome || "Vendedor";
    const transcricao = manualText.trim() || mockTranscription;

    // Dynamically extract client name from the transcription text
    let clienteNome = "";
    const textoParaAnalise = transcricao.toLowerCase();
    if (textoParaAnalise.includes("nutrisoja")) {
      clienteNome = "NutriSoja";
    } else if (textoParaAnalise.includes("nestle") || textoParaAnalise.includes("nestlé")) {
      clienteNome = "Nestlé";
    } else if (textoParaAnalise.includes("cerâmica branco") || textoParaAnalise.includes("ceramica branco")) {
      clienteNome = "Cerâmica Branco";
    } else if (textoParaAnalise.includes("anaclara") || textoParaAnalise.includes("ana clara")) {
      clienteNome = "AnaClara";
    } else {
      const match = transcricao.match(/(?:cliente|planta)\s+(?:de|da|do)?\s*([A-Z][a-zA-Z0-9_]+(?:\s+[A-Z][a-zA-Z0-9_]+)*)/);
      if (match && match[1]) {
        clienteNome = match[1];
      }
    }
    if (!clienteNome) {
      clienteNome = "Cliente Geral";
    }

    try {
      let res;
      if (file) {
        const formData = new FormData();
        formData.append("audio", file);
        formData.append("vendedor", vendedorNome);
        formData.append("cliente_nome", clienteNome);
        console.log("[1] FRONTEND: processar áudio — POST /api/cotacao/processar-audio");
        res = await cotacaoApi.processarAudio(formData);
      } else {
        console.log("[2] FRONTEND: POST /api/cotacao/processar", { transcricao_audio: transcricao.slice(0, 80) });
        res = await cotacaoApi.processar({
          transcricao_audio: transcricao,
          vendedor: vendedorNome,
          cliente_nome: clienteNome,
        });
      }

      const data = res.data;
      setResult(data);

      const valorTotal = (data.bom || []).reduce(
        (sum: number, item: any) => sum + (item.quantidade || 0) * (item.valor_unit || 0),
        0
      );

      const finalClienteNome = data.cliente_nome || clienteNome;

      console.log("[2b] FRONTEND: POST /api/quotations/draft");
      const draftRes = await quotationsApi.saveDraft({
        texto_transcrito: data.transcricao_gerada || transcricao,
        json_proposta_ia: {
          cliente_nome: finalClienteNome,
          valor_estimado: valorTotal,
          bom: data.bom,
          parametros: data.parametros_extraidos,
          template_comissionamento: data.template_comissionamento,
        },
        cliente_nome: finalClienteNome,
        valor_estimado: valorTotal,
      });
      const draftId = draftRes.data.id_cotacao;
      setResult((prev: any) => ({ ...prev, cotacao_id: data.cotacao_id, draft_id: draftId }));
      console.log("[5] FRONTEND: Draft saved, id_cotacao:", draftId);

      if (data.template_comissionamento || data.bom) {
        setProposalText(
          `[Escopo Técnico — ${finalClienteNome}]\n\n` +
            (data.bom || [])
              .map((i: any) => `- ${i.quantidade}x ${i.descricao}`)
              .join("\n")
        );
      }
      setStep("done");
    } catch (err: any) {
      console.error("[FRONTEND ERROR] processar cotação:", err);
      addToast(err?.response?.data?.detail || err?.response?.data?.error || "Falha ao processar cotação.", "error");
      setStep("upload");
    } finally {
      setLoading(false);
    }
  };

  const handleAprovar = async () => {
    const approveId = result?.draft_id || result?.cotacao_id;
    if (!approveId) {
      addToast("Cotação inválida ou não possui ID.", "error");
      return;
    }
    try {
      setLoading(true);
      console.log('[1] FRONTEND: "Aprovar e Enviar" button clicked');
      console.log("[6] FRONTEND: POST /api/quotations/" + approveId + "/approve");

      let projetoId: string;
      if (result?.draft_id) {
        const res = await quotationsApi.approve(approveId);
        projetoId = res.data.id || res.data.id_projeto;
      } else {
        const res = await cotacaoApi.aprovar(approveId);
        projetoId = res.data.projeto_id;
      }

      console.log("[8] FRONTEND: projeto criado:", projetoId);
      await refreshAppData();
      qc.invalidateQueries({ queryKey: ["comissionamento-kanban"] });
      qc.invalidateQueries({ queryKey: ["app-state"] });
      addToast("Cotação aprovada! Projeto criado.", "success");
      navigate(`/comissionamento?projeto=${projetoId}&open=true`);
    } catch (err: any) {
      console.error("[FRONTEND ERROR] aprovar:", err);
      addToast(err?.response?.data?.detail || err?.response?.data?.error || "Erro ao aprovar cotação.", "error");
    } finally {
      setLoading(false);
    }
  };

  const bom = result?.bom || [];
  const totalBOM = bom.reduce(
    (sum: number, item: any) => sum + (item.quantidade || 0) * (item.valor_unit || 0),
    0
  );

  return (
    <div className="space-y-6 max-w-[1200px] animate-fade-in">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Lado Esquerdo: Upload e Processamento */}
        <div className="space-y-4 flex flex-col">
          <div className="apple-card p-6 flex-1 flex flex-col">
            <h3 className="text-[15px] font-semibold text-apple-label mb-4">
              1. Assistente de Cotação (Áudio/Voz)
            </h3>

            {step === "upload" && (
              <div 
                className={`flex-1 border-2 border-dashed rounded-2xl flex flex-col items-center justify-center p-8 transition-colors ${
                  isDragging ? "border-apple-blue bg-apple-blue/5" : "border-apple-separator/40 hover:border-apple-separator"
                }`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
              >
                {!file ? (
                  <>
                    <div className="w-16 h-16 rounded-full bg-apple-surface-1 flex items-center justify-center mb-4">
                      <UploadCloud size={28} className="text-apple-blue" />
                    </div>
                    <p className="text-[14px] font-semibold text-apple-label mb-1">Arraste um áudio do WhatsApp</p>
                    <p className="text-[12px] text-apple-tertiary mb-6">ou clique para selecionar (MP3, OGG, WAV)</p>
                    
                    <label className="apple-btn apple-btn-secondary cursor-pointer w-full justify-center">
                      <Mic size={16} />
                      Selecionar Arquivo de Áudio
                      <input type="file" accept="audio/*" className="hidden" onChange={handleFileSelect} />
                    </label>

                    <div className="flex items-center w-full my-6">
                      <div className="flex-1 h-px bg-apple-separator/30"></div>
                      <span className="px-4 text-[12px] text-apple-tertiary uppercase font-semibold">ou digite</span>
                      <div className="flex-1 h-px bg-apple-separator/30"></div>
                    </div>

                    <textarea
                      className="w-full bg-apple-surface-0 border border-apple-separator/50 rounded-xl p-4 text-[13px] text-apple-label placeholder:text-apple-tertiary focus:outline-none focus:ring-2 focus:ring-apple-blue resize-none"
                      rows={4}
                      placeholder="Descreva a visita e as necessidades do cliente..."
                      value={manualText}
                      onChange={(e) => setManualText(e.target.value)}
                    ></textarea>

                    <button
                      onClick={handleProcess}
                      disabled={!manualText.trim()}
                      className="apple-btn apple-btn-primary w-full mt-4 py-3 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <Sparkles size={16} />
                      Gerar Proposta com IA
                    </button>
                  </>
                ) : (
                  <div className="w-full">
                    <div className="flex items-center gap-4 p-4 bg-apple-surface-1 rounded-xl">
                      <div className="w-11 h-11 rounded-xl bg-apple-orange/10 flex items-center justify-center flex-shrink-0">
                        <Mic size={20} className="text-apple-orange" />
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="text-[13px] font-semibold text-apple-label truncate">
                          {file.name}
                        </p>
                        <p className="text-[11px] text-apple-tertiary">
                          {(file.size / 1024 / 1024).toFixed(2)} MB · Áudio Recebido
                        </p>
                      </div>
                      <button onClick={() => setFile(null)} className="text-[12px] text-apple-red hover:underline p-2">
                        Remover
                      </button>
                    </div>
                    
                    <button
                      onClick={handleProcess}
                      className="apple-btn apple-btn-primary w-full mt-6 py-3"
                    >
                      <Sparkles size={16} />
                      Processar com Whisper & GPT-4o
                    </button>
                  </div>
                )}
              </div>
            )}

            {step === "processing" && (
              <div className="flex-1 flex flex-col items-center justify-center py-12">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-apple-blue to-apple-purple flex items-center justify-center mb-6 shadow-xl shadow-apple-blue/20 animate-pulse">
                  <Sparkles size={28} className="text-white" />
                </div>
                <div className="space-y-4 w-full max-w-[240px]">
                  {[
                    { label: "Transcrevendo áudio (Whisper)..." },
                    { label: "Extraindo parâmetros de engenharia..." },
                    { label: "Gerando BOM e Checklist..." },
                  ].map((s, i) => (
                    <div key={i} className="flex items-center gap-3 text-[13px] bg-apple-surface-1 p-3 rounded-xl animate-fade-in" style={{ animationDelay: `${i * 1.5}s` }}>
                      <Loader2 size={16} className="text-apple-blue animate-spin" />
                      <span className="text-apple-secondary font-medium">{s.label}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {step === "done" && (
              <div className="flex-1 flex flex-col">
                <div className="flex items-center gap-4 p-4 bg-apple-surface-1 rounded-xl mb-4">
                  <div className="w-11 h-11 rounded-xl bg-apple-green/10 flex items-center justify-center flex-shrink-0">
                    <CheckCircle size={20} className="text-apple-green" />
                  </div>
                  <div className="min-w-0">
                    <p className="text-[13px] font-semibold text-apple-label">
                      Processamento Concluído
                    </p>
                    <p className="text-[11px] text-apple-tertiary">
                      Tempo total: {result?.tempo_processamento_segundos || 4.8}s
                    </p>
                  </div>
                </div>

                <div className="apple-card bg-apple-surface-1 p-4 flex-1">
                  <h4 className="text-[12px] font-semibold text-apple-secondary mb-2 uppercase tracking-wider">
                    Transcrição Automática
                  </h4>
                  <p className="text-[13px] text-apple-secondary leading-relaxed italic">
                    {result?.transcricao_gerada || mockTranscription}
                  </p>
                </div>
                
                <button 
                  onClick={() => { setStep("upload"); setFile(null); setResult(null); setProposalText(""); }}
                  className="mt-4 apple-btn apple-btn-secondary text-[12px] w-full"
                >
                  Processar Novo Áudio
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Lado Direito: Resultados (BOM e Checklist) */}
        <div className="space-y-4">
          {step === "done" ? (
            <>
              <div className="apple-card overflow-hidden animate-scale-in" style={{ animationDelay: "0.1s" }}>
                <div className="px-6 py-4 border-b border-apple-separator/50 flex items-center gap-2 bg-apple-surface-0">
                  <FileText size={18} className="text-apple-blue" />
                  <h3 className="text-[15px] font-semibold text-apple-label">
                    Escopo Técnico (Revisão)
                  </h3>
                </div>
                <div className="p-4 bg-apple-surface-1/20">
                  <textarea
                    className="w-full bg-apple-surface-0 border border-apple-separator/50 rounded-xl p-4 text-[13px] text-apple-label placeholder:text-apple-tertiary focus:outline-none focus:ring-2 focus:ring-apple-blue font-mono"
                    rows={12}
                    value={proposalText}
                    onChange={(e) => setProposalText(e.target.value)}
                  ></textarea>
                  
                  <div className="mt-5 flex justify-end gap-3">
                    <button className="apple-btn apple-btn-secondary text-[13px] py-2">
                      Refazer / Ajustar
                    </button>
                    <button 
                      className="apple-btn apple-btn-primary text-[13px] py-2 disabled:opacity-50"
                      onClick={handleAprovar}
                      disabled={loading}
                    >
                      {loading ? <Loader2 size={14} className="animate-spin" /> : null}
                      Aprovar e Enviar para Engenharia
                      <ArrowRight size={14} />
                    </button>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="apple-card h-full min-h-[400px] flex items-center justify-center p-12 border border-dashed border-apple-separator/50 bg-transparent">
              <div className="text-center opacity-50">
                <FileText size={48} strokeWidth={1} className="mx-auto mb-4 text-apple-tertiary" />
                <p className="text-[14px] font-medium text-apple-secondary">
                  Aguardando Processamento
                </p>
                <p className="text-[12px] text-apple-tertiary mt-1 max-w-[250px] mx-auto">
                  Faça o upload do áudio para gerar a lista de materiais (BOM) e o checklist.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
