import sys
import os
import asyncio

sys.path.insert(0, '.')

from database.connection import SessionLocal
from database.models import (
    Usuario, PerfilUsuario, CotacaoDraft, Comissionamento, 
    Projeto, StatusComissionamento, FaseProjeto, Cliente
)
from routers.quotations import create_draft, approve_draft
from routers.projects import submit_validation
from pydantic import BaseModel

class MockDraftCreateRequest:
    def __init__(self, texto_transcrito, cliente_nome="", valor_estimado=0, audio_raw_url=None):
        self.texto_transcrito = texto_transcrito
        self.cliente_nome = cliente_nome
        self.valor_estimado = valor_estimado
        self.audio_raw_url = audio_raw_url
        self.json_proposta_ia = None

    def model_dump(self):
        return {
            "texto_transcrito": self.texto_transcrito,
            "cliente_nome": self.cliente_nome,
            "valor_estimado": self.valor_estimado,
            "audio_raw_url": self.audio_raw_url,
            "json_proposta_ia": self.json_proposta_ia
        }

async def run_test():
    print("=== STARTING BACKEND INTEGRATION TEST ===")
    db = SessionLocal()
    
    # 1. Get or create a seller user
    vendedor = db.query(Usuario).filter(Usuario.perfil == PerfilUsuario.vendedor).first()
    if not vendedor:
        vendedor = Usuario(
            nome="Vendedor Teste",
            email="vendedor@altaclp.com.br",
            senha_hash="dummy",
            perfil=PerfilUsuario.vendedor,
            ativo=True
        )
        db.add(vendedor)
        db.commit()
        db.refresh(vendedor)
    print(f"Using seller: {vendedor.nome} ({vendedor.id})")

    # 2. Simulate POST /quotations/draft with immediate AI analysis
    body = MockDraftCreateRequest(
        texto_transcrito="Estou na planta da Nestlé, é uma prensa industrial de 25kW trifásica 380V. Precisa de sensor de temperatura PT100, transmissor de pressão e relé de segurança NR-12.",
        cliente_nome="Nestlé SA",
        valor_estimado=0
    )
    
    print("\n--- 1. Creating Draft (Immediate AI analysis) ---")
    draft_response = await create_draft(body, db, vendedor)
    print("Draft response:")
    print(f"  ID: {draft_response['id_cotacao']}")
    print(f"  Cliente: {draft_response['cliente_nome']}")
    print(f"  Valor Estimado: {draft_response['valor_estimado']}")
    print(f"  JSON Proposta IA keys: {list(draft_response['json_proposta_ia'].keys())}")
    
    assert draft_response['valor_estimado'] > 0, "Valor estimado should be calculated from BOM!"
    assert len(draft_response['json_proposta_ia'].get('bom', [])) > 0, "BOM should be generated!"
    assert len(draft_response['json_proposta_ia'].get('template_comissionamento', {}).get('etapas', [])) > 0, "Checklist should be generated!"

    draft_id = draft_response['id_cotacao']

    # 3. Simulate POST /quotations/{draft_id}/approve
    print("\n--- 2. Approving Draft ---")
    project_response = await approve_draft(draft_id, None, db, vendedor)
    proj_id = project_response['id_projeto']
    comiss_id = project_response['comissionamento_id']
    print("Project response:")
    print(f"  Projeto ID: {proj_id}")
    print(f"  Comissionamento ID: {comiss_id}")

    # 4. Verify in DB that Comissionamento has checklist and BOM
    import uuid as uuid_pkg
    db.expire_all()
    comiss = db.query(Comissionamento).filter(Comissionamento.id == uuid_pkg.UUID(comiss_id)).first()
    assert comiss is not None
    assert comiss.bom_json is not None, "BOM should be persisted in Comissionamento!"
    assert comiss.checklist_json is not None, "Checklist should be persisted in Comissionamento!"
    print("\n[SUCCESS] BOM and Checklist persisted in SQLite!")
    print(f"  BOM items in DB: {len(comiss.bom_json)}")
    print(f"  Checklist items in DB: {len(comiss.checklist_json.get('etapas', []))}")
    print(f"  Comissionamento initial status: {comiss.status.value}")
    print(f"  Comissionamento initial phase: {comiss.fase_projeto.value}")

    # 5. Get or create an engineer user
    engineer = db.query(Usuario).filter(Usuario.perfil == PerfilUsuario.engenharia).first()
    if not engineer:
        engineer = Usuario(
            nome="Engenheiro Teste",
            email="engenharia@altaclp.com.br",
            senha_hash="dummy",
            perfil=PerfilUsuario.engenharia,
            ativo=True
        )
        db.add(engineer)
        db.commit()
        db.refresh(engineer)
    print(f"Using engineer: {engineer.nome} ({engineer.id})")

    # 6. Stage 1 -> Stage 2: aguardando_dados -> em_andamento
    print("\n--- 3. Stage 1 -> 2: Approving Documentation (Awaiting Data -> In Progress) ---")
    submit_response_1 = await submit_validation(proj_id, db, vendedor)
    db.refresh(comiss)
    print(f"  Comissionamento status: {comiss.status.value}")
    assert comiss.status == StatusComissionamento.em_andamento, "Status should be em_andamento!"
    print("[SUCCESS] Bypassed checklist and transitioned to In Progress!")

    # 7. Stage 2 -> Stage 3 (attempt with incomplete tasks should fail)
    print("\n--- 4. Stage 2 -> 3: Attempt Handover with Incomplete Tasks (Should Fail) ---")
    from fastapi import HTTPException
    try:
        await submit_validation(proj_id, db, vendedor)
        assert False, "Should have failed with incomplete tasks!"
    except HTTPException as e:
        assert e.status_code == 400
        print(f"[SUCCESS] Handover blocked as expected: {e.detail}")

    # 8. Complete all tasks and submit Stage 2 -> Stage 3
    print("\n--- 5. Stage 2 -> 3: Complete Tasks and Submit Handover ---")
    from database.models import ProjetoPendencia
    db.query(ProjetoPendencia).filter(ProjetoPendencia.id_projeto == proj_id).update({"concluida": True})
    db.commit()
    submit_response_2 = await submit_validation(proj_id, db, vendedor)
    db.refresh(comiss)
    print(f"  Comissionamento status: {comiss.status.value}")
    print(f"  Comissionamento phase: {comiss.fase_projeto.value}")
    assert comiss.status == StatusComissionamento.fat_pendente, "Status should be fat_pendente!"
    assert comiss.fase_projeto == FaseProjeto.post_sale, "Phase should be post_sale!"
    print("[SUCCESS] Transitioned to Pending Invoice!")

    # 9. Stage 3 -> Stage 4 (attempt with non-engineer seller should fail)
    print("\n--- 6. Stage 3 -> 4: Attempt Invoice Approval by Seller (Should Fail) ---")
    try:
        await submit_validation(proj_id, db, vendedor)
        assert False, "Should have failed with non-engineer user!"
    except HTTPException as e:
        assert e.status_code == 403
        print(f"[SUCCESS] Invoice approval blocked as expected: {e.detail}")

    # 10. Approve Stage 3 -> Stage 4 with Engineer user
    print("\n--- 7. Stage 3 -> 4: Approve Invoice by Engineer ---")
    submit_response_3 = await submit_validation(proj_id, db, engineer)
    db.refresh(comiss)
    print(f"  Comissionamento final status: {comiss.status.value}")
    assert comiss.status == StatusComissionamento.treinamento_operador, "Status should be treinamento_operador!"
    print("[SUCCESS] Approved and transitioned to Training Stage!")

    # Cleanup test data so we don't pollute the db
    print("\n--- 4. Cleaning Up Test Data ---")
    from database.models import Maquina, ProjetoPendencia, ProjetoHistorico
    db.query(ProjetoPendencia).filter(ProjetoPendencia.id_projeto == proj_id).delete()
    db.query(ProjetoHistorico).filter(ProjetoHistorico.comissionamento_id == comiss.id).delete()
    db.query(Comissionamento).filter(Comissionamento.id == comiss.id).delete()
    db.query(Maquina).filter(Maquina.id_projeto == proj_id).delete()
    db.query(Projeto).filter(Projeto.id == proj_id).delete()
    db.query(CotacaoDraft).filter(CotacaoDraft.id_cotacao == uuid_pkg.UUID(draft_id)).delete()
    db.commit()
    print("Cleanup completed.")
    
    db.close()
    print("\n=== ALL TESTS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    asyncio.run(run_test())
