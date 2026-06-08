# FastApiRouters

Backend for **NextStep** — a FastAPI-based web server providing authentication, quiz management, and Italian school data APIs.

## Table of Contents

- [Requirements](#requirements)
- [Setup](#setup)
- [Running the Server](#running-the-server)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
  - [Authentication](#authentication)
  - [Data Acquisition](#data-acquisition)
- [Database](#database)
- [Maintenance Scripts](#maintenance-scripts)
- [Development](#development)

---

## Requirements

- Python 3.10+
- PostgreSQL database named `nextStepDB` running on `localhost:5432`

---

## Setup

1. Clone the repository:

```bash
git clone https://github.com/NextStepComo/FastApiRouters.git
cd FastApiRouters
```

2. Activate the virtual environment:

```bash
source venv_FastApiRouters/bin/activate
```

3. Ensure the PostgreSQL database `nextStepDB` is available with the following tables:

- `usersDB` — user accounts
- `questions` — quiz questions
- `answers` — user quiz responses
- `scuole` — Italian school records (with `indirizzi_scolastici` JSONB column)

---

## Running the Server

```bash
fastapi dev --host 0.0.0.0
```

The API will be available at `http://0.0.0.0:8000`.

Interactive documentation (Swagger UI) is available at `http://0.0.0.0:8000/docs`.

---

## Project Structure

```
FastApiRouters/
├── main.py                              # FastAPI application entry point
├── hash_password.py                     # Password hashing utilities
├── routerOAuth2/                        # API routers package
│   ├── root_r.py                        # Aggregator router
│   ├── auth/                            # Authentication module
│   │   ├── router.py                    # Auth endpoints
│   │   ├── utils.py                     # JWT, DB, password utilities
│   │   └── model.py                     # Pydantic models
│   └── dataAcquisition/                 # Data acquisition module
│       ├── router.py                    # Data endpoints
│       ├── utils.py                     # DB query utilities
│       └── model.py                     # Pydantic models
├── aggiungi_nomi.py                     # Script: disambiguate school names
├── elimina_duplicate.py                 # Script: remove duplicate schools
├── indirizzi_particolari.py             # Script: manual address fixes
├── merge_scuole.py                      # Script: merge schools into JSONB
├── standard_indirizzi.py               # Script: normalize school types
└── README.md
```

---

## API Endpoints

### Authentication

All auth endpoints are prefixed with `/` (root-level).

| Method | Path                | Description                          |
|--------|---------------------|--------------------------------------|
| POST   | `/login`            | Authenticate user, return JWT tokens |
| POST   | `/register`         | Register a new user                  |
| POST   | `/refresh`          | Refresh expired access token         |
| GET    | `/users/me/`        | Get current user profile             |
| GET    | `/users/me/quiz`    | Get quiz completion status           |
| POST   | `/quizCompletato`   | Mark quiz as completed               |

#### `POST /login`

Authenticates a user with username and password.

- **Request body**: `application/x-www-form-urlencoded` with `username` and `password` fields (standard OAuth2 password flow).
- **Response**: `Token` object containing `access_token`, `refresh_token`, and `token_type`.

#### `POST /register`

Creates a new user account.

- **Request body**: JSON with `username`, `full_name`, `quizsolved`, `date_birth`, `password`.
- **Response**: `Token` object.

#### `POST /refresh`

Issues a new access/refresh token pair.

- **Request body**: JSON with `refresh_token` string.
- **Response**: New `Token` object.

#### `GET /users/me/`

Returns the authenticated user's profile. Requires a valid Bearer token.

- **Auth**: Bearer token (JWT access token).
- **Response**: `User` object with `userID`, `username`, `full_name`, `quizsolved`, `date_birth`.

#### `GET /users/me/quiz`

Returns the authenticated user's `quizsolved` status. Requires a valid Bearer token.

#### `POST /quizCompletato`

Marks the current user's quiz as completed (`quizsolved = true`). Requires a valid Bearer token.

---

### Data Acquisition

All data endpoints are prefixed with `/acquire`.

| Method | Path                                  | Description                    |
|--------|---------------------------------------|--------------------------------|
| POST   | `/acquire/quizResponses`              | Submit a quiz answer           |
| GET    | `/acquire/quizQuestions`              | Get a quiz question by ID      |
| GET    | `/acquire/scuolePosizione`            | Get schools by province        |

#### `POST /acquire/quizResponses`

Stores or updates a quiz answer.

- **Request body**: JSON with `userID` (int), `domanda` (int), `risposta` (int).
- **Response**: `{"status": "success"}`.

#### `GET /acquire/quizQuestions`

Fetches a single quiz question and its answers.

- **Query parameters**: `q` (int) — question ID.
- **Response**: Question data including associated answers.

#### `GET /acquire/scuolePosizione`

Fetches schools filtered by province.

- **Query parameters**: `provincia` (string) — province code. Use `XX` to return all schools.
- **Response**: List of schools with name, address, coordinates, contacts, and aggregated course offerings.

---

## Database

The application connects to a local PostgreSQL database (`nextStepDB`) with credentials:

- **Host**: `localhost:5432`
- **User**: `postgres`
- **Password**: `password`

### Key Tables

| Table       | Description                                  |
|-------------|----------------------------------------------|
| `usersDB`   | User accounts (`userid`, `username`, `full_name`, `hashed_password`, `quizsolved`, `date_birth`) |
| `questions` | Quiz questions (`q_id`, question text, answers) |
| `answers`   | User responses (`user_id`, `q_id`, `risp_id`) |
| `scuole`    | Italian school records with `indirizzi_scolastici` (JSONB) column storing an array of course offerings |

### Authentication Flow

1. User registers via `POST /register` — password is hashed with **Argon2** (via `pwdlib`) and stored in `usersDB`.
2. User logs in via `POST /login` — credentials are verified, and a JWT **access token** (30-minute expiry) and **refresh token** (7-day expiry) are returned.
3. Protected endpoints require the access token in the `Authorization: Bearer <token>` header.
4. When the access token expires, the client can use `POST /refresh` with the refresh token to obtain a new pair.

---

## Maintenance Scripts

Standalone Python scripts for database maintenance and data normalization. Each script connects directly to `nextStepDB` and performs a specific transformation.

| Script                    | Description                                                     |
|---------------------------|-----------------------------------------------------------------|
| `aggiungi_nomi.py`        | Disambiguates schools with identical names by appending the city name in parentheses |
| `elimina_duplicate.py`    | Removes duplicate school rows keeping only the first occurrence |
| `indirizzi_particolari.py`| Applies manual address name normalizations (e.g., `L. Sportivo` → `L. Scientifico ad indirizzo Sportivo`) |
| `merge_scuole.py`         | Groups schools by physical location and aggregates course offerings into a JSONB array (`indirizzi_scolastici`) |
| `standard_indirizzi.py`   | Normalizes school type abbreviations (e.g., `L. Scient` → `L. Scientifico`, `I.P. Agr` → `I.P. Agrario`) |

### Usage

Activate the virtual environment and run any script directly:

```bash
source venv_FastApiRouters/bin/activate
python merge_scuole.py
```

---

## Development

### Adding New Endpoints

1. Create or extend a router module under `routerOAuth2/`.
2. Define Pydantic models in `model.py`.
3. Implement database utilities in `utils.py`.
4. Register the router in `root_r.py`.

### Dependencies

The virtual environment (`venv_FastApiRouters/`) contains all required packages, including:

- **FastAPI** — web framework
- **Uvicorn** — ASGI server
- **PyJWT** — JWT encoding/decoding
- **psycopg2-binary** — PostgreSQL adapter
- **pwdlib** — password hashing (Argon2)
- **python-multipart** — form data parsing
- **email-validator** — email validation
- **python-dotenv** — environment variable support
