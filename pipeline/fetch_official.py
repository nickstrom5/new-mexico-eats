"""Archive New Mexico's official records -> data/raw/official/ (playbook/12-sources.md).

Only the City of Albuquerque publishes current inspection results: a weekly PDF, "Consumer Health Protection Inspections
Performed", replaced at the same URL each week (robots.txt allows it; check_sources.py). Each run saves the current edition under
its week's last day (albuquerque/chpd-<yyyy-mm-dd>.pdf) with its text (pdf_text.swift, macOS PDFKit), so the archive grows week by
week. History before the first archived week needs a records request (cabq.nextrequest.com): Nick's call. Bernalillo County and NMED
publish no results; the liquor licensee list is a paid IPRA copy (Nick's call); neither is read.
Usage: ../.venv/bin/python fetch_official.py
"""
import os, re, json, datetime, subprocess
import requests
from common import RAW

OFF = os.path.join(RAW, "official")
D = os.path.join(OFF, "albuquerque")
URL = "https://www.cabq.gov/environmentalhealth/documents/chpd_main_inspection_report.pdf"
UA = "NewMexicoEatsDataCheck/1.0 (nick@eatsranked.com)"
MONTHS = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                                      "November", "December"], 1)}
os.makedirs(D, exist_ok=True)

r = requests.get(URL, headers={"User-Agent": UA}, timeout=120)
r.raise_for_status()
pdf = r.content
assert pdf[:5] == b"%PDF-", "not a PDF"
tmp = os.path.join(D, "_latest.pdf")
open(tmp, "wb").write(pdf)
txt = subprocess.run(["swift", os.path.join(os.path.dirname(__file__), "pdf_text.swift"), tmp], capture_output=True, text=True, check=True).stdout
flat = re.sub(r"\s+", " ", txt)
m = re.search(r"Performed Week: (\w+) (\d+), (\d{4}) to (\w+) (\d+), (\d{4})", flat)
assert m, "no 'Performed Week' line"
week_end = datetime.date(int(m.group(6)), MONTHS[m.group(4)], int(m.group(5))).isoformat()
base = os.path.join(D, f"chpd-{week_end}")
os.replace(tmp, base + ".pdf")
open(base + ".txt", "w", encoding="utf-8").write(txt)
editions = sorted(f[5:15] for f in os.listdir(D) if re.match(r"chpd-\d{4}-\d{2}-\d{2}\.txt$", f))
meta = {"albuquerque": {"url": URL, "latest_edition": week_end, "editions": editions, "fetched": datetime.date.today().isoformat(),
                        "amended": bool(re.search(r"Report Amended", flat))}}
json.dump(meta, open(os.path.join(OFF, "meta.json"), "w"), indent=1)
print("Albuquerque: week ending", week_end, "|", len(pdf) // 1024, "KB |", len(editions), "editions archived:", editions)
