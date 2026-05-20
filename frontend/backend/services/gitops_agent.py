"""
AltaCLP Intelligence Platform — Agente GitOps
Verificação de hash (código campo vs Git) + geração de diffs simulados
para auditoria de código Structured Text nos CLPs.
"""

import uuid
import hashlib
from datetime import datetime
from sqlalchemy.orm import Session

from database.models import Maquina, GitOpsAuditoria, AcaoGitOps


# Diffs simulados realistas de código Structured Text para CLPs com drift
DIFFS_SIMULADOS = {
    "CLP-007": {
        "tecnico": "Anderson Vasconcellos",
        "resumo": "Alteração no setpoint de temperatura linha 3 sem documentação",
        "linhas": 3,
        "detalhe": """--- a/PLC_PRG/Temperature_Control_L3.st
+++ b/PLC_PRG/Temperature_Control_L3.st
@@ -45,7 +45,9 @@
 (* Bloco de controle de temperatura - Linha 3 Extrusão *)
 IF bEnable_TempControl THEN
-    (* Original setpoint temperatura linha 3 *)
-    IF rTemperature_PV > 78.5 THEN
+    (* Hotfix Anderson 22/04 - setpoint ajustado em campo *)
+    (* ATENÇÃO: não documentado no Git *)
+    IF rTemperature_PV > 82.0 THEN
         bAlarm_HighTemp := TRUE;
         rOutput_Cooling := 100.0;
     ELSIF rTemperature_PV < 65.0 THEN
""",
    },
    "CLP-019": {
        "tecnico": "Anderson Vasconcellos",
        "resumo": "Hotfix emergencial válvula VH-221 — não documentado no Git",
        "linhas": 7,
        "detalhe": """--- a/PLC_PRG/Valve_Control_VH221.st
+++ b/PLC_PRG/Valve_Control_VH221.st
@@ -12,10 +12,17 @@
 (* Controle válvula proporcional VH-221 *)
 (* Belmare Cosméticos - Tanque misturador principal *)
-rValve_Setpoint := rFlow_Demand * 0.85;
-IF rPressure_Inlet > 4.2 THEN
-    rValve_Setpoint := rValve_Setpoint * 0.7;
-END_IF;
+
+(* HOTFIX Anderson 14/03 - EMERGENCIAL *)
+(* Válvula travava em 100% quando pressão > 4.2 bar *)
+(* Causa raiz: coeficiente de 0.85 muito alto para nova bomba *)
+rValve_Setpoint := rFlow_Demand * 0.62;  (* era 0.85 *)
+IF rPressure_Inlet > 3.8 THEN           (* era 4.2 *)
+    rValve_Setpoint := rValve_Setpoint * 0.5;  (* era 0.7 *)
+    bAlarm_HighPressure := TRUE;
+END_IF;
+
+(* TODO: remover este hotfix após revisão eng — Anderson *)

 rValve_Output := LIMIT(0.0, rValve_Setpoint, 100.0);
""",
    },
    "CLP-034": {
        "tecnico": "Júnior Almeida",
        "resumo": "Ajuste dosagem sem aprovação GxP — risco de multa ANVISA",
        "linhas": 2,
        "detalhe": """--- a/PLC_PRG/Dosing_Control_Pharma.st
+++ b/PLC_PRG/Dosing_Control_Pharma.st
@@ -78,7 +78,7 @@
 (* Controle de dosagem - Pampulha Pharma *)
 (* ATENÇÃO: Parâmetro validado GxP - NÃO ALTERAR SEM APROVAÇÃO *)
-rDosing_Volume := 12.50;   (* Volume nominal em mL - validado ANVISA *)
-rDosing_Tolerance := 0.15; (* Tolerância ±0.15 mL *)
+rDosing_Volume := 12.80;   (* Ajustado Júnior 02/01 - bomba descalibrada *)
+rDosing_Tolerance := 0.25; (* Ampliado para compensar variação *)

 (* VALIDAÇÃO GxP: Referência Doc QA-2025-0087 Rev.3 *)
""",
    },
}


