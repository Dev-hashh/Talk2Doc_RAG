import requests
# print("Generator module loaded.")
class Generator:
    def __init__(self, model_name="deepseek-v3.1:671b-cloud"):
        self.model_name = model_name
        self.url = "http://localhost:11434/api/generate"

    def generate(self, context, query):

        prompt = f"""
Use only the following context to answer.

Context:
{context}

Question:
{query}
"""

        response = requests.post(
            self.url,
            json={
                "model": self.model_name,
                "prompt": prompt,
                "stream": False
            }
        )

        data = response.json()

        if "response" in data:
            return data["response"]
        else:
            return f"Error: {data}"

