# Voilà Floor Care — Interactive Home Website Strategy v1

Date: 29 September 2026
Working market: Adelaide, South Australia
Status: PRE-GENERATION / CONCEPT LOCK
Internal working name: The House of Voilà

## Objective

Turn the Voilà Floor Care homepage into a premium interactive residential journey. The visitor moves through one coherent Adelaide home by scrolling. Each room exposes the surfaces Voilà specialises in, and service hotspots open real HTML cards with concise service information and a Request a Quote CTA.

The experience positions Voilà as a specialist in surface-specific care, restoration and preservation rather than as a generic cleaning company.

The cinematic house is navigation and value framing. It is not evidence of completed work. Real Voilà case studies and before/after imagery must remain clearly identified as real customer-site proof.

## Adelaide visual direction

The house should feel recognisably Adelaide:
- refined character-home shell with a sensitively renovated interior;
- sandstone / stone cues rather than an anonymous international mansion;
- premium wool carpet and rugs;
- genuine leather and quality upholstery;
- tiled and natural-stone wet areas;
- indoor-outdoor connection;
- terracotta or masonry terrace;
- mature pots and restrained planting;
- bright South Australian daylight.

The property should be affluent but attainable. Avoid hotel, display-home, mega-mansion and ultra-luxury showroom cues.

## Synthetic customer panel

This is a synthetic qualitative stress-test, not recruited human research and not statistical evidence.

1. Burnside professional family, 40s — renovated family home, porcelain/tile, wool carpet, leather sectional. Wants low risk and polished service.
2. Unley heritage-villa owner, 50s–60s — stone, terrazzo, terracotta and older finishes. Values preservation and material knowledge.
3. Norwood design-conscious renovator, 30s–40s — premium bathroom, rug and upholstery. Expects tasteful design and concise technical proof.
4. Adelaide Hills family with pets — wool carpet and rugs. Needs stain/odour capability without rough treatment.
5. Glenelg/coastal homeowner — tile, stone and outdoor paving. Concerned with wear and exterior maintenance.
6. North Adelaide downsizer — Persian/Oriental rug and leather furniture. Wants specialist handling and direct knowledgeable contact.
7. Mitcham multigenerational household — high-use tile/grout plus carpet. Wants clear scope and a simple quote process.
8. Prospect character-home owner — wants several surfaces refreshed by one competent specialist.
9. Prestige property manager — values consistency, photos, documentation and repeatability.
10. Interior designer / architect referrer — cares about substrate identification, finish compatibility and reputational risk.
11. Boutique accommodation operator — upholstery, carpet, tile and periodic specialist floor care; values downtime control.
12. Aspirational mainstream homeowner — likes premium results but will disengage if the site looks unaffordable or exclusive.

### Panel consensus

Strongest positives:
- Room-to-room discovery is more memorable than a generic service grid.
- Customers understand their own surfaces before they understand industry terminology.
- Material detail communicates expertise better than broad professional-cleaning claims.
- One coherent house feels far more premium than a montage of unrelated AI rooms.

Risks to design out:
- A mansion can signal not-for-me and imply excessive pricing.
- Hotspots must not feel like a game.
- Mobile cards must not cover the surface just selected.
- Synthetic visuals must never be used as before/after proof.
- Video must not block quote access or make the mobile site heavy.
- A reduced-motion/static route must carry the same information.

Conversion preferences:
- Primary CTA: Request a Quote.
- Secondary path: Call.
- No price inside cinematic hotspot cards.
- Real case studies should follow immediately after the hero when content is available.
- Full service pages remain conventional, indexable pages for SEO and detailed technical information.

## Interactive journey

### Scene 01 — Threshold / Living
Surface story: tile & grout + quality wool rug.
Hotspots: Tile & Grout Cleaning; Rug / Wool Care.
End direction: camera faces the physical opening to Scene 02.

### Scene 02 — Lounge / Theatre
Surface story: wool carpet + leather + upholstery.
Hotspots: Carpet Cleaning; Wool Specialist Care; Leather Cleaning & Conditioning; Upholstery Cleaning.
End direction: corridor/master-suite transition.

### Scene 03 — Master Suite
Surface story: carpet + upholstery / mattress.
Hotspots: Carpet Cleaning; Upholstery / Mattress Care.
End direction: ensuite doorway centred and reachable.

### Scene 04 — Ensuite
Surface story: tile, grout, shower and natural stone.
Hotspots: Tile & Grout Cleaning; Shower / Grout Restoration; Natural Stone Cleaning & Protection.
End direction: terrace/glazed-door transition.

### Scene 05 — Terrace
Surface story: terracotta + natural stone + sealing/restoration.
Hotspots: Terracotta Cleaning & Resealing; Natural Stone Cleaning & Protection; Floor Sealing / Recoating.
End state: stable final frame with surface foreground and negative space for CTA.

