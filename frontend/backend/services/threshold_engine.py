"""
AltaCLP Intelligence Platform — Motor de Thresholds Dinâmicos
Calcula thresholds por máquina usando estatística sobre dados históricos,
eliminando a abordagem de threshold fixo que gera 64% de falsos alertas.
"""

import statistics
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from database.models import LeituraSensor, Maquina, Turno


class ThresholdEngine:
    """
    Motor de thresholds dinâmicos por máquina.
    Substitui os thresholds fixos (causa raiz dos 64% de falsos alertas)
    por limites calculados com base no comportamento real de cada CLP.
    """

    # Multiplicador de desvios padrão — 2.5σ captura 99.4% dos valores normais
    SIGMA_MULTIPLIER = 2.5

    @staticmethod
    def calcular_threshold_dinamico(db: Session, maquina_id, historico_dias: int = 30) -> dict:
        """
        Analisa os últimos N dias de telemetria da máquina específica.
        Calcula média + 2.5σ para cada sensor, por turno.
        Retorna thresholds sugeridos + redução estimada de falsos alertas.
        """
        data_inicio = datetime.utcnow() - timedelta(days=historico_dias)

        leituras = db.query(LeituraSensor).filter(
            LeituraSensor.maquina_id == maquina_id,
            LeituraSensor.timestamp >= data_inicio
        ).all()

        if not leituras or len(leituras) < 10:
            return {
                "erro": "Dados insuficientes",
                "leituras_encontradas": len(leituras) if leituras else 0,
                "minimo_necessario": 10
            }

        # Extrai arrays de valores
        temps = [l.temperatura for l in leituras if l.temperatura is not None]
        pressoes = [l.pressao for l in leituras if l.pressao is not None]
        vibracoes = [l.vibracao for l in leituras if l.vibracao is not None]
        correntes = [l.corrente for l in leituras if l.corrente is not None]

        def calc_threshold(valores):
            if not valores:
                return None
            if len(valores) < 2:
                return round(float(valores[0]), 2)
            media = statistics.mean(valores)
            desvio = statistics.pstdev(valores)
            return round(float(media + ThresholdEngine.SIGMA_MULTIPLIER * desvio), 2)

        # Thresholds por turno (mais granular)
        thresholds_por_turno = {}
        for turno_val in [Turno.manha, Turno.tarde, Turno.noite]:
            leituras_turno = [l for l in leituras if l.turno == turno_val]
            if leituras_turno:
                t_temps = [l.temperatura for l in leituras_turno if l.temperatura is not None]
                t_press = [l.pressao for l in leituras_turno if l.pressao is not None]
                t_vibr = [l.vibracao for l in leituras_turno if l.vibracao is not None]
                t_corr = [l.corrente for l in leituras_turno if l.corrente is not None]
                thresholds_por_turno[turno_val.value] = {
                    "temperatura_max": calc_threshold(t_temps),
                    "pressao_max": calc_threshold(t_press),
                    "vibracao_max": calc_threshold(t_vibr),
                    "corrente_max": calc_threshold(t_corr),
                }

        # Threshold geral (fallback)
        thresholds_gerais = {
            "temperatura_max": calc_threshold(temps),
            "pressao_max": calc_threshold(pressoes),
            "vibracao_max": calc_threshold(vibracoes),
            "corrente_max": calc_threshold(correntes),
        }

        # Estatísticas descritivas
        estatisticas = {}
        for nome, valores in [("temperatura", temps), ("pressao", pressoes),
                               ("vibracao", vibracoes), ("corrente", correntes)]:
            if valores:
                estatisticas[nome] = {
                    "media": round(float(statistics.mean(valores)), 2),
                    "desvio_padrao": round(float(statistics.pstdev(valores) if len(valores) > 1 else 0.0), 2),
                    "min": round(float(min(valores)), 2),
                    "max": round(float(max(valores)), 2),
                    "mediana": round(float(statistics.median(valores)), 2),
                }

        return {
            "maquina_id": str(maquina_id),
            "historico_dias": historico_dias,
            "total_leituras_analisadas": len(leituras),
            "thresholds_sugeridos": thresholds_gerais,
            "thresholds_por_turno": thresholds_por_turno,
            "estatisticas": estatisticas,
            "reducao_estimada_falsos_pct": ThresholdEngine._estimar_reducao(
                db, maquina_id, thresholds_gerais, data_inicio
            )
        }

    @staticmethod
    def avaliar_alerta(leitura: dict, thresholds_maquina: dict) -> dict:
        """
        Decide se uma leitura é alerta real ou falso alerta.
        Considera: valor vs threshold, contexto de turno.
        """
        alertas = []
        probabilidade_falso = 0.0

        sensores = [
            ("temperatura", "temperatura_max"),
            ("pressao", "pressao_max"),
            ("vibracao", "vibracao_max"),
            ("corrente", "corrente_max"),
        ]

        for sensor, threshold_key in sensores:
            valor = leitura.get(sensor)
            limite = thresholds_maquina.get(threshold_key)

            if valor is not None and limite is not None and valor > limite:
                # Quanto acima do threshold está?
                excesso_pct = ((valor - limite) / limite) * 100

                if excesso_pct > 20:
                    severidade = "emergência"
                    probabilidade_falso = 0.05
                elif excesso_pct > 10:
                    severidade = "crítico"
                    probabilidade_falso = 0.15
                elif excesso_pct > 5:
                    severidade = "aviso"
                    probabilidade_falso = 0.40
                else:
                    severidade = "info"
                    probabilidade_falso = 0.70  # Perto do threshold = alta chance de falso

                alertas.append({
                    "sensor": sensor,
                    "valor": valor,
                    "threshold": limite,
                    "excesso_pct": round(excesso_pct, 2),
                    "severidade": severidade,
                })

        é_alerta = len(alertas) > 0
        if alertas:
            # Severidade máxima entre os sensores
            severidade_final = max(alertas, key=lambda a: {
                "info": 0, "aviso": 1, "crítico": 2, "emergência": 3
            }.get(a["severidade"], 0))["severidade"]
        else:
            severidade_final = None

        return {
            "é_alerta": é_alerta,
            "severidade": severidade_final,
            "probabilidade_falso": round(probabilidade_falso, 2),
            "detalhes_sensores": alertas,
        }

    @staticmethod
    def projetar_reducao_falsos(db: Session, maquina_id, novos_thresholds: dict) -> float:
        """
        Simula a redução de falsos alertas aplicando novos thresholds
        sobre os dados históricos. Compara com os thresholds atuais.
        """
        data_inicio = datetime.utcnow() - timedelta(days=90)
        return ThresholdEngine._estimar_reducao(db, maquina_id, novos_thresholds, data_inicio)

    @staticmethod
    def _estimar_reducao(db: Session, maquina_id, novos_thresholds: dict, data_inicio) -> float:
        """
        Calcula a redução estimada de falsos alertas comparando
        thresholds atuais vs novos thresholds sobre dados históricos.
        """
        maquina = db.query(Maquina).filter(Maquina.id == maquina_id).first()
        if not maquina:
            return 0.0

        leituras = db.query(LeituraSensor).filter(
            LeituraSensor.maquina_id == maquina_id,
            LeituraSensor.timestamp >= data_inicio
        ).all()

        if not leituras:
            return 0.0

        # Conta alertas com threshold atual vs novo
        alertas_antigos = 0
        alertas_novos = 0

        for l in leituras:
            # Threshold antigo
            if (l.temperatura and maquina.threshold_temperatura_max and
                    l.temperatura > maquina.threshold_temperatura_max):
                alertas_antigos += 1
            if (l.pressao and maquina.threshold_pressao_max and
                    l.pressao > maquina.threshold_pressao_max):
                alertas_antigos += 1

            # Threshold novo
            novo_temp = novos_thresholds.get("temperatura_max")
            novo_press = novos_thresholds.get("pressao_max")

            if novo_temp and l.temperatura and l.temperatura > novo_temp:
                alertas_novos += 1
            if novo_press and l.pressao and l.pressao > novo_press:
                alertas_novos += 1

        if alertas_antigos == 0:
            return 0.0

        reducao = ((alertas_antigos - alertas_novos) / alertas_antigos) * 100
        return round(max(0.0, min(reducao, 100.0)), 1)
