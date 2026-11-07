"""Writes data/research/app/*.json (hand-checked New Mexico guides), data/research/michelin.json, jbf.json and closed.json from the
compact lists below. Ported from nh-eats/pipeline/build_research.py (ma-eats before it).

The guides come from the New Mexico Tourism Department's own trail listings on newmexico.org (New Mexico True), read on 2026-11-06 in
the built-in browser, every page of each (data/research/raw/nmtrue-trails-2026-11-06.json, with each place's address): the Green Chile
Cheeseburger Trail, the Breakfast Burrito Byway and Culinary Treasures (long-running, family-owned restaurants). The notes are our own
words; the trails are cited, never copied. A place is kept only when it matches one open map listing in its town (or the same name at
the same street number statewide); a stop listed as "Multiple Locations" or without a street address, or not found, is a lead.
Founding years: Tasting Table (2025-09-23, 2026-09-09), Chowhound (2026-05-03) and jamesbeard.org, each for the restaurant itself, never
a building. Honors: guide.michelin.com (MICHELIN Guide American Southwest, first selection August 2026) and jamesbeard.org.
Usage: ../.venv/bin/python build_research.py   (then newmexico.py)"""
import json, os, re
from brands import brand_of
from common import norm_name
ROOT = os.path.join(os.path.dirname(__file__), "..")
R = os.path.join(ROOT, "data", "research")
d = json.load(open(os.path.join(ROOT, "site", "newmexico.json")))
C, M = d["cols"], d["meta"]
import unicodedata
norm = lambda s: re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", unicodedata.normalize("NFKD", (s or "").lower()).encode("ascii", "ignore").decode()
                                             .replace("'", ""))).strip()

RAW = json.load(open(os.path.join(R, "raw", "nmtrue-trails-2026-11-06.json")))
GCC = RAW["green_chile_cheeseburger_trail"]["url"]    # New Mexico True (the state tourism department's own listing), read 2026-11-06
BBB = RAW["breakfast_burrito_byway"]["url"]
CT = RAW["culinary_treasures"]["url"]
TT_OLD = "https://www.tastingtable.com/1975409/oldest-restaurant-every-state-still-open/"             # Tasting Table, 2025-09-23
TT_DINER = "https://www.tastingtable.com/2251841/best-diner-breakfast-every-major-us-region/"         # Tasting Table, 2026-09-09
CH_HIST = "https://chowhound.com/2160227/most-historic-new-mexico-restaurants"                         # Chowhound, 2026-05-03
JBF_MT = "https://archive.jamesbeard.org/blog/americas-classics-mary-titos-cafe"                       # America's Classics 2010
JBF_RC = "https://www.jamesbeard.org/stories/2016-americas-classic-rancho-de-chimay-restaurante"      # America's Classics 2016
JBF22W = "https://www.jamesbeard.org/stories/the-2022-james-beard-award-winners"
JBF_MK = "https://archive.jamesbeard.org/chef/mark-kiffin"                                             # Best Chef: Southwest 2005
JBF26 = "https://www.jamesbeard.org/stories/james-beard-award-semifinalists-2026"                   # 2026-01-21
JBF26N = "https://www.jamesbeard.org/stories/james-beard-awards-restaurant-and-chef-nominees-2026"  # 2026-03-31
JBF25 = "https://www.jamesbeard.org/stories/the-2025-james-beard-award-semifinalists"               # 2025-01-22
JBF25N = "https://www.jamesbeard.org/stories/2025-james-beard-awards-restaurant-and-chef-nominees"  # 2025-04-02
MI_NM = "https://guide.michelin.com/us/en/new-mexico/restaurants"                                     # read 2026-11-06

NOTE = {"green chile cheeseburger": "A stop on New Mexico True's Green Chile Cheeseburger Trail, the state tourism department's own list.",
        "breakfast burrito": "A stop on New Mexico True's Breakfast Burrito Byway, the state tourism department's own list.",
        "culinary treasure": "One of New Mexico True's Culinary Treasures: a long-running restaurant still owned and run by its family."}
