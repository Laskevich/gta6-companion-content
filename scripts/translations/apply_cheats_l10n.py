"""Writes the translations from cheats_l10n.py into content/cheats.json.

Only fills `effect.<locale>` and `unlock.challenge.text.<locale>`; names stay
official-only. Fails if an English text has no translation, so new cheats are
noticed. Usage: python scripts/translations/apply_cheats_l10n.py
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import cheats_l10n as T  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
PATH = ROOT / "content" / "cheats.json"

SPAWN = re.compile(r"^Spawns the (.+)\.$")
DISCOVER = re.compile(r"^Discover the (.+) \(Progress menu\)\.$")
DISCOVER_PLAIN = re.compile(r"^Discover (.+) \(Progress menu\)\.$")
FINISH5 = re.compile(r"^Finish 5 (\w+) challenges\.$")
FINISH_ALL = re.compile(r"^Finish every (\w+) challenge\.$")


def translate(text, lang, kind):
    tr = T.L[lang]
    table = dict(zip(T.EFFECTS_EN if kind == "effect" else T.CHALLENGES_EN, tr["effects" if kind == "effect" else "challenges"]))
    if text in table:
        return table[text]
    cats = dict(zip(T.CATEGORIES, tr["cats"]))
    for rx, key in ((SPAWN, "spawn"), (DISCOVER, "discover"), (DISCOVER_PLAIN, "discover_plain")):
        m = rx.match(text)
        if m:
            return tr[key].format(name=m.group(1))
    for rx, key in ((FINISH5, "finish5"), (FINISH_ALL, "finish_all")):
        m = rx.match(text)
        if m and m.group(1) in cats:
            return tr[key].format(cat=cats[m.group(1)])
    raise SystemExit(f"no {lang} translation for {kind}: {text!r}")


def main():
    for lang, tr in T.L.items():
        assert len(tr["effects"]) == len(T.EFFECTS_EN), lang
        assert len(tr["challenges"]) == len(T.CHALLENGES_EN), lang
    data = json.loads(PATH.read_text(encoding="utf-8"))
    count = 0
    for item in data["items"]:
        effect = item.get("effect") or {}
        challenge = item["unlock"].get("challenge")
        for lang in T.L:
            if effect.get("en"):
                effect[lang] = translate(effect["en"], lang, "effect")
                count += 1
            if challenge and challenge["text"].get("en"):
                challenge["text"][lang] = translate(challenge["text"]["en"], lang, "challenge")
                count += 1
    PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{count} texts written")


if __name__ == "__main__":
    main()
