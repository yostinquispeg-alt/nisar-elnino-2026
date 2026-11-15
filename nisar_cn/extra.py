"""Productos NISAR adicionales: L3 SME2 (humedad del suelo) y L2 GUNW (coherencia interferométrica).

- SME2: humedad volumétrica del suelo (m³/m³) a 200 m, calculada por NASA (R3). Es la medida directa de "suelo
  más húmedo" que nuestro Δε′ solo aproxima.
- GUNW: coherencia entre dos pasadas de 12 días (0–1), solo co-polar (R4). Cae cuando la superficie cambia entre
  pasadas: inundación, suelo removido, cultivos cosechados, huaicos.

[?] Rutas internas: no las tomo de la especificación sino que las BUSCO en el archivo, por nombre de dataset
(soilMoisture, coherenceMagnitude) y con las coordenadas xCoordinates/yCoordinates del mismo grupo, que es la
convención de las grillas L2 de NISAR (la misma del GCOV). Si no se encuentran, el producto se omite y se avisa:
`python 2_mapa/generar_mapa.py --diagnostico` imprime la estructura real para corregirlo.
"""
from pathlib import Path

import numpy as np

from .config import COLECCIONES, ZONAS, bbox

UMBRAL_COHERENCIA_BAJA = 0.3   # [A][?] corte para "superficie que cambió"; falta referencia


def _buscar(h5, raiz, nombre):
    import h5py
    hallado = []

    def f(n, o):
        if isinstance(o, h5py.Dataset) and n.split("/")[-1].lower() == nombre.lower():
            hallado.append(n)
            return True
    if raiz in h5:
        h5[raiz].visititems(f)
    return f"{raiz}/{hallado[0]}" if hallado else None


def _epsg(h5, grupo, x):
    for k in ("projection", "../projection"):
        p = f"{grupo}/{k}"
        try:
            if p in h5:
                for a in ("epsg_code", "epsg"):
                    if a in h5[p].attrs:
                        return int(np.ravel(h5[p].attrs[a])[0])
                v = h5[p][()]
                if np.ndim(v) == 0 and int(v) > 1000:
                    return int(v)
        except Exception:
            pass
    return 4326 if np.nanmax(np.abs(x)) <= 360 else None


def leer_capa(h5, raiz, nombre, caja):
    """Recorte de la zona de un dataset 2-D con xCoordinates/yCoordinates en su grupo o en el grupo padre."""
    from pyproj import Transformer
    ruta = _buscar(h5, raiz, nombre)
    if not ruta:
        raise KeyError(f"no encontré '{nombre}' bajo {raiz}")
    grupo = ruta.rsplit("/", 1)[0]
    for g in (grupo, grupo.rsplit("/", 1)[0], grupo.rsplit("/", 2)[0]):
        if f"{g}/xCoordinates" in h5:
            break
    else:
        raise KeyError(f"no encontré xCoordinates cerca de {ruta}")
    x, y = h5[f"{g}/xCoordinates"][()], h5[f"{g}/yCoordinates"][()]
    epsg = _epsg(h5, g, x)
    if epsg is None:
        raise KeyError(f"no pude determinar la proyección de {ruta}")
    tr = Transformer.from_crs(4326, epsg, always_xy=True)
    xs, ys = tr.transform([caja["w"], caja["e"], caja["w"], caja["e"]], [caja["s"], caja["s"], caja["n"], caja["n"]])
    c = np.where((x >= min(xs)) & (x <= max(xs)))[0]
    r = np.where((y >= min(ys)) & (y <= max(ys)))[0]
    if len(c) < 2 or len(r) < 2:
        raise ValueError("la zona cae fuera de la escena")
    v = h5[ruta][r[0]:r[-1] + 1, c[0]:c[-1] + 1].astype("float32")
    fill = h5[ruta].attrs.get("_FillValue")
    if fill is not None:
        v[v == np.ravel(fill)[0]] = np.nan
    return dict(v=v, x=x[c[0]:c[-1] + 1], y=y[r[0]:r[-1] + 1], epsg=epsg, ruta=ruta)


