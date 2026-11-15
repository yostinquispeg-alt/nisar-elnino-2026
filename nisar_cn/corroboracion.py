"""Corroboración de lo que mide NISAR con fuentes independientes (sección 9 del notebook).

| Fuente | Qué aporta | Acceso | Ref. |
|---|---|---|---|
| CHIRPS v3 diario «sat» (prelim) | lluvia 0,05°: total pentadal mezclado con estaciones y repartido por día con IMERG Late V07 | HTTPS abierto, sin llave (UCSB-CHC) | R23 [V] |
| GPM IMERG Late diario V07 (GPM_3IMERGDL, NASA) | lluvia satelital diaria 0,1° | CMR + HTTPS con llave Earthdata; exige aceptar la EULA de GES DISC | R19, R25 [V] |
| Open-Meteo Historical Weather API | lluvia diaria de reanálisis ECMWF | API sin llave, uso no comercial | R21 [V] |
| Estaciones Senamhi citadas en la prensa | lluvia medida (mm) | notas N1, N3, N5, N8–N10, N15; coordenadas del mapa de estaciones (R22) | [V] |
| Caudal del río Tumbes (El Tigre) | 1 021,33 m³/s el 2 nov a las 5:00 | N3, N4 | [V] |
| Umbrales del río Tumbes | impactos desde 743,49 m³/s (151 ha); 1 629,02 m³/s (1 234 ha) | Breña Aliaga et al. (2026) | R18 [V] |
| Carta Internacional, activación 1058 | confirmación institucional (Zarumilla) | página de la activación | R20 [V] |
| Copernicus EMS Rapid Mapping | ¿hay activación para Perú? | API pública del portal | R24 [V] |
| Verificación dicotómica (POD, FAR, CSI, sesgo) | puntaje de la correspondencia | definiciones JWGFVR (WWRP/WMO) | R26 [V] |
"""
import datetime as dt
import json
from pathlib import Path

import numpy as np

from .config import COLECCIONES, CRONICA, EVENTOS, LIMA, UTC, ZONAS, bbox

IMERG_CID = "C2723754859-GES_DISC"     # R19 [V]
CHIRPS_URL = ("https://data.chc.ucsb.edu/products/CHIRPS/v3.0/daily/prelim/sat/netcdf/byYear/"
              "chirps-v3.0_prelim.sat.{anio}.days_p05.nc")   # R23 [V] (listado del servidor, 15 nov 2026)

# --- Lluvia medida en estaciones, tal como la reportan las notas abiertas (mm). fin = fin del periodo (Lima).
# lat/lon: mapa de estaciones de Senamhi (R22, leído el 15 nov 2026) [V]; None = la nota no da una estación de
# Senamhi identificable y se usa el punto de la zona [A].
ESTACIONES = [
    dict(estacion="Aeropuerto de Tumbes", zona="tumbes", fin=dt.datetime(2026, 10, 22, 8, tzinfo=LIMA), mm=70.0,
         periodo="una noche (21–22 oct)", horas=12, fuente="N9", nota="dato del especialista A. Levy, no de Senamhi",
         lat=None, lon=None),
    dict(estacion="Puerto Pizarro", zona="pizarro", fin=dt.datetime(2026, 10, 23, 8, tzinfo=LIMA), mm=52.0,
         periodo="acumulado del evento", horas=None, fuente="N1", nota="Senamhi según la nota",
         lat=-3.50396, lon=-80.39538, cod="103038"),
    dict(estacion="Zarumilla", zona="zarumilla", fin=dt.datetime(2026, 10, 27, 6, tzinfo=LIMA), mm=99.3,
         periodo="00:00 del 26 a 06:00 del 27 oct", horas=30, fuente="N10", nota="Senamhi",
         lat=None, lon=None),
    dict(estacion="El Salto", zona="zarumilla", fin=dt.datetime(2026, 10, 27, 7, tzinfo=LIMA), mm=102.0,
         periodo="24 h (hora de cierre no indicada)", horas=24, fuente="N5", nota="Senamhi; máximo del mes",
         lat=-3.45171, lon=-80.2802, cod="103041"),
    dict(estacion="El Salto", zona="zarumilla", fin=dt.datetime(2026, 11, 2, 7, tzinfo=LIMA), mm=104.1,
         periodo="24 h (hora de cierre no indicada)", horas=24, fuente="N3", nota="Senamhi",
         lat=-3.45171, lon=-80.2802, cod="103041"),
    dict(estacion="El Salto", zona="zarumilla", fin=dt.datetime(2026, 11, 2, 7, tzinfo=LIMA), mm=110.3,
         periodo="«madrugada» del 2 nov (periodo no indicado)", horas=None, fuente="N5",
         nota="Senamhi; lo normal de noviembre ≈ 9 mm", lat=-3.45171, lon=-80.2802, cod="103041"),
    dict(estacion="Cabo Inga", zona="tumbes", fin=dt.datetime(2026, 11, 4, 19, tzinfo=LIMA), mm=74.4,
         periodo="16:00–19:00 del 4 nov", horas=3, fuente="N15", nota="Senamhi",
         lat=-3.97594, lon=-80.40182, cod="103043"),
]
# El Salto, 2 nov: N3 da 104,1 mm «en 24 horas» y N5 da 110,3 mm «durante la madrugada», sin periodo. Son dos
# ventanas distintas informadas por dos medios; se conservan las dos y no se elige una [V] (ambas notas releídas
# el 15 nov 2026). Lecturas de N8 sin periodo (no se grafican): Puerto Pizarro 45,2 mm, Campamento Sede 25,1 mm,
# Puente Tumbes 12,9 mm, Hualcuy 34,7 mm, Paimas 24,5 mm.

