# Hugo rental site template

A Bazel-built Hugo marketing and blog site for a short-term-rental
business. It is paired with a separate external booking engine that this
repository does not build; the marketing site links out to it.

The rendered site is meant to be served from a host of your choice
(`www.yourdomain.com`), with booking on its own property
(`book.yourdomain.com`). Both hostnames are placeholders; replace the
tokens described in "How to make it yours" below.


## Building

The site is built by Bazel. Nothing needs to be installed on the machine
beyond Bazel itself -- the pinned hugo (extended) is downloaded by the
build.

```sh
bazel build //:site
```

The rendered site lands in `bazel-bin/site`.

To preview it locally with hugo's dev server:

```sh
bazel run //:serve
```

To format the Bazel files:

```sh
bazel run //:buildifier
```


## Layout

* `config.yaml` -- the Hugo site configuration.
* `content/` -- the site's pages and blog posts.
* `layouts/` -- site-local overrides merged over the theme's layouts. Holds
  the Google Analytics tag (`partials/head_custom.html`) and the MathJax
  loaders (`partials/foot_custom.html`).
* `static/` -- files copied verbatim to the site root, including the
  booking redirect under `static/r/`.
* `static/logo/` -- the brand logo as TikZ sources (`brand-logo.tex`,
  `brand-mark.tex`), rendered to SVG at build time by `bazel/tikz.bzl` and
  published under `/logo/`. See `ai/logo_spec.md`; regenerate the sources
  with `scripts/trace_logo.py`.
* `data/` -- YAML data files that drive listings and other structured
  content.
* `third_party/rentaltheme/` -- the vendored Hugo theme, carrying its own
  `hugo_theme` target. It is vendored rather than a git submodule because
  Bazel needs a `BUILD.bazel` inside the theme directory, and a submodule
  cannot carry one belonging to this repository.
* `third_party/booking-engine/` -- a reference snapshot of the external
  booking engine's site, kept for parity checks. Nothing here builds it.


## Deployment

CI builds `//:site` and pushes the resulting `bazel-bin/site` tree to a
deploy repository or host of your choice. A convenient way to do this is
`peaceiris/actions-gh-pages`, used purely for its push-to-another-repo
behaviour; the tree that lands there is what your web server publishes.
Configure anything server-side (redirects, headers, TLS) on that host, not
in this repository. Run the same build on pull requests without deploying
to catch breakage before merge.


## How to make it yours

1. Replace the `YOURBRAND` token and the `yourdomain.com` /
   `www.yourdomain.com` / `book.yourdomain.com` hostnames throughout with
   your brand and domains.
2. Set your Google Analytics tag: replace the `G-XXXXXXXXXX` placeholder in
   `layouts/partials/head_custom.html`.
3. Swap the logo: replace the TikZ sources in `static/logo/`
   (`brand-logo.tex`, `brand-mark.tex`), or retrace your own raster with
   `scripts/trace_logo.py`.
4. Replace the placeholder images under `static/img/`.
5. Edit `data/*.yaml` to describe your own properties and listings.
6. Write real content under `content/`.
7. Replace the placeholder legal pages (privacy, terms) with your own.
