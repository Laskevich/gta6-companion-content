"""Place names for our Leonida map, positioned in map units (0..1000 wide).

Positions were read off the official 'Visit Leonida' map (PC Gamer, 2026-11-19) in a
1400 px wide view; `to_map` converts them. Writes map/labels.json.
Kinds: county (big caps), city, area (neighborhood / island / landmark), water.
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
SMALL_TO_FULL = 1870 / 1400
FRAME_X, FRAME_Y, FRAME_W = 62, 62, 1746


def to_map(x, y):
    return (round((x * SMALL_TO_FULL - FRAME_X) * 1000 / FRAME_W, 1),
            round((y * SMALL_TO_FULL - FRAME_Y) * 1000 / FRAME_W, 1))


LABELS = [
    # counties
    ("county", "Lummox County", 700, 372), ("county", "Kelly County", 593, 758),
    ("county", "Leonard County", 1000, 715), ("county", "Vice-Dale County", 1000, 1112),
    ("county", "Mariana County", 560, 1420),
    # cities and towns
    ("city", "Vice City", 937, 997), ("city", "Vice Beach", 1193, 938), ("city", "Port Gellhorn", 427, 690),
    ("city", "Ambrosia", 777, 684), ("city", "Belville", 920, 759), ("city", "Hamlet", 785, 1313),
    ("city", "Key Lento", 795, 1596), ("city", "Grassrivers", 631, 1270), ("city", "Capri", 403, 1010),
    ("city", "Watson Bay", 604, 1349), ("city", "Millport", 922, 440), ("city", "Bonanza", 646, 271),
    ("city", "Grayson", 532, 418), ("city", "Draper Island", 344, 573), ("city", "Waning Sands", 1035, 618),
    ("city", "Southwind", 458, 1637), ("city", "Mile Zero Air Station", 386, 1666),
    # Vice City neighborhoods and islands
    ("area", "Downtown", 990, 1040), ("area", "Little Cuba", 915, 1018), ("area", "Balsero", 820, 957),
    ("area", "Rockridge", 905, 960), ("area", "Crosstown", 985, 945), ("area", "La Perle", 952, 890),
    ("area", "Stockyard", 1012, 861), ("area", "Decor District", 1018, 830), ("area", "Salton", 870, 1036),
    ("area", "Tequesta", 943, 1140), ("area", "Peacock Bay", 930, 1225), ("area", "Southside", 873, 1245),
    ("area", "South Vice-Dale", 865, 1298), ("area", "Bayside", 1033, 905),
    ("area", "Starfish Island", 1100, 985), ("area", "Waxman Island", 1080, 1021),
    ("area", "Ocean Beach", 1206, 1000), ("area", "Port Vice City", 1128, 1065),
    ("area", "Gloriana Key", 1115, 1198), ("area", "Catalan Key", 1021, 1231),
    ("area", "Dalton Island", 1210, 1140), ("area", "Washington Beach", 1210, 852),
    ("area", "Leaf Links", 1085, 800),
    # landmarks and nature
    ("area", "VCIA", 793, 1092), ("area", "Mount Kalaga National Park", 697, 433),
    ("area", "Buckskin Swamp", 672, 905), ("area", "Breakwater Quarry", 578, 1116),
    ("area", "Moreau", 722, 318), ("area", "Pelican Valley", 731, 1404), ("area", "Corsair Key", 946, 1414),
    ("area", "Shoeless Keys", 848, 1453), ("area", "Abismo Key", 630, 1709), ("area", "Maroon Key", 630, 1650),
    ("area", "Permit Keys", 511, 1617), ("area", "Riquezas Keys", 304, 1590),
    # water
    ("water", "Lake Leonida", 847, 600), ("water", "Atlantic Ocean", 1225, 610),
    ("water", "Gulf of Leonida", 180, 1225),
]


def main():
    out = []
    for kind, name, x, y in LABELS:
        mx, my = to_map(x, y)
        out.append({"kind": kind, "name": name, "x": mx, "y": my})
    (HERE / "labels.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(out), "labels")


if __name__ == "__main__":
    main()
