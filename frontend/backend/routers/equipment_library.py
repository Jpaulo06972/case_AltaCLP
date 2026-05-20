"""
AltaCLP — Biblioteca de Equipamentos (URLs externas de manuais).
"""

import math
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, HttpUrl
from typing import Optional

from database.connection import get_db
from database.models import PortfolioEquipamento, PerfilUsuario, Usuario
from middleware.rbac import require_roles, require_equipment_write
from routers.auth import get_usuario_atual

router = APIRouter(prefix="/equipment-library", tags=["Biblioteca de Equipamentos"])


class EquipamentoCreate(BaseModel):
    nome_equipamento: str
    fabricante: str
    categoria: str
    url_manual: str


class EquipamentoUpdate(BaseModel):
    nome_equipamento: Optional[str] = None
    fabricante: Optional[str] = None
    categoria: Optional[str] = None
    url_manual: Optional[str] = None


MOCK_PORTFOLIO = [
    {"nome_equipamento": "WEG W22 Three-Phase Motor", "fabricante": "WEG", "categoria": "Motor", "url_manual": "https://www.weg.net/catalog/weg/BR/pt/Motores-El%C3%A9tricos/Motores-de-Indu%C3%A7%C3%A3o-Trif%C3%A1sicos/Linha-W22/p/MKT_WEG-motor-w22"},
    {"nome_equipamento": "WEG CFW500 Variable Frequency Drive", "fabricante": "WEG", "categoria": "Inverter", "url_manual": "https://www.weg.net/catalog/weg/BR/pt/Drives-e-Soft-Starters/Drives-de-Frequ%C3%AAncia-CA/Uso-Geral/CFW500/p/MKT_WEG-cfw500"},
    {"nome_equipamento": "WEG CFW700 Variable Frequency Drive", "fabricante": "WEG", "categoria": "Inverter", "url_manual": "https://www.weg.net/catalog/weg/BR/pt/Drives-e-Soft-Starters/Drives-de-Frequ%C3%AAncia-CA/Uso-Geral/CFW700/p/MKT_WEG-cfw700"},
    {"nome_equipamento": "WEG CFW11 Variable Frequency Drive", "fabricante": "WEG", "categoria": "Inverter", "url_manual": "https://www.weg.net/catalog/weg/BR/pt/Drives-e-Soft-Starters/Drives-de-Frequ%C3%AAncia-CA/Uso-Geral/CFW11/p/MKT_WEG-cfw11"},
    {"nome_equipamento": "WEG SSW07 Soft Starter", "fabricante": "WEG", "categoria": "Soft Starter", "url_manual": "https://www.weg.net/catalog/weg/BR/pt/Drives-e-Soft-Starters/Soft-Starters/SSW07/p/MKT_WEG-ssw07"},
    {"nome_equipamento": "WEG CWM Contactors", "fabricante": "WEG", "categoria": "Contactor", "url_manual": "https://www.weg.net/catalog/weg/BR/pt/Controle-e-Prote%C3%A7%C3%A3o/Contatores-e-Rel%C3%A9s-de-Sobrecarga/Contatores/CWM/p/MKT_WEG-cwm"},
    {"nome_equipamento": "Siemens S7-1200 PLC (CPU 1214C)", "fabricante": "Siemens", "categoria": "PLC", "url_manual": "https://support.industry.siemens.com/cs/document/36932465"},
    {"nome_equipamento": "Siemens S7-1500 PLC", "fabricante": "Siemens", "categoria": "PLC", "url_manual": "https://support.industry.siemens.com/cs/document/59191792"},
    {"nome_equipamento": "Siemens S7-300 PLC", "fabricante": "Siemens", "categoria": "PLC", "url_manual": "https://support.industry.siemens.com/cs/document/23904550"},
    {"nome_equipamento": "Siemens KTP700 Basic HMI Panel", "fabricante": "Siemens", "categoria": "HMI", "url_manual": "https://support.industry.siemens.com/cs/document/73503823"},
    {"nome_equipamento": "Siemens SINAMICS G120 Inverter", "fabricante": "Siemens", "categoria": "Inverter", "url_manual": "https://support.industry.siemens.com/cs/document/44240717"},
    {"nome_equipamento": "Siemens LOGO! 8 Controller", "fabricante": "Siemens", "categoria": "PLC", "url_manual": "https://support.industry.siemens.com/cs/document/109741041"},
    {"nome_equipamento": "Danfoss VLT AQUA Drive FC 202", "fabricante": "Danfoss", "categoria": "Inverter", "url_manual": "https://www.danfoss.com/en/service-and-support/downloads/dds/vlt-aqua-drive-fc-202/"},
    {"nome_equipamento": "Danfoss VLT AutomationDrive FC 302", "fabricante": "Danfoss", "categoria": "Inverter", "url_manual": "https://www.danfoss.com/en/service-and-support/downloads/dds/vlt-automationdrive-fc-302/"},
    {"nome_equipamento": "Danfoss VLT Midi Drive FC 280", "fabricante": "Danfoss", "categoria": "Inverter", "url_manual": "https://www.danfoss.com/en/service-and-support/downloads/dds/vlt-midi-drive-fc-280/"},
    {"nome_equipamento": "Danfoss iC2-Micro Frequency Converter", "fabricante": "Danfoss", "categoria": "Inverter", "url_manual": "https://www.danfoss.com/en/service-and-support/downloads/dds/ic2-micro/"},
    {"nome_equipamento": "ABB ACS550 Drive", "fabricante": "ABB", "categoria": "Inverter", "url_manual": "https://library.e.abb.com/public/3afb000012d2a8c3c12573e700496013/ACS550_UsersManual_A4_RevD_EN_lowres.pdf"},
    {"nome_equipamento": "ABB ACS880 Industrial Drive", "fabricante": "ABB", "categoria": "Inverter", "url_manual": "https://library.e.abb.com/public/b1c5f82cd9784b6d9e8ebb07b1cba91f/ACS880-01_HW_manual_EN_RevL_3AUA0000078093.pdf"},
    {"nome_equipamento": "ABB M2M Three-Phase Motor", "fabricante": "ABB", "categoria": "Motor", "url_manual": "https://library.e.abb.com/public/06af03f60e1fdbb4c1257acb003c7d65/Low_voltage_motors_for_explosive_atmospheres.pdf"},
    {"nome_equipamento": "ABB AF Series Contactors", "fabricante": "ABB", "categoria": "Contactor", "url_manual": "https://library.e.abb.com/public/3b695c3db1264eb384a3d4f07e4f0e46/2CDC135011D0201.pdf"},
    {"nome_equipamento": "IFM IGS204 Inductive Proximity Sensor", "fabricante": "IFM", "categoria": "Sensor", "url_manual": "https://www.ifm.com/us/en/product/IGS204.html"},
    {"nome_equipamento": "IFM PN7070 Pressure Sensor", "fabricante": "IFM", "categoria": "Sensor", "url_manual": "https://www.ifm.com/us/en/product/PN7070.html"},
    {"nome_equipamento": "IFM O5D150 Photoelectric Distance Sensor", "fabricante": "IFM", "categoria": "Sensor", "url_manual": "https://www.ifm.com/us/en/product/O5D150.html"},
    {"nome_equipamento": "IFM TA3000 Temperature Sensor", "fabricante": "IFM", "categoria": "Sensor", "url_manual": "https://www.ifm.com/us/en/product/TA3000.html"},
    {"nome_equipamento": "IFM VS0100 Flow Sensor", "fabricante": "IFM", "categoria": "Sensor", "url_manual": "https://www.ifm.com/us/en/product/VS0100.html"},
    {"nome_equipamento": "IFM JN2200 Level Sensor", "fabricante": "IFM", "categoria": "Sensor", "url_manual": "https://www.ifm.com/us/en/product/JN2200.html"},
    {"nome_equipamento": "Sick W4S-3 Photoelectric Sensor", "fabricante": "Sick", "categoria": "Sensor", "url_manual": "https://www.sick.com/us/en/catalog/products/sensors/photoelectric-sensors/w4s-3/p/p365828"},
    {"nome_equipamento": "Sick TM18 Compact Photoelectric Sensor", "fabricante": "Sick", "categoria": "Sensor", "url_manual": "https://www.sick.com/us/en/catalog/products/sensors/photoelectric-sensors/tm18/p/p311655"},
    {"nome_equipamento": "Sick S300 Safety Laser Scanner", "fabricante": "Sick", "categoria": "Safety", "url_manual": "https://www.sick.com/us/en/catalog/products/safety/safety-laser-scanners/s300/p/p35346"},
    {"nome_equipamento": "Sick IME12 Inductive Sensor", "fabricante": "Sick", "categoria": "Sensor", "url_manual": "https://www.sick.com/us/en/catalog/products/sensors/inductive-sensors/ime/p/p212437"},
    {"nome_equipamento": "Balluff BSP Pressure Transmitter", "fabricante": "Balluff", "categoria": "Sensor", "url_manual": "https://www.balluff.com/en-us/products/BSP000G/"},
    {"nome_equipamento": "Balluff BES Inductive Sensor", "fabricante": "Balluff", "categoria": "Sensor", "url_manual": "https://www.balluff.com/en-us/products/BES01EP/"},
    {"nome_equipamento": "Balluff BOS Photoelectric Sensor", "fabricante": "Balluff", "categoria": "Sensor", "url_manual": "https://www.balluff.com/en-us/products/BOS00EK/"},
    {"nome_equipamento": "Balluff BIS RFID System", "fabricante": "Balluff", "categoria": "RFID", "url_manual": "https://www.balluff.com/en-us/products/BIS00A2/"},
    {"nome_equipamento": "Schneider Modicon M221 PLC", "fabricante": "Schneider Electric", "categoria": "PLC", "url_manual": "https://www.se.com/ww/en/product/TM221CE40R/modicon-m221-40-io-relay-ethernet/"},
    {"nome_equipamento": "Schneider Modicon M340 PLC", "fabricante": "Schneider Electric", "categoria": "PLC", "url_manual": "https://www.se.com/ww/en/product-range/1468-modicon-m340/"},
    {"nome_equipamento": "Schneider Altivar 312 Inverter", "fabricante": "Schneider Electric", "categoria": "Inverter", "url_manual": "https://www.se.com/ww/en/product-range/2286-altivar-312/"},
    {"nome_equipamento": "Schneider Altivar 630 Inverter", "fabricante": "Schneider Electric", "categoria": "Inverter", "url_manual": "https://www.se.com/ww/en/product-range/62087-altivar-process-630/"},
    {"nome_equipamento": "Schneider TeSys D Contactor", "fabricante": "Schneider Electric", "categoria": "Contactor", "url_manual": "https://www.se.com/ww/en/product-range/1217-tesys-d/"},
    {"nome_equipamento": "Schneider Zelio Logic Smart Relay", "fabricante": "Schneider Electric", "categoria": "Relay", "url_manual": "https://www.se.com/ww/en/product-range/2259-zelio-logic/"},
    {"nome_equipamento": "Allen-Bradley MicroLogix 1100 PLC", "fabricante": "Rockwell Automation", "categoria": "PLC", "url_manual": "https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1763-um001_-en-p.pdf"},
    {"nome_equipamento": "Allen-Bradley CompactLogix 5370 PLC", "fabricante": "Rockwell Automation", "categoria": "PLC", "url_manual": "https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1769-um021_-en-p.pdf"},
    {"nome_equipamento": "Allen-Bradley PowerFlex 525 Drive", "fabricante": "Rockwell Automation", "categoria": "Inverter", "url_manual": "https://literature.rockwellautomation.com/idc/groups/literature/documents/um/520-um001_-en-e.pdf"},
    {"nome_equipamento": "Allen-Bradley PowerFlex 755 Drive", "fabricante": "Rockwell Automation", "categoria": "Inverter", "url_manual": "https://literature.rockwellautomation.com/idc/groups/literature/documents/um/750-um001_-en-p.pdf"},
    {"nome_equipamento": "Omron CP1E PLC", "fabricante": "Omron", "categoria": "PLC", "url_manual": "https://assets.omron.eu/downloads/manual/en/v4/w480_cp1e_cpu_unit_operation_manual_en.pdf"},
    {"nome_equipamento": "Omron CJ2M PLC", "fabricante": "Omron", "categoria": "PLC", "url_manual": "https://assets.omron.eu/downloads/manual/en/v3/w472_cj2m_cpu_units_operation_manual_en.pdf"},
    {"nome_equipamento": "Omron E3Z Photoelectric Sensor", "fabricante": "Omron", "categoria": "Sensor", "url_manual": "https://assets.omron.eu/downloads/datasheet/en/v3/e102_e3z_datasheet_en.pdf"},
    {"nome_equipamento": "Omron E2E Inductive Proximity Sensor", "fabricante": "Omron", "categoria": "Sensor", "url_manual": "https://assets.omron.eu/downloads/datasheet/en/v4/n131_e2e_datasheet_en.pdf"},
]


