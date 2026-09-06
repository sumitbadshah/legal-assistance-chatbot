# AI Legal Assistance — Backend

A real, deployable FastAPI backend for the AI legal assistance platform: JWT auth,
PostgreSQL, RAG-grounded legal Q&A, document drafting, case search, and feedback —
matching `API_SPEC.md` and `DATABASE_SCHEMA.md`.

## What's actually implemented

- **Auth**: register/login with bcrypt-hashed passwords, JWT bearer tokens.
- **Chat**: `POST /chat` retrieves relevant legal source chunks (TF-IDF search
  over the `documents` table), sends them to Claude as grounding context, and
  saves the full conversation per user.
- **Document search**: `GET /documents/search`, `POST /documents/upload` to
  extend the legal corpus.
- **Drafting**: `POST /draft/generate` — accepts *any* document type as free
  text (not a fixed list), generates a plain-text draft with a
  "have a lawyer review this" notice baked in, saves it per user.
- **Case search**: `GET /cases/search` — simple keyword search over a small
  seeded case table.
- **Feedback**: `POST /feedback` — thumbs up/down tied to a message.
- **Persistence**: every table from `DATABASE_SCHEMA.md` (users, chats,
  messages, documents, embeddings, cases, generated_documents, feedback,
  search_history) as real Postgres tables via SQLAlchemy.

## What's intentionally simplified (and how to upgrade it)

- **Retrieval** is TF-IDF cosine similarity, not neural embeddings — it
  deploys anywhere with no extra API cost or GPU. Swap `app/rag/retriever.py`
  for pgvector + a real embedding model (OpenAI/Cohere/local) when you need
  semantic (not just keyword) matching at scale. The public interface
  (`retrieve(query, k)`) is designed to stay the same.
- **Legal corpus** is ~26 seeded Act/Section snippets in `app/seed_data.py` —
  illustrative, not the full text of Indian law. Real ingestion (PDF parsing
  of full Acts/judgments, chunking) is the next real piece of work.
- **Migrations**: tables are created via `Base.metadata.create_all` on
  startup, fine for getting started. Before you have real users, switch to
  Alembic migrations so schema changes don't require dropping data.
- **LLM provider**: uses the Anthropic API directly (`app/llm/client.py`).
  Your original docs assumed OpenAI GPT — swap the client if you'd rather
  use OpenAI; the rest of the app doesn't care which provider `complete()`
  calls.

## Run it locally (Docker — recommended)

```bash
cp .env.example .env
# edit .env and set a real ANTHROPIC_API_KEY

docker compose up --build
```

The API is now at `http://localhost:8000`. Interactive docs at
`http://localhost:8000/docs`.

## Run it locally (without Docker)

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# start a local Postgres however you like, then:
cp .env.example .env
# edit .env: DATABASE_URL, ANTHROPIC_API_KEY

uvicorn app.main:app --reload
```

## Run the tests

```bash
pip install pytest httpx
python -m pytest tests/ -v
```

(Tests run against SQLite automatically — no Postgres needed for these.)

## Deploying it for real

This is a standard containerized FastAPI + Postgres app, so any of these work:

**Railway / Render (simplest)**
1. Push this folder to a GitHub repo.
2. Create a new Web Service from the repo — both platforms auto-detect the
   `Dockerfile`.
3. Add a managed Postgres instance (both platforms offer one in a couple of
   clicks) and set `DATABASE_URL` to its connection string.
4. Set `SECRET_KEY`, `ANTHROPIC_API_KEY`, and `ALLOWED_ORIGINS` (your
   frontend's real URL) as environment variables.
5. Deploy. Health check: `GET /health`.

**Fly.io**
```bash
fly launch          # detects the Dockerfile
fly postgres create # attach a Postgres cluster
fly secrets set SECRET_KEY=... ANTHROPIC_API_KEY=... ALLOWED_ORIGINS=...
fly deploy
```

**Any VPS / your own server**
```bash
docker compose up -d --build
```
Put this behind a reverse proxy (Caddy/Nginx) for HTTPS and you're live.

## Connecting the frontend

The React frontend built earlier (`nyaya-sahayak.jsx`) currently calls the
Anthropic API directly from the browser. To use this backend instead:

1. Add a `POST /auth/register` + `/auth/login` flow to get a token.
2. Replace the direct `fetch("https://api.anthropic.com/...")` calls with
   calls to `POST {API_BASE_URL}/chat` and `POST {API_BASE_URL}/draft/generate`,
   sending `Authorization: Bearer <token>`.
3. Set `ALLOWED_ORIGINS` in your backend `.env` to wherever the frontend is
   hosted.

Happy to make that wiring change in the frontend file directly if you want —
just say the word.

## Security notes before going to production

- Rotate `SECRET_KEY` to a long random value (`openssl rand -hex 32`) and
  never commit it.
- Put real rate limiting in front of `/auth/login` and `/chat` (e.g. via
  your reverse proxy or `slowapi`).
- Add an admin-only guard on `POST /documents/upload` before opening this up
  beyond internal use.
- Enable HTTPS everywhere (handled automatically on Railway/Render/Fly; use
  Caddy/Nginx + Let's Encrypt on a raw VPS).
