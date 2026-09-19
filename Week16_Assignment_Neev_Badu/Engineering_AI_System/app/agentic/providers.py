"""Gemini REST adapter with finite timeout, no automatic retries, and real usage."""
import json
import os
import re
from urllib.request import Request, urlopen


class GeminiModel:
    usage_kind = "provider_reported"

    def __init__(self, model=None):
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
        self.key = os.getenv("GEMINI_API_KEY")
        self.model = model or os.getenv("GEMINI_MODEL")
        if not self.key or not self.model:
            raise ValueError("Set GEMINI_API_KEY and GEMINI_MODEL in the environment or .env")
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", self.model):
            raise ValueError("GEMINI_MODEL must be a model ID, not a URL")

    def decide(self, system, context):
        payload = {"systemInstruction": {"parts": [{"text": system}]},
                   "contents": [{"role": "user", "parts": [{"text": json.dumps(context)}]}],
                   "generationConfig": {"temperature": 0, "maxOutputTokens": 4096,
                                        "responseMimeType": "application/json"}}
        request = Request(
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json", "x-goog-api-key": self.key}, method="POST")
        with urlopen(request, timeout=45) as response:
            data = json.load(response)
        usage = data.get("usageMetadata", {})
        candidate = (data.get("candidates") or [{}])[0]
        parts = candidate.get("content", {}).get("parts", [])
        text = "".join(p.get("text", "") for p in parts if not p.get("thought"))
        # Return even malformed/empty text so its usage is counted by the loop.
        return text, {"input_tokens": usage.get("promptTokenCount"),
                      "output_tokens": usage.get("candidatesTokenCount"),
                      "thought_tokens": usage.get("thoughtsTokenCount", 0),
                      "total_tokens": usage.get("totalTokenCount")}
