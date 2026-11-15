"""Indicadores por escena y por par antes/después.

- Agua: Otsu (R10 [?], implementación del equipo R15) con acotación [−22, −14] dB (R15 [?]);
  física de la reflexión especular: R7 [V].
- Vegetación inundada: rebote doble sensible a HH (R6, R7 [V]); umbrales −3.5 dB y 7 dB (R15 [?]).
- σ⁰ = γ⁰ · rtcGammaToSigmaFactor (R2 [V]).
- Δε' por detección de cambios con ks constante: deducción propia sobre R8 [A].
- Limpieza previa (limpieza.py): máscara `mask` 1–5 (R16 [V]) erosionada 2 px por el desalineamiento (R17 [V], [A]),
  filtro de Lee con ENL = numberOfLooks (Lee 1980 [?]; uso de filtro Lee en el río Tumbes: R18 [V]),
  θ por píxel desde el cubo incidenceAngle (R16 [V], interpolación [A]).
- Vegetación: σ⁰_HV como dispersión de volumen (R6 [V]); ΔHV como cambio de vegetación/estructura [A].
- Capa "impacto": combina agua, vegetación inundada y Δσ⁰ con UMBRALES_IMPACTO (config.py) [A][?].
"""
import warnings

import numpy as np
from scipy.ndimage import median_filter

from .config import THETA_RESPALDO_DEG, UMBRALES, UMBRALES_IMPACTO
from .fisica import delta_eps


def to_db(lin):
    with np.errstate(divide="ignore", invalid="ignore"):
        return 10 * np.log10(np.where(lin > 0, lin, np.nan))


def otsu(v, lo=-30, hi=5, bins=256):
    h, e = np.histogram(v[np.isfinite(v)], bins=bins, range=(lo, hi)); c = (e[:-1] + e[1:]) / 2
    w0 = np.cumsum(h); w1 = w0[-1] - w0
    m0 = np.cumsum(h * c) / np.maximum(w0, 1); m1 = (np.sum(h * c) - np.cumsum(h * c)) / np.maximum(w1, 1)
    return float(c[np.argmax(w0 * w1 * (m0 - m1) ** 2)])


def clasificar(hh_db, hv_db, umb=UMBRALES, filtrar=False):
    """0 tierra, 1 agua abierta, 2 vegetación inundada, 255 sin dato. hh_db ya viene limpio (máscara + Lee);
    filtrar=True aplica además la mediana 3×3 del código original del equipo (R15)."""
    hh = np.nan_to_num(hh_db, nan=-40)
    if filtrar:
        hh = median_filter(hh, size=3)
    thr = min(umb["agua_max"], max(umb["agua_min"], otsu(hh)))
    cls = np.zeros(hh.shape, np.uint8); cls[hh < thr] = 1
    if hv_db is not None:
        hv = np.nan_to_num(hv_db, nan=-40)
        if filtrar:
            hv = median_filter(hv, size=3)
        cls[(cls == 0) & (hh > umb["inund_hh"]) & ((hh - hv) > umb["inund_dif"])] = 2
    cls[~np.isfinite(hh_db)] = 255
    return cls, thr


def preparar_fecha(c):
    """Limpieza de una fecha (limpieza.py) y conversión a dB. Guarda las etapas para poder graficarlas."""
    from .limpieza import lee, mascara_valida
    valido, info = mascara_valida(c)
    looks = c.get("numberOfLooks")
    fac = c["rtcGammaToSigmaFactor"] if c.get("rtcGammaToSigmaFactor") is not None else 1.0
    hh = np.where(valido, c["HHHH"], np.nan)
    hv = np.where(valido, c["HVHV"], np.nan) if c.get("HVHV") is not None else None
    hh_f = lee(hh, looks)
    hv_f = lee(hv, looks) if hv is not None else None
    c["valido"], c["limpieza"] = valido, info
    c["hh_db_bruto"] = to_db(c["HHHH"])
    c["hh_db"], c["hv_db"] = to_db(hh_f), (to_db(hv_f) if hv_f is not None else None)
    c["s0hh_db"] = to_db(hh_f * fac)
    c["s0hv_db"] = to_db(hv_f * fac) if hv_f is not None else None
    c["cls"], c["thr"] = clasificar(c["hh_db"], c["hv_db"])
    return c


def theta_rad(lectura, capas=None):
    th = (capas or lectura["capas"]).get("theta_deg")
    if th is not None and np.isfinite(th).any():
        return np.radians(th), lectura.get("nota_theta") or "θ por píxel desde el cubo incidenceAngle (R16)"
    nota = f"θ = {THETA_RESPALDO_DEG:.0f}° (punto medio de 33–47°, R13): aproximación"
    if lectura["rutas_incidencia"]:
        # El producto trae el cubo incidenceAngle, pero falta interpolarlo a la grilla [?]. Mientras tanto se usa
        # el valor de respaldo para no dejar Δε′ vacío.
        nota += f"; el GCOV trae {lectura['rutas_incidencia'][0]}, falta interpolarlo"
    return np.radians(THETA_RESPALDO_DEG), nota


def recorte_comun(A, B):
    """Recorta dos lecturas a las coordenadas comunes (mismo track/frame ⇒ misma grilla)."""
    xa, xb = np.round(A["x"], 3), np.round(B["x"], 3); ya, yb = np.round(A["y"], 3), np.round(B["y"], 3)
    cx, cy = np.intersect1d(xa, xb), np.intersect1d(ya, yb)
    if len(cx) < 10 or len(cy) < 10:
        raise ValueError("Las grillas no coinciden: haría falta reproyectar")
    out = []
    for L in (A, B):
        m = np.isin(np.round(L["y"], 3), cy)[:, None] & np.isin(np.round(L["x"], 3), cx)[None, :]
        shp = (len(cy), len(cx))
        out.append({k: (v[m].reshape(shp) if v is not None else None) for k, v in L["capas"].items()})
    xs = A["x"][np.isin(np.round(A["x"], 3), cx)]; ys = A["y"][np.isin(np.round(A["y"], 3), cy)]
    return out, abs(A["dx"] * A["dy"]), xs, ys


