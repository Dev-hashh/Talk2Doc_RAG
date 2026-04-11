import os
import requests
from dotenv import load_dotenv
load_dotenv()

USE_GROQ = os.getenv("USE_GROQ", "false").lower() == "true"
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "GROQ_MODEL")

OLLAMA_URL = os.getenv("OLLAMA_URL", "OLLAMA_URL")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "OLLAMA_MODEL")

# class Generator:
#     def __init__(self, model_name="deepseek-v3.1:671b-cloud", url="http://localhost:11434/api/generate"):
#         self.model_name = model_name
#         self.url = url

#     def generate(self, context, query):
#         prompt = f"""
# Use only the following context to answer.

# Context:
# {context}

# Question:
# {query}
# """
#         response = requests.post(
#             self.url,
#             json={
#                 "model": self.model_name,
#                 "prompt": prompt,
#                 "stream": False,
#             },
#             timeout=120,
#         )
#         response.raise_for_status()
#         data = response.json()

#         if "response" in data:
#             return data["response"]

#         return f"Error: {data}"

def generate_answer(context: str, question: str) -> str:
    prompt = f"""You are a helpful assistant. Use the context below to answer the question.

Context:
{context}

Question: {question}

Answer:"""

    if USE_GROQ:
        return _generate_groq(prompt)
    else:
        return _generate_ollama(prompt)


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
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()


def _generate_ollama(prompt: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }
    response = requests.post(OLLAMA_URL, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()["response"].strip()