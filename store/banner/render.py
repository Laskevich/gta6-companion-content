"""Renders the App Store header / search-results banners for every store locale.

Usage: python store/banner/render.py [--debug] [lang ...]
Output: store/banner/out/<kind>-<lang>.png (RGB, no alpha — Apple rejects transparency).
Needs Google Chrome; uses Windows fonts (Segoe UI Black, Yu Gothic, Malgun Gothic).
"""
import pathlib
import subprocess
import sys
import tempfile

from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "out"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
SIZES = {"header": (3840, 1646), "search": (3840, 2560)}
LANGS = ["en", "es", "pt", "de", "fr", "it", "ru", "ja", "ko"]


def render(kind, lang, debug):
    w, h = SIZES[kind]
    out = OUT / f"{kind}-{lang}{'-debug' if debug else ''}.png"
    url = (HERE / "banner.html").as_uri() + f"?kind={kind}&lang={lang}" + ("&debug=1" if debug else "")
    # Own profile dir, so headless Chrome never attaches to the user's running browser.
    profile = pathlib.Path(tempfile.gettempdir()) / "banner-chrome-profile"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    f"--user-data-dir={profile}", "--no-first-run", "--no-default-browser-check",
                    "--force-device-scale-factor=1", f"--window-size={w},{h}",
                    "--virtual-time-budget=3000", f"--screenshot={out}", url],
                   check=True, capture_output=True)
    img = Image.open(out)
    if img.size != (w, h):
        raise SystemExit(f"{out.name}: got {img.size}, want {(w, h)}")
    img.convert("RGB").save(out, optimize=True)
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    debug = "--debug" in sys.argv
    OUT.mkdir(exist_ok=True)
    for lang in args or LANGS:
        for kind in SIZES:
            print(render(kind, lang, debug).name)


if __name__ == "__main__":
    main()
