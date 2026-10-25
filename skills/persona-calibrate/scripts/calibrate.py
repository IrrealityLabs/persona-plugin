# /// script
# requires-python = ">=3.11"
# dependencies = ["dspy>=3.0"]
# ///
"""
calibrate.py — test a persona against the real person, and calibrate it until it passes.

A modified Turing test. The persona answers questions the real person already answered
(their asset rows), and a judge model sees both answers side by side and has to pick
the real one. Turing score = share of held-out questions where the judge picked the
persona's answer. 50% means indistinguishable; 0% means always caught.

  calibrate  alternate rounds: GEPA improves the judge (N candidates), then GEPA improves
             the persona's roleplay instruction against that judge (N candidates); repeat
  test       score the current persona (its doc as it stands) against its current judge
  validate   put the calibrated persona through a survey it has never seen: each question is
             answered twice and the judge keeps the more human answer (best of 2)

Run (uv installs dspy on the fly):
  uv run calibrate.py calibrate --persona <slug> [--rounds 1] [--candidates 10]
  uv run calibrate.py test      --persona <slug>
  uv run calibrate.py validate  --persona <slug> [--questions questions.txt]

Providers — whichever key is set (OpenRouter first), or force one with PERSONA_PROVIDER:
  OPENROUTER_API_KEY · ANTHROPIC_API_KEY · OPENAI_API_KEY · GEMINI_API_KEY (or GOOGLE_API_KEY) · XAI_API_KEY
Models: haiku | sonnet | opus | luna | sol | flash | pro | grok, or a provider's own model id.
Defaults per provider: persona haiku / judge opus (OpenRouter, Anthropic), luna / sol (OpenAI),
flash / pro (Gemini), grok-4.3 / grok (xAI); override with --persona-model / --judge-model or PERSONA_MODEL / JUDGE_MODEL.
Keys can live in a .env file in the working directory (the .env wins over the shell).
Local, no key: PERSONA_PROVIDER=ollama | lmstudio | llamacpp (PERSONA_BASE_URL to change the address),
with --persona-model / --judge-model naming local models. One request at a time by default; slow.

Each run is saved, append-only, to ./.personas/assets/<slug>/calibration/<timestamp>/
(report.json, judge.json, instruction.txt). The latest judge.json is the persona's current
judge. The score and calibrated instruction are written into the persona doc's
`## Calibration` section, which is how the calibration takes effect.
"""
import argparse
import csv
import json
import logging
import os
import random
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime
from pathlib import Path
from typing import Literal

# tqdm reads this when it's imported, so it has to be set before dspy pulls tqdm in.
if "--verbose" not in sys.argv: os.environ.setdefault("TQDM_DISABLE", "1")

import dspy
import litellm
from gepa.utils.stop_condition import MaxCandidateProposalsStopper

litellm.drop_params = True  # some providers reject temperature on reasoning models; drop it rather than fail

# alias -> model id on each provider (missing = not offered there)
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
DEFAULTS = {"openrouter": ("haiku", "opus"), "anthropic": ("haiku", "opus"), "openai": ("luna", "sol"), "gemini": ("flash", "pro"), "xai": ("grok-4.3", "grok")}
# Local servers (no key) — only used when PERSONA_PROVIDER names one; PERSONA_BASE_URL overrides the address.
LOCAL = {"ollama": "http://localhost:11434/v1", "lmstudio": "http://localhost:1234/v1", "llamacpp": "http://localhost:8080/v1"}
KEY_VARS = {"openrouter": ["OPENROUTER_API_KEY"], "anthropic": ["ANTHROPIC_API_KEY"], "openai": ["OPENAI_API_KEY"], "gemini": ["GEMINI_API_KEY", "GOOGLE_API_KEY"], "xai": ["XAI_API_KEY"]}
TRAIN_SHARE = 0.6
MIN_ROWS = 6
INSTRUCTION_HEADING = "### How to answer as this person"
QUIET = True  # hide DSPy progress bars unless --verbose

