"""Download the Overture Maps extracts that newmexico.py reads -> data/nm/

- overture_nm_bbox.parquet     every place in New Mexico's bounding box (name, category, address, point)
- overture_nm_sources.parquet  which datasets each New Mexico eating/drinking listing came from (Meta, Foursquare, ...)
- nm_shapes.json               simplified state and county outlines for the map
- nm_state_detail.geojson      the state outline at full detail, for the in-state test
- nm_counties_detail.geojson   the 33 counties (the files split by region)
- nm_towns_detail.geojson      Overture's locality outlines in New Mexico (cities, towns, villages and the census-designated places):
                               a listing in one takes its name as its town; one outside every outline (most of the state is
                               unincorporated) keeps its postal town

Reads the public Overture bucket over S3 with DuckDB (no account needed). Ported from va-eats/pipeline/fetch_overture.py (2026-11-06).
The script checks the towns on the lines with Arizona, Utah, Colorado, Oklahoma, Texas and Mexico (Texico is in, Farwell TX is out;
Sunland Park is in, El Paso and Ciudad Juárez are out).
"""
import os, re, json, time
import duckdb
from shapely import wkb
from shapely.geometry import mapping, Polygon

RELEASE = "2026-10-21.0"
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "nm")
# New Mexico (31.33°N–37.00°N, 103.00°W–109.05°W) plus a margin for the border towns
BBOX = "bbox.xmin BETWEEN -109.15 AND -102.95 AND bbox.ymin BETWEEN 31.3 AND 37.05"
EAT = "('restaurant','casual_eatery','bar','fast_food_restaurant','coffee_shop','cafe','smoothie_juice_bar','brewery','food_court')"
os.makedirs(OUT, exist_ok=True)

con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs; INSTALL spatial; LOAD spatial; SET s3_region='us-west-2';")
places = f"s3://overturemaps-us-west-2/release/{RELEASE}/theme=places/type=place/*.parquet"

t = time.time()
if not os.path.exists(f"{OUT}/overture_nm_bbox.parquet"):
    con.execute(f"""
COPY (
  SELECT id, names.primary AS name, basic_category AS cat, taxonomy.primary AS tax, taxonomy.hierarchy AS hier, confidence,
         operating_status AS status, brand.names.primary AS brand, addresses[1].freeform AS street, addresses[1].locality AS city,
         addresses[1].postcode AS zip, addresses[1].region AS region, ST_Y(geometry) AS lat, ST_X(geometry) AS lon, websites[1] AS web,
         phones[1] AS phone
  FROM read_parquet('{places}', hive_partitioning=1) WHERE {BBOX}
) TO '{OUT}/overture_nm_bbox.parquet' (FORMAT PARQUET)""")
    print("places in bbox", round(time.time() - t), "s", flush=True)
if not os.path.exists(f"{OUT}/overture_nm_sources.parquet"):
    con.execute(f"""
COPY (
  SELECT id, list_transform(sources, lambda x: x.dataset) AS ds, list_transform(sources, lambda x: x.update_time) AS ut,
         list_transform(sources, lambda x: x.record_id) AS rid,
         len(socials) AS n_soc, len(websites) AS n_web, len(phones) AS n_ph
  FROM read_parquet('{places}', hive_partitioning=1)
  WHERE {BBOX} AND basic_category IN {EAT}
) TO '{OUT}/overture_nm_sources.parquet' (FORMAT PARQUET)""")
    print("sources", round(time.time() - t), "s", flush=True)

areas = f"s3://overturemaps-us-west-2/release/{RELEASE}/theme=divisions/type=division_area/*.parquet"
rows = con.execute(f"""
  SELECT subtype, names.primary AS name, ST_AsWKB(geometry) AS g
  FROM read_parquet('{areas}', hive_partitioning=1)
  WHERE country = 'US' AND region = 'US-NM' AND subtype IN ('region', 'county') AND class = 'land'
    AND bbox.xmin > -109.3 AND bbox.xmax < -102.8 AND bbox.ymin > 31.2 AND bbox.ymax < 37.2""").fetchall()
# the towns: every Overture locality outline in New Mexico (a name used twice is one town, its outlines joined)
trows = con.execute(f"""
  SELECT names.primary AS name, ST_AsWKB(geometry) AS g
  FROM read_parquet('{areas}', hive_partitioning=1)
  WHERE country = 'US' AND region = 'US-NM' AND subtype = 'locality' AND class = 'land'""").fetchall()
from shapely.ops import unary_union
NOT_TOWNS = {"Manzano / Four Hills Open Space", "Old Hornsby Ranch", "Lama Foundation"}   # an Albuquerque open space, a ranch, a commune
towns = {}
for n, g in trows:
    n = re.sub(r"\s*/\s*CDP$", "", n or "")   # "Chilili/CDP"
    if n in NOT_TOWNS:
        continue
    geom = wkb.loads(bytes(g)).buffer(0)
    if n and geom.geom_type in ("Polygon", "MultiPolygon") and not geom.is_empty:
        towns[n] = unary_union([towns[n], geom]) if n in towns else geom
