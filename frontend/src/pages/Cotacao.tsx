/**
 * AltaCLP Intelligence — Cotação Inteligente & Comissionamento
 * WhatsApp audio → AI-powered BOM & Checklist generation
 */

import { useState, useCallback } from "react";
import { cotacaoApi } from "@/services/api";
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
  const [step, setStep] = useState<"upload" | "processing" | "done">("upload");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);

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

    try {
      // Simulate API call using our mock transcription
      const res = await cotacaoApi.processar({
        transcricao_audio: mockTranscription,
        vendedor: "João Vendedor",
        cliente_nome: "Cerâmica Branco",
      });
      setResult(res.data);
    } catch (err) {
      console.error(err);
      // Fallback BOM for demo
      setResult({
        bom: [
          { codigo: "CLP-S71500", descricao: "CLP Siemens S7-1500 (CPU 1515-2 PN) IP65", quantidade: 3, unidade: "un", valor_unit: 9200 },
          { codigo: "SM-1231-AI", descricao: "Módulo E/S Analógico SM 1231", quantidade: 6, unidade: "un", valor_unit: 1200 },
          { codigo: "GW-OPCUA", descricao: "Gateway OPC UA / OPC DA", quantidade: 1, unidade: "un", valor_unit: 4500 },
          { codigo: "SNS-PT100", descricao: "Sensor Temperatura PT100", quantidade: 9, unidade: "un", valor_unit: 380 },
          { codigo: "TRS-400B", descricao: "Transdutor de Pressão (0-400 bar)", quantidade: 6, unidade: "un", valor_unit: 520 },
          { codigo: "ENG-COM", descricao: "Engenharia de Aplicação & Comissionamento", quantidade: 12, unidade: "dias", valor_unit: 1800 },
        ],
        tempo_processamento_segundos: 4.8,
      });
    } finally {
      setStep("done");
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
                    
                    <label className="apple-btn apple-btn-secondary cursor-pointer">
                      <Mic size={16} />
                      Selecionar Arquivo
                      <input type="file" accept="audio/*" className="hidden" onChange={handleFileSelect} />
                    </label>
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
                    {mockTranscription}
                  </p>
                </div>
                
                <button 
                  onClick={() => { setStep("upload"); setFile(null); setResult(null); }}
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
              {/* Bloco 1: BOM */}
              <div className="apple-card overflow-hidden animate-scale-in" style={{ animationDelay: "0.1s" }}>
                <div className="px-6 py-4 border-b border-apple-separator/50 flex items-center gap-2 bg-apple-surface-0">
                  <FileText size={18} className="text-apple-blue" />
                  <h3 className="text-[15px] font-semibold text-apple-label">
                    Bill of Materials (BOM)
                  </h3>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-[13px]">
                    <thead>
                      <tr className="border-b border-apple-separator/30 bg-apple-surface-1/30">
                        {["Item", "Qtd", "Un.", "Total"].map((h) => (
                          <th key={h} className="px-4 py-2 text-left text-[11px] font-semibold text-apple-tertiary uppercase">
                            {h}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {bom.map((item: any, i: number) => (
                        <tr key={i} className="border-b border-apple-separator/20 hover:bg-apple-surface-1/50 transition-colors">
                          <td className="px-4 py-3">
                            <p className="font-medium text-apple-label line-clamp-1">{item.descricao}</p>
                            <p className="text-[11px] text-apple-tertiary font-mono">{item.codigo}</p>
                          </td>
                          <td className="px-4 py-3 font-semibold text-apple-blue">{item.quantidade}</td>
                          <td className="px-4 py-3 text-apple-tertiary">{item.unidade}</td>
                          <td className="px-4 py-3 font-medium text-apple-label">
                            R$ {((item.quantidade || 0) * (item.valor_unit || 0)).toLocaleString("pt-BR")}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                    <tfoot>
                      <tr className="border-t border-apple-separator/50 bg-apple-surface-0">
                        <td colSpan={3} className="px-4 py-3 text-right text-[12px] font-semibold text-apple-tertiary">
                          Total Estimado:
                        </td>
                        <td className="px-4 py-3 text-[14px] font-bold text-apple-green">
                          R$ {totalBOM.toLocaleString("pt-BR")}
                        </td>
                      </tr>
                    </tfoot>
                  </table>
                </div>
              </div>

              {/* Bloco 2: Template de Comissionamento */}
              <div className="apple-card overflow-hidden animate-scale-in" style={{ animationDelay: "0.2s" }}>
                <div className="px-6 py-4 border-b border-apple-separator/50 flex items-center gap-2 bg-apple-surface-0">
                  <ClipboardList size={18} className="text-apple-purple" />
                  <h3 className="text-[15px] font-semibold text-apple-label">
                    Template de Comissionamento (Gerado via IA)
                  </h3>
                </div>
                <div className="p-4 bg-apple-surface-1/20">
                  <div className="space-y-2">
                    {mockChecklist.map((task) => (
                      <div key={task.id} className="flex items-start gap-3 p-3 bg-apple-surface-0 rounded-lg border border-apple-separator/30">
                        <div className="w-5 h-5 rounded-full border-2 border-apple-separator flex items-center justify-center flex-shrink-0 mt-0.5"></div>
                        <p className="text-[13px] font-medium text-apple-secondary leading-snug">{task.text}</p>
                      </div>
                    ))}
                  </div>
                  
                  <div className="mt-5 flex justify-end">
                    <button className="apple-btn apple-btn-primary text-[13px] py-2">
                      Salvar Projeto e Aprovar
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