def indicadores_par(A, B):
    """A, B: lecturas (leer_ventana) antes y después. Devuelve métricas y mapas."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)   # medianas de conjuntos vacíos → NaN (se ve en la tabla)
        return _indicadores_par(A, B)


def _indicadores_par(A, B):
    (ca, cb), area_px, xs, ys = recorte_comun(A, B)
    th, nota_th = theta_rad(A, ca)
    res = {"a": preparar_fecha(ca), "d": preparar_fecha(cb)}
    wa, wd = res["a"]["cls"] == 1, res["d"]["cls"] == 1
    valido = (res["a"]["cls"] != 255) & (res["d"]["cls"] != 255)
    tierra = valido & ~wa & ~wd & (res["a"]["cls"] != 2) & (res["d"]["cls"] != 2)
    dsig = res["d"]["s0hh_db"] - res["a"]["s0hh_db"]
    deps = delta_eps(dsig, th) if th is not None else np.full(dsig.shape, np.nan)
    km2 = area_px / 1e6
    dhv = (res["d"]["s0hv_db"] - res["a"]["s0hv_db"]) if res["a"]["s0hv_db"] is not None else np.full(dsig.shape, np.nan)
    impacto = impacto_par(res["a"]["cls"], res["d"]["cls"], dsig, tierra)

    def hvhh(c):
        return float(np.nanmedian((c["hv_db"] - c["hh_db"])[tierra])) if c["hv_db"] is not None else np.nan

    met = dict(
        agua_antes_km2=float(wa[valido].sum() * km2), agua_despues_km2=float(wd[valido].sum() * km2),
        agua_ganada_km2=float((wd & ~wa & valido).sum() * km2), agua_perdida_km2=float((wa & ~wd & valido).sum() * km2),
        veg_inundada_despues_km2=float((res["d"]["cls"] == 2).sum() * km2),
        umbral_antes_db=res["a"]["thr"], umbral_despues_db=res["d"]["thr"],
        dsigma_tierra_med_db=float(np.nanmedian(dsig[tierra])), deps_tierra_med=float(np.nanmedian(deps[tierra])),
        hvhh_antes_db=hvhh(res["a"]), hvhh_despues_db=hvhh(res["d"]),
        looks_med=float(np.nanmedian(res["a"]["numberOfLooks"])) if res["a"]["numberOfLooks"] is not None else np.nan,
        cobertura=float(valido.mean()), theta=nota_th,
        theta_med_deg=float(np.nanmedian(np.degrees(th))) if np.ndim(th) else float(np.degrees(th)),
        mask_valida_antes=res["a"]["limpieza"].get("frac_mask_valida"), mask_valida_despues=res["d"]["limpieza"].get("frac_mask_valida"),
        s0hh_tierra_antes_db=float(np.nanmedian(res["a"]["s0hh_db"][tierra])), s0hh_tierra_despues_db=float(np.nanmedian(res["d"]["s0hh_db"][tierra])),
        veg_inundada_nueva_km2=float((impacto == 4).sum() * km2), estructuras_km2=float((impacto == 7).sum() * km2),
        suelo_humedecido_km2=float((impacto == 5).sum() * km2), suelo_secado_km2=float((impacto == 6).sum() * km2),
        dhv_tierra_med_db=float(np.nanmedian(dhv[tierra])) if np.isfinite(dhv).any() else np.nan)
    return met, dict(res=res, dsig=dsig, deps=deps, dhv=dhv, tierra=tierra, impacto=impacto,
                     x=xs, y=ys, epsg=A["epsg"], theta=th)


IMPACTO_CLASES = {0: "sin cambio", 1: "agua permanente", 2: "inundación nueva", 3: "agua retirada",
                  4: "vegetación inundada nueva", 5: "suelo más húmedo/rugoso", 6: "suelo más seco/liso",
                  7: "estructuras / ciudad (rebote doble en ambas fechas)", 255: "sin dato"}


def impacto_par(cls_a, cls_d, dsig, tierra, u=UMBRALES_IMPACTO):
    """Una sola capa con todos los efectos (códigos en IMPACTO_CLASES). Orden de prioridad: agua > vegetación > suelo.
    Δσ⁰ se suaviza con mediana 5×5 antes de cortar en ±2 dB para no clasificar el moteado (speckle) píxel a píxel [A]."""
    dsig = median_filter(np.nan_to_num(dsig, nan=0.0), size=5)
    out = np.zeros(cls_a.shape, np.uint8)
    out[tierra & (dsig >= u["dsig_humedo_db"])] = 5
    out[tierra & (dsig <= u["dsig_seco_db"])] = 6
    # Limpieza: el rebote doble aparece tanto en vegetación inundada como en edificios. Si ya estaba en la fecha
    # de referencia es una estructura permanente (ciudad, galpones), no una inundación [A].
    out[(cls_d == 2) & (cls_a != 2)] = 4
    out[(cls_d == 2) & (cls_a == 2)] = 7
    out[(cls_a == 1) & (cls_d != 1)] = 3
    out[(cls_a != 1) & (cls_d == 1)] = 2
    out[(cls_a == 1) & (cls_d == 1)] = 1
    out[(cls_a == 255) | (cls_d == 255)] = 255
    return out
