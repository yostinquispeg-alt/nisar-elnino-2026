"""Capas PNG en lat/lon para el visor `visor/mapa_nisar.html`.

Para cada par antes/después analizado escribe, en salidas/mapas_<modo>/:
    *_sar_antes.png, *_sar_despues.png   σ⁰ HH en dB (gris, −25…0 dB)
    *_clases_antes.png, *_clases_despues.png   agua / vegetación inundada (clasificar, indicadores.py)
    *_cambio.png    agua ganada / agua perdida entre las dos fechas
    *_dsigma.png    Δσ⁰ HH en dB sobre tierra (divergente, ±5 dB)
    *_deps.png      Δε' sobre tierra = humedad del suelo (Dubois, R8; supone rugosidad constante [A])
    *_hv_antes.png, *_hv_despues.png   σ⁰ HV = vegetación (dispersión de volumen, R6)
    *_dhv.png       Δσ⁰ HV sobre tierra (cambio de vegetación/estructura) [A]
    *_rgb_antes.png, *_rgb_despues.png  compuesto R=σ⁰HH, G=σ⁰HV, B=HH−HV (elección de visualización [A])
    *_impacto.png   todos los efectos en una capa (IMPACTO_CLASES en indicadores.py)

Las grillas GCOV están en coordenadas proyectadas (EPSG del producto, R2). El visor (Leaflet) usa lat/lon,
así que cada capa se remuestrea por vecino más cercano a una grilla regular lat/lon con pyproj [A: método
estándar de remuestreo; no cambia los valores, solo su ubicación].
"""
from pathlib import Path

import numpy as np
from pyproj import Transformer

COLOR = {  # RGBA
    "agua": (30, 120, 255, 230), "veg": (40, 200, 90, 230),
    "ganada": (0, 200, 255, 240), "perdida": (255, 140, 0, 240),
}
COLOR_IMPACTO = {1: (20, 60, 200, 235), 2: (0, 210, 255, 245), 3: (255, 140, 0, 240), 4: (40, 200, 90, 240),
                 5: (170, 90, 255, 220), 6: (165, 105, 45, 220), 7: (150, 150, 150, 200)}


def _a_latlon(arr_list, x, y, epsg, n=None):
    """Remuestrea arrays (filas = y, columnas = x) a una grilla lat/lon regular. Devuelve arrays y bounds."""
    tr = Transformer.from_crs(epsg, 4326, always_xy=True)
    X, Y = np.meshgrid([x.min(), x.max()], [y.min(), y.max()])
    lon, lat = tr.transform(X.ravel(), Y.ravel())
    b = dict(s=float(min(lat)), n=float(max(lat)), w=float(min(lon)), e=float(max(lon)))
    ny, nx = (n or len(y)), (n or len(x))
    LON, LAT = np.meshgrid(np.linspace(b["w"], b["e"], nx), np.linspace(b["n"], b["s"], ny))
    xs, ys = Transformer.from_crs(4326, epsg, always_xy=True).transform(LON, LAT)
    dx, dy = x[1] - x[0], y[1] - y[0]
    ci = np.round((xs - x[0]) / dx).astype(int); ri = np.round((ys - y[0]) / dy).astype(int)
    fuera = (ci < 0) | (ci >= len(x)) | (ri < 0) | (ri >= len(y))
    ci, ri = np.clip(ci, 0, len(x) - 1), np.clip(ri, 0, len(y) - 1)
    out = []
    for a in arr_list:
        v = a[ri, ci].astype("float32")
        v[fuera] = np.nan
        out.append(v)
    return out, b


def _gris(db, lo=-25.0, hi=0.0):
    g = np.nan_to_num(np.clip((db - lo) / (hi - lo), 0, 1))
    rgba = np.zeros(db.shape + (4,), "uint8")
    rgba[..., :3] = (g * 255).astype("uint8")[..., None]
    rgba[..., 3] = np.where(np.isfinite(db), 255, 0)
    return rgba


def _clases(cls):
    rgba = np.zeros(cls.shape + (4,), "uint8")
    rgba[cls == 1] = COLOR["agua"]
    rgba[cls == 2] = COLOR["veg"]
    return rgba


