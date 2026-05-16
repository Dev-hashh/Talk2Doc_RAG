# Talk2Doc

Talk2Doc is a PDF question-answering app. Upload a PDF, build a FAISS index, and chat with the document through a FastAPI backend and Vite frontend.

The app uses:

- `pypdf` for PDF text extraction
- low-memory hashing embeddings by default
- `FAISS` for vector search
- Supabase Postgres for users/auth data
- Supabase Storage for uploaded FAISS index files
- Ollama or Groq for answer generation

## How It Works

1. A user logs in.
2. The user uploads a PDF.
3. The backend extracts text and splits it into chunks.
4. Chunks are embedded and stored in a FAISS index.
5. The FAISS index and chunk metadata are uploaded to Supabase Storage.
6. Chat requests download the selected index, retrieve matching chunks, and send context to the configured LLM.

## Project Structure

```text
talk2doc/
  backend/
    app/
      routers/
      services/
      schemas/
      config.py
      main.py
  frontend/
    src/
      components/
      hooks/
      api/
  docchat/
    chunker.py
    document_loader.py
    embedder.py
    generator.py
    storage.py
  Dockerfile.backend
  docker-compose.yml
  requirements.txt
```

## Environment

Create `.env` in the project root. At minimum:

```text
DATABASE_URL=postgresql://postgres:password@host:5432/postgres
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
AUTH_SECRET=replace-with-a-long-random-secret

EMBEDDING_MODEL=hashing
OLLAMA_URL=http://localhost:11434/api/generate
MODEL_NAME=deepseek-v3.1:671b-cloud

USE_GROQ=false
GROQ_API_KEY=
GROQ_MODEL=llama-3.3-70b-versatile
```

Use `EMBEDDING_MODEL=hashing` on small hosts. This avoids loading PyTorch and Hugging Face models into the web process, which helps prevent 512 MB memory crashes.

If you want transformer embeddings on a larger host, install the optional extra and set `EMBEDDING_MODEL` to a Sentence Transformers model name:

```powershell
python -m pip install ".[transformer-embeddings]"
```

After changing embedding models, re-ingest PDFs. Index vectors created with one embedding model should be queried with the same embedding model.

## Local Setup

Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
python -m pip install -r backend/requirements.txt
```

Run the backend:

```powershell
python backend/run.py --host 0.0.0.0 --port 8000
```

Run the frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

## Docker

Start the full app:

```powershell
docker compose up --build
```

Services:

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`
- Health check: `http://localhost:8000/health`

In Docker, the backend reaches Ollama through `host.docker.internal`. Keep Ollama running on the host, or set `USE_GROQ=true` with Groq credentials.

## Supabase Storage

The app expects a Supabase Storage bucket named:

```text
Indexes
```

Indexes are stored by user:

```text
<user_id>/<index_name>.index
<user_id>/<index_name>.pkl
```

The local `INDEX_DIR` is only a fallback/runtime path. The web app's active index storage flow uses Supabase Storage.

## Deployment Notes

For small-memory platforms, use:

```text
EMBEDDING_MODEL=hashing
```

Avoid installing transformer/PyTorch dependencies unless the host has enough memory. If the service reports out-of-memory during upload, confirm the deployed environment is not overriding `EMBEDDING_MODEL` with a transformer model such as `all-MiniLM-L6-v2` or `BAAI/bge-small-en`.

The `/health` endpoint is intentionally lightweight. It does not create or resolve the index directory, so health checks should not fail because of a transient index filesystem issue.

## API

Core endpoints:

- `GET /health`
- `POST /auth/register`
- `POST /auth/login`
- `GET /indexes`
- `DELETE /indexes/{name}`
- `POST /ingest`
- `GET /chat/conversations`
- `POST /chat`

API docs are available when the backend is running:

```text
http://localhost:8000/docs
```

## CLI

The `docchat` CLI still exists for local experiments:

```powershell
python -m docchat --help
python -m docchat ingest --pdf "C:\path\to\file.pdf"
python -m docchat ask --question "Summarize this document."
```

The web app path is the primary flow. It stores indexes in Supabase Storage rather than relying on local `faiss.index` and `metadata.pkl` files.

## Troubleshooting

If uploads fail with an out-of-memory message:

- set `EMBEDDING_MODEL=hashing`
- rebuild/redeploy the backend image
- re-ingest the PDFs

If answer generation fails:

- verify Ollama is running, or enable Groq
- verify the configured generation model exists
- verify `OLLAMA_URL` is reachable from where the backend runs

If indexes do not appear:

- verify `SUPABASE_URL` and `SUPABASE_SERVICE_KEY`
- verify the `Indexes` bucket exists
- verify the user is authenticated before upload
