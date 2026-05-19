"""
AltaCLP — Árvore de equipamentos (sensores, motores, inversores) + telemetria MQTT simulada.
"""

import random
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database.connection import get_db
from database.models import (
    EquipamentoPlanta, Maquina, LogThreshold, TipoEquipamento, PerfilUsuario,
)
from middleware.rbac import require_roles
from routers.auth import get_usuario_atual
from services.tecnico_scope import assert_maquina_acesso, is_tecnico

router = APIRouter(prefix="/equipamentos", tags=["Equipamentos da Planta"])


class ThresholdUpdateBody(BaseModel):
    parametro: str
    valor_novo: float
    origem: str = "manual"
    equipamento_id: str | None = None


PLC_LABELS = {
    "siemens_s7": "Siemens S7",
    "allen_bradley": "Allen-Bradley",
    "schneider": "Schneider",
    "weg": "WEG",
    "weintek": "Weintek",
}


def _ensure_equipment_tree(db: Session, maquina_id: UUID):
    if db.query(EquipamentoPlanta).filter(EquipamentoPlanta.maquina_id == maquina_id).count() > 0:
        return
    templates = [
        ("TT-101", "Sensor Temperatura Extrusora", TipoEquipamento.sensor, "°C", 72, 60, 95),
        ("PT-201", "Sensor Pressão Linha", TipoEquipamento.sensor, "bar", 3.2, 0, 6),
        ("VT-301", "Sensor Vibração Motor", TipoEquipamento.sensor, "mm/s", 1.8, 0, 5),
        ("MTR-01", "Motor Principal Extrusora", TipoEquipamento.motor, "A", 12.5, 0, 20),
        ("INV-01", "Inversor WEG CFW500", TipoEquipamento.inversor, "Hz", 45, 0, 60),
    ]
    for tag, nome, tipo, un, val, tmin, tmax in templates:
        db.add(
            EquipamentoPlanta(
                maquina_id=maquina_id,
                tag=tag,
                nome=nome,
                tipo=tipo,
                unidade=un,
                valor_atual=val + random.uniform(-0.5, 0.5),
                threshold_min=tmin,
                threshold_max=tmax,
            )
        )
    db.commit()


@router.get("/maquina/{maquina_id}/arvore")
def arvore_equipamentos(
    maquina_id: UUID,
    db: Session = Depends(get_db),
    _user=Depends(
        require_roles(
            PerfilUsuario.engenharia.value,
            PerfilUsuario.tecnico_campo.value,
        )
    ),
):
    maq = db.query(Maquina).filter(Maquina.id == maquina_id).first()
    if not maq:
        raise HTTPException(status_code=404, detail="Máquina não encontrada")
    _ensure_equipment_tree(db, maquina_id)
    items = db.query(EquipamentoPlanta).filter(EquipamentoPlanta.maquina_id == maquina_id).all()
    return {
        "maquina_id": str(maquina_id),
        "modelo_clp_label": PLC_LABELS.get(maq.modelo_clp.value if maq.modelo_clp else "", "—"),
        "resumo_aplicacao": maq.observacoes or f"Automação industrial — {maq.nome} no setor {maq.setor_planta or 'planta'}.",
        "equipamentos": [
            {
                "id": str(e.id),
                "tag": e.tag,
                "nome": e.nome,
                "tipo": e.tipo.value if e.tipo else None,
                "unidade": e.unidade,
                "valor_atual": round(e.valor_atual or 0, 2),
                "threshold_min": e.threshold_min,
                "threshold_max": e.threshold_max,
                "ultima_atualizacao": e.ultima_atualizacao.isoformat() if e.ultima_atualizacao else None,
            }
            for e in items
        ],
    }


@router.get("/{equipamento_id}/telemetria")
def telemetria_equipamento(
    equipamento_id: UUID,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(PerfilUsuario.engenharia.value, PerfilUsuario.tecnico_campo.value)),
):
    """Stream simulado de telemetria MQTT (último valor + histórico curto)."""
    eq = db.query(EquipamentoPlanta).filter(EquipamentoPlanta.id == equipamento_id).first()
    if not eq:
        raise HTTPException(status_code=404, detail="Equipamento não encontrado")
    eq.valor_atual = (eq.valor_atual or 0) + random.uniform(-0.3, 0.3)
    eq.ultima_atualizacao = datetime.utcnow()
    db.commit()
    historico = [
        {"timestamp": datetime.utcnow().isoformat(), "valor": round(eq.valor_atual, 2)}
        for _ in range(10)
    ]
    return {
        "tag": eq.tag,
        "valor_atual": round(eq.valor_atual, 2),
        "unidade": eq.unidade,
        "threshold_min": eq.threshold_min,
        "threshold_max": eq.threshold_max,
        "fonte": "mqtt_simulado",
        "historico": historico,
    }


@router.put("/threshold")
def atualizar_threshold(
    body: ThresholdUpdateBody,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_atual),
):
    """Grava threshold no equipamento/CLP e registra audit log."""
    if body.equipamento_id:
        eq_pre = db.query(EquipamentoPlanta).filter(EquipamentoPlanta.id == UUID(body.equipamento_id)).first()
        if eq_pre:
            assert_maquina_acesso(db, usuario, eq_pre.maquina_id)
    valor_antigo = None
    eq = None
    if body.equipamento_id:
        eq = db.query(EquipamentoPlanta).filter(EquipamentoPlanta.id == UUID(body.equipamento_id)).first()
        if not eq:
            raise HTTPException(status_code=404, detail="Equipamento não encontrado")
        if body.parametro in ("threshold_max", "max"):
            valor_antigo = eq.threshold_max
            eq.threshold_max = body.valor_novo
        elif body.parametro in ("threshold_min", "min"):
            valor_antigo = eq.threshold_min
            eq.threshold_min = body.valor_novo
        eq.ultima_atualizacao = datetime.utcnow()

    user_id = "IA" if body.origem == "ia" else str(usuario.id)
    if body.origem == "ia" and usuario.perfil.value != PerfilUsuario.engenharia.value:
        raise HTTPException(status_code=403, detail="Sugestões IA requerem aprovação de engenheiro")

    log = LogThreshold(
        id_equipamento=eq.id if eq else None,
        maquina_id=eq.maquina_id if eq else None,
        parametro_alterado=body.parametro,
        valor_antigo=valor_antigo,
        valor_novo=body.valor_novo,
        id_usuario=user_id,
        origem=body.origem,
    )
    db.add(log)
    db.commit()
    return {
        "sucesso": True,
        "valor_antigo": valor_antigo,
        "valor_novo": body.valor_novo,
        "id_registro": str(log.id_registro),
        "plc_sync": "simulado_opc_ua",
    }
