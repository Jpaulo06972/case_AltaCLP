# Proposta Comercial — Plataforma de Inteligência Operacional AltaCLP
**HomoDeus × AltaCLP Indústria S.A.**
Versão 1.0 · 17 de maio de 2026

---

## Parte 1 — O Problema Real (O que Descobrimos)

A AltaCLP apresenta cinco problemas operacionais declarados e ao menos oito problemas ocultos. A análise das transcrições de reunião, planilhas internas e comunicações da equipe revela uma divergência significativa entre a percepção do CEO e a realidade operacional.

### O Que o Marcos Vê vs. O Que Existe

| Dimensão | Visão do Marcos | Realidade (Cláudia + Dados) |
|---|---|---|
| Taxa de falsos alertas | 60% | **64%** (dado de 6 meses atrás) |
| Custo mensal de visitas falsas | R$ 27.000 | **R$ 31.400** (após reajuste de combustível) |
| Backlog de comissionamento | 22 máquinas | **26 máquinas** (4 novas da Anaclara) |
| Tempo por comissionamento | 3-4 dias | **6 dias** (média real; 12-13 dias em farmacêutico) |
| Incidentes por drift de código | 3 em 2026 | **4 em 2026** (Marcos esconde o quarto) |
| Prejuízo por incidentes | ~R$ 220k | **~R$ 250k** (inclui Ponta Grossa) |

Esta divergência não é acidental. Ela reflete um padrão de gestão: Marcos é avesso a episódios grandes e prefere problemas pequenos, recorrentes e controláveis. Roberto (CFO) pressiona pelo caixa mensal. Cláudia vê o risco estratégico. **A nossa proposta precisa falar com os três ao mesmo tempo.**

---

## Parte 2 — A Solução: Plataforma de Inteligência Operacional

A solução não é "colocar IA em tudo". É uma plataforma híbrida que resolve os problemas certos, na ordem certa, com a tecnologia certa para cada caso.

### Princípio de Design da Solução

> **"Não construímos IA porque é moderno. Construímos IA onde os dados permitem e regras onde os dados não estão prontos."**

Esta distinção é crítica. O banco de dados de sensores da AltaCLP possui labels de incidente a apenas 50% de completude. Um modelo de IA preditiva puro entregaria apenas 20% de melhoria — insuficiente para justificar o investimento inicial. A abordagem híbrida entrega 30% de melhoria imediata (via thresholds dinâmicos, sem IA) e 65% em regime pleno (com IA treinada em dados limpos).

### Os Três Módulos

**Módulo 1 — Assistente de Comissionamento e Cotação**
O vendedor encaminha o áudio do WhatsApp para o sistema. O Whisper (OpenAI) transcreve o áudio com precisão para termos técnicos industriais em português brasileiro. O GPT-4o extrai os parâmetros da fábrica — tipo de equipamento, tensão, protocolo de comunicação, setor industrial, requisitos de certificação — e gera automaticamente a Bill of Materials (BOM) e o template de comissionamento pré-preenchido. O engenheiro recebe 90% do trabalho feito e precisa apenas calibrar, fazer o FAT e treinar o operador.

**Módulo 2 — Preditiva Híbrida**
Um painel de thresholds dinâmicos permite que a Cláudia ajuste os limites máquina a máquina em uma interface web, sem código. Em paralelo, um modelo de Isolation Forest (scikit-learn) aprende o padrão normal de cada máquina individualmente, considerando contexto de turno, temperatura ambiente e histórico. O modelo detecta combinações anômalas de sensores — não apenas valores individuais fora de range.

**Módulo 3 — Auditoria GitOps de Campo**
Um agente leve instalado no Gateway IoT do cliente calcula o hash do código rodando no CLP a cada 6 horas via OPC UA e compara com a versão oficial no repositório Git central. Se houver divergência, a engenharia é alertada antes do próximo deploy. O sistema sugere automaticamente um Pull Request com o diff do hotfix para revisão e merge.

