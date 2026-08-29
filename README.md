# Hugo rental site template

[![Build pages](https://github.com/filmil/hugo-rental-template/actions/workflows/build-pages.yaml/badge.svg)](https://github.com/filmil/hugo-rental-template/actions/workflows/build-pages.yaml)
[![Test a pull request](https://github.com/filmil/hugo-rental-template/actions/workflows/test-pages.yaml/badge.svg)](https://github.com/filmil/hugo-rental-template/actions/workflows/test-pages.yaml)

A Bazel-built Hugo marketing and blog site for a short-term-rental
business. It is paired with a separate external booking engine that this
repository does not build; the marketing site links out to it.

The rendered site is meant to be served from a host of your choice
(`www.yourdomain.com`), with booking on its own property
(`book.yourdomain.com`). Both hostnames are placeholders; replace the
tokens described in "How to make it yours" below.


## Live demo

CI builds this repository and deploys the rendered site to a separate
results repository, [filmil/hugo-rental-template-site](https://github.com/filmil/hugo-rental-template-site),
on every push to `main`. That repo holds the generated HTML only; point
`external_repository` in `.github/workflows/build-pages.yaml` at your own
deploy target to make it yours.


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


## Contributing

This template began as the engine behind one specific vacation-rental site.
It no longer tracks that site.
It now stands on its own as a general-purpose starting point that anyone can
use, so contributions are welcome and wanted.

If you build something with it, or find a rough edge, please open an issue or
a pull request:

- Bug reports and fixes.
- Improvements to the theme, the build, or the docs.
- New reusable examples, as long as they stay generic and carry no
  brand-specific content.

A few practical notes:

- Keep the template brand-neutral.
  Real names, domains, keys, and photos belong in a fork, not here.
- Make sure `bazel build //:site` passes before you open a pull request.
- Keep each pull request focused on a single change.

The project is Apache-2.0 licensed, so your contributions are too.
