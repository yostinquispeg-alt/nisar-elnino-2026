"""Limpieza de los datos NISAR GCOV antes de calcular indicadores.

Cada paso lleva su fuente y su estatus ([V] verificado abriendo la fuente, [A] decisión o deducción nuestra,
[?] falta referencia):

1. Máscara de validez (`mask`): 0 = inválido o parcialmente enfocado, 1–5 = válido (número de sub-swath),
   255 = relleno fuera de la imagen. JPL D-102274 Rev D, sec. 4.3.3 (p. 20) y tabla 5-3 (p. 29) [V] (R16).
   La guía advierte que esa máscara está desalineada con los datos y deja artefactos en los bordes de los
   productos L2 (R17, «Product Known Issues», 27 feb 2026) [V]. Por eso se erosiona 2 píxeles [A].
2. HHHH/HVHV sin dato: `_FillValue = nan`, `valid_min = 0` (R16, tabla 5-3) [V]. Se descartan ≤ 0 y no finitos.
3. Moteado (speckle): filtro de Lee adaptativo con el número de looks REAL de cada píxel (`numberOfLooks`, R2)
   como ENL [A]. Fórmula clásica de Lee (1980) [?] (artículo original no abierto). El estudio del río Tumbes de
   Breña Aliaga et al. (2026) usa un filtro Lee-Sigma sobre Sentinel-1 antes de umbralizar (R18) [V].
4. Ángulo de incidencia: cubo 3-D `/science/LSAR/GCOV/metadata/radarGrid/incidenceAngle` con ejes
   (alto, y, x) y coordenadas `heightAboveEllipsoid`, `yCoordinates`, `xCoordinates` (R16, sec. 3.2.4 y tabla 5-1)
   [V]. Se toma la capa de altura más cercana a 0 m y se interpola bilinealmente a la grilla de la zona [A].
5. Agua permanente: píxeles que son agua en ≥ 80 % de las fechas ANTES del primer evento de la zona [A]; la idea
   de separar agua permanente con la serie temporal está en R18 [V], el 80 % es nuestro [?].
6. Control de calidad por fecha: > 60 % de la ventana clasificada como agua ⇒ fecha dudosa [A].
7. Salto de madurez PROVISIONAL → VALIDATED: R3 advierte que las diferencias pueden venir del procesamiento [V];
   se mide la mediana de σ⁰ HH en tierra estable por fecha para ver si hay un escalón al cambiar de madurez [A].
"""
import numpy as np
from scipy.ndimage import binary_erosion, uniform_filter

EROSION_PX = 2           # [A] por el desalineamiento de la máscara (R17)
LEE_VENTANA = 5          # [A]
FRAC_PERMANENTE = 0.8    # [A][?]


def mascara_valida(capas):
    """True donde el píxel es utilizable según `mask` (1–5) y HHHH > 0 finito."""
    hh = capas["HHHH"]
    ok = np.isfinite(hh) & (hh > 0)
    m = capas.get("mask")
    info = {"usa_mask": m is not None}
    if m is not None:
        mv = (m >= 1) & (m <= 5)
        info["frac_mask_valida"] = float(mv.mean())
        info["frac_mask_0"] = float((m == 0).mean())
        info["frac_mask_255"] = float((m == 255).mean())
        ok &= mv
    if EROSION_PX and ok.any():
        ok = binary_erosion(ok, iterations=EROSION_PX)
    info["frac_valida_final"] = float(ok.mean())
    return ok, info


def lee(intensidad, looks=None, ventana=LEE_VENTANA):
    """Filtro de Lee en potencia lineal. ENL = numberOfLooks por píxel (si no hay, 1)."""
    z = np.where(np.isfinite(intensidad), intensidad, 0.0).astype("float64")
    w = np.isfinite(intensidad).astype("float64")
    n = np.maximum(uniform_filter(w, ventana), 1e-6)
    mu = uniform_filter(z, ventana) / n
    var = np.maximum(uniform_filter(z * z, ventana) / n - mu ** 2, 0)
    enl = np.where(np.isfinite(looks) & (looks > 0), looks, 1.0) if looks is not None else 1.0
    cv2 = 1.0 / enl                                   # varianza relativa del speckle
    varx = np.maximum((var - mu ** 2 * cv2) / (1 + cv2), 0)
    W = np.where(var > 0, varx / np.maximum(var, 1e-12), 0)
    out = mu + W * (z - mu)
    return np.where(np.isfinite(intensidad), out, np.nan).astype("float32")


def theta_desde_cubo(h5, ruta_inc, x, y):
    """Ángulo de incidencia (grados) en la grilla (y, x) de la ventana, desde el cubo radarGrid (R16)."""
    from scipy.interpolate import RegularGridInterpolator
    grp = ruta_inc.rsplit("/", 1)[0]
    cubo = h5[ruta_inc]
    cx, cy = h5[f"{grp}/xCoordinates"][()], h5[f"{grp}/yCoordinates"][()]
    alt = h5[f"{grp}/heightAboveEllipsoid"][()] if f"{grp}/heightAboveEllipsoid" in h5 else np.array([0.0])
    k = int(np.argmin(np.abs(alt))) if cubo.ndim == 3 else None
    capa = cubo[k] if cubo.ndim == 3 else cubo[()]
    capa = np.asarray(capa, dtype="float64")
    if capa.shape != (len(cy), len(cx)):
        raise ValueError(f"forma del cubo {capa.shape} ≠ (len y, len x) = {(len(cy), len(cx))}")
    if x.min() < cx.min() - 1 or x.max() > cx.max() + 1 or y.min() < cy.min() - 1 or y.max() > cy.max() + 1:
        raise ValueError("la ventana cae fuera de las coordenadas del cubo")
    ys, ix = (cy, slice(None)) if cy[0] < cy[-1] else (cy[::-1], slice(None, None, -1))
    capa = capa[ix, :]
    xs, jx = (cx, slice(None)) if cx[0] < cx[-1] else (cx[::-1], slice(None, None, -1))
    capa = capa[:, jx]
    f = RegularGridInterpolator((ys, xs), capa, bounds_error=False, fill_value=np.nan)
    Y, X = np.meshgrid(y, x, indexing="ij")
    return f((Y, X)).astype("float32"), float(alt[k]) if k is not None else 0.0


def agua_permanente(lista_cls, fechas, inicio_evento):
    """Frecuencia de agua en las fechas anteriores al primer evento. Devuelve (máscara, n_fechas usadas)."""
    pre = [c for c, t in zip(lista_cls, fechas) if t < inicio_evento]
    if len(pre) < 2:
        return None, len(pre)
    st = np.stack([(c == 1).astype("float32") for c in pre])
    val = np.stack([(c != 255) for c in pre]).sum(0)
    frac = np.where(val > 0, st.sum(0) / np.maximum(val, 1), np.nan)
    return frac >= FRAC_PERMANENTE, len(pre)
