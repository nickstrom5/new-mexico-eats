"""Official records for New Mexico -> one table of licensed food businesses (playbook/12-sources.md).

Off tribal land three agencies inspect restaurants: the City of Albuquerque's Environmental Health Department, Bernalillo County (the
unincorporated county) and NMED's Food Safety Program (everywhere else). Only Albuquerque publishes anything current: a weekly PDF,
"Consumer Health Protection Inspections Performed", replaced at the same URL each week, so fetch_official.py archives each edition
(data/raw/official/albuquerque/*.pdf, with its text from pdf_text.swift). Each establishment's permit, each visit's date, type and
result, and the result posted now, as the city words them: Approved (green), Conditional Approved (yellow), Unsatisfactory (red) or
Closed (orange). Shown labeled official and dated; never a computed letter or score. Bernalillo County and NMED publish no results;
tribal land (the Pueblos, the Navajo Nation, the Jicarilla and Mescalero Apache) is outside state and city inspection.
Never shown: the PDF's legal names before "DBA" (owners, often people).

load() returns: jur, lic (our id), name, keys (name keys), addr, city, zip, num, street, lat, lon, kind, active, ltype, insp, biz.
"""
import os, re, json, glob, datetime
import numpy as np, pandas as pd
from common import norm_name, RAW, name_sim, _stems, GENERIC, canon_city

OFF = os.path.join(RAW, "official")
DIRS = {"N": "N", "S": "S", "E": "E", "W": "W", "NORTH": "N", "SOUTH": "S", "EAST": "E", "WEST": "W"}
TYPES = set("ST STREET AVE AV AVENUE BLVD BOULEVARD RD ROAD DR DRIVE LN LANE CT COURT PL PLACE PKWY PARKWAY TER TRL TRAIL WAY HWY CIR "
            "CIRCLE PLZ SQ MALL BND PASS XING RUN ROW WALK RDG LOOP FWY FREEWAY EXPY EXPRESSWAY PIKE PK PKE".split())


def road(a):
    """One spelling for numbered roads. New Mexico writes one road as 'Route 100', 'US 7', 'Rt 2', 'NM 100' or 'NM Route 100', so every
    numbered US or state route is 'SH n' (as in ri-eats); 'N INTERSTATE 95' = 'I-95'; 'COUNTY ROAD 5' = 'CR 5'."""
    a = re.sub(r"(\d)\s*&\s*(\d)", r"\1-\2", a.upper())
    a = re.sub(r"\b(US|NM|SR|SH|CR|I|IH|RT|RTE)-(\w)", r"\1 \2", a)
    a = re.sub(r"\b(?:INTERSTATE(?: HIGHWAY| HWY)?|IH|I H)\s*(?=\d)", "I ", a)
    a = re.sub(r"\b(?:US|U S)\s+(?:HIGHWAY|HWY)\b", "US", a)
    a = re.sub(r"\b(?:FARM[- ]TO[- ]MARKET(?: ROAD| RD)?|FARM (?:ROAD|RD)|F M)\b", "FM", a)
    a = re.sub(r"\b(?:RANCH[- ]TO[- ]MARKET(?: ROAD| RD)?|RANCH (?:ROAD|RD)|RR|RM)\b(?=\s*\d)", "RM", a)
    a = re.sub(r"\b(?:STATE (?:HIGHWAY|HWY|ROAD|RD|ROUTE|RTE)|SR|SH|VERMONT (?:ROUTE|RTE|HIGHWAY|HWY)|NM (?:ROUTE|RTE|RT|HIGHWAY|HWY)|NM|"
               r"US (?:ROUTE|RTE|RT)|US|ROUTE|RTE|RT|HWY)\b\.?(?=\s*\d)", "SH", a)
    a = re.sub(r"\b(?:COUNTY (?:HIGHWAY|HWY|ROAD|RD)|CO RD|CTY (?:HWY|RD)|CR)\b", "CR", a)
    a = re.sub(r"\bHIGHWAY\b", "HWY", a)
    return re.sub(r"\b(US|SH|CR|HWY|FM|RM|I) (\w+)\s*-\s*\w+", r"\1 \2", a)


ORD = {"FIRST": "1ST", "SECOND": "2ND", "THIRD": "3RD", "FOURTH": "4TH", "FIFTH": "5TH", "SIXTH": "6TH", "SEVENTH": "7TH",
       "EIGHTH": "8TH", "NINTH": "9TH", "TENTH": "10TH", "ELEVENTH": "11TH", "TWELFTH": "12TH"}


