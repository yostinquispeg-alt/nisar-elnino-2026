"""Genera el mapa: procesa las escenas NISAR y escribe las capas que lee MAPA_NISAR.html.

Desde la carpeta del proyecto:
    python 2_mapa/generar_mapa.py               # datos reales (llave del .env) y abre el mapa
    python 2_mapa/generar_mapa.py --probar      # solo prueba la llave leyendo 8 bytes de una escena real
    python 2_mapa/generar_mapa.py --modo DEMO   # datos sintéticos, para probar el código
    python 2_mapa/generar_mapa.py --diagnostico # revisa la capa mask y la estructura de SME2 y GUNW
    python 2_mapa/generar_mapa.py --sin-extra   # sin SME2 ni GUNW (más rápido)
    python 2_mapa/generar_mapa.py --sin-serie   # solo pares antes/después (sin la serie temporal ni los GIF)
"""
import argparse
import sys
import webbrowser
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent      # carpeta del proyecto
sys.path.insert(0, str(RAIZ))
MAPA = Path(__file__).resolve().parent / "MAPA_NISAR.html"

from nisar_cn import acceso
from nisar_cn.exportar import capas_mapa, escribir, storytelling
from nisar_cn.pipeline import ejecutar
from nisar_cn.serie import ZONAS_CON_EVENTO, serie_temporal
from nisar_cn.lluvia import lluvia_todas
from nisar_cn.extra import productos_extra



def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--modo", choices=["DEMO", "REAL"], default="REAL")
    ap.add_argument("--probar", action="store_true", help="probar la llave de Earthdata y salir")
    ap.add_argument("--diagnostico", action="store_true", help="revisa mask y la estructura de SME2/GUNW, y sale")
    ap.add_argument("--sin-extra", action="store_true", help="no procesar SME2 (humedad) ni GUNW (coherencia)")
    ap.add_argument("--sin-serie", action="store_true", help="no procesar la serie temporal (todas las fechas)")
    args = ap.parse_args()

    ruta_env, nombres = acceso.cargar_env()
    print(".env:", ruta_env or "no encontrado", "| variables:", nombres, "| credencial:", acceso.credenciales()["tipo"])
    if args.diagnostico:
        from nisar_cn import diagnostico
        diagnostico.ejecutar(RAIZ / "cache")
        return
    if args.probar:
        url = ("https://nisar.asf.earthdatacloud.nasa.gov/NISAR/NISAR_L2_GCOV_V1/"
               "NISAR_L2_PR_GCOV_034_003_A_176_4005_DHDH_A_20261024T110112_20261024T110149_P05036_N_F_J_001/"
               "NISAR_L2_PR_GCOV_034_003_A_176_4005_DHDH_A_20261024T110112_20261024T110149_P05036_N_F_J_001.h5")
        ok, cab = acceso.probar_acceso(url)
        print("Acceso a NASA:", "OK — HDF5 válido" if ok else f"respuesta inesperada {cab!r}")
        return

    cat, pares, tabla, mapas = ejecutar(args.modo, RAIZ / "cache")
    print("\nEscenas por zona:", {z: len(v) for z, v in cat.items()})
    print("\nPares antes/después:")
    print(pares.drop(columns=["_a", "_d"]).to_string(index=False))
    if args.modo == "DEMO":
        print("\n⚠ MODO DEMO: archivos SINTÉTICOS. Las cifras no son resultados.")
    if len(tabla):
        cols = ["evento", "zona", "geom", "agua_ganada_km2", "dsigma_tierra_med_db", "deps_tierra_med", "cobertura"]
        print(tabla[cols].round(3).to_string(index=False))
        capas = capas_mapa(tabla, mapas, args.modo, RAIZ / "salidas")
        serie = []
        if not args.sin_serie:
            print("\nSerie temporal (todas las fechas disponibles; la 1.ª vez tarda, luego usa la caché):")
            serie = serie_temporal(cat, args.modo, RAIZ / "cache", RAIZ / "salidas")
        print("\nLluvia diaria por zona (Open-Meteo, reanálisis) para contrastar:")
        lluvia = lluvia_todas(RAIZ / "cache")
        extra = {}
        if not args.sin_extra and args.modo == "REAL":
            print("\nProductos NISAR adicionales: SME2 (humedad del suelo) y GUNW (coherencia):")
            extra = productos_extra(sorted({s["zona"] for s in serie}) or ZONAS_CON_EVENTO, RAIZ / "cache", RAIZ / "salidas")
        csv, js = escribir(storytelling(tabla, args.modo), args.modo, RAIZ / "salidas", capas, serie, lluvia, extra)
        print(f"\nEscrito: {csv.name}, {js.name}, {len(capas)} pares y {len(serie)} series con GIF en salidas/")
        print("Mapa:", MAPA)
        webbrowser.open(MAPA.as_uri())


if __name__ == "__main__":
    main()
