# Production Log-to-Eval Dataset Builder

Mines production-like LLM logs, samples useful examples, auto-labels them (LLM-as-judge),
routes low-confidence cases to human review, and exports an approved eval dataset (JSONL).

## Stack
- **Backend:** FastAPI, SQLAlchemy, PostgreSQL, sentence-transformers, scikit-learn (HDBSCAN/KMeans), Anthropic API
- **Frontend:** React + Vite + Tailwind, react-router, axios
- **Storage:** PostgreSQL (log store), JSONL (eval dataset export)

## Quick start (Docker)

```bash
cp backend/.env.example backend/.env   # fill in ANTHROPIC_API_KEY
export ANTHROPIC_API_KEY=sk-ant-...
docker compose up --build
```

- Backend: http://localhost:8000 (docs at /docs)
- Frontend: https://ai-log-eval-dataset.vercel.app

## Deploying both on Vercel

This repo is set up as two separate Vercel projects pointing at the same GitHub repo,
one with **Root Directory = `backend`**, the other **Root Directory = `frontend`**.

### Backend (`backend/`)
- Vercel auto-detects FastAPI from `requirements.txt` + the `api/index.py` entrypoint
  (`api/index.py` just re-exports `app` from `app/main.py`).
- `vercel.json` sets `maxDuration: 60` on the function and rewrites all paths to it.
- **Environment variables** (Project Settings → Environment Variables):
  - `DATABASE_URL` — use your **Neon pooled connection string** (hostname contains `-pooler`),
    e.g. `postgresql://user:pass@ep-xxx-pooler.region.aws.neon.tech/eval_builder?sslmode=require`.
    Serverless functions open a fresh DB connection per invocation (see `NullPool` in
    `database.py`), so you need Neon's built-in PgBouncer pooler, not the direct connection string.
  - `ANTHROPIC_API_KEY`
- Note: `sentence-transformers`/`torch` were swapped out for **TF-IDF + TruncatedSVD from
  scikit-learn** (`app/services/clustering.py`) specifically because torch would blow past
  Vercel's 500MB serverless bundle limit and add multi-second cold starts. Clustering quality
  is a bit coarser than transformer embeddings but is fine for this project's scale, and it's
  one less external model download.
- Table creation (`Base.metadata.create_all`) runs on cold start — harmless but means the very
  first request after a deploy is a little slower.
- Deploy: `vercel --cwd backend` or connect the repo in the Vercel dashboard with Root Directory
  set to `backend`.

### Frontend (`frontend/`)
- Vercel auto-detects Vite. Root Directory = `frontend`, framework preset = Vite.
- `vercel.json` rewrites all paths to `index.html` so React Router's client-side routes
  (`/logs`, `/clusters`, `/review`, `/export`) don't 404 on a hard refresh.
- **Environment variable**: `VITE_API_URL` = your deployed backend's URL, e.g.
  `https://eval-dataset-builder-api.vercel.app`.
- Deploy: `vercel --cwd frontend` or connect the repo with Root Directory set to `frontend`.

### CORS
Update `cors_origins` in `backend/app/config.py` (or set it via an env var override) to your
actual frontend domain once you know it — the wildcard `https://*.vercel.app` in the default
config is only safe for early testing, not production.

## Quick start (local, no Docker)


**Backend**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# start a local postgres, then:
cp .env.example .env   # edit DATABASE_URL / ANTHROPIC_API_KEY
uvicorn app.main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

## Workflow (matches the 6-phase build guide)

1. **Dashboard** → seed 1,000 synthetic logs (or point log ingestion at real production data).
2. **Logs** → filter, run sampling modes (random / failure-biased / diversity), or pull
   "high-value candidates" (negative feedback, retries, errors). Select logs → generate eval labels.
3. **Clusters** → embed prompts (sentence-transformers) and cluster with scikit-learn
   (HDBSCAN by default, falls back to KMeans on older sklearn or when you pick it explicitly).
   Each cluster tracks eval coverage.
4. **Review Queue** → cases with `confidence < 0.7` land here. Approve, edit + approve, or reject.
   Every action is logged as a `ReviewEvent` (what changed, why).
5. **Export** → download `eval_dataset.jsonl` (approved cases only) and see dataset health
   (totals, by status/difficulty/label type, auto-label vs. human-reviewed %).

## Key design notes

- **Privacy:** `app/services/privacy.py` redacts emails, phone numbers, secrets, and
  self-declared names before logs are stored; redaction method + fields are tracked per log.
- **Dedup:** `app/services/dedup.py` skips exact-hash duplicates before calling the labeler;
  hooks are in place for embedding-similarity dedup too.
- **Clustering algorithm swap:** set `algorithm: "kmeans"` in the `/clusters/run` request if
  your scikit-learn version doesn't ship `HDBSCAN` (added in 1.3) — the service auto-falls-back anyway.
- **Dataset status machine:** every `EvalCase` is `draft → approved | rejected | deprecated`,
  so exports only ever pull consistent, reviewed data.
