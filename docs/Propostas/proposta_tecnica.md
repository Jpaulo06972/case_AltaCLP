# Proposta Técnica: Plataforma de Inteligência Operacional AltaCLP

## 1. O Problema Real vs. O Problema Percebido

Após análise profunda da operação da AltaCLP, incluindo dados de campo, comunicações internas e transcrições de reuniões, identificamos um desalinhamento crítico entre a visão executiva e a realidade operacional.

O CEO (Marcos) acredita que o maior problema é a **manutenção preditiva** (64% de falsos alertas, gerando R$ 31.400/mês de custo em visitas desnecessárias). No entanto, a Engenharia (Cláudia) aponta para um problema muito mais grave: o **backlog de comissionamento** (26 máquinas paradas, 13 com atraso contratual), que coloca em risco imediato contratos de R$ 780.000 (caso Anaclara Alimentos).

Além disso, existem problemas ocultos de alta severidade:
- **Drift de Código:** Técnicos fazem hotfixes em campo sem versionamento no Git, causando paradas de fábrica (ex: Belmare Cosméticos, R$ 140k de prejuízo).
- **Cotação Lenta:** Vendedores mandam áudios de 14 minutos no WhatsApp, e a engenharia demora 5-7 dias para orçar, perdendo negócios para a Mecasul (R$ 80k/mês).
- **Suporte sem Contexto:** Técnicos chegam ao cliente sem histórico, derrubando o NPS de 82 para 68.

## 2. A Solução Proposta: Abordagem Híbrida

A solução não é apenas "colocar IA em tudo". O banco de dados de sensores atual possui qualidade ruim (label a 50%, dados sujos), o que limitaria a eficácia de um modelo preditivo puro a apenas 20% de melhoria.

A arquitetura proposta resolve os problemas em três frentes paralelas, combinando IA Generativa para processos e Regras Dinâmicas + Machine Learning para telemetria.

### Módulo 1: Assistente de Comissionamento e Cotação (Impacto Imediato)
**Problema resolvido:** Backlog de 26 máquinas e perda de vendas.
- **Como funciona:** O vendedor encaminha o áudio do WhatsApp para o sistema. O sistema usa IA (Whisper + LLM) para transcrever e extrair automaticamente os parâmetros da fábrica (ex: "tanque de 500L", "válvula proporcional").
- **Resultado:** O sistema gera a Bill of Materials (BOM) e um *template* de comissionamento pré-preenchido em 90%. O tempo de comissionamento cai de 6 dias para 2 dias por máquina.

### Módulo 2: Preditiva Híbrida (Impacto a Médio Prazo)
**Problema resolvido:** Falsos alertas e visitas perdidas.
- **Como funciona:** Em vez de depender apenas de IA com dados ruins, implementamos primeiro um **Motor de Regras de Threshold Dinâmico**, permitindo que a Engenharia (Cláudia) ajuste os limites máquina a máquina (resolvendo 30% do problema em 1 semana). Em paralelo, a IA treina modelos de *Anomaly Detection* sobre os dados limpos para identificar padrões complexos.

### Módulo 3: Auditoria GitOps de Campo (Mitigação de Risco)
**Problema resolvido:** Drift de código e multas contratuais.
- **Como funciona:** Um agente leve roda no Gateway IoT do cliente, calculando o *hash* do código rodando no CLP e comparando com a versão oficial no Git Central da AltaCLP. Se houver divergência, o painel alerta a engenharia antes do próximo deploy.

## 3. Arquitetura Técnica

A arquitetura foi desenhada para se integrar à infraestrutura existente da AltaCLP (PostgreSQL, MQTT, Git) sem exigir substituição de hardware de campo.

![Arquitetura Técnica](./arquitetura.png)

### Justificativa de Tecnologias (Qual IA usar e por quê)

| Componente | Tecnologia Escolhida | Justificativa Técnica e de Negócio |
|---|---|---|
| **Transcrição de Áudio** | OpenAI Whisper API | Alta precisão com sotaques brasileiros e termos técnicos de engenharia. Resolve o problema dos áudios longos do vendedor João. |
| **Extração de Entidades (BOM)** | GPT-4o ou Claude 3.5 Sonnet | Capacidade superior de raciocínio para ler a transcrição e entender que "extrusora" no contexto significa "moldadora", estruturando a cotação. |
| **Preditiva (Anomaly Detection)** | Isolation Forest / Autoencoders | Modelos clássicos de ML são mais adequados que Deep Learning puro devido à sujeira atual dos dados (labels a 50%). |
| **Backend / Integração** | Python (FastAPI) | Integração nativa com ecossistema de dados (Pandas, Scikit-learn) e facilidade para conectar ao PostgreSQL e MQTT existentes da AltaCLP. |

## 4. Estratégia de Implementação (Roadmap)

O projeto será entregue em fases, priorizando o que salva dinheiro e contratos imediatamente, para garantir o sucesso da Due Diligence do CFO Roberto.

**Fase 1 (Semanas 1-4): Estancar o Sangramento**
- Implementação do painel de Thresholds Dinâmicos (corta falsos alertas em 30%).
- Assistente de Cotação via WhatsApp (libera a engenharia para focar no comissionamento).
- *Vitória rápida:* Salva o contrato da Anaclara Alimentos (R$ 780k) permitindo entrega em junho.

**Fase 2 (Semanas 5-8): Controle e Visibilidade**
- Auditoria de Código (Campo vs. Git) para evitar novos desastres como o da Belmare.
- App Mobile para Técnicos com histórico da máquina e contexto da visita.

**Fase 3 (Semanas 9-12): Preditiva Avançada**
- Treinamento e deploy do modelo de IA para detecção de anomalias em sensores.
- Dashboard executivo unificado para a reunião de conselho.

## 5. Definição de Escopo e Dados Necessários

**Prazo Total:** 12 semanas (3 meses).
**Custo Salvo Estimado:** R$ 1.100.000 / ano (redução de falsos alertas, retenção de clientes, ganho de eficiência comercial).

**Dados que precisamos da AltaCLP para iniciar:**
1. Acesso de leitura ao banco PostgreSQL (schemas de sensores). *Nota: Será necessário alinhar com Sérgio do TPM, que atualmente bloqueia este acesso.*
2. Histórico de incidentes exportado do sistema atual.
3. 10 exemplos de áudios de cotação do vendedor João + as BOMs finais geradas pela Cláudia.
4. Acesso ao repositório Git para mapear a estrutura de código dos CLPs.
