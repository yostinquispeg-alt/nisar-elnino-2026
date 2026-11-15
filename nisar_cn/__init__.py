"""nisar_cn — El Niño 2026 en la costa norte del Perú con NISAR (GCOV, banda L).

Módulos:
  config       zonas, eventos, noticias, colecciones, constantes temporales
  fisica       Dubois (HH) + Topp; sensibilidad a rugosidad y constante dieléctrica
  busqueda     CMR, nombres de producto, catálogo DEMO, pares antes/después
  acceso       streaming HTTPS con credenciales de Earthdata
  lectura      ventana de la zona en el HDF5; HDF5 sintéticos (DEMO)
  indicadores  agua, vegetación inundada, Δσ⁰, Δε', HH/HV
  exportar     CSV de storytelling y manifiesto para la web
  serie        todas las fechas por zona y órbita, capas por fecha y GIF
  pipeline     orquesta todo (lo usan 2_mapa/generar_mapa.py y el notebook)
"""