### Justificativa de Tecnologias

| Componente | Tecnologia | Por Que Esta e Não Outra |
|---|---|---|
| Transcrição de áudio | OpenAI Whisper API | Precisão superior com sotaques brasileiros e terminologia técnica industrial. Testado com áudios de 8-14 minutos de WhatsApp. Alternativa Google Speech-to-Text perde em vocabulário técnico. |
| Extração de entidades | GPT-4o (OpenAI) | Capacidade de raciocínio contextual — entende que "extrusora de 75kW" implica módulo de potência específico. Claude 3.5 Sonnet é alternativa viável com custo similar. Gemini Pro perde em precisão técnica. |
| Anomaly Detection | Isolation Forest (scikit-learn) | Adequado para dados com labels incompletos (50%). Não requer grandes volumes de dados rotulados. Alternativa LSTM/Autoencoder exigiria 12+ meses de dados limpos — inviável no prazo. |
| Backend | Python + FastAPI | Integração nativa com ecossistema científico (Pandas, scikit-learn). Conexão direta ao PostgreSQL e MQTT existentes da AltaCLP. Alternativa Node.js perderia em bibliotecas de ML. |
| Frontend | React + TypeScript | Padrão de mercado para dashboards B2B. Componentes reutilizáveis para múltiplos perfis de usuário (CEO, Engenharia, Campo). |
| Agente Edge (GitOps) | Python leve + OPC UA | Footprint mínimo no Gateway existente. Sem necessidade de hardware adicional. |

---

## Parte 3 — Estratégia de Venda

### Quem Decide e O Que Cada Um Quer

| Stakeholder | Motivação Principal | O Que Teme | Como Falar com Ele |
|---|---|---|---|
| **Marcos Tedesco** (CEO, 70% ações) | Cortar os R$ 31.400/mês de visitas falsas. Mostrar resultado para o conselho. | Projeto que não entrega em 3 meses. Custo alto sem ROI claro. | Falar em meses, não em anos. Mostrar payback em semanas. |
| **Roberto** (CFO, 30% ações) | Due Diligence. Empresa mais valorizável para o fundo. | Risco de projeto de TI que atrasa e estoura orçamento. | Falar em múltiplo de valuation, não em economia mensal. |
| **Cláudia Santarém** (Engenharia) | Resolver o backlog. Não ser sobrecarregada. | IA que não funciona com dados ruins. Promessas que ela vai ter que cumprir. | Ser honesto sobre limitações dos dados. Mostrar que a Fase 1 não depende de IA. |

### O Argumento Principal (Para o Marcos)

> "Marcos, você me pediu para resolver os R$ 31.400 de visitas falsas. Eu vou resolver. Mas antes de chegar lá, preciso te mostrar um número que você não está vendo: você tem R$ 780.000 em risco de cancelamento na Anaclara Alimentos. O gestor de planta deles disse à Cláudia que cancela se não entregar em junho. Isso é 25 vezes o custo mensal das visitas falsas. A nossa Fase 1 resolve os dois ao mesmo tempo, em 4 semanas."

### O Argumento Para o Roberto (Due Diligence)

> "Roberto, uma empresa de automação industrial com um sistema de inteligência operacional proprietário vale de 2 a 3x mais em múltiplo de EBITDA do que uma empresa que opera no Excel. O fundo que está fazendo a due diligence vai perguntar: 'Como vocês gerenciam a manutenção preditiva de 50 máquinas em campo?' Com a plataforma, a resposta é: 'Com IA e auditoria automática de código.' Sem ela, a resposta é: 'Com threshold fixo e caderninho do técnico.'"

---

## Parte 4 — Respostas a Objeções

### Objeção 1: "Isso é caro. R$ 150k é muito dinheiro."

**Resposta:** "Marcos, você está gastando R$ 31.400 por mês em visitas que não precisariam acontecer. Em menos de 5 meses, o projeto se paga só com isso. Mas o payback real é em menos de 6 semanas — porque a Fase 1 desbloqueia a entrega da Anaclara, que vale R$ 780.000. O investimento é R$ 150k. O retorno no primeiro ano é R$ 1,32 milhão. Isso é 8,8x de ROI. Qual investimento financeiro te dá isso?"

