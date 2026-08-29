# Booking-engine reference snapshot

This folder is a reference snapshot of your external booking engine's site
(e.g. Hostaway, Lodgify, Guesty, or OwnerRez): its head script, design
settings, and exported pages. It is kept here so the Hugo marketing site and
the booking site stay consistent with each other.

**It is not built by Hugo.** Nothing in this directory is part of the Hugo
render; it is stored under `third_party/` because its system of record is an
external service, not this repository. Replace these files with your own
engine's export.

## What to put here

| File | What it is | Where it comes from |
| --- | --- | --- |
| `head-script.original.html` | The engine's "Head script" field as exported: custom CSS, analytics tags, and consent loader. Keep this as the revert baseline. | Your engine dashboard: Booking Website -> Scripts & Widgets -> Head script |
| `head-script.repaired.html` | A cleaned-up head script keyed to stable selectors, ready to paste back into the engine. | Authored here |
| `design-settings.json` | The engine's design settings: colors, fonts, logo/favicon URLs, hero, and navigation. Keys illustrate the shape; values are placeholders. | Your engine dashboard: Booking Website -> Design |
| `assets/` | Logo, favicon, and hero image the engine serves, plus `MANIFEST.json` recording each asset's source URL and checksum. | See `assets/MANIFEST.json` |
| `pages/about-us.html` | The About page's exported `<main>` content. | Your engine dashboard: Booking Website -> Pages |
| `pages/privacy-policy.html` | The privacy page's exported content. | Booking Website -> Pages |
| `pages/terms-and-conditions.html` | The terms page's exported content. | Booking Website -> Pages |
| `pages/contact-details.txt` | Company, email, phone, and address as shown on the contact page. | Booking Website -> Pages |

All values in these files are generic placeholders. Swap in your own brand,
domain, analytics id (`G-XXXXXXXXXX`), consent-manager loader, keys/tokens
(`YOUR_..._KEY`), and asset URLs when you adopt the template.

## Head script

A booking-engine head script usually bundles three things: custom CSS that
restyles the engine's rendered widgets, an analytics or tag-manager tag, and
a cookie-consent (CMP) loader. Both head-script files here show these three
parts as clearly labelled placeholders rather than working snippets.

Engines that render with styled-components emit class names that rotate on
each deployment, so target stable element selectors or your own element ids
(for example `#booking-widget`) rather than the rotating hashes.

## Reverting a change

Keep `head-script.original.html` as the known-good baseline. To undo an edit,
paste it back into your engine's "Head script" field and republish.