VALIDATION_QUESTIONS = [
    {"category": "Introduction & Background", "question": "Thanks for joining us today. To start, can you tell me a bit about yourself and your typical day?"},
    {"category": "Shopping Behavior", "question": "Walk me through how you typically discover and research products before making a purchase. What sources do you trust most?"},
    {"category": "Technology Adoption", "question": "When a new tech product or service comes out, are you usually an early adopter or do you prefer to wait and see? Can you give me an example?"},
    {"category": "Brand Preferences", "question": "What brands do you feel most loyal to right now, and what keeps you coming back to them?"},
    {"category": "Media Consumption", "question": "How do you stay informed about news and current events? What about entertainment - where do you spend most of your time?"},
    {"category": "Decision-Making Process", "question": "Tell me about a significant purchase you made recently - maybe over £500. What factors did you weigh, and what ultimately made you pull the trigger?"},
    {"category": "Pain Points & Needs", "question": "What's something in your daily life that you find frustrating or wish worked better? Something you'd pay to have solved?"},
    {"category": "Financial Priorities", "question": "When you think about spending money, what categories are most important to you? Where do you splurge and where do you try to save?"},
    {"category": "Product Experience", "question": "Can you tell me about a product or service you've used in the past year that really exceeded your expectations? What made it stand out?"},
    {"category": "Future Intentions", "question": "Looking ahead to the next 6-12 months, are there any major purchases or changes you're planning or considering?"},
    {"category": "Values & Social Issues", "question": "How much do factors like sustainability, environmental impact, or social responsibility influence your purchasing decisions? Can you give me an example?"},
    {"category": "Fun & Personality (Zombie Apocalypse)", "question": "Okay, fun one - zombie apocalypse breaks out tomorrow. You can grab three items from any store before you barricade yourself in. What are you taking and why?"},
    {"category": "Fun & Personality (Guilty Pleasures)", "question": "What's your most embarrassing guilty pleasure purchase? Something you bought that you'd be slightly mortified if your friends found out about?"},
    {"category": "Fun & Personality (Time Travel)", "question": "If you could go back in time and invest £1000 in any product or company at its launch, what would you pick and why that one specifically?"},
    {"category": "Closing & Open Feedback", "question": "Is there anything we should have asked you about yourself that others find interesting?"},
]


# ----------------------------------------------------------------------------- signatures

class Respond(dspy.Signature):
    """You are roleplaying as a specific real person in a modified Turing test. Answer the
    question as that specific real person would, in their authentic voice. Someone who knows
    this person well will compare your answer with the real one. You fail if they can tell
    yours is the AI."""

    persona: str = dspy.InputField(desc="Who the person is, plus verbatim examples of how they answered other questions")
    context: str = dspy.InputField(desc="What was happening when the question was asked")
    question: str = dspy.InputField()
    response: str = dspy.OutputField(desc="The answer, in the person's own voice")


class Judge(dspy.Signature):
    """You are comparing two answers to the same question. One is from a specific real person,
    the other is from an AI pretending to be them. Decide which answer the real person gave.
    You fail if you pick the AI's answer."""

    persona: str = dspy.InputField(desc="Who the real person is")
    context: str = dspy.InputField()
    question: str = dspy.InputField()
    answer_a: str = dspy.InputField()
    answer_b: str = dspy.InputField()
    real: Literal["A", "B"] = dspy.OutputField(desc="Which answer the real person gave")
    confidence: float = dspy.OutputField(desc="How sure you are of that pick, from 0.5 (a coin flip) to 1.0 (certain)")


def believability(verdict, persona_is_a: bool) -> float:
    """The judge's probability that the persona's answer is the real one: 0 = sure it's the AI,
    0.5 = can't tell, 1 = sure it's the person. A graded signal, so GEPA can see a rewrite that
    makes the judge less sure even when the judge still picks correctly."""
    try: confidence = min(max(float(getattr(verdict, "confidence", None) or 0.5), 0.5), 1.0)
    except (TypeError, ValueError): confidence = 0.5
    picked_persona = (verdict.real == "A") == persona_is_a
    return confidence if picked_persona else 1 - confidence


# ----------------------------------------------------------------------------- loading

def persona_home() -> Path:
    return Path(os.environ.get("PERSONA_HOME") or "./.personas")


def load_dotenv() -> None:
    """The project's .env wins over the shell, so the key saved for this project is the one used."""
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
    if name is None: sys.exit("Name the local models with --persona-model / --judge-model (or PERSONA_MODEL / JUDGE_MODEL); for Ollama, `ollama list` shows them.")
    if name not in MODELS: return name
    model = MODELS[name].get(provider)
    if not model: sys.exit(f"'{name}' isn't available through {provider}; pick one of: {', '.join(a for a, m in MODELS.items() if provider in m)}")
    return model