## Services outside the cinematic hero

Do not force the entire service catalogue into the house film. Follow the journey with a conventional More surfaces we care for section:
- Vinyl & Resilient Floor Care
- Concrete & Epoxy Floor Care
- Gym & Rubber Flooring
- Commercial, Strata & Contract Floor Care
- Recurring / facilities maintenance

## Interaction model

The film is visual background only. All service copy and actions are real semantic HTML.

Desktop:
- page scroll scrubs the film;
- a subtle anchored marker appears only when the associated surface is readable;
- hover may show the service name;
- click opens the card;
- card contains title, short explanation, View Service and Request a Quote.

Mobile:
- tap, never hover dependency;
- use a bottom sheet or compact anchored card;
- sticky Request a Quote plus phone path;
- first-frame poster loads immediately;
- lighter mobile video assets.

Accessibility:
- prefers-reduced-motion gets a static sequential version with no forced video fetch;
- keyboard access for markers/cards;
- semantic service headings remain in DOM reading order;
- no copy burned into video;
- no generated audio.

## Durable production architecture

GitHub: Zalahk417/VOILA-FLOOR-CARE
- master prompts;
- machine-readable asset manifest;
- model parameters;
- version history;
- approval state;
- deployable optimised assets where practical.

Cloudflare:
- production site delivery;
- serve final optimised media;
- use R2 for heavy masters if appropriate;
- never hotlink temporary model-hosted generation URLs in production.

Notion:
- human-readable creative brief;
- customer-panel findings;
- market decisions;
- approval/rejection notes;
- links back to canonical GitHub artefacts.

GitHub is the machine-readable creative source of truth. Notion is the human decision layer.

## Asset naming

Pattern:
vfc-house-sSCENE-SLUG-vVERSION-MODEL-RESOLUTION.ext

Examples:
vfc-house-s01-entry-v01-kling3turbo-720p.mp4
vfc-house-s04-ensuite-v02-kling3turbo-1080p.mp4
vfc-house-storyboard-v01-gptimage2-1k.png

## Continuity contract

This is a five-leg journey through the same house.

For every final leg:
1. Generate the current leg.
2. Extract its actual final rendered frame.
3. Approve the boundary frame.
4. Use that exact frame as the next scene start image.
5. Preserve camera height, lens, light direction, colour response and forward velocity.
6. Never generate the five production legs as independent clips.

## Production gates and current Higgsfield credit estimates

G0 — Research and creative system
Status: COMPLETE
Cost: 0 credits.

G1 — World/storyboard lock
One 16:9 six-panel storyboard.
Budget: 1–2 credits.

G2 — Motion-grammar proof
One 15-second 16:9 720p Kling 3.0 Turbo walkthrough.
Current estimate: 22.5 credits.
Purpose: validate camera speed, material fidelity, world tone and scroll feel.

G3 — Final five-leg production
Five sequential 5-second 1080p Kling 3.0 Turbo scenes.
Current estimate: 10 credits each / 50 credits total.

G4 — Contingency
Reserve two 5-second 1080p re-rolls.
Budget: 20 credits.

Target controlled envelope:
Storyboard 1 + motion proof 22.5 + final legs 50 + contingency 20 = 93.5 credits.

Hard ceiling without new owner approval: 100 credits.

Optional premium upgrade:
Seedance 2.5 should be selective only.
Current estimates:
- 5 seconds 720p: 35 credits.
- 5 seconds 1080p: 60 credits.
Five 720p Seedance legs would be 175 credits before retries, so this is not the baseline.

## Spending gate

Connected Higgsfield state observed 29 September 2026:
- 1.85 available credits;
- Free plan;
- 100-credit trial offered/pending;
- no active unlimited allowance.

This does not match the owner's expectation of roughly US$50 already funded elsewhere.

No paid generation is authorised from this connected workspace until the balance/workspace identity is reconciled or the owner explicitly approves use of the pending trial.

## Post-hero page structure

1. Interactive House of Voilà.
2. Real Voilà proof: before/after and case studies.
3. Premium service families with short technical explanations.
4. More surfaces we care for.
5. Why surface-specific care matters.
6. Adelaide residential/commercial pathways.
7. Quote CTA and phone path.
8. Terms, privacy and footer.

## Definition of done

The homepage is not complete until:
- final footage passes continuity review;
- desktop and mobile encodes and exact posters exist;
- reduced-motion fallback works;
- markers are keyboard and touch accessible;
- cards link to canonical service content;
- Request a Quote reaches the approved ServiceM8 path;
- generated house imagery is never described as a real customer job;
- real before/after evidence is clearly separated;
- production Cloudflare site is smoke-tested on desktop and mobile;
- no dead media URLs, missing assets or visible layout jumps remain.
