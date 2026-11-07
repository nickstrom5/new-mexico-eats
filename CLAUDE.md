# New Mexico Eats (nm-eats) — notes for Claude Code sessions

Built 2026-11-06 by a side session for Nick's "build the 17 remaining states" (group: Massachusetts, New Hampshire, New Mexico, Montana),
ported from `../ma-eats/` (itself from `../va-eats/`, with every fix to 2026-11-05: delivery-only brands hidden, the shared website
blocklist and `link_blocklist.py`, the Share link to `Links.site + explore/#p=<id>`, OTA data, the widened adult rule, the Denny's
delivery-brand guard, Utah's street-word merge fix, the exact-outline county lookup). Local only: git-ignored data, no repo, no remote,
nothing published. Sources and calibration: `playbook/12-sources.md`. Brand: `playbook/05-naming.md` — **final** (Nick's decisions, 2026-11-07: "New Mexico Eats: Red or Green" on the App Store, Home Screen "New Mexico Eats"; a red chile pod icon, concept A, on
turquoise; chile red #8C1D18, green chile #3F6B22, turquoise #0E7C86, chile yellow #FFD700 fill only, adobe #FAF4E6; a band of the
Sandia ridge over red and green stripes). No Zia sun symbol anywhere.

## New Mexico is different
- **No Google data at all**, in either build (Nick's rule for these four states): `listings.py` reads no UCSD snapshot.
- **Official data:** only the City of Albuquerque publishes current inspections, as a weekly PDF replaced at the same URL.
  `fetch_official.py` archives each edition (`data/raw/official/albuquerque/chpd-<week end>.pdf` and its text, through
  `pipeline/pdf_text.swift`, macOS PDFKit); **run it every week** so the archive grows (only the week ending 2026-10-31 so far).
  `official.py` reads every archived edition: each permit, each visit (date, type, result) and the result posted now (Approved,
  Conditional Approved, Unsatisfactory, Closed: the city's sticker). Places show the posted result, dated, labeled official; never a
  computed grade. Legal names before "DBA" are dropped. History before the archive needs a records request (cabq.nextrequest.com),
  NMED's results need registration or IPRA, and the liquor licensee list is a $100 IPRA copy: all **Nick's call**. "Serves alcohol" is
  "—" everywhere. Tribal land is outside state and city inspection.
- **Towns:** Overture's 131 New Mexico locality outlines (cities, towns, villages and some census places); a listing outside every
  outline (most of the state is unincorporated) keeps its postal town. A different postal name stays as `area` (`ar`). Counties (33)
  only split the detail files into 6 regions.
- **Honors:** MICHELIN Guide American Southwest (August 2026): 5 Bib Gourmands and 7 recommended, no stars. James Beard: America's
  Classics Mary & Tito's (2010) and Rancho de Chimayó (2016), Best Chef: Southwest Fernando Olea (Sazón, 2022) and Mark Kiffin (The
  Compound, 2005), finalists Bow & Arrow (2026), Mesa Provisions (2026), Campo at Los Poblanos (2025), and the 2025-26 semifinalists.
  The Shed's and Cafe Pasqual's America's Classics are leads (no jamesbeard.org page found).
- **Guides** (tags in `newmexico.py` TAGS, bits 1, 2, 4, 8): green chile cheeseburgers, breakfast burritos and Culinary Treasures, all
  from New Mexico True's own trail listings (`data/research/raw/nmtrue-trails-2026-11-06.json`, read in the built-in browser), each stop
  kept only when one open map listing matches it at the trail's address (`build_research.py`, by name or by street number and a similar
  name, the kept places first, then an open Overture listing); oldest (3 dated places: El Farol 1835, La Cita 1940, The Pantry 1948; no
  oldest page on the site until there are 4). Leads in `data/research/app/LEADS.md`. Never write "Hatch" as a chile claim (the Chile
  Advertising Act).
- **Venues:** the Sunport's terminal (2200 Sunport Blvd and its box), the bases and labs, the stadiums and arenas, the fairgrounds, the
  prisons; casinos are soft venues.
- **Inspections:** only on place pages (no inspection list among the guides), per Nick's 11-05 call.

## Rebuild
```bash
cd pipeline
../.venv/bin/python check_sources.py URL...   # a new host first
../.venv/bin/python fetch_overture.py && ../.venv/bin/python fetch_extras.py && ../.venv/bin/python fetch_official.py   # weekly
../.venv/bin/python geocode_official.py && ../.venv/bin/python listings.py && ../.venv/bin/python calibrate.py
../.venv/bin/python newmexico.py && ../.venv/bin/python build_research.py && ../.venv/bin/python newmexico.py
NM_APP=1 ../.venv/bin/python newmexico.py && cd .. && cp data/app/places.json data/app/detail-*.json NewMexicoEats/Resources/
cd pipeline && ../.venv/bin/python check_websites.py && ../.venv/bin/python check_websites.py --retry-transient && cd ..   # then re-export
.venv/bin/python scripts/make-site.py && .venv/bin/python scripts/publish_app_data.py && .venv/bin/python scripts/publish_app_data.py --check
.venv/bin/python scripts/qa-site.py
```
(`listings.py` before `calibrate.py`; `newmexico.py` once before `build_research.py`, which matches names against `site/newmexico.json`.)
The `.venv` is a copy of wy-eats' (python.org framework Python 3.12, md-eats' package versions).

