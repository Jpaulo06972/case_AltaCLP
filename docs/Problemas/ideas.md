# AltaCLP Intelligence — Ideias de Design

## Contexto
Dashboard de inteligência operacional para empresa de automação industrial brasileira (B2B, setor industrial). Usuários: CEO (Marcos), CFO (Roberto), Coordenadora de Engenharia (Cláudia), Técnicos de Campo. O produto precisa transmitir seriedade técnica, confiança e precisão — não um SaaS genérico.

---

<response>
<probability>0.07</probability>
<text>

## Opção A — Industrial Precision (Escolhida)

**Design Movement:** Brutalismo Industrial Refinado — inspirado em painéis de controle de sala de operações (SCADA), com influência de dashboards de trading e sistemas de monitoramento aeroespacial.

**Core Principles:**
1. Dados como protagonistas: cada pixel serve à informação, não à decoração
2. Hierarquia de urgência: vermelho/âmbar/verde com significado operacional real
3. Densidade sem caos: alta densidade de informação com espaçamento cirúrgico
4. Confiança técnica: tipografia monospace para dados, sans-serif para contexto

**Color Philosophy:**
- Background: Cinza ardósia profundo (#0F1117) — evoca sala de controle, não startup
- Accent primário: Âmbar industrial (#F59E0B) — alerta, atenção, ação
- Accent secundário: Verde operacional (#10B981) — sistema saudável, OK
- Vermelho crítico: (#EF4444) — parada, incidente, urgente
- Texto principal: Branco frio (#F8FAFC)
- Texto secundário: Cinza (#94A3B8)
- Bordas: (#1E2433) — separação sutil, não intrusiva

**Layout Paradigm:**
- Sidebar fixa à esquerda (64px colapsada / 240px expandida) com ícones industriais
- Grid assimétrico: coluna principal 2/3 + coluna lateral 1/3
- Métricas críticas em cards com bordas coloridas por status (não apenas ícones)
- Linha do tempo de incidentes como trilho horizontal, não lista vertical

**Signature Elements:**
1. Indicadores de status com pulso animado (dot pulsante para alertas ativos)
2. Números grandes com fonte monospace (JetBrains Mono) para métricas críticas
3. Micro-gráficos sparkline inline nos cards de máquina

**Interaction Philosophy:**
- Hover revela contexto adicional sem mudar layout
- Clique em incidente expande detalhes inline (não modal)
- Filtros como chips industriais, não dropdowns

**Animation:**
- Entrada de dados: counter animado (0 → valor real) em 800ms
- Alertas novos: flash sutil de borda + entrada de cima
- Transições de página: fade de 150ms, sem slides
- Dots de status: pulso 2s infinito para alertas ativos

**Typography System:**
- Display/Títulos: Space Grotesk Bold (700) — geométrico, técnico, não genérico
- Corpo/Labels: Space Grotesk Regular (400)
- Dados/Métricas: JetBrains Mono — monospace que transmite precisão de engenharia
- Tamanhos: 11px (labels), 13px (corpo), 15px (subtítulo), 24px (métrica), 40px (hero)

</text>
</response>

<response>
<probability>0.05</probability>
<text>

## Opção B — Clean Manufacturing

**Design Movement:** Swiss International Style aplicado a software industrial — grid rígido, tipografia como estrutura, zero ornamento.

**Core Principles:**
1. Grid de 8px como lei absoluta
2. Tipografia como único elemento decorativo
3. Cor apenas para semântica, nunca para estética
4. Informação antes de interface

**Color Philosophy:** Branco puro + preto + um único acento (azul Siemens #009999). Sem gradientes.

**Layout Paradigm:** Colunas de largura fixa, separadas por linhas de 1px. Tabelas como elemento principal.

**Typography System:** IBM Plex Mono para tudo. Hierarquia apenas por tamanho e peso.

</text>
</response>

<response>
<probability>0.03</probability>
<text>

## Opção C — Dark Ops Dashboard

**Design Movement:** Cyberpunk Industrial — inspirado em interfaces de ficção científica mas com dados reais. Para impressionar em apresentação executiva.

**Core Principles:**
1. Glassmorphism sobre fundo escuro profundo
2. Neon sutil como accent (não excessivo)
3. Animações de dados em tempo real
4. Sensação de "sala de guerra"

**Color Philosophy:** Preto absoluto (#000000) + Verde neon (#00FF88) + Azul elétrico (#0066FF). Alto contraste.

**Layout Paradigm:** Cards flutuantes com blur, sobreposições, z-index intencional.

**Typography System:** Orbitron para títulos (futurista), Inter para corpo.

</text>
</response>

---

## Decisão Final: **Opção A — Industrial Precision**

Escolhida porque:
- Transmite seriedade técnica adequada para empresa de automação industrial B2B
- O CEO (Marcos) é engenheiro mecânico de 22 anos de mercado — vai reconhecer a linguagem visual
- Alta densidade de informação sem parecer "app de startup"
- Diferencia da concorrência (Mecasul, WEG) que provavelmente usa dashboards genéricos
- Adequado para apresentação em reunião de conselho (Due Diligence)
