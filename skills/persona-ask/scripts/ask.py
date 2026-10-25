#!/usr/bin/env python3
"""
ask.py — ask one or many personas the same question in parallel, through a model API.

The fast alternative to spawning one subagent per persona: every persona gets its own model call,
all at once, and each answers under the same rules a persona subagent follows (this skill's
"Shaping the response" section, read from SKILL.md so there is one source of truth). Returns the
same Grounding / Thinking / Talking parts, as JSON, for the orchestrator to synthesize.

  python3 ask.py --personas skeptical-cto,sarah-chen --question "…" [--asset page.md]
  python3 ask.py --all --question "…" --model luna --out answers.json

Providers — whichever key is set (OpenRouter first), or force one with PERSONA_PROVIDER:
  OPENROUTER_API_KEY · ANTHROPIC_API_KEY · OPENAI_API_KEY · GEMINI_API_KEY (or GOOGLE_API_KEY) · XAI_API_KEY
Local, no key: PERSONA_PROVIDER=ollama | lmstudio | llamacpp (PERSONA_BASE_URL to change the address)
and name the model (--model llama3.2). llama.cpp serves one model, so any name works there. Local servers
mostly answer one request at a time, so this mode is for privacy and cost, not speed.
Models: haiku | sonnet | opus | luna | sol | flash | pro | grok, or a provider's own model id;
default is the provider's fast model (or PERSONA_MODEL). Keys can live in .env (the .env wins).
Standard library only.
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# alias -> model id on each provider (None = not offered there)
MODELS = {
    "haiku": {"openrouter": "anthropic/claude-haiku-5.5", "anthropic": "claude-haiku-5-5"},
    "sonnet": {"openrouter": "anthropic/claude-sonnet-5.5", "anthropic": "claude-sonnet-5-5"},
    "opus": {"openrouter": "anthropic/claude-opus-5.5", "anthropic": "claude-opus-5-5"},
    "luna": {"openrouter": "openai/gpt-6-luna", "openai": "gpt-6-luna"},
    "sol": {"openrouter": "openai/gpt-6.1-sol", "openai": "gpt-6.1-sol"},
    "flash": {"openrouter": "google/gemini-3.8-flash", "gemini": "gemini-3.8-flash"},
    "pro": {"openrouter": "google/gemini-3.1-pro-preview", "gemini": "gemini-3.1-pro-preview"},
    "grok": {"openrouter": "x-ai/grok-4.7", "xai": "grok-4.7"},
}
FAST_MODEL = {"openrouter": "haiku", "anthropic": "haiku", "openai": "luna", "gemini": "flash", "xai": "grok-4.3"}
# Local servers (no key) — only used when PERSONA_PROVIDER names one; PERSONA_BASE_URL overrides the address.
LOCAL = {"ollama": "http://localhost:11434/v1", "lmstudio": "http://localhost:1234/v1", "llamacpp": "http://localhost:8080/v1"}
KEY_VARS = {"openrouter": ["OPENROUTER_API_KEY"], "anthropic": ["ANTHROPIC_API_KEY"], "openai": ["OPENAI_API_KEY"], "gemini": ["GEMINI_API_KEY", "GOOGLE_API_KEY"], "xai": ["XAI_API_KEY"]}
SKILL = Path(__file__).resolve().parent.parent / "SKILL.md"
# Local servers constrain output to this schema, so small models still return one valid object.
ANSWER_SCHEMA = {"type": "object", "required": ["grounding", "confidence", "thinking", "at_a_glance", "talking"], "properties": {
    "grounding": {"type": "array", "items": {"type": "object", "properties": {"section": {"type": "string"}, "quote": {"type": "string"}}, "required": ["section", "quote"]}},
    "confidence": {"type": "string", "enum": ["high", "medium", "low", "off-pattern"]}, "confidence_reason": {"type": "string"},
    "thinking": {"type": "string"}, "at_a_glance": {"type": "string"}, "talking": {"type": "string"},
    "follow_ups": {"type": "array", "items": {"type": "string"}}}}
RETURN_FORMAT = """Return ONLY a JSON object, no prose around it, with these keys:
{"grounding": [{"section": "<persona-doc section>", "quote": "<short quote or paraphrase>"}],
 "confidence": "high" | "medium" | "low" | "off-pattern",
 "confidence_reason": "<one line on how strong the support is>",
 "thinking": "<2-4 lines of private reasoning over the grounding>",
 "at_a_glance": "<two sentences max: the headline reaction>",
 "talking": "<the first-person answer, in their voice>",
 "follow_ups": ["<questions they'd ask before committing>"]}"""


def load_dotenv() -> None:
    env_file = Path(".env")
    if not env_file.exists(): return
    for line in env_file.read_text().splitlines():
        name, sep, value = line.partition("=")
        if sep and name.strip() and not name.strip().startswith("#"): os.environ[name.strip()] = value.strip().strip("\"'")


def pick_provider() -> tuple[str, str]:
    forced = os.environ.get("PERSONA_PROVIDER")
    if forced in LOCAL: return forced, "local"
    for provider in ([forced] if forced else ["openrouter", "anthropic", "openai", "gemini", "xai"]):
        key = next((os.environ[v] for v in KEY_VARS.get(provider, []) if os.environ.get(v)), None)
        if key: return provider, key
    sys.exit("No model key found. Set one of OPENROUTER_API_KEY (recommended: one key, every model), ANTHROPIC_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY or XAI_API_KEY in .env"
             + (f" (PERSONA_PROVIDER={forced} but its key is missing)" if forced else ""))


def resolve_model(name: str, provider: str) -> str:
    if name is None: sys.exit(f"Name the local model to use with --model or PERSONA_MODEL (for Ollama, `ollama list` shows them).")
    if name not in MODELS: return name
    model = MODELS[name].get(provider)
    if not model: sys.exit(f"'{name}' isn't available through {provider}; pick one of: {', '.join(a for a, m in MODELS.items() if provider in m)}")
    return model


def persona_home() -> Path:
    return Path(os.environ.get("PERSONA_HOME") or "./.personas")


def answering_rules() -> str:
    """This skill's 'Shaping the response' section, so script answers follow the subagent rules."""
    text = SKILL.read_text()
    start = text.find("## Shaping the response")
    end = text.find("\n## ", start + 1)
    return text[start:end if end != -1 else None].strip()


