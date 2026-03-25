import argparse
import pickle
from pathlib import Path

from .bootstrap import ensure_dependencies


DEFAULT_INDEX_PATH = Path("faiss.index")
DEFAULT_METADATA_PATH = Path("metadata.pkl")
DEFAULT_MODEL_NAME = "deepseek-v3.1:671b-cloud"
DEFAULT_OLLAMA_URL = "http://localhost:11434/api/generate"


def build_parser():
    parser = argparse.ArgumentParser(prog="docchat", description="Talk to a PDF with embeddings, FAISS, and Ollama.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser("ingest", help="Chunk a PDF and build the FAISS index.")
    ingest_parser.add_argument("--pdf", required=True, help="Path to the PDF to ingest.")
    ingest_parser.add_argument("--index", default=str(DEFAULT_INDEX_PATH), help="Where to save the FAISS index.")
    ingest_parser.add_argument("--metadata", default=str(DEFAULT_METADATA_PATH), help="Where to save chunk metadata.")
    ingest_parser.add_argument("--chunk-size", type=int, default=700, help="Chunk size in characters.")
    ingest_parser.add_argument("--overlap", type=int, default=100, help="Chunk overlap in characters.")

    ask_parser = subparsers.add_parser("ask", help="Ask one question against an existing index.")
    ask_parser.add_argument("--question", required=True, help="Question to ask.")
    ask_parser.add_argument("--index", default=str(DEFAULT_INDEX_PATH), help="Path to the FAISS index.")
    ask_parser.add_argument("--metadata", default=str(DEFAULT_METADATA_PATH), help="Path to the metadata pickle.")
    ask_parser.add_argument("--top-k", type=int, default=3, help="How many chunks to retrieve.")
    ask_parser.add_argument("--model", default=DEFAULT_MODEL_NAME, help="Ollama model name.")
    ask_parser.add_argument("--ollama-url", default=DEFAULT_OLLAMA_URL, help="Ollama generate endpoint URL.")

    chat_parser = subparsers.add_parser("chat", help="Start an interactive chat against an existing index.")
    chat_parser.add_argument("--index", default=str(DEFAULT_INDEX_PATH), help="Path to the FAISS index.")
    chat_parser.add_argument("--metadata", default=str(DEFAULT_METADATA_PATH), help="Path to the metadata pickle.")
    chat_parser.add_argument("--top-k", type=int, default=3, help="How many chunks to retrieve.")
    chat_parser.add_argument("--model", default=DEFAULT_MODEL_NAME, help="Ollama model name.")
    chat_parser.add_argument("--ollama-url", default=DEFAULT_OLLAMA_URL, help="Ollama generate endpoint URL.")

    return parser


def load_retrieval_stack(index_path, metadata_path):
    ensure_dependencies()
    from .embedder import Embedder
    from .retriever import Retriever
    from .vector_store import VectorStore

    index_file = Path(index_path)
    metadata_file = Path(metadata_path)

    if not index_file.exists():
        raise SystemExit(f"Index not found: {index_file}")

    if not metadata_file.exists():
        raise SystemExit(f"Metadata not found: {metadata_file}")

    print("Loading index...")
    vector_store = VectorStore()
    vector_store.load(str(index_file))

    print("Loading metadata...")
    with metadata_file.open("rb") as file:
        chunks = pickle.load(file)

    vector_store.documents = chunks

    embedder = Embedder()
    retriever = Retriever(embedder, vector_store)
    return retriever


def run_ingest(args):
    ensure_dependencies()
    from . import chunker, document_loader
    from .embedder import Embedder
    from .vector_store import VectorStore

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        raise SystemExit(f"PDF not found: {pdf_path}")

    print("Loading document...")
    pages = document_loader.load_pdf(str(pdf_path))

    print("Chunking document...")
    chunks = chunker.chunk_pages(pages, chunk_size=args.chunk_size, overlap=args.overlap)
    print("Total chunks:", len(chunks))

    if not chunks:
        raise SystemExit("No chunks created. Check PDF extraction.")

    embedder = Embedder()
    doc_embeddings = embedder.embed_documents(chunks)

    vector_store = VectorStore()
    vector_store.add(doc_embeddings, chunks)

    print("Saving FAISS index...")
    vector_store.save(args.index)

    print("Saving metadata...")
    with Path(args.metadata).open("wb") as file:
        pickle.dump(chunks, file)

    print("Ingestion complete.")
    return 0


def answer_question(question, retriever, generator, top_k):
    retrieved_chunks = retriever.retrieve(question, k=top_k)

    if not retrieved_chunks:
        print("No chunks retrieved.")
        return 1

    context = "\n".join(chunk["text"] for chunk in retrieved_chunks)

    print("\nSources:")
    for chunk in retrieved_chunks:
        print(f"- {chunk['source']} | page {chunk['page']} | chunk {chunk['chunk_id']}")

    answer = generator.generate(context, question)
    print("\nAnswer:\n", answer)
    return 0


def run_ask(args):
    ensure_dependencies()
    from .generator import Generator

    retriever = load_retrieval_stack(args.index, args.metadata)
    generator = Generator(model_name=args.model, url=args.ollama_url)
    return answer_question(args.question, retriever, generator, args.top_k)


def run_chat(args):
    ensure_dependencies()
    from .generator import Generator

    retriever = load_retrieval_stack(args.index, args.metadata)
    generator = Generator(model_name=args.model, url=args.ollama_url)

    while True:
        question = input("\nAsk a question (or type 'exit'): ")
        if question.lower() == "exit":
            return 0
        answer_question(question, retriever, generator, args.top_k)


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "ingest":
        return run_ingest(args)
    if args.command == "ask":
        return run_ask(args)
    if args.command == "chat":
        return run_chat(args)

    parser.error(f"Unknown command: {args.command}")
    return 2