## App, site, screenshots
- App: `NewMexicoEats/` (XcodeGen `project.yml`, bundle `com.newmexicoeats.ios`, display "New Mexico Eats"), tests in `NewMexicoEatsTests/`
  (data guards; the outline with El Paso, Ciudad Juárez, Palomas, Farwell, Trinidad, Cortez and Sanders outside) and
  `NewMexicoEatsUITests/`. Run with `DEVELOPER_DIR="/Applications/Xcode 1.app/Contents/Developer"`; unit tests may use
  `CODE_SIGNING_ALLOWED=NO`, UI tests need the signed runner (no flag). Archive only with Xcode 1.app (27.2, 27B52). Run `xcodegen
  generate` whenever the set of `Resources/*.json` files changes.
- Site: `scripts/make-site.py` writes `docs/` and `playbook/site-numbers.json`; `scripts/explore.js` is the web app (its map projection
  and `NM_RINGS` outline are New Mexico's); `scripts/qa-site.py` the QA. Site URL for now: nickstrom5.github.io/new-mexico-eats (no
  CNAME). Rebuild the site before the unit tests (`ShareLinkTests` reads `docs/`).
- OTA data: `docs/data/app/` via `scripts/publish_app_data.py` (`../OTA-DATA.md`).
- Screenshots: `scripts/capture-screenshots.sh <sim>` (ScreenshotMode pins Albuquerque's Old Town Plaza; Santa Fe's Plaza for honors),
  then `scripts/site-images.sh`, then make-site + qa-site. App Store frames: `scripts/appstore-screenshots.py`. Icons:
  `scripts/icon-concepts.swift` and `scripts/make-brand.swift` (concept A).

## Status (2026-11-07): ready to publish
- Data: 4,262 places, 4,099 restaurants in 154 towns (CBP 3,935); 82 hand-checked on a guide (34 green chile cheeseburgers, 25 breakfast
  burritos, 25 Culinary Treasures), 3 dated oldest, 27 MICHELIN or James Beard honorees, 30 Albuquerque permits with posted results.
- Tests: unit (49) pass on iPhone 17 Pro Max; UI tests pass on iPad Pro 13" and iPhone (iOS 27.0, Xcode 1.app).
  Launch-time check: passed on iPhone on a quiet Mac, 4.56 s (the QA session, 2026-11-07); the iPad pass was running then.
  Screenshots and App Store frames done; `qa-site.py` (full)
  passes; OTA 2026-11-06.1 (`--check` OK); listing.json written.
- Records: the QA session is drafting the NMED request, for Nick. Not now (Nick, 2026-11-07): Albuquerque's inspection history and
  the $100 liquor licensee copy.

## Rules
No commits, pushes, public repos, App Store Connect or DNS changes without Nick's yes each time; never submit for review or accept
agreements; never publish Google-derived data. Support email nick@eatsranked.com. Commit author "Nick Soderstrom"
<329204362+nickstrom5@users.noreply.github.com> via `-c user.name -c user.email`.
