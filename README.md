# Footprint

Discover the online accounts you may have forgotten, by scanning your Gmail
(read-only) for account-related emails.

## Project structure

```
tracemine/
├── backend/     FastAPI + PostgreSQL + Gmail API + LLM classification
└── frontend/    React + TypeScript + Tailwind
```

## Backend setup

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in real values, see below
alembic upgrade head
uvicorn app.main:app --reload
```

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

## External setup required before running

1. **PostgreSQL** - a local database (Docker is easiest):
   ```bash
   docker run --name footprint-db -e POSTGRES_USER=footprint \
     -e POSTGRES_PASSWORD=footprint -e POSTGRES_DB=footprint \
     -p 5432:5432 -d postgres:16
   ```

2. **Google Cloud project** (for Gmail OAuth):
   - Create a project at console.cloud.google.com
   - Enable the "Gmail API"
   - Configure the OAuth consent screen (start in "Testing" mode, add
     yourself as a test user)
   - Add these scopes to the consent screen: `openid`, `.../auth/userinfo.email`,
     `.../auth/gmail.readonly` (email is used only to reliably identify which
     Google account was connected; no broader profile access is requested)
   - Create OAuth 2.0 credentials (type: Web application)
     - Authorized redirect URI: `http://localhost:8000/auth/google/callback`
   - Copy the client ID/secret into `.env`

3. **Token encryption key** - generate one and put it in `.env`:
   ```bash
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

4. **LLM API key** - an Anthropic API key for classifying ambiguous emails.
   Only sender domain, subject, and Gmail's short snippet are ever sent -
   never the full email body or the whole inbox.

See `backend/.env.example` for the full list of environment variables.

## Privacy and security notes

- Only the `gmail.readonly` OAuth scope is ever requested.
- Your Gmail password is never seen or stored.
- OAuth tokens are encrypted at rest (Fernet) and only decrypted in memory
  when a scan runs.
- Full email bodies are never fetched or stored - only headers and Gmail's
  own short snippet.
- The LLM stage only sees ambiguous cases, and only sender domain + subject
  + snippet - not the raw email.
- `DELETE /privacy/delete-my-data` removes all data for a user, cascading
  through OAuth tokens, evidence, and accounts.

## Known limitations (MVP)

- Scan progress is real: the frontend polls `GET /scan/status/{id}` every
  1.5s and reflects actual stages (searching, classifying, building
  inventory) and real counts, no WebSockets needed at this scale.
- Single Google account per user; no support for multiple connected inboxes
  yet.
- No automated tests yet.
