# 🎛️ AltaCLP Intelligence Platform

Bem-vindo ao repositório oficial da **Plataforma de Inteligência Operacional AltaCLP**, desenvolvida em parceria com a **HomoDeus**. 

Este sistema foi arquitetado para resolver, de forma preditiva e inteligente, os maiores gargalos operacionais da AltaCLP, incluindo a redução drástica de falsos alertas, auditoria automática de código de campo em CLPs (GitOps) e geração rápida de cotações comerciais utilizando Inteligência Artificial (IA).

---

## 🌟 O que a Plataforma resolve?

A operação diária de chão de fábrica e gestão de CLPs (Controladores Lógicos Programáveis) lida com desafios críticos:
1. **Fadiga de Alertas**: Excesso de alertas falsos de telemetria faz com que alertas críticos e reais sejam ignorados.
2. **Drift de Código (Código "Espaguete")**: Técnicos alteram o código *Structured Text* dos CLPs em campo (hotfix) e esquecem de versionar, causando acidentes e perda de rastreabilidade.
3. **Orçamentos Lentos**: Solicitações de peças em campo feitas via áudio de WhatsApp demoram dias para virarem orçamentos (Bill of Materials).

**A AltaCLP Intelligence resolve tudo isso usando IA:**
- 🧠 **Motor Preditivo (Threshold Engine)**: Calcula thresholds dinâmicos baseados no histórico real do cliente para ignorar falsos positivos.
- 🛡️ **GitOps Agent**: Monitora e compara o hash do código que está rodando no CLP físico com o repositório no Git. Se houver divergência, ele detecta, alerta e sugere um Pull Request reverso.
- 💬 **Orçamentador de IA + Comissionamento**: Transforma áudios e textos soltos dos técnicos em campo diretamente em orçamentos estruturados (BOM) usando IA. Ao aprovar, o orçamentador materializa automaticamente o projeto e a máquina física (CLP) no Kanban de Comissionamento para a Engenharia.
- 🔄 **Sincronização de Estado em Tempo Real (Kanban)**: O painel de acompanhamento sincroniza de forma transparente e instantânea (via polling) o progresso do projeto entre Vendedores (que criam) e a equipe de Engenharia (que visualiza e dá andamento) — com regras rígidas de RBAC (Role-Based Access Control) aplicadas em banco de dados.

---

## 🏗️ Arquitetura do Sistema

O projeto é dividido em duas frentes principais (Frontend e Backend), utilizando tecnologias modernas e de altíssima performance.

### 🌐 Frontend (React + Vite)
- **Framework**: React.js com Vite para build ultrarrápido.
- **Linguagem**: TypeScript para tipagem estática e segurança.
- **Estilização**: Tailwind CSS v4 para um design *Apple-inspired*, minimalista e responsivo.
- **Gerenciamento de Estado/Cache**: TanStack Query (React Query) para sincronização perfeita com a API.
- **Comunicação em Tempo Real**: Server-Sent Events (SSE) para receber telemetria dos CLPs ao vivo.

### ⚙️ Backend (FastAPI + Python)
- **Framework**: FastAPI (assíncrono, incrivelmente rápido e com documentação automática).
- **Linguagem**: Python 3.10+.
- **Banco de Dados**: Suporte para PostgreSQL (via Docker) com **Fallback Automático Inteligente** para SQLite local (zero-config).
- **ORM**: SQLAlchemy para modelagem do banco relacional.
- **Segurança**: Autenticação via JWT (JSON Web Tokens) e senhas hasheadas via `bcrypt`.

---

## 🚀 Como Rodar o Projeto (Passo a Passo)

A aplicação foi projetada para ter uma **experiência de desenvolvimento "Zero-Config"**. Se você não tiver o Docker ou o PostgreSQL instalado, o sistema vai automaticamente criar um banco de dados local (SQLite) e popular tudo sozinho!

