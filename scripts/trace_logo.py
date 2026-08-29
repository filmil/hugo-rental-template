#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Trace a raster logo into the TikZ sources in //static/logo.

Usage: python3 scripts/trace_logo.py <logo.jpg> [outdir]

The input is the brand logo as a raster (JPEG or PNG). Marching squares at
the 128 grey level with linear interpolation follows the antialiasing, so
the contours are sub-pixel smooth; Douglas-Peucker at 0.22 px keeps them
compact. Each closed loop becomes a TikZ subpath and even-odd filling turns
inner loops into holes, so counters and interior negative space are holes in
the ink rather than white paint.

Needs numpy and PIL. Fidelity can be checked with an XOR rasterisation of
the traced polygons against the source ink mask.

The x-range groupings below (mark, then the two wordmark halves) match a
mark-plus-wordmark lockup where the wordmark is drawn in two weights; adjust
the ranges in group() to fit your own artwork.
"""
import sys
import pathlib
import numpy as np
from PIL import Image

im = Image.open(sys.argv[1]).convert("L")
OUT = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "static/logo")

import numpy as np
from PIL import Image

G = np.array(im).astype(float)
H, W = G.shape
LEVEL = 128.0

def marching_squares(g, level):
    """Closed iso-contours of g at `level` (ink = below level).

    Returns a list of loops, each an (N,2) float array of (x, y) points in
    pixel coordinates.
    """
    f = level - g  # ink positive
    from collections import defaultdict
    segs = defaultdict(list)   # start-key -> [(a, b), ...]
    nseg = 0
    def key(p): return (round(p[0]*4096), round(p[1]*4096))
    def interp(pa, va, pb, vb):
        t = va / (va - vb)
        return (pa[0] + t*(pb[0]-pa[0]), pa[1] + t*(pb[1]-pa[1]))
    out = []
    for y in range(H-1):
        row0, row1 = f[y], f[y+1]
        for x in range(W-1):
            tl, tr = row0[x], row0[x+1]
            bl, br = row1[x], row1[x+1]
            c = (tl>0)|((tr>0)<<1)|((br>0)<<2)|((bl>0)<<3)
            if c in (0,15): continue
            top    = interp((x,y),tl,(x+1,y),tr)     if (tl>0)!=(tr>0) else None
            right  = interp((x+1,y),tr,(x+1,y+1),br) if (tr>0)!=(br>0) else None
            bottom = interp((x,y+1),bl,(x+1,y+1),br) if (bl>0)!=(br>0) else None
            left   = interp((x,y),tl,(x,y+1),bl)     if (tl>0)!=(bl>0) else None
            # directed edges keep ink on the left, so loops chain consistently
            table = {
                1:[(left,top)], 2:[(top,right)], 3:[(left,right)],
                4:[(right,bottom)], 6:[(top,bottom)], 7:[(left,bottom)],
                8:[(bottom,left)], 9:[(bottom,top)], 11:[(bottom,right)],
                12:[(right,left)], 13:[(right,top)], 14:[(top,left)],
            }
            if c in (5,10):
                center = (tl+tr+bl+br)/4.0
                if c==5:
                    segs_c = [(left,top),(right,bottom)] if center<=0 else [(left,bottom),(right,top)]
                else:
                    segs_c = [(top,right),(bottom,left)] if center<=0 else [(top,left),(bottom,right)]
            else:
                segs_c = table[c]
            for a,b in segs_c:
                if a is None or b is None: continue
                segs[key(a)].append((a,b)); nseg += 1
    # chain segments into loops
    loops = []
    open_chains = 0
    while segs:
        k0 = next(iter(segs))
        a, b = segs[k0].pop()
        if not segs[k0]: del segs[k0]
        loop = [a, b]
        while True:
            k = key(loop[-1])
            if k == key(loop[0]):
                loops.append(np.array(loop[:-1])); break
            bucket = segs.get(k)
            if not bucket:
                open_chains += 1; break   # dropped: could not close
            _, nb = bucket.pop()
            if not bucket: del segs[k]
            loop.append(nb)
    print(f"segments: {nseg}, open (dropped) chains: {open_chains}")
    return [l for l in loops if len(l) >= 6]

def dp(points, tol):
    """Douglas-Peucker on a closed loop (split at two extreme points)."""
    pts = points
    def simplify(seg):
        if len(seg) < 3: return seg
        a, b = seg[0], seg[-1]
        ab = b - a; L = np.hypot(*ab)
        if L == 0:
            d = np.hypot(*(seg - a).T)
        else:
            d = np.abs(np.cross(ab, seg - a)) / L
        i = int(np.argmax(d))
        if d[i] > tol:
            return np.vstack([simplify(seg[:i+1])[:-1], simplify(seg[i:])])
        return np.array([a, b])
    i0 = 0
    i1 = int(np.argmax(np.hypot(*(pts - pts[0]).T)))
    if i1 == 0: return pts
    p1 = np.vstack([pts[i0:i1+1]])
    p2 = np.vstack([pts[i1:], pts[:1]])
    s = np.vstack([simplify(p1)[:-1], simplify(p2)[:-1]])
    return s


loops = marching_squares(G, LEVEL)
loops = [dp(l, 0.22) for l in loops]


H = 294.0

def group(lo, hi):
    return [l for l in loops if lo <= l[:,0].max() <= hi]

mark      = group(0, 340)     # the mark, with its interior holes
word_dim  = group(341, 745)   # first wordmark half, drawn de-emphasised
word_bold = group(746, 1100)  # second wordmark half, drawn solid

def subpaths(ls, sx, sy, dx, dy, prec=3):
    """TikZ subpath text for loops: X=x*sx+dx, Y=(H-y)*sy+dy."""
    parts = []
    for l in ls:
        pts = " -- ".join(f"({x*sx+dx:.{prec}f},{(H-y)*sy+dy:.{prec}f})" for x, y in l)
        parts.append(pts + " -- cycle")
    return "\n    ".join(parts)

def fill(ls, opts, sx, sy, dx, dy):
    return f"  \\fill[{opts}]\n    {subpaths(ls, sx, sy, dx, dy)};"

# ---- full lockup: 100mm x 29.4mm canvas ----
s = 0.1
logo = f"""% SPDX-License-Identifier: Apache-2.0
%
% The brand lockup: the mark and the wordmark, traced from the raster logo.
% Trace: marching squares over the antialiased bitmap at the 128 grey level,
% Douglas-Peucker simplified to 0.22 px; regenerate with //scripts:trace_logo.
%
% Counters and interior negative space in the mark are HOLES in the ink
% (even-odd subpaths), not white paint. Painted white would lie on any
% surface that is not white; a hole shows the real ground through, which is
% what lets the same file sit on the page, a dark footer, and a dark tab
% strip. The first wordmark half is drawn at 0.74 opacity so it keeps its
% relative weight in any ink colour.
%
% Make PGF emit SVG directly instead of PostScript specials. With the
% default DVI driver every \\draw becomes a PS special that dvisvgm can only
% interpret through Ghostscript; where gs is absent -- a sandboxed CI action,
% for instance -- the strokes are dropped silently. This driver removes the
% dependency entirely.
\\def\\pgfsysdriver{{pgfsys-dvisvgm.def}}
\\documentclass[tikz,border=0pt]{{standalone}}
\\begin{{document}}
\\begin{{tikzpicture}}[x=1mm, y=1mm]
  % dvisvgm sizes a DVI by its ink, so the canvas is pinned with a
  % zero-opacity stroke rather than an unstroked path.
  \\draw[opacity=0,line width=0.01mm] (-0.5,-0.5) rectangle (100.5,29.9);

