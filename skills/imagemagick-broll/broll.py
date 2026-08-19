"""Cinematic B-roll pack generator driven by ImageMagick.

Usage:
    python broll.py --brand navy_gold --out ./broll --size 1920x1080 --seed 7
    python broll.py --colors "#1F3864,#C9A84C,#0B1526" --out ./broll
"""
from __future__ import annotations

import argparse
import glob
import os
import random
import subprocess
import sys

BRANDS = {
    "navy_gold": {"dark": "#0B1526", "mid": "#1F3864", "accent": "#C9A84C",
                  "accent2": "#D6B75F"},
    "slate_teal": {"dark": "#0E1418", "mid": "#1F3A40", "accent": "#4FB0A6",
                   "accent2": "#7FD1C8"},
    "plum_rose": {"dark": "#160D1A", "mid": "#41224E", "accent": "#C96A8B",
                  "accent2": "#E39CB4"},
}


def find_magick() -> str:
    from shutil import which
    m = which("magick")
    if m:
        return m
    hits = glob.glob(r"C:\Program Files\ImageMagick-*\magick.exe")
    if hits:
        return hits[0]
    sys.exit("magick not found — install ImageMagick 7 first")


MAGICK = find_magick()


def run(args: list[str]) -> None:
    r = subprocess.run([MAGICK] + args, capture_output=True)
    if r.returncode != 0:
        sys.exit("magick failed: " + " ".join(args[:8]) + "\n"
                 + r.stderr.decode(errors="replace")[-800:])


def finish(extra: list[str]) -> list[str]:
    """Vignette-ish darkened corners + light noise to prevent banding."""
    return extra + ["-attenuate", "0.12", "+noise", "Gaussian"]


def gen_nebula(out, size, c, seed):
    run(["-size", size, "-seed", str(seed), "plasma:fractal",
         "-blur", "0x26", "-colorspace", "Gray", "-auto-level",
         "+level-colors", f"{c['dark']},{c['mid']}",
         "(", "-size", size, "-seed", str(seed + 1), "plasma:fractal",
         "-blur", "0x40", "-colorspace", "Gray", "-auto-level",
         "-threshold", "62%", "-blur", "0x36",
         "-fill", c["accent"], "-opaque", "white", "-transparent", "black",
         "-channel", "A", "-evaluate", "multiply", "0.18", "+channel", ")",
         "-compose", "Screen", "-composite",
         *finish([]), out])


def gen_mesh(out, size, c, seed, rng):
    w, h = map(int, size.split("x"))
    layers = ["-size", size, f"xc:{c['dark']}"]
    for color in [c["mid"], c["mid"], c["accent"], c["mid"]]:
        cx, cy = rng.randint(0, w), rng.randint(0, h)
        r = rng.randint(int(w * 0.35), int(w * 0.7))
        op = "45" if color == c["accent"] else "75"
        layers += ["(", "-size", f"{2*r}x{2*r}",
                   f"radial-gradient:{color}-none",
                   "-channel", "A", "-evaluate", "multiply", f"0.{op}",
                   "+channel", ")",
                   "-geometry", f"+{cx - r}+{cy - r}",
                   "-compose", "Screen", "-composite"]
    run(layers + finish(["-blur", "0x8"]) + [out])


def gen_glow(out, size, c, seed):
    w, h = map(int, size.split("x"))
    r = int(w * 0.55)
    run(["-size", size, f"xc:{c['dark']}",
         "(", "-size", f"{2*r}x{2*r}", f"radial-gradient:{c['accent']}-none",
         "-channel", "A", "-evaluate", "multiply", "0.55", "+channel", ")",
         "-geometry", f"+{int(w*0.58) - r}+{int(h*0.30) - r}",
         "-compose", "Screen", "-composite",
         *finish(["-blur", "0x4"]), out])


