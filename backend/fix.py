import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'altaclp_db.db')
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("UPDATE alertas SET severidade = 'aviso' WHERE severidade = 'alto';")
conn.commit()
conn.close()
print('Fixed enum in db.')