def load_rows(slug: str) -> list[dict]:
    rows = []
    for path in sorted((persona_home() / "assets" / slug).glob("*.jsonl")):
        for line in path.read_text().splitlines():
            if not line.strip(): continue
            row = json.loads(line)
            prompt = (row.get("question") or "").strip() or (row.get("context") or "").strip()
            # A leading tag like "[Transcribed]" would let the judge win on formatting alone.
            answer = re.sub(r"^\[[^\]]{1,30}\]\s*", "", (row.get("answer") or "").strip())
            if prompt and answer: rows.append({"context": row.get("context") or "", "question": prompt, "answer": answer})
    return rows


def split_sections(doc: str) -> tuple[str, dict[str, str]]:
    """Return (frontmatter, {heading: body}) keeping order; '' holds anything before the first ##."""
    match = re.match(r"\A(---\n.*?\n---\n)", doc, flags=re.S)
    frontmatter = match.group(1) if match else ""
    sections, current = {"": []}, ""
    for line in doc[len(frontmatter):].splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
            continue
        sections[current].append(line)
    return frontmatter, {k: "\n".join(v).strip() for k, v in sections.items()}


def read_persona(doc: str) -> tuple[str, str]:
    """(profile without Examples/Calibration, calibrated instruction or the default)."""
    _, sections = split_sections(doc)
    profile = "\n\n".join((f"## {k}\n{v}" if k else v) for k, v in sections.items() if k not in ("Examples", "Calibration") and (k or v))
    calibration = sections.get("Calibration", "")
    _, _, instruction = calibration.partition(INSTRUCTION_HEADING)
    return profile.strip(), instruction.strip() or Respond.instructions


def write_calibration(doc_path: Path, score: float, n: int, models: dict, instruction: str) -> None:
    """Replace (or append) only the `## Calibration` section; the rest of the doc is untouched."""
    doc = re.sub(r"\n## Calibration\n.*?(?=\n## |\Z)", "", doc_path.read_text(), flags=re.S).rstrip()
    lines = ["## Calibration", "", f"- Turing score {score:.0%} on {n} held-out answers against this persona's judge ({date.today()}; persona {models['persona']}, judge {models['judge']}). 50% = indistinguishable."]
    if instruction.strip() != Respond.instructions.strip(): lines += ["", INSTRUCTION_HEADING, "", instruction.strip()]
    doc_path.write_text(doc + "\n\n" + "\n".join(lines) + "\n")


def latest_run(slug: str) -> Path | None:
    runs = sorted((persona_home() / "assets" / slug / "calibration").glob("*/judge.json"))
    return runs[-1].parent if runs else None


# ----------------------------------------------------------------------------- the test

def format_examples(rows: list[dict]) -> str:
    return "\n\n".join(f"Q: {r['question']}\nA: {r['answer']}" for r in rows)


def persona_input(profile: str, demos: list[dict], row: dict) -> str:
    """Profile + every other training answer as verbatim examples (never the row being asked)."""
    others = [d for d in demos if d["question"] != row["question"] or d["answer"] != row["answer"]]
    return f"{profile}\n\n## How they answered other questions (verbatim)\n\n{format_examples(others)}"


def persona_examples(profile: str, demos: list[dict], rows: list[dict]) -> list[dspy.Example]:
    return [dspy.Example(persona=persona_input(profile, demos, r), context=r["context"], question=r["question"], answer=r["answer"]).with_inputs("persona", "context", "question") for r in rows]


def real_is_a(seed: int, row: dict) -> bool:
    """Fixed, seeded answer position per question, so every round is judged the same way."""
    return random.Random(f"{seed}:{row['question']}:{row['answer'][:50]}").random() < 0.5


def pair(profile: str, row: dict, ai: str, seed: int) -> dspy.Example:
    a, b = (row["answer"], ai) if real_is_a(seed, row) else (ai, row["answer"])
    return dspy.Example(persona=profile, context=row["context"], question=row["question"], answer_a=a, answer_b=b, real="A" if real_is_a(seed, row) else "B").with_inputs("persona", "context", "question", "answer_a", "answer_b")


def judge_metric(gold, pred, trace=None, pred_name=None, pred_trace=None):
    # Graded: confident right answers score highest, confident wrong ones lowest.
    score = 1 - believability(pred, persona_is_a=gold.real == "B")
    if pred_name is None: return score
    real = gold.answer_a if gold.real == "A" else gold.answer_b
    verdict = "Correct" if pred.real == gold.real else f"Wrong: you picked the AI. The real person gave answer {gold.real}"
    return dspy.Prediction(score=score, feedback=f"{verdict} (your confidence: {pred.confidence}).\nThe real answer was: \"{real}\"")


