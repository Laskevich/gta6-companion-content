"""Frames raw store screenshots with captions for App Store Connect (6.9" iPhone, 1320x2868).

Usage: python store/screens/render.py <raw dir> [lang ...]
  <raw dir> holds <app lang>/<NN-name>.png from the Codemagic `ios-screenshots` artifact
  (screenshots/store/<lang>/). Output: store/screens/out/<lang>/NN.png in store order.
"""
import pathlib
import subprocess
import sys
import tempfile

from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "out"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
W, H = 1320, 2868
# Store order -> raw screenshot from the UI test. Captions in frame.html follow this order.
ORDER = ["01-cheats", "04-secrets", "03-input", "05-guide", "02-cheat", "06-plan", "07-more"]
# Caption language -> app language folder of the raw screenshots.
LANGS = {"en": "en", "es": "es", "pt": "pt-BR", "de": "de", "fr": "fr", "it": "it",
         "ru": "ru", "ja": "ja", "ko": "ko"}


def render(lang, n, src, out):
    profile = pathlib.Path(tempfile.gettempdir()) / "frame-chrome-profile"
    url = (HERE / "frame.html").as_uri() + f"?lang={lang}&n={n}&src={src.as_uri()}"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    f"--user-data-dir={profile}", "--no-first-run", "--allow-file-access-from-files",
                    "--force-device-scale-factor=1", f"--window-size={W},{H}",
                    "--virtual-time-budget=3000", f"--screenshot={out}", url],
                   check=True, capture_output=True)
    img = Image.open(out)
    if img.size != (W, H):
        raise SystemExit(f"{out}: got {img.size}")
    img.convert("RGB").save(out, optimize=True)


def main():
    raw = pathlib.Path(sys.argv[1])
    langs = sys.argv[2:] or list(LANGS)
    for lang in langs:
        folder = OUT / lang
        folder.mkdir(parents=True, exist_ok=True)
        for n, name in enumerate(ORDER, start=1):
            src = raw / LANGS[lang] / f"{name}.png"
            if not src.exists():
                print(f"missing {src}")
                continue
            render(lang, n, src.resolve(), folder / f"{n:02d}.png")
        print(lang, sorted(p.name for p in folder.glob("*.png")))


if __name__ == "__main__":
    main()