SRC = {"green chile cheeseburger": GCC, "breakfast burrito": BBB, "culinary treasure": CT}
# the source's town -> one of ours ("Grants-Milan" is Grants; "La Mesilla" is Mesilla)
TOWN = {"Grants-Milan": "Grants", "La Mesilla": "Mesilla"}
# founding years, each for the restaurant itself (the year its own source gives), never its building
FOUNDED = {("Pantry Restaurant", "Santa Fe"): (1948, "Tasting Table (September 2026): The Pantry opened in 1948.", [TT_DINER]),
           ("Mary & Tito's Cafe", "Albuquerque"): (1963, "The James Beard Foundation (America's Classics, 2010): Mary and Tito Gonzales opened the cafe in 1963.", [JBF_MT])}
GUIDES = {}
for raw_key, kind in (("green_chile_cheeseburger_trail", "green chile cheeseburger"), ("breakfast_burrito_byway", "breakfast burrito"),
                      ("culinary_treasures", "culinary treasure")):
    GUIDES[kind] = []
    for name, addr, town in RAW[raw_key]["stops"]:
        name = re.sub(r"\s+-\s+(?:Cuba|Abq|Cedar Crest|Belen|Bosque Farms|Broadway|Los Lunas)$", "", name).strip()
        town = TOWN.get(town, town)
        addr = None if re.search(r"(?i)multiple locations|catering office|^RR \d", addr or "") or not re.match(r"\s*\d", addr or "") else addr.strip()
        f = FOUNDED.get((name, town))
        GUIDES[kind].append((name, town, addr, NOTE[kind], f[0] if f else None, f[1] if f else None, [SRC[kind]] + (f[2] if f else [])))
# the oldest places with a dated source and no trail listing
GUIDES["historic restaurant"] = [
  ("El Farol", "Santa Fe", "808 Canyon Rd", "A Canyon Road cantina and tapas restaurant; Tasting Table calls it New Mexico's oldest restaurant.", 1835,
   "Tasting Table (September 2025) gives 1835, the restaurant's own claim to be the state's oldest.", [TT_OLD]),
  ("La Cita", "Tucumcari", "820 S 1st St", "A Route 66 Mexican restaurant in Tucumcari.", 1940,
   "Chowhound (May 2026): La Cita opened in 1940.", [CH_HIST])]

ADDR, POINT = {}, {}
# the name to show where the kept map listing is a twin under another name at the same address ("Galeria El Farol", "Lacita Restaurant")
DISPLAY = {("El Farol", "Santa Fe"): "El Farol", ("La Cita", "Tucumcari"): "La Cita"}
CUISINE = {("Mr. Powdrell's Barbeque House", "Albuquerque"): "BBQ", ("Pappas Sweet Shop", "Raton"): "Bakery & Sweets",
           ("Lucky Boy Chinese Food & Hamburgers", "Albuquerque"): "Burgers", ("La Cita", "Tucumcari"): "Mexican",
           # New Mexican kitchens whose names say "Cafe" (the name rule would file them as coffee shops)
           ("Mary & Tito's Cafe", "Albuquerque"): "Mexican", ("Atrisco Cafe & Bar", "Santa Fe"): "Mexican", ("Jerry's Cafe", "Gallup"): "Mexican",
           ("Dick's Cafe", "Las Cruces"): "Mexican", ("El Sombrero Patio Cafe", "Las Cruces"): "Mexican", ("Pete's Cafe", "Belen"): "Mexican",
           ("Silver Moon Cafe", "Santa Rosa"): "Mexican", ("El Cafecito", "Grants"): "Mexican"}
KINDS = {k: [k] for k in GUIDES}

