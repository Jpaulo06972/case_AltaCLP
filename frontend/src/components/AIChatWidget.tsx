/**
 * Widget de chat IA reutilizável (resumo mensal, RAG por equipamento/projeto).
 */

import { useState } from "react";
import { Sparkles, Send, Loader2 } from "lucide-react";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

interface AIChatWidgetProps {
  title?: string;
  initialSummary?: string;
  onSend: (message: string, history: ChatMessage[]) => Promise<string>;
  placeholder?: string;
  className?: string;
  suggestions?: string[];
}

export default function AIChatWidget({
  title = "Assistente IA",
  initialSummary,
  onSend,
  placeholder = "Pergunte sobre custos, manutenção ou operação...",
  className = "",
  suggestions = [],
}: AIChatWidgetProps) {
  const [messages, setMessages] = useState<ChatMessage[]>(
    initialSummary ? [{ role: "assistant", content: initialSummary }] : []
  );
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const userMsg = input.trim();
    setInput("");
    const nextHistory: ChatMessage[] = [...messages, { role: "user", content: userMsg }];
    setMessages(nextHistory);
    setLoading(true);
    try {
      const reply = await onSend(userMsg, messages);
      setMessages([...nextHistory, { role: "assistant", content: reply }]);
    } catch {
      setMessages([
        ...nextHistory,
        { role: "assistant", content: "Não foi possível processar a consulta. Tente novamente." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`apple-card flex flex-col overflow-hidden ${className}`}>
      <div className="px-5 py-3 border-b border-apple-separator/40 flex items-center gap-2">
        <Sparkles size={16} className="text-apple-purple" />
        <h3 className="text-[14px] font-semibold text-apple-label">{title}</h3>
      </div>
      <div className="flex-1 min-h-[180px] max-h-[280px] overflow-y-auto px-5 py-3 space-y-3">
        {messages.length === 0 && (
          <p className="text-[12px] text-apple-tertiary">Carregando contexto operacional...</p>
        )}
        {messages.map((m, i) => (
          <div
            key={i}
            className={`text-[13px] leading-relaxed rounded-xl px-3 py-2 ${
              m.role === "user"
                ? "bg-apple-blue/10 text-apple-label ml-8"
                : "bg-apple-surface-1 text-apple-secondary mr-4"
            }`}
          >
            {m.content}
          </div>
        ))}
        {loading && (
          <div className="flex items-center gap-2 text-apple-tertiary text-[12px]">
            <Loader2 size={14} className="animate-spin" />
            Analisando dados...
          </div>
        )}
      </div>
      
      {suggestions.length > 0 && messages.length <= (initialSummary ? 1 : 0) && (
        <div className="px-4 py-3 border-t border-apple-separator/20 bg-apple-surface-0 flex flex-wrap gap-2">
          {suggestions.map((s, i) => (
            <button
              key={i}
              onClick={() => setInput(s)}
              className="text-[12px] bg-apple-surface-1 hover:bg-apple-blue/10 text-apple-secondary hover:text-apple-blue border border-apple-separator/40 rounded-full px-3 py-1.5 transition-colors text-left"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      <div className="px-4 py-3 border-t border-apple-separator/30 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder={placeholder}
          className="flex-1 text-[13px] px-3 py-2 rounded-lg bg-apple-surface-1 border-0 outline-none focus:ring-2 focus:ring-apple-blue/30"
        />
        <button
          type="button"
          onClick={handleSend}
          disabled={loading || !input.trim()}
          className="apple-btn apple-btn-primary p-2 disabled:opacity-40"
        >
          <Send size={16} />
        </button>
      </div>
    </div>
  );
}