### Objeção 2: "A gente já tentou padronizar processo antes e não funcionou."

**Resposta:** "Você tentou padronizar com planilha e caderninho. O que não funcionou foi a disciplina humana — o Anderson não dá push porque está cansado, o Júnior não segue o template porque está com pressa. A nossa solução não depende de disciplina. O sistema captura automaticamente o que o técnico fez, compara com o Git e alerta antes que o problema aconteça. Não estamos pedindo que as pessoas mudem. Estamos colocando uma rede de segurança embaixo do jeito que elas já trabalham."

### Objeção 3: "IA com dados ruins não funciona. A Cláudia disse que os labels estão a 50%."

**Resposta:** "A Cláudia está certa, e é exatamente por isso que a nossa Fase 1 não usa IA para preditiva. Usamos thresholds dinâmicos — sem modelo, sem dado de treino — e já reduzimos 30% dos falsos alertas em 1 semana. A IA entra na Fase 3, quando já temos 8 semanas de dados limpos coletados. Não estamos apostando na IA cega. Estamos construindo a base de dados enquanto entregamos resultado imediato."

### Objeção 4: "E se o projeto atrasar? Vocês são uma consultoria pequena."

**Resposta:** "A Fase 1 tem escopo fixo e entregável concreto: painel de thresholds no ar, assistente de cotação funcionando, integração com o PostgreSQL de vocês. São 4 semanas. Se não entregar, não cobramos. Propomos um contrato por fase, com pagamento na entrega de cada milestone. Vocês não estão comprando um projeto de 12 semanas às cegas — estão comprando 4 semanas de cada vez, com resultado visível antes de aprovar a próxima."

### Objeção 5: "O Sérgio do TPM não vai deixar a gente acessar os dados."

**Resposta:** "Esse é o obstáculo mais real que temos. A nossa proposta inclui uma semana de trabalho conjunto com o Sérgio para mapear os schemas necessários — não precisamos de acesso irrestrito, precisamos de leitura em 3 tabelas específicas. Se o Sérgio continuar bloqueando após essa conversa, precisamos que o Marcos ou a Cláudia escalem internamente. Isso não é um problema técnico, é um problema político que precisa de patrocínio executivo."

### Objeção 6: "E quando o Júnior sair, quem vai manter o sistema?"

**Resposta:** "O sistema foi desenhado para não depender de um único engenheiro. A documentação é gerada automaticamente, os modelos são retreinados mensalmente de forma autônoma, e a interface de thresholds pode ser operada por qualquer engenheiro de aplicação sem treinamento especial. Além disso, incluímos 6 meses de suporte pós-entrega no contrato. O risco de concentração de conhecimento que vocês têm hoje — onde o Júnior é o único que conhece a planta da Pampulha — é exatamente o tipo de problema que a plataforma resolve."

---

## Parte 5 — Roadmap de Expansão (Próximas Versões)

### Versão 1.0 (MVP — 12 semanas)
O que está sendo entregue agora: thresholds dinâmicos, assistente de cotação, auditoria GitOps, app mobile para técnicos, dashboard executivo.

### Versão 2.0 (Meses 4-9) — Inteligência de Campo
Com 6 meses de dados limpos coletados, o modelo de IA preditiva entra em produção. O app mobile dos técnicos ganha um assistente contextual: ao chegar em uma máquina, o técnico vê o histórico completo de visitas, peças trocadas, hotfixes anteriores e uma sugestão de diagnóstico baseada nos alertas recentes. O NPS tende a recuperar 8-10 pontos.