def _cambio(ca, cd):
    rgba = np.zeros(ca.shape + (4,), "uint8")
    v = np.isfinite(ca) & np.isfinite(cd) & (ca != 255) & (cd != 255)
    rgba[v & (cd == 1) & (ca != 1)] = COLOR["ganada"]
    rgba[v & (ca == 1) & (cd != 1)] = COLOR["perdida"]
    return rgba


def _impacto(im):
    rgba = np.zeros(im.shape + (4,), "uint8")
    for k, c in COLOR_IMPACTO.items():
        rgba[im == k] = c
    return rgba


def _secuencial(v, lo, hi, nombre):
    import matplotlib
    rgba = (matplotlib.colormaps[nombre](np.nan_to_num(np.clip((v - lo) / (hi - lo), 0, 1))) * 255).astype("uint8")
    rgba[..., 3] = np.where(np.isfinite(v), 230, 0)
    return rgba


def _rgb(hh, hv):
    """R = σ⁰HH (−25…0 dB), G = σ⁰HV (−32…−8 dB), B = HH−HV (0…15 dB)."""
    n = lambda v, lo, hi: np.nan_to_num(np.clip((v - lo) / (hi - lo), 0, 1))
    rgba = np.zeros(hh.shape + (4,), "uint8")
    rgba[..., 0] = n(hh, -25, 0) * 255; rgba[..., 1] = n(hv, -32, -8) * 255; rgba[..., 2] = n(hh - hv, 0, 15) * 255
    rgba[..., 3] = np.where(np.isfinite(hh) & np.isfinite(hv), 255, 0)
    return rgba


def _divergente(v, lim, nombre="RdBu_r"):
    import matplotlib
    cmap = matplotlib.colormaps[nombre]
    rgba = (cmap(np.nan_to_num(np.clip((v + lim) / (2 * lim), 0, 1))) * 255).astype("uint8")
    rgba[..., 3] = np.where(np.isfinite(v), 220, 0)
    return rgba


def escribir_capas(fila, mapas, carpeta: Path, prefijo_web: str):
    """fila: dict con evento/zona/geom; mapas: salida de indicadores_par. Devuelve dict de rutas y bounds."""
    import matplotlib.pyplot as plt
    carpeta.mkdir(parents=True, exist_ok=True)
    ra, rd = mapas["res"]["a"], mapas["res"]["d"]
    tierra = mapas["tierra"]
    dsig = np.where(tierra, mapas["dsig"], np.nan)
    deps = np.where(tierra, mapas["deps"], np.nan)
    nan = np.full(dsig.shape, np.nan, "float32")
    hva = ra["s0hv_db"] if ra.get("s0hv_db") is not None else nan
    hvd = rd["s0hv_db"] if rd.get("s0hv_db") is not None else nan
    dhv = np.where(tierra, mapas["dhv"], np.nan)
    capas_in = [ra["s0hh_db"], rd["s0hh_db"], ra["cls"].astype("float32"), rd["cls"].astype("float32"), dsig, deps,
                hva, hvd, dhv, mapas["impacto"].astype("float32")]
    (sa, sd, ca, cd, ds, de, va, vd, dv, ip), b = _a_latlon(capas_in, mapas["x"], mapas["y"], mapas["epsg"])
    ca = np.where(np.isfinite(ca), ca, 255); cd = np.where(np.isfinite(cd), cd, 255)
    ip = np.where(np.isfinite(ip), ip, 255)
    base = f"{fila['evento']}_{fila['zona']}_{fila['geom']}"
    imgs = {"sar_antes": _gris(sa), "sar_despues": _gris(sd), "clases_antes": _clases(ca),
            "clases_despues": _clases(cd), "cambio": _cambio(ca, cd),
            "dsigma": _divergente(ds, 5.0), "deps": _divergente(de, 15.0, "BrBG"),
            "hv_antes": _secuencial(va, -30, -10, "YlGn"), "hv_despues": _secuencial(vd, -30, -10, "YlGn"),
            "dhv": _divergente(dv, 4.0, "PiYG"), "rgb_antes": _rgb(sa, va), "rgb_despues": _rgb(sd, vd),
            "impacto": _impacto(ip)}
    rutas = {}
    for k, im in imgs.items():
        nombre = f"{base}_{k}.png"
        plt.imsave(carpeta / nombre, im)
        rutas[k] = f"{prefijo_web}/{nombre}"
    return dict(bounds=b, capas=rutas)
