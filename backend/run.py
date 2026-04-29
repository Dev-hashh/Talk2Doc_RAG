"""
run.py
Convenience launcher — run from the project root:

    python backend/run.py
    python backend/run.py --reload          # dev mode
    python backend/run.py --host 0.0.0.0 --port 8080
"""
import argparse
import sys
from pathlib import Path

# Ensure the project root (parent of backend/) is on sys.path so that
# the `docchat` package is importable alongside the `app` package.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import uvicorn  # noqa: E402  (import after path fix)


def main():
    parser = argparse.ArgumentParser(description="Talk2Doc RAG – FastAPI server")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Bind port (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable hot-reload (dev mode)")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes")
    args = parser.parse_args()

    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers if not args.reload else 1,
        app_dir=str(Path(__file__).resolve().parent),  # backend/ is the app root
    )


if __name__ == "__main__":
    main()
