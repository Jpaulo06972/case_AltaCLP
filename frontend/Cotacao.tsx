// AltaCLP Intelligence — Assistente de Cotação
// Demo of the WhatsApp audio → BOM generation flow

import { useState } from "react";
import { Zap, Mic, CheckCircle, Clock, FileText, ArrowRight } from "lucide-react";

const mockTranscription = `"Oi Cláudia, é o João. Então, o cliente da Anápolis, a Cerâmica Branco, eles querem automatizar a linha de prensagem deles. São três prensas hidráulicas, cada uma com motor de 75kW, precisam de controle de pressão e posição. Temperatura do molde tem que ser monitorada, faixa de 180 a 220 graus. Eles têm um supervisório antigo da Wonderware que querem manter, então precisa de comunicação OPC. Ah, e o cliente é do setor cerâmico, então tem bastante poeira, precisa de IP65 no mínimo nos CLPs. Prazo deles é setembro. Me faz uma cotação?"`;

const mockBOM = [
  { item: "CLP Siemens S7-1500 (CPU 1515-2 PN)", qty: 3, unit: "un", unitPrice: 8200, notes: "IP65 · Módulo de segurança integrado" },
  { item: "Módulo de E/S Analógico (SM 1231)", qty: 6, unit: "un", unitPrice: 1200, notes: "Leitura temperatura + pressão" },
  { item: "Módulo de E/S Digital (SM 1221)", qty: 3, unit: "un", unitPrice: 680, notes: "Sinais de posição e atuadores" },
  { item: "Gateway OPC UA / OPC DA", qty: 1, unit: "un", unitPrice: 4500, notes: "Compatibilidade Wonderware legado" },
  { item: "Sensor de Temperatura PT100 (IP65)", qty: 9, unit: "un", unitPrice: 380, notes: "3 por prensa · faixa 0-300°C" },
  { item: "Transdutor de Pressão (0-400 bar)", qty: 6, unit: "un", unitPrice: 520, notes: "2 por prensa · 4-20mA" },
  { item: "Encoder Linear (posição)", qty: 3, unit: "un", unitPrice: 1800, notes: "Resolução 0.1mm" },
  { item: "Painel Elétrico IP65 (600x800mm)", qty: 3, unit: "un", unitPrice: 3200, notes: "Com climatização" },
  { item: "Engenharia de Aplicação (comissionamento)", qty: 12, unit: "dias", unitPrice: 1800, notes: "3 prensas · 4 dias/prensa" },
  { item: "Treinamento Operadores", qty: 2, unit: "dias", unitPrice: 2500, notes: "In-loco · Anápolis" },
];

