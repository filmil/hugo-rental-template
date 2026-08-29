# Spec: build the site with Bazel


## Goal

Build and publish this Hugo site with Bazel, so nothing needs to be
installed on a developer machine or a CI runner beyond Bazel itself.


## Requirements

* Build with `bazel build //:site`. The output tree is what CI deploys, and
  it must match what a bare `hugo` run would write into `public/`. Verify
  with `diff -r` when migrating.
* Hugo is pinned to a fixed extended version, downloaded by the build rather
  than installed on the machine or the CI runner.
* `rules_hugo` is consumed as an overlay over `stackb/rules_hugo`, patched
  for a modern Bazel (modern providers, exec cfg).
* The theme carries its own `hugo_theme` target.
* CI builds with Bazel and deploys `bazel-bin/site`; no hugo or node setup
  steps remain.


## Notes on the theme

`rules_hugo` stages a theme under `themes/<theme_name>/` by stripping the
theme package's path from each of its source files. That only works when the
`hugo_theme` target lives in the theme's own directory. A git submodule
cannot carry a `BUILD.bazel` belonging to this repository, so the theme is
vendored verbatim into `//third_party/rentaltheme` instead of being a
submodule.

If the theme is later maintained in a repository of its own, the
`hugo_theme` target should move upstream and a vendoring tool can keep the
in-tree copy in sync.
