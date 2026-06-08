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

# Trova e rimuove i duplicati mantenendo solo la riga con il ctid più basso (la prima inserita)
SQLquery = """
    DELETE FROM scuole
    WHERE ctid NOT IN (
        SELECT MIN(ctid)
        FROM scuole
        GROUP BY denominazione_sede_direttivo
    );
"""

cursor.execute(SQLquery)
deleted = cursor.rowcount
connection.commit()
cursor.close()

print(f"Eliminate {deleted} righe duplicate.")