CAUDALES_TUMBES = [
    dict(fecha=dt.datetime(2026, 11, 2, 5, tzinfo=LIMA), m3s=1021.33, estacion="El Tigre", fuente="N3, N4"),
]
UMBRAL_ALERTA_ROJA_M3S = 1000.0          # N3 (aviso Senamhi N.° 1667) y N5 [V]
UMBRAL_IMPACTO_BRENA_M3S = 743.49        # R18, resumen y «Highlights»: 151 ha, 157 habitantes [V]
UMBRAL_EXTREMO_BRENA_M3S = 1629.02       # R18, resumen: 1 234 ha agrícolas, 749 habitantes [V]
# Área de estudio de R18 (fig. 2, marco «Study Area», UTM 17S): del El Tigre al mar. Coordenadas leídas de los
# ejes de la figura [V figura], con lectura a ±1 km [A].
AREA_R18_UTM17S = dict(e0=549_000, e1=571_000, n0=9_582_000, n1=9_616_000)

CARTA = dict(activacion=1058, fecha=dt.datetime(2026, 11, 3, 14, 52, tzinfo=dt.timezone(dt.timedelta(hours=2))),
             zona="zarumilla", url="https://disasterscharter.org/activations/flood-in-peru-activation-1058-",
             texto="Activación 1058 de la Carta Internacional (3 nov 2026, 14:52 UTC+2), pedida por INDECI en nombre de "
                   "CONIDA: desborde del río Zarumilla sobre el asentamiento Puerto Perú (Aguas Verdes), más de 150 "
                   "viviendas dañadas y más de 700 personas afectadas. Gestor del proyecto: CONIDA. Al 15 nov 2026 la "
                   "página no lista productos cartográficos.")
CEMS_API = "https://rapidmapping.emergency.copernicus.eu/backend/dashboard-api/public-activations-info/"


# ---------------------------------------------------------------- utilidades
def _celda(lat, lon, la, lo):
    return int(np.argmin(np.abs(lat - la))), int(np.argmin(np.abs(lon - lo)))


def _serie_dict(datos, zonas, fuente):
    dias = sorted(datos)
    if not dias:
        return {}
    return {z: {"fechas": dias, "mm": [datos[d].get(z) for d in dias], "fuente": fuente} for z in zonas}


def _puntos(zonas):
    """Puntos donde se extrae la lluvia: cada zona y cada estación con coordenadas (clave 'est:<nombre>')."""
    p = {z: ZONAS[z]["punto"] for z in zonas}
    for x in ESTACIONES:
        if x.get("lat") is not None:
            p[f"est:{x['estacion']}"] = (x["lat"], x["lon"])
    return p


