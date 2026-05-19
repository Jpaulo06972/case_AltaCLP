"""
AltaCLP — RAG e resumos mensais para camada de Engenharia.
"""

import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from database.models import (
    Alerta, VisitaTecnica, CustoOperacional, Maquina, Cliente,
    Comissionamento, LeituraSensor, EquipamentoPlanta, StatusAlerta,
)
from services.ai_analyst import AIAnalyst


async def compilar_resumo_mensal(db: Session) -> dict:
    """Compila contexto mensal de custos de visita e manutenção."""
    inicio = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    custo_visitas = (
        db.query(func.coalesce(func.sum(VisitaTecnica.custo), 0))
        .filter(VisitaTecnica.data_visita >= inicio)
        .scalar()
    )
    visitas_total = db.query(VisitaTecnica).filter(VisitaTecnica.data_visita >= inicio).count()
    visitas_falsas = (
        db.query(VisitaTecnica)
        .filter(VisitaTecnica.data_visita >= inicio, VisitaTecnica.foi_falso_alerta == True)
        .count()
    )

    custos_ops = (
        db.query(func.coalesce(func.sum(CustoOperacional.valor), 0))
        .filter(CustoOperacional.data_referencia >= inicio)
        .scalar()
    )

    alertas_abertos = db.query(Alerta).filter(Alerta.status == StatusAlerta.aberto).count()
    maquinas_criticas = db.query(Maquina).filter(Maquina.status.in_(["crítico", "critico"])).count()

    contexto = f"""RESUMO OPERACIONAL — {inicio.strftime('%B/%Y')}
- Custos de visitas técnicas no mês: R$ {float(custo_visitas or 0):,.2f} ({visitas_total} visitas, {visitas_falsas} falsos alertas)
- Custos operacionais diversos: R$ {float(custos_ops or 0):,.2f}
- Alertas abertos: {alertas_abertos}
- Máquinas em estado crítico: {maquinas_criticas}
"""

    try:
        from services.groq_client import get_groq_client, DEFAULT_TEXT_MODEL

        client = get_groq_client()
        if client:
            msg = client.chat.completions.create(
                model=DEFAULT_TEXT_MODEL,
                max_tokens=600,
                messages=[
                    {
                        "role": "user",
                        "content": f"Gere um resumo executivo mensal em português (3-4 parágrafos) para engenheiros e CEO:\n\n{contexto}",
                    }
                ],
            )
            resumo = msg.choices[0].message.content
            fonte = "groq"
        else:
            resumo = (
                f"No mês atual, a operação registrou {visitas_total} visitas técnicas totalizando "
                f"R$ {float(custo_visitas or 0):,.2f}, sendo {visitas_falsas} classificadas como falso alerta. "
                f"Custos operacionais adicionais somam R$ {float(custos_ops or 0):,.2f}. "
                f"Há {alertas_abertos} alertas abertos e {maquinas_criticas} máquinas em estado crítico — "
                f"priorize gargalos de comissionamento e ajuste de thresholds nas unidades com maior taxa de falso alerta."
            )
            fonte = "heuristic"
    except Exception:
        resumo = contexto
        fonte = "fallback"

    return {
        "resumo": resumo,
        "contexto_bruto": contexto,
        "metricas": {
            "custo_visitas_mes": float(custo_visitas or 0),
            "visitas_total": visitas_total,
            "visitas_falsas": visitas_falsas,
            "custos_operacionais": float(custos_ops or 0),
            "alertas_abertos": alertas_abertos,
        },
        "fonte": fonte,
        "gerado_em": datetime.utcnow().isoformat(),
    }


async def rag_chat_engenharia(
    db: Session,
    pergunta: str,
    perfil: str = "engenharia",
    equipamento_tag: str | None = None,
    maquina_id: str | None = None,
    projeto_id: str | None = None,
) -> dict:
    """RAG operacional — cruza pergunta com dados do banco."""
    contexto = AIAnalyst.get_contexto_operacional(db)

    if equipamento_tag and maquina_id:
        eq = (
            db.query(EquipamentoPlanta)
            .filter(
                EquipamentoPlanta.maquina_id == maquina_id,
                EquipamentoPlanta.tag == equipamento_tag,
            )
            .first()
        )
        if eq:
            contexto += f"\n\nEQUIPAMENTO SELECIONADO: {eq.tag} ({eq.nome}) — valor atual: {eq.valor_atual} {eq.unidade or ''}, limites: {eq.threshold_min}-{eq.threshold_max}"

    if projeto_id:
        com = db.query(Comissionamento).filter(Comissionamento.id == projeto_id).first()
        if com:
            contexto += f"\n\nPROJETO: fase={com.fase_projeto}, status={com.status}, specs={com.especificacoes_tecnicas}"

    return await AIAnalyst.responder_decisao(pergunta=pergunta, perfil=perfil, db=db)


async def analisar_causa_raiz_alarme(db: Session, alerta_id: str) -> str:
    """Gera análise preliminar de causa raiz para um alarme."""
    from uuid import UUID

    alerta = db.query(Alerta).filter(Alerta.id == UUID(alerta_id)).first()
    if not alerta:
        return "Alarme não encontrado."

    maq = db.query(Maquina).filter(Maquina.id == alerta.maquina_id).first()
    leituras = (
        db.query(LeituraSensor)
        .filter(LeituraSensor.maquina_id == alerta.maquina_id)
        .order_by(LeituraSensor.timestamp.desc())
        .limit(20)
        .all()
    )

    payload = (
        f"Alarme: {alerta.titulo} | Tipo: {alerta.tipo} | Severidade: {alerta.severidade}\n"
        f"Máquina: {maq.codigo if maq else '?'} | Valor sensor: {alerta.valor_sensor} | Threshold: {alerta.threshold_configurado}\n"
        f"Últimas leituras: temp={[l.temperatura for l in leituras[:5]]}, vib={[l.vibracao for l in leituras[:5]]}"
    )

    try:
        from services.groq_client import get_groq_client, DEFAULT_TEXT_MODEL

        client = get_groq_client()
        if client:
            msg = client.chat.completions.create(
                model=DEFAULT_TEXT_MODEL,
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": f"Como engenheiro de automação, faça análise de causa raiz preliminar (RCA) em português:\n{payload}",
                    }
                ],
            )
            return msg.choices[0].message.content
    except Exception:
        pass

    return (
        f"Análise preliminar: o alarme '{alerta.titulo}' indica desvio em {alerta.tipo.value.replace('_', ' ')}. "
        f"Valor medido {alerta.valor_sensor} vs limite {alerta.threshold_configurado}. "
        f"Recomenda-se verificar sensores associados, última manutenção preventiva e histórico de drift de código no CLP."
    )
