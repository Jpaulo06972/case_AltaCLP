"""
Script de emergência: cria usuários diretamente via sqlite3 nativo.
Sem dependências externas problemáticas.
"""
import sqlite3
import uuid
import bcrypt
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "altaclp_db.db")

# Gera hash bcrypt diretamente (sem passlib)
senha = b"demo123"
senha_hash = bcrypt.hashpw(senha, bcrypt.gensalt()).decode("utf-8")

USERS = [
    (str(uuid.uuid4()), "Marcos Tedesco",        "marcos.tedesco@altaclp.com.br", senha_hash, "ceo"),
    (str(uuid.uuid4()), "Roberto CFO",           "roberto.cfo@altaclp.com.br",    senha_hash, "cfo"),
    (str(uuid.uuid4()), "Cláudia Santarém",      "claudia.eng@altaclp.com.br",    senha_hash, "engenharia"),
    (str(uuid.uuid4()), "Anderson Vasconcellos", "anderson.campo@altaclp.com.br", senha_hash, "tecnico_campo"),
]

con = sqlite3.connect(DB_PATH, timeout=10)
cur = con.cursor()

# Cria a tabela se não existir
cur.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id TEXT PRIMARY KEY,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha_hash TEXT NOT NULL,
        perfil TEXT NOT NULL,
        ativo INTEGER DEFAULT 1,
        ultimo_acesso TEXT
    )
""")

created = 0
for uid, nome, email, hsh, perfil in USERS:
    existing = cur.execute("SELECT id FROM usuarios WHERE email = ?", (email,)).fetchone()
    if existing:
        print(f"  [SKIP] {email} já existe.")
        continue
    cur.execute(
        "INSERT INTO usuarios (id, nome, email, senha_hash, perfil, ativo) VALUES (?, ?, ?, ?, ?, 1)",
        (uid, nome, email, hsh, perfil)
    )
    created += 1
    print(f"  [OK] Criado: {email}")

con.commit()
con.close()
print(f"\n[OK] {created} usuário(s) criado(s). Senha: demo123")
