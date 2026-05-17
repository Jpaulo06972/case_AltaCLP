# AltaCLP — Análise Completa de Problemas

## Contexto da Empresa
- **Razão Social:** AltaCLP Indústria de Automação e Controle S.A.
- **Fundação:** 2004 | **Sede:** Sumaré/SP
- **Faturamento 2025:** R$ 97-104M | **Meta 2026:** R$ 118M
- **Funcionários:** ~300 CLT | **Bases:** Sumaré, BH, Curitiba
- **Clientes:** 25 contas | R$ 16.3M receita contratada | 40 plantas ativas em 7 estados
- **Técnicos de campo:** 22 técnicos | 4 engenheiros de aplicação (Cláudia + 3)

## Contexto Estratégico Crítico (não declarado)
- **Due Diligence em curso:** Roberto (CFO/30%) está negociando com fundo de investimento
- **Reunião de conselho:** 18/mai/2026 — apresentação Q1 + plano (HOJE ou amanhã)
- **Pressão de tempo:** 6 semanas, não 6 meses como o Marcos pensa
- **Marcos tem 70% das ações ordinárias** — Roberto não pode agir sem ele
- **Júnior saindo:** engenheiro de aplicação sênior pediu demissão (Atos, +38% salário)
- **Sérgio do TPM:** está ativamente bloqueando acesso aos dados de sensor para consultoria externa

## Os 5 Problemas Declarados (por Marcos)

### Problema 1 — Falsos Alertas / Manutenção Preditiva
- **Métrica real (Cláudia):** 64% de falsos alertas (Marcos diz 60%)
- **Custo real:** R$ 31.400/mês (Marcos diz R$ 27k — dado desatualizado)
- **Custo anual:** ~R$ 376.800
- **Causa raiz:** Thresholds fixos e burros — não consideram contexto de máquina
- **Detalhe técnico:** Sistema usa Modbus + OPC UA, threshold único por tipo de sensor
- **Exemplo:** Sensor pressão M-VH-118 (Vinhal) — 4 visitas falsas em 12 semanas
- **Nota Cláudia:** Ajuste de threshold máquina-a-máquina = 1 semana de trabalho = 30% de redução SEM IA

### Problema 2 — Backlog de Comissionamento
- **Backlog real (Cláudia):** 26 máquinas (Marcos diz 22 — dado desatualizado)
- **Atraso contratual:** 13 das 26 máquinas com multa em 4 casos
- **Tempo real por máquina:** 6 dias em média (Marcos diz 3-4 — melhor caso)
- **Tempo farmacêutico:** 12-13 dias por validação GxP
- **Risco imediato:** Anaclara Alimentos (Boituva) — 4 máquinas, R$ 780k, prazo junho
- **Causa raiz:** Sem template padronizado, cada eng tem seu jeito, onboarding leva 6 meses
- **Impacto:** 104 dias de eng liberados se reduzir de 6 para 2 dias por máquina

### Problema 3 — Drift de Código (Campo vs. Git)
- **Incidentes graves:** 4 em 12 meses (Marcos diz 3 — esconde o quarto)
- **Custo total:** ~R$ 250k em prejuízo direto + R$ 140k crédito Belmare
- **Causa raiz:** Técnicos fazem hotfix em campo, não conseguem dar git push (VLAN restrita, cansaço, falta de disciplina)
- **Caso mais grave:** Belmare Cosméticos — linha parada 36h, tanque transbordou, quase rescisão
- **Exigência do cliente Belmare:** Auditoria automática mensal código campo vs. Git
- **Padrão:** Anderson Vasconcellos fez 2 hotfixes não documentados

### Problema 4 — Cotação Técnica Lenta
- **Tempo atual:** 5-7 dias | **Concorrente Mecasul:** 24 horas
- **Perda mensal:** ~6 negócios/mês | ~R$ 80k/mês em ticket médio
- **Causa real (Cláudia):** 90% do tempo é espera de resposta do vendedor, não a engenharia
- **Dinâmica política:** João vendedor é amigo pessoal do Marcos desde o colégio, padrinho de casamento — intocável
- **Formato atual:** Vendedor manda áudio de WhatsApp de 8-14 min descrevendo fábrica
- **Gargalo:** Engenharia ouve, transcreve, monta BOM no Excel manualmente

### Problema 5 — Suporte de Campo Sem Contexto
- **NPS:** caiu de 82 para 68 em 18 meses (-14 pontos)
- **Causa 1 (50%):** Técnico chega sem histórico — não sabe o que outro técnico fez antes
- **Causa 2 (50%):** Fila de atendimento terceirizado (BH) — 7-11 min de espera, atendente sem contexto
- **Exemplo:** Aspáragos Alimentos — Sebastião chegou sem saber que Joelson esteve lá 9 dias antes
- **Custo:** Terceirização BH = R$ 14k/mês, reduziu carga em 25% (esperado 60%)

## Problemas Escondidos (identificados na análise)
1. **Dados sujos:** NaN no sensor 7 por 2 meses, logs sem padrão — label de dado a 50%
2. **Resistência interna:** Sérgio do TPM bloqueando acesso a schemas do banco
3. **Due Diligence:** Roberto negociando com fundo sem Marcos saber do estágio real
4. **Saída de Júnior:** Único eng que conhece a planta inteira da Pampulha (risco de concentração)
5. **Terceirização BH:** Erro de gestão do Marcos — não vai admitir publicamente
6. **Marcos prometeu coisas sem consultar Cláudia:** Anaclara em junho, projeto preditiva em 3 meses
7. **Cláudia sobrecarregada:** Anderson trabalhando 7 fins de semana em 8 semanas
8. **Dados de campo:** Sérgio Branchini (criador do sistema de alertas) saiu para WEG, deixou planilha de thresholds incompleta

## Infraestrutura Técnica Existente
- **Protocolo campo:** Modbus + OPC UA (máquinas mais novas)
- **Banco de dados:** PostgreSQL (mencionado por Sérgio)
- **Broker:** MQTT (mencionado por Sérgio do TPM)
- **Repositório:** Git central (código Structured Text + Lua supervisório)
- **Volume de dados:** ~12.500 leituras/dia/máquina
- **Supervisório:** Lua (linguagem)
- **CLP:** Structured Text (linguagem IEC 61131-3)
- **Problema de conectividade:** VLANs restritas em clientes impedem git push do campo

## Análise Financeira
| Problema | Custo Atual/Mês | Potencial de Economia |
|---|---|---|
| Falsos alertas | R$ 31.400 | R$ 20-25k/mês (redução 65-80%) |
| Backlog comissionamento | R$ 65k+ (oportunidade perdida) | R$ 780k em risco imediato |
| Drift de código | R$ 20k/mês (média incidentes) | R$ 240k/ano |
| Cotação lenta | R$ 80k/mês (receita perdida) | R$ 60k/mês recuperável |
| Suporte sem contexto | R$ 14k/mês (terceirização) + NPS | Recuperação de NPS + retenção |
| **TOTAL** | **~R$ 210k/mês** | **~R$ 1.1M/ano** |