class GitOpsAgent:
    """
    Agente de auditoria GitOps.
    Verifica integridade do código nos CLPs (hash campo vs Git).
    Gera diffs simulados e sugere Pull Requests automáticos.
    """

    @staticmethod
    def verificar_hash(db: Session, maquina_id) -> dict:
        """
        Simula verificação de hash do CLP vs Git.
        Para CLPs com drift (codigo_sync=False): retorna hashes diferentes + diff.
        Para CLPs OK: retorna hashes iguais.
        """
        maquina = db.query(Maquina).filter(Maquina.id == maquina_id).first()
        if not maquina:
            return {"erro": "Máquina não encontrada"}

        # Verifica se este CLP tem drift simulado
        drift_info = DIFFS_SIMULADOS.get(maquina.codigo)

        if drift_info:
            # CLP com drift — hashes diferentes
            em_sync = False
            hash_campo = maquina.codigo_hash_campo or hashlib.sha256(
                f"campo-{maquina.codigo}-drift".encode()
            ).hexdigest()[:16]
            hash_git = maquina.codigo_hash_git or hashlib.sha256(
                f"git-{maquina.codigo}-official".encode()
            ).hexdigest()[:16]
        else:
            # CLP sincronizado — hashes iguais
            em_sync = True
            hash_valor = hashlib.sha256(
                f"{maquina.codigo}-{datetime.utcnow().date()}".encode()
            ).hexdigest()[:16]
            hash_campo = hash_valor
            hash_git = hash_valor

        # Registra auditoria no banco
        auditoria = GitOpsAuditoria(
            id=uuid.uuid4(),
            maquina_id=maquina_id,
            timestamp_verificacao=datetime.utcnow(),
            hash_campo=hash_campo,
            hash_git=hash_git,
            em_sync=em_sync,
            diff_linhas=drift_info["linhas"] if drift_info else 0,
            diff_resumo=drift_info["resumo"] if drift_info else None,
            diff_detalhe=drift_info["detalhe"] if drift_info else None,
            tecnico_suspeito=drift_info["tecnico"] if drift_info else None,
            pr_sugerido=not em_sync,
            acao_tomada=AcaoGitOps.alerta_enviado if not em_sync else AcaoGitOps.nenhuma,
        )

        try:
            db.add(auditoria)

            # Atualiza máquina
            maquina.codigo_hash_campo = hash_campo
            maquina.codigo_hash_git = hash_git
            maquina.codigo_sync = em_sync
            maquina.ultima_verificacao_gitops = datetime.utcnow()

            db.commit()
            db.refresh(auditoria)
        except Exception as e:
            db.rollback()
            return {"erro": f"Falha ao registrar auditoria: {str(e)}"}

        return {
            "auditoria_id": str(auditoria.id),
            "maquina_codigo": maquina.codigo,
            "em_sync": em_sync,
            "hash_campo": hash_campo,
            "hash_git": hash_git,
            "diff_linhas": auditoria.diff_linhas,
            "diff_resumo": auditoria.diff_resumo,
            "tecnico_suspeito": auditoria.tecnico_suspeito,
            "timestamp": auditoria.timestamp_verificacao.isoformat(),
        }

    @staticmethod
    def gerar_diff_simulado(maquina_codigo: str) -> dict:
        """
        Gera um diff realista de código Structured Text.
        Usado para exibição no dashboard de engenharia.
        """
        drift_info = DIFFS_SIMULADOS.get(maquina_codigo)

        if not drift_info:
            return {
                "maquina": maquina_codigo,
                "status": "em_sync",
                "mensagem": "Código do CLP está sincronizado com o repositório Git.",
            }

        return {
            "maquina": maquina_codigo,
            "status": "drift_detectado",
            "tecnico_suspeito": drift_info["tecnico"],
            "resumo": drift_info["resumo"],
            "linhas_alteradas": drift_info["linhas"],
            "diff": drift_info["detalhe"],
        }

    @staticmethod
    def sugerir_pr(db: Session, auditoria_id) -> dict:
        """
        Gera texto de Pull Request automático com o diff encontrado.
        Inclui: título, descrição, arquivos modificados, revisor sugerido.
        """
        auditoria = db.query(GitOpsAuditoria).filter(
            GitOpsAuditoria.id == auditoria_id
        ).first()

        if not auditoria:
            return {"erro": "Auditoria não encontrada"}

        if auditoria.em_sync:
            return {"erro": "Código está sincronizado — PR não necessário"}

        maquina = db.query(Maquina).filter(
            Maquina.id == auditoria.maquina_id
        ).first()

        pr_numero = f"PR-{datetime.utcnow().strftime('%Y%m%d')}-{str(auditoria.id)[:8]}"
        pr_url = f"https://github.com/altaclp/plc-programs/pull/{pr_numero}"

        pr = {
            "numero": pr_numero,
            "titulo": f"[HOTFIX] {maquina.codigo}: {auditoria.diff_resumo}",
            "descricao": f"""## Hotfix detectado em campo — Revisão necessária

**CLP:** {maquina.codigo} — {maquina.nome}
**Técnico responsável:** {auditoria.tecnico_suspeito or 'Não identificado'}
**Data do hotfix:** {auditoria.timestamp_verificacao.strftime('%d/%m/%Y %H:%M')}
**Linhas alteradas:** {auditoria.diff_linhas}

### Resumo
{auditoria.diff_resumo}

### Diff
```st
{auditoria.diff_detalhe or 'Diff não disponível'}
```

### Ação necessária
- [ ] Revisar alterações com engenharia
- [ ] Validar contra especificação do cliente
- [ ] Aprovar ou reverter no CLP
- [ ] Atualizar documentação
""",
            "arquivos_modificados": [
                f"PLC_PRG/{maquina.codigo}_control.st"
            ],
            "revisor_sugerido": "Cláudia Santarém (Eng. Coordenadora)",
            "labels": ["hotfix", "campo", "revisão-urgente"],
            "url": pr_url,
        }

        # Atualiza auditoria com PR sugerido
        try:
            auditoria.pr_sugerido = True
            auditoria.pr_url = pr_url
            auditoria.acao_tomada = AcaoGitOps.pr_criado
            db.commit()
        except Exception:
            db.rollback()

        return pr
