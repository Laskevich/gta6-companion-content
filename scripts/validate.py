"""Validate content: JSON Schema + rating rules + link reachability (optional).

Usage: python scripts/validate.py [--check-links]
Exit code 1 on any error.
"""
import json
import pathlib
import sys
import urllib.parse
import urllib.request

import jsonschema

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
SCHEMA = ROOT / "schema"
MAJOR_OR_VIDEO = {"outlet", "video"}

errors = []


def err(item_id, msg):
    errors.append(f"{item_id}: {msg}")


def check_cheats():
    data = json.loads((CONTENT / "cheats.json").read_text(encoding="utf-8"))
    schema = json.loads((SCHEMA / "cheats.schema.json").read_text(encoding="utf-8"))
    v = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    for e in v.iter_errors(data):
        err("cheats.json", f"{'/'.join(map(str, e.path))}: {e.message}")
    if errors:
        return data

    seen = set()
    for it in data["items"]:
        i = it["id"]
        if i in seen:
            err(i, "duplicate id")
        seen.add(i)
        supporting = [e for e in it["evidence"] if e["stance"] == "supports"]
        refuting = [e for e in it["evidence"] if e["stance"] == "refutes"]
        domains = {urllib.parse.urlparse(e["url"]).netloc.removeprefix("www.") for e in supporting}
        if it["status"] == "green":
            if len(domains) < 2:
                err(i, "green needs supporting evidence from >= 2 different domains")
            if not any(e["source_type"] in MAJOR_OR_VIDEO for e in supporting):
                err(i, "green needs a major outlet or a video among supporting sources")
            if any(e["stance"] == "conflicts" for e in it["evidence"]):
                err(i, "green cannot have conflicting evidence")
            if it["sequence"] is None:
                err(i, "green needs a confirmed code")
        if it["status"] == "red" and not refuting and "red_reason" not in it.get("notes", ""):
            err(i, "red needs refuting evidence or 'red_reason' in notes")
        if not it["evidence"]:
            err(i, "no evidence")
    return data


def check_links(data):
    urls = sorted({e["url"] for it in data["items"] for e in it["evidence"]})
    for u in urls:
        req = urllib.request.Request(u, method="HEAD", headers={"User-Agent": "content-link-check"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                if r.status >= 400:
                    err("links", f"{u} -> {r.status}")
        except Exception as ex:  # noqa: BLE001 - report and continue
            print(f"warning: {u} -> {ex}", file=sys.stderr)


if __name__ == "__main__":
    d = check_cheats()
    if "--check-links" in sys.argv and not errors:
        check_links(d)
    for e in errors:
        print("ERROR", e)
    print(f"{len(errors)} error(s)")
    sys.exit(1 if errors else 0)
