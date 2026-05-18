"""
AltaCLP Intelligence Platform — Gerador de BOM (Bill of Materials)
Extrai parâmetros técnicos de transcrições de áudio e gera BOM + template.
Usa Anthropic API quando disponível, fallback para extração heurística.
"""

import os
import json
import time
from datetime import datetime


# Catálogo de componentes padrão AltaCLP para geração de BOM
CATALOGO_COMPONENTES = [
    {"codigo": "CLP-AB-L5K", "descricao": "CLP Allen-Bradley CompactLogix L5K", "valor_unit": 12500.00, "categoria": "clp"},
    {"codigo": "CLP-S7-1500", "descricao": "CLP Siemens S7-1500", "valor_unit": 14200.00, "categoria": "clp"},
    {"codigo": "CLP-SCH-M241", "descricao": "CLP Schneider Modicon M241", "valor_unit": 8900.00, "categoria": "clp"},
    {"codigo": "CLP-WEG-TPW04", "descricao": "CLP WEG TPW-04", "valor_unit": 6500.00, "categoria": "clp"},
    {"codigo": "SEN-TEMP-PT100", "descricao": "Sensor temperatura PT100 industrial -50~400°C", "valor_unit": 450.00, "categoria": "sensor"},
    {"codigo": "SEN-PRESS-4-20", "descricao": "Transmissor pressão 4-20mA 0-10 bar", "valor_unit": 1200.00, "categoria": "sensor"},
    {"codigo": "SEN-VIB-ICP", "descricao": "Acelerômetro ICP vibração industrial", "valor_unit": 2800.00, "categoria": "sensor"},
    {"codigo": "SEN-CORR-TC", "descricao": "Transformador de corrente TC split-core", "valor_unit": 380.00, "categoria": "sensor"},
    {"codigo": "MOD-MODBUS-ETH", "descricao": "Módulo comunicação Modbus TCP/Ethernet", "valor_unit": 1800.00, "categoria": "comunicacao"},
    {"codigo": "MOD-OPCUA-GW", "descricao": "Gateway OPC UA Industrial", "valor_unit": 3500.00, "categoria": "comunicacao"},
    {"codigo": "IHM-7POL", "descricao": "IHM 7 polegadas touchscreen industrial", "valor_unit": 4200.00, "categoria": "ihm"},
    {"codigo": "INV-FREQ-15KW", "descricao": "Inversor de frequência 15kW 380V", "valor_unit": 5800.00, "categoria": "acionamento"},
    {"codigo": "INV-FREQ-30KW", "descricao": "Inversor de frequência 30kW 380V", "valor_unit": 9200.00, "categoria": "acionamento"},
    {"codigo": "PAI-CMD-24P", "descricao": "Painel de comando 24 pontos IP65", "valor_unit": 7500.00, "categoria": "painel"},
    {"codigo": "CAB-IND-100M", "descricao": "Cabo industrial blindado 100m", "valor_unit": 1200.00, "categoria": "infraestrutura"},
    {"codigo": "FONT-24VDC", "descricao": "Fonte alimentação 24VDC 10A industrial", "valor_unit": 650.00, "categoria": "alimentacao"},
    {"codigo": "REL-SEG-NR12", "descricao": "Relé de segurança NR-12 Cat.4", "valor_unit": 1400.00, "categoria": "seguranca"},
    {"codigo": "SW-IND-8P", "descricao": "Switch industrial 8 portas Ethernet", "valor_unit": 2200.00, "categoria": "rede"},
]


async def gerar_bom_da_transcricao(transcricao: str, vendedor: str, cliente_nome: str = None) -> dict:
    """
    Processa transcrição de áudio do vendedor e gera BOM + template de comissionamento.
    Tenta usar Anthropic API. Se não disponível, usa extração heurística local.
    """
    inicio = time.time()

    api_key = os.getenv("ANTHROPIC_API_KEY", "")

    if api_key and api_key.startswith("sk-ant-"):
        resultado = await _gerar_com_ia(transcricao, vendedor, cliente_nome, api_key)
    else:
        resultado = _gerar_heuristico(transcricao, vendedor, cliente_nome)

    resultado["tempo_processamento_segundos"] = round(time.time() - inicio, 2)
    return resultado