# MICHELIN Guide American Southwest (first selection August 26, 2026): the 12 New Mexico places on guide.michelin.com (read 2026-11-06),
# five Bib Gourmands and seven recommended ("Selected Restaurants"); no Stars, no Green Stars
MICHELIN = [("Paper Dosa", "Santa Fe", "Bib Gourmand", "Indian"), ("La Choza", "Santa Fe", "Bib Gourmand", "Southwestern"),
            ("Jambo Cafe", "Santa Fe", "Bib Gourmand", "African"), ("Frontier", "Albuquerque", "Bib Gourmand", "Southwestern"),
            ("Tia Sophia's", "Santa Fe", "Bib Gourmand", "Southwestern"),
            ("Paloma", "Santa Fe", "Recommended", "Mexican"), ("Arroyo Vino", "Santa Fe", "Recommended", "Contemporary"),
            ("Restaurant Martin", "Santa Fe", "Recommended", "Contemporary"), ("Izanami", "Santa Fe", "Recommended", "Japanese"),
            ("Market Steer", "Santa Fe", "Recommended", "Steakhouse"), ("Joseph's Culinary Pub", "Santa Fe", "Recommended", "Gastropub"),
            ("Campo at Los Poblanos", "Los Ranchos de Albuquerque", "Recommended", "Contemporary")]
MI_MATCH = {"Frontier": ["FRONTIER RESTAURANT"], "Joseph's Culinary Pub": ["JOSEPHS", "JOSEPH S CULINARY PUB"],
            "Campo at Los Poblanos": ["CAMPO", "LOS POBLANOS", "CAMPO AT LOS POBLANOS HISTORIC INN AND ORGANIC FARM"],
            "Tia Sophia's": ["TIA SOPHIAS"], "Market Steer": ["MARKET STEER STEAKHOUSE"]}
MI_UT = MI_NM
SW = "Best Chef: Southwest"
JBF = [{"name": "Rancho de Chimayó", "city": "Chimayo", "honors": ["America's Classics 2016"], "sources": [JBF_RC],
        "match_names": ["RANCHO DE CHIMAYO", "RANCHO DE CHIMAYO RESTAURANTE"]},
       {"name": "Mary & Tito's Cafe", "city": "Albuquerque", "honors": ["America's Classics 2010"], "sources": [JBF_MT],
        "match_names": ["MARY AND TITOS", "MARY TITOS CAFE"]},
       {"name": "Sazón", "city": "Santa Fe", "honors": [f"{SW} winner 2022 (Fernando Olea)"], "sources": [JBF22W], "match_names": ["SAZON"]},
       {"name": "The Compound", "city": "Santa Fe", "honors": [f"{SW} winner 2005 (Mark Kiffin)"], "sources": [JBF_MK],
        "match_names": ["THE COMPOUND RESTAURANT", "COMPOUND"]},
       {"name": "Bow & Arrow Brewing Co.", "city": "Albuquerque", "address": "608 McKnight Ave NW", "honors": ["Outstanding Bar finalist 2026"], "sources": [JBF26N, JBF26],
        "match_names": ["BOW AND ARROW BREWING", "BOW AND ARROW BREWING CO"]},
       {"name": "Mesa Provisions", "city": "Albuquerque", "honors": [f"{SW} finalist 2026 (Steve Riley)"], "sources": [JBF26N, JBF26]},
       {"name": "Campo at Los Poblanos", "city": "Los Ranchos de Albuquerque", "honors": ["Outstanding Wine and Other Beverages Program finalist 2025"],
        "sources": [JBF25N, JBF25], "match_names": ["CAMPO", "LOS POBLANOS"]},
       {"name": "The Burque Bakehouse", "city": "Albuquerque", "honors": ["Outstanding Bakery semifinalist 2026"], "sources": [JBF26],
        "match_names": ["BURQUE BAKEHOUSE"]},
       {"name": "Daydream Rum Bar", "city": "Albuquerque", "honors": ["Best New Bar semifinalist 2026"], "sources": [JBF26]},
       {"name": "Ardovino's Desert Crossing", "city": "Sunland Park", "honors": [f"{SW} semifinalist 2026 (Danny Calleros)"], "sources": [JBF26],
        "match_names": ["ARDOVINOS DESERT CROSSING", "ARDOVINOS"]},
       {"name": "NOSA Restaurant & Inn", "city": "Ojo Caliente", "honors": [f"{SW} semifinalist 2026 (Graham Dodds)"], "sources": [JBF26],
        "match_names": ["NOSA"]},
       {"name": "Coda Bakery", "city": "Albuquerque", "honors": ["Outstanding Bakery semifinalist 2025"], "sources": [JBF25]},
       {"name": "Happy Accidents", "city": "Albuquerque", "honors": ["Outstanding Professional in Cocktail Service semifinalist 2025 (Kate Gerwin)"],
        "sources": [JBF25]},
       {"name": "Sassella", "city": "Santa Fe", "honors": [f"{SW} semifinalist 2025 (Cristian Pontiggia)"], "sources": [JBF25]},
       {"name": "Buen Provecho", "city": "Albuquerque", "honors": [f"{SW} semifinalist 2025 (Kattia Rojas)"], "sources": [JBF25]},
       {"name": "Level 5", "city": "Albuquerque", "honors": [f"{SW} semifinalist 2025 (Sean Sinclair)"], "sources": [JBF25]},
       {"name": "Joseph's Culinary Pub", "city": "Santa Fe", "honors": [f"{SW} semifinalist 2025 (Joseph Wrede)"], "sources": [JBF25],
        "match_names": ["JOSEPHS", "JOSEPH S CULINARY PUB"]}]
