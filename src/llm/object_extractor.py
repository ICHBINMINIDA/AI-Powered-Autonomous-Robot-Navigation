"""Target-object extraction through a locally hosted Ollama model."""

from __future__ import annotations

import json
from typing import Optional

import requests


class ObjectExtractor:
    def __init__(self, endpoint: str, model: str, timeout: float = 20.0) -> None:
        self.endpoint = endpoint
        self.model = model
        self.timeout = timeout

    def extract(self, command_text: str) -> Optional[str]:
        prompt = f"""
You extract the target object from robot navigation commands.
Return JSON only in this exact form:
{{"object": "target description"}}

Example:
Command: "Please find the blue ball"
Response: {{"object": "blue ball"}}

Command: "{command_text}"
""".strip()

        try:
            response = requests.post(
                self.endpoint,
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=self.timeout,
            )
            response.raise_for_status()
            raw_model_response = response.json().get("response", "")
            parsed = json.loads(raw_model_response)
            target = parsed.get("object")
            return str(target).strip().lower() if target else None
        except (requests.RequestException, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            print(f"Object extraction failed: {exc}")
            return None
