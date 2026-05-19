"""
AltaCLP — RAG técnico: manuais da biblioteca de equipamentos (instalação/calibração).
Sem análise gerencial — foco em documentação e procedimentos.
"""

import os
from sqlalchemy.orm import Session

from database.models import PortfolioEquipamento, EquipamentoPlanta


SYSTEM_PROMPT_TECNICO = """Você é o assistente técnico de campo da AltaCLP.
REGRAS OBRIGATÓRIAS:
- Responda APENAS sobre instalação, montagem, esquemas elétricos, calibração e manutenção.
- NÃO forneça análise financeira, ROI, KPIs gerenciais ou recomendações estratégicas.
- Use o contexto de manuais e datasheets fornecidos.
- Se não houver informação no contexto, indique qual manual consultar e sugira passos genéricos de segurança industrial.
- Responda em português brasileiro, de forma objetiva e passo a passo."""


def _montar_contexto_manuais(db: Session, equipamento_tag: str | None = None) -> str:
    q = db.query(PortfolioEquipamento)
    if equipamento_tag:
        q = q.filter(
            PortfolioEquipamento.nome_equipamento.ilike(f"%{equipamento_tag}%")
            | PortfolioEquipamento.categoria.ilike(f"%{equipamento_tag}%")
        )
    items = q.limit(15).all()
    if not items:
        items = db.query(PortfolioEquipamento).limit(10).all()
    blocos = []
    for i in items:
        blocos.append(
            f"- [{i.categoria}] {i.nome_equipamento} ({i.fabricante}): manual em {i.url_manual}"
        )
    return "MANUAIS E DATASHEETS REGISTRADOS:\n" + "\n".join(blocos)


async def chat_instalacao_tecnico(
    db: Session,
    pergunta: str,
    maquina_id: str | None = None,
    equipamento_tag: str | None = None,
    modo: str = "instalacao",
) -> dict:
    contexto = _montar_contexto_manuais(db, equipamento_tag)

    if maquina_id and equipamento_tag:
        eq = (
            db.query(EquipamentoPlanta)
            .filter(
                EquipamentoPlanta.maquina_id == maquina_id,
                EquipamentoPlanta.tag == equipamento_tag,
            )
            .first()
        )
        if eq:
            contexto += f"\n\nEQUIPAMENTO: {eq.tag} — {eq.nome}. Valores atuais: {eq.valor_atual} {eq.unidade or ''}. Limites: {eq.threshold_min} a {eq.threshold_max}."

    if modo == "calibracao":
        instrucao = "Foque em procedimento de calibração, tolerâncias e verificação pós-ajuste."
    else:
        instrucao = "Foque em instalação, ligação elétrica, montagem mecânica e checklist de comissionamento."

    prompt = f"{contexto}\n\n{instrucao}\n\nPergunta do técnico: {pergunta}"

    try:
        from services.groq_client import get_groq_client, DEFAULT_TEXT_MODEL

        client = get_groq_client()
        if client:
            msg = client.chat.completions.create(
                model=DEFAULT_TEXT_MODEL,
                max_tokens=700,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT_TECNICO},
                    {"role": "user", "content": prompt}
                ],
            )
            return {"resposta": msg.choices[0].message.content, "fonte": "groq", "modo": modo}
    except Exception:
        pass

    return {
        "resposta": (
            f"[Modo documentação técnica]\n\nCom base nos manuais cadastrados, para '{pergunta}':\n"
            f"1. Consulte o manual do fabricante listado acima.\n"
            f"2. Verifique alimentação, aterramento e sinal antes de energizar.\n"
            f"3. Registre parâmetros no log de calibração após ajuste.\n\n"
            f"Contexto: {len(contexto.split(chr(10)))} referências de biblioteca."
        ),
        "fonte": "heuristic",
        "modo": modo,
    }


async def revisar_submissao_ia(db: Session, projeto_id: str, documentos: list) -> str:
    """Scan básico de documentos submetidos pelo técnico."""
    n_docs = len(documentos)
    pendencias = db.query(PortfolioEquipamento).count()
    return (
        f"Revisão automática: {n_docs} arquivo(s) recebido(s). "
        f"Checklist visual sugerido: fotos da instalação, etiquetas de série, testes de I/O. "
        f"Pendente aprovação do engenheiro responsável."
    )
