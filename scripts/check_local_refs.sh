#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
#
# Preflight: fail if any built page references a local asset (src/href
# starting with "/") that the built site does not contain. Catches the
# broken-image / dead-internal-link class of bug -- including the kind a
# racy merge introduces by dropping a file -- before it can deploy.
#
# Usage: scripts/check_local_refs.sh <site-dir>
set -o errexit -o nounset -o pipefail
site="${1:?usage: check_local_refs.sh <site-dir>}"

missing=0
# Extract every root-relative src="/..." and href="/..." from every HTML
# page, strip query/fragment, and check the file exists in the site tree.
while IFS= read -r ref; do
  # skip directory-style internal links (e.g. /post/, /about-us/): those
  # resolve to <dir>/index.html, checked separately below.
  path="${ref%%[?#]*}"
  case "$path" in
    */) target="${site}${path}index.html" ;;
    *.*) target="${site}${path}" ;;        # has an extension: a file
    *)  target="${site}${path}/index.html" ;;  # extensionless: a page
  esac
  if [ ! -e "$target" ]; then
    echo "::error::broken local reference: ${path} (no ${target#$site})" >&2
    missing=$((missing + 1))
  fi
done < <(
  grep -rhoE '(src|href)="/[^"]*"' "$site" --include='*.html' \
    | sed -E 's/.*="([^"]*)"/\1/' \
    | sort -u
)

if [ "$missing" -gt 0 ]; then
  echo "::error::${missing} broken local reference(s); refusing to deploy" >&2
  exit 1
fi
echo "local reference check: all references resolve"
