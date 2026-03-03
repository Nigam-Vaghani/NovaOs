import os
import requests
from pathlib import Path
import math
# import matplotlib

def _load_env_file() -> None:
    env_file = Path.cwd() / ".env"
    if not env_file.exists():
        return

    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key and key not in os.environ:
            os.environ[key] = value


class AIAdapter:
    def __init__(self):
        _load_env_file()
        self.provider = os.getenv("AI_PROVIDER", "groq").lower().strip()

        if self.provider == "gemini":
            self.api_key = os.getenv("GEMINI_API_KEY")
            self.model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        else:
            self.provider = "groq"
            self.api_key = os.getenv("GROQ_API_KEY") or os.getenv("GEMINI_API_KEY")
            self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    def is_available(self):
        return self.api_key is not None

    def summarize(self, text: str):
        if not self.is_available():
            if self.provider == "groq":
                return "AI not configured. Set GROQ_API_KEY in .env or environment variables."
            return "AI not configured. Set GEMINI_API_KEY in .env or environment variables."

        prepared_text = self._prepare_text(text)

        if self.provider == "groq":
            return self._summarize_with_groq(prepared_text)

        return self._summarize_with_gemini(prepared_text)

    def _prepare_text(self, text: str) -> str:
        max_chars = int(os.getenv("AI_SUMMARY_MAX_CHARS", "5000"))
        if len(text) <= max_chars:
            return text

        trimmed = text[:max_chars]
        return f"{trimmed}\n\n[Truncated report for token limits]"

    def _summarize_with_groq(self, text: str) -> str:
        url = "https://api.groq.com/openai/v1/chat/completions"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a concise code analysis assistant.",
                },
                {
                    "role": "user",
                    "content": f"Summarize this project analysis report:\n{text}",
                },
            ],
            "temperature": 0.2,
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            return f"AI request failed ({response.status_code}): {error_body}"

        data = response.json()
        choices = data.get("choices", [])
        if not choices:
            return "AI request succeeded but returned no choices."

        content = choices[0].get("message", {}).get("content", "")
        if not content:
            return "AI request succeeded but summary text was empty."

        return content

    def _summarize_with_gemini(self, text: str) -> str:

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Summarize this:\n{text}"
                }]
            }]
        }

        response = requests.post(
            f"{url}?key={self.api_key}",
            headers=headers,
            json=payload
        )

        if response.status_code != 200:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            return f"AI request failed ({response.status_code}): {error_body}"

        data = response.json()
        candidates = data.get("candidates", [])
        if not candidates:
            return "AI request succeeded but returned no candidates."

        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            return "AI request succeeded but returned empty content."

        return parts[0].get("text", "AI request succeeded but summary text was empty.")