"""
Patch script — assigns all unlinked maquinas to a Projeto round-robin.
Safe to re-run: only updates rows where id_projeto IS NULL.
"""
import sqlite3

conn = sqlite3.connect('altaclp_db.db')
cur = conn.cursor()

# Get all project IDs
cur.execute("SELECT id FROM projetos ORDER BY id")
projeto_ids = [r[0] for r in cur.fetchall()]

if not projeto_ids:
    print("ERROR: No projects found in DB. Run seed_commissioning.py first.")
    exit(1)

# Get machines without a project
cur.execute("SELECT id, codigo FROM maquinas WHERE id_projeto IS NULL ORDER BY codigo")
machines = cur.fetchall()

print(f"Found {len(machines)} unlinked machines. Distributing across {len(projeto_ids)} projects...")

for i, (maq_id, codigo) in enumerate(machines):
    proj_id = projeto_ids[i % len(projeto_ids)]
    cur.execute("UPDATE maquinas SET id_projeto = ? WHERE id = ?", (proj_id, maq_id))
    print(f"  {codigo} -> {proj_id}")

conn.commit()
conn.close()
print("Done! All machines now linked to projects.")