# ---------------------------------------------------------------- CHIRPS v3 (abierto)
def chirps_zonas(cache: Path, inicio="2026-08-01", fin=None, verbose=True):
    """Lluvia diaria CHIRPS v3 «sat» (prelim) en la celda de 0,05° de cada zona y estación.

    Lee por HTTPS solo el bloque de filas/columnas que cubre la costa norte (todas las zonas caen en el mismo
    trozo HDF5), sin bajar el archivo anual de 2,7 GB. No requiere credenciales: NO se envía la llave Earthdata.
    R23: el diario CHIRPS no es un producto diario independiente (el total es pentadal); sirve para acumulados
    entre pasadas NISAR (~12 días), que es como se usa en la matriz 9.3."""
    import fsspec
    import h5py
    fin = fin or (dt.date.today() - dt.timedelta(days=1)).isoformat()
    ruta = cache / "chirps_v3_sat.json"
    datos = json.loads(ruta.read_text()) if ruta.exists() else {}
    puntos = _puntos(list(ZONAS))
    d0, d1 = dt.date.fromisoformat(inicio), dt.date.fromisoformat(fin)
    faltan = [(d0 + dt.timedelta(days=k)).isoformat() for k in range((d1 - d0).days + 1)]
    faltan = [d for d in faltan if d not in datos or any(k not in datos[d] for k in puntos)]
    if faltan:
        fs = fsspec.filesystem("https")
        for anio in sorted({d[:4] for d in faltan}):
            url = CHIRPS_URL.format(anio=anio)
            if verbose:
                print(f"CHIRPS v3 {anio}: leyendo solo la ventana de la costa norte de {url.rsplit('/', 1)[1]}", flush=True)
            with fs.open(url, block_size=1024 * 1024, cache_type="blockcache") as f, h5py.File(f, "r") as h5:
                lat, lon = h5["latitude"][()], h5["longitude"][()]
                t = h5["time"][()]
                base = dt.date(1980, 1, 1)   # unidades «days since 1980-1-1» (atributo del archivo)
                fechas = [(base + dt.timedelta(days=int(v))).isoformat() for v in t]
                idx = {k: _celda(lat, lon, *ll) for k, ll in puntos.items()}
                i0, i1 = min(i for i, _ in idx.values()), max(i for i, _ in idx.values()) + 1
                j0, j1 = min(j for _, j in idx.values()), max(j for _, j in idx.values()) + 1
                sel = [k for k, f_ in enumerate(fechas) if f_ in set(faltan)]
                if not sel:
                    continue
                bloque = h5["precip"][sel[0]:sel[-1] + 1, i0:i1, j0:j1]
                fill = float(np.atleast_1d(h5["precip"].attrs.get("_FillValue", -9999.0))[0])
                for n, k in enumerate(range(sel[0], sel[-1] + 1)):
                    fila = {}
                    for key, (i, j) in idx.items():
                        v = float(bloque[n, i - i0, j - j0])
                        fila[key] = None if (v < 0 or v == fill or not np.isfinite(v)) else round(v, 2)
                    datos[fechas[k]] = fila
        ruta.write_text(json.dumps(datos))
    datos = {d: v for d, v in datos.items() if inicio <= d <= fin}
    if verbose:
        print(f"CHIRPS v3: {len(datos)} días ({min(datos, default='—')} a {max(datos, default='—')})", flush=True)
    return _serie_dict(datos, list(puntos), "CHIRPS v3 diario «sat» (estaciones + IMERG Late V07)")


# ---------------------------------------------------------------- GPM IMERG
def _imerg_granulos(inicio, fin):
    import requests
    out, page = [], 1
    while True:
        r = requests.get("https://cmr.earthdata.nasa.gov/search/granules.json",
                         params={"collection_concept_id": IMERG_CID, "temporal": f"{inicio}T00:00:00Z,{fin}T23:59:59Z",
                                 "page_size": 200, "page_num": page, "sort_key": "start_date"}, timeout=(10, 60))
        r.raise_for_status()
        ents = r.json()["feed"]["entry"]
        for e in ents:
            url = next((l["href"] for l in e.get("links", []) if l["href"].endswith(".nc4")
                        and l["href"].startswith("https") and "opendap" not in l["href"].lower()), None)
            if url:
                out.append({"dia": e["time_start"][:10], "url": url})
        if len(ents) < 200:
            return out
        page += 1