def _png(capa, carpeta: Path, nombre, prefijo, lo, hi, cmap):
    import matplotlib.pyplot as plt
    from .mapas import _a_latlon, _secuencial
    x, y = capa["x"], capa["y"]
    if capa["epsg"] == 4326:
        b = dict(s=float(y.min()), n=float(y.max()), w=float(x.min()), e=float(x.max()))
        v = capa["v"] if y[0] > y[-1] else capa["v"][::-1]
    else:
        (v,), b = _a_latlon([capa["v"]], x, y, capa["epsg"])
    plt.imsave(carpeta / nombre, _secuencial(v, lo, hi, cmap))
    return f"{prefijo}/{nombre}", b


def _serie_producto(producto, zona, cache: Path, carpeta: Path, prefijo, verbose=True):
    import h5py
    from .acceso import abrir_remoto
    from .busqueda import cmr_buscar
    lat, lon = ZONAS[zona]["punto"]
    gs = []
    for mad, cid in COLECCIONES[producto].items():
        try:
            for g in cmr_buscar(cid, lat, lon, generico=True):
                g["madurez"] = mad
                gs.append(g)
        except Exception as e:
            print(f"      {producto} {zona}: CMR falló ({type(e).__name__})", flush=True)
    gs = sorted({g["nombre"]: g for g in gs}.values(), key=lambda g: g["t"])
    if verbose:
        print(f"   {producto} {zona}: {len(gs)} escenas", flush=True)
    out = []
    for g in gs:
        npz = cache / f"{g['nombre']}_{zona}_{producto}.npz"
        try:
            if npz.exists():
                z = np.load(npz)
                capa = dict(v=z["v"], x=z["x"], y=z["y"], epsg=int(z["epsg"]))
            else:
                with h5py.File(abrir_remoto(g), "r") as h5:
                    if producto == "SME2":
                        capa = leer_capa(h5, "/science/LSAR/SME2", "soilMoisture", bbox(zona))
                    else:
                        capa = leer_capa(h5, "/science/LSAR/GUNW/grids", "coherenceMagnitude", bbox(zona))
                np.savez_compressed(npz, v=capa["v"], x=capa["x"], y=capa["y"], epsg=capa["epsg"])
                if verbose:
                    print(f"      {g['t']:%d %b}: {capa.get('ruta', '')} {capa['v'].shape}", flush=True)
        except Exception as e:
            print(f"      {producto} {g['t']:%d %b} omitida ({type(e).__name__}: {e})", flush=True)
            continue
        v = capa["v"]
        nombre = f"{zona}_{producto}_{g['t']:%Y%m%d}_{g['nombre'][-12:]}.png"
        if producto == "SME2":
            url, b = _png(capa, carpeta, nombre, prefijo, 0.0, 0.5, "YlGnBu")
            met = {"humedad_med_m3m3": float(np.nanmedian(v)) if np.isfinite(v).any() else None}
        else:
            url, b = _png(capa, carpeta, nombre, prefijo, 0.0, 1.0, "magma")
            ok = np.isfinite(v)
            met = {"coherencia_med": float(np.nanmedian(v)) if ok.any() else None,
                   "frac_coherencia_baja": float((v[ok] < UMBRAL_COHERENCIA_BAJA).mean()) if ok.any() else None}
        out.append({"fecha": g["t"].isoformat(), "fecha_ini": g.get("t_ini", g["t"]).isoformat(), "granulo": g["nombre"], "madurez": g["madurez"],
                    "png": url, "bounds": b, "metricas": met})
    return out


def productos_extra(zonas, cache: Path, salida: Path, modo="REAL", verbose=True):
    """Devuelve {zona: {"SME2": [...], "GUNW": [...]}}. En DEMO no hay productos extra."""
    if modo != "REAL":
        return {}
    sub = "extra_real"
    carpeta = salida / sub
    carpeta.mkdir(parents=True, exist_ok=True)
    res = {}
    for z in zonas:
        res[z] = {}
        for prod in ("SME2", "GUNW"):
            try:
                res[z][prod] = _serie_producto(prod, z, cache, carpeta, f"../salidas/{sub}", verbose)
            except Exception as e:
                print(f"   {prod} {z}: omitido ({type(e).__name__}: {e})", flush=True)
                res[z][prod] = []
    return res
