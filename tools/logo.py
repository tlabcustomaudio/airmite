"""AirMite wordmark -> docs/logo/ (SVG + PNG, for light and dark backgrounds).
Outfit (SIL OFL) converted to outlines; the dot of the i in "Mite" is a tiny mite.
Colours = Home Assistant theme NoPattern Aurora: first word in the aurora gradient, "Mite" in the text colour, mascot pink.
Run: python tools/logo.py <path to Outfit-Regular.ttf> <path to Outfit-Bold.ttf>"""
import math, os, sys
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Ellipse, Circle
from matplotlib.colors import LinearSegmentedColormap
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "logo")
# NoPattern Aurora: gradient stops (pink, orange, cyan, violet); per scheme ("Mite" colour, mascot colour)
AURORA = [(0, "#FF2E97"), (0.22, "#FF8A3D"), (0.58, "#2BE4FF"), (1, "#8B3DFF")]
SCHEMES = {"light": ("#04061A", "#FF2E97"), "dark": ("#F3F1FF", "#FF7AC0")}


def aurora_fill(ax, paths):
    """fill the glyph paths with the aurora gradient, left to right"""
    comp = Path.make_compound_path(*paths)
    e = comp.get_extents()
    clip = PathPatch(comp, fc="none", ec="none"); ax.add_patch(clip)
    im = ax.imshow(np.linspace(0, 1, 256)[None, :], cmap=LinearSegmentedColormap.from_list("aurora", AURORA),
                   extent=(e.x0, e.x1, e.y0, e.y1), aspect="auto", interpolation="bicubic", zorder=2)
    im.set_clip_path(clip)


def glyph_paths(font_file, text, x0, tracking=0):
    """outline paths of text in font units, plus the advance; 'ı' = dotless i"""
    f = TTFont(font_file); gs = f.getGlyphSet(); cmap = f.getBestCmap()
    out, x = [], x0
    for ch in text:
        name = cmap[ord(ch)]
        pen = DecomposingRecordingPen(gs); gs[name].draw(pen)
        verts, codes = [], []
        for op, pts in pen.value:
            if op == "moveTo":
                verts.append(pts[0]); codes.append(Path.MOVETO)
            elif op == "lineTo":
                verts.append(pts[0]); codes.append(Path.LINETO)
            elif op == "qCurveTo":     # TrueType: implied on-curve points between off-curve ones
                *offs, end = pts
                for i, p in enumerate(offs):
                    nxt = end if i == len(offs) - 1 else ((p[0] + offs[i + 1][0]) / 2, (p[1] + offs[i + 1][1]) / 2)
                    verts += [p, nxt]; codes += [Path.CURVE3, Path.CURVE3]
            elif op == "curveTo":
                verts += list(pts); codes += [Path.CURVE4] * 3
            elif op == "closePath":
                verts.append((0, 0)); codes.append(Path.CLOSEPOLY)
        if verts:
            out.append((Path([(vx + x, vy) for vx, vy in verts], codes), ch))
        x += gs[name].width + tracking
    return out, x


def mite(ax, cx, cy, s, col, pt):
    """tiny mite seen from above, centred on (cx, cy), body length ~2.4 s; pt = points per unit"""
    lw = s * 0.16 * pt
    for side in (-1, 1):
        for k, a in enumerate((35, 0, -35)):        # 3 legs per side, bent backwards
            r = math.radians(a)
            x1, y1 = cx + side * s * 0.55, cy + s * 0.25 * (1 - k)
            x2, y2 = x1 + side * s * 0.75 * math.cos(r), y1 + s * 0.75 * math.sin(r)
            x3, y3 = x2 + side * s * 0.25, y2 - s * 0.35
            ax.plot([x1, x2, x3], [y1, y2, y3], color=col, lw=lw, solid_capstyle="round",
                    solid_joinstyle="round", zorder=3)
        ax.plot([cx + side * s * 0.15, cx + side * s * 0.5, cx + side * s * 0.75],
                [cy + s * 1.15, cy + s * 1.65, cy + s * 1.75], color=col, lw=lw * 0.8,
                solid_capstyle="round", zorder=3)          # antennae
    ax.add_patch(Ellipse((cx, cy - s * 0.1), s * 1.3, s * 1.6, fc=col, ec="none", zorder=4))   # body
    ax.add_patch(Circle((cx, cy + s * 0.85), s * 0.42, fc=col, ec="none", zorder=4))          # head


def render(reg, bold, scheme):
    mite_c, bug_c = SCHEMES[scheme]
    air, x = glyph_paths(reg, "Air", 0, tracking=-10)
    m, x_end = glyph_paths(bold, "Mıte", x + 40, tracking=-10)
    fig = plt.figure(figsize=(8, 2.4)); ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    aurora_fill(ax, [p for p, _ in air])
    for p, _ in m:
        ax.add_patch(PathPatch(p, fc=mite_c, ec="none"))
    ax.set_xlim(-30, x_end + 10); ax.set_ylim(-200, 1000); ax.set_aspect("equal")
    fig.canvas.draw()
    bb = ax.get_window_extent()
    pt = min(bb.width / (x_end + 40), bb.height / 1200) / fig.dpi * 72     # points per font unit
    stem = [p for p, ch in m if ch == "ı"][0].get_extents()
    mite(ax, (stem.x0 + stem.x1) / 2, stem.y1 + 190, 70, bug_c, pt)
    os.makedirs(OUT, exist_ok=True)
    for ext in ("svg", "png"):
        fig.savefig(os.path.join(OUT, "airmite-wordmark-%s.%s" % (scheme, ext)), transparent=True,
                    dpi=200, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


if __name__ == "__main__":
    for sc in SCHEMES:
        render(sys.argv[1], sys.argv[2], sc)
    print("wrote", sorted(os.listdir(OUT)))
