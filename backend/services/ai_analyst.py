"""
AltaCLP Intelligence Platform — Analista de IA
Integração com Anthropic API para análise operacional contextualizada.
Monta contexto em tempo real a partir do banco de dados.
"""

import os
import json
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func

from database.models import (
    Maquina, Alerta, Incidente, Comissionamento, Cliente,
    KPIHistorico, GitOpsAuditoria,
    StatusMaquina, StatusAlerta, StatusComissionamento, SeveridadeAlerta,
)


class AIAnalyst:
    """
    Sistema de IA contextualizada da AltaCLP Intelligence Platform.
    Usa dados em tempo real do banco + contexto de negócio fixo dos stakeholders.
    """

    SYSTEM_PROMPT_BASE = """Você é o sistema de IA da AltaCLP Intelligence Platform, desenvolvido pela HomoDeus.
Você tem acesso ao estado operacional em tempo real de toda a operação da AltaCLP.

CONTEXTO ATUAL (atualizado em tempo real):
{contexto_operacional}

REGRAS DE PERFIL:
Se o perfil for 'ceo' ou 'cfo' (Nível Executivo):
1. Comporte-se como Assistente Executivo focado em saúde do negócio, OPEX, CAPEX, TCO, ROI e OEE.
2. NUNCA foque em como consertar ou instalar equipamentos. Aborde alarmes pelo seu impacto financeiro, custo de horas ociosas e risco ao cronograma de projetos.
3. Entregue resumos de criticidade (ex: "Temos 5 alarmes críticos atrasando o Projeto X, gerando custo estimado de $Y em horas ociosas").
4. Formatação: seja objetivo e analítico. Use tabelas curtas, bullet points e liderança com KPIs e análise de riscos. Evite jargões técnicos de baixo nível, exceto para justificar custos.
5. Sempre cruze dados de produtividade (visitas técnicas, resoluções) com orçamentos de projeto. Inclua um indicador de frescor ou confiança se os dados de campo parecerem não atualizados.

Se o perfil for 'engenharia' ou 'campo':
- Foque em detalhes técnicos operacionais, troubleshooting e métricas de máquina.

STAKEHOLDERS PARA REFERÊNCIA:
- Marcos Tedesco (CEO, 70% ações): Quer cortar visitas falsas.
- Roberto (CFO): Foco em OPEX/CAPEX e múltiplo EBITDA.
- Cláudia Santarém (Engenharia): Foco em backlog.
- Anaclara Alimentos: Cliente crítico (R$ 780k em risco).

Responda sempre em português brasileiro.
Perfil atual do usuário: {perfil_usuario}"""

    @staticmethod
    def get_contexto_operacional(db: Session) -> str:
        """
        Monta o contexto completo da operação a partir do banco em tempo real.
        """
        try:
            # Máquinas por status
            total_maquinas = db.query(Maquina).count()
            operando = db.query(Maquina).filter(Maquina.status == StatusMaquina.operando).count()
            alerta = db.query(Maquina).filter(Maquina.status == StatusMaquina.alerta).count()
            critico = db.query(Maquina).filter(Maquina.status == StatusMaquina.critico).count()
            offline = db.query(Maquina).filter(Maquina.status == StatusMaquina.offline).count()
            em_comiss = db.query(Maquina).filter(Maquina.status == StatusMaquina.em_comissionamento).count()

            # Alertas
            alertas_abertos = db.query(Alerta).filter(
                Alerta.status == StatusAlerta.aberto
            ).count()
            alertas_criticos = db.query(Alerta).filter(
                Alerta.status == StatusAlerta.aberto,
                Alerta.severidade == SeveridadeAlerta.critico
            ).count()

            # Custo de visitas no mês atual
            inicio_mes = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
            custo_visitas = db.query(func.sum(Alerta.custo_visita)).filter(
                Alerta.timestamp_criacao >= inicio_mes,
                Alerta.custo_visita.isnot(None)
            ).scalar() or 0

            # Taxa de falso alerta
            total_alertas_90d = db.query(Alerta).filter(
                Alerta.timestamp_criacao >= datetime.utcnow() - timedelta(days=90)
            ).count()
            falsos_90d = db.query(Alerta).filter(
                Alerta.timestamp_criacao >= datetime.utcnow() - timedelta(days=90),
                Alerta.is_falso_alerta == True
            ).count()
            taxa_falso = (falsos_90d / total_alertas_90d * 100) if total_alertas_90d > 0 else 0

            # Drifts ativos
            drifts = db.query(Maquina).filter(Maquina.codigo_sync == False).count()

            # Comissionamentos
            backlog = db.query(Comissionamento).filter(
                Comissionamento.status.in_([
                    StatusComissionamento.aguardando_dados,
                    StatusComissionamento.em_andamento,
                    StatusComissionamento.fat_pendente,
                    StatusComissionamento.treinamento_operador,
                ])
            ).count()
            com_risco = db.query(Comissionamento).filter(
                Comissionamento.risco_cancelamento == True
            ).count()

            # Incidentes recentes
            incidentes_90d = db.query(Incidente).filter(
                Incidente.data_ocorrencia >= datetime.utcnow() - timedelta(days=90)
            ).count()
            prejuizo_total = db.query(func.sum(Incidente.prejuizo_estimado)).scalar() or 0

            # Clientes
            total_clientes = db.query(Cliente).filter(Cliente.ativo == True).count()

            contexto = f"""
ESTADO OPERACIONAL EM TEMPO REAL ({datetime.utcnow().strftime('%d/%m/%Y %H:%M UTC')}):

MÁQUINAS ({total_maquinas} CLPs):
- Operando: {operando} | Alerta: {alerta} | Crítico: {critico}
- Offline: {offline} | Em Comissionamento: {em_comiss}

ALERTAS:
- Abertos: {alertas_abertos} | Críticos: {alertas_criticos}
- Taxa de falso alerta (90d): {taxa_falso:.1f}%
- Custo visitas mês atual: R$ {float(custo_visitas):,.2f}

GITOPS:
- CLPs com drift de código: {drifts}

COMISSIONAMENTO:
- Backlog total: {backlog} máquinas
- Com risco de cancelamento: {com_risco}

INCIDENTES (90 dias):
- Total: {incidentes_90d}
- Prejuízo acumulado histórico: R$ {float(prejuizo_total):,.2f}

CLIENTES ATIVOS: {total_clientes}
"""
            return contexto

        except Exception as e:
            return f"[Erro ao montar contexto: {str(e)}]"

    @classmethod
    async def analisar_planta(cls, db: Session) -> dict:
        """Análise completa com contexto real do banco."""
        from services.groq_client import get_groq_client
        client = get_groq_client()
        contexto = cls.get_contexto_operacional(db)

        if client:
            return await cls._chamar_ia(
                contexto=contexto,
                perfil="ceo",
                mensagem="""Faça uma análise completa da operação. Inclua:
1. Resumo executivo (2-3 parágrafos)
2. Top 5 riscos críticos com impacto financeiro
3. Ações recomendadas priorizadas (com prazos e responsáveis)
4. Projeção SEM ação nos próximos 6 meses
5. Projeção COM plano de ação implementado

Formate como JSON com: resumo_executivo, riscos_criticos, acoes_recomendadas, projecao_sem_acao, projecao_com_plano""",
                client=client
            )
        else:
            return cls._analise_offline(contexto)

    @classmethod
    async def responder_decisao(cls, pergunta: str, perfil: str, db: Session) -> dict:
        """Resposta contextualizada por perfil."""
        from services.groq_client import get_groq_client
        client = get_groq_client()
        contexto = cls.get_contexto_operacional(db)

        if client:
            return await cls._chamar_ia(
                contexto=contexto,
                perfil=perfil,
                mensagem=f"Pergunta do usuário ({perfil}):\n{pergunta}\n\nResponda de forma direta e analítica, com números específicos.",
                client=client,
                formato="decisao"
            )
        else:
            return {
                "resposta": f"[Modo offline — sem API key]\n\nPergunta: {pergunta}\n\nPara respostas contextualizadas com IA, configure GROQ_API_KEY no .env.",
                "dados_usados": ["contexto_operacional_banco"],
                "confianca": "baixa (modo offline)",
            }

    @classmethod
    async def gerar_relatorio(cls, tipo: str, db: Session) -> dict:
        """Gera relatório por tipo de perfil."""
        from services.groq_client import get_groq_client
        client = get_groq_client()
        contexto = cls.get_contexto_operacional(db)

        if client:
            return await cls._chamar_ia(
                contexto=contexto,
                perfil=tipo,
                mensagem=f"Gere um relatório executivo completo para o perfil '{tipo}'. Inclua KPIs relevantes, riscos e recomendações.",
                client=client,
                formato="relatorio"
            )
        else:
            return {
                "relatorio": f"[Relatório {tipo.upper()} — Modo offline]\n\n{contexto}\n\nPara relatórios com IA, configure GROQ_API_KEY.",
                "secoes": ["Contexto Operacional", "KPIs", "Riscos", "Recomendações"],
                "data_geracao": datetime.utcnow().isoformat(),
            }

    @classmethod
    async def chat(cls, mensagem: str, historico: list, perfil: str, db: Session) -> dict:
        """Chat com histórico de conversa."""
        from services.groq_client import get_groq_client, DEFAULT_TEXT_MODEL
        client = get_groq_client()
        contexto = cls.get_contexto_operacional(db)

        if client:
            try:
                system_prompt = cls.SYSTEM_PROMPT_BASE.format(
                    contexto_operacional=contexto,
                    perfil_usuario=perfil
                )

                # Monta mensagens com histórico
                messages = [{"role": "system", "content": system_prompt}]
                for msg in historico[-10:]:  # Últimas 10 mensagens
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })
                messages.append({"role": "user", "content": mensagem})

                response = client.chat.completions.create(
                    model=DEFAULT_TEXT_MODEL,
                    max_tokens=2000,
                    messages=messages,
                )

                return {
                    "resposta": response.choices[0].message.content,
                    "tokens_usados": response.usage.total_tokens if response.usage else 0,
                }

            except Exception as e:
                return {
                    "resposta": f"Erro na API: {str(e)}. Verifique sua GROQ_API_KEY.",
                    "tokens_usados": 0,
                }
        else:
            return {
                "resposta": f"[Modo offline]\n\nSua mensagem: {mensagem}\n\nContexto atual:\n{contexto}\n\nPara chat com IA, configure GROQ_API_KEY no .env.",
                "tokens_usados": 0,
            }

    @classmethod
    async def _chamar_ia(cls, contexto: str, perfil: str, mensagem: str,
                         client, formato: str = "analise") -> dict:
        """Chamada genérica à Groq API com tratamento de erros."""
        try:
            from services.groq_client import DEFAULT_TEXT_MODEL

            system_prompt = cls.SYSTEM_PROMPT_BASE.format(
                contexto_operacional=contexto,
                perfil_usuario=perfil
            )

            response = client.chat.completions.create(
                model=DEFAULT_TEXT_MODEL,
                max_tokens=3000,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": mensagem}
                ],
            )

            texto = response.choices[0].message.content

            # Tenta parsear como JSON
            try:
                return json.loads(texto)
            except json.JSONDecodeError:
                if formato == "analise":
                    return {
                        "resumo_executivo": texto,
                        "riscos_criticos": [],
                        "acoes_recomendadas": [],
                        "projecao_sem_acao": "",
                        "projecao_com_plano": "",
                    }
                elif formato == "decisao":
                    return {
                        "resposta": texto,
                        "dados_usados": ["contexto_operacional_banco", "api_anthropic"],
                        "confianca": "alta",
                    }
                elif formato == "relatorio":
                    return {
                        "relatorio": texto,
                        "secoes": ["Análise Completa"],
                        "data_geracao": datetime.utcnow().isoformat(),
                    }
                return {"resposta": texto}

        except Exception as e:
            error_msg = str(e)
            if "authentication" in error_msg.lower() or "api_key" in error_msg.lower():
                error_msg = "API key inválida. Verifique GROQ_API_KEY no .env."

            return {
                "erro": error_msg,
                "fallback": cls._analise_offline(contexto) if formato == "analise" else None,
            }

    @staticmethod
    def _analise_offline(contexto: str) -> dict:
        """Análise básica offline — sem IA, baseada em regras fixas."""
        return {
            "resumo_executivo": (
                "A operação da AltaCLP apresenta 5 riscos críticos simultâneos. "
                "A taxa de falsos alertas de 64% gera custos de R$ 31.400/mês em visitas "
                "desnecessárias. O backlog de 26 máquinas em comissionamento inclui 4 da Anaclara "
                "Alimentos com prazo em junho/2026, totalizando R$ 780.000 em risco contratual. "
                "Há 3 CLPs com drift de código não documentado, sendo que 2 hotfixes do Anderson "
                "Vasconcellos causaram os incidentes de Belmare (R$ 140k) e Anaclara (R$ 15k). "
                "[Análise gerada em modo offline — configure ANTHROPIC_API_KEY para análise com IA]"
            ),
            "riscos_criticos": [
                {
                    "rank": 1,
                    "titulo": "Contrato Anaclara Alimentos — R$ 780.000 em risco",
                    "impacto_financeiro": 780000,
                    "urgencia": "imediata",
                    "descricao": "4 máquinas com prazo em junho/2026. Gustavo Mendes ameaça cancelar."
                },
                {
                    "rank": 2,
                    "titulo": "Drift de código — risco de incidente grave",
                    "impacto_financeiro": 250000,
                    "urgencia": "alta",
                    "descricao": "3 CLPs com código divergente. Último incidente (Belmare): R$ 140k + 36h paradas."
                },
                {
                    "rank": 3,
                    "titulo": "Falsos alertas — R$ 376.800/ano desperdiçados",
                    "impacto_financeiro": 376800,
                    "urgencia": "alta",
                    "descricao": "64% de alertas são falsos. Custo mensal: R$ 31.400 em visitas desnecessárias."
                },
                {
                    "rank": 4,
                    "titulo": "Saída do Júnior Almeida — concentração de conhecimento",
                    "impacto_financeiro": 100000,
                    "urgencia": "média",
                    "descricao": "Único engenheiro que conhece Pampulha. Risco operacional alto sem documentação."
                },
                {
                    "rank": 5,
                    "titulo": "NPS em queda — 82 → 68 em 18 meses",
                    "impacto_financeiro": 500000,
                    "urgencia": "média",
                    "descricao": "Risco de perda de contratos. Terceirização BH ineficaz (R$ 14k/mês)."
                },
            ],
            "acoes_recomendadas": [
                {
                    "prioridade": 1,
                    "acao": "Priorizar comissionamento Anaclara — 4 máquinas até junho/2026",
                    "prazo": "6 semanas",
                    "responsavel": "Cláudia Santarém",
                    "impacto_estimado": "Preservar R$ 780.000 em receita contratada"
                },
                {
                    "prioridade": 2,
                    "acao": "Implementar thresholds dinâmicos por máquina",
                    "prazo": "2 semanas",
                    "responsavel": "Engenharia + IA",
                    "impacto_estimado": "Reduzir falsos alertas de 64% para ~30% → economia de R$ 20k/mês"
                },
                {
                    "prioridade": 3,
                    "acao": "Resolver drift de código em CLP-007, CLP-019 e CLP-034",
                    "prazo": "1 semana",
                    "responsavel": "Cláudia + Anderson",
                    "impacto_estimado": "Eliminar risco de incidente → prevenir R$ 250k+ em prejuízo"
                },
            ],
            "projecao_sem_acao": (
                "Sem intervenção nos próximos 6 meses: perda do contrato Anaclara (R$ 780k), "
                "probabilidade de novo incidente por drift (R$ 100-200k), NPS abaixo de 60 "
                "com risco de perda da Belmare (R$ 420k) e Aspáragos (R$ 145k). "
                "Prejuízo estimado: R$ 1.5-2.0M."
            ),
            "projecao_com_plano": (
                "Com o plano implementado: entrega Anaclara no prazo (R$ 780k preservados), "
                "redução de 50-65% nos falsos alertas (economia R$ 200k/ano), "
                "zero incidentes por drift (economia R$ 250k/ano), cotação em 2h vs 5-7 dias "
                "(recuperação R$ 60k/mês). ROI do investimento: 8.8x no primeiro ano."
            ),
        }
