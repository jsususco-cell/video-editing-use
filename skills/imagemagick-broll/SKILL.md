---
name: imagemagick-broll
description: Generate cinematic B-roll stills and branded backdrops with ImageMagick — plasma nebulas, mesh gradients, bokeh fields, light streaks, gold-particle textures — for use as Ken Burns pan/zoom shots, card backgrounds, and interstitials in promotional videos. Use whenever a video needs beautiful original imagery instead of screenshots or stock.
---

# ImageMagick B-roll

Generate original, on-brand still imagery for video work. Every image is
procedurally generated — no stock licenses, no screenshots, fully reproducible
from a seed.

## Requirements

- ImageMagick 7.x (`magick` on PATH, or the default Windows install at
  `C:\Program Files\ImageMagick-7.*-Q16-HDRI\magick.exe`).
  Windows install: `winget install --id ImageMagick.ImageMagick -e`
- Python 3.10+ (the generator shells out to `magick`).

## The generator

`broll.py` (next to this file) renders a themed pack:

```bash
python broll.py --brand navy_gold --out ./broll --size 1920x1080 --seed 7
python broll.py --colors "#1F3864,#C9A84C,#0B1526" --out ./broll --size 2400x1350
```

Styles produced per pack (one PNG each, named `broll_<style>.png`):

| Style | Look | Good for |
|---|---|---|
| `nebula` | blurred plasma clouds in brand darks | title backdrops |
| `mesh` | soft multi-point radial gradient (mesh-gradient look) | card/stat backgrounds |
| `glow` | single off-center accent glow on dark field | logo/end cards |
| `bokeh` | out-of-focus accent orbs drifting on dark | warm interstitials |
| `streak` | diagonal motion-blurred light streaks | energy transitions |
| `particles` | fine accent dust/particles field | overlay (screen blend) |
| `wave` | dark gradient with sine-displaced bands | section dividers |
| `grain` | tileable film-grain sheet | grain overlay at low opacity |

## Using packs in video

- **Ken Burns**: render at 1.25× target (2400×1350 for 1080p) and pan/zoom with
  ffmpeg `zoompan` — generated fields have no faces, so any crop works.
- **Card backgrounds**: composite text/HTML captures over `mesh`/`nebula`
  instead of flat CSS gradients.
- **Overlays**: `particles` and `grain` composite with `blend=screen`
  (ffmpeg) or `-compose Screen` (magick) at 10–25% opacity.
- **Motion from stills**: two renders of the same style with different seeds
  crossfaded over 3–4s read as slow ambient motion.

## Recipe notes (for going beyond the generator)

- `plasma:` between two brand colors + heavy `-blur` = instant nebula:
  `magick -size 1920x1080 -seed 7 plasma:#0B1526-#1F3864 -blur 0x24 out.png`
- Mesh look = stack several `radial-gradient:` layers with `-compose Screen`
  at random offsets (the generator does exactly this).
- Bokeh = draw random filled circles, `-blur 0x12`, then `-compose Screen`
  over the base; vary radius/opacity per circle.
- Always finish with a subtle vignette + 1–2% gaussian noise so flat
  gradients don't band on video encodes:
  `-attenuate 0.15 +noise Gaussian`
- Brand palette (Byrdson): navy `#1F3864`, deep `#0B1526`, gold `#C9A84C`,
  soft gold `#D6B75F`.
