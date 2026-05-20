# Deploy no Vercel — Login e variáveis de ambiente

Este projeto **não usa NextAuth**. A autenticação é **JWT (FastAPI)** + **localStorage** no frontend React/Vite.

## Por que o login falha no Vercel (causas mais comuns)

| Causa | Sintoma | Correção |
|-------|---------|----------|
| `VITE_API_URL` apontando para `localhost` | Network error / login sempre falha | Definir env no Vercel ou usar fallback `/_backend/api/v1` (já no código) |
| Rewrite SPA engolindo `/_backend` | 404 HTML no POST `/auth/login` | `vercel.json` exclui `_backend` do fallback |
| Banco vazio no serverless | 401 "Credenciais inválidas" com senha correta | PostgreSQL (Neon/Vercel Postgres) + rodar seed uma vez |
| `CORS_ORIGINS` sem domínio Vercel | Erro de CORS no browser | `ENVIRONMENT=production` + CORS ou deixar auto (`VERCEL_URL`) |
| `SECRET_KEY` diferente entre deploys | Login OK, depois 401 em `/me` | Mesma `SECRET_KEY` em todos os deploys |

**Não se aplica aqui:** `NEXTAUTH_URL`, `NEXTAUTH_SECRET`, OAuth callbacks.

## Variáveis no painel Vercel

### Frontend (Build)
| Variável | Valor sugerido |
|----------|----------------|
| `VITE_API_URL` | *(vazio)* se backend no mesmo projeto — usa `/_backend/api/v1` |

Se o backend estiver em outro host (Railway, Render):
```
VITE_API_URL=https://sua-api.exemplo.com/api/v1
```

### Backend (Runtime)
| Variável | Obrigatório | Exemplo |
|----------|-------------|---------|
| `DATABASE_URL` | Sim (produção) | `postgresql://user:pass@host/db` |
| `SECRET_KEY` | Sim | string ≥ 32 caracteres |
| `ENVIRONMENT` | Sim | `production` |
| `CORS_ORIGINS` | Opcional | `https://seu-app.vercel.app` |

SQLite **não é confiável** no Vercel (filesystem efêmero). Use Postgres.

## Popular usuários de demo (uma vez)

Com `DATABASE_URL` configurado, rode localmente apontando para o mesmo banco:

```bash
cd backend
source .venv/bin/activate
export DATABASE_URL="postgresql://..."
python -c "from database.seed import run_seed; run_seed()"
```

Contas: senha `demo123` — ver README (ex.: `joao.vendas@altaclp.com.br`).

## Confirmar o fix

1. **Redeploy** após alterar env vars (Vite embute `VITE_*` no build).
2. DevTools → Network → `POST .../auth/login`:
   - **200** + `access_token` → login OK
   - **401** + `CREDENCIAIS_INVALIDAS` → API OK, usuário/senha ou DB vazio
   - **404 HTML** → rewrite/API URL errada
   - **CORS blocked** → ajustar `CORS_ORIGINS` / `ENVIRONMENT`
3. Vercel → **Logs** do serviço `backend`: `[ROUTE HIT] POST /api/v1/auth/login`

## Teste rápido (curl)

```bash
curl -X POST "https://SEU-DOMINIO.vercel.app/_backend/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"joao.vendas@altaclp.com.br","senha":"demo123"}'
```

Resposta esperada: JSON com `access_token`, `perfil`, `nome`.
