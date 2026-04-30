from dotenv import load_dotenv
import os
import httpx
import asyncio

load_dotenv()


class OpenRouterClient:

    def __init__(self, config):
        self.api_key = os.getenv("OPENROUTER_API_KEY")

        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment")

        # ✅ DEBUG goes HERE (inside class)
        print("🔑 OpenRouter API Key:", self.api_key[:10])

        self.base_url = config["base_url"]
        self.model = config["model"]
        self.max_tokens = config["max_tokens"]
        self.temperature = config["temperature"]
        self.retry_attempts = config["retry_attempts"]
        self.backoff = config.get("retry_backoff_seconds", 2)

    async def generate(self, system_prompt, user_prompt):

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }

        for attempt in range(self.retry_attempts):
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload
                    )

                if response.status_code != 200:
                    raise Exception(response.text)

                data = response.json()
                return data["choices"][0]["message"]["content"]

            except Exception as e:
                if attempt == self.retry_attempts - 1:
                    raise Exception(f"OpenRouter failed: {str(e)}")

                await asyncio.sleep(self.backoff ** attempt)