def _seed_portfolio_if_empty(db: Session):
    if db.query(PortfolioEquipamento).count() > 0:
        return
    for item in MOCK_PORTFOLIO:
        db.add(
            PortfolioEquipamento(
                id_equipamento=uuid.uuid4(),
                nome_equipamento=item["nome_equipamento"],
                fabricante=item["fabricante"],
                categoria=item["categoria"],
                url_manual=item["url_manual"],
            )
        )
    db.commit()


@router.get("")
def listar_equipamentos(
    busca: str = None,
    categoria: str = None,
    fabricante: str = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _user=Depends(
        require_roles(
            PerfilUsuario.engenharia.value,
            PerfilUsuario.tecnico_campo.value,
            PerfilUsuario.ceo.value,
            PerfilUsuario.cfo.value,
            PerfilUsuario.vendedor.value,
        )
    ),
):
    _seed_portfolio_if_empty(db)
    q = db.query(PortfolioEquipamento)
    if busca:
        q = q.filter(
            PortfolioEquipamento.nome_equipamento.ilike(f"%{busca}%")
            | PortfolioEquipamento.fabricante.ilike(f"%{busca}%")
        )
    if categoria:
        q = q.filter(PortfolioEquipamento.categoria.ilike(categoria))
    if fabricante:
        q = q.filter(PortfolioEquipamento.fabricante.ilike(fabricante))
    total = q.count()
    items = q.order_by(PortfolioEquipamento.categoria, PortfolioEquipamento.nome_equipamento).offset(
        (page - 1) * limit
    ).limit(limit).all()
    return {
        "dados": [
            {
                "id_equipamento": str(i.id_equipamento),
                "nome_equipamento": i.nome_equipamento,
                "fabricante": i.fabricante,
                "categoria": i.categoria,
                "url_manual": i.url_manual,
                "data_cadastro": i.data_cadastro.isoformat() if i.data_cadastro else None,
            }
            for i in items
        ],
        "total": total,
        "pagina": page,
        "por_pagina": limit,
        "paginas": math.ceil(total / limit) if limit else 0,
        "categorias": ["PLC", "Sensor", "Inverter", "Motor", "Soft Starter", "Contactor", "HMI", "Safety", "RFID", "Relay"],
    }


