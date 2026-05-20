import sqlite3

def cleanup():
    conn = sqlite3.connect('altaclp_db.db')
    cur = conn.cursor()

    # Verify initial count
    cur.execute('''
        SELECT COUNT(*) FROM comissionamentos 
        JOIN maquinas ON comissionamentos.maquina_id = maquinas.id 
        WHERE maquinas.id_projeto IS NULL
    ''')
    to_delete = cur.fetchone()[0]
    print(f"Found {to_delete} seeded/static comissionamentos with no project.")

    if to_delete > 0:
        # Delete comissionamentos with no project
        cur.execute('''
            DELETE FROM comissionamentos 
            WHERE maquina_id IN (SELECT id FROM maquinas WHERE id_projeto IS NULL)
        ''')
        deleted = cur.rowcount
        print(f"Successfully deleted {deleted} static comissionamentos.")

        # Clean up related Project Pendencies that might be linked to deleted comissionamentos
        cur.execute('''
            DELETE FROM projeto_pendencias 
            WHERE comissionamento_id IS NOT NULL AND comissionamento_id NOT IN (SELECT id FROM comissionamentos)
        ''')
        deleted_pendencias = cur.rowcount
        print(f"Cleaned up {deleted_pendencias} orphaned project pendencies.")

        # Clean up related Project History that might be linked to deleted comissionamentos
        cur.execute('''
            DELETE FROM projeto_historico 
            WHERE comissionamento_id IS NOT NULL AND comissionamento_id NOT IN (SELECT id FROM comissionamentos)
        ''')
        deleted_history = cur.rowcount
        print(f"Cleaned up {deleted_history} orphaned project history logs.")

    conn.commit()
    conn.close()
    print("Database cleanup completed.")

if __name__ == "__main__":
    cleanup()