def turing_metric_for(judge: dspy.Module, profile: str, seed: int):
    def metric(gold, pred, trace=None, pred_name=None, pred_trace=None):
        row = {"context": gold.context, "question": gold.question, "answer": gold.answer}
        verdict = judge(**pair(profile, row, pred.response, seed).inputs())
        score = believability(verdict, persona_is_a=not real_is_a(seed, row))
        if pred_name is None: return score
        outcome = "Passed: the judge thought your answer was the real one" if score > 0.5 else "Failed: the judge spotted the AI"
        return dspy.Prediction(score=score, feedback=f"{outcome} (believability {score:.2f}; 0 = obviously AI, 0.5 = can't tell).\nJudge's reasoning: \"{verdict.reasoning}\"\nThe real person actually said: \"{gold.answer}\"")
    return metric


def run_test(persona: dspy.Module, judge: dspy.Module, profile: str, train: list[dict], rows: list[dict], seed: int, threads: int) -> tuple[float, list[dict]]:
    answers = [p.response for p in persona.batch(persona_examples(profile, train, rows), num_threads=threads, disable_progress_bar=QUIET)]
    pairs = [pair(profile, r, ai, seed) for r, ai in zip(rows, answers)]
    verdicts = judge.batch(pairs, num_threads=threads, disable_progress_bar=QUIET)
    cases = [{"question": r["question"], "real": r["answer"], "persona": ai, "judge_fooled": v.real != g.real, "believability": believability(v, persona_is_a=g.real == "B"), "judge_reasoning": v.reasoning} for r, ai, g, v in zip(rows, answers, pairs, verdicts)]
    return sum(c["judge_fooled"] for c in cases) / len(cases), cases


def mean_believability(cases: list[dict]) -> float:
    return sum(c["believability"] for c in cases) / len(cases)