def gen_bokeh(out, size, c, seed, rng):
    w, h = map(int, size.split("x"))
    draw = []
    for _ in range(26):
        x, y = rng.randint(0, w), rng.randint(0, h)
        r = rng.randint(14, 90)
        draw.append(f"fill-opacity {rng.uniform(0.08, 0.4):.2f} "
                    f"circle {x},{y} {x + r},{y}")
    run(["-size", size, f"xc:{c['dark']}",
         "(", "-size", size, "xc:none", "-fill", c["accent"],
         "-draw", " ".join(draw), "-blur", "0x14", ")",
         "-compose", "Screen", "-composite",
         "(", "-size", size, f"gradient:none-{c['dark']}",
         "-channel", "A", "-evaluate", "multiply", "0.5", "+channel", ")",
         "-compose", "Over", "-composite",
         *finish([]), out])


def gen_streak(out, size, c, seed):
    run(["-size", size, "-seed", str(seed), "plasma:fractal",
         "-colorspace", "Gray", "-auto-level",
         "-motion-blur", "0x64+35", "-blur", "0x5", "-gamma", "0.45",
         "+level-colors", f"{c['dark']},{c['accent']}",
         "-modulate", "88,104,100",
         *finish([]), out])


def gen_particles(out, size, c, seed):
    rng = random.Random(seed + 99)
    w, h = map(int, size.split("x"))
    draw = []
    for _ in range(420):
        x, y = rng.randint(0, w), rng.randint(0, h)
        r = rng.choice([1, 1, 1, 2, 2, 3])
        draw.append(f"fill-opacity {rng.uniform(0.15, 0.9):.2f} "
                    f"circle {x},{y} {x + r},{y}")
    run(["-size", size, "xc:none", "-fill", c["accent2"],
         "-draw", " ".join(draw), "-blur", "0x0.6", out])


def gen_wave(out, size, c, seed):
    w, h = map(int, size.split("x"))
    run(["-size", f"{w}x{int(h*1.3)}", f"gradient:{c['mid']}-{c['dark']}",
         "-wave", f"{int(h*0.12)}x{int(w*0.55)}",
         "-gravity", "center", "-crop", f"{size}+0+0", "+repage",
         "-blur", "0x3", *finish([]), out])


def gen_grain(out, size, c, seed):
    run(["-size", size, "-seed", str(seed), "xc:gray50",
         "-attenuate", "0.9", "+noise", "Gaussian", "-clamp",
         "-colorspace", "Gray", "-auto-level", "-level", "35%,65%", out])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand", choices=sorted(BRANDS), default=None)
    ap.add_argument("--colors", default=None,
                    help="mid,accent,dark hex triplet, e.g. '#1F3864,#C9A84C,#0B1526'")
    ap.add_argument("--out", default="./broll")
    ap.add_argument("--size", default="1920x1080")
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    if args.colors:
        mid, accent, dark = [x.strip() for x in args.colors.split(",")]
        c = {"dark": dark, "mid": mid, "accent": accent, "accent2": accent}
    else:
        c = BRANDS[args.brand or "navy_gold"]

    os.makedirs(args.out, exist_ok=True)
    rng = random.Random(args.seed)
    jobs = [
        ("nebula", lambda o: gen_nebula(o, args.size, c, args.seed)),
        ("mesh", lambda o: gen_mesh(o, args.size, c, args.seed, rng)),
        ("glow", lambda o: gen_glow(o, args.size, c, args.seed)),
        ("bokeh", lambda o: gen_bokeh(o, args.size, c, args.seed, rng)),
        ("streak", lambda o: gen_streak(o, args.size, c, args.seed)),
        ("particles", lambda o: gen_particles(o, args.size, c, args.seed)),
        ("wave", lambda o: gen_wave(o, args.size, c, args.seed)),
        ("grain", lambda o: gen_grain(o, args.size, c, args.seed)),
    ]
    for name, fn in jobs:
        out = os.path.join(args.out, f"broll_{name}.png")
        fn(out)
        print("ok", out)


if __name__ == "__main__":
    main()