def diagnostico_imerg(url):
    """Pide 8 bytes con la llave y devuelve (código HTTP, mensaje del servidor). Para un 403 de GES DISC el
    cuerpo trae 'error_description' y 'resolution_url' (observado el 15 nov 2026: «EULA Acceptance Failure»)."""
    import requests
    from .acceso import NOMBRES_PASS, NOMBRES_TOKEN, NOMBRES_USER, _primero, cargar_env
    cargar_env()
    _, u = _primero(NOMBRES_USER)
    _, p = _primero(NOMBRES_PASS)
    _, tok = _primero(NOMBRES_TOKEN)
    h, auth = {"Range": "bytes=0-7"}, None
    if u and p:
        auth = (u, p)
    elif tok:
        h["Authorization"] = f"Bearer {tok.removeprefix('Bearer ').strip()}"
    r = requests.get(url, headers=h, auth=auth, timeout=(10, 60))
    try:
        j = r.json()
        return r.status_code, f"{j.get('error_description', '')} → {j.get('resolution_url', '')}".strip(" →")
    except ValueError:
        return r.status_code, r.reason


def imerg_zonas(cache: Path, inicio="2026-08-01", fin=None, zonas=None, verbose=True):
    """Lluvia diaria IMERG Late (mm/día) en la celda de 0,1° de cada zona y estación. Devuelve {} si no hay datos."""
    import h5py
    from .acceso import sistema_https
    puntos = _puntos(zonas or list(ZONAS))
    fin = fin or (dt.date.today() - dt.timedelta(days=1)).isoformat()
    ruta = cache / "imerg_late.json"
    datos = json.loads(ruta.read_text()) if ruta.exists() else {}
    gs = _imerg_granulos(inicio, fin)
    faltan = [g for g in gs if g["dia"] not in datos or any(k not in datos[g["dia"]] for k in puntos)]
    if verbose:
        print(f"IMERG: {len(gs)} días en el CMR, {len(faltan)} por leer (el resto desde caché)", flush=True)
    fs = sistema_https() if faltan else None
    for k, g in enumerate(faltan, 1):
        try:
            with fs.open(g["url"], block_size=2 * 1024 * 1024, cache_type="blockcache") as f, h5py.File(f, "r") as h5:
                lat, lon = h5["lat"][()], h5["lon"][()]
                p = h5["precipitation"]
                fila = {}
                for key, (la, lo) in puntos.items():
                    i, j = _celda(lat, lon, la, lo)
                    idx = [0] * p.ndim
                    idx[list(p.shape).index(len(lon))] = j
                    idx[list(p.shape).index(len(lat))] = i
                    v = float(p[tuple(idx)])
                    fila[key] = None if v < 0 else round(v, 2)
                datos[g["dia"]] = fila
        except Exception as e:
            cod, msg = diagnostico_imerg(g["url"]) if k == 1 else (None, "")
            print(f"   IMERG {g['dia']}: falló ({type(e).__name__}: {str(e)[:100]})", flush=True)
            if cod in (401, 403):
                print(f"   GES DISC respondió {cod}: {msg}\n   Abre ese enlace una vez con tu cuenta Earthdata, acepta la "
                      "EULA de «NASA GESDISC DATA ARCHIVE» y vuelve a correr. Se detiene IMERG para no repetir el error.",
                      flush=True)
                break
            continue
        if verbose and k % 10 == 0:
            print(f"   IMERG: {k}/{len(faltan)}", flush=True)
            ruta.write_text(json.dumps(datos))
    if datos:
        ruta.write_text(json.dumps(datos))
    return _serie_dict(datos, list(puntos), "NASA GPM IMERG Late diario V07")


# ---------------------------------------------------------------- estaciones vs productos en malla
def _suma_ventana(serie_k, fin_local, dias):
    """Suma de los valores diarios cuyo día de calendario cae en los `dias` que terminan el día de `fin_local`."""
    if not serie_k:
        return None
    d1 = fin_local.date()
    ds = {(d1 - dt.timedelta(days=n)).isoformat() for n in range(dias)}
    v = [m for f, m in zip(serie_k["fechas"], serie_k["mm"]) if f in ds and m is not None]
    return round(sum(v), 1) if len(v) == dias else None


