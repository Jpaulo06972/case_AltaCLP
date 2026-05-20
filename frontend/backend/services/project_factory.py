"""
Criação transacional de Projeto + Máquina + Comissionamento a partir de cotação/draft.
"""

import uuid
import json
from datetime import datetime, date
from typing import Any, Optional

from sqlalchemy.orm import Session

from database.models import (
    Projeto,
    Maquina,
    Comissionamento,
    Cliente,
    ProjetoHistorico,
    ProjetoPendencia,
    StatusComissionamento,
    FaseProjeto,
    ModeloCLP,
    ProtocoloCLP,
    StatusMaquina,
    SetorCliente,
    StatusTarefaPendencia,
    Usuario,
)

DEFAULT_PENDENCIAS = [
    "Validar especificação técnica com engenharia",
    "Confirmar layout elétrico e IO",
    "Agendar visita técnica de campo",
    "Preparar documentação FAT",
]


def _resolve_cliente(db: Session, cliente_nome: Optional[str]) -> uuid.UUID:
    if cliente_nome:
        cliente = db.query(Cliente).filter(Cliente.nome.ilike(f"%{cliente_nome}%")).first()
        if cliente:
            return cliente.id
    novo = Cliente(
        id=uuid.uuid4(),
        nome=cliente_nome or "Cliente IA",
        setor=SetorCliente.alimentos,
        cidade="indefinida",
        estado="SP",
    )
    db.add(novo)
    db.flush()
    return novo.id


def create_project_from_quotation(
    db: Session,
    usuario: Usuario,
    *,
    cliente_nome: str,
    valor_estimado: float = 0,
    texto_transcrito: str = "",
    json_proposta_ia: Optional[dict] = None,
    bom_json: Optional[list] = None,
    template_comissionamento: Optional[dict] = None,
    prazo: Optional[date] = None,
) -> dict[str, Any]:
    """Cria projeto, máquina, comissionamento, pendências e histórico em uma transação."""
    cliente_id = _resolve_cliente(db, cliente_nome)
    proj_id = f"PROJ-{str(uuid.uuid4())[:8].upper()}"
    maq_codigo = f"CLP-{str(uuid.uuid4())[:4].upper()}"

    escopo = json_proposta_ia or {}
    if isinstance(escopo, str):
        try:
            escopo = json.loads(escopo)
        except json.JSONDecodeError:
            escopo = {"texto": escopo}

    projeto = Projeto(
        id=proj_id,
        nome_contrato=cliente_nome or f"Projeto {proj_id}",
        id_vendedor=str(usuario.id),
        id_engenheiro=None,
        valor_contrato=valor_estimado or 0,
        status="AGUARDANDO_ENGENHARIA",
        prazo=prazo,
        dias_atraso=0,
        risco="BAIXO",
    )
    db.add(projeto)
    db.flush()

    maquina = Maquina(
        id=uuid.uuid4(),
        id_projeto=proj_id,
        codigo=maq_codigo,
        nome=f"Linha {proj_id}",
        modelo_clp=ModeloCLP.siemens_s7,
        protocolo=ProtocoloCLP.modbus_tcp,
        status=StatusMaquina.offline,
        cliente_id=cliente_id,
    )
    db.add(maquina)
    db.flush()

    comiss = Comissionamento(
        id=uuid.uuid4(),
        maquina_id=maquina.id,
        cliente_id=cliente_id,
        status=StatusComissionamento.aguardando_dados,
        fase_projeto=FaseProjeto.awaiting_engineering,
        engenheiro_responsavel="Engenharia AltaCLP",
        valor_contrato=valor_estimado or 0,
        checklist_json=template_comissionamento,
        bom_json=bom_json,
        resumo_cotacao={"transcricao": texto_transcrito, "proposta_ia": escopo},
        escopo_tecnico_detalhado=escopo,
        id_vendedor=usuario.id,
    )
    db.add(comiss)
    db.flush()

    etapas = []
    if template_comissionamento and isinstance(template_comissionamento, dict):
        etapas = template_comissionamento.get("etapas", [])
    
    if not etapas:
        etapas = DEFAULT_PENDENCIAS

    for ordem, titulo in enumerate(etapas, start=1):
        db.add(
            ProjetoPendencia(
                id=uuid.uuid4(),
                comissionamento_id=comiss.id,
                id_projeto=proj_id,
                titulo=titulo,
                ordem=ordem,
                concluida=False,
                status_tarefa=StatusTarefaPendencia.pendente,
                fase="aguardando_dados",
            )
        )

    db.add(
        ProjetoHistorico(
            id=uuid.uuid4(),
            comissionamento_id=comiss.id,
            acao_realizada="PROJECT_CREATED",
            id_usuario=str(usuario.id),
            data_hora=datetime.utcnow(),
        )
    )
    db.flush()

    saved = db.query(Projeto).filter(Projeto.id == proj_id).first()
    if not saved:
        raise RuntimeError("Database write failed — project not found after insert")

    return {
        "id": saved.id,
        "id_projeto": saved.id,
        "nome_contrato": saved.nome_contrato,
        "id_vendedor": saved.id_vendedor,
        "status": saved.status,
        "valor_contrato": float(saved.valor_contrato) if saved.valor_contrato else 0,
        "prazo": saved.prazo.isoformat() if saved.prazo else None,
        "dias_atraso": saved.dias_atraso,
        "risco": saved.risco,
        "comissionamento_id": str(comiss.id),
        "maquina_codigo": maq_codigo,
        "cliente_nome": cliente_nome,
    }
