# docchat

`docchat` is a local PDF question-answering CLI built with:

- `pypdf` for PDF text extraction
- `sentence-transformers` for embeddings
- `FAISS` for vector search
- `Ollama` for answer generation

It follows a basic RAG pipeline:

1. Load a PDF
2. Split it into overlapping chunks
3. Embed the chunks
4. Store them in a FAISS index
5. Retrieve relevant chunks for a question
6. Send the retrieved context to an Ollama model

## Project Structure

```text
talk2doc/
  docchat/
    __main__.py
    cli.py
    bootstrap.py
    document_loader.py
    chunker.py
    embedder.py
    vector_store.py
    retriever.py
    generator.py
  ingest.py
  main.py
  query.py
  requirements.txt
  pyproject.toml
```

Notes:

- `docchat/` contains the active package code.
- `ingest.py`, `main.py`, and `query.py` are compatibility wrappers.
- `faiss.index` and `metadata.pkl` are generated ingestion artifacts.

## Setup

Create and activate the virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Requirements

- Python 3.12+
- Ollama running locally
- A model available through Ollama

Default generation endpoint:

```text
http://localhost:11434/api/generate
```

Default generation model:

```text
deepseek-v3.1:671b-cloud
```

## CLI Usage

Top-level help:

```powershell
python -m docchat --help
```

### Ingest a PDF

```powershell
python -m docchat ingest --pdf "C:\path\to\file.pdf"
```

Optional outputs:

```powershell
python -m docchat ingest --pdf "C:\path\to\file.pdf" --index "custom.index" --metadata "custom.pkl"
```

Optional chunk settings:

```powershell
python -m docchat ingest --pdf "C:\path\to\file.pdf" --chunk-size 700 --overlap 100
```

### Ask One Question

```powershell
python -m docchat ask --question "What is normalization?"
```

Use a custom index:

```powershell
python -m docchat ask --question "What is normalization?" --index "custom.index" --metadata "custom.pkl"
```

### Start Interactive Chat

```powershell
python -m docchat chat
```

Use a custom index:

```powershell
python -m docchat chat --index "custom.index" --metadata "custom.pkl"
```

## Example

Ingest:

```powershell
.\venv\Scripts\python.exe -m docchat ingest --pdf "C:\Users\dev\Downloads\Unit - 2.pdf"
```

Ask:

```powershell
.\venv\Scripts\python.exe -m docchat ask --question "Summarize this unit."
```

Chat:

```powershell
.\venv\Scripts\python.exe -m docchat chat
```

Separate index files for that PDF:

```powershell
.\venv\Scripts\python.exe -m docchat ingest --pdf "C:\Users\dev\Downloads\Unit - 2.pdf" --index "unit2.index" --metadata "unit2.pkl"
.\venv\Scripts\python.exe -m docchat ask --question "Summarize this unit." --index "unit2.index" --metadata "unit2.pkl"
.\venv\Scripts\python.exe -m docchat chat --index "unit2.index" --metadata "unit2.pkl"
```

## Compatibility Scripts

These still work, but they are wrappers around the new package CLI:

```powershell
python ingest.py
python main.py
python query.py
```

Preferred usage is:

```powershell
python -m docchat ...
```

## Current Limitations

- One PDF per ingest command
- New ingestion overwrites the default `faiss.index` and `metadata.pkl` unless custom paths are provided
- Retrieval is basic fixed-size chunking
- There is no multi-PDF combined index yet
- There are no automated tests yet

## Troubleshooting

If you get missing dependency errors, use the project virtualenv:

```powershell
.\venv\Scripts\python.exe -m docchat --help
```

If PowerShell blocks virtualenv activation:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\venv\Scripts\Activate.ps1
```

If answer generation fails:

- verify Ollama is running
- verify the configured model exists
- verify `http://localhost:11434/api/generate` is reachable
