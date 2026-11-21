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
from referencing import Registry, Resource

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
SCHEMA = ROOT / "schema"
MAJOR_OR_VIDEO = {"outlet", "video"}

errors = []


def err(item_id, msg):
    errors.append(f"{item_id}: {msg}")


def load_schema(name):
    return json.loads((SCHEMA / name).read_text(encoding="utf-8"))


# guides.schema.json reuses locales/evidence definitions from cheats.schema.json.
REGISTRY = Registry().with_resources(
    [(name, Resource.from_contents(load_schema(name))) for name in ("cheats.schema.json", "guides.schema.json")]
)


def schema_errors(file_name, schema_name):
    data = json.loads((CONTENT / file_name).read_text(encoding="utf-8"))
    v = jsonschema.Draft202012Validator(
        load_schema(schema_name), registry=REGISTRY, format_checker=jsonschema.FormatChecker()
    )
    before = len(errors)
    for e in v.iter_errors(data):
        err(file_name, f"{'/'.join(map(str, e.path))}: {e.message}")
    return data, len(errors) > before


def check_rating(it, needs_code):
    """Status rules from HANDOFF, shared by cheats and guides."""
    i = it["id"]
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
        if needs_code and it["sequence"] is None:
            err(i, "green needs a confirmed code")
    if it["status"] == "red" and not refuting and "red_reason" not in it.get("notes", ""):
        err(i, "red needs refuting evidence or 'red_reason' in notes")
    if not it["evidence"]:
        err(i, "no evidence")


def check_items(file_name, schema_name, needs_code):
    data, failed = schema_errors(file_name, schema_name)
    if failed:
        return data
    seen = set()
    for it in data["items"]:
        if it["id"] in seen:
            err(it["id"], f"duplicate id in {file_name}")
        seen.add(it["id"])
        check_rating(it, needs_code)
    return data


def check_manifest(guides):
    manifest = json.loads((CONTENT / "manifest.json").read_text(encoding="utf-8"))
    online = manifest.get("online")
    if online is not None:
        if online.get("status") not in ("unannounced", "announced", "released"):
            err("manifest", "online.status must be unannounced, announced or released")
        if online.get("status") == "released" and not online.get("release_date"):
            err("manifest", "online.release_date is required once released")
    if manifest["sections"].get("guides", {}).get("enabled") and not guides["items"]:
        err("manifest", "guides section is enabled but guides.json has no items")


def check_links(*files):
    urls = sorted({e["url"] for data in files for it in data["items"] for e in it["evidence"]})
    for u in urls:
        req = urllib.request.Request(u, method="HEAD", headers={"User-Agent": "content-link-check"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                if r.status >= 400:
                    err("links", f"{u} -> {r.status}")
        except Exception as ex:  # noqa: BLE001 - report and continue
            print(f"warning: {u} -> {ex}", file=sys.stderr)


if __name__ == "__main__":
    cheats = check_items("cheats.json", "cheats.schema.json", needs_code=True)
    guides = check_items("guides.json", "guides.schema.json", needs_code=False)
    check_manifest(guides)
    cheat_ids = {it["id"] for it in cheats["items"]}
    for it in guides["items"]:
        if it["id"] in cheat_ids:
            err(it["id"], "guide id clashes with a cheat id")
    if "--check-links" in sys.argv and not errors:
        check_links(cheats, guides)
    for e in errors:
        print("ERROR", e)
    print(f"{len(errors)} error(s)")
    sys.exit(1 if errors else 0)
