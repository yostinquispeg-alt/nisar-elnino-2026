"""Búsqueda de escenas en el CMR, interpretación de nombres y pares antes/después.

- Convención de nombres NISAR: R2 [V].
- Catálogo DEMO: escenas reales leídas del CMR el 14 nov 2026 (R14 [V]).
- Una sola geometría por serie: idea del código del equipo (R15 [V]).
"""
import datetime as dt
import re

from .config import CMR_GRANULES, COLECCIONES, GAP_END, GAP_START, UTC, ZONAS

NOMBRE_RE = re.compile(
    r"NISAR_(?P<I>[LS])(?P<L>\d)_(?P<PT>[A-Z]{2})_(?P<PROD>[A-Z0-9]{4})_(?P<CYL>\d{3})_(?P<REL>\d{3})_(?P<P>[AD])_"
    r"(?P<FRM>\d{3})_(?P<MODE>\d{4})_(?P<POLE>[A-Z]{4})_(?P<S>[AM])_(?P<start>\d{8}T\d{6})_(?P<end>\d{8}T\d{6})_"
    r"(?P<CRID>[A-Z]\d{5})_(?P<A>[PMNF])_(?P<C>[FP])_(?P<LOC>[A-Z])_(?P<CTR>\d{3})")


def parse_nombre(nombre):
    m = NOMBRE_RE.search(nombre)
    if not m:
        return None
    d = m.groupdict()
    d["t"] = dt.datetime.strptime(d["start"], "%Y%m%dT%H%M%S").replace(tzinfo=UTC)
    d["geom"] = (int(d["REL"]), d["P"], int(d["FRM"]))
    return d


TEMPORAL_EVENTOS = "2026-08-01T00:00:00Z,2026-12-31T23:59:59Z"   # cubre la línea base de agosto y los eventos E1–E5


def cmr_buscar(concept_id, lat, lon, temporal=TEMPORAL_EVENTOS, intentos=3, generico=False):
    """Consulta pública al CMR (no requiere credenciales). Filtra por fecha y ordena de la más reciente a la más
    antigua: sin filtro, page_size=200 en orden ascendente devolvía las escenas más viejas y podía dejar fuera octubre."""
    import time
    import requests
    p = {"collection_concept_id": concept_id, "point": f"{lon},{lat}", "page_size": 200, "sort_key": "-start_date"}
    if temporal:
        p["temporal"] = temporal
    for k in range(intentos):
        try:
            r = requests.get(CMR_GRANULES, params=p, timeout=(10, 40))
            r.raise_for_status()
            break
        except requests.RequestException as e:
            print(f"      CMR: intento {k + 1}/{intentos} falló ({type(e).__name__})", flush=True)
            if k == intentos - 1:
                raise
            time.sleep(3)
    out = []
    for g in r.json()["feed"]["entry"]:
        nombre = g.get("producer_granule_id") or g["title"]
        url = next((l["href"] for l in g.get("links", []) if l["href"].startswith("https") and l["href"].endswith(".h5")), None)
        d = parse_nombre(nombre)
        if d:
            out.append({**d, "nombre": nombre, "url": url})
        elif generico and url:
            # Otros productos (GUNW con dos fechas, SME2): basta la primera y la última fecha del nombre.
            fechas = re.findall(r"\d{8}T\d{6}", nombre)
            if fechas:
                t = [dt.datetime.strptime(f, "%Y%m%dT%H%M%S").replace(tzinfo=UTC) for f in fechas]
                out.append({"nombre": nombre, "url": url, "t": max(t), "t_ini": min(t)})
    return out