CLOSED = []


import pandas as pd
from common import name_sim, NM
_S1 = pd.read_pickle(os.path.join(NM, "stage1.pkl"))
_S1 = _S1[~_S1.ov_closed.fillna(False) & ~_S1.j_outside.fillna(False)]
_num = lambda a: ((re.match(r"\s*0*(\d+)", a if isinstance(a, str) else "") or [None, ""])[1]).upper()


def by_address(name, num):
    """The same street number and a name that's the same business ("Grandma's K & I Diner" is K & I Diner; "Nopalito Restaurant" is
    Nopalito's Restaurants): the kept places first, then an open Overture listing the keep rule left out."""
    n0, k = _num(num), norm_name(name)
    kept = [i for i, a in enumerate(C["addr"]) if _num(a) == n0 and C["city"][i] is not None and name_sim(k, norm_name(C["name"][i])) >= 80]
    if kept:
        return kept, None
    s1 = _S1[_S1.street.map(_num).eq(n0)]
    s1 = s1[[name_sim(k, norm_name(n)) >= 80 for n in s1.name.fillna("")]]
    return [], (s1.iloc[0] if len(s1) == 1 else None)


def key(s):
    """The name key without a leading "the": "Varsity" is our "The Varsity"."""
    return re.sub(r"^the ", "", norm(s))


def find(name, town, num):
    hits = find_in(name, town, num)
    if not hits and num:   # the source's town is a village ("Intervale"): the same name at the same street number anywhere
        hits = find_in(name, None, num)
    return hits


def find_in(name, town, num):
    k = key(name)
    hits = [i for i, n in enumerate(C["name"]) if C["city"][i] is not None and (town is None or M["cities"][C["city"][i]] == town)
            and (key(n) == k or key(n).startswith(k + " ") or k.startswith(key(n) + " ") or key(n).replace(" ", "") == k.replace(" ", "")
                 or (key(n).split()[:2] == k.split()[:2] and len(k.split()) >= 2))]
    if num:
        hits = [i for i in hits if (C["addr"][i] or "").split(" ")[0].upper() == num.upper()]
    exact = [i for i in hits if key(C["name"][i]) == k]   # "Limoncello" and "Limoncello Ristorante", one place listed twice
    return exact if len(hits) > 1 and len(exact) == 1 else hits


