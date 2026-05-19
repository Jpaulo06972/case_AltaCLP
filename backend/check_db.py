import sqlite3
conn = sqlite3.connect('altaclp_db.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute('SELECT COUNT(*) as total FROM maquinas')
total = cur.fetchone()['total']
cur.execute('SELECT COUNT(*) as cnt FROM maquinas WHERE id_projeto IS NOT NULL')
with_proj = cur.fetchone()['cnt']
print(f'Total machines: {total}, with id_projeto: {with_proj}')

cur.execute('SELECT codigo, id_projeto FROM maquinas LIMIT 8')
for r in cur.fetchall():
    print(dict(r))

conn.close()
