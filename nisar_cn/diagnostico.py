"""Diagnóstico de los datos reales, para cerrar huecos [?] con evidencia de los propios archivos.

1. Valores de la capa `mask` y estadísticas de σ⁰ en los recortes guardados en cache/ (¿qué píxeles marca mask?).
2. Estructura (grupos, datasets, formas) de un producto L3 SME2 (humedad del suelo) y de un L2 GUNW
   (coherencia interferométrica) que cubren Tumbes, para integrarlos con las rutas correctas.

Solo lee metadatos y recortes pequeños. No imprime credenciales.
"""
import time
from pathlib import Path

import numpy as np

from .config import COLECCIONES, ZONAS


def resumen_cache(cache: Path, n=6):
    from .lectura import cargar_lectura
    archivos = sorted(cache.glob("*.npz"))
    print(f"\n== 1. Recortes en cache/: {len(archivos)} ==")
    for f in archivos[:n]:
        L = cargar_lectura(f)
        hh = L["capas"]["HHHH"]
        db = 10 * np.log10(np.where(hh > 0, hh, np.nan))
        m = L["capas"]["mask"]
        print(f"\n{f.name[:90]}")
        print(f"  ventana {hh.shape}, EPSG {L['epsg']}, píxel {abs(L['dx']):.0f} m")
        print(f"  HH dB percentiles 1/50/99: {np.nanpercentile(db, [1, 50, 99]).round(1)} · NaN o ≤0: {np.mean(~np.isfinite(db)):.1%}")
        if m is not None:
            v, c = np.unique(m[np.isfinite(m)], return_counts=True)
            orden = np.argsort(-c)[:10]
            print("  mask, valores más frecuentes:", {float(v[i]): f"{c[i] / m.size:.1%}" for i in orden})
        else:
            print("  mask: no está en el producto")
        print("  incidenceAngle:", L["rutas_incidencia"] or "no encontrado en el grupo de metadatos")


def arbol(h5, raiz="/", max_items=120):
    import h5py
    items = []

    def f(nombre, obj):
        if len(items) >= max_items:
            return True          # detiene el recorrido (no seguir bajando metadatos)
        if isinstance(obj, h5py.Dataset):
            items.append(f"  {nombre}  {obj.shape} {obj.dtype}")
        else:
            items.append(f"  {nombre}/")
    h5[raiz].visititems(f)
    print("\n".join(items) + ("\n  …" if len(items) >= max_items else ""))


def estructura(producto, madurez="PROVISIONAL", zona="tumbes", grupo=None):
    import h5py
    from .acceso import abrir_remoto
    from .busqueda import cmr_buscar
    lat, lon = ZONAS[zona]["punto"]
    cid = COLECCIONES[producto].get(madurez) or next(iter(COLECCIONES[producto].values()))
    print(f"\n== {producto} ({madurez}) sobre {zona}: buscando en CMR… ==", flush=True)
    gs = cmr_buscar(cid, lat, lon, generico=True)
    if not gs:
        print("  sin escenas")
        return
    g = gs[0]
    print(f"  {len(gs)} escenas; abro la más reciente: {g['nombre']}", flush=True)
    t0 = time.time()
    with h5py.File(abrir_remoto(g), "r") as h5:
        grupo = grupo or next((k for k in (f"/science/LSAR/{producto}/grids", f"/science/LSAR/{producto}") if k in h5), "/")
        print(f"  árbol de {grupo}:")
        arbol(h5, grupo)
    print(f"  ({time.time() - t0:.0f} s)")


def ejecutar(cache: Path):
    resumen_cache(cache)
    for prod in ("SME2", "GUNW"):
        try:
            estructura(prod)
        except Exception as e:
            print(f"  {prod}: falló ({type(e).__name__}: {e})")