### Versão 3.0 (Meses 10-18) — Plataforma como Produto
A AltaCLP pode oferecer a plataforma como serviço para seus próprios clientes industriais — um portal onde o gestor de planta da Anaclara, da Belmare e da Cubatão acompanha em tempo real o status das suas máquinas, recebe alertas antes de paradas e aprova remotamente atualizações de código. Isso transforma a AltaCLP de prestadora de serviço em empresa de tecnologia industrial, aumentando o múltiplo de valuation para a due diligence do Roberto.

### Versão 4.0 (Ano 2+) — Rede de Conhecimento Industrial
Com dados de 50+ máquinas em campo, a plataforma acumula o maior banco de dados de comportamento de CLPs industriais do Brasil. Modelos treinados em uma fábrica de alimentos aprendem com incidentes de outra fábrica de alimentos. O sistema se torna mais inteligente a cada cliente novo — um efeito de rede que a Siemens e a GE não conseguem replicar com soluções genéricas.

---

## Parte 6 — Escopo, Custo e Dados Necessários

### Escopo por Fase

| Fase | Duração | Entregáveis | Valor |
|---|---|---|---|
| **Fase 1** | Semanas 1-4 | Painel de thresholds dinâmicos, Assistente de cotação (Whisper + GPT-4o), Integração MQTT/PostgreSQL, Dashboard executivo básico | **R$ 45.000** |
| **Fase 2** | Semanas 5-8 | Agente GitOps de auditoria, App mobile para técnicos, Dashboard completo (CEO + Engenharia + Campo) | **R$ 55.000** |
| **Fase 3** | Semanas 9-12 | Modelo de IA preditiva (Isolation Forest), Retreinamento automático mensal, Suporte 6 meses pós-entrega | **R$ 50.000** |
| **Total** | **12 semanas** | **Plataforma completa** | **R$ 150.000** |

### Cronograma de Pagamento (Proposta)
Pagamento por milestone entregue, não por tempo decorrido. Fase 1: R$ 45k na entrega e aprovação do painel. Fase 2: R$ 55k na entrega e aprovação do app. Fase 3: R$ 50k na entrega do modelo em produção.

### Dados que Precisamos da AltaCLP

Para iniciar o projeto, precisamos dos seguintes dados e acessos. O prazo de coleta estimado é de 1 semana (Semana 0, antes do início oficial):

| Item | Formato | Responsável AltaCLP | Observação |
|---|---|---|---|
| Acesso leitura PostgreSQL (3 tabelas de sensores) | Credenciais de banco | Sérgio do TPM | **Item crítico.** Requer alinhamento executivo se houver resistência. |
| Histórico de incidentes (últimos 24 meses) | Export CSV ou Excel | Cláudia Santarém | Incluir data, máquina, tipo de alerta, se foi falso ou real. |
| 10 áudios de cotação do vendedor + BOMs finais | .ogg ou .mp3 + .xlsx | João Vendedor + Cláudia | Para treinar o pipeline de extração de entidades. |
| Acesso de leitura ao repositório Git central | Token de leitura | Cláudia Santarém | Para o agente GitOps mapear a estrutura de código. |
| Lista de 50 máquinas em campo com protocolo (Modbus/OPC UA) | Planilha | Cláudia Santarém | Para configurar o agente de coleta de hash. |
| Planilha de thresholds atual (Sérgio) | Excel | Sérgio do TPM | Base para o painel de thresholds dinâmicos. |

### Premissas e Riscos

O projeto assume que o acesso ao PostgreSQL será liberado na Semana 0. Se o Sérgio do TPM continuar bloqueando, a Fase 1 pode ser iniciada com dados sintéticos (para demonstração) enquanto o acesso é negociado. O prazo de 12 semanas assume disponibilidade de 4 horas/semana da Cláudia para revisão e aprovação de entregáveis. A saída do Júnior Almeida não impacta o projeto, mas aumenta a urgência da Fase 2 (app mobile com histórico de máquinas).

---

*Proposta preparada por HomoDeus com base em análise das transcrições de call, planilhas internas e comunicações da AltaCLP. Dados financeiros baseados em informações fornecidas pela própria empresa.*
