"""
AltaCLP Intelligence Platform — Gerador de BOM (Bill of Materials)
Extrai parâmetros técnicos de transcrições de áudio e gera BOM + template.
Usa Groq API quando disponível, fallback para extração heurística.
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

    from services.groq_client import get_groq_client
    client = get_groq_client()

    if client:
        resultado = await _gerar_com_ia(transcricao, vendedor, cliente_nome, client)
    else:
        resultado = _gerar_heuristico(transcricao, vendedor, cliente_nome)

    # Make sure cliente_nome is resolved and set
    resolved_cliente = cliente_nome
    if not resolved_cliente and resultado.get("parametros_extraidos"):
        resolved_cliente = resultado["parametros_extraidos"].get("outros", {}).get("cliente", "")
    
    resultado["cliente_nome"] = resolved_cliente or "Cliente Geral"
    resultado["tempo_processamento_segundos"] = round(time.time() - inicio, 2)
    return resultado


async def _gerar_com_ia(transcricao: str, vendedor: str, cliente_nome: str, client) -> dict:
    """
    Usa Groq API para extrair parâmetros e gerar BOM inteligente.
    """
    try:
        from services.groq_client import DEFAULT_TEXT_MODEL

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

        message = client.chat.completions.create(
            model=DEFAULT_TEXT_MODEL,
            max_tokens=2000,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Vendedor: {vendedor}\nCliente: {cliente_nome or 'Não informado'}\n\nTranscrição do áudio:\n{transcricao}"
                }
            ]
        )

        response_text = message.choices[0].message.content
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]
        resultado = json.loads(response_text)
        return resultado

    except json.JSONDecodeError:
        # Se a IA retornar JSON inválido, usa fallback heurístico
        return _gerar_heuristico(transcricao, vendedor, cliente_nome)
    except Exception as e:
        print(f"[BOM] Erro na API Groq: {e}. Usando fallback heurístico.")
        return _gerar_heuristico(transcricao, vendedor, cliente_nome)


def _gerar_heuristico(transcricao: str, vendedor: str, cliente_nome: str = None) -> dict:
    """
    Extração heurística local inteligente baseada em regras dinâmicas e regex.
    Analisa as necessidades do cliente, extrai quantidades de componentes e
    especificações de forma dinâmica.
    """
    import re
    texto = transcricao.lower()

    # Dynamic Client Name Extraction from transcript if not provided or default
    detected_cliente = None
    if not cliente_nome or cliente_nome in ("Cerâmica Branco", "Cliente Geral", "Novo Cliente", "Cliente IA"):
        if "nutrisoja" in texto:
            detected_cliente = "NutriSoja"
        elif "nestlé" in texto or "nestle" in texto:
            detected_cliente = "Nestlé"
        elif "cerâmica branco" in texto or "ceramica branco" in texto:
            detected_cliente = "Cerâmica Branco"
        elif "anaclara" in texto or "ana clara" in texto:
            detected_cliente = "AnaClara"
        else:
            # Let's try some regexes:
            match = re.search(r'cliente (?:de|da|do)\s+[a-zA-Záàâãéèêíïóôõöúçñ\s]+,\s+a\s+([a-zA-Záàâãéèêíïóôõöúçñ\s0-9]+)', transcricao)
            if match:
                detected_cliente = match.group(1).strip()
            else:
                match2 = re.search(r'planta da\s+([a-zA-Záàâãéèêíïóôõöúçñ\s0-9]+)', transcricao)
                if match2:
                    detected_cliente = match2.group(1).strip()
                else:
                    match3 = re.search(r'cliente:\s*([a-zA-Záàâãéèêíïóôõöúçñ\s0-9]+)', transcricao)
                    if match3:
                        detected_cliente = match3.group(1).strip()
    
    if detected_cliente:
        cliente_nome = detected_cliente
    elif not cliente_nome:
        cliente_nome = "Cliente Geral"

    # Detecção de tipo de equipamento
    tipo_equip = "Não identificado"
    if any(w in texto for w in ["extrusora", "extrusão"]):
        tipo_equip = "Extrusora Industrial"
    elif any(w in texto for w in ["misturador", "tanque", "reator"]):
        tipo_equip = "Tanque Misturador/Reator"
    elif any(w in texto for w in ["dosador", "dosagem", "envase"]):
        tipo_equip = "Sistema de Dosagem/Envase"
    elif any(w in texto for w in ["prensa", "estampa", "prensagem"]):
        tipo_equip = "Prensa Industrial"
    elif any(w in texto for w in ["esteira", "transportador", "conveyor"]):
        tipo_equip = "Transportador/Esteira"
    elif any(w in texto for w in ["caldeira", "boiler"]):
        tipo_equip = "Caldeira Industrial"
    elif any(w in texto for w in ["moagem", "moinho", "moer"]):
        tipo_equip = "Moinho Industrial"

    # Detecção de potência
    potencia = 15.0  # default
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
    if any(w in texto for w in ["aliment", "comida", "food", "soja", "nutrisoja"]):
        setor = "alimentos"
    elif any(w in texto for w in ["farmac", "pharma", "medicamento", "gxp"]):
        setor = "farmacêutico"
    elif any(w in texto for w in ["cosmét", "beleza"]):
        setor = "cosméticos"
    elif any(w in texto for w in ["químic", "react"]):
        setor = "químico"
    elif any(w in texto for w in ["automotiv", "autopeç"]):
        setor = "automotivo"
    elif any(w in texto for w in ["ceram", "cerâm", "argila"]):
        setor = "cerâmica"

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

    # Helper function to find quantities dynamically in the text
    def find_quantity(patterns, default_qty=1):
        for pat in patterns:
            # Matches "5 pt100", "5x pt100", "5 peças de pt100", "5 sensores pt100"
            rx1 = rf"(\d+)\s*(?:x|unidades|unidade|peças|peça|pçs|pç|sensores|sensor|transmissores|transmissor|clps|clp)?\s*(?:de)?\s*(?:[a-zA-Záàâãéèêíïóôõöúçñ\-\s]*?){pat}"
            m1 = re.search(rx1, texto)
            if m1:
                return max(1, int(m1.group(1)))
            
            # Matches "pt100: 5", "pt100 - 5"
            rx2 = rf"{pat}\s*(?::|-|—)?\s*(\d+)"
            m2 = re.search(rx2, texto)
            if m2:
                return max(1, int(m2.group(1)))
                
        # If keyword matches but no number found, return default quantity
        if any(re.search(rf"\b{pat}\b", texto) for pat in patterns):
            return default_qty
        return 0

    components_mapping = [
        {
            "codigo": "CLP-S7-1500",
            "descricao": "CLP Siemens S7-1500",
            "valor_unit": 14200.00,
            "unidade": "pç",
            "patterns": ["siemens", "s7-1500", "s7 1500"],
            "default_qty": 1
        },
        {
            "codigo": "CLP-AB-L5K",
            "descricao": "CLP Allen-Bradley CompactLogix L5K",
            "valor_unit": 12500.00,
            "unidade": "pç",
            "patterns": ["allen", "bradley", "compactlogix", "ab l5k"],
            "default_qty": 1
        },
        {
            "codigo": "CLP-SCH-M241",
            "descricao": "CLP Schneider Modicon M241",
            "valor_unit": 8900.00,
            "unidade": "pç",
            "patterns": ["schneider", "modicon", "m241"],
            "default_qty": 1
        },
        {
            "codigo": "CLP-WEG-TPW04",
            "descricao": "CLP WEG TPW-04",
            "valor_unit": 6500.00,
            "unidade": "pç",
            "patterns": ["weg", "tpw", "tpw-04", "tpw04"],
            "default_qty": 1
        },
        {
            "codigo": "SEN-TEMP-PT100",
            "descricao": "Sensor temperatura PT100 industrial -50~400°C",
            "valor_unit": 450.00,
            "unidade": "pç",
            "patterns": ["pt100", "sensor de temperatura", "sensor temperatura", "sensores de temperatura", "sensores temperatura", "temperatura", "molde"],
            "default_qty": 4
        },
        {
            "codigo": "SEN-PRESS-4-20",
            "descricao": "Transmissor pressão 4-20mA 0-10 bar",
            "valor_unit": 1200.00,
            "unidade": "pç",
            "patterns": ["pressão", "pressao", "transmissor de pressão", "transmissor pressão", "transmissores de pressão", "bar", "transdutor"],
            "default_qty": 2
        },
        {
            "codigo": "SEN-VIB-ICP",
            "descricao": "Acelerômetro ICP vibração industrial",
            "valor_unit": 2800.00,
            "unidade": "pç",
            "patterns": ["vibração", "vibraçao", "acelerometro", "acelerômetro", "icp"],
            "default_qty": 2
        },
        {
            "codigo": "SEN-CORR-TC",
            "descricao": "Transformador de corrente TC split-core",
            "valor_unit": 380.00,
            "unidade": "pç",
            "patterns": ["corrente", "tc", "split-core", "tc split"],
            "default_qty": 3
        },
        {
            "codigo": "MOD-OPCUA-GW",
            "descricao": "Gateway OPC UA Industrial",
            "valor_unit": 3500.00,
            "unidade": "pç",
            "patterns": ["opc", "opcua", "opc-ua", "opc ua"],
            "default_qty": 1
        },
        {
            "codigo": "MOD-MODBUS-ETH",
            "descricao": "Módulo comunicação Modbus TCP/Ethernet",
            "valor_unit": 1800.00,
            "unidade": "pç",
            "patterns": ["modbus", "modulo modbus", "módulo modbus"],
            "default_qty": 1
        },
        {
            "codigo": "IHM-7POL",
            "descricao": "IHM 7 polegadas touchscreen industrial",
            "valor_unit": 4200.00,
            "unidade": "pç",
            "patterns": ["ihm", "touchscreen", "tela", "touch"],
            "default_qty": 1
        },
        {
            "codigo": "PAI-CMD-24P",
            "descricao": "Painel de comando 24 pontos IP65",
            "valor_unit": 7500.00,
            "unidade": "pç",
            "patterns": ["painel de comando", "painel de controle", "painel", "ip65"],
            "default_qty": 1
        },
        {
            "codigo": "CAB-IND-100M",
            "descricao": "Cabo industrial blindado 100m",
            "valor_unit": 1200.00,
            "unidade": "rolo",
            "patterns": ["cabo blindado", "cabo", "cabos blindados", "blindado"],
            "default_qty": 1
        },
        {
            "codigo": "FONT-24VDC",
            "descricao": "Fonte alimentação 24VDC 10A industrial",
            "valor_unit": 650.00,
            "unidade": "pç",
            "patterns": ["fonte alimentacao", "fonte alimentação", "fonte 24v", "fonte 24vdc", "fonte"],
            "default_qty": 2
        },
        {
            "codigo": "REL-SEG-NR12",
            "descricao": "Relé de segurança NR-12 Cat.4",
            "valor_unit": 1400.00,
            "unidade": "pç",
            "patterns": ["rele de seguranca", "relé de segurança", "rele de seg", "nr12", "nr-12", "segurança", "seguranca"],
            "default_qty": 2
        },
        {
            "codigo": "SW-IND-8P",
            "descricao": "Switch industrial 8 portas Ethernet",
            "valor_unit": 2200.00,
            "unidade": "pç",
            "patterns": ["switch", "switch industrial", "switch ethernet"],
            "default_qty": 1
        },
        {
            "codigo": "INV-FREQ-30KW",
            "descricao": "Inversor de frequência 30kW 380V",
            "valor_unit": 9200.00,
            "unidade": "pç",
            "patterns": ["inversor 30kw", "inversor.*30.*kw", "30kw"],
            "default_qty": 1
        },
        {
            "codigo": "INV-FREQ-15KW",
            "descricao": "Inversor de frequência 15kW 380V",
            "valor_unit": 5800.00,
            "unidade": "pç",
            "patterns": ["inversor 15kw", "inversor.*15.*kw", "15kw", "inversor", "motores", "motor"],
            "default_qty": 1
        }
    ]

    bom = []
    for comp in components_mapping:
        qty = find_quantity(comp["patterns"], comp["default_qty"])
        if qty > 0:
            # Evitar duplicar inversores se ambos casarem
            if comp["codigo"] == "INV-FREQ-15KW" and any(x["codigo"] == "INV-FREQ-30KW" for x in bom):
                continue
            # Evitar duplicar CLPs se mais de um casar
            if comp["codigo"].startswith("CLP-") and any(x["codigo"].startswith("CLP-") for x in bom):
                continue
            # Evitar duplicar módulos de comunicação
            if comp["codigo"].startswith("MOD-") and any(x["codigo"].startswith("MOD-") for x in bom):
                continue
            
            bom.append({
                "codigo": comp["codigo"],
                "descricao": comp["descricao"],
                "quantidade": qty,
                "unidade": comp["unidade"],
                "valor_unit": comp["valor_unit"]
            })

    # Fallback caso nada seja detectado no texto
    if not bom:
        if potencia > 20:
            bom.append({"codigo": "CLP-AB-L5K", "descricao": "CLP Allen-Bradley CompactLogix L5K", "quantidade": 1, "unidade": "pç", "valor_unit": 12500.00})
        else:
            bom.append({"codigo": "CLP-WEG-TPW04", "descricao": "CLP WEG TPW-04", "quantidade": 1, "unidade": "pç", "valor_unit": 6500.00})
        
        bom.append({"codigo": "SEN-TEMP-PT100", "descricao": "Sensor temperatura PT100 industrial -50~400°C", "quantidade": 4, "unidade": "pç", "valor_unit": 450.00})
        bom.append({"codigo": "SEN-PRESS-4-20", "descricao": "Transmissor pressão 4-20mA 0-10 bar", "quantidade": 2, "unidade": "pç", "valor_unit": 1200.00})
        bom.append({"codigo": "SEN-VIB-ICP", "descricao": "Acelerômetro ICP vibração industrial", "quantidade": 2, "unidade": "pç", "valor_unit": 2800.00})
        bom.append({"codigo": "SEN-CORR-TC", "descricao": "Transformador de corrente TC split-core", "quantidade": 3, "unidade": "pç", "valor_unit": 380.00})
        
        if protocolo == "OPC UA":
            bom.append({"codigo": "MOD-OPCUA-GW", "descricao": "Gateway OPC UA Industrial", "quantidade": 1, "unidade": "pç", "valor_unit": 3500.00})
        else:
            bom.append({"codigo": "MOD-MODBUS-ETH", "descricao": "Módulo comunicação Modbus TCP/Ethernet", "quantidade": 1, "unidade": "pç", "valor_unit": 1800.00})
            
        bom.append({"codigo": "IHM-7POL", "descricao": "IHM 7 polegadas touchscreen industrial", "quantidade": 1, "unidade": "pç", "valor_unit": 4200.00})
        bom.append({"codigo": "PAI-CMD-24P", "descricao": "Painel de comando 24 pontos IP65", "quantidade": 1, "unidade": "pç", "valor_unit": 7500.00})
        bom.append({"codigo": "FONT-24VDC", "descricao": "Fonte alimentação 24VDC 10A industrial", "quantidade": 2, "unidade": "pç", "valor_unit": 650.00})
        bom.append({"codigo": "CAB-IND-100M", "descricao": "Cabo industrial blindado 100m", "quantidade": 1, "unidade": "rolo", "valor_unit": 1200.00})
        bom.append({"codigo": "SW-IND-8P", "descricao": "Switch industrial 8 portas Ethernet", "quantidade": 1, "unidade": "pç", "valor_unit": 2200.00})
        
        if "NR-12" in certificacoes:
            bom.append({"codigo": "REL-SEG-NR12", "descricao": "Relé de segurança NR-12 Cat.4", "quantidade": 2, "unidade": "pç", "valor_unit": 1400.00})
        if potencia > 10:
            inv = "INV-FREQ-30KW" if potencia > 20 else "INV-FREQ-15KW"
            bom.append({"codigo": inv, "descricao": "Inversor de frequência 30kW 380V" if potencia > 20 else "Inversor de frequência 15kW 380V", "quantidade": 1, "unidade": "pç", "valor_unit": 9200.00 if potencia > 20 else 5800.00})

    # Template comissionamento dinâmico
    dias_base = 6
    if setor == "farmacêutico":
        dias_base = 13
    elif setor == "químico":
        dias_base = 8

    etapas = [
        "1. Inspeção física do painel e cabeamento",
        "2. Verificação de alimentação elétrica",
    ]
    
    clp_item = next((x for x in bom if x["codigo"].startswith("CLP-")), None)
    if clp_item:
        etapas.append(f"3. Download do programa no {clp_item['descricao']}")
        etapas.append("4. Teste de I/O (entradas e saídas) ponto a ponto")
    else:
        etapas.append("3. Download do programa no CLP")
        etapas.append("4. Teste de I/O (entradas e saídas) ponto a ponto")
        
    gw_item = next((x for x in bom if x["codigo"].startswith("MOD-")), None)
    if gw_item:
        etapas.append(f"5. Configuração de comunicação ({'OPC UA' if 'OPCUA' in gw_item['codigo'] else 'Modbus TCP'})")
    else:
        etapas.append(f"5. Configuração de comunicação ({protocolo})")
        
    sensor_items = [x for x in bom if x["codigo"].startswith("SEN-")]
    if sensor_items:
        etapas.append(f"6. Calibração de sensores em campo ({', '.join(x['descricao'].split()[0] for x in sensor_items)})")
    else:
        etapas.append("6. Calibração de sensores em campo")
        
    etapas.extend([
        "7. Teste funcional em modo manual",
        "8. Teste funcional em modo automático",
        "9. Ajuste de parâmetros e setpoints",
        "10. Treinamento do operador",
        "11. Documentação e entrega final",
    ])
    
    if setor == "farmacêutico":
        etapas.insert(8, "8.1. Protocolo de validação IQ/OQ/PQ (ANVISA)")
        etapas.append("12. Emissão de certificado de validação GxP")

    template = {
        "etapas": etapas,
        "dias_estimados": dias_base,
        "engenheiro_sugerido": "Cláudia Santarém" if setor == "farmacêutico" else "A definir",
        "riscos": [
            "Atraso por incompatibilidade de protocolo",
            "Calibração de sensores fora de especificação",
            f"{'Validação GxP pode estender prazo em 5+ dias' if setor == 'farmacêutico' else 'Intempéries climáticas'}",
            "Necessidade de treinamento adicional para operadores",
        ]
    }

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
                "metodo_extracao": "heurístico dinâmico",
            }
        },
        "bom": bom,
        "template_comissionamento": template,
    }
