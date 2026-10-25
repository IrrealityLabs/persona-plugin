#!/usr/bin/env python3
"""
anonymize.py — apply a pseudonym map to source files, deterministically.

The map is a JSON list written by the agent after reading the files:
  [{"type": "PERSON", "text": "Jane Smith", "replacement": "Joan Sutton"}, ...]

Every exact, whole-word occurrence is replaced in one pass, longest first (so "Jane Smith" wins
over "Jane"). For a multi-word PERSON whose pseudonym has the same number of words, the first and
last names are also mapped on their own, so a later "Jane" or "Smith" is caught too. To keep a
phrase that contains a mapped name, map the phrase to itself:
  {"type": "KEEP", "text": "Mona Lisa", "replacement": "Mona Lisa"}

  python3 anonymize.py --map pii-map.json <file> [<file> ...]

Writes <name>.anon<ext> next to each input and never touches the originals.
Standard library only.
"""
import argparse
import json
import re
import sys
from pathlib import Path


def expand(mapping: list[dict]) -> dict[str, str]:
    pairs = {m["text"]: m["replacement"] for m in mapping if m.get("text") and m.get("replacement")}
    for m in mapping:
        if m.get("type") != "PERSON": continue
        original, pseudonym = m["text"].split(), m["replacement"].split()
        if len(original) < 2 or len(original) != len(pseudonym): continue
        pairs.setdefault(original[0], pseudonym[0])
        pairs.setdefault(original[-1], pseudonym[-1])
    return pairs


def apply(text: str, pairs: dict[str, str]) -> tuple[str, int]:
    """One pass, longest match first, so a replaced span is never rewritten again — which also
    lets a map entry protect a phrase by mapping it to itself ("Mona Lisa" -> "Mona Lisa")."""
    # Lookarounds rather than \b, so spans that start or end with punctuation still match whole.
    pattern = re.compile(r"(?<!\w)(" + "|".join(re.escape(o) for o in sorted(pairs, key=len, reverse=True)) + r")(?!\w)")
    replaced = [0]
    def swap(match: re.Match) -> str:
        if pairs[match.group(1)] != match.group(1): replaced[0] += 1
        return pairs[match.group(1)]
    return pattern.sub(swap, text), replaced[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--map", required=True, help="JSON list of {type, text, replacement}")
    parser.add_argument("files", nargs="+")
    args = parser.parse_args()
    pairs = expand(json.loads(Path(args.map).read_text()))
    if not pairs: sys.exit("The map is empty; nothing to replace.")
    for name in args.files:
        source = Path(name)
        text, count = apply(source.read_text(), pairs)
        out = source.with_name(f"{source.stem}.anon{source.suffix}")
        out.write_text(text)
        print(f"{out}  ({count} replacements)")


if __name__ == "__main__":
    main()
