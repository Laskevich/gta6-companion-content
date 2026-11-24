"""Build the public files the app downloads into dist/v1/.

Drops red items and internal fields (evidence, notes) so sources and
internal reasoning never ship. Adds a content hash for cheap update checks.
"""
import hashlib
import json
import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
DIST = ROOT / "dist" / "v1"
PRIVATE_FIELDS = {"evidence", "notes"}


def public_items(file_name):
    data = json.loads((CONTENT / file_name).read_text(encoding="utf-8"))
    data["items"] = [
        {k: v for k, v in it.items() if k not in PRIVATE_FIELDS}
        for it in data["items"]
        if it["status"] != "red"
    ]
    return data


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    manifest = json.loads((CONTENT / "manifest.json").read_text(encoding="utf-8"))
    manifest["input_method"].pop("evidence", None)
    manifest["input_method"].pop("notes", None)

    files = {"cheats.json": public_items("cheats.json")}
    # Published only once there is something to show; the app treats it as optional.
    if (CONTENT / "guides.json").exists():
        guides = public_items("guides.json")
        if guides["items"]:
            files["guides.json"] = guides
    # Our Leonida map (coastline, place names); the app shows guide pins on it.
    if (CONTENT / "map.json").exists():
        files["map.json"] = json.loads((CONTENT / "map.json").read_text(encoding="utf-8"))
    hashes = {}
    for name, obj in files.items():
        raw = json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        (DIST / name).write_bytes(raw)
        hashes[name] = hashlib.sha256(raw).hexdigest()[:16]

    manifest["hashes"] = hashes
    (DIST / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (ROOT / "dist" / ".nojekyll").write_text("")
    # Static pages (privacy policy) are served from the site root.
    for page in (ROOT / "site").glob("*.html"):
        shutil.copyfile(page, ROOT / "dist" / page.name)
    print("built", ", ".join(f"{k}={v}" for k, v in hashes.items()))


if __name__ == "__main__":
    main()