{fill(mark, "even odd rule", s, s, 0, 0)}

{fill(word_dim, "even odd rule, fill opacity=0.74", s, s, 0, 0)}

{fill(word_bold, "even odd rule", s, s, 0, 0)}
\\end{{tikzpicture}}
\\end{{document}}
"""

# ---- mark alone: 10mm square canvas, centred ----
xs = np.concatenate([l[:,0] for l in mark]); ys = np.concatenate([l[:,1] for l in mark])
x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
sm = 10.0 / max(x1-x0, y1-y0)
dx = (10.0 - (x1-x0)*sm)/2 - x0*sm
dy = (10.0 - (y1-y0)*sm)/2 - (H-y1)*sm
markt = f"""% SPDX-License-Identifier: Apache-2.0
%
% The mark alone: the favicon and small-size companion to brand-logo.tex.
% Same trace, same even-odd holes; see that file for provenance and for why
% the interior negative space is a hole rather than paint. The wordmark is
% dropped here on purpose: at favicon size it reads as noise, and the mark's
% silhouette is the part that survives 16 px.
\\def\\pgfsysdriver{{pgfsys-dvisvgm.def}}
\\documentclass[tikz,border=0pt]{{standalone}}
\\begin{{document}}
\\begin{{tikzpicture}}[x=1mm, y=1mm]
  \\draw[opacity=0,line width=0.01mm] (-0.2,-0.2) rectangle (10.2,10.2);

{fill(mark, "even odd rule", sm, sm, dx, dy)}
\\end{{tikzpicture}}
\\end{{document}}
"""
OUT.joinpath("brand-logo.tex").write_text(logo)
OUT.joinpath("brand-mark.tex").write_text(markt)
print("logo.tex lines:", logo.count("\n"), " mark.tex lines:", markt.count("\n"))
print("mark loops:", len(mark), "word_dim:", len(word_dim), "word_bold:", len(word_bold))
