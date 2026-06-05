import json
import re
from collections import defaultdict

import psycopg2
import psycopg2.extras  # per RealDictCursor

# ─────────────────────────────────────────────
# CONFIGURAZIONE
# ─────────────────────────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "nextStepDB",       # ← cambia
    "user":     "postgres",        # ← cambia
    "password": "password",      # ← cambia
}


SOURCE_TABLE = "scuole"
DEST_TABLE   = "scuole_merged"

# Chiave che identifica la stessa sede fisica
GROUP_KEY = ("denominazione_sede_direttivo", "indirizzo", "comune")

# Campi che vanno dentro il JSON per ogni indirizzo
FIELDS_IN_JSON = [
    "organico_autonomia",
    "organico_sede",
    "num_sedi_autonomia",
    "macrotipologia_autonomia",
    "tipologia_autonomia",
    "tipologia_sede",
    "telefono_sede_autonomia",
]

# ─────────────────────────────────────────────
# UTILITY
# ─────────────────────────────────────────────

def estrai_indirizzo(denominazione: str, nome_scuola: str) -> str:
    if not denominazione:
        return denominazione or ""

    if nome_scuola:
        pattern = re.compile(
            r"\s*-\s*" + re.escape(nome_scuola.strip()) + r"\s*$",
            re.IGNORECASE
        )
        cleaned = pattern.sub("", denominazione).strip()
        if cleaned != denominazione.strip():
            return cleaned

    idx = denominazione.rfind(" - ")
    if idx != -1:
        return denominazione[:idx].strip()

    return denominazione.strip()


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # Leggi tutte le righe
    cur.execute(f"SELECT * FROM {SOURCE_TABLE}")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]

    print(f"Righe lette: {len(rows)}")

    # ── Raggruppa per sede fisica ──────────────────────────────────────────────
    groups = defaultdict(list)
    for row in rows:
        key = tuple(
            (row[k] or "").strip().upper()
            for k in GROUP_KEY
        )
        groups[key].append(dict(row))

    print(f"Sedi uniche trovate: {len(groups)}")

    # ── Costruisci righe merged ────────────────────────────────────────────────
    merged_rows = []

    for key, same_sede in groups.items():
        base = dict(same_sede[0])
        nome_scuola = (base.get("denominazione_sede_direttivo") or "").strip()

        indirizzi_list = []
        seen = set()
        for r in same_sede:
            den = (r.get("denominazione") or "").strip()
            nome_indirizzo = estrai_indirizzo(den, nome_scuola)

            k = nome_indirizzo.upper()
            if k not in seen:
                seen.add(k)
                entry = {"indirizzo_scolastico": nome_indirizzo}
                for field in FIELDS_IN_JSON:
                    entry[field] = r.get(field, "")
                indirizzi_list.append(entry)

        # In PostgreSQL il campo è JSONB nativo — passiamo Json() wrapper
        base["indirizzi_scolastici"] = json.dumps(indirizzi_list, ensure_ascii=False)
        base["denominazione"] = nome_scuola

        merged_rows.append(base)

    # ── Crea la tabella destinazione ──────────────────────────────────────────
    # Usa un cursore normale (non RealDict) per DDL/DML
    cur2 = conn.cursor()

    cur2.execute(f"DROP TABLE IF EXISTS {DEST_TABLE}")

    # Tutte le colonne originali come TEXT + indirizzi_scolastici come JSONB
    col_defs = ", ".join(f'"{c}" TEXT' for c in columns)
    col_defs += ', "indirizzi_scolastici" JSONB'

    cur2.execute(f'CREATE TABLE {DEST_TABLE} ({col_defs})')

    # ── Inserisci ─────────────────────────────────────────────────────────────
    new_cols = columns + ["indirizzi_scolastici"]
    placeholders = ", ".join(f"%s" for _ in new_cols)
    insert_sql = f'INSERT INTO {DEST_TABLE} ({", ".join(f"{chr(34)}{c}{chr(34)}" for c in new_cols)}) VALUES ({placeholders})'

    for r in merged_rows:
        values = []
        for c in new_cols:
            val = r.get(c, "")
            # Il campo JSONB va passato come stringa JSON a psycopg2
            if c == "indirizzi_scolastici":
                values.append(psycopg2.extras.Json(json.loads(val)))
            else:
                values.append(val)
        cur2.execute(insert_sql, values)

    conn.commit()
    cur.close()
    cur2.close()
    conn.close()

    print(f"\n✅ Tabella '{DEST_TABLE}' creata con {len(merged_rows)} righe.")
    print("\nEsempio struttura JSON campo 'indirizzi_scolastici':")
    example = json.loads(merged_rows[0]["indirizzi_scolastici"])
    print(json.dumps(example, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()