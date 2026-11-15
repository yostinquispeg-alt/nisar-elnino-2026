"""Serie temporal: todas las fechas NISAR disponibles por zona y órbita, comparadas con la primera fecha.

Para cada zona con evento y cada geometría (track_dir_frame) con al menos dos escenas fuera del corte de datos:
- la primera escena es la referencia (línea base);
- cada escena se compara con la referencia usando los mismos indicadores que los pares (indicadores.py);
- se escriben capas PNG por fecha para la barra de tiempo del mapa y un GIF animado por serie.

Comparar siempre con la misma escena de referencia y la misma geometría evita mezclar ángulos de vista distintos
[A: decisión de diseño]. Las escenas PROVISIONAL y VALIDATED se mezclan en la serie: cada fecha lleva su madurez
para que se vea en la línea de tiempo (R12).
"""
from pathlib import Path

import numpy as np

from .busqueda import en_gap
from .config import EVENTOS, ZONAS, bbox
from .indicadores import indicadores_par
from .mapas import COLOR_IMPACTO, _a_latlon, _clases, _gris, _impacto, _secuencial

ZONAS_CON_EVENTO = [z for z in ZONAS if any(z in e["zonas"] for e in EVENTOS)]


def _lectura(g, zona, modo, cache, i):
    from .lectura import demo_h5, leer_ventana
    from .pipeline import lectura_real
    if modo == "REAL":
        return lectura_real(g, zona, cache)
    return leer_ventana(demo_h5(g, bbox(zona), zona, cache, post=i > 0), bbox(zona))


def _series(cat, zonas):
    for z in zonas:
        por_geom = {}
        for g in cat.get(z, []):
            if not en_gap(g["t"]) and g.get("madurez") != "BETA":
                por_geom.setdefault(g["geom"], {})[g["nombre"]] = g
        for geom, d in por_geom.items():
            gs = sorted(d.values(), key=lambda g: g["t"])
            gs = [g for g in gs if g["POLE"] == gs[0]["POLE"]]
            if len(gs) >= 2:
                yield z, f"{geom[0]:03d}_{geom[1]}_{geom[2]:03d}", gs


def _capas_fecha(m, carpeta: Path, base: str, prefijo_web: str):
    import matplotlib.pyplot as plt
    rd = m["res"]["d"]
    nan = np.full(m["dsig"].shape, np.nan, "float32")
    hv = rd["s0hv_db"] if rd.get("s0hv_db") is not None else nan
    (sar, cls, imp, hvl), b = _a_latlon([rd["s0hh_db"], rd["cls"].astype("float32"),
                                         m["impacto"].astype("float32"), hv], m["x"], m["y"], m["epsg"])
    cls = np.where(np.isfinite(cls), cls, 255); imp = np.where(np.isfinite(imp), imp, 255)
    imgs = {"sar": _gris(sar), "clases": _clases(cls), "impacto": _impacto(imp), "hv": _secuencial(hvl, -30, -10, "YlGn")}
    rutas = {}
    for k, im in imgs.items():
        plt.imsave(carpeta / f"{base}_{k}.png", im)
        rutas[k] = f"{prefijo_web}/{base}_{k}.png"
    return rutas, b, sar, imp


