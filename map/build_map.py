"""Writes content/map.json from map/land.json + map/labels.json (run trace.py / labels.py first).

Usage: python map/build_map.py [YYYY-MM-DD]
"""
import datetime
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent


def main():
    land = json.loads((HERE / "land.json").read_text(encoding="utf-8"))
    labels = json.loads((HERE / "labels.json").read_text(encoding="utf-8"))
    updated = sys.argv[1] if len(sys.argv) > 1 else datetime.date.today().isoformat()
    out = {"schema_version": 1, "updated": updated, "width": land["width"], "height": land["height"],
           "shapes": land["shapes"], "labels": labels}
    path = HERE.parent / "content" / "map.json"
    path.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(path.name, path.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
