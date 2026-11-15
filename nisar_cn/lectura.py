"""Lectura de la ventana de una zona en un GCOV, y HDF5 sintéticos para el modo DEMO.

- Capas y rutas: R2 [V] (HHHH, HVHV, rtcGammaToSigmaFactor, numberOfLooks, mask; píxel 10/20 m según ancho de banda).
- `find_grid` y recorte por ventana: adaptados del código del equipo (R15 [V]).
- incidenceAngle como cubo de metadatos: NISAR Data User Guide, página «Metadata», tabla 1 [V].
- Valores de `mask`: 0 inválido o parcialmente enfocado, 1–5 válido (sub-swath), 255 relleno: JPL D-102274 Rev D,
  sec. 4.3.3 (R16 [V], releída el 15 nov 2026). Se aplica en limpieza.mascara_valida.
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
    Ruta del grupo `metadata/radarGrid`: R16, sec. 3.2.4 y tabla 5-1 [V]."""
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
        capas["theta_deg"], nota = _theta(h5, inc, x[c0:c1], y[r0:r1])
    return dict(capas=capas, x=x[c0:c1], y=y[r0:r1], dx=dx, dy=dy, epsg=epsg, rutas_incidencia=inc, nota_theta=nota)


def _theta(h5, inc, x, y):
    """Interpola el cubo incidenceAngle a la ventana (limpieza.theta_desde_cubo). None si no se puede."""
    if not inc:
        return None, "sin cubo incidenceAngle en el producto"
    try:
        from .limpieza import theta_desde_cubo
        th, alt = theta_desde_cubo(h5, inc[0], x, y)
        return th, f"θ interpolado del cubo {inc[0]} (altura {alt:.0f} m)"
    except Exception as e:
        return None, f"no se pudo interpolar {inc[0]}: {type(e).__name__}: {e}"


def completar_theta(L, h5):
    """Para recortes guardados antes de existir el cálculo de θ: lee solo el cubo (pocos KB) y lo agrega."""
    if L["capas"].get("theta_deg") is None and L.get("rutas_incidencia"):
        L["capas"]["theta_deg"], L["nota_theta"] = _theta(h5, L["rutas_incidencia"], L["x"], L["y"])
    return L


def guardar_lectura(L, ruta: Path):
    np.savez_compressed(ruta, x=L["x"], y=L["y"], dx=L["dx"], dy=L["dy"], epsg=L["epsg"],
                        inc=np.array(L["rutas_incidencia"], dtype=str), nota_theta=np.array(L.get("nota_theta", "")),
                        **{f"c_{k}": v for k, v in L["capas"].items() if v is not None})


def cargar_lectura(ruta: Path):
    z = np.load(ruta)
    capas = {k: (z[f"c_{k}"] if f"c_{k}" in z else None)
             for k in ("HHHH", "HVHV", "rtcGammaToSigmaFactor", "numberOfLooks", "mask", "theta_deg")}
    return dict(capas=capas, x=z["x"], y=z["y"], dx=float(z["dx"]), dy=float(z["dy"]), epsg=int(z["epsg"]),
                rutas_incidencia=list(z["inc"]), nota_theta=str(z["nota_theta"]) if "nota_theta" in z else "")


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
        G["numberOfLooks"] = np.full(X.shape, 12, "float32")
        mk = np.ones(X.shape, "uint8"); mk[:, :25] = 0; mk[:8, :] = 255          # borde inválido y relleno (R16)
        G["mask"] = mk
        # Cubo de ángulo de incidencia con la estructura de R16 (alto, y, x); valores sintéticos 33–47°.
        R = h5.create_group("/science/LSAR/GCOV/metadata/radarGrid")
        cx = np.linspace(x[0] - 5000, x[-1] + 5000, 12); cy = np.linspace(y[0] + 5000, y[-1] - 5000, 10)
        alt = np.array([-500.0, 0.0, 500.0, 1500.0])
        inc = 33 + 14 * (cx - cx[0]) / (cx[-1] - cx[0])
        R["incidenceAngle"] = np.broadcast_to(inc[None, None, :], (len(alt), len(cy), len(cx))).astype("float32")
        R["xCoordinates"] = cx; R["yCoordinates"] = cy; R["heightAboveEllipsoid"] = alt
    return p


def explorar_capas(fuente, patrones=("coherence", "soilMoisture", "DSG", "PMI", "TSR", "uncertainty", "incidenceAngle")):
    """Lista las rutas que coinciden con cada patrón (para fijar rutas de GUNW/SME2)."""
    with h5py.File(fuente, "r") as h5:
        return {p: buscar_dataset(h5, p) for p in patrones}