def _gif(cuadros, ruta: Path, titulo: str):
    """cuadros: lista de (fecha, madurez, sar_latlon, impacto_latlon, texto_evento). Fondo σ⁰ HH + efectos en color."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    from PIL import Image
    nombres = {1: "agua permanente", 2: "inundación nueva", 3: "agua retirada", 4: "vegetación inundada nueva",
               5: "suelo más húmedo/rugoso", 6: "suelo más seco/liso", 7: "estructuras / ciudad"}
    imgs = []
    for fecha, mad, sar, imp, ev in cuadros:
        fig = plt.figure(figsize=(6.4, 7.2), dpi=90, facecolor="#0b1118")
        ax = fig.add_axes([0.03, 0.2, 0.94, 0.66])
        ax.imshow(np.nan_to_num(np.clip((sar + 25) / 25, 0, 1)), cmap="gray", vmin=0, vmax=1)
        ax.imshow(_impacto(imp))
        ax.axis("off")
        fig.text(0.03, 0.95, titulo, color="white", fontsize=12, weight="bold")
        fig.text(0.03, 0.905, f"{fecha:%d %b %Y}  ·  {mad}  ·  comparado con la 1.ª fecha", color="#8b9bab", fontsize=9.5)
        if ev:
            fig.text(0.03, 0.875, ev[:95], color="#ff6b6b", fontsize=8.5)
        fig.legend(handles=[Patch(color=np.array(COLOR_IMPACTO[k][:3]) / 255, label=v) for k, v in nombres.items()],
                   loc="lower center", ncol=2, fontsize=8, frameon=False, labelcolor="white")
        fig.canvas.draw()
        rgb = Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[..., :3].copy())
        imgs.append(rgb.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE))
        plt.close(fig)
    imgs[0].save(ruta, save_all=True, append_images=imgs[1:], duration=1100, loop=0)


def _calidad(m):
    """Control de calidad [A]: si casi toda la ventana sale como agua, lo más probable es un problema del dato
    (calibración, recorte fuera de la escena, valores casi nulos), no una inundación total."""
    cls = m["res"]["d"]["cls"]
    valido = cls != 255
    frac = float((cls[valido] == 1).mean()) if valido.any() else 1.0
    nota = None
    if frac > 0.6:
        nota = f"{frac:.0%} de la ventana sale como agua: probablemente un problema del dato, no una inundación"
    return {"frac_agua": round(frac, 3), "sospechosa": nota is not None, "nota": nota}


def _evento_vigente(t, zona):
    previos = [e for e in EVENTOS if e["inicio"] <= t and zona in e["zonas"]]
    if not previos:
        return None, ""
    e = previos[-1]
    return e["id"], f"Después de {e['id']}: {e['titular']}"


def serie_temporal(cat, modo, cache: Path, salida: Path, zonas=None, verbose=True):
    """Procesa todas las series. Devuelve la lista para el manifiesto del mapa."""
    sub = f"serie_{modo.lower()}"
    carpeta = salida / sub
    carpeta.mkdir(parents=True, exist_ok=True)
    out = []
    series = list(_series(cat, zonas or ZONAS_CON_EVENTO))
    if verbose:
        print(f"Series temporales: {len(series)} (zona × órbita), "
              f"{sum(len(s[2]) for s in series)} fechas en total", flush=True)
    for n, (z, geom, gs) in enumerate(series, 1):
        if verbose:
            print(f"[serie {n}/{len(series)}] {z} {geom}: {len(gs)} fechas "
                  f"({gs[0]['t']:%d %b} → {gs[-1]['t']:%d %b})", flush=True)
        try:
            Lb = _lectura(gs[0], z, modo, cache, 0)
        except Exception as e:
            print(f"   omitida ({type(e).__name__}: {e})", flush=True)
            continue
        frames, cuadros = [], []
        for i, g in enumerate(gs):
            try:
                L = Lb if i == 0 else _lectura(g, z, modo, cache, i)
                met, m = indicadores_par(Lb, L)
            except Exception as e:
                print(f"   {g['t']:%d %b} omitida ({type(e).__name__}: {e})", flush=True)
                continue
            base = f"{z}_{geom}_{g['t']:%Y%m%d}"
            rutas, b, sar, imp = _capas_fecha(m, carpeta, base, f"../salidas/{sub}")
            ev_id, ev_txt = _evento_vigente(g["t"], z)
            r = lambda v: None if v is None or v != v else round(float(v), 4)
            frames.append({
                "fecha": g["t"].isoformat(), "granulo": g["nombre"], "madurez": g["madurez"],
                "evento_previo": ev_id, "bounds": b, "capas": rutas,
                "metricas": {"agua_km2": r(met["agua_despues_km2"]), "veg_inundada_nueva_km2": r(met["veg_inundada_nueva_km2"]),
                             "estructuras_km2": r(met["estructuras_km2"]),
                             "agua_nueva_vs_base_km2": r(met["agua_ganada_km2"]),
                             "dsigma_tierra_med_db": r(met["dsigma_tierra_med_db"]), "deps_tierra_med": r(met["deps_tierra_med"]),
                             "suelo_humedecido_km2": r(met["suelo_humedecido_km2"]), "hvhh_db": r(met["hvhh_despues_db"])},
                "calidad": _calidad(m)})
            cuadros.append((g["t"], g["madurez"], sar, imp, ev_txt))
        if len(frames) < 2:
            continue
        gif = carpeta / f"{z}_{geom}.gif"
        _gif(cuadros, gif, f"{ZONAS[z]['nombre']} · órbita {geom}")
        out.append({"zona": z, "geom": geom, "base": frames[0]["fecha"], "frames": frames,
                    "gif": f"../salidas/{sub}/{gif.name}"})
        if verbose:
            print(f"   GIF: salidas/{sub}/{gif.name}", flush=True)
    return out