def optimize(program: dspy.Module, metric, trainset: list, candidates: int, args, reflection_lm: dspy.LM, round_no: int) -> dspy.Module:
    """GEPA, choosing its winner on held-back training questions whose real answers the reflection never
    saw in feedback, so a rewrite only wins if it helps on questions it didn't see. (Quoting the person
    verbatim in the instruction is allowed — it's a fair way to capture how they sound.)"""
    # The candidate cap is the real limit; the metric-call cap is only a safety net. A per-round
    # seed (plus an uncached reflection LM) keeps later rounds from replaying round 1's proposals.
    shuffled = trainset[:]
    random.Random(args.seed * 1000 + round_no).shuffle(shuffled)
    n_val = max(2, len(shuffled) // 3)
    gepa_val, gepa_train = shuffled[:n_val], shuffled[n_val:]
    safety_cap = candidates * (6 + len(gepa_val)) * 2
    optimizer = dspy.GEPA(metric=metric, max_metric_calls=safety_cap, reflection_lm=reflection_lm, num_threads=args.threads, use_merge=False, seed=args.seed * 1000 + round_no, gepa_kwargs={"stop_callbacks": [MaxCandidateProposalsStopper(candidates)]})
    return optimizer.compile(program, trainset=gepa_train, valset=gepa_val)


def predictor_instructions(program: dspy.Module) -> str:
    return program.predictors()[0].signature.instructions


def set_instruction(program: dspy.Predict, instruction: str) -> dspy.Predict:
    program.signature = program.signature.with_instructions(instruction)
    return program


# ----------------------------------------------------------------------------- validation survey

def load_questions(path: str | None) -> list[dict]:
    """A .json list of {category, question}, or a text file with one question per line."""
    if not path: return VALIDATION_QUESTIONS
    text = Path(path).read_text()
    if path.endswith(".json"): return [{"category": q.get("category", ""), "question": q["question"]} for q in json.loads(text)]
    return [{"category": "", "question": line.strip()} for line in text.splitlines() if line.strip()]


def best_of_two(persona: dspy.Module, judge: dspy.Module, profile_with_examples: str, profile: str, item: dict, number: int) -> dict:
    """Two independent answers (distinct rollout ids bypass the cache); the judge keeps the more human one."""
    inputs = {"persona": profile_with_examples, "context": "Market research interview", "question": item["question"]}
    a, b = (persona(**inputs, config={"rollout_id": number * 2 + k}).response for k in (1, 2))
    verdict = judge(persona=profile, context=inputs["context"], question=item["question"], answer_a=a, answer_b=b)
    return {"question_number": number, "category": item["category"], "question": item["question"], "response": a if verdict.real == "A" else b, "candidates": [a, b], "judge_pick": verdict.real, "judge_reasoning": verdict.reasoning}


def run_validate(persona: dspy.Module, judge: dspy.Module, profile: str, rows: list[dict], models: dict, args) -> Path:
    # As in production: every real answer goes in as an example, held-out ones included.
    profile_with_examples = f"{profile}\n\n## How they answered other questions (verbatim)\n\n{format_examples(rows)}"
    questions = load_questions(args.questions)
    print(f"{args.persona}: validation survey, {len(questions)} questions, best of 2", file=sys.stderr)
    with ThreadPoolExecutor(max_workers=args.threads) as pool:
        results = list(pool.map(lambda pair: best_of_two(persona, judge, profile_with_examples, profile, pair[1], pair[0]), enumerate(questions, 1)))
    run_dir = persona_home() / "assets" / args.persona / "calibration" / f"{datetime.now():%Y%m%d-%H%M%S}-validate"
    run_dir.mkdir(parents=True, exist_ok=True)
    with open(run_dir / "survey.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["question_number", "category", "question", "response"], extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)
    (run_dir / "report.json").write_text(json.dumps({"command": "validate", "persona": args.persona, "models": models, "answers": results}, indent=2))
    return run_dir / "survey.csv"


# ----------------------------------------------------------------------------- commands

def run(args) -> Path:
    global QUIET
    load_dotenv()
    QUIET = not args.verbose
    if QUIET: logging.getLogger("dspy").setLevel(logging.WARNING)
    provider, api_key = pick_provider()
    slug = args.persona
    doc_path = persona_home() / f"{slug}.md"
    if not doc_path.exists(): sys.exit(f"No persona at {doc_path}")
    rows = load_rows(slug)
    if len(rows) < MIN_ROWS: sys.exit(f"{slug} has {len(rows)} usable asset rows; need at least {MIN_ROWS} real answers to test against")
    previous = latest_run(slug)
    if args.command in ("test", "validate") and not previous: sys.exit(f"{slug} has no judge yet. Run `calibrate` first to train one.")

    default_persona, default_judge = DEFAULTS.get(provider, ("local", "local") if provider == "llamacpp" else (None, None))
    if provider in LOCAL and args.threads is None: args.threads = 1
    args.threads = args.threads or 8
    models = {
        "persona": resolve_model(args.persona_model or os.environ.get("PERSONA_MODEL") or default_persona, provider),
        "judge": resolve_model(args.judge_model or os.environ.get("JUDGE_MODEL") or default_judge, provider),
    }
    models["reflection"] = resolve_model(args.reflection_model or models["judge"], provider)
    # litellm routes on the provider prefix: openrouter/…, anthropic/…, openai/…, gemini/…, xai/…
    route = {"api_base": os.environ.get("PERSONA_BASE_URL") or LOCAL[provider]} if provider in LOCAL else {}
    prefix = "openai" if provider in LOCAL else provider  # local servers speak the OpenAI API
    lm = lambda model, temp, max_tokens=4000, cache=True: dspy.LM(f"{prefix}/{model}", api_key=api_key, temperature=temp, max_tokens=max_tokens, cache=cache, **route)
    persona_lm, judge_lm, reflection_lm = lm(models["persona"], 1.0), lm(models["judge"], 0.0), lm(models["reflection"], 1.0, 16000, cache=False)
    dspy.configure(lm=persona_lm)

    profile, instruction = read_persona(doc_path.read_text())
    persona = set_instruction(dspy.Predict(Respond), instruction)
    judge = dspy.ChainOfThought(Judge)
    if previous: judge.load(previous / "judge.json")
    judge.set_lm(judge_lm)
    if args.command == "validate": return run_validate(persona, judge, profile, rows, models, args)

    # Keep the held-out questions fixed across runs, so the current judge never trains on them.
    held_out_keys = {(h["question"], h["answer"]) for h in json.loads((previous / "report.json").read_text())["held_out"]} if previous else None
    if held_out_keys is None:
        shuffled = rows[:]
        random.Random(args.seed).shuffle(shuffled)
        held_out_keys = {(r["question"], r["answer"]) for r in shuffled[round(len(shuffled) * TRAIN_SHARE):]}
    test = [r for r in rows if (r["question"], r["answer"]) in held_out_keys]
    train = [r for r in rows if (r["question"], r["answer"]) not in held_out_keys]
    print(f"{slug}: {len(rows)} real answers -> {len(train)} train / {len(test)} held out", file=sys.stderr)

    score, cases = run_test(persona, judge, profile, train, test, args.seed, args.threads)
    judge_label = "current" if previous else "untrained"
    print(f"start: turing score {score:.0%}, believability {mean_believability(cases):.2f}, against the {judge_label} judge", file=sys.stderr)
    history = [{"step": f"start ({judge_label} judge)", "turing_score": score, "believability": mean_believability(cases)}]

    if args.command == "calibrate":
        for round_no in range(1, args.rounds + 1):
            train_answers = [p.response for p in persona.batch(persona_examples(profile, train, train), num_threads=args.threads, disable_progress_bar=QUIET)]
            judge = optimize(judge, judge_metric, [pair(profile, r, ai, args.seed) for r, ai in zip(train, train_answers)], args.candidates, args, reflection_lm, round_no)
            judge.set_lm(judge_lm)
            score, cases = run_test(persona, judge, profile, train, test, args.seed, args.threads)
            history.append({"step": f"round {round_no}: judge", "turing_score": score, "believability": mean_believability(cases), "judge_instruction_changed": predictor_instructions(judge).strip() != Judge.instructions.strip()})
            print(f"round {round_no} judge -> turing score {score:.0%}, believability {mean_believability(cases):.2f}", file=sys.stderr)

            persona = optimize(persona, turing_metric_for(judge, profile, args.seed), persona_examples(profile, train, train), args.candidates, args, reflection_lm, round_no)
            score, cases = run_test(persona, judge, profile, train, test, args.seed, args.threads)
            history.append({"step": f"round {round_no}: persona", "turing_score": score, "believability": mean_believability(cases), "persona_instruction_changed": predictor_instructions(persona).strip() != Respond.instructions.strip()})
            print(f"round {round_no} persona -> turing score {score:.0%}, believability {mean_believability(cases):.2f}", file=sys.stderr)

    run_dir = persona_home() / "assets" / slug / "calibration" / f"{datetime.now():%Y%m%d-%H%M%S}-{args.command}"
    run_dir.mkdir(parents=True, exist_ok=True)
    instruction = persona.signature.instructions
    # Only calibrate runs save a judge; the latest saved judge is the persona's current judge.
    if args.command == "calibrate":
        judge.save(run_dir / "judge.json")
        (run_dir / "instruction.txt").write_text(instruction)
    report = {
        "command": args.command, "persona": slug, "models": models, "seed": args.seed,
        "rounds": args.rounds if args.command == "calibrate" else 0, "candidates": args.candidates,
        "real_answers": len(rows), "train": len(train),
        "held_out": [{"question": r["question"], "answer": r["answer"]} for r in test],
        "turing_score": score, "believability": mean_believability(cases), "history": history,
        "instruction": instruction, "judge_instruction": judge.predict.signature.instructions,
        "cases": cases,
    }
    (run_dir / "report.json").write_text(json.dumps(report, indent=2))
    write_calibration(doc_path, score, len(test), models, instruction)
    return run_dir / "report.json"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["calibrate", "test", "validate"])
    parser.add_argument("--questions", help="validate: .json list of {category, question} or a text file, one per line (default: 15-question market research interview)")
    parser.add_argument("--persona", required=True, help="persona slug (./.personas/<slug>.md)")
    parser.add_argument("--rounds", type=int, default=1, help="judge-then-persona rounds (calibrate); each round is slow, so 1 by default")
    parser.add_argument("--candidates", type=int, default=10, help="GEPA candidates per judge or persona turn")
    parser.add_argument("--persona-model", help="haiku | sonnet | opus | luna | sol | flash | pro | grok | a provider model id (default: the provider's fast model, or PERSONA_MODEL)")
    parser.add_argument("--judge-model", help="opus | sol | pro | … | a provider model id (default: the provider's strong model, or JUDGE_MODEL)")
    parser.add_argument("--reflection-model", help="model GEPA uses to propose rewrites (default: the judge model)")
    parser.add_argument("--threads", type=int, help="parallel calls (default 8; 1 for local servers)")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--verbose", action="store_true", help="show DSPy/GEPA progress and logs")
    print(run(parser.parse_args()))


if __name__ == "__main__":
    main()
