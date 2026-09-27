"""A local language model behind the assistant, through Ollama's HTTP API (no cloud, no keys, standard library only).

Default model: qwen3:4b (2.5 GB, runs comfortably on a 16 GB Apple-silicon laptop next to two fly brains; its
"thinking" mode is switched off so the token cap goes to the answer).  Any Ollama model works: `--llm gemma3:4b`,
`--llm llama3.2:3b` ...
Replies are grammar-constrained to the JSON schema by default (Ollama `format`), which qwen3 handles cleanly; the
parse is lenient anyway (fences stripped, first {...} taken, string fields recovered by regex).  `strict=False`
(assistant.py --llm-loose) asks for JSON in the prompt instead — gemma3:4b derails under the grammar on long prompts
but answers well loosely.  Generation is capped (num_predict) so a looping model cannot stall the notes.
"""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.request

DEFAULT_MODEL = "qwen3:4b"
DEFAULT_URL = "http://127.0.0.1:11434"


class LocalLLM:
    def __init__(self, model: str = DEFAULT_MODEL, url: str = DEFAULT_URL, num_ctx: int = 8192,
                 keep_alive: str = "30m", timeout: float = 300.0, temperature: float = 0.2, num_predict: int = 400, strict: bool = True):
        self.model, self.url, self.num_ctx, self.keep_alive, self.timeout, self.temperature = model, url.rstrip("/"), num_ctx, keep_alive, timeout, temperature
        self.num_predict, self.strict = num_predict, strict
        self.last_error: str | None = None
        self.calls = 0
        self.tokens = 0
        self.seconds = 0.0

    def available(self) -> tuple[bool, str]:
        try:
            with urllib.request.urlopen(f"{self.url}/api/tags", timeout=3) as r:
                names = [m["name"] for m in json.load(r).get("models", [])]
        except Exception as e:  # noqa: BLE001
            return False, f"Ollama not reachable at {self.url} ({e}); start it with `ollama serve`"
        base = self.model.split(":")[0]
        if self.model not in names and not any(n.split(":")[0] == base for n in names):
            return False, f"model {self.model} not pulled (have: {', '.join(names) or 'none'}); run `ollama pull {self.model}`"
        return True, f"{self.model} via Ollama at {self.url}"

    def chat_json(self, system: str, user: str, schema: dict, history: list[dict] | None = None, strict: bool | None = None) -> dict | None:
        """One JSON reply shaped like `schema` (top-level keys), or None on any failure (the reason is in last_error).
        Keep `system` byte-identical between calls: Ollama then reuses the prompt cache for that prefix."""
        keys = list((schema.get("properties") or {}).keys())
        ask = "\n\nReply with ONE JSON object and nothing else, keys: " + ", ".join(
            f"{k} ({self._kind(v)})" for k, v in (schema.get("properties") or {}).items()) + "."
        messages = [{"role": "system", "content": system}] + list(history or []) + [{"role": "user", "content": user + ask}]
        req_body = {"model": self.model, "stream": False, "keep_alive": self.keep_alive, "think": False,
                    "options": {"temperature": self.temperature, "num_ctx": self.num_ctx, "num_predict": self.num_predict},
                    "messages": messages}
        if self.strict if strict is None else strict:
            req_body["format"] = schema
        body = json.dumps(req_body).encode()
        req = urllib.request.Request(f"{self.url}/api/chat", data=body, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                resp = json.load(r)
        except urllib.error.HTTPError as e:
            self.last_error = f"HTTP {e.code}: {e.read().decode(errors='replace')[:200]}"
            return None
        except Exception as e:  # noqa: BLE001
            self.last_error = str(e)
            return None
        self.calls += 1
        self.tokens += int(resp.get("eval_count", 0) or 0)
        self.seconds += float(resp.get("eval_duration", 0) or 0) / 1e9 + float(resp.get("prompt_eval_duration", 0) or 0) / 1e9
        content = (resp.get("message") or {}).get("content", "")
        out = self.parse(content, schema)
        if out is None:
            self.last_error = f"unparseable reply: {content[:200]!r}"
            return None
        self.last_error = None
        return out

    @staticmethod
    def _kind(prop: dict) -> str:
        t = prop.get("type", "string")
        if t == "array":
            return "list of " + ("agenda ids like H1, A4, T2" if "items" in prop and prop["items"].get("type") == "string" else "objects")
        return t

    @staticmethod
    def parse(content: str, schema: dict) -> dict | None:
        """Lenient JSON: strip fences, take the outermost {...}; if that fails, recover string/bool/list fields by regex."""
        props = schema.get("properties") or {}
        text = re.sub(r"<think>.*?</think>", "", content, flags=re.S)          # qwen-style reasoning, if any leaks through
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.M).strip()
        obj = None
        i, j = text.find("{"), text.rfind("}")
        if i >= 0 and j > i:
            for cand in (text[i:j + 1], text[i:] + "}", text[i:] + "\"}", text[i:] + "\"]}"):
                try:
                    obj = json.loads(cand)
                    break
                except json.JSONDecodeError:
                    continue
        if not isinstance(obj, dict):
            obj = {}
            for k, v in props.items():
                if v.get("type") == "string":
                    m = re.search(r'"%s"\s*:\s*"((?:[^"\\]|\\.)*)' % re.escape(k), text)
                    if m:
                        obj[k] = m.group(1).replace('\\"', '"')
                elif v.get("type") == "boolean":
                    m = re.search(r'"%s"\s*:\s*(true|false)' % re.escape(k), text)
                    obj[k] = bool(m and m.group(1) == "true")
                elif v.get("type") == "array":
                    m = re.search(r'"%s"\s*:\s*\[(.*?)\]' % re.escape(k), text, re.S)
                    obj[k] = re.findall(r"[A-Za-z]+\d*", m.group(1)) if m else []
            if not any(k in obj and obj[k] for k in props if props[k].get("type") == "string"):
                return None
        # coerce shapes the small models get wrong
        out = {}
        for k, v in props.items():
            val = obj.get(k)
            t = v.get("type")
            if t == "string":
                out[k] = "" if val is None else (val if isinstance(val, str) else json.dumps(val))
            elif t == "boolean":
                out[k] = val if isinstance(val, bool) else str(val).lower() in ("true", "yes", "1")
            elif t == "array":
                if isinstance(val, str):
                    val = [x.strip() for x in re.split(r"[,;]", val) if x.strip()]
                out[k] = val if isinstance(val, list) else []
                if (v.get("items") or {}).get("type") == "string":
                    ids = []
                    for x in out[k]:
                        m = re.match(r"\s*([HAT]\d+)", str(x))
                        ids.append(m.group(1) if m else str(x))
                    out[k] = ids
            else:
                out[k] = val
        return out

    def stats(self) -> str:
        return f"{self.calls} calls, {self.tokens} tokens generated, {self.seconds:.0f} s of model time"