@router.post("")
def criar_equipamento(
    body: EquipamentoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_equipment_write),
):
    item = PortfolioEquipamento(
        id_equipamento=uuid.uuid4(),
        nome_equipamento=body.nome_equipamento,
        fabricante=body.fabricante,
        categoria=body.categoria,
        url_manual=body.url_manual,
        cadastrado_por=usuario.id,
    )
    db.add(item)
    db.commit()
    return {"id_equipamento": str(item.id_equipamento), "mensagem": "Equipamento cadastrado"}


@router.put("/{equipamento_id}")
def atualizar_equipamento(
    equipamento_id: str,
    body: EquipamentoUpdate,
    db: Session = Depends(get_db),
    _user: Usuario = Depends(require_equipment_write),
):
    from uuid import UUID

    item = db.query(PortfolioEquipamento).filter(PortfolioEquipamento.id_equipamento == UUID(equipamento_id)).first()
    if not item:
        raise HTTPException(status_code=404, detail="Equipamento não encontrado")
    for field, val in body.model_dump(exclude_unset=True).items():
        setattr(item, field.replace("nome_equipamento", "nome_equipamento"), val)
    if body.nome_equipamento is not None:
        item.nome_equipamento = body.nome_equipamento
    if body.fabricante is not None:
        item.fabricante = body.fabricante
    if body.categoria is not None:
        item.categoria = body.categoria
    if body.url_manual is not None:
        item.url_manual = body.url_manual
    db.commit()
    return {"mensagem": "Atualizado"}


@router.delete("/{equipamento_id}")
def excluir_equipamento(
    equipamento_id: str,
    db: Session = Depends(get_db),
    _user: Usuario = Depends(require_equipment_write),
):
    from uuid import UUID

    item = db.query(PortfolioEquipamento).filter(PortfolioEquipamento.id_equipamento == UUID(equipamento_id)).first()
    if not item:
        raise HTTPException(status_code=404, detail="Equipamento não encontrado")
    db.delete(item)
    db.commit()
    return {"mensagem": "Removido"}
