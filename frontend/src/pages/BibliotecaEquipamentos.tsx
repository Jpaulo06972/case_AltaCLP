/**
 * Screen 6 — Biblioteca de Equipamentos (URLs externas de manuais).
 */

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { equipmentLibraryApi } from "@/services/api";
import { Search, ExternalLink, Loader2, BookOpen } from "lucide-react";

export default function BibliotecaEquipamentos() {
  const [busca, setBusca] = useState("");
  const [categoria, setCategoria] = useState("");
  const [page, setPage] = useState(1);
  const limit = 20;

  const { data, isLoading } = useQuery({
    queryKey: ["equipment-library", busca, categoria, page],
    queryFn: () =>
      equipmentLibraryApi
        .list({ busca: busca || undefined, categoria: categoria || undefined, page, limit } as any)
        .then((r) => r.data),
  });

  const items = data?.dados || [];
  const categorias = data?.categorias || ["PLC", "Sensor", "Inverter", "Motor"];
  const totalPages = data?.paginas || 1;

  return (
    <div className="space-y-6 max-w-[1400px]">
      <div className="apple-card p-4 flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-apple-tertiary" />
          <input
            value={busca}
            onChange={(e) => { setBusca(e.target.value); setPage(1); }}
            placeholder="Buscar equipamento ou fabricante..."
            className="w-full pl-9 pr-3 py-2.5 rounded-lg bg-apple-surface-1 text-[13px] outline-none focus:ring-2 focus:ring-apple-blue/30"
          />
        </div>
        <select
          value={categoria}
          onChange={(e) => { setCategoria(e.target.value); setPage(1); }}
          className="px-3 py-2.5 rounded-lg bg-apple-surface-1 text-[13px] min-w-[160px]"
        >
          <option value="">Todas categorias</option>
          {categorias.map((c: string) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
      </div>
      {isLoading ? (
        <div className="flex justify-center py-20">
          <Loader2 className="animate-spin text-apple-blue" size={32} />
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {items.map((item: { id_equipamento: string; categoria: string; nome_equipamento: string; fabricante: string; url_manual: string }) => (
              <div key={item.id_equipamento} className="apple-card p-5 flex flex-col">
                <span className="text-[10px] font-bold uppercase tracking-wider text-apple-blue mb-2">{item.categoria}</span>
                <h3 className="text-[14px] font-semibold text-apple-label leading-snug flex-1">{item.nome_equipamento}</h3>
                <p className="text-[12px] text-apple-tertiary mt-1">{item.fabricante}</p>
                <a
                  href={item.url_manual}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-4 apple-btn apple-btn-secondary text-[12px] py-2 flex items-center justify-center gap-2"
                >
                  <BookOpen size={14} />
                  Acessar Manual
                  <ExternalLink size={12} />
                </a>
              </div>
            ))}
          </div>
          
          {totalPages > 1 && (
            <div className="flex justify-center items-center gap-4 mt-8">
              <button 
                disabled={page <= 1} 
                onClick={() => setPage(p => Math.max(1, p - 1))}
                className="apple-btn apple-btn-secondary px-4 py-1.5 text-[12px] disabled:opacity-50"
              >
                Anterior
              </button>
              <span className="text-[12px] font-medium text-apple-secondary">Página {page} de {totalPages}</span>
              <button 
                disabled={page >= totalPages} 
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                className="apple-btn apple-btn-secondary px-4 py-1.5 text-[12px] disabled:opacity-50"
              >
                Próxima
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}