export default function Cotacao() {
  const [step, setStep] = useState<"upload" | "transcribing" | "extracting" | "done">("upload");
  const [isProcessing, setIsProcessing] = useState(false);

  const totalBOM = mockBOM.reduce((sum, item) => sum + item.qty * item.unitPrice, 0);

  const handleProcess = () => {
    setIsProcessing(true);
    setStep("transcribing");
    setTimeout(() => setStep("extracting"), 2000);
    setTimeout(() => {
      setStep("done");
      setIsProcessing(false);
    }, 4000);
  };

  return (
    <div className="min-h-screen">
      <header
        className="sticky top-0 z-10 flex items-center justify-between px-6 h-14 border-b"
        style={{ background: "oklch(0.11 0.008 260 / 0.95)", borderColor: "oklch(0.18 0.008 260)", backdropFilter: "blur(8px)" }}
      >
        <div className="flex items-center gap-3">
          <Zap size={16} style={{ color: "#F59E0B" }} />
          <h1 className="text-sm font-semibold" style={{ color: "oklch(0.95 0.003 260)", fontFamily: "'Space Grotesk', sans-serif" }}>
            Assistente de Cotação Técnica
          </h1>
        </div>
        <div className="text-xs px-3 py-1 rounded" style={{ background: "oklch(0.75 0.18 80 / 0.1)", color: "#F59E0B", fontFamily: "'JetBrains Mono', monospace" }}>
          5-7 dias → &lt; 2 horas
        </div>
      </header>

      <div className="p-6 space-y-6">
        {/* Problem context */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {[
            { label: "Tempo atual", value: "5-7 dias", color: "#EF4444", sub: "Mecasul entrega em 24h" },
            { label: "Negócios perdidos/mês", value: "6", color: "#EF4444", sub: "~R$ 80k em ticket médio" },
            { label: "Com assistente IA", value: "< 2h", color: "#10B981", sub: "Vendedor mantém seu jeito" },
          ].map((k) => (
            <div key={k.label} className="p-5 rounded" style={{ background: "oklch(0.13 0.008 260)", border: `1px solid ${k.color}40` }}>
              <div className="text-xs font-semibold uppercase mb-2" style={{ color: "oklch(0.55 0.012 260)", fontFamily: "'Space Grotesk', sans-serif" }}>{k.label}</div>
              <div className="text-3xl font-bold" style={{ color: k.color, fontFamily: "'JetBrains Mono', monospace" }}>{k.value}</div>
              <div className="text-xs mt-1" style={{ color: "oklch(0.45 0.01 260)" }}>{k.sub}</div>
            </div>
          ))}
        </div>

        {/* Demo flow */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Input side */}
          <div className="space-y-4">
            <div className="p-5 rounded" style={{ background: "oklch(0.13 0.008 260)", border: "1px solid oklch(0.22 0.008 260)" }}>
              <h3 className="text-sm font-semibold mb-3" style={{ color: "oklch(0.95 0.003 260)", fontFamily: "'Space Grotesk', sans-serif" }}>
                1. Áudio do Vendedor (WhatsApp)
              </h3>
              <div className="p-4 rounded flex items-center gap-4" style={{ background: "oklch(0.16 0.008 260)", border: "1px dashed oklch(0.3 0.008 260)" }}>
                <div className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0" style={{ background: "oklch(0.75 0.18 80 / 0.15)" }}>
                  <Mic size={18} style={{ color: "#F59E0B" }} />
                </div>
                <div>
                  <div className="text-xs font-semibold mb-0.5" style={{ color: "oklch(0.85 0.005 260)", fontFamily: "'Space Grotesk', sans-serif" }}>
                    cotacao_ceramica_branco.ogg
                  </div>
                  <div className="text-xs" style={{ color: "oklch(0.45 0.01 260)", fontFamily: "'JetBrains Mono', monospace" }}>
                    8:42 min · João Vendedor · 17/05/2026
                  </div>
                </div>
              </div>
              {step === "upload" && (
                <button
                  onClick={handleProcess}
                  className="mt-3 w-full py-2.5 rounded text-sm font-semibold flex items-center justify-center gap-2 transition-opacity hover:opacity-90"
                  style={{ background: "#F59E0B", color: "oklch(0.1 0.008 260)", fontFamily: "'Space Grotesk', sans-serif" }}
                >
                  <Zap size={14} />
                  Processar com IA
                </button>
              )}
              {step !== "upload" && (
                <div className="mt-3 space-y-2">
                  {[
                    { label: "Transcrição (Whisper)", done: step !== "transcribing" },
                    { label: "Extração de parâmetros (GPT-4o)", done: step === "done" },
                    { label: "Geração da BOM", done: step === "done" },
                  ].map((s) => (
                    <div key={s.label} className="flex items-center gap-2 text-xs">
                      {s.done ? (
                        <CheckCircle size={12} style={{ color: "#10B981" }} />
                      ) : (
                        <div className="w-3 h-3 rounded-full border-2 border-amber-500 border-t-transparent animate-spin" />
                      )}
                      <span style={{ color: s.done ? "#10B981" : "#F59E0B", fontFamily: "'Space Grotesk', sans-serif" }}>
                        {s.label}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {(step === "extracting" || step === "done") && (
              <div className="p-5 rounded" style={{ background: "oklch(0.13 0.008 260)", border: "1px solid oklch(0.22 0.008 260)" }}>
                <h3 className="text-sm font-semibold mb-3" style={{ color: "oklch(0.95 0.003 260)", fontFamily: "'Space Grotesk', sans-serif" }}>
                  2. Transcrição Automática
                </h3>
                <p className="text-xs leading-relaxed p-3 rounded italic" style={{ color: "oklch(0.65 0.008 260)", background: "oklch(0.16 0.008 260)", fontFamily: "'Space Grotesk', sans-serif" }}>
                  {mockTranscription}
                </p>
              </div>
            )}
          </div>

          {/* Output side */}
          <div>
            {step === "done" && (
              <div className="rounded overflow-hidden" style={{ background: "oklch(0.13 0.008 260)", border: "1px solid oklch(0.65 0.17 160 / 0.4)" }}>
                <div className="px-5 py-3 border-b flex items-center gap-2" style={{ borderColor: "oklch(0.18 0.008 260)" }}>
                  <CheckCircle size={14} style={{ color: "#10B981" }} />
                  <h3 className="text-sm font-semibold" style={{ color: "#10B981", fontFamily: "'Space Grotesk', sans-serif" }}>
                    3. BOM Gerada Automaticamente
                  </h3>
                  <span className="ml-auto text-xs px-2 py-0.5 rounded" style={{ background: "oklch(0.65 0.17 160 / 0.15)", color: "#10B981", fontFamily: "'JetBrains Mono', monospace" }}>
                    &lt; 2 minutos
                  </span>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-xs">
                    <thead>
                      <tr style={{ borderBottom: "1px solid oklch(0.18 0.008 260)" }}>
                        {["Item", "Qtd", "Un.", "Unit.", "Total"].map((h) => (
                          <th key={h} className="px-3 py-2 text-left font-semibold uppercase tracking-wider"
                            style={{ color: "oklch(0.4 0.01 260)", fontFamily: "'Space Grotesk', sans-serif", fontSize: "10px" }}>
                            {h}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {mockBOM.map((item, i) => (
                        <tr key={i} className="hover:bg-[oklch(0.16_0.008_260)] transition-colors"
                          style={{ borderBottom: i < mockBOM.length - 1 ? "1px solid oklch(0.16 0.008 260)" : "none" }}>
                          <td className="px-3 py-2" style={{ color: "oklch(0.75 0.008 260)", fontFamily: "'Space Grotesk', sans-serif" }}>
                            <div>{item.item}</div>
                            <div className="text-xs mt-0.5" style={{ color: "oklch(0.45 0.01 260)" }}>{item.notes}</div>
                          </td>
                          <td className="px-3 py-2 font-bold" style={{ color: "#F59E0B", fontFamily: "'JetBrains Mono', monospace" }}>{item.qty}</td>
                          <td className="px-3 py-2" style={{ color: "oklch(0.55 0.012 260)", fontFamily: "'JetBrains Mono', monospace" }}>{item.unit}</td>
                          <td className="px-3 py-2" style={{ color: "oklch(0.65 0.008 260)", fontFamily: "'JetBrains Mono', monospace" }}>
                            R$ {item.unitPrice.toLocaleString("pt-BR")}
                          </td>
                          <td className="px-3 py-2 font-semibold" style={{ color: "#10B981", fontFamily: "'JetBrains Mono', monospace" }}>
                            R$ {(item.qty * item.unitPrice).toLocaleString("pt-BR")}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                    <tfoot>
                      <tr style={{ borderTop: "1px solid oklch(0.22 0.008 260)" }}>
                        <td colSpan={4} className="px-3 py-3 text-right font-semibold text-xs" style={{ color: "oklch(0.55 0.012 260)", fontFamily: "'Space Grotesk', sans-serif" }}>
                          Total da BOM:
                        </td>
                        <td className="px-3 py-3 font-bold" style={{ color: "#10B981", fontFamily: "'JetBrains Mono', monospace" }}>
                          R$ {totalBOM.toLocaleString("pt-BR")}
                        </td>
                      </tr>
                    </tfoot>
                  </table>
                </div>
                <div className="px-5 py-3 flex items-center justify-between" style={{ borderTop: "1px solid oklch(0.18 0.008 260)" }}>
                  <div className="text-xs" style={{ color: "oklch(0.45 0.01 260)", fontFamily: "'Space Grotesk', sans-serif" }}>
                    Revisão da Engenharia estimada: 30 minutos
                  </div>
                  <button className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded font-semibold"
                    style={{ background: "#10B981", color: "white", fontFamily: "'Space Grotesk', sans-serif" }}>
                    Enviar para Aprovação <ArrowRight size={12} />
                  </button>
                </div>
              </div>
            )}

            {step !== "done" && (
              <div className="h-full flex items-center justify-center p-10 rounded" style={{ background: "oklch(0.13 0.008 260)", border: "1px dashed oklch(0.22 0.008 260)" }}>
                <div className="text-center">
                  <FileText size={32} className="mx-auto mb-3" style={{ color: "oklch(0.3 0.008 260)" }} />
                  <p className="text-xs" style={{ color: "oklch(0.4 0.01 260)", fontFamily: "'Space Grotesk', sans-serif" }}>
                    A BOM gerada aparecerá aqui após o processamento
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
