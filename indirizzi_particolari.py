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

modifiche_manuali = {
    'L. Sportivo': 'L. Scientifico ad indirizzo Sportivo'
}

for originale, normalizzato in modifiche_manuali.items():
    cursor.execute("""
        UPDATE scuole
        SET indirizzi_scolastici = (
            SELECT jsonb_agg(
                CASE 
                    WHEN elem->>'indirizzo_scolastico' = %s 
                    THEN jsonb_set(elem, '{indirizzo_scolastico}', to_jsonb(%s::text))
                    ELSE elem
                END
            )
            FROM jsonb_array_elements(indirizzi_scolastici::jsonb) as elem
        )
        WHERE indirizzi_scolastici::text LIKE %s;
    """, (originale, normalizzato, f'%{originale}%'))
    print(f"'{originale}' → '{normalizzato}' ({cursor.rowcount} righe)")

connection.commit()
print("\n✅ Fatto!")
cursor.close()
connection.close()