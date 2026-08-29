# Spec: the brand logo as build-generated SVG


## Goal

Carry the brand logo as a generic mark plus wordmark, authored as TikZ
sources and rendered to SVG at build time. The SVG is the single source
used for the site logo, the favicon, and any other derived resources.


## Sources

The logo lives as two TikZ files in `//static/logo`:

* `brand-logo.tex` -- the full lockup: the mark plus the wordmark.
* `brand-mark.tex` -- the mark alone on a square canvas, for the favicon.

If you are starting from a raster logo, `//scripts:trace_logo.py` traces a
JPEG or PNG into these TikZ sources. Marching squares at the 128 grey level
with linear interpolation follows the antialiasing, so the contours are
sub-pixel smooth; Douglas-Peucker simplification keeps them compact. Each
closed loop becomes a TikZ subpath, and even-odd filling turns inner loops
into holes.

The holes are the point. Counters and interior negative space are holes in
the ink, not white paint. Painted white lies on any surface that is not
white; a hole shows the real ground through. One file therefore works on
the page, on a dark footer, and on a dark tab strip.


## Build

`//bazel:tikz.bzl` provides `tikz_svg`: latex plus dvisvgm out of a pinned
TeX Live bundle, hermetic, with hard-coded colours rewritten to
`currentColor` and the build failing if one survives. Ink is black on light
surfaces and white on dark ones, so the same file adapts to the surface it
sits on.

Targets:

* `//static/logo:brand-logo`, the full lockup, published at
  `/logo/brand-logo.svg`.
* `//static/logo:brand-mark`, the mark alone on a square canvas for the
  favicon, published at `/logo/brand-mark.svg`. The wordmark is dropped
  there because it reads as noise at 16 px.
* `brand-logo-black` and `brand-mark-black`, fixed-ink companions whose
  embedded stylesheet pins both colour schemes to black. For print, for
  uploads to systems that composite the mark themselves, and for surfaces
  known to be light.

`//static/logo` is its own Bazel package, so the site's `static` glob cannot
reach into it: the `.tex` sources, the BUILD file and the tracer are never
published. Only the generated SVGs are, via labels in `//:site`.


## Follow-ups

* Point the theme's `logo` and `favicon` params at the two SVGs.
* If the external booking engine accepts a logo upload, offer it the
  fixed-ink `brand-*-black` SVG so its footer renders the mark cleanly.