### 1️⃣ Pré-requisitos
Certifique-se de ter instalado:
*   [Node.js](https://nodejs.org/) (Versão 18 ou superior)
*   [Python 3.10+](https://www.python.org/downloads/)

### 2️⃣ Rodando o Backend (API)
Abra um terminal na raiz do projeto e siga os passos:

```powershell
# 1. Crie o ambiente virtual Python (caso não exista)
python -m venv .venv

# 2. Instale as dependências (apenas na primeira vez)
.\.venv\Scripts\pip install -r requirements.txt

# 3. Ative o ambiente virtual Python
.\.venv\Scripts\Activate.ps1

# 4. Entre na pasta do backend
cd backend

# 5. Inicie o servidor
uvicorn main:app --reload
```
> **Mágica dos Dados Automáticos (Seed)**: Na primeira vez que você rodar o comando acima, o sistema detectará que o banco está vazio e **gerará automaticamente mais de 100.000 registros** simulados de telemetria, clientes, alertas e usuários. Isso leva de 30 a 60 segundos. Quando aparecer `[API] [OK] Plataforma pronta!`, está tudo certo!

*A API ficará disponível em:* **`http://localhost:8000`**
*Documentação automática Swagger em:* **`http://localhost:8000/docs`**

### 3️⃣ Rodando o Frontend (Painel Web)
Mantenha o terminal do backend rodando e abra um **novo terminal** na raiz do projeto:

```powershell
# 1. Entre na pasta do frontend
cd frontend

# 2. Instale as dependências (apenas na primeira vez)
npm install

# 3. Inicie o servidor de desenvolvimento
npm run dev
```

*O site ficará disponível em:* **`http://localhost:5173`** (ou a porta indicada no terminal).

---

## 🔒 Contas de Demonstração (Login)

Ao abrir o Frontend, você será recebido por uma tela de login. Use as contas abaixo para explorar diferentes visões da plataforma. Todas as contas possuem a senha padrão **`demo123`**:

| Usuário | E-mail | Perfil de Acesso |
| :--- | :--- | :--- |
| **Marcos Tedesco** | `marcos.tedesco@altaclp.com.br` | **CEO** (Focado em Visão Executiva, ROI, Custos de Falsos Alertas) |
| **Roberto CFO** | `roberto.cfo@altaclp.com.br` | **CFO** (Focado em Finanças, EBITDA e Valuation) |
| **Cláudia Santarém** | `claudia.eng@altaclp.com.br` | **Engenharia** (Focada em Máquinas, Gestão de Código GitOps) |
| **Anderson Vasconcellos** | `anderson.campo@altaclp.com.br` | **Técnico de Campo** (Focado em alertas, resolução de problemas no chão de fábrica) |
| **João Vendas** | `joao.vendas@altaclp.com.br` | **Vendas** (Focado no Assistente de Cotação de IA e BOMs) |

---

## 🤖 Integração com a Inteligência Artificial (Anthropic)
O backend possui um assistente de IA configurado para a API da Anthropic (Claude).
Para ativar a inteligência real:
1. Abra o arquivo `backend/.env`.
2. Insira sua chave da Anthropic em `ANTHROPIC_API_KEY=sk-ant-suachaveaqui`.

*Nota: Se a chave não for fornecida, o sistema usa graciosamente um **modo de simulação offline (fallback)** que gera respostas heurísticas, garantindo que o sistema nunca quebre na ausência de chaves de IA.*

---

## 🛠️ Solução de Problemas Comuns

- **Erro "Database is locked" (SQLite)**: Como o SQLite é um banco de dados em arquivo, rodar scripts externos enquanto a API está escrevendo dados pesados pode travá-lo. Basta apertar `Ctrl + C` para parar a API, esperar alguns segundos, e iniciá-la novamente.
- **Login diz "Credenciais Inválidas" na primeira execução**: Certifique-se de aguardar a mensagem `[API] [OK] Plataforma pronta!` no terminal do backend antes de tentar o login. O processo de "Seed" dos dados pode demorar quase 1 minuto na primeira execução.

---
Desenvolvido para revolucionar a automação industrial. 🚀
