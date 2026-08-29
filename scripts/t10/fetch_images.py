#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Resolve IMAGE:<query> placeholders in a generated post.

For each `<img src="IMAGE:query">`, search Wikimedia Commons for a suitably
licensed photo, download and resize it into static/img/auto/, rewrite the
src to the local path, and append the required attribution to the figure's
caption. Records provenance in static/img/auto/MANIFEST.json.

Usage: fetch_images.py <post.md>

Only CC0, CC BY, CC BY-SA and public-domain images are accepted; anything
else is skipped and the figure is removed so nothing unlicensed ships.
"""
import sys, re, json, io, hashlib, urllib.request, urllib.parse, pathlib

UA = {"User-Agent": "YOURBRANDSiteBot/1.0 (contact@yourdomain.com)"}
OK_LICENCES = ("cc0", "public domain", "cc by", "cc-by")
OUT = pathlib.Path("static/img/auto")

def api(params):
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30))

def _search_once(query):
    r = api({"action":"query","list":"search","srsearch":query,"srnamespace":"6",
             "srlimit":"12","format":"json"})
    return [h["title"] for h in r["query"]["search"]
            if h["title"].lower().endswith((".jpg",".jpeg",".png"))]

def find(query):
    # Try the query, then progressively broader forms: over-specific queries
    # tend to surface book scans and maps instead of photos.
    words = query.split()
    variants = [query]
    # Broaden by dropping trailing descriptive words, but never below the
    # first three: over-broadening can drop the proper-noun context and match
    # an unrelated place with a similar name. Keep the leading proper nouns.
    for k in (5, 4, 3):
        if len(words) > k:
            variants.append(" ".join(words[:k]))
    titles = []
    for v in variants:
        titles = _search_once(v)
        if titles:
            break
    if not titles:
        return None
    r = api({"action":"query","titles":"|".join(titles[:12]),"prop":"imageinfo",
             "iiprop":"url|size|extmetadata","format":"json"})
    best = None
    for p in r["query"]["pages"].values():
        ii = p.get("imageinfo",[{}])[0]
        if not ii or ii.get("width",0) < 1000:
            continue
        lic = ii["extmetadata"].get("LicenseShortName",{}).get("value","")
        if not any(k in lic.lower() for k in OK_LICENCES):
            continue
        artist = re.sub(r"<[^>]+>","",ii["extmetadata"].get("Artist",{}).get("value","")).strip()
        cand = {"url":ii["url"],"title":p["title"],"license":lic,
                "license_url":ii["extmetadata"].get("LicenseUrl",{}).get("value",""),
                "artist":artist or "Unknown","page":ii["descriptionurl"],"w":ii["width"]}
        if best is None or cand["w"] > best["w"]:
            best = cand
    return best

def main():
    from PIL import Image
    post = pathlib.Path(sys.argv[1])
    text = post.read_text()
    OUT.mkdir(parents=True, exist_ok=True)
    manp = OUT/"MANIFEST.json"
    man = json.loads(manp.read_text()) if manp.exists() else {"images":[]}

    used_pages = set()

    def replace_figure(m):
        block = m.group(0)
        qm = re.search(r'src="IMAGE:([^"]+)"', block)
        if not qm:
            return block
        query = qm.group(1)
        hit = find(query)
        if not hit:
            print(f"  no licensed image for {query!r}; dropping figure", file=sys.stderr)
            return ""  # ship nothing rather than something unlicensed
        if hit["page"] in used_pages:
            print(f"  {query!r} resolved to an image already used in this post; dropping figure", file=sys.stderr)
            return ""
        used_pages.add(hit["page"])
        data = urllib.request.urlopen(urllib.request.Request(hit["url"], headers=UA), timeout=180).read()
        im = Image.open(io.BytesIO(data)).convert("RGB")
        im.thumbnail((1600,1600), Image.LANCZOS)
        slug = hashlib.sha1(hit["page"].encode()).hexdigest()[:12] + ".jpg"
        im.save(OUT/slug, quality=82, optimize=True)
        credit = f'Photo: <a href="{hit["page"]}">{hit["artist"]}</a>'
        credit += f', <a href="{hit["license_url"]}">{hit["license"]}</a>' if hit["license_url"] else f', {hit["license"]}'
        credit += ", via Wikimedia Commons."
        man["images"].append({"file":f"auto/{slug}","query":query,"source":hit["page"],
            "author":hit["artist"],"license":hit["license"],"license_url":hit["license_url"]})
        block = block.replace(f'src="IMAGE:{query}"', f'src="/img/auto/{slug}"')
        block = re.sub(r"(</figcaption>)", " " + credit + r"\1", block, count=1)
        # if the caption had no credit slot, inject before </figcaption>
        if credit not in block:
            block = block.replace("</figcaption>", " " + credit + "</figcaption>")
        return block

    text = re.sub(r"<figure>.*?</figure>", replace_figure, text, flags=re.S)
    post.write_text(text)
    manp.write_text(json.dumps(man, indent=1) + "\n")
    remaining = text.count("IMAGE:")
    if remaining:
        print(f"  WARNING: {remaining} unresolved IMAGE: placeholder(s)", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
