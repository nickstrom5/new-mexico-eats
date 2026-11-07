# New Mexico sources and calibration (checked 2026-11-06)

## Official sources
| Source | What it has | Can a script read it? | Used |
|---|---|---|---|
| City of Albuquerque Environmental Health, "Consumer Health Protection Inspections Performed" (cabq.gov/environmentalhealth/documents/chpd_main_inspection_report.pdf, weekly, replaced at the same URL) | the week's inspections: each establishment and permit, each visit's date, type and result, the narrative, and the result each place has posted now (Approved green, Conditional Approved yellow, Unsatisfactory red, Closed orange) | yes (robots.txt allows; `fetch_official.py`, text through macOS PDFKit) | yes: archived each week (`data/raw/official/albuquerque/chpd-<week end>.pdf`); the 2026-10-31 edition (amended 11-02) has 54 permits, 45 food establishments, 64 visits; 30 joined to map listings. The posted result is shown as the city words it, dated, labeled official; never a computed grade. Legal names before "DBA" are dropped |
| Albuquerque's history (data.cabq.gov foodinspections History, 2003-FY2020) and LIVES feed | stale history; the LIVES inspection files are empty | yes | no (stale); history since 2020 needs a records request (cabq.nextrequest.com): **Nick's call** |
| Albuquerque "Info Connect" (albuquerquenm-cc.connect.socrata.com) | non-public Socrata data | no (403) | no; ask ABQ-Data@cabq.gov: **Nick's call** |
| Bernalillo County Consumer Health Protection (unincorporated county, ~500 places) | reports on request | no | no |
| NMED Food Safety Program (everywhere else off tribal land; env.nm.gov/foodprogram) | no results, grades or permit list online; api.env.nm.gov lists APIs only to registered users | no | linked from places outside Albuquerque. Registering or an IPRA request: **Nick's call** |
| RLD Alcoholic Beverage Control, NM-PLUS (Salesforce search) | licensees, search only; the full listing is a $100 IPRA copy by money order | no (not scraped) | no: "Serves alcohol" is "—" everywhere. Buying the listing: **Nick's call** |
| Tribal land (19 Pueblos, the Navajo Nation, Jicarilla and Mescalero Apache), casinos included | outside state and city inspection | — | places there show no record, never "clean" |

## Towns
A listing's town is the Overture locality outline its point is in (131 outlines: the incorporated cities, towns and villages plus some
census places; an Albuquerque open space, a ranch and a commune left out), or the nearest within ~1 km; outside every outline (most of
the state is unincorporated) it keeps its postal town. 111 listings' points sat in another town than their postal name; a postal name
that differs and isn't a town ("South Valley", "El Prado") stays as the place's area. The 26 border tests (El Paso, Ciudad Juárez,
Palomas, Farwell, Texline, Trinidad, Cortez and Sanders out; Sunland Park, Anthony, Columbus, Texico, Shiprock and Raton in) pass. Counties
(33) split the app's detail files into 6 regions.

## Calibration
- Census County Business Patterns 2023: 3,935 NAICS 722 establishments (per the prompt; Bernalillo 1,480, Santa Fe 400, Doña Ana 326).
- Overture 2026-10-21.0: 15,086 eating and drinking listings in New Mexico's box, 6,237 of them across the line (El Paso, Juárez); 8,376
  open, cleaned listings in the state. The family's keep rule (Meta 0.95, or 0.90 with a website, or a brand feed), measured where
  cities publish full lists (Massachusetts' Cambridge and Somerville: Meta 0.95+ matched an official record about 90% of the time), plus
  the hand-checked and honored places gives the App Store build **4,262 places, 4,097 restaurants** (104% of CBP).
- Albuquerque's one week of reports is no full list, so it only measures coverage: **60%** of the 40 inspected food establishments
  (daycares and senior housing among them) were found among the open map listings.
- No Google data at all.

## Research sources (each place cites its own; data/research/app/*.json; read 2026-11-06)
- New Mexico True (the New Mexico Tourism Department, newmexico.org), read in the built-in browser, every page of each trail's listing
  (`data/research/raw/nmtrue-trails-2026-11-06.json`, with addresses): the Green Chile Cheeseburger Trail (49 stops; 34 matched),
  the Breakfast Burrito Byway (34; 25) and Culinary Treasures (30 long-running family restaurants; 25). A stop is kept only when one open
  map listing matches it at the trail's address; chains listed at "Multiple Locations" and unmatched stops are leads
  (`data/research/app/LEADS.md`). The notes are our own words.
- Tasting Table: the oldest restaurant in every state (2025-09-23; El Farol, 1835, the restaurant's own claim) and the best diner
  breakfast by region (2026-09-09; The Pantry, 1948). Chowhound: New Mexico's historic restaurants (2026-05-03; La Cita, 1940).
- guide.michelin.com: the MICHELIN Guide American Southwest's 12 New Mexico places (5 Bib Gourmands, 7 recommended; no stars).
- jamesbeard.org: America's Classics Mary & Tito's (2010) and Rancho de Chimayó (2016), Best Chef: Southwest Fernando Olea (2022) and
  Mark Kiffin (2005, the archive), the 2025 and 2026 semifinalists, nominees and winners. The Shed's and Cafe Pasqual's America's
  Classics have no jamesbeard.org page found yet (leads).
- Not usable: abqjournal.com, santafenewmexican.com, lcsun-news.com, koat.com, sourcenm.com (robots.txt disallows Claude).
