"""Traces land and lakes from a reference map image into our own simplified vector shapes.

Usage: python map/trace.py <reference.png> -> map/land.json
The reference image is only read here (never shipped). Output: polygons in map units
(0..1000 wide), outer land rings and lake holes, simplified so the drawing is our own.
"""
import json
import pathlib
import sys

import cv2
import numpy as np
from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
# Inner frame of the reference image (pixels) and overlays to ignore (legend, seal, title, compass).
FRAME = (62, 62, 1808, 2499)
IGNORE = [(154, 134, 421, 478), (1382, 2003, 1596, 2217), (1282, 2237, 1690, 2384), (260, 1716, 387, 1877)]


def main():
    im = np.array(Image.open(sys.argv[1]).convert("RGB")).astype(int)
    x0, y0, x1, y1 = FRAME
    im = im[y0:y1, x0:x1]
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    water = (b - r > 70) & (g - r > 40)
    white = (r > 215) & (g > 215) & (b > 215)
    land = (~water & ~white).astype(np.uint8) * 255
    # White next to land is roads, runways and labels on land: count it as land.
    near = cv2.dilate(land, np.ones((25, 25), np.uint8)) > 0
    land[white & near] = 255
    for ax0, ay0, ax1, ay1 in IGNORE:
        land[ay0 - y0:ay1 - y0, ax0 - x0:ax1 - x0] = 0
    # Fill roads and labels that cross land, then drop specks (text letters, noise).
    land = cv2.morphologyEx(land, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    land = cv2.morphologyEx(land, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(land, 8)
    keep = np.zeros_like(land)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] >= 120:
            keep[lab == i] = 255
    contours, hier = cv2.findContours(keep, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    H, W = keep.shape
    scale = 1000 / W
    shapes = []
    for i, c in enumerate(contours):
        area = cv2.contourArea(c)
        is_hole = hier[0][i][3] != -1
        if area < (600 if is_hole else 120):
            continue
        approx = cv2.approxPolyDP(c, 1.6, True)
        if len(approx) < 3:
            continue
        pts = [[round(float(p[0][0]) * scale, 1), round(float(p[0][1]) * scale, 1)] for p in approx]
        shapes.append({"hole": bool(is_hole), "points": pts})
    out = {"width": 1000, "height": round(H * scale, 1), "shapes": shapes}
    (HERE / "land.json").write_text(json.dumps(out, separators=(",", ":")), encoding="utf-8")
    print(len(shapes), "shapes;", sum(len(s["points"]) for s in shapes), "points; height", out["height"])


if __name__ == "__main__":
    main()