def street_key(a):
    """'2505 Monroe St' -> ('2505', 'MONROE'); '1000 OSAGE STREET' -> ('1000', 'OSAGE'); 'E Colfax Ave' keeps 'COLFAX'."""
    if not isinstance(a, str):
        return None, None
    a = re.sub(r"[.,#]", " ", road(a))
    # "20940-A North Frederick Ave": a hyphenated unit letter is part of the number (Maryland's Montgomery County wrote them so)
    m = re.match(r"^\s*(\d+)(?:-?[A-Z])?(?:\s*-\s*\d+[A-Z]?)?\s+(.*)$", a)
    if not m:
        return None, None
    words = [w for w in m.group(2).split() if w]
    if len(words) > 1 and words[0] in DIRS:
        words = words[1:]
    core = []
    for w in words:
        if w in TYPES and core:
            break
        core.append(w)
    core = [ORD.get(w, w) for w in core]
    return m.group(1), " ".join(core[:3]) or None


def street_compat(a, b):
    """Same street, or one is a whole-word prefix of the other: Boulder's 2025 set sometimes truncates ("1206 CENTAUR" = Centaur Village Dr)."""
    if not isinstance(a, str) or not isinstance(b, str) or not a or not b:
        return False
    return a == b or a.startswith(b + " ") or b.startswith(a + " ")


def street_nums(a):
    """'157-159 W Main St' -> {'157', '159'}; '2505 Monroe St' -> {'2505'}."""
    if not isinstance(a, str):
        return set()
    a = road(a)
    m = re.match(r"^\s*(\d+)[A-Z]?(?:\s*-\s*(\d+)[A-Z]?)?\s", a.upper() + " ")
    if not m:
        return set()
    lo = int(m.group(1)); hi = int(m.group(2)) if m.group(2) else lo
    if hi < lo:   # "1500-02"
        hi = int(str(lo)[: len(str(lo)) - len(m.group(2))] + m.group(2)) if m.group(2) else lo
    return {str(x) for x in range(lo, hi + 1, 2 if (hi - lo) % 2 == 0 else 1)} if 0 <= hi - lo <= 12 else {str(lo)}


def _names(*vals):
    out = []
    for v in vals:
        if not isinstance(v, str):
            continue
        v = re.sub(r"\s*\((?:MOBILE|MOBILE UNIT|COMMISSARY|CATERING|SPECIAL EVENT|SPEC EVENT|TEMP(?:ORARY)? EVENT|CP|INSIDE [^)]*)\)\s*$", "", v, flags=re.I)
        for part in re.split(r"\s*/\s*|\s+\bdba\b\s+|\s+&\s+(?=[A-Z][a-z])", v, flags=re.I):
            k = norm_name(re.sub(r"\b(?:LLC|INC|CORP|CORPORATION|LTD|CO)\b\.?", "", part, flags=re.I))
            if k and k not in out:
                out.append(k)
    return out


META = json.load(open(os.path.join(OFF, "meta.json"))) if os.path.exists(os.path.join(OFF, "meta.json")) else {}
LIST_DATE = (META.get("albuquerque") or {}).get("latest_edition") or None
# Albuquerque's food safety page (the weekly report is linked there), and NMED's Food Safety Program for everywhere else (no results online)
MONT_PAGE = "https://www.cabq.gov/environmentalhealth/food-safety"
INSPECTIONS_URL = "https://www.env.nm.gov/foodprogram/"
# the results as Albuquerque posts them (its sticker: green, yellow, red, orange)
RESULTS = ("Approved", "Conditional Approved", "Unsatisfactory", "Closed")
ONPREM_T = ()


def liq_kind(t):
    """A license type as shown -> on-premises or retail."""
    if not isinstance(t, str):
        return None
    return "onprem" if t in ONPREM_T else "retail" if "Package" in t else None


COLUMNS = ["jur", "lic", "name", "dba", "holder", "keys", "addr", "city", "zip", "num", "street", "lat", "lon", "kind", "active", "ltype",
           "insp", "posted", "issued", "biz", "drinks", "county"]


def _zip(z):
    z = re.sub(r"\D", "", str(z or ""))
    return z[:5] if len(z) >= 5 else ""


def _addr(a):
    """'2790 VETERANS MEMORIAL BLVD STE 130' -> '2790 Veterans Memorial Blvd Ste 130'."""
    a = re.sub(r"\s+", " ", a or "").strip()
    a = re.sub(r"\b([A-Z]{2,})\b", lambda m: m.group(1).title(), a)
    return re.sub(r"\b(Ne|Nw|Se|Sw)\b", lambda m: m.group(1).upper(), a)   # Albuquerque's quadrants stay NE, NW, SE, SW


def _day(v):
    return v[:10] if isinstance(v, str) and re.match(r"\d{4}-\d{2}-\d{2}", v) else None


