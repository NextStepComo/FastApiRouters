import psycopg2
from psycopg2.extras import RealDictCursor
import re

connection = psycopg2.connect(
    database="nextStepDB",
    user="postgres",
    password="password",
    host="localhost",
    port=5432
)

NORMALIZZAZIONE = {
    r"I\.?\s*P\.?\s*Serv.*Ind.*Artig": "I.P. Servizi e Industria e Artigianato",
    r"I\.?\s*P\.?\s*Agri": "I.P. Agrario",
    r"I\.?\s*P\.?\s*Econom": "I.P. Economico",
    r"I\.?\s*P\.?\s*Ind.*Artig": "I.P. Industria e Artigianato",
    r"I\.?\s*P\.?\s*Serv": "I.P. Servizi",
    r"I\.?\s*P\.?\s*e\s*L\.?": "I.P. e Liceo",
    r"I\.?\s*P\.?\s*Serale": "I.P. Serale",
    r"I\.?\s*P\.?\s*San Pelleg": "I.P. San Pellegrino Terme",
    r"^I\.?\s*P\.?$": "I.P.",
    r"I\.?\s*T\.?\s*Agr": "I.T. Agrario",
    r"I\.?\s*T\.?\s*Econ.*Tecn": "I.T. Economico e Tecnologico",
    r"I\.?\s*T\.?\s*Tecn.*Econ": "I.T. Economico e Tecnologico",
    r"I\.?\s*T\.?\s*Econ": "I.T. Economico",
    r"I\.?\s*T\.?\s*Tecn": "I.T. Tecnologico",
    r"I\.?\s*T\.?\s*Vanoni": "I.T. Vanoni",
    r"^I\.?\s*T\.?$": "I.T.",
    r"L\.?\s*Artist": "L. Artistico",
    r"L\.?\s*Class": "L. Classico",
    r"L\.?\s*[Ll]ingui": "L. Linguistico",
    r"L\.?\s*Music.*Coreutic": "L. Musicale e Coreutico",
    r"Liceo\s*Music.*Coreutic": "L. Musicale e Coreutico",
    r"L\.?\s*Music": "L. Musicale",
    r"L\.?\s*Scient.*Sport": "L. Scientifico ad indirizzo Sportivo",
    r"Liceo\s*Scient.*Sport": "L. Scientifico ad indirizzo Sportivo",
    r"L\.?\s*Scient.*Appl": "L. Scientifico Scienze Applicate",
    r"L\.?\s*Scient": "L. Scientifico",
    r"Liceo\s*Scient": "L. Scientifico",
    r"L\s*Scient": "L. Scientifico",
    r"L\.?\s*Scienze\s*[Uu]mane": "L. Scienze Umane",
    r"Liceo\s*Scienze\s*[Uu]mane": "L. Scienze Umane",
    r"L\.?\s*Sport": "L. Sportivo",
    r"Liceo\s*Sport": "L. Sportivo",
    r"^Liceo$": "Liceo",
}

ORDINE = [
    r"I\.?\s*P\.?\s*Serv.*Ind.*Artig",
    r"I\.?\s*P\.?\s*Agri",
    r"I\.?\s*P\.?\s*Econom",
    r"I\.?\s*P\.?\s*Ind.*Artig",
    r"I\.?\s*P\.?\s*Serv",
    r"I\.?\s*P\.?\s*e\s*L\.?",
    r"I\.?\s*P\.?\s*Serale",
    r"I\.?\s*P\.?\s*San Pelleg",
    r"^I\.?\s*P\.?$",
    r"I\.?\s*T\.?\s*Agr",
    r"I\.?\s*T\.?\s*Econ.*Tecn",
    r"I\.?\s*T\.?\s*Tecn.*Econ",
    r"I\.?\s*T\.?\s*Econ",
    r"I\.?\s*T\.?\s*Tecn",
    r"I\.?\s*T\.?\s*Vanoni",
    r"^I\.?\s*T\.?$",
    r"L\.?\s*Artist",
    r"L\.?\s*Class",
    r"L\.?\s*[Ll]ingui",
    r"L\.?\s*Music.*Coreutic",
    r"Liceo\s*Music.*Coreutic",
    r"L\.?\s*Music",
    r"L\.?\s*Scient.*Sport",
    r"Liceo\s*Scient.*Sport",
    r"L\.?\s*Scient.*Appl",
    r"L\.?\s*Scient",
    r"Liceo\s*Scient",
    r"L\s*Scient",
    r"L\.?\s*Scienze\s*[Uu]mane",
    r"Liceo\s*Scienze\s*[Uu]mane",
    r"L\.?\s*Sport",
    r"Liceo\s*Sport",
    r"^Liceo$",
]

def normalizza(indirizzo: str) -> str:
    if not indirizzo:
        return indirizzo
    indirizzo_clean = indirizzo.strip()
    for pattern in ORDINE:
        if re.search(pattern, indirizzo_clean, re.IGNORECASE):
            return NORMALIZZAZIONE[pattern]
    return indirizzo_clean

cursor = connection.cursor(cursor_factory=RealDictCursor)

# Leggi tutti gli indirizzi distinti dal JSON
cursor.execute("""
    SELECT DISTINCT elem->>'indirizzo_scolastico' as indirizzo_scolastico
    FROM scuole,
        jsonb_array_elements(indirizzi_scolastici::jsonb) as elem
    WHERE elem->>'indirizzo_scolastico' IS NOT NULL
    AND elem->>'indirizzo_scolastico' != '';
""")
indirizzi = cursor.fetchall()

print(f"Trovati {len(indirizzi)} indirizzi distinti\n")

# Preview
print("=== PREVIEW ===")
modifiche = {}
non_modificati = []
for row in indirizzi:
    originale = row["indirizzo_scolastico"]
    normalizzato = normalizza(originale)
    if originale != normalizzato:
        modifiche[originale] = normalizzato
        print(f"  '{originale}' → '{normalizzato}'")
    else:
        non_modificati.append(originale)

print(f"\n{len(modifiche)} indirizzi verranno modificati")
print(f"{len(non_modificati)} indirizzi rimarranno invariati")

if non_modificati:
    print("\n=== NON MODIFICATI (controlla manualmente) ===")
    for i in non_modificati:
        print(f"  '{i}'")

conferma = input("\nProcedere con l'aggiornamento? (s/n): ")

if conferma.lower() == "s":
    count = 0
    for originale, normalizzato in modifiche.items():
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
        count += cursor.rowcount

    connection.commit()
    print(f"\n✅ Aggiornate {count} righe!")
else:
    print("Operazione annullata.")

cursor.close()
connection.close()