async def _gerar_com_ia(transcricao: str, vendedor: str, cliente_nome: str, api_key: str) -> dict:
    """
    Usa Anthropic API para extrair parâmetros e gerar BOM inteligente.
    """
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)

        system_prompt = """Você é um engenheiro sênior de automação industrial com 15 anos de experiência
em CLPs (Allen-Bradley, Siemens S7, Schneider, WEG), protocolos industriais
(Modbus, OPC UA, Profibus), sensores industriais e painéis de controle.

Você vai receber a transcrição de um áudio de um vendedor descrevendo a planta
de um cliente industrial brasileiro. Extraia TODOS os parâmetros técnicos e gere:

1. Lista de parâmetros extraídos (estruturado)
2. Bill of Materials (BOM) com: codigo do item, descricao técnica, quantidade,
   unidade de medida, valor unitário estimado em R$
3. Template de comissionamento com: etapas ordenadas, dias estimados por etapa,
   riscos identificados, requisitos de certificação (ANVISA, NR-12, ATEX, etc.)

Responda APENAS em JSON válido, sem markdown. Use esta estrutura:
{
  "parametros_extraidos": {
    "tipo_equipamento": "string",
    "potencia_kw": 0.0,
    "tensao": "string",
    "protocolo": "string",
    "setor": "string",
    "certificacoes": ["string"],
    "outros": {}
  },
  "bom": [
    {"codigo": "string", "descricao": "string", "quantidade": 1, "unidade": "pç", "valor_unit": 0.0}
  ],
  "template_comissionamento": {
    "etapas": ["string"],
    "dias_estimados": 0,
    "engenheiro_sugerido": "string",
    "riscos": ["string"]
  }
}"""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": f"Vendedor: {vendedor}\nCliente: {cliente_nome or 'Não informado'}\n\nTranscrição do áudio:\n{transcricao}"
                }
            ]
        )

        response_text = message.content[0].text
        resultado = json.loads(response_text)
        return resultado

    except json.JSONDecodeError:
        # Se a IA retornar JSON inválido, usa fallback heurístico
        return _gerar_heuristico(transcricao, vendedor, cliente_nome)
    except Exception as e:
        print(f"[BOM] Erro na API Anthropic: {e}. Usando fallback heurístico.")
        return _gerar_heuristico(transcricao, vendedor, cliente_nome)


