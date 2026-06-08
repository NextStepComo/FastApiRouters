import psycopg2
from psycopg2.extras import RealDictCursor

connection = psycopg2.connect(
    database="nextStepDB",
    user="postgres",
    password="password",
    host="localhost",
    port=5432
)

cursor = connection.cursor(cursor_factory=RealDictCursor)

# Trova tutte le scuole che hanno lo stesso nome ma città diverse
SQLquery = """
    SELECT denominazione_sede_direttivo, comune_sede_di_direttivo
    FROM scuole
    WHERE denominazione_sede_direttivo IN (
        SELECT denominazione_sede_direttivo
        FROM scuole
        GROUP BY denominazione_sede_direttivo
        HAVING COUNT(DISTINCT comune_sede_di_direttivo) > 1
    )
    GROUP BY denominazione_sede_direttivo, comune_sede_di_direttivo;
"""

cursor.execute(SQLquery)
duplicati = cursor.fetchall()

print(f"Trovati {len(duplicati)} casi da aggiornare:")
for row in duplicati:
    nuovo_nome = f"{row['denominazione_sede_direttivo']} ({row['comune_sede_di_direttivo']})"
    print(f"  {row['denominazione_sede_direttivo']} → {nuovo_nome}")

    cursor.execute("""
        UPDATE scuole 
        SET denominazione_sede_direttivo = %s
        WHERE denominazione_sede_direttivo = %s 
        AND comune_sede_di_direttivo = %s;
    """, (nuovo_nome, row['denominazione_sede_direttivo'], row['comune_sede_di_direttivo']))

connection.commit()
cursor.close()
print("Aggiornamento completato!")