def _f(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


# Albuquerque's report: a summary table (establishment, then each permit, then each visit), then one detail section per establishment
# whose heading carries the result posted now. Its status words -> the sticker result
STATUS = [(re.compile(r"^Approved$", re.I), "Approved"), (re.compile(r"^Conditional Approv", re.I), "Conditional Approved"),
          (re.compile(r"^Unsatisfactory", re.I), "Unsatisfactory"), (re.compile(r"^Clos", re.I), "Closed")]
ROW = re.compile(r"^(\d\d)/(\d\d)/(\d{4}) (\S+) (.*?(?:Inspection|Compliance)) (.+?) Pg\. \d+$")
PERMIT = re.compile(r"^(.*?)\s*\(Permit # - ([^)]+)\) - Operational Status [-–] (\w+)")
EST = re.compile(r"^(.+?) - (.+)$")


def _status(t):
    t = (t or "").strip()
    return next((v for rx, v in STATUS if rx.search(t)), None)


def _est_name(n):
    """'AN BE LLC DBA Saigon Restaurant' -> 'Saigon Restaurant' (the legal name before DBA is never kept)."""
    n = re.sub(r"(?i)^.*?\bd\s*/?\s*b\s*/?\s*a\b\.?:?\s+", "", n).strip(" ,-")
    return re.sub(r"\s+", " ", n)


def parse_albuquerque(txt):
    lines = [l.strip() for l in txt.splitlines()]
    lines = [l for l in lines if l and not l.startswith("=== PAGE") and not re.match(r"^Page \d+ of \d+$", l) and l != "￼"]
    ests, cur, perm = {}, None, None
    for i, l in enumerate(lines):
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        if nxt.startswith("Inspection Date Inspection ID Number") and EST.match(l):
            cur = l; ests.setdefault(cur, {"permits": {}, "posted": None}); perm = None
            continue
        m = PERMIT.match(l)
        if m and cur:
            perm = m.group(2).strip()
            ests[cur]["permits"].setdefault(perm, {"type": m.group(1).strip(), "open": m.group(3).lower() == "open", "visits": []})
            continue
        m = ROW.match(l)
        if m and cur and perm:
            mo, d, y, iid, typ, st = m.groups()
            ests[cur]["permits"][perm]["visits"].append([f"{y}-{mo}-{d}", _status(st), typ, iid, st])
            continue
        # a detail heading: "<establishment> – <result posted now>"
        for e in ests:
            if l.startswith(e) and len(l) > len(e) + 3 and l[len(e)] == " " and l[len(e) + 1] in "-–":
                st = _status(l[len(e) + 2:])
                if st:
                    ests[e]["posted"] = st
                break
    return ests


def load_albuquerque():
    d = os.path.join(OFF, "albuquerque")
    rows, by_permit = [], {}
    for f in sorted(glob.glob(os.path.join(d, "*.txt"))):   # oldest edition first: a later one's operational status wins
        for est, e in parse_albuquerque(open(f, encoding="utf-8").read()).items():
            m = EST.match(est)
            name, full = _est_name(m.group(1)), m.group(2)
            addr = _addr(full)
            if not re.search(r"[A-Za-z]{2}", name):
                continue
            for pid, p in e["permits"].items():
                r = by_permit.get(pid)
                if r is None:
                    num, st = street_key(addr)
                    kind = "food" if p["type"] == "Food Establishment" else "other"
                    r = {"jur": "albuquerque", "lic": "albuquerque-" + pid, "name": name, "dba": name, "holder": None, "keys": _names(name),
                         "addr": addr, "city": "Albuquerque", "zip": "", "num": num, "street": st, "lat": None, "lon": None, "kind": kind,
                         "active": p["open"], "ltype": "Albuquerque " + p["type"].lower() + " permit", "insp": [], "posted": None,
                         "issued": None, "drinks": None, "county": "Bernalillo County"}
                    by_permit[pid] = r; rows.append(r)
                r["active"] = p["open"]
                have = {v[3] for v in r["insp"]}
                r["insp"] += [v[:4] + [[]] for v in p["visits"] if v[1] and v[3] not in have]
                if e["posted"]:
                    r["posted"] = e["posted"]
    for r in rows:   # latest first; on one day the corrective-action visit follows the inspection it corrects
        r["insp"].sort(key=lambda v: (v[0], v[2].startswith("Corrective")), reverse=True)
    n_v = sum(len(r["insp"]) for r in rows)
    print("Albuquerque:", len(rows), "permits,", sum(r["kind"] == "food" for r in rows), "food establishments |", n_v, "visits |",
          "posted results", sum(bool(r["posted"]) for r in rows))
    return rows


def load():
    """Albuquerque's archived weekly reports, one row per permit (see the docstring)."""
    rows = load_albuquerque() if glob.glob(os.path.join(OFF, "albuquerque", "*.txt")) else []
    df = pd.DataFrame(rows) if rows else pd.DataFrame({c: pd.Series(dtype=object) for c in COLUMNS})
    for c_ in COLUMNS:
        if c_ not in df.columns:
            df[c_] = None
    df["lat"] = df["lat"].astype(float); df["lon"] = df["lon"].astype(float); df["active"] = df["active"].astype(bool)
    df["biz"] = np.arange(len(df))
    return df