def contraste_estaciones(productos: dict):
    """Para cada lectura de estación: lluvia de cada producto en la celda de la estación (o de la zona), en el día
    de cierre y en los 2 días que terminan ese día (las ventanas de 24 h cruzan la medianoche) [A]."""
    import pandas as pd
    filas = []
    for x in ESTACIONES:
        clave = f"est:{x['estacion']}" if x.get("lat") is not None else x["zona"]
        fila = dict(estacion=x["estacion"], fin=x["fin"].strftime("%Y-%m-%d %H:%M"), periodo=x["periodo"],
                    mm_estacion=x["mm"], fuente=x["fuente"])
        for nombre, prod in productos.items():
            prod = prod or {}
            s = prod.get(clave) or prod.get(x["zona"])
            con_coord = x.get("lat") is not None and clave in prod
            fila[f"{nombre}_celda"] = "—" if s is None else ("estación" if con_coord else "zona")
            fila[f"{nombre}_dia"] = _suma_ventana(s, x["fin"], 1)
            fila[f"{nombre}_2dias"] = _suma_ventana(s, x["fin"], 2)
        filas.append(fila)
    return pd.DataFrame(filas)


# ---------------------------------------------------------------- NISAR después del 2 nov y solape con R18
def escenas_despues(desde=dt.datetime(2026, 11, 2, 12, tzinfo=UTC), zonas=("tumbes", "zarumilla", "pizarro")):
    """Consulta en vivo al CMR: escenas NISAR (todas las colecciones y madureces) posteriores a `desde`."""
    import requests
    filas = []
    for z in zonas:
        la, lo = ZONAS[z]["punto"]
        for prod, cids in COLECCIONES.items():
            for mad, cid in cids.items():
                r = requests.get("https://cmr.earthdata.nasa.gov/search/granules.json",
                                 params={"collection_concept_id": cid, "point": f"{lo},{la}", "page_size": 50,
                                         "temporal": f"{desde:%Y-%m-%dT%H:%M:%SZ},", "sort_key": "start_date"},
                                 timeout=(10, 40))
                r.raise_for_status()
                for e in r.json()["feed"]["entry"]:
                    filas.append(dict(zona=z, producto=prod, madurez=mad, inicio=e["time_start"], escena=e["title"]))
    return filas


def solape_r18(zona="tumbes"):
    """Fracción de la caja de la zona dentro del área de estudio de R18 (UTM 17S, fig. 2)."""
    from pyproj import Transformer
    c = bbox(zona)
    tr = Transformer.from_crs(4326, 32717, always_xy=True)
    xs, ys = tr.transform([c["w"], c["e"], c["w"], c["e"]], [c["s"], c["s"], c["n"], c["n"]])
    e0, e1, n0, n1 = min(xs), max(xs), min(ys), max(ys)
    a = AREA_R18_UTM17S
    ie = max(0.0, min(e1, a["e1"]) - max(e0, a["e0"]))
    in_ = max(0.0, min(n1, a["n1"]) - max(n0, a["n0"]))
    return dict(zona=zona, caja_km2=round((e1 - e0) * (n1 - n0) / 1e6, 1), dentro_km2=round(ie * in_ / 1e6, 1),
                fraccion=round(ie * in_ / ((e1 - e0) * (n1 - n0)), 3))


def cems_peru():
    """Activaciones de Copernicus EMS Rapid Mapping para Perú (API pública del portal)."""
    import requests
    r = requests.get(CEMS_API, params={"limit": 1000}, timeout=(10, 60))
    r.raise_for_status()
    res = r.json()["results"]
    peru = [x for x in res if "Peru" in x.get("countries", [])]
    return dict(total=len(res), ultima=max((x["activationTime"] for x in res), default=None), peru=peru)


# ---------------------------------------------------------------- correspondencia
REGLA = dict(lluvia_mm=30.0, agua_km2=0.5, veg_km2=0.5, suelo_km2=1.0)   # [A][?] la misma del mapa


def _suma(lluvia_z, tA, tB):
    if not lluvia_z:
        return None
    tot, n = 0.0, 0
    for f, v in zip(lluvia_z["fechas"], lluvia_z["mm"]):
        t = dt.datetime.fromisoformat(f).replace(hour=12, tzinfo=LIMA)
        if tA < t <= tB and v is not None:
            tot += v; n += 1
    return round(tot, 1) if n else None


