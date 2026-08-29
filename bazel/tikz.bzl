# SPDX-License-Identifier: Apache-2.0
"""Build an SVG from a TikZ picture, hermetically.

`tikz_svg` compiles a standalone TikZ document with the pinned TeX tree from
`@texlive_bundle`, then converts the DVI to SVG with `dvisvgm`.

Neither TeX nor dvisvgm has to be installed on the machine: both come out
of the fetched distribution, and the whole tree is declared as action
inputs, so the action runs sandboxed.

`dvisvgm` is not part of the `rules_latex_host` toolchain contract (which
covers pdflatex, pdfinfo, pdfunite and gs), so both binaries are located
inside the bundle's `:files` filegroup rather than taken from a toolchain.

The DVI route is deliberate: `dvisvgm --pdf` needs ghostscript older than
10.01, while DVI input needs no ghostscript at all.

Example:

    tikz_svg(
        name = "hf-logo",
        src = "hf-logo.tex",
        texlive = "@texlive_bundle//:files",
    )
"""

def _find_binary(files, name):
    """Return the File named `name` under the distribution's bin/ directory."""
    for f in files:
        if f.basename == name and "/bin/" in f.path:
            return f
    fail("no '%s' in the TeX distribution; is it in texlive_packages?" % name)

def _scheme_style(ctx):
    """The <style> element injected into the SVG, or "" when disabled."""
    if not ctx.attr.scheme_style:
        return ""
    return ("<style>:root{color:%s}" +
            "@media(prefers-color-scheme:dark){:root{color:%s}}" +
            "</style>") % (ctx.attr.light_ink, ctx.attr.dark_ink)