BASE = "https://nisar.asf.earthdatacloud.nasa.gov/NISAR/"
DEMO_CATALOGO = [  # R14: escenas reales GCOV (14 nov 2026)
    "NISAR_L2_PR_GCOV_028_003_A_176_4005_DHDH_A_20260813T110112_20260813T110148_P05023_N_F_J_001",
    "NISAR_L2_PR_GCOV_033_003_A_176_4005_DHDH_A_20261012T110112_20261012T110148_P05023_N_F_J_001",
    "NISAR_L2_PR_GCOV_034_003_A_176_4005_DHDH_A_20261024T110112_20261024T110149_P05036_N_F_J_001",
    "NISAR_L2_PR_GCOV_033_112_D_090_4005_DHDH_A_20261019T233944_20261019T234018_P05023_N_F_J_001",
    "NISAR_L2_PR_GCOV_034_112_D_090_4005_DHDH_A_20261031T233944_20261031T234018_P05036_N_F_J_001",
    "NISAR_L2_PR_GCOV_033_104_A_175_2005_DHDH_A_20261019T110900_20261019T110934_P05023_N_F_J_001",
    "NISAR_L2_PR_GCOV_034_104_A_175_2005_DHDH_A_20261031T110900_20261031T110935_P05036_N_F_J_001",
    "NISAR_L2_PR_GCOV_033_112_D_091_4005_DHDH_A_20261019T234017_20261019T234052_P05023_N_F_J_001",
    "NISAR_L2_PR_GCOV_034_112_D_091_4005_DHDH_A_20261031T234017_20261031T234052_P05036_N_F_J_001",
]
# Frames que cubren cada zona según la consulta CMR del 14 nov 2026 (R14)
FRAMES_DEMO = {
    "tumbes": {(3, "A", 176), (112, "D", 90)}, "zarumilla": {(3, "A", 176), (112, "D", 90)},
    "pizarro": {(3, "A", 176), (112, "D", 90)}, "piura": {(104, "A", 175), (112, "D", 91)},
    "sullana": {(104, "A", 175), (112, "D", 91)},
}


def _madurez(crid):
    return "VALIDATED" if crid == "P05036" else "PROVISIONAL"


def catalogo(zona, modo="DEMO", producto="GCOV"):
    lat, lon = ZONAS[zona]["punto"]
    if modo == "REAL":
        res = []
        try:
            for mad, cid in COLECCIONES[producto].items():
                if mad == "BETA":
                    continue
                for g in cmr_buscar(cid, lat, lon):
                    g["madurez"] = mad
                    res.append(g)
        except Exception as e:
            # Respaldo: la lista de escenas REALES consultada en el CMR el 14 nov 2026 (R14), con sus URL de ASF.
            print(f"      CMR no respondió ({type(e).__name__}); uso la lista de escenas reales del 14 nov (R14)", flush=True)
            return catalogo(zona, "DEMO", producto)
        return res
    res = []
    for n in DEMO_CATALOGO:
        d = parse_nombre(n)
        if d["geom"] in FRAMES_DEMO.get(zona, set()):
            col = "NISAR_L2_GCOV_V1" if d["CRID"] == "P05036" else "NISAR_L2_GCOV_PROVISIONAL_V1"
            res.append({**d, "nombre": n, "url": f"{BASE}{col}/{n}/{n}.h5", "madurez": _madurez(d["CRID"])})
    return res


def en_gap(t):
    return GAP_START <= t < GAP_END


def pares(evento, cat):
    """Última escena antes del evento y primera después, por geometría, con el mismo modo de polarización."""
    filas = []
    for z in evento["zonas"]:
        por_geom = {}
        for g in cat.get(z, []):
            if not en_gap(g["t"]):
                por_geom.setdefault(g["geom"], []).append(g)
        for geom, gs in por_geom.items():
            gs = sorted(gs, key=lambda g: g["t"])
            antes = [g for g in gs if g["t"] < evento["inicio"]]
            despues = [g for g in gs if g["t"] > evento["fin"]]
            a = antes[-1] if antes else None
            d = next((x for x in despues if a is None or x["POLE"] == a["POLE"]), None)
            filas.append(dict(
                evento=evento["id"], zona=z, geom=f"{geom[0]:03d}_{geom[1]}_{geom[2]:03d}",
                antes=a["t"] if a else None, despues=d["t"] if d else None, pol=a["POLE"] if a else None,
                mezcla_madurez=bool(a and d and a["madurez"] != d["madurez"]),
                estado="ok" if (a and d) else ("sin escena posterior publicada" if a else "sin escena previa"),
                _a=a, _d=d))
    return filas
