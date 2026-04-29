import os
from unittest.mock import MagicMock
import requests
from dotenv import load_dotenv
load_dotenv()

USE_GROQ = os.getenv("USE_GROQ", "false").lower() == "true"
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "")

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "")


# Module-level helpers — must NOT be inside the class (they take no `self`)

def _generate_groq(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
    }
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=30,
    )
    print(f"DEBUG status: {response.status_code}")
    print(f"DEBUG response: {response.text}")
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()

def _generate_ollama(prompt: str, model_name: str, url: str) -> str:
    payload = {
        "model": model_name or OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }
    response = requests.post(url or OLLAMA_URL, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()["response"].strip()


class Generator:
    def __init__(self, model_name="deepseek-v3.1:671b-cloud", url="http://localhost:11434/api/generate"):
        self.model_name = model_name
        self.url = url

    def generate(self, context: str, question: str) -> str:
        return self.generate_answer(context, question)

    def generate_answer(self, context: str, question: str) -> str:
        prompt = f"""You are a helpful assistant. Use the context below to answer the question.

Context:
{context}

Question: {question}

Answer:"""

        if USE_GROQ:
            return _generate_groq(prompt)
        else:
            return _generate_ollama(prompt, self.model_name, self.url)
  
      
# Test with USE_GROQ=false, mock the requests.post call
if __name__ == "__main__":
    from unittest.mock import patch, MagicMock
    import generator
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "Paris"}
    mock_response.raise_for_status = MagicMock()

    with patch("generator.requests.post", return_value=mock_response):
        g = Generator()
        answer = g.generate("France's capital is Paris.", "What is the capital of France?")
        assert answer == "Paris"