def matriz_correspondencia(serie, lluvia_reanalisis=None, lluvia_imerg=None, lluvia_chirps=None, regla=None):
    """Una fila por periodo entre dos pasadas NISAR consecutivas de cada serie (zona × órbita)."""
    import pandas as pd
    R = {**REGLA, **(regla or {})}
    filas = []
    for s in serie:
        z, fr = s["zona"], s["frames"]
        for a, b in zip(fr[:-1], fr[1:]):
            tA, tB = dt.datetime.fromisoformat(a["fecha"]), dt.datetime.fromisoformat(b["fecha"])
            notas = [c["id"] for c in CRONICA if z in c["zonas"] and tA < c["fecha"] <= tB]
            evs = [e["id"] for e in EVENTOS if z in e["zonas"] and tA < e["inicio"] <= tB]
            est = [x for x in ESTACIONES if x["zona"] == z and tA < x["fin"] <= tB]
            l_im = _suma((lluvia_imerg or {}).get(z), tA, tB)
            l_ch = _suma((lluvia_chirps or {}).get(z), tA, tB)
            l_re = _suma((lluvia_reanalisis or {}).get(z), tA, tB)
            ma, mb = a["metricas"], b["metricas"]
            dagua = (mb.get("agua_km2") or 0) - (ma.get("agua_km2") or 0)
            evid = bool(notas or evs or est or any((v or 0) >= R["lluvia_mm"] for v in (l_im, l_ch, l_re)))
            senal = dagua > R["agua_km2"] or (mb.get("veg_inundada_nueva_km2") or 0) > R["veg_km2"] \
                or (mb.get("suelo_humedecido_km2") or 0) > R["suelo_km2"]
            dudosa = bool(b.get("calidad", {}).get("sospechosa"))
            ver = ("dato dudoso" if dudosa else "coinciden" if evid and senal else
                   "NISAR no lo ve" if evid else "NISAR sin noticia" if senal else "sin cambio ni noticia")
            filas.append(dict(zona=z, geom=s["geom"], desde=tA, hasta=tB, madurez=f"{a['madurez'][:4]}→{b['madurez'][:4]}",
                              eventos=",".join(evs), noticias=",".join(notas),
                              estaciones_mm=max((x["mm"] for x in est), default=None),
                              lluvia_imerg_mm=l_im, lluvia_chirps_mm=l_ch, lluvia_reanalisis_mm=l_re,
                              dagua_km2=round(dagua, 3), veg_nueva_km2=mb.get("veg_inundada_nueva_km2"),
                              suelo_humedo_km2=mb.get("suelo_humedecido_km2"), veredicto=ver))
    return pd.DataFrame(filas)


def puntajes(mc):
    """Tabla de contingencia y puntajes dicotómicos (R26): «pronóstico» = señal NISAR, «observado» = evidencia
    en tierra. Se excluyen los periodos con dato dudoso."""
    v = mc["veredicto"].value_counts() if len(mc) else {}
    a, c, b, d = (int(v.get(k, 0)) for k in ("coinciden", "NISAR no lo ve", "NISAR sin noticia", "sin cambio ni noticia"))
    div = lambda x, y: round(x / y, 3) if y else None
    return dict(aciertos=a, fallos=c, falsas_alarmas=b, negativos_correctos=d, excluidos_dudosos=int(v.get("dato dudoso", 0)),
                POD=div(a, a + c), FAR=div(b, a + b), CSI=div(a, a + b + c), sesgo=div(a + b, a + c))


def sensibilidad(serie, lluvia_reanalisis=None, lluvia_imerg=None, lluvia_chirps=None,
                 lluvias=(15, 30, 50), aguas=(0.25, 0.5, 1.0), suelos=(0.5, 1.0, 2.0)):
    """Recalcula la matriz con cada combinación de umbrales [A] y mide cuánto cambia respecto de REGLA."""
    import pandas as pd
    base = matriz_correspondencia(serie, lluvia_reanalisis, lluvia_imerg, lluvia_chirps)
    filas = []
    for ll in lluvias:
        for ag in aguas:
            for su in suelos:
                m = matriz_correspondencia(serie, lluvia_reanalisis, lluvia_imerg, lluvia_chirps,
                                           regla=dict(lluvia_mm=ll, agua_km2=ag, veg_km2=ag, suelo_km2=su))
                p = puntajes(m)
                filas.append(dict(lluvia_mm=ll, agua_km2=ag, suelo_km2=su,
                                  igual_a_base=round(float((m["veredicto"] == base["veredicto"]).mean()), 3) if len(m) else None,
                                  **{k: p[k] for k in ("aciertos", "fallos", "falsas_alarmas", "POD", "FAR", "CSI")}))
    return pd.DataFrame(filas)