def complete(provider: str, key: str, model: str, system: str, user: str) -> str:
    if provider == "anthropic":
        url, headers = "https://api.anthropic.com/v1/messages", {"x-api-key": key, "anthropic-version": "2023-06-01"}
        body = {"model": model, "max_tokens": 4000, "system": system, "messages": [{"role": "user", "content": user}]}
        read = lambda r: "".join(part.get("text", "") for part in r["content"])
    elif provider == "gemini":
        url, headers = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent", {"x-goog-api-key": key}
        body = {"systemInstruction": {"parts": [{"text": system}]}, "contents": [{"role": "user", "parts": [{"text": user}]}]}
        read = lambda r: "".join(part.get("text", "") for part in r["candidates"][0]["content"]["parts"])
    else:
        base = os.environ.get("PERSONA_BASE_URL") or {"openrouter": "https://openrouter.ai/api/v1", "xai": "https://api.x.ai/v1", **LOCAL}.get(provider, "https://api.openai.com/v1")
        url, headers = f"{base}/chat/completions", {"Authorization": f"Bearer {key}"}
        body = {"model": model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
        if provider in LOCAL: body["response_format"] = {"type": "json_schema", "json_schema": {"name": "persona_answer", "schema": ANSWER_SCHEMA}}
        read = lambda r: r["choices"][0]["message"]["content"]
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={**headers, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as resp: return read(json.loads(resp.read()))


def ask_one(slug: str, question: str, asset: str, provider: str, key: str, model: str, rules: str) -> dict:
    doc = (persona_home() / f"{slug}.md").read_text()
    system = f"You are answering as the persona below. Follow these rules exactly.\n\n{rules}\n\n{RETURN_FORMAT}\n\n# THE PERSONA DOC\n\n{doc}"
    user = question + (f"\n\n# THE ASSET\n\n{asset}" if asset else "")
    try: content = complete(provider, key, model, system, user)
    except urllib.error.HTTPError as err:
        return {"persona": slug, "error": f"{provider} {err.code}: {err.read().decode(errors='replace')[:300]}"}
    match = re.search(r"\{.*\}", content, flags=re.S)
    try: answer = json.loads(match.group(0)) if match else {}
    except json.JSONDecodeError: answer = {}
    return {"persona": slug, **answer} if answer else {"persona": slug, "error": "answer was not valid JSON", "raw": content}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    who = parser.add_mutually_exclusive_group(required=True)
    who.add_argument("--personas", help="comma-separated slugs")
    who.add_argument("--all", action="store_true", help="every persona in the store")
    parser.add_argument("--question", required=True, help="the framed question, asked verbatim")
    parser.add_argument("--asset", help="optional file to show the personas (copy, page, transcript…)")
    parser.add_argument("--model", help="haiku | sonnet | opus | luna | sol | flash | pro | grok | a provider model id (default: the provider's fast model, or PERSONA_MODEL)")
    parser.add_argument("--threads", type=int, help="parallel calls (default 16; 1 for local servers, which mostly run one request at a time)")
    parser.add_argument("--out", help="also write the answers to this JSON file")
    args = parser.parse_args()

    load_dotenv()
    provider, key = pick_provider()
    slugs = sorted(p.stem for p in persona_home().glob("*.md")) if args.all else [s.strip() for s in args.personas.split(",") if s.strip()]
    missing = [s for s in slugs if not (persona_home() / f"{s}.md").exists()]
    if missing: sys.exit(f"No persona file for: {', '.join(missing)} (looked in {persona_home()})")
    model = resolve_model(args.model or os.environ.get("PERSONA_MODEL") or FAST_MODEL.get(provider) or ("local" if provider == "llamacpp" else None), provider)
    asset = Path(args.asset).read_text() if args.asset else ""
    rules = answering_rules()
    with ThreadPoolExecutor(max_workers=args.threads or (1 if provider in LOCAL else 16)) as pool:
        answers = list(pool.map(lambda s: ask_one(s, args.question, asset, provider, key, model, rules), slugs))
    output = json.dumps({"provider": provider, "model": model, "question": args.question, "answers": answers}, indent=2, ensure_ascii=False)
    if args.out: Path(args.out).write_text(output)
    print(output)


if __name__ == "__main__":
    main()
