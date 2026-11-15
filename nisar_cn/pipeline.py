"""Orquestación: catálogo → pares → lectura → indicadores → exportación."""
import sys
import time
from pathlib import Path

import h5py
import pandas as pd

from .busqueda import catalogo, pares
from .config import EVENTOS, ZONAS, bbox
from .indicadores import indicadores_par
from .lectura import cargar_lectura, demo_h5, guardar_lectura, leer_ventana


def construir_catalogo(modo, verbose=True):
    cat = {}
    for z in ZONAS:
        t0 = time.time()
        if verbose:
            print(f"Buscando escenas NISAR para {z}…", end=" ", flush=True)
        cat[z] = catalogo(z, modo)
        if verbose:
            print(f"{len(cat[z])} escenas ({time.time() - t0:.0f} s)", flush=True)
    return cat


def tabla_pares(cat):
    return pd.DataFrame([f for e in EVENTOS for f in pares(e, cat)])


def _log(msg):
    print(msg, flush=True)
    sys.stdout.flush()


_ABIERTOS = {}   # escena → h5py.File remoto, para no reabrirla en cada zona


def _h5_remoto(g):
    if g["nombre"] not in _ABIERTOS:
        from .acceso import abrir_remoto
        _ABIERTOS[g["nombre"]] = h5py.File(abrir_remoto(g), "r")
    return _ABIERTOS[g["nombre"]]


def cerrar_remotos():
    for h in _ABIERTOS.values():
        try:
            h.close()
        except Exception:
            pass
    _ABIERTOS.clear()


def lectura_real(g, zona, cache: Path):
    """Ventana de la zona en la escena g. Se guarda en cache/ (.npz, pocos MB): la segunda vez es instantánea."""
    cache.mkdir(parents=True, exist_ok=True)
    ruta = cache / f"{g['nombre']}_{zona}.npz"
    if ruta.exists():
        _log(f"      {g['nombre'][:60]}… {zona}: desde caché")
        return cargar_lectura(ruta)
    t0 = time.time()
    _log(f"      leyendo {g['nombre'][:60]}… ({zona})")
    L = leer_ventana(_h5_remoto(g), bbox(zona))
    guardar_lectura(L, ruta)
    _log(f"      listo en {time.time() - t0:.0f} s, ventana {L['capas']['HHHH'].shape}")
    return L


def analizar_par(fila, modo, cache: Path):
    a, d, z = fila["_a"], fila["_d"], fila["zona"]
    caja = bbox(z)
    if modo == "REAL":
        return indicadores_par(lectura_real(a, z, cache), lectura_real(d, z, cache))
    fa, fd = demo_h5(a, caja, z, cache, post=False), demo_h5(d, caja, z, cache, post=True)
    return indicadores_par(leer_ventana(fa, caja), leer_ventana(fd, caja))


def ejecutar(modo="DEMO", cache=Path("cache"), verbose=True):
    cat = construir_catalogo(modo, verbose)
    P = tabla_pares(cat)
    filas, mapas = [], []
    ok = P[P["estado"] == "ok"] if len(P) else P
    if verbose:
        _log(f"Pares a procesar: {len(ok)}")
    for n, (_, f) in enumerate(ok.iterrows(), 1):
        t0 = time.time()
        if verbose:
            _log(f"[{n}/{len(ok)}] {f['evento']} {f['zona']} órbita {f['geom']}")
        try:
            met, m = analizar_par(f, modo, Path(cache))
        except Exception as e:
            if verbose:
                _log(f"   omitido ({type(e).__name__}: {e})")
            continue
        if verbose:
            _log(f"   hecho en {time.time() - t0:.0f} s · inundación nueva {met['agua_ganada_km2']:.2f} km² · cobertura {met['cobertura']:.0%}")
        filas.append({**f.drop(["_a", "_d"]).to_dict(), **met,
                      "granulo_antes": f["_a"]["nombre"], "granulo_despues": f["_d"]["nombre"]})
        mapas.append(m)
    cerrar_remotos()
    return cat, P, pd.DataFrame(filas), mapas
