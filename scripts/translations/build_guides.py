"""Builds content/guides.json from guides_src.py and checks every text has all 9 languages.

Keeps the `added` date of guides that already exist, so the NEW badge doesn't restart.
Usage: python scripts/translations/build_guides.py
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "map"))
import guides_src as G  # noqa: E402
from pins import map_pins  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
PATH = ROOT / "content" / "guides.json"
TEXT_FIELDS = ("title", "summary", "location", "reward")


def main():
    old = {}
    if PATH.exists():
        old = {g["id"]: g for g in json.loads(PATH.read_text(encoding="utf-8"))["items"]}
    items = []
    pins = map_pins()
    for g in G.GUIDES:
        for field in TEXT_FIELDS + ("steps",):
            missing = [l for l in G.LANGS if l not in g.get(field, {})]
            if missing:
                raise SystemExit(f"{g['id']}.{field}: missing {missing}")
        counts = {len(v) for v in g["steps"].values()}
        if len(counts) != 1:
            raise SystemExit(f"{g['id']}.steps: different step counts per language {counts}")
        item = {
            "id": g["id"], "kind": g["kind"], "mode": g["mode"],
            **{f: g[f] for f in TEXT_FIELDS[:3]},
            "reward": g["reward"],
            "steps": g["steps"],
            **({"map": pins[g["id"]]} if g["id"] in pins else {}),
            "free": g["free"], "status": g["status"], "evidence": g["evidence"],
            "game_patch": None,
            "added": old.get(g["id"], {}).get("added", G.TODAY),
            "last_checked": G.TODAY,
        }
        if g.get("notes"):
            item["notes"] = g["notes"]
        items.append(item)
    PATH.write_text(json.dumps({"schema_version": 1, "updated": G.TODAY, "items": items},
                               ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(items)} guides written")


if __name__ == "__main__":
    main()
