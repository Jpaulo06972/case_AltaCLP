"""
AltaCLP Intelligence Platform — Detector de Anomalias (Isolation Forest)
Usa scikit-learn para detectar anomalias em séries de telemetria por máquina.
"""

import random
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from database.models import LeituraSensor, Turno

try:
    import numpy as np
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    HAS_ML = True
except ImportError:
    HAS_ML = False
    print("[IA] scikit-learn ou numpy não instalados. Ativando detector em modo Fallback Heurístico.")


class IsolationForestDetector:
    """
    Detector de anomalias baseado em Isolation Forest.
    Treina um modelo por máquina usando dados históricos.
    Features: temperatura, pressão, vibração, corrente, turno (encoded), hora do dia.
    """

    # Cache de modelos treinados em memória {maquina_id: (modelo, scaler, timestamp)}
    _modelos: dict = {}

    @classmethod
    def treinar_modelo(cls, db: Session, maquina_id, dias_historico: int = 60) -> dict:
        """
        Treina Isolation Forest com dados históricos da máquina.
        contamination=0.1 → assume 10% de anomalias nos dados históricos.
        """
        data_inicio = datetime.utcnow() - timedelta(days=dias_historico)

        leituras = db.query(LeituraSensor).filter(
            LeituraSensor.maquina_id == maquina_id,
            LeituraSensor.timestamp >= data_inicio
        ).order_by(LeituraSensor.timestamp).all()

        if not HAS_ML:
            return {
                "status": "treinado_mock",
                "maquina_id": str(maquina_id),
                "amostras_treino": len(leituras) if leituras else 100,
                "anomalias_no_historico": int(len(leituras) * 0.05) if leituras else 5,
                "taxa_anomalia_historica": 5.0,
                "score_medio": 0.45,
                "score_min": 0.1,
                "treinado_em": datetime.utcnow().isoformat(),
                "mensagem": "Modelo simulado (scikit-learn não instalado)."
            }

        if len(leituras) < 50:
            return {
                "status": "dados_insuficientes",
                "leituras": len(leituras),
                "minimo": 50,
                "mensagem": f"Necessário mínimo de 50 leituras, encontradas {len(leituras)}"
            }

        # Monta a matriz de features
        X = cls._extrair_features(leituras)

        if X.shape[0] < 50:
            return {
                "status": "dados_insuficientes",
                "leituras_validas": X.shape[0],
                "mensagem": "Muitas leituras com valores nulos"
            }

        # Normaliza features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Treina Isolation Forest
        modelo = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100,
            max_samples='auto'
        )
        modelo.fit(X_scaled)

        # Armazena em cache
        maquina_key = str(maquina_id)
        cls._modelos[maquina_key] = {
            "modelo": modelo,
            "scaler": scaler,
            "treinado_em": datetime.utcnow(),
            "amostras": X.shape[0],
            "features": X.shape[1],
        }

        # Calcula métricas do modelo treinado
        scores = modelo.decision_function(X_scaled)
        predictions = modelo.predict(X_scaled)
        anomalias_detectadas = int(np.sum(predictions == -1))

        return {
            "status": "treinado",
            "maquina_id": str(maquina_id),
            "amostras_treino": X.shape[0],
            "anomalias_no_historico": anomalias_detectadas,
            "taxa_anomalia_historica": round(anomalias_detectadas / X.shape[0] * 100, 2),
            "score_medio": round(float(np.mean(scores)), 4),
            "score_min": round(float(np.min(scores)), 4),
            "treinado_em": datetime.utcnow().isoformat(),
        }

    @classmethod
    def detectar_anomalia(cls, maquina_id, leitura_dict: dict) -> dict:
        """
        Aplica modelo treinado numa leitura individual.
        Retorna: é_anomalia, score, features que mais contribuíram.
        """
        if not HAS_ML:
            temperatura = leitura_dict.get("temperatura", 0.0) or 0.0
            pressao = leitura_dict.get("pressao", 0.0) or 0.0
            vibracao = leitura_dict.get("vibracao", 0.0) or 0.0
            
            # Anomalia simples: se algum sensor estiver muito fora do padrão
            é_anomalia = temperatura > 82.0 or pressao > 4.2 or vibracao > 3.0
            score = -0.12 if é_anomalia else 0.45
            
            features_contribuintes = []
            if é_anomalia:
                if temperatura > 82.0:
                    features_contribuintes.append({
                        "feature": "temperatura", "valor": round(temperatura, 2),
                        "esperado": 72.0, "desvio_sigma": 3.0
                    })
                if pressao > 4.2:
                    features_contribuintes.append({
                        "feature": "pressao", "valor": round(pressao, 2),
                        "esperado": 3.2, "desvio_sigma": 2.5
                    })
                if vibracao > 3.0:
                    features_contribuintes.append({
                        "feature": "vibracao", "valor": round(vibracao, 2),
                        "esperado": 2.1, "desvio_sigma": 2.5
                    })
                    
            return {
                "é_anomalia": é_anomalia,
                "score": score,
                "predicao_raw": -1 if é_anomalia else 1,
                "features_contribuintes": features_contribuintes[:3],
                "modelo_treinado_em": datetime.utcnow().isoformat(),
                "modo": "Heurística (scikit-learn Offline)"
            }

        maquina_key = str(maquina_id)

        if maquina_key not in cls._modelos:
            return {
                "erro": "Modelo não treinado para esta máquina",
                "sugestao": f"Chame POST /ia/treinar-modelo/{maquina_id} primeiro"
            }

        modelo_info = cls._modelos[maquina_key]
        modelo = modelo_info["modelo"]
        scaler = modelo_info["scaler"]

        # Monta feature vector de uma leitura
        turno_map = {"manhã": 0, "tarde": 1, "noite": 2}
        timestamp = leitura_dict.get("timestamp", datetime.utcnow())
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)

        features = [
            leitura_dict.get("temperatura", 0) or 0,
            leitura_dict.get("pressao", 0) or 0,
            leitura_dict.get("vibracao", 0) or 0,
            leitura_dict.get("corrente", 0) or 0,
            leitura_dict.get("tensao", 0) or 0,
            turno_map.get(leitura_dict.get("turno", "manhã"), 0),
            timestamp.hour if hasattr(timestamp, 'hour') else 12,
            leitura_dict.get("temperatura_ambiente", 25) or 25,
        ]

        X = np.array([features])
        X_scaled = scaler.transform(X)

        # Previsão: 1 = normal, -1 = anomalia
        predicao = modelo.predict(X_scaled)[0]
        score = modelo.decision_function(X_scaled)[0]

        # Identifica features que mais contribuíram para anomalia
        feature_names = ["temperatura", "pressao", "vibracao", "corrente",
                         "tensao", "turno", "hora_dia", "temp_ambiente"]
        features_contribuintes = []

        if predicao == -1:
            # Compara cada feature com a média esperada
            media_features = scaler.mean_
            for i, (nome, val, media) in enumerate(zip(feature_names, features, media_features)):
                desvio = abs(val - media) / (scaler.scale_[i] + 1e-8)
                if desvio > 2.0:  # Mais de 2σ da média
                    features_contribuintes.append({
                        "feature": nome,
                        "valor": round(val, 2),
                        "esperado": round(float(media), 2),
                        "desvio_sigma": round(float(desvio), 2),
                    })

            # Ordena por desvio (maior desvio = maior contribuição)
            features_contribuintes.sort(key=lambda x: x["desvio_sigma"], reverse=True)

        return {
            "é_anomalia": predicao == -1,
            "score": round(float(score), 4),
            "predicao_raw": int(predicao),
            "features_contribuintes": features_contribuintes[:3],  # Top 3
            "modelo_treinado_em": modelo_info["treinado_em"].isoformat(),
        }

    @classmethod
    def status_modelos(cls) -> dict:
        """
        Retorna status de todos os modelos treinados.
        Usado pelo dashboard de engenharia.
        """
        modelos_info = []
        for maquina_key, info in cls._modelos.items():
            modelos_info.append({
                "maquina_id": maquina_key,
                "amostras_treino": info["amostras"],
                "features": info["features"],
                "treinado_em": info["treinado_em"].isoformat(),
            })

        return {
            "maquinas_com_modelo": len(cls._modelos),
            "modelos": modelos_info,
            "ultima_atualizacao": datetime.utcnow().isoformat(),
        }

    @staticmethod
    def _extrair_features(leituras):
        """
        Extrai matriz de features a partir de leituras do banco.
        Ignora leituras com valores nulos nos sensores principais.
        """
        turno_map = {"manhã": 0, "tarde": 1, "noite": 2}
        rows = []

        for l in leituras:
            if l.temperatura is None or l.pressao is None or l.vibracao is None:
                continue

            rows.append([
                l.temperatura,
                l.pressao,
                l.vibracao,
                l.corrente or 0,
                l.tensao or 0,
                turno_map.get(l.turno.value if l.turno else "manhã", 0),
                l.timestamp.hour if l.timestamp else 12,
                l.temperatura_ambiente or 25,
            ])

        return np.array(rows) if rows else np.array([]).reshape(0, 8)
