/**
 * Cards informativos persistentes (status planta, gargalos).
 */

interface InfoCard {
  id: string;
  titulo: string;
  valor: string;
  severidade: "ok" | "aviso" | "critico";
  detalhe?: string;
}

const severityStyles = {
  ok: "border-apple-green/30 bg-apple-green/5",
  aviso: "border-apple-orange/30 bg-apple-orange/5",
  critico: "border-apple-red/30 bg-apple-red/5",
};

const dotStyles = {
  ok: "bg-apple-green",
  aviso: "bg-apple-orange",
  critico: "bg-apple-red",
};

export default function InfoCards({ cards }: { cards: InfoCard[] }) {
  if (!cards?.length) return null;
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
      {cards.map((card) => (
        <div
          key={card.id}
          className={`apple-card p-4 border ${severityStyles[card.severidade] || severityStyles.ok}`}
        >
          <div className="flex items-center gap-2 mb-2">
            <span className={`w-2 h-2 rounded-full ${dotStyles[card.severidade]}`} />
            <p className="text-[11px] font-semibold text-apple-tertiary uppercase tracking-wide">
              {card.titulo}
            </p>
          </div>
          <p className="text-[16px] font-bold text-apple-label">{card.valor}</p>
          {card.detalhe && (
            <p className="text-[12px] text-apple-secondary mt-1">{card.detalhe}</p>
          )}
        </div>
      ))}
    </div>
  );
}
