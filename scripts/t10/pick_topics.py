#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Pick the next N unwritten topics, round-robin across destinations.

A topic is written if content/post/ contains a file whose slug front-matter
equals the topic slug. Prints one TSV row per pick:
  dest \t slug \t title_hint \t season \t prefer_images \t listing \t banned
"""
import sys, pathlib, re

def load_topics(path="scripts/t10/topics.yaml"):
    # Minimal YAML read (no pyyaml dependency): parse the known shape.
    import yaml  # try the real thing first
    return yaml.safe_load(pathlib.Path(path).read_text())

def written_slugs():
    slugs = set()
    for f in pathlib.Path("content/post").glob("*.md"):
        m = re.search(r'^slug:\s*(\S+)', f.read_text(), re.M)
        if m:
            slugs.add(m.group(1).strip().strip('"\''))
    return slugs

def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    data = load_topics()
    done = written_slugs()
    # queues per destination, unwritten only
    queues = []
    for d in data["destinations"]:
        q = [t for t in d["topics"] if t["slug"] not in done]
        queues.append((d, q))
    picks, i = [], 0
    while len(picks) < n and any(q for _, q in queues):
        d, q = queues[i % len(queues)]
        if q:
            t = q.pop(0)
            banned = "; ".join(d.get("banned", [])) or "none"
            picks.append((d["name"], t["slug"], t["title_hint"], t.get("season","any"),
                          d["prefer_images"], d["listing_filter"], banned))
        i += 1
        if i > 10000:
            break
    for p in picks:
        print("\t".join(p))

if __name__ == "__main__":
    main()
