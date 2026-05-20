"""
AltaCLP Intelligence Platform — Simulador de Telemetria
Gera leituras de sensores em tempo real para todas as máquinas ativas.
Injeta anomalias com probabilidade proporcional ao histórico de cada CLP.
"""

import uuid
import asyncio
import random
import math
from datetime import datetime
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from database.models import (
    Maquina, LeituraSensor, Alerta, StatusMaquina,
    StatusOperacao, Turno, FonteLeitura,
    TipoAlerta, SeveridadeAlerta, StatusAlerta, OrigemAlerta
)


class TelemetriaSimulator:
    """
    Gera telemetria simulada em tempo real para todas as máquinas ativas.
    Roda como background task do FastAPI com asyncio.
    """

    # Contadores para gerar códigos de alerta únicos
    _alerta_counter = 5000
    _running = False

    @classmethod
    def gerar_leitura(cls, maquina, timestamp=None) -> dict:
        """
        Gera uma leitura realista para uma máquina específica.
        Considera: turno, temperatura ambiente, status da máquina, taxa de falso alerta.
        """
        if timestamp is None:
            timestamp = datetime.utcnow()

        hora = timestamp.hour

        # Determina turno
        if 6 <= hora < 14:
            turno = Turno.manha
            turno_offset = 2.0  # +5% carga no turno da manhã
        elif 14 <= hora < 22:
            turno = Turno.tarde
            turno_offset = 0.0  # Nominal
        else:
            turno = Turno.noite
            turno_offset = -3.0  # -10% carga à noite

        # Offset por hora do dia (ciclo diurno)
        hora_offset = math.sin(hora / 24 * 2 * math.pi) * 1.5

        # Temperatura ambiente simulada (25-38°C dependendo da hora)
        temp_ambiente = 28 + 5 * math.sin((hora - 6) / 24 * 2 * math.pi)

        # Parâmetros base dependem do status da máquina
        if maquina.status == StatusMaquina.offline:
            return {
                "temperatura": None,
                "pressao": None,
                "vibracao": None,
                "corrente": 0,
                "tensao": 0,
                "rpm": 0,
                "status_operacao": StatusOperacao.desligada,
                "turno": turno,
                "temperatura_ambiente": round(temp_ambiente, 1),
                "timestamp": timestamp,
            }

        # Base varia por tipo de máquina (máquinas críticas tendem a ter valores mais altos)
        if maquina.status == StatusMaquina.critico:
            temp_base = 82.0
            press_base = 4.0
            vib_base = 3.2
        elif maquina.status == StatusMaquina.alerta:
            temp_base = 78.0
            press_base = 3.6
            vib_base = 2.8
        else:
            temp_base = 72.0
            press_base = 3.2
            vib_base = 2.1

        # Gera valores com ruído gaussiano
        temperatura = random.gauss(temp_base, 3.5) + turno_offset + hora_offset
        pressao = random.gauss(press_base, 0.4)
        vibracao = random.gauss(vib_base, 0.6)
        corrente = random.gauss(8.5, 1.2) + turno_offset * 0.3
        tensao = random.gauss(380, 5)
        rpm = random.gauss(1750, 30) if random.random() > 0.1 else 0

        # Injeta picos de alerta baseado na taxa de falso alerta da máquina
        taxa_falso = maquina.taxa_falso_alerta or 0.5
        if random.random() < 0.08:  # 8% chance de gerar pico
            # Decide se é falso alerta ou real
            if random.random() < taxa_falso:
                # Falso alerta — valor ligeiramente acima do threshold
                sensor_pico = random.choice(["temperatura", "pressao", "vibracao"])
                if sensor_pico == "temperatura":
                    threshold = maquina.threshold_temperatura_max or 85
                    temperatura = threshold + random.uniform(0.5, 3.0)
                elif sensor_pico == "pressao":
                    threshold = maquina.threshold_pressao_max or 4.5
                    pressao = threshold + random.uniform(0.1, 0.5)
                else:
                    threshold = maquina.threshold_vibracao_max or 3.5
                    vibracao = threshold + random.uniform(0.2, 1.0)
            else:
                # Alerta real — valor significativamente acima do threshold
                sensor_pico = random.choice(["temperatura", "pressao", "vibracao"])
                if sensor_pico == "temperatura":
                    temperatura += random.uniform(15, 25)
                elif sensor_pico == "pressao":
                    pressao += random.uniform(1.5, 3.0)
                else:
                    vibracao += random.uniform(2.0, 4.0)

        # Status de operação
        if rpm > 100:
            status_op = StatusOperacao.ligada
        elif random.random() < 0.05:
            status_op = StatusOperacao.falha
        else:
            status_op = StatusOperacao.standby

        return {
            "temperatura": round(float(temperatura), 2),
            "pressao": round(float(max(0, pressao)), 2),
            "vibracao": round(float(max(0, vibracao)), 2),
            "corrente": round(float(max(0, corrente)), 2),
            "tensao": round(float(max(0, tensao)), 1),
            "rpm": round(float(max(0, rpm)), 0),
            "status_operacao": status_op,
            "turno": turno,
            "temperatura_ambiente": round(float(temp_ambiente), 1),
            "timestamp": timestamp,
        }

    @classmethod
    async def loop_simulacao(cls):
        """
        Roda em background task. Gera leituras a cada 60s para todas as máquinas.
        Persiste no banco e dispara alertas se threshold violado.
        """
        cls._running = True
        print("[SIMULATOR] Iniciando loop de simulação de telemetria...")

        while cls._running:
            try:
                db = SessionLocal()
                maquinas = db.query(Maquina).filter(
                    Maquina.status != StatusMaquina.offline
                ).all()

                for maquina in maquinas:
                    leitura_data = cls.gerar_leitura(maquina)

                    # Persiste leitura
                    leitura = LeituraSensor(
                        maquina_id=maquina.id,
                        timestamp=leitura_data["timestamp"],
                        temperatura=leitura_data["temperatura"],
                        pressao=leitura_data["pressao"],
                        vibracao=leitura_data["vibracao"],
                        corrente=leitura_data["corrente"],
                        tensao=leitura_data["tensao"],
                        rpm=leitura_data["rpm"],
                        status_operacao=leitura_data["status_operacao"],
                        turno=leitura_data["turno"],
                        temperatura_ambiente=leitura_data["temperatura_ambiente"],
                        fonte=FonteLeitura.simulado,
                    )
                    db.add(leitura)

                    # Atualiza última leitura da máquina
                    maquina.ultima_leitura = leitura_data["timestamp"]

                    # Verifica se gerou alerta
                    cls._verificar_alerta(db, maquina, leitura_data)

                db.commit()
                db.close()

            except Exception as e:
                print(f"[SIMULATOR] Erro no loop: {e}")
                try:
                    db.rollback()
                    db.close()
                except Exception:
                    pass

            await asyncio.sleep(60)  # Espera 60 segundos

    @classmethod
    def _verificar_alerta(cls, db: Session, maquina, leitura_data: dict):
        """
        Verifica se a leitura gerou violação de threshold.
        Se sim, cria alerta no banco.
        """
        sensores_check = [
            ("temperatura", maquina.threshold_temperatura_max, TipoAlerta.temperatura_alta),
            ("pressao", maquina.threshold_pressao_max, TipoAlerta.pressao_alta),
            ("vibracao", maquina.threshold_vibracao_max, TipoAlerta.vibracao_alta),
            ("corrente", maquina.threshold_corrente_max, TipoAlerta.corrente_alta),
        ]

        for sensor_nome, threshold, tipo_alerta in sensores_check:
            valor = leitura_data.get(sensor_nome)
            if valor and threshold and valor > threshold:
                cls._alerta_counter += 1
                excesso = ((valor - threshold) / threshold) * 100

                if excesso > 20:
                    severidade = SeveridadeAlerta.emergencia
                elif excesso > 10:
                    severidade = SeveridadeAlerta.critico
                else:
                    severidade = SeveridadeAlerta.aviso

                alerta = Alerta(
                    id=uuid.uuid4(),
                    maquina_id=maquina.id,
                    cliente_id=maquina.cliente_id,
                    codigo_alerta=f"ALT-2026-{cls._alerta_counter:06d}",
                    tipo=tipo_alerta,
                    severidade=severidade,
                    titulo=f"{sensor_nome.capitalize()} acima do limite em {maquina.codigo}",
                    descricao=f"Valor: {valor:.2f} | Threshold: {threshold:.2f} | Excesso: {excesso:.1f}%",
                    valor_sensor=valor,
                    threshold_configurado=threshold,
                    timestamp_criacao=leitura_data["timestamp"],
                    status=StatusAlerta.aberto,
                    origem=OrigemAlerta.threshold,
                )
                db.add(alerta)

    @classmethod
    def parar(cls):
        """Para o loop de simulação."""
        cls._running = False
        print("[SIMULATOR] Loop de simulação parado.")

    @classmethod
    async def gerar_evento_sse(cls):
        """
        Generator para Server-Sent Events.
        Gera um alerta simulado a cada 15 segundos.
        """
        while True:
            try:
                db = SessionLocal()
                maquinas = db.query(Maquina).filter(
                    Maquina.status.in_([StatusMaquina.alerta, StatusMaquina.critico])
                ).all()

                if maquinas:
                    maquina = random.choice(maquinas)
                    leitura = cls.gerar_leitura(maquina)

                    # Força um pico para o SSE
                    sensor = random.choice(["temperatura", "pressao", "vibracao"])
                    if sensor == "temperatura":
                        threshold = maquina.threshold_temperatura_max or 85
                        leitura["temperatura"] = round(threshold + random.uniform(1, 8), 2)
                    elif sensor == "pressao":
                        threshold = maquina.threshold_pressao_max or 4.5
                        leitura["pressao"] = round(threshold + random.uniform(0.3, 1.5), 2)
                    else:
                        threshold = maquina.threshold_vibracao_max or 3.5
                        leitura["vibracao"] = round(threshold + random.uniform(0.5, 2.0), 2)

                    import json
                    evento = {
                        "evento": "novo_alerta",
                        "alerta": {
                            "maquina_codigo": maquina.codigo,
                            "maquina_nome": maquina.nome,
                            "sensor": sensor,
                            "valor": leitura[sensor],
                            "threshold": threshold,
                            "severidade": "crítico" if leitura[sensor] > threshold * 1.15 else "aviso",
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    }
                    yield f"data: {json.dumps(evento, ensure_ascii=False)}\n\n"

                db.close()
            except Exception as e:
                print(f"[SSE] Erro: {e}")
                try:
                    db.close()
                except Exception:
                    pass

            await asyncio.sleep(15)
