# House of Voilà positioning audit — 1 October 2026

Baseline: `0c17a1bf766124cf78e17fad571f700053dc0767`.
Scope: homepage and `/cinematic/`, approved welcome asset, surface markers, existing service destinations and terrace enquiry layout. Existing backend/lead transport retained. No test enquiry submitted and no customer photo transmitted.

## Findings and repairs

- Fixed a malformed quote in the welcome image URL. Restored the approved technician at the start, a readable welcome card, upward scroll fade, and reverse-scroll restoration. Scene controls stay hidden/inert during the opening.
- Previous marker timings used scroll ranges unrelated to the actual film scenes. Recalibrated all surfaces against the 854×480 master film and decoded film seconds: entry tile, living rug/tile, lounge carpet/couch, hallway carpet, ensuite shower/stone, terrace terracotta.
- Overlay labels now follow presented video frames, not unfulfilled seek requests. Coalesced seeking prevents rapid/reverse scrolling from advancing labels ahead of the film.
- Corrected coordinates for `object-fit: cover`, viewport resizing and the terrace zoom. Mobile markers move to the visible portion of the same surface when its central anchor is cropped. Entirely cropped surfaces do not receive a misleading floating marker; the corresponding scene link remains available.
- All scene links are direct service-page links. Added the missing rug destination and conventional rug link. The build fails if any cinematic service destination is missing.
- Added a natural-stone floor marker to the ensuite. The shower marker correctly links to the existing tile/grout service that includes shower care.
- Repositioned the terrace form, retained its internally scrollable mobile layout, photo input and direct telephone link, and kept terracotta links clear of the form. Removed the duplicate floating quote button at the final stop.
- Versioned cinematic styles/scripts to avoid old cached presentation. Added reduced-motion and media-error static layouts and inert states for inactive controls.

## Verification

- Static website build: pass, 43 files.
- Website acceptance tests: 6/6 pass locally.
- Timeline/coordinate/link tests: 3/3 pass locally, including forward/reverse scene boundaries and mobile cropping.
- JavaScript syntax and diff whitespace checks: pass.
- Full Python suite locally: 25 pass, one pre-existing Windows SQLite cleanup file-lock error. Linux CI is the required full-suite gate before merge.
- Local browser screenshots inspected at 1440×900 and 390×844: welcome, rug/tile, couch/carpet, shower/stone and terrace. Reverse scroll restores the welcome; no warning/error console entries observed at the final stop. These are local-preview screenshots, not production evidence.
- Live visual QA is blocked because access to `www.voilafloor.com.au` was explicitly denied by the browser. Do not label production visual QA as PASS or bypass that denial. GitHub Actions and the Cloudflare Pages check can establish build/deployment status, but cannot establish live rendered positioning.

## Separate content issue

The cinematic homepage says Adelaide, while legacy service content references Geraldton. The user's current request and screenshots do not establish a new business-location brief; this patch does not silently relocate the business or rewrite legacy location claims. Confirm the intended service area in a separate content pass.
