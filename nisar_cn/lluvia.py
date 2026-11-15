"""Lluvia diaria por zona para contrastar con NISAR: Open-Meteo Historical Weather API.

Documentación abierta completa el 14 nov 2026 (https://open-meteo.com/en/docs/historical-weather-api) [V]:
- endpoint /v1/archive (host archive-api.open-meteo.com), parámetros latitude, longitude, start_date, end_date,
  daily=precipitation_sum (mm); con variables diarias el parámetro timezone es obligatorio;
- se basa en reanálisis (estaciones, aviones, boyas, radar y satélite combinados con modelos): ERA5 (0,25°),
  ERA5-Land (0,1°) y, desde 2017, ECMWF IFS a 9 km; ERA5 llega con 5 días de retraso, IFS sin retraso;
- uso solo no comercial y menos de 10 000 llamadas diarias.
Es un reanálisis, no un pluviómetro: sirve para ver CUÁNDO llovió fuerte, no el valor exacto en un punto [A].
Los valores medidos por Senamhi en estaciones están en la crónica (config.CRONICA).
"""
import datetime as dt
import json
from pathlib import Path

from .config import ZONAS

URL = "https://archive-api.open-meteo.com/v1/archive"


def lluvia_zona(zona, inicio="2026-08-01", fin=None, cache: Path = None):
    import requests
    fin = fin or (dt.date.today() - dt.timedelta(days=2)).isoformat()
    ruta = cache / f"lluvia_{zona}_{inicio}_{fin}.json" if cache else None
    if ruta and ruta.exists():
        return json.loads(ruta.read_text())
    lat, lon = ZONAS[zona]["punto"]
    r = requests.get(URL, params={"latitude": lat, "longitude": lon, "start_date": inicio, "end_date": fin,
                                  "daily": "precipitation_sum", "timezone": "America/Lima"}, timeout=(10, 40))
    r.raise_for_status()
    d = r.json()["daily"]
    out = {"fechas": d["time"], "mm": d["precipitation_sum"], "fuente": "Open-Meteo Historical Weather API (reanálisis ECMWF)"}
    if ruta:
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(json.dumps(out))
    return out


def lluvia_todas(cache: Path, verbose=True):
    res = {}
    for z in ZONAS:
        try:
            res[z] = lluvia_zona(z, cache=cache)
            if verbose:
                tot = sum(v or 0 for v in res[z]["mm"])
                print(f"   lluvia {z}: {len(res[z]['fechas'])} días, {tot:.0f} mm acumulados (Open-Meteo)", flush=True)
        except Exception as e:
            if verbose:
                print(f"   lluvia {z}: no disponible ({type(e).__name__})", flush=True)
    return res