def _tikz_svg_impl(ctx):
    files = ctx.attr.texlive[DefaultInfo].files.to_list()
    latex = _find_binary(files, "latex")
    dvisvgm = _find_binary(files, "dvisvgm")
    out = ctx.actions.declare_file(ctx.label.name + ".svg")

    # TEXMFVAR must be writable: kpathsea wants somewhere to put its caches and
    # the fetched distribution is read-only inside the sandbox.
    ctx.actions.run_shell(
        mnemonic = "TikzSvg",
        progress_message = "Rendering %s" % out.short_path,
        inputs = depset([ctx.file.src], transitive = [ctx.attr.texlive[DefaultInfo].files]),
        outputs = [out],
        command = """
set -euo pipefail
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
export TEXMFVAR="$work/texmf-var"
mkdir -p "$TEXMFVAR"

"$1" -interaction=nonstopmode -halt-on-error \
     -output-directory="$work" "$2" >/dev/null 2>&1 || {
  echo "latex failed; log follows:" >&2
  cat "$work"/*.log >&2 || true
  exit 1
}

stem="$(basename "$2")"
"$3" --no-fonts --currentcolor -o "$work/out.svg" "$work/${stem%.tex}.dvi" >/dev/null 2>&1

# --currentcolor rewrites the colours dvisvgm sets itself, but the pgfsys
# dvisvgm driver passes its own SVG through as raw specials, and those keep a
# literal #000. Rewrite them too: a mark that hard-codes black disappears on a
# dark background, which is the whole reason the drawing is stroked rather
# than filled.
sed -e "s/stroke='#000'/stroke='currentColor'/g"     -e "s/fill='#000'/fill='currentColor'/g"     -e 's/stroke:#000/stroke:currentColor/g'     -e 's/fill:#000/fill:currentColor/g'     "$work/out.svg" > "$4"

if grep -qE "(stroke|fill)(=.|:)#[0-9a-fA-F]{3,6}" "$4"; then
  echo "a hard-coded colour survived in $4:" >&2
  grep -oE "(stroke|fill)(=.|:)#[0-9a-fA-F]{3,6}" "$4" | sort -u >&2
  exit 1
fi

# currentColor makes the mark follow the palette only where CSS can reach
# it: inlined in a page. Referenced from an <img> or as a favicon the SVG
# is its own document, currentColor falls back to the initial value, and
# the mark renders black -- invisible on a dark tab strip or surface. The
# embedded stylesheet gives that document its own palette, keyed to the
# only theme signal an isolated SVG can see: prefers-color-scheme.
if [ -n "${5:-}" ]; then
  awk -v style="$5" '{print} /^<svg /{print style}' "$4" > "$4.styled"
  mv "$4.styled" "$4"
fi

# The knockout: re-emit the page subtree inside an SVG mask, with the
# drawing paths dropped and the glyphs forced black over a white ground,
# then apply that mask to the page. Ink survives everywhere except under
# the glyphs, so the text becomes a hole in the drawing rather than paint
# on top of it: the real background shows through, whatever it is. The
# glyphs sit inside dvisvgm's nested transform groups, which is why the
# whole subtree is copied rather than the <use> elements alone.
if [ -n "${6:-}" ]; then
  awk -v q="'" '
    NR==FNR {
      if (index($0, "<g id=" q "page1" q ">")==1) cap=1
      if (cap && index($0,"</svg>")!=1) {
        line=$0
        if (index(line,"<path")!=1) {
          gsub("fill=" q "currentColor" q, "fill=" q "black" q, line)
          gsub("stroke=" q "currentColor" q, "stroke=" q "none" q, line)
          sub(" id=" q "page1" q, "", line)
          u[n++]=line
        }
      }
      if (index($0,"viewBox=")>0 && vb=="") {
        rest=substr($0, index($0,"viewBox=")+9)
        vb=substr(rest, 1, index(rest,q)-1)
      }
      next
    }
    index($0,"</defs>")==1 {
      split(vb, v, " ")
      print "<mask id=" q "ko" q ">"
      print "<rect x=" q v[1] q " y=" q v[2] q " width=" q v[3] q \
            " height=" q v[4] q " fill=" q "white" q "/>"
      for (i2=0; i2<n; i2++) print u[i2]
      print "</mask>"
    }
    index($0,"<g id=" q "page1" q ">")==1 {
      $0="<g id=" q "page1" q " mask=" q "url(#ko)" q ">"
    }
    {print}
  ' "$4" "$4" > "$4.ko"
  grep -q "url(#ko)" "$4.ko" || { echo "knockout mask not applied" >&2; exit 1; }
  mv "$4.ko" "$4"
fi
""",
        arguments = [
            latex.path,
            ctx.file.src.path,
            dvisvgm.path,
            out.path,
            _scheme_style(ctx),
            "1" if ctx.attr.knockout else "",
        ],
        tools = [latex, dvisvgm],
    )
    return [DefaultInfo(files = depset([out]))]

tikz_svg = rule(
    implementation = _tikz_svg_impl,
    doc = "Compile a standalone TikZ document to SVG with a fetched TeX distribution.",
    attrs = {
        "src": attr.label(
            allow_single_file = [".tex"],
            mandatory = True,
            doc = "The standalone TikZ document to render.",
        ),
        "texlive": attr.label(
            mandatory = True,
            doc = "Filegroup holding the whole TeX tree, e.g. " +
                  "@texlive_bundle//:files.",
        ),
        "scheme_style": attr.bool(
            default = False,
            doc = "Embed a stylesheet that sets the SVG's own ink from " +
                  "prefers-color-scheme. Needed wherever the SVG renders " +
                  "as its own document (favicon, <img>): there " +
                  "currentColor cannot see the page and falls back to " +
                  "black, which disappears on a dark surface.",
        ),
        "light_ink": attr.string(
            default = "#1c2128",
            doc = "Ink under a light scheme (the site's --fg).",
        ),
        "dark_ink": attr.string(
            default = "#d7dde3",
            doc = "Ink under a dark scheme (the site's dark --fg).",
        ),
        "knockout": attr.bool(
            default = False,
            doc = "Turn the text into a hole in the drawing instead of " +
                  "paint on top of it, via an SVG mask built from the " +
                  "glyphs. For marks whose text sits on filled ink: a " +
                  "painted symbol would need to guess the ground colour; " +
                  "a hole shows the real ground through.",
        ),
    },
)
