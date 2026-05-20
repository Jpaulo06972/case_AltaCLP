"""
AltaCLP Intelligence Platform — Router de IA
Análise de planta, decisão, relatórios e chat com contexto operacional.
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import get_db
from schemas.schemas import (
    DecisaoRequest, DecisaoResponse,
    GerarRelatorioRequest, GerarRelatorioResponse,
    ChatRequest, ChatResponse,
    AnalisePlantaResponse,
)
from services.ai_analyst import AIAnalyst
from services.anomaly_detector import IsolationForestDetector
from services.threshold_engine import ThresholdEngine

router = APIRouter(prefix="/ia", tags=["Inteligência Artificial"])


@router.post("/analisar-planta")
async def analisar_planta(db: Session = Depends(get_db)):
    """
    Análise completa da operação usando IA (Anthropic API).
    Se API key não configurada, retorna análise offline baseada em regras.
    """
    try:
        resultado = await AIAnalyst.analisar_planta(db)
        return resultado
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro na análise: {str(e)}"
        )


@router.post("/decisao")
async def responder_decisao(
    body: DecisaoRequest,
    db: Session = Depends(get_db)
):
    """
    Resposta contextualizada por perfil a uma pergunta específica.
    """
    try:
        resultado = await AIAnalyst.responder_decisao(
            pergunta=body.pergunta,
            perfil=body.perfil_usuario or "ceo",
            db=db
        )
        return resultado
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar decisão: {str(e)}"
        )


@router.post("/gerar-relatorio")
async def gerar_relatorio(
    body: GerarRelatorioRequest,
    db: Session = Depends(get_db)
):
    """
    Gera relatório executivo por perfil (CEO, CFO, Engenharia, Campo, Due Diligence).
    """
    tipos_validos = ["ceo", "cfo", "engenharia", "campo", "due_diligence"]
    if body.tipo not in tipos_validos:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo inválido. Use: {', '.join(tipos_validos)}"
        )

    try:
        resultado = await AIAnalyst.gerar_relatorio(tipo=body.tipo, db=db)
        return resultado
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar relatório: {str(e)}"
        )


@router.post("/chat")
async def chat(
    body: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Chat interativo com contexto operacional completo.
    Mantém histórico de conversa.
    """
    try:
        resultado = await AIAnalyst.chat(
            mensagem=body.mensagem,
            historico=body.historico,
            perfil=body.perfil,
            db=db
        )
        return resultado
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro no chat: {str(e)}"
        )


@router.get("/modelos/status")
def status_modelos():
    """Status dos modelos de ML (Isolation Forest) treinados."""
    return IsolationForestDetector.status_modelos()


@router.post("/treinar-modelo/{maquina_id}")
def treinar_modelo(maquina_id: str, db: Session = Depends(get_db)):
    """Treina modelo Isolation Forest para uma máquina específica."""
    try:
        resultado = IsolationForestDetector.treinar_modelo(db, maquina_id)
        return resultado
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao treinar modelo: {str(e)}"
        )


@router.post("/threshold-dinamico/{maquina_id}")
def calcular_threshold(maquina_id: str, db: Session = Depends(get_db)):
    """Calcula thresholds dinâmicos para uma máquina específica."""
    try:
        resultado = ThresholdEngine.calcular_threshold_dinamico(db, maquina_id)
        return resultado
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao calcular threshold: {str(e)}"
        )
