"""Lectura de la ventana de una zona en un GCOV, y HDF5 sintéticos para el modo DEMO.

- Capas y rutas: R2 [V] (HHHH, HVHV, rtcGammaToSigmaFactor, numberOfLooks, mask; píxel 10/20 m según ancho de banda).
- `find_grid` y recorte por ventana: adaptados del código del equipo (R15 [V]).
- incidenceAngle como cubo de metadatos: NISAR Data User Guide, página «Metadata», tabla 1 [V].
- [?] Significado de los valores de `mask`: requiere la especificación JPL D-102274 Rev. F, sección 4.3.
"""
import re
from pathlib import Path

import h5py
import numpy as np
from pyproj import Transformer


def find_grid(h5):
    for band in ("LSAR", "SSAR"):
        k = f"/science/{band}/GCOV/grids/frequencyA"
        if k in h5:
            return h5[k]
    raise KeyError("No se encontró la grilla GCOV frequencyA")


def buscar_dataset(h5, patron):
    hallados = []
    h5.visititems(lambda n, o: hallados.append(n) if isinstance(o, h5py.Dataset) and re.search(patron, n, re.I) else None)
    return hallados


def rutas_incidencia(h5):
    """Busca el cubo incidenceAngle solo en el grupo de metadatos de geometría, sin recorrer todo el archivo.
    Recorrer el HDF5 completo por streaming obliga a bajar cientos de MB de metadatos.
    [?] Ruta del grupo: falta confirmarla en la especificación JPL D-102274."""
    for band in ("LSAR", "SSAR"):
        for grp in (f"/science/{band}/GCOV/metadata/radarGrid", f"/science/{band}/GCOV/metadata/geolocationGrid"):
            if grp in h5:
                return [f"{grp}/{k}" for k in h5[grp].keys() if "incidence" in k.lower()]
    return []


def leer_ventana(fuente, caja, margen_m=300):
    """fuente: ruta local, objeto tipo archivo (streaming) o h5py.File ya abierto. caja: dict(s, n, w, e) en grados."""
    if isinstance(fuente, h5py.File):
        return _leer_ventana(fuente, caja, margen_m)
    with h5py.File(fuente, "r") as h5:
        return _leer_ventana(h5, caja, margen_m)


def _leer_ventana(h5, caja, margen_m):
    if True:
        g = find_grid(h5)
        epsg = int(g["projection"].attrs.get("epsg_code", g["projection"][()]))
        x, y = g["xCoordinates"][()], g["yCoordinates"][()]
        dx, dy = float(x[1] - x[0]), float(y[1] - y[0])
        tr = Transformer.from_crs(4326, epsg, always_xy=True)
        xs, ys = tr.transform([caja["w"], caja["e"], caja["w"], caja["e"]], [caja["s"], caja["s"], caja["n"], caja["n"]])
        c0 = max(0, int((min(xs) - margen_m - x[0]) / dx)); c1 = min(len(x), int((max(xs) + margen_m - x[0]) / dx) + 1)
        r0 = max(0, int((max(ys) + margen_m - y[0]) / dy)); r1 = min(len(y), int((min(ys) - margen_m - y[0]) / dy) + 1)
        if c1 <= c0 or r1 <= r0:
            raise ValueError("La caja no cae dentro de esta escena")
        lee = lambda k: g[k][r0:r1, c0:c1].astype("float32") if k in g else None
        capas = {k: lee(k) for k in ("HHHH", "HVHV", "rtcGammaToSigmaFactor", "numberOfLooks", "mask")}
        inc = rutas_incidencia(h5)
    return dict(capas=capas, x=x[c0:c1], y=y[r0:r1], dx=dx, dy=dy, epsg=epsg, rutas_incidencia=inc)


def guardar_lectura(L, ruta: Path):
    np.savez_compressed(ruta, x=L["x"], y=L["y"], dx=L["dx"], dy=L["dy"], epsg=L["epsg"],
                        inc=np.array(L["rutas_incidencia"], dtype=str),
                        **{f"c_{k}": v for k, v in L["capas"].items() if v is not None})


def cargar_lectura(ruta: Path):
    z = np.load(ruta)
    capas = {k: (z[f"c_{k}"] if f"c_{k}" in z else None)
             for k in ("HHHH", "HVHV", "rtcGammaToSigmaFactor", "numberOfLooks", "mask")}
    return dict(capas=capas, x=z["x"], y=z["y"], dx=float(z["dx"]), dy=float(z["dy"]), epsg=int(z["epsg"]),
                rutas_incidencia=list(z["inc"]))


def demo_h5(g, caja, zona, cache: Path, post=False):
    """HDF5 SINTÉTICO con la estructura de un GCOV (rutas de R2). Valores inventados: no representan la realidad."""
    cache.mkdir(parents=True, exist_ok=True)
    p = cache / f"{g['nombre']}_{zona}_{'post' if post else 'pre'}_DEMO.h5"
    if p.exists():
        return p
    rng = np.random.default_rng(abs(hash((g["nombre"], zona, post))) % 2**32)
    epsg = 32717   # UTM 17S
    tr = Transformer.from_crs(4326, epsg, always_xy=True)
    x0, y0 = tr.transform(caja["w"] - 0.01, caja["n"] + 0.01)
    x1, y1 = tr.transform(caja["e"] + 0.01, caja["s"] - 0.01)
    px = 10.0 if g["MODE"].startswith("40") else 20.0     # R2, tabla 1
    x = np.arange(x0, x1, px); y = np.arange(y0, y1, -px)
    X, Y = np.meshgrid((x - x.mean()) / 1000, (y - y.mean()) / 1000)
    cauce = np.abs(Y - 0.6 * np.sin(X / 1.5)) < 0.15
    llanura = (np.abs(Y - 0.6 * np.sin(X / 1.5)) < 1.2) & ~cauce
    hh_db = rng.normal(-9, 1.8, X.shape); hv_db = hh_db - rng.normal(7, 1.5, X.shape)
    hh_db[cauce] = rng.normal(-21, 1.5, cauce.sum()); hv_db[cauce] = hh_db[cauce] - 6
    if post:
        nueva = llanura & (rng.random(X.shape) < 0.55)
        hh_db[nueva] = rng.normal(-20, 1.5, nueva.sum()); hv_db[nueva] = hh_db[nueva] - 6
        hh_db[~(cauce | nueva)] += 1.2
    with h5py.File(p, "w") as h5:
        G = h5.create_group("/science/LSAR/GCOV/grids/frequencyA")
        pr = G.create_dataset("projection", data=epsg); pr.attrs["epsg_code"] = epsg
        G["xCoordinates"] = x; G["yCoordinates"] = y
        G["HHHH"] = (10 ** (hh_db / 10)).astype("float32"); G["HVHV"] = (10 ** (hv_db / 10)).astype("float32")
        G["rtcGammaToSigmaFactor"] = np.full(X.shape, 0.9, "float32")
        G["numberOfLooks"] = np.full(X.shape, 12, "float32"); G["mask"] = np.ones(X.shape, "uint8")
    return p


def explorar_capas(fuente, patrones=("coherence", "soilMoisture", "DSG", "PMI", "TSR", "uncertainty", "incidenceAngle")):
    """Lista las rutas que coinciden con cada patrón (para fijar rutas de GUNW/SME2)."""
    with h5py.File(fuente, "r") as h5:
        return {p: buscar_dataset(h5, p) for p in patrones}