leads, n_out = [], {}
for kind, rows in GUIDES.items():
    out = []
    for name, town, addr, note, founded, fnote, srcs in rows:
        num = (re.match(r"\s*(\d+)", addr or "") or [None, None])[1]
        hits = find(name, town, num)
        s1row = None
        if len(hits) != 1 and addr:
            alt, s1row = by_address(name, addr)
            if len(alt) == 1:
                hits = alt
        if len(hits) != 1 and addr and (kind == "historic restaurant" or s1row is not None):
            # a dated source with its own address, or a trail stop that is an open Overture listing at that address (the keep rule left
            # it out): added with the street address
            out.append({"name": name, "address": addr, "city": town, "zip": None, "kinds": KINDS[kind], "dishes": [], "note": note,
                        "founded": founded, "founded_note": fnote, "website": None, "open": True, "evidence_date": "2026-11",
                        "sources": srcs, "match_names": []} | ({"cuisine": CUISINE[(name, town)]} if (name, town) in CUISINE else {}))
            continue
        if len(hits) != 1:
            # trail listings carry no date, so a stop that matches no open map listing may have closed: a lead, not added
            why = "listed at several locations" if not addr else f"{len(hits)} open map listings match it"
            leads.append(f"- {kind}: {name} ({town}{', ' + addr if addr else ''}) — {why}; not added"); continue
        i = hits[0]
        out.append({"name": C["name"][i], "address": C["addr"][i], "city": M["cities"][C["city"][i]], "zip": str(C["zip"][i]) if C["zip"][i] else None,
                    "kinds": KINDS[kind], "dishes": [], "note": note, "founded": founded, "founded_note": fnote, "website": None, "open": True,
                    "evidence_date": "2026-11", "sources": srcs, "match_names": [name.upper()] if norm(name) != norm(C["name"][i]) else []})
        if brand_of(norm_name(name)):
            out[-1]["display"] = name
        if (name, town) in DISPLAY:
            out[-1]["display"] = DISPLAY[(name, town)]
        if (name, town) in CUISINE:
            out[-1]["cuisine"] = CUISINE[(name, town)]
    fn = re.sub(r"[^a-z]+", "_", kind).strip("_")
    json.dump(out, open(f"{R}/app/{fn}.json", "w"), indent=1, ensure_ascii=False)
    n_out[kind] = len(out)

MI_ADDR = {}
json.dump({"restaurants": [{"name": n, "address": MI_ADDR.get(n), "city": t, "zip": None, "distinction": dist, "cuisine": cu, "green_star": False,
                             "michelin_url": MI_UT, "sources": [MI_UT], "match_names": [x.upper() for x in MI_MATCH.get(n, [])], "open": True}
                            for n, t, dist, cu in MICHELIN]}, open(f"{R}/michelin.json", "w"), indent=1, ensure_ascii=False)
json.dump([dict({"address": None}, **j, zip=None, open=True) for j in JBF], open(f"{R}/jbf.json", "w"), indent=1, ensure_ascii=False)
json.dump(CLOSED, open(f"{R}/closed.json", "w"), indent=1, ensure_ascii=False)
open(f"{R}/app/LEADS.md", "w").write("# New Mexico research leads (not yet verified)\n\nWritten by pipeline/build_research.py.\n\n" + "\n".join(leads) + """

## Waiting for a source we may use
- James Beard America's Classics for The Shed (2003) and Cafe Pasqual's (1999), both Santa Fe: no jamesbeard.org page found yet (only
  a blog and Wikipedia). Mark Miller's 1996 Best Chef win went to the chef, who has long left Coyote Cafe: not tied to the restaurant.
- The Shed's 1953 (Chowhound: the Carswell family has owned it since then; it has moved since), La Plazuela's 1922 dining room, the
  Legal Tender's 1881 and the Buckhorn's 1863 buildings, and the Owl Bar's 1945: building or ownership dates, not the restaurant's
  founding at its address, so no founding year is shown.
- Red-or-green New Mexican classics, biscochito bakeries, Native-owned restaurants and fry bread, and Route 66 diners: no 2025-26
  source on a host that lets Claude read it yet beyond New Mexico True's trails. abqjournal.com, santafenewmexican.com, lcsun-news.com,
  koat.com and sourcenm.com disallow Claude.
- Escondido (Santa Fe; Fernando Ruiz, a 2025 Best Chef: Southwest semifinalist): no address found yet, so not placed.
- Blake's Lotaburger, El Parasol, Weck's, Golden Pride, Santa Fe Grill and Garcia's Kitchen are on the trails as chains or "Multiple
  Locations": not tied to one place.
""")
print(n_out, "| leads:", len(leads))
for l in leads: print(l)
