"""Credenciales (.env) y acceso a los HDF5 de NISAR por streaming, sin descargar el archivo completo.

Fuente del método: ASF, NISAR Data User Guide, sección «Stream Data» [V] (fsspec HTTPS + aiohttp.BasicAuth,
block_size 16 MB, cache_type 'background'). Cada GCOV pesa ~6–7 GB (ficha CMR, R14 [V]).
Token Bearer en la cabecera Authorization: como en el código del equipo (R15).
[A] Se pasa el objeto de fsspec a h5py.File (el ejemplo oficial usa xarray/h5netcdf); no probado contra NASA.
"""
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# Nombres aceptados para la llave en el .env (se usa el primero que exista)
NOMBRES_TOKEN = ("EARTHDATA_TOKEN", "EDL_TOKEN", "EARTHDATA_BEARER_TOKEN", "NASA_EARTHDATA_TOKEN", "NASA_TOKEN", "BEARER_TOKEN", "TOKEN")
NOMBRES_USER = ("EARTHDATA_USER", "EARTHDATA_USERNAME", "EDL_USER", "EDL_USERNAME")
NOMBRES_PASS = ("EARTHDATA_PASS", "EARTHDATA_PASSWORD", "EDL_PASS", "EDL_PASSWORD")

_FS = None


def buscar_env(desde: Path = RAIZ, niveles: int = 3):
    """Busca un archivo .env en la carpeta del proyecto y hasta `niveles` carpetas hacia arriba."""
    p = Path(desde).resolve()
    for _ in range(niveles + 1):
        if (p / ".env").is_file():
            return p / ".env"
        p = p.parent
    # Respaldo: el .env de la carpeta anterior del proyecto (Descargas\NassaSpaceAppChallenge), si sigue ahí.
    viejo = Path(desde).resolve().parent / "NassaSpaceAppChallenge" / ".env"
    return viejo if viejo.is_file() else None


def cargar_env(ruta=None, sobrescribir=False):
    """Lee KEY=VALUE del .env y los pone en os.environ. Devuelve (ruta, nombres) y nunca los valores."""
    ruta = Path(ruta) if ruta else buscar_env()
    if ruta is None:
        return None, []
    nombres = []
    for linea in ruta.read_text(encoding="utf-8-sig").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        k, v = linea.split("=", 1)
        k = k.strip().removeprefix("export ").strip()
        v = v.strip().strip("'\"")
        if k and (sobrescribir or k not in os.environ):
            os.environ[k] = v
        nombres.append(k)
    return ruta, nombres


def _primero(nombres):
    for n in nombres:
        v = os.environ.get(n, "").strip()
        if v:
            return n, v
    return None, None


def credenciales():
    """Qué credencial se usará (solo nombres, nunca valores)."""
    nu, u = _primero(NOMBRES_USER)
    np_, p = _primero(NOMBRES_PASS)
    nt, t = _primero(NOMBRES_TOKEN)
    if u and p:
        return {"tipo": "usuario/clave", "variables": [nu, np_]}
    if t:
        return {"tipo": "token", "variables": [nt]}
    return {"tipo": None, "variables": []}


def sistema_https():
    global _FS
    if _FS is None:
        import aiohttp
        import fsspec
        cargar_env()
        _, u = _primero(NOMBRES_USER)
        _, p = _primero(NOMBRES_PASS)
        _, t = _primero(NOMBRES_TOKEN)
        if u and p:
            _FS = fsspec.filesystem("https", client_kwargs={"auth": aiohttp.BasicAuth(u, p)})
        elif t:
            t = t.removeprefix("Bearer ").strip()
            _FS = fsspec.filesystem("https", client_kwargs={"headers": {"Authorization": f"Bearer {t}"}})
        else:
            raise SystemExit("No encontré credenciales. Pon en el .env una línea EARTHDATA_TOKEN=... "
                             f"(o uno de {NOMBRES_TOKEN}), o EARTHDATA_USER y EARTHDATA_PASS.")
    return _FS


def abrir_remoto(g):
    """Objeto tipo archivo sobre el HDF5 remoto: solo se transfieren los bloques que se leen."""
    # blockcache guarda los bloques ya leídos (acceso aleatorio de HDF5); 4 MB × 64 bloques = hasta 256 MB en memoria.
    return sistema_https().open(g["url"], block_size=4 * 1024 * 1024, cache_type="blockcache",
                                cache_options={"maxblocks": 64})


def probar_acceso(url):
    """Lee los primeros 8 bytes de un HDF5 remoto. Un HDF5 válido empieza con la firma b'\\x89HDF\\r\\n\\x1a\\n'."""
    with sistema_https().open(url, block_size=1024 * 1024, cache_type="none") as f:
        cab = f.read(8)
    return cab == b"\x89HDF\r\n\x1a\n", cab


def descargar(g, cache: Path):
    """Descarga completa (opcional; 6–7 GB por GCOV)."""
    cache.mkdir(parents=True, exist_ok=True)
    p = cache / (g["nombre"] + ".h5")
    if not p.exists():
        sistema_https().get(g["url"], str(p))
    return p
