"""Guide pins for the map, read off the official 'Visit Leonida' map (1400 px view coordinates).

A pin without `r` is an exact spot; with `r` (view px) it is a search area. `n` is an
optional number or letter drawn on the pin (steps of a chain). Writes map/pins.json
(for the preview) and is imported by the guide build to attach `map` to each guide.
"""
import json
import pathlib

from labels import to_map

HERE = pathlib.Path(__file__).resolve().parent
SCALE = 1000 / 1746 * (1870 / 1400)  # view px -> map units

PINS = {
    "tv-tower-easter-egg": [dict(x=790, y=1220, r=18)],
    "skunk-ape-kirk": [dict(x=785, y=1300, r=30)],
    "ufo-encounter": [dict(x=520, y=740, r=55)],
    "dexter-apartment": [dict(x=1163, y=840)],
    "fast-furious-car": [dict(x=1086, y=937)],
    "cool-dog": [dict(x=790, y=1505, r=40)],
    "crab-lab": [dict(x=680, y=1450, r=35)],
    "arthur-morgan-hat": [dict(x=450, y=775, r=25)],
    "shirley-missable": [dict(x=800, y=1575, r=40)],
    "bret-hunting": [dict(x=697, y=450, r=55)],
    "vice-city-portal": [
        dict(x=815, y=1555, r=18, n="S"),
        dict(x=990, y=1035, r=22, n="1"), dict(x=820, y=957, r=22, n="2"), dict(x=785, y=1600, r=22, n="3"),
        dict(x=1195, y=880, r=22, n="4"), dict(x=955, y=870, r=22, n="5"), dict(x=430, y=700, r=22, n="6"),
        dict(x=775, y=1288, r=20, n="7"), dict(x=1115, y=1195, r=22, n="8"), dict(x=740, y=1310, r=20, n="9"),
        dict(x=470, y=712, r=20, n="10"), dict(x=808, y=1322, r=20, n="11"), dict(x=610, y=1110, r=22, n="12"),
        dict(x=883, y=1365, n="★"),
    ],
    "mario-luigi-hats": [dict(x=725, y=345, r=25)],
    "killer-clown-elevator": [dict(x=1142, y=990)],
    "dexter-kill-room": [dict(x=745, y=1640, r=18)],
    "simulation-garage": [dict(x=920, y=772, r=25)],
    "collateral-hitman": [dict(x=1180, y=960, r=40)],
    "satan-hell": [dict(x=427, y=632, r=16)],
    "hyde-island-hunt": [dict(x=803, y=215, r=22)],
    "marbelle-hotel": [dict(x=975, y=962, r=12)],
    "scarface-motel": [dict(x=1200, y=1040, r=12)],
    "mushroom-trip": [dict(x=905, y=405, r=14)],
    "final-flush": [dict(x=946, y=1414, r=14, n="1"), dict(x=943, y=1140, r=16, n="2"), dict(x=790, y=1290, r=22, n="3")],
    "ghost-ship": [dict(x=1083, y=470, r=18)],
    "red-hulk": [dict(x=625, y=655, r=30)],
    "christine-car": [dict(x=850, y=490, r=35)],
    "dom-vamos": [dict(x=385, y=1005, r=16)],
    "ninja-turtles": [dict(x=915, y=422, r=16)],
    "ufo-house": [dict(x=762, y=690, r=14)],
    "michaels-boat": [dict(x=830, y=1540, r=35)],
}


def map_pins():
    out = {}
    for gid, pins in PINS.items():
        conv = []
        for p in pins:
            x, y = to_map(p["x"], p["y"])
            q = {"x": x, "y": y}
            if "r" in p:
                q["r"] = round(p["r"] * SCALE, 1)
            if "n" in p:
                q["n"] = p["n"]
            conv.append(q)
        out[gid] = conv
    return out


if __name__ == "__main__":
    flat = [dict(p, guide=g) for g, ps in map_pins().items() for p in ps]
    (HERE / "pins.json").write_text(json.dumps(flat, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(flat), "pins")
