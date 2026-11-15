"""Tabla de storytelling (CSV) y manifiesto `window.NISAR_MANIFEST` compatible con app.js del equipo (R15)."""
import datetime as dt
import json
from pathlib import Path

import pandas as pd

from .config import CONTEXTO, CRONICA, EVENTOS, GAP_END, GAP_START, NOTICIAS, UTC, ZONAS, bbox


def storytelling(tabla: pd.DataFrame, modo: str) -> pd.DataFrame:
    ev = {e["id"]: e for e in EVENTOS}
    return tabla.assign(
        region=tabla["zona"].map(lambda z: ZONAS[z]["region"]),
        zona_nombre=tabla["zona"].map(lambda z: ZONAS[z]["nombre"]),
        titular=tabla["evento"].map(lambda e: ev[e]["titular"]),
        noticia=tabla["evento"].map(lambda e: NOTICIAS[ev[e]["fuente"]]),
        modo=modo,
    )[["modo", "evento", "region", "zona_nombre", "geom", "antes", "despues", "mezcla_madurez", "agua_ganada_km2",
       "dsigma_tierra_med_db", "deps_tierra_med", "titular", "noticia"]]


def _num(v):
    try:
        f = float(v)
        return None if f != f else round(f, 4)
    except (TypeError, ValueError):
        return v


def capas_mapa(tabla: pd.DataFrame, mapas: list, modo: str, salida: Path):
    """PNG por par (mapas.py) + metadatos para el visor. tabla y mapas vienen alineados de pipeline.ejecutar."""
    from .mapas import escribir_capas
    sub = f"mapas_{modo.lower()}"
    out = []
    for (_, f), m in zip(tabla.iterrows(), mapas):
        geo = escribir_capas(f, m, salida / sub, f"../salidas/{sub}")
        met = {k: _num(f[k]) for k in ("agua_antes_km2", "agua_despues_km2", "agua_ganada_km2", "agua_perdida_km2",
                                       "veg_inundada_despues_km2", "umbral_antes_db", "umbral_despues_db",
                                       "dsigma_tierra_med_db", "deps_tierra_med", "hvhh_antes_db", "hvhh_despues_db",
                                       "looks_med", "cobertura", "suelo_humedecido_km2", "suelo_secado_km2", "dhv_tierra_med_db", "veg_inundada_nueva_km2", "estructuras_km2") if k in f}
        out.append({"evento": f["evento"], "zona": f["zona"], "geom": f["geom"],
                    "antes": str(f["antes"]), "despues": str(f["despues"]),
                    "granulo_antes": f.get("granulo_antes"), "granulo_despues": f.get("granulo_despues"),
                    "theta": f.get("theta"), "metricas": met, **geo})
    return out


def escribir(story: pd.DataFrame, modo: str, salida: Path, capas=None, serie=None, lluvia=None, extra=None):
    salida.mkdir(parents=True, exist_ok=True)
    csv = salida / f"storytelling_{modo.lower()}.csv"
    story.to_csv(csv, index=False)
    manifest = {
        "source": "NISAR L2 GCOV (ASF DAAC), L-band, gamma0 → sigma0 vía rtcGammaToSigmaFactor",
        "modo": modo, "generated": dt.datetime.now(UTC).isoformat(),
        "gap": {"start": GAP_START.isoformat(), "end": GAP_END.isoformat()},
        "eventos": [{k: (v.isoformat() if isinstance(v, dt.datetime) else v) for k, v in e.items()} for e in EVENTOS],
        "zonas": {z: {"nombre": v["nombre"], "region": v["region"], "punto": list(v["punto"]),
                      "noticias": v["noticias"], "caja": bbox(z)} for z, v in ZONAS.items()},
        "noticias": NOTICIAS,
        "resultados": json.loads(story.to_json(orient="records", date_format="iso")),
        "capas": capas or [],
        "serie": serie or [],
        "cronica": [{**{k: v for k, v in c.items() if k != "fecha"}, "fecha": c["fecha"].isoformat(), "url": NOTICIAS.get(c["id"])}
                    for c in CRONICA],
        "contexto": [{**c, "url": NOTICIAS.get(c["id"])} for c in CONTEXTO],
        "lluvia": lluvia or {},
        "extra": extra or {},
    }
    js = salida / f"nisar_manifest_{modo.lower()}.js"
    js.write_text("// Generado por nisar_cn\nwindow.NISAR_MANIFEST = "
                  + json.dumps(manifest, indent=1, ensure_ascii=False) + ";\n", encoding="utf-8")
    return csv, js