def _gerar_heuristico(transcricao: str, vendedor: str, cliente_nome: str = None) -> dict:
    """
    Extração heurística local — funciona sem API key.
    Usa keywords na transcrição para montar BOM básica.
    """
    texto = transcricao.lower()

    # Detecção de tipo de equipamento
    tipo_equip = "Não identificado"
    if any(w in texto for w in ["extrusora", "extrusão"]):
        tipo_equip = "Extrusora Industrial"
    elif any(w in texto for w in ["misturador", "tanque", "reator"]):
        tipo_equip = "Tanque Misturador/Reator"
    elif any(w in texto for w in ["dosador", "dosagem", "envase"]):
        tipo_equip = "Sistema de Dosagem/Envase"
    elif any(w in texto for w in ["prensa", "estampa"]):
        tipo_equip = "Prensa Industrial"
    elif any(w in texto for w in ["esteira", "transportador", "conveyor"]):
        tipo_equip = "Transportador/Esteira"
    elif any(w in texto for w in ["caldeira", "boiler"]):
        tipo_equip = "Caldeira Industrial"

    # Detecção de potência
    potencia = 15.0  # default
    import re
    pot_match = re.search(r'(\d+)\s*(kw|kilowatt|cv|hp)', texto)
    if pot_match:
        potencia = float(pot_match.group(1))
        if 'cv' in pot_match.group(2) or 'hp' in pot_match.group(2):
            potencia *= 0.7355  # CV para kW

    # Detecção de tensão
    tensao = "380V trifásico"
    if "220" in texto:
        tensao = "220V"
    elif "440" in texto:
        tensao = "440V trifásico"

    # Detecção de protocolo
    protocolo = "Modbus TCP"
    if "opc" in texto or "ua" in texto:
        protocolo = "OPC UA"
    elif "profibus" in texto:
        protocolo = "Profibus DP"

    # Detecção de setor
    setor = "industrial"
    if any(w in texto for w in ["aliment", "comida", "food"]):
        setor = "alimentos"
    elif any(w in texto for w in ["farmac", "pharma", "medicamento", "gxp"]):
        setor = "farmacêutico"
    elif any(w in texto for w in ["cosmét", "beleza"]):
        setor = "cosméticos"
    elif any(w in texto for w in ["químic", "react"]):
        setor = "químico"
    elif any(w in texto for w in ["automotiv", "autopeç"]):
        setor = "automotivo"

    # Certificações
    certificacoes = []
    if "nr-12" in texto or "nr12" in texto or "segurança" in texto:
        certificacoes.append("NR-12")
    if "anvisa" in texto or "gxp" in texto or "farmac" in texto:
        certificacoes.append("ANVISA/GxP")
    if "atex" in texto or "explos" in texto:
        certificacoes.append("ATEX")
    if not certificacoes:
        certificacoes.append("NR-12")  # Mínimo obrigatório

    # Monta BOM baseada no tipo de equipamento
    bom = []
    # CLP — escolhe baseado na complexidade
    if potencia > 20:
        bom.append({"codigo": "CLP-AB-L5K", "descricao": "CLP Allen-Bradley CompactLogix L5K", "quantidade": 1, "unidade": "pç", "valor_unit": 12500.00})
    else:
        bom.append({"codigo": "CLP-WEG-TPW04", "descricao": "CLP WEG TPW-04", "quantidade": 1, "unidade": "pç", "valor_unit": 6500.00})

    # Sensores padrão
    bom.append({"codigo": "SEN-TEMP-PT100", "descricao": "Sensor temperatura PT100 industrial -50~400°C", "quantidade": 4, "unidade": "pç", "valor_unit": 450.00})
    bom.append({"codigo": "SEN-PRESS-4-20", "descricao": "Transmissor pressão 4-20mA 0-10 bar", "quantidade": 2, "unidade": "pç", "valor_unit": 1200.00})
    bom.append({"codigo": "SEN-VIB-ICP", "descricao": "Acelerômetro ICP vibração industrial", "quantidade": 2, "unidade": "pç", "valor_unit": 2800.00})
    bom.append({"codigo": "SEN-CORR-TC", "descricao": "Transformador de corrente TC split-core", "quantidade": 3, "unidade": "pç", "valor_unit": 380.00})

    # Comunicação
    if protocolo == "OPC UA":
        bom.append({"codigo": "MOD-OPCUA-GW", "descricao": "Gateway OPC UA Industrial", "quantidade": 1, "unidade": "pç", "valor_unit": 3500.00})
    else:
        bom.append({"codigo": "MOD-MODBUS-ETH", "descricao": "Módulo comunicação Modbus TCP/Ethernet", "quantidade": 1, "unidade": "pç", "valor_unit": 1800.00})

    # Infraestrutura comum
    bom.append({"codigo": "IHM-7POL", "descricao": "IHM 7 polegadas touchscreen industrial", "quantidade": 1, "unidade": "pç", "valor_unit": 4200.00})
    bom.append({"codigo": "PAI-CMD-24P", "descricao": "Painel de comando 24 pontos IP65", "quantidade": 1, "unidade": "pç", "valor_unit": 7500.00})
    bom.append({"codigo": "FONT-24VDC", "descricao": "Fonte alimentação 24VDC 10A industrial", "quantidade": 2, "unidade": "pç", "valor_unit": 650.00})
    bom.append({"codigo": "CAB-IND-100M", "descricao": "Cabo industrial blindado 100m", "quantidade": 1, "unidade": "rolo", "valor_unit": 1200.00})
    bom.append({"codigo": "SW-IND-8P", "descricao": "Switch industrial 8 portas Ethernet", "quantidade": 1, "unidade": "pç", "valor_unit": 2200.00})

    if "NR-12" in certificacoes:
        bom.append({"codigo": "REL-SEG-NR12", "descricao": "Relé de segurança NR-12 Cat.4", "quantidade": 2, "unidade": "pç", "valor_unit": 1400.00})

    # Inversor se há motor
    if potencia > 10:
        inv = "INV-FREQ-30KW" if potencia > 20 else "INV-FREQ-15KW"
        inv_item = [c for c in CATALOGO_COMPONENTES if c["codigo"] == inv][0]
        bom.append({"codigo": inv, "descricao": inv_item["descricao"], "quantidade": 1, "unidade": "pç", "valor_unit": inv_item["valor_unit"]})

    # Template comissionamento
    dias_base = 6
    if setor == "farmacêutico":
        dias_base = 13  # GxP requer validação extra
    elif setor == "químico":
        dias_base = 8

    template = {
        "etapas": [
            "1. Inspeção física do painel e cabeamento",
            "2. Verificação de alimentação elétrica",
            "3. Download do programa no CLP",
            "4. Teste de I/O (entradas e saídas) ponto a ponto",
            "5. Configuração de comunicação (Modbus/OPC UA)",
            "6. Calibração de sensores em campo",
            "7. Teste funcional em modo manual",
            "8. Teste funcional em modo automático",
            "9. Ajuste de parâmetros e setpoints",
            "10. Treinamento do operador",
            "11. Documentação e entrega final",
        ],
        "dias_estimados": dias_base,
        "engenheiro_sugerido": "Cláudia Santarém" if setor == "farmacêutico" else "A definir",
        "riscos": [
            "Atraso por incompatibilidade de protocolo",
            "Calibração de sensores fora de especificação",
            f"{'Validação GxP pode estender prazo em 5+ dias' if setor == 'farmacêutico' else 'Intempéries climáticas'}",
            "Necessidade de treinamento adicional para operadores",
        ]
    }

    if setor == "farmacêutico":
        template["etapas"].insert(8, "8.1. Protocolo de validação IQ/OQ/PQ (ANVISA)")
        template["etapas"].append("12. Emissão de certificado de validação GxP")

    return {
        "parametros_extraidos": {
            "tipo_equipamento": tipo_equip,
            "potencia_kw": potencia,
            "tensao": tensao,
            "protocolo": protocolo,
            "setor": setor,
            "certificacoes": certificacoes,
            "outros": {
                "vendedor": vendedor,
                "cliente": cliente_nome,
                "metodo_extracao": "heurístico (sem API key)",
            }
        },
        "bom": bom,
        "template_comissionamento": template,
    }