assert 100 < len(towns) < 600, len(towns)
json.dump({n: mapping(g.simplify(0.0002, preserve_topology=True)) for n, g in towns.items()}, open(f"{OUT}/nm_towns_detail.geojson", "w"))
print("towns:", len(towns), "of", len(trows), "locality rows")


def rings(geom, tol, min_area):
    geom = geom.simplify(tol, preserve_topology=True)
    polys = [p for p in getattr(geom, "geoms", [geom]) if p.geom_type == "Polygon" and p.area >= min_area]
    return [[[round(x, 3), round(y, 3)] for x, y in p.exterior.coords] for p in polys]


out = {"state": None, "counties": []}
for sub, name, g in rows:
    geom = wkb.loads(bytes(g)).buffer(0)
    if sub == "region":
        json.dump(mapping(geom.simplify(0.0005, preserve_topology=True)), open(f"{OUT}/nm_state_detail.geojson", "w"))
        out["state"] = [[r] for r in rings(geom, 0.002, 0.000005)]
    else:
        out["counties"].append({"name": name, "c": rings(geom, 0.004, 0.00002)})
# full-detail county polygons for assigning each place to a county (not shipped)
json.dump({name: mapping(wkb.loads(bytes(g)).buffer(0).simplify(0.0003, preserve_topology=True))
           for sub, name, g in rows if sub == "county"}, open(f"{OUT}/nm_counties_detail.geojson", "w"))
json.dump(out, open(f"{OUT}/nm_shapes.json", "w"), separators=(",", ":"))
print("outlines: state", len(out["state"] or []), "rings +", len(out["counties"]), "counties;", round(time.time() - t), "s total")
# islands, shores and border towns: each must fall on the right side of the detailed state outline
from shapely.geometry import shape, Point
st = shape(json.load(open(f"{OUT}/nm_state_detail.geojson")))
for nm, lon, lat, want in [("Albuquerque", -106.6504, 35.0844, True), ("Santa Fe", -105.9378, 35.6870, True), ("Las Cruces", -106.7637, 32.3199, True),
                           ("Farmington", -108.2187, 36.7281, True), ("Shiprock", -108.6865, 36.7856, True), ("Gallup", -108.7426, 35.5281, True),
                           ("Sanders, AZ", -109.3312, 35.2153, False), ("Cortez, CO", -108.5859, 37.3489, False), ("Raton", -104.4391, 36.9034, True),
                           ("Trinidad, CO", -104.5005, 37.1695, False), ("Clayton", -103.1844, 36.4517, True), ("Texline, TX", -103.0216, 36.3775, False),
                           ("Clovis", -103.2052, 34.4048, True), ("Texico", -103.0510, 34.3895, True), ("Farwell, TX", -103.0300, 34.3820, False),
                           ("Hobbs", -103.1360, 32.7026, True), ("Carlsbad", -104.2288, 32.4207, True), ("Sunland Park", -106.5800, 31.7965, True),
                           ("El Paso, TX", -106.4850, 31.7619, False), ("Ciudad Juárez, MX", -106.4245, 31.6904, False), ("Columbus", -107.6403, 31.8276, True),
                           ("Palomas, MX", -107.6280, 31.7720, False), ("Anthony", -106.6056, 32.0043, True), ("Taos", -105.5731, 36.4072, True),
                           ("Chama", -106.5797, 36.9031, True), ("Silver City", -108.2803, 32.7701, True)]:
    ok = st.contains(Point(lon, lat))
    print(f"  {nm}: {'inside' if ok else 'outside'}{'' if ok == want else '  <-- WRONG'}")
print("counties:", len(out["counties"]), sorted(c["name"] for c in out["counties"]))

# the neighbours' land (Arizona, Utah, Colorado, Oklahoma, Texas, Chihuahua and Sonora): listings.py widens New Mexico's outline ~300 m,
# but only where no neighbour's land is, so a Farwell, TX or El Paso listing on the far side of the line stays out
nb = con.execute(f"""
  SELECT region, ST_AsWKB(geometry) FROM read_parquet('{areas}', hive_partitioning=1)
  WHERE ((country = 'US' AND region IN ('US-AZ', 'US-UT', 'US-CO', 'US-OK', 'US-TX')) OR (country = 'MX' AND region IN ('MX-CHH', 'MX-SON')))
    AND subtype = 'region' AND class = 'land'""").fetchall()
from shapely.geometry import box
near = box(-109.3, 31.2, -102.8, 37.2)
nbg = unary_union([wkb.loads(bytes(g)).buffer(0).intersection(near) for _, g in nb])
json.dump(mapping(nbg.simplify(0.0002, preserve_topology=True)), open(f"{OUT}/nm_neighbors.geojson", "w"))
print("neighbours:", sorted(r for r, _ in nb))
