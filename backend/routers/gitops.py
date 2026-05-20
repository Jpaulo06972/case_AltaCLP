"""
AltaCLP Intelligence Platform — Router GitOps
Auditoria de código campo vs Git + diffs + aprovação de PRs.
"""

import math
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from database.connection import get_db
from database.models import (
    GitOpsAuditoria, Maquina, Cliente, Incidente,
    AcaoGitOps, LogAuditoriaGit, AcaoAuditoriaGit,
)
from pydantic import BaseModel
import uuid as uuid_mod
from schemas.schemas import AprovarPRRequest
from services.gitops_agent import GitOpsAgent

router = APIRouter(prefix="/gitops", tags=["GitOps — Auditoria de Código"])


@router.get("/auditorias")
def listar_auditorias(
    em_sync: bool = None,
    cliente_id: UUID = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Lista auditorias GitOps com filtros."""
    query = db.query(GitOpsAuditoria, Maquina.codigo, Cliente.nome).join(
        Maquina, GitOpsAuditoria.maquina_id == Maquina.id
    ).join(
        Cliente, Maquina.cliente_id == Cliente.id
    )

    if em_sync is not None:
        query = query.filter(GitOpsAuditoria.em_sync == em_sync)
    if cliente_id:
        query = query.filter(Maquina.cliente_id == cliente_id)

    total = query.count()
    offset = (page - 1) * limit
    resultados = query.order_by(desc(GitOpsAuditoria.timestamp_verificacao)).offset(offset).limit(limit).all()

    dados = []
    for audit, maq_codigo, cli_nome in resultados:
        dados.append({
            "id": str(audit.id),
            "maquina_id": str(audit.maquina_id),
            "maquina_codigo": maq_codigo,
            "cliente_nome": cli_nome,
            "timestamp_verificacao": audit.timestamp_verificacao.isoformat() if audit.timestamp_verificacao else None,
            "hash_campo": audit.hash_campo,
            "hash_git": audit.hash_git,
            "em_sync": audit.em_sync,
            "diff_linhas": audit.diff_linhas,
            "diff_resumo": audit.diff_resumo,
            "tecnico_suspeito": audit.tecnico_suspeito,
            "pr_sugerido": audit.pr_sugerido,
            "pr_url": audit.pr_url,
            "acao_tomada": audit.acao_tomada.value if audit.acao_tomada else None,
            "aprovado_por": audit.aprovado_por,
        })

    return {
        "dados": dados,
        "total": total,
        "pagina": page,
        "por_pagina": limit,
        "paginas": math.ceil(total / limit) if limit > 0 else 0,
    }


@router.get("/drifts/ativos")
def drifts_ativos(db: Session = Depends(get_db)):
    """Lista CLPs com drift ativo (codigo_sync = False) + detalhes."""
    maquinas_drift = db.query(Maquina, Cliente.nome).join(
        Cliente, Maquina.cliente_id == Cliente.id
    ).filter(
        Maquina.codigo_sync == False
    ).all()

    drifts = []
    for maq, cli_nome in maquinas_drift:
        # Busca última auditoria desta máquina
        ultima_audit = db.query(GitOpsAuditoria).filter(
            GitOpsAuditoria.maquina_id == maq.id,
            GitOpsAuditoria.em_sync == False
        ).order_by(desc(GitOpsAuditoria.timestamp_verificacao)).first()

        # Gera diff simulado
        diff_info = GitOpsAgent.gerar_diff_simulado(maq.codigo)

        drifts.append({
            "maquina_id": str(maq.id),
            "maquina_codigo": maq.codigo,
            "maquina_nome": maq.nome,
            "cliente_nome": cli_nome,
            "hash_campo": maq.codigo_hash_campo,
            "hash_git": maq.codigo_hash_git,
            "ultima_verificacao": maq.ultima_verificacao_gitops.isoformat() if maq.ultima_verificacao_gitops else None,
            "diff": diff_info,
            "auditoria_id": str(ultima_audit.id) if ultima_audit else None,
            "tecnico_suspeito": ultima_audit.tecnico_suspeito if ultima_audit else None,
        })

    return {
        "total_drifts": len(drifts),
        "drifts": drifts,
    }


@router.get("/auditorias/{maquina_id}/historico")
def historico_auditoria(maquina_id: UUID, db: Session = Depends(get_db)):
    """Histórico de verificações GitOps da máquina."""
    maquina = db.query(Maquina).filter(Maquina.id == maquina_id).first()
    if not maquina:
        raise HTTPException(status_code=404, detail="Máquina não encontrada")

    auditorias = db.query(GitOpsAuditoria).filter(
        GitOpsAuditoria.maquina_id == maquina_id
    ).order_by(desc(GitOpsAuditoria.timestamp_verificacao)).limit(50).all()

    return {
        "maquina_codigo": maquina.codigo,
        "total": len(auditorias),
        "auditorias": [{
            "id": str(a.id),
            "timestamp": a.timestamp_verificacao.isoformat() if a.timestamp_verificacao else None,
            "em_sync": a.em_sync,
            "hash_campo": a.hash_campo,
            "hash_git": a.hash_git,
            "diff_linhas": a.diff_linhas,
            "diff_resumo": a.diff_resumo,
            "tecnico_suspeito": a.tecnico_suspeito,
            "acao_tomada": a.acao_tomada.value if a.acao_tomada else None,
        } for a in auditorias]
    }


@router.post("/verificar/{maquina_id}")
def verificar_maquina(maquina_id: UUID, db: Session = Depends(get_db)):
    """Simula nova verificação de hash para a máquina."""
    resultado = GitOpsAgent.verificar_hash(db, maquina_id)
    if "erro" in resultado:
        raise HTTPException(status_code=400, detail=resultado["erro"])
    return resultado


@router.post("/aprovar-pr/{auditoria_id}")
def aprovar_pr(
    auditoria_id: UUID,
    body: AprovarPRRequest,
    db: Session = Depends(get_db)
):
    """Aprova o PR sugerido e simula merge no repositório."""
    auditoria = db.query(GitOpsAuditoria).filter(
        GitOpsAuditoria.id == auditoria_id
    ).first()

    if not auditoria:
        raise HTTPException(status_code=404, detail="Auditoria não encontrada")

    try:
        auditoria.acao_tomada = AcaoGitOps.aprovado
        auditoria.aprovado_por = body.aprovado_por

        # Sincroniza a máquina (simula merge)
        maquina = db.query(Maquina).filter(Maquina.id == auditoria.maquina_id).first()
        if maquina:
            maquina.codigo_hash_git = auditoria.hash_campo  # Git agora tem o código do campo
            maquina.codigo_sync = True

        db.commit()
        
        # Opcional: Efetuar push real pro Github
        import os
        import requests
        import base64
        import time
        github_token = os.getenv("GITHUB_TOKEN")
        
        if github_token and maquina:
            try:
                headers = {"Authorization": f"token {github_token}", "Accept": "application/vnd.github.v3+json"}
                r_repos = requests.get("https://api.github.com/user/repos?sort=updated&per_page=1", headers=headers)
                if r_repos.status_code == 200 and r_repos.json():
                    repo_full_name = r_repos.json()[0]["full_name"]
                    
                    content = f"PR Aprovado: {body.comentario}\nDiff:\n{auditoria.diff_detalhe or auditoria.diff_resumo}\nMáquina: {maquina.codigo}"
                    encoded_content = base64.b64encode(content.encode()).decode()
                    
                    push_data = {
                        "message": f"Hotfix(GitOps): Merge aprovado por {body.aprovado_por} para {maquina.codigo}",
                        "content": encoded_content
                    }
                    filename = f"gitops_audits/audit_{maquina.codigo}_{int(time.time())}.txt"
                    push_url = f"https://api.github.com/repos/{repo_full_name}/contents/{filename}"
                    requests.put(push_url, headers=headers, json=push_data, timeout=5)
            except Exception as e:
                print(f"[GitOps] Erro Github flow: {e}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao aprovar: {str(e)}")

    return {
        "mensagem": f"PR aprovado por {body.aprovado_por}. Código sincronizado.",
        "auditoria_id": str(auditoria_id),
        "maquina_codigo": maquina.codigo if maquina else None,
        "em_sync": True,
        "comentario": body.comentario,
    }


@router.get("/estatisticas")
def estatisticas_gitops(db: Session = Depends(get_db)):
    """Estatísticas gerais do GitOps."""
    data_24h = datetime.utcnow() - timedelta(hours=24)

    total_24h = db.query(GitOpsAuditoria).filter(
        GitOpsAuditoria.timestamp_verificacao >= data_24h
    ).count()

    total_maquinas = db.query(Maquina).count()
    em_sync = db.query(Maquina).filter(Maquina.codigo_sync == True).count()
    em_sync_pct = (em_sync / total_maquinas * 100) if total_maquinas > 0 else 0

    drifts_ativos = db.query(Maquina).filter(Maquina.codigo_sync == False).count()

    # Prejuízo histórico por incidentes de drift
    from database.models import TipoIncidente
    prejuizo = db.query(func.sum(Incidente.prejuizo_estimado)).filter(
        Incidente.tipo == TipoIncidente.drift_codigo
    ).scalar() or 0

    return {
        "total_verificacoes_24h": total_24h,
        "em_sync_pct": round(em_sync_pct, 1),
        "drifts_ativos": drifts_ativos,
        "prejuizo_historico": float(prejuizo),
    }


import os
import requests

PROJETOS_GIT = [
    {"id_projeto": "plc-anaclara-l1", "nome": "Anaclara Extrusora L1", "repo": "altaclp/plc-anaclara"},
    {"id_projeto": "plc-belmare", "nome": "Belmare Dosagem", "repo": "altaclp/plc-belmare"},
    {"id_projeto": "plc-pampulha", "nome": "Pampulha Reator", "repo": "altaclp/plc-pampulha"},
]


@router.get("/projetos")
def listar_projetos_git(db: Session = Depends(get_db)):
    """Projetos disponíveis para técnicos (read) e engenheiros (merge)."""
    github_token = os.getenv("GITHUB_TOKEN")
    projetos = []
    
    if github_token:
        try:
            headers = {"Authorization": f"token {github_token}"}
            r = requests.get("https://api.github.com/user/repos?sort=updated&per_page=10", headers=headers, timeout=5)
            if r.status_code == 200:
                for repo in r.json():
                    projetos.append({
                        "id_projeto": repo["name"],
                        "nome": repo["full_name"],
                        "repo": repo["full_name"]
                    })
        except Exception as e:
            print(f"[GitOps] Erro ao buscar projetos GitHub: {e}")

    if not projetos:
        projetos = PROJETOS_GIT.copy()

    for p in projetos:
        busca = p['id_projeto'].split('-')[-1] if '-' in p['id_projeto'] else p['id_projeto']
        drifts = db.query(GitOpsAuditoria).join(Maquina).filter(
            Maquina.codigo.ilike(f"%{busca}%"),
            GitOpsAuditoria.em_sync == False,
        ).count()
        p["prs_pendentes"] = drifts
    return {"projetos": projetos}


@router.get("/auditoria-log")
def log_auditoria(
    id_projeto: str = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    q = db.query(LogAuditoriaGit).order_by(desc(LogAuditoriaGit.timestamp))
    if id_projeto:
        q = q.filter(LogAuditoriaGit.id_projeto == id_projeto)
    logs = q.limit(limit).all()
    return {
        "timeline": [
            {
                "id": str(l.id),
                "id_projeto": l.id_projeto,
                "acao": l.acao.value if l.acao else None,
                "id_usuario": l.id_usuario,
                "diff_resumo": l.diff_resumo,
                "risco_ia": l.risco_ia,
                "timestamp": l.timestamp.isoformat() if l.timestamp else None,
            }
            for l in logs
        ]
    }


@router.get("/review-ia/{auditoria_id}")
async def review_ia_pr(auditoria_id: UUID, db: Session = Depends(get_db)):
    """Análise estática IA do PR (resumo + riscos) via Groq."""
    audit = db.query(GitOpsAuditoria).filter(GitOpsAuditoria.id == auditoria_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Auditoria não encontrada")
        
    diff = audit.diff_detalhe or audit.diff_resumo or "Sem detalhes de diff."
    
    risco_default = (
        "ALTO: alteração em bloco de segurança (E-Stop) sem revisão cruzada. Verificar intertravamento."
        if audit.diff_linhas and audit.diff_linhas > 5
        else "MÉDIO: ajustes de setpoint dentro do esperado para comissionamento."
    )
    resumo_default = audit.diff_resumo or "Alterações em lógica de sequência e timers de ciclo."
    recomendacao_default = "Aprovar com teste FAT documentado" if "MÉDIO" in risco_default else "Rejeitar até correção"

    from services.groq_client import get_groq_client, DEFAULT_TEXT_MODEL
    client = get_groq_client()
    
    if client:
        try:
            prompt = f"""Você é um especialista em automação industrial e PLC (Structured Text).
Avalie este diff de código e responda ESTRITAMENTE em formato JSON com as chaves:
"resumo": "Um parágrafo curto e direto explicando as modificações",
"risco": "Nível de risco (ALTO, MÉDIO, BAIXO) e o motivo curto focado em segurança e impacto",
"recomendacao": "Recomendação curta (Aprovar, Rejeitar, Testar, etc)"

Diff:
{diff}
"""
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=DEFAULT_TEXT_MODEL,
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            import json
            resp = json.loads(chat_completion.choices[0].message.content)
            return {
                "auditoria_id": str(auditoria_id),
                "resumo_mudancas": resp.get("resumo", resumo_default),
                "riscos": resp.get("risco", risco_default),
                "recomendacao": resp.get("recomendacao", recomendacao_default),
            }
        except Exception as e:
            print(f"[GitOps] Erro na IA: {e}")

    return {
        "auditoria_id": str(auditoria_id),
        "resumo_mudancas": resumo_default,
        "riscos": risco_default,
        "recomendacao": recomendacao_default,
    }


class RejectPRRequest(BaseModel):
    motivo: str
    rejeitado_por: str


@router.post("/rejeitar-pr/{auditoria_id}")
def rejeitar_pr(
    auditoria_id: UUID,
    body: RejectPRRequest,
    db: Session = Depends(get_db),
):
    audit = db.query(GitOpsAuditoria).filter(GitOpsAuditoria.id == auditoria_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Auditoria não encontrada")
    maq = db.query(Maquina).filter(Maquina.id == audit.maquina_id).first()
    db.add(LogAuditoriaGit(
        id=uuid_mod.uuid4(),
        id_projeto=maq.codigo if maq else "unknown",
        acao=AcaoAuditoriaGit.reject,
        id_usuario=body.rejeitado_por,
        diff_resumo=body.motivo,
        risco_ia="PR rejeitado pelo engenheiro",
    ))
    db.commit()
    return {"mensagem": "PR rejeitado", "motivo": body.motivo}
