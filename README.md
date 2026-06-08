# FastApiRouters

Backend di **NextStep** — server web basato su FastAPI per autenticazione, gestione quiz e API sui dati delle scuole italiane.

## Indice

- [Requisiti](#requisiti)
- [Setup](#setup)
- [Avvio del Server](#avvio-del-server)
- [Struttura del Progetto](#struttura-del-progetto)
- [API Endpoints](#api-endpoints)
  - [Autenticazione](#autenticazione)
  - [Acquisizione Dati](#acquisizione-dati)
  - [Chat AI](#chat-ai)
- [Database](#database)
- [Script di Manutenzione](#script-di-manutenzione)
- [Sviluppo](#sviluppo)

---

## Requisiti

- Python 3.10+
- Database PostgreSQL `nextStepDB` su `localhost:5432`
- Ollama con modello `gemma4:e2b` (per l'endpoint chat)

---

## Setup

1. Clona il repository:

```bash
git clone https://github.com/NextStepComo/FastApiRouters.git
cd FastApiRouters
```

2. Attiva l'ambiente virtuale:

```bash
source venv_FastApiRouters/bin/activate
```

3. Assicurati che il database PostgreSQL `nextStepDB` sia disponibile con le seguenti tabelle:

- `usersDB` — account utenti
- `questions` — domande del quiz
- `answers` — risposte degli utenti
- `scuole` — dati delle scuole italiane (con colonna JSONB `indirizzi_scolastici`)

4. Per la funzionalità chat AI, installa [Ollama](https://ollama.ai/) e scarica il modello:

```bash
ollama pull gemma4:e2b
```

---

## Avvio del Server

```bash
fastapi dev --host 0.0.0.0
```

L'API sarà disponibile su `http://0.0.0.0:8000`.

Documentazione interattiva (Swagger UI): `http://0.0.0.0:8000/docs`.

---

## Struttura del Progetto

```
FastApiRouters/
├── main.py                              # Punto di ingresso FastAPI
├── hash_password.py                     # Utility per hashing password
├── chiamata_ollama.py                   # Script standalone per testare Ollama
├── routerOAuth2/                        # Package router API
│   ├── root_r.py                        # Router aggregatore
│   ├── auth/                            # Modulo autenticazione
│   │   ├── router.py                    # Endpoint auth
│   │   ├── utils.py                     # Utility JWT, DB, password
│   │   └── model.py                     # Modelli Pydantic
│   └── dataAcquisition/                 # Modulo acquisizione dati
│       ├── router.py                    # Endpoint dati e chat AI
│       ├── utils.py                     # Utility query DB e chiamate Ollama
│       └── model.py                     # Modelli Pydantic
├── aggiungi_nomi.py                     # Script: disambiguazione nomi scuole
├── elimina_duplicate.py                 # Script: rimozione duplicati
├── indirizzi_particolari.py             # Script: correzioni manuali indirizzi
├── merge_scuole.py                      # Script: merge scuole in JSONB
├── standard_indirizzi.py               # Script: normalizzazione tipi scuola
└── README.md
```

---

## API Endpoints

### Autenticazione

Tutti gli endpoint di autenticazione sono prefissati con `/`.

| Metodo | Path                | Descrizione                              |
|--------|---------------------|------------------------------------------|
| POST   | `/login`            | Autentica utente, restituisce token JWT  |
| POST   | `/register`         | Registra un nuovo utente                 |
| POST   | `/refresh`          | Rinnova il token di accesso scaduto      |
| GET    | `/users/me/`        | Ottiene il profilo dell'utente corrente  |
| GET    | `/users/me/quiz`    | Ottiene lo stato di completamento quiz   |
| POST   | `/quizCompletato`   | Segna il quiz come completato            |

#### `POST /login`

Autentica un utente con username e password.

- **Corpo richiesta**: `application/x-www-form-urlencoded` con campi `username` e `password` (flusso OAuth2 standard).
- **Risposta**: Oggetto `Token` con `access_token`, `refresh_token`, `token_type`.

#### `POST /register`

Crea un nuovo account utente.

- **Corpo richiesta**: JSON con `username`, `full_name`, `quizsolved`, `date_birth`, `password`.
- **Risposta**: Oggetto `Token`.

#### `POST /refresh`

Emette una nuova coppia di token di accesso e refresh.

- **Corpo richiesta**: JSON con campo `refresh_token`.
- **Risposta**: Nuovo oggetto `Token`.

#### `GET /users/me/`

Restituisce il profilo dell'utente autenticato. Richiede token Bearer valido.

- **Auth**: Bearer token (JWT access token).
- **Risposta**: Oggetto `User` con `userID`, `username`, `full_name`, `quizsolved`, `date_birth`.

#### `GET /users/me/quiz`

Restituisce il campo `quizsolved` dell'utente autenticato. Richiede token Bearer valido.

#### `POST /quizCompletato`

Imposta `quizsolved = true` per l'utente corrente. Richiede token Bearer valido.

---

### Acquisizione Dati

Tutti gli endpoint di acquisizione dati sono prefissati con `/acquire`.

| Metodo | Path                                  | Descrizione                            |
|--------|---------------------------------------|----------------------------------------|
| POST   | `/acquire/quizResponses`              | Invia una risposta al quiz             |
| GET    | `/acquire/quizQuestions`              | Ottiene una domanda del quiz per ID    |
| GET    | `/acquire/scuolePosizione`            | Ottiene le scuole per provincia        |

#### `POST /acquire/quizResponses`

Salva o aggiorna una risposta al quiz.

- **Corpo richiesta**: JSON con `userID` (int), `domanda` (int), `risposta` (int).
- **Risposta**: `{"status": "success"}`.

#### `GET /acquire/quizQuestions`

Recupera una domanda del quiz con le relative risposte.

- **Parametri query**: `q` (int) — ID della domanda.
- **Risposta**: Dati della domanda incluse le risposte associate.

#### `GET /acquire/scuolePosizione`

Recupera le scuole filtrate per provincia.

- **Parametri query**: `provincia` (string) — codice provincia. Usa `XX` per ottenere tutte le scuole.
- **Risposta**: Elenco di scuole con nome, indirizzo, coordinate, contatti e corsi aggregati.

---

### Chat AI

| Metodo | Path                | Descrizione                              |
|--------|---------------------|------------------------------------------|
| POST   | `/acquire/chat`     | Invia un messaggio all'assistente AI     |

#### `POST /acquire/chat`

Invia un messaggio testuale al modello AI locale (Gemma 4 tramite Ollama) e riceve una risposta.

- **Corpo richiesta**: JSON con `inputText` (string) — il messaggio dell'utente.
- **Risposta**: Testo della risposta generata dal modello AI.
- **Ruolo sistema**: L'assistente AI è configurato come supporto all'orientamento scolastico per studenti delle medie, rispondendo in italiano in modo conciso e semplice.
- **Modello**: `gemma4:e2b` con temperatura 0.7 e top_p 0.9.

---

## Database

L'applicazione si connette a un database PostgreSQL locale (`nextStepDB`) con le seguenti credenziali:

- **Host**: `localhost:5432`
- **Utente**: `postgres`
- **Password**: `password`

### Tabelle Principali

| Tabella     | Descrizione                                                      |
|-------------|------------------------------------------------------------------|
| `usersDB`   | Account utenti (`userid`, `username`, `full_name`, `hashed_password`, `quizsolved`, `date_birth`) |
| `questions` | Domande del quiz (`q_id`, testo domanda, risposte)               |
| `answers`   | Risposte degli utenti (`user_id`, `q_id`, `risp_id`)             |
| `scuole`    | Record delle scuole italiane con colonna `indirizzi_scolastici` (JSONB) contenente un array di offerte formative |

### Flusso di Autenticazione

1. L'utente si registra tramite `POST /register` — la password viene hashata con **Argon2** (tramite `pwdlib`) e salvata in `usersDB`.
2. L'utente effettua il login tramite `POST /login` — le credenziali vengono verificate e vengono restituiti un **access token** JWT (scadenza 30 minuti) e un **refresh token** (scadenza 7 giorni).
3. Gli endpoint protetti richiedono l'access token nell'header `Authorization: Bearer <token>`.
4. Quando l'access token scade, il client può usare `POST /refresh` con il refresh token per ottenere una nuova coppia.

---

## Script di Manutenzione

Script Python standalone per la manutenzione e normalizzazione del database. Ogni script si connette direttamente a `nextStepDB` ed esegue una trasformazione specifica.

| Script                    | Descrizione                                                           |
|---------------------------|-----------------------------------------------------------------------|
| `aggiungi_nomi.py`        | Disambigua scuole con nomi identici aggiungendo il comune tra parentesi |
| `elimina_duplicate.py`    | Rimuove righe duplicate dalla tabella `scuole` mantenendo la prima occorrenza |
| `indirizzi_particolari.py`| Applica normalizzazioni manuali ai nomi degli indirizzi (es. `L. Sportivo` → `L. Scientifico ad indirizzo Sportivo`) |
| `merge_scuole.py`         | Raggruppa scuole per sede fisica e aggrega le offerte formative in un array JSONB (`indirizzi_scolastici`) |
| `standard_indirizzi.py`   | Normalizza le abbreviazioni dei tipi di scuola (es. `L. Scient` → `L. Scientifico`, `I.P. Agr` → `I.P. Agrario`) |
| `chiamata_ollama.py`      | Script di test per verificare il funzionamento di Ollama con il modello Gemma 4 |

### Utilizzo

Attiva l'ambiente virtuale ed esegui qualsiasi script direttamente:

```bash
source venv_FastApiRouters/bin/activate
python merge_scuole.py
```

---

## Sviluppo

### Aggiungere Nuovi Endpoint

1. Crea o estendi un modulo router sotto `routerOAuth2/`.
2. Definisci i modelli Pydantic in `model.py`.
3. Implementa le utility per il database in `utils.py`.
4. Registra il router in `root_r.py`.

### Dipendenze

L'ambiente virtuale (`venv_FastApiRouters/`) contiene tutti i pacchetti richiesti, inclusi:

- **FastAPI** — framework web
- **Uvicorn** — server ASGI
- **PyJWT** — codifica/decodifica JWT
- **psycopg2-binary** — adapter PostgreSQL
- **pwdlib** — hashing password (Argon2)
- **python-multipart** — parsing form data
- **email-validator** — validazione email
- **ollama** — client Python per Ollama
- **python-dotenv** — supporto file di ambiente
