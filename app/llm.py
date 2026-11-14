import json
import os
import re
import time

import httpx

def get_provider():
    p = os.getenv("LLM_PROVIDER")
    if p:
        return p.lower()
    if os.getenv("GEMINI_API_KEY"):
        return "gemini"
    if os.getenv("GROQ_API_KEY"):
        return "groq"
    return "ollama"


# For backwards compatibility with callers accessing llm.PROVIDER
class _ProviderProxy:
    def __str__(self):
        return get_provider()
    def __repr__(self):
        return repr(get_provider())
    def __eq__(self, other):
        return get_provider() == other
    def lower(self):
        return get_provider()

PROVIDER = _ProviderProxy()
TIMEOUT = float(os.getenv("LLM_TIMEOUT", "180"))


class LLMError(Exception):
    pass


def _ollama(system, user, json_mode, temperature):
    base = os.getenv("OLLAMA_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    timeout = float(os.getenv("LLM_TIMEOUT", "180"))
    payload = {
        "model": model,
        "stream": False,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "options": {"temperature": temperature, "num_ctx": int(os.getenv("OLLAMA_CTX", "8192"))},
    }
    if json_mode:
        payload["format"] = "json"
    r = httpx.post(base + "/api/chat", json=payload, timeout=timeout)
    r.raise_for_status()
    return r.json()["message"]["content"]


def _gemini(system, user, json_mode, temperature):
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise LLMError("GEMINI_API_KEY is not set")
    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    cfg = {"temperature": temperature}
    if json_mode:
        cfg["responseMimeType"] = "application/json"
    payload = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": cfg,
    }
    timeout = float(os.getenv("LLM_TIMEOUT", "180"))
    last_err = None
    for attempt in range(3):
        try:
            r = httpx.post(url, params={"key": key}, json=payload, timeout=timeout)
            if r.status_code == 429:
                time.sleep(5 * (attempt + 1))
                continue
            r.raise_for_status()
            data = r.json()
            parts = data["candidates"][0]["content"]["parts"]
            return "".join(p.get("text", "") for p in parts)
        except Exception as exc:
            last_err = exc
            if attempt < 2:
                time.sleep(4)
                continue
            break
    raise LLMError(f"Gemini call failed: {last_err}")


def _groq(system, user, json_mode, temperature):
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise LLMError("GROQ_API_KEY is not set")
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    timeout = float(os.getenv("LLM_TIMEOUT", "180"))
    payload = {
        "model": model,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    headers = {"Authorization": f"Bearer {key}"}
    url = "https://api.groq.com/openai/v1/chat/completions"
    r = httpx.post(url, json=payload, headers=headers, timeout=timeout)
    if r.status_code == 429:
        time.sleep(15)
        r = httpx.post(url, json=payload, headers=headers, timeout=timeout)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


_PROVIDERS = {"ollama": _ollama, "gemini": _gemini, "groq": _groq}


def available():
    provider = get_provider()
    if provider == "gemini":
        return bool(os.getenv("GEMINI_API_KEY"))
    if provider == "groq":
        return bool(os.getenv("GROQ_API_KEY"))
    if provider == "ollama":
        try:
            httpx.get(os.getenv("OLLAMA_URL", "http://localhost:11434") + "/api/tags", timeout=3)
            return True
        except Exception:
            return False
    return False


def chat(system, user, json_mode=False, temperature=0.2):
    provider = get_provider()
    fn = _PROVIDERS.get(provider)
    if fn is None:
        raise LLMError(f"Unknown LLM_PROVIDER '{provider}'. Use ollama, gemini or groq.")
    try:
        return fn(system, user, json_mode, temperature)
    except LLMError:
        raise
    except Exception as exc:
        raise LLMError(f"{provider} call failed: {exc}")


def _extract_json(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.M).strip()
    try:
        return json.loads(text)
    except ValueError:
        pass
    for opener, closer in (("{", "}"), ("[", "]")):
        start = text.find(opener)
        end = text.rfind(closer)
        if start != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except ValueError:
                continue
    return None


def chat_json(system, user, temperature=0.2, retries=1):
    last = ""
    for attempt in range(retries + 1):
        prompt = user if attempt == 0 else user + "\n\nReturn ONLY valid JSON, no prose."
        last = chat(system, prompt, json_mode=True, temperature=temperature)
        parsed = _extract_json(last)
        if parsed is not None:
            return parsed
    raise LLMError(f"Model did not return valid JSON: {last[:200]}")
