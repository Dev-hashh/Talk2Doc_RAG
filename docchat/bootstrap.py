import importlib
import sys


REQUIRED_MODULES = {
    "pypdf": "pypdf",
    "sentence_transformers": "sentence-transformers",
    "faiss": "faiss-cpu",
    "numpy": "numpy",
    "requests": "requests",
    "dotenv": "python-dotenv",
}


def ensure_dependencies():
    missing = []

    for module_name, package_name in REQUIRED_MODULES.items():
        try:
            importlib.import_module(module_name)
        except ModuleNotFoundError:
            missing.append(package_name)

    if not missing:
        return

    package_list = ", ".join(sorted(set(missing)))
    raise SystemExit(
        "Missing project dependencies in the current Python environment.\n"
        f"Python executable: {sys.executable}\n"
        f"Missing packages: {package_list}\n\n"
        "Install dependencies with `python -m pip install -r requirements.txt` "
        "or run the command with the project virtualenv: "
        "`.\\venv\\Scripts\\python.exe -m docchat ...`."
    )
