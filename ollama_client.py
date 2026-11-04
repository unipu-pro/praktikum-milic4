"""Minimal client for a local Ollama server."""
import os

import requests
from dotenv import load_dotenv

load_dotenv()


class OllamaError(Exception):
    """Raised when the Ollama server cannot be reached or returns an error."""


DEFAULT_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3.2:1b"


def get_base_url():
    return os.getenv("OLLAMA_BASE_URL", DEFAULT_BASE_URL)


def get_model():
    return os.getenv("OLLAMA_MODEL", DEFAULT_MODEL)


def _request(method, path, payload=None, timeout=120):
    url = get_base_url().rstrip("/") + path
    try:
        response = requests.request(method, url, json=payload, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except (requests.exceptions.RequestException, ValueError) as exc:
        raise OllamaError(f"Ollama request failed: {exc}") from exc


def is_running():
    try:
        response = requests.get(get_base_url(), timeout=3)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def list_models():
    data = _request("GET", "/api/tags")
    return [m["name"] for m in data.get("models", [])]


def generate(prompt, model=None, system=None):
    payload = {"model": model or get_model(), "prompt": prompt, "stream": False}
    if system:
        payload["system"] = system
    return _request("POST", "/api/generate", payload)["response"]


def build_messages(prompt, system=None, history=None):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": prompt})
    return messages


def chat(messages, model=None):
    payload = {"model": model or get_model(), "messages": messages, "stream": False}
    return _request("POST", "/api/chat", payload)["message"]["content"]
