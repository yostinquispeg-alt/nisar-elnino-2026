"""Configuración: colecciones NISAR, restricciones temporales, zonas, eventos y noticias.

Cada constante lleva su fuente (ver docs/REFERENCIAS.md):
[V] verificado en fuente abierta · [A] deducción/elección propia · [?] hueco, falta referencia.
"""
import datetime as dt

UTC = dt.timezone.utc
LIMA = dt.timezone(dt.timedelta(hours=-5))

# --- Colecciones NISAR en el CMR (R14 [V]); madurez y precaución al mezclarlas (R3 [V])
COLECCIONES = {
    "GCOV": {"PROVISIONAL": "C2854338529-ASF", "VALIDATED": "C3622241360-ASF", "BETA": "C3622214170-ASF"},
    "GSLC": {"PROVISIONAL": "C2854332392-ASF", "VALIDATED": "C3622244601-ASF"},
    "GUNW": {"PROVISIONAL": "C2854335566-ASF", "VALIDATED": "C3622247503-ASF"},
    "SME2": {"PROVISIONAL": "C2854344945-ASF"},   # R3: SME2 aún sin VALIDATED
}
CMR_GRANULES = "https://cmr.earthdata.nasa.gov/search/granules.json"

# --- Restricciones temporales
GAP_START = dt.datetime(2026, 7, 27, 22, 3, 25, tzinfo=UTC)    # R11 [V]
GAP_END = dt.datetime(2026, 8, 10, 0, 55, 27, tzinfo=UTC)      # R11 [V]
PAUSA_PR = dt.datetime(2026, 10, 23, 23, 53, tzinfo=UTC)       # R12 [V]

# --- Zonas: punto (lat, lon) elegido por mí para la consulta [A]; daño documentado en N1–N6 [V]
R_DEG = 0.06   # semiancho de la caja (grados); parámetro de análisis [A]

ZONAS = {
    "tumbes":     dict(nombre="Tumbes – ciudad",                 punto=(-3.57, -80.45), region="Tumbes", noticias=["N1", "N4"]),
    "zarumilla":  dict(nombre="Zarumilla – Aguas Verdes",        punto=(-3.48, -80.25), region="Tumbes", noticias=["N3", "N4", "N5"]),
    "pizarro":    dict(nombre="Puerto Pizarro",                  punto=(-3.50, -80.39), region="Tumbes", noticias=["N1"]),
    "piura":      dict(nombre="Piura – Castilla",                punto=(-5.19, -80.63), region="Piura",  noticias=["N2", "N6"]),
    "chulucanas": dict(nombre="Chulucanas",                      punto=(-5.09, -80.16), region="Piura",  noticias=["N2"]),
    "salitral":   dict(nombre="Salitral – Morropón (q. Serrán)", punto=(-5.34, -79.83), region="Piura",  noticias=["N6"]),
    "sullana":    dict(nombre="Sullana",                         punto=(-4.90, -80.69), region="Piura",  noticias=["N2", "N5"]),
    "ayabaca":    dict(nombre="Ayabaca (sierra)",                punto=(-4.64, -79.71), region="Piura",  noticias=["N2", "N5"]),
}


def bbox(zona, r=R_DEG):
    lat, lon = ZONAS[zona]["punto"]
    return dict(s=lat - r, n=lat + r, w=lon - r, e=lon + r)


# --- Eventos: fechas de las noticias [V]; acotación horaria de la ventana [A]
EVENTOS = [
    dict(id="E1", inicio=dt.datetime(2026, 10, 19, 18, 0, tzinfo=LIMA), fin=dt.datetime(2026, 10, 20, 23, 59, tzinfo=LIMA),
         zonas=["piura", "chulucanas", "sullana"], fuente="N2",
         titular="Lluvias inundan Piura; ~30 cm de agua en el mercado de Chulucanas"),
    dict(id="E2", inicio=dt.datetime(2026, 10, 23, 0, 0, tzinfo=LIMA), fin=dt.datetime(2026, 10, 23, 23, 59, tzinfo=LIMA),
         zonas=["tumbes", "zarumilla", "pizarro"], fuente="N1",
         titular="Más de 8 h de lluvia en Tumbes; Puerto Pizarro inundado (52 mm)"),
    dict(id="E3", inicio=dt.datetime(2026, 10, 27, 0, 0, tzinfo=LIMA), fin=dt.datetime(2026, 10, 27, 23, 59, tzinfo=LIMA),
         zonas=["zarumilla"], fuente="N5", titular="El Salto (Zarumilla): 102 mm en un día"),
    dict(id="E4", inicio=dt.datetime(2026, 11, 1, 18, 0, tzinfo=LIMA), fin=dt.datetime(2026, 11, 2, 23, 59, tzinfo=LIMA),
         zonas=["zarumilla", "tumbes"], fuente="N3",
         titular="Desborde del Zarumilla en Puerto Perú; río Tumbes 1 021,33 m³/s (El Tigre)"),
    dict(id="E5", inicio=dt.datetime(2026, 11, 2, 0, 0, tzinfo=LIMA), fin=dt.datetime(2026, 11, 2, 23, 59, tzinfo=LIMA),
         zonas=["salitral", "piura"], fuente="N6", titular="Quebrada Serrán activada en Salitral; drenaje en Piura"),
    dict(id="E6", inicio=dt.datetime(2026, 10, 28, 20, 15, tzinfo=LIMA), fin=dt.datetime(2026, 10, 29, 23, 59, tzinfo=LIMA),
         zonas=["chulucanas"], fuente="N11", titular="Alerta roja y aniegos severos en Chulucanas"),
]

NOTICIAS = {
    "N1": "https://www.americatv.com.pe/noticias/amp/actualidad/tumbes-lluvia-mas-ocho-horas-provoca-inundaciones-n523751",
    "N2": "https://caretas.pe/?p=840084",
    "N3": "https://caretas.pe/?p=842604",
    "N4": "https://elbuho.pe/?p=441556",
    "N5": "https://andina.pe/agencia/noticia-el-nino-tumbes-endures-extraordinary-rainfall-of-up-to-110-liters-per-square-meter-1098315.aspx",
    "N6": "https://elperuano.pe/noticia/308191-fuerzas-armadas-activan-puente-terrestre-para-evitar-que-morropon-quede-aislada-por-el-nino",
    "N7": "https://www.telesurtv.net/costa-peru-nino-precipitaciones-el-nino/",
    "N8": "https://www.primicias.ec/internacional/peru-lluvias-fenomeno-elnino-frontera-ecuador-piura-tumbes-135919/",
    "N9": "https://www.expreso.com.pe/actualidad/tumbes-bate-record-de-lluvias-con-70-mm-en-una-sola-noche-distrito-de-pampas-hospital-noticia/1325307/",
    "N10": "https://andina.pe/agencia/noticia-zarumilla-recorded-993-liters-of-rainfall-per-square-meter-over-the-last-24-hours-1097513.aspx",
    "N11": "https://www.americatv.com.pe/noticias/amp/actualidad/lluvias-extremas-chulucanas-provocan-severas-inundaciones-n523927",
    "N12": "https://elbuho.pe/?p=441642",
    "N13": "https://www.americatv.com.pe/noticias/amp/actualidad/piura-fuertes-lluvias-inundan-calles-mancora-y-chulucanas-n524080",
    "N14": "https://www.primicias.ec/internacional/peru-emergencia-fenomeno-nino-municipios-lluvias-inundaciones-136308/",
    "N15": "https://elbuho.pe/?p=441960",
    "N16": "https://elperuano.pe/noticia/308553-tumbes-cuenta-con-tres-albergues-temporales-para-familias-damnificadas-por-las-lluvias",
    "N17": "https://panamericana.pe/nacionales/476700-enfen-pronostica-nino-costero-continuaria-fines-otono-2027/amp",
}

# --- Crónica: noticias y reportes oficiales fechados, por zona, para cruzar con lo que mide NISAR.
#     Cada página se ABRIÓ COMPLETA el 14 nov 2026 (WebFetch o navegador) [V]; resúmenes con palabras propias.
#     fecha = momento del hecho (hora de Lima) cuando la nota lo da; fecha_aprox=True si solo hay fecha de publicación.
#     tipo: "noticia" (medio), "medicion" (dato medido citado: lluvia, caudal), "oficial" (Senamhi, COEN, Indeci, ENFEN, Gobierno).
def _d(a, m, d_, h=12, mi=0):
    return dt.datetime(a, m, d_, h, mi, tzinfo=LIMA)


CRONICA = [
    dict(id="N2", fecha=_d(2026, 10, 19, 21), zonas=["chulucanas", "piura", "sullana"], tipo="noticia", medio="Caretas (20 oct)",
         texto="Las lluvias empiezan la noche del lunes 19 de octubre. En Chulucanas el agua llega a unos 30 cm en el mercado modelo "
               "y entra a viviendas de Monte Verde, Villa Mercedes, Consuelo de Velasco y José Carlos Mariátegui; también llueve en Castilla, Sullana y Tambogrande."),
    dict(id="N7", fecha=_d(2026, 10, 20, 6), zonas=["chulucanas"], tipo="noticia", medio="teleSUR (20 oct, 21:41)",
         texto="El martes 20 de octubre, tras más de dos horas de lluvia desde la madrugada, se inundan calles de Chulucanas; "
               "el mercado modelo colapsa con unos 30 cm de agua. La nota no da cifras de lluvia."),
    dict(id="N9", fecha=_d(2026, 10, 22, 5), zonas=["tumbes", "zarumilla"], tipo="medicion", medio="Expreso (23 oct, 09:09)", fecha_aprox=True,
         texto="Lluvias desde la noche del miércoles: el aeropuerto de Tumbes acumula 70 mm en una noche, según el especialista Abraham Levy "
               "(no Senamhi). En la ciudad llueve desde las 5:00 y se anegan el entorno del mercado, el barrio San José y Pampa Grande; "
               "se activan quebradas en Pampas de Hospital. Senamhi emite el aviso N.° 430 (Tumbes, Zarumilla, Contralmirante Villar) hasta el 25 oct. "
               "El 5 400 % de exceso en octubre es cálculo de Levy y la propia nota dice que falta corroborarlo."),
    dict(id="N1", fecha=_d(2026, 10, 23, 6), zonas=["pizarro", "tumbes", "zarumilla"], tipo="medicion", medio="América TV (23 oct)", fecha_aprox=True,
         texto="Más de ocho horas de lluvia desde la madrugada. Senamhi reporta 52 mm acumulados en Puerto Pizarro, donde se inundan "
               "varios barrios y entra agua a las casas; también hay aniegos en la ciudad de Tumbes (barrio San José) y en Zarumilla."),
    dict(id="N10", fecha=_d(2026, 10, 27, 6), zonas=["zarumilla"], tipo="medicion", medio="Andina (27 oct, 13:16)",
         texto="Senamhi: Zarumilla acumula 99,3 mm desde la medianoche del lunes 26 hasta las 6:00 del martes 27 "
               "(la nota lo llama «últimas 24 horas», aunque la ventana es de unas 30 h)."),
    dict(id="N8", fecha=_d(2026, 10, 28, 15, 48), zonas=["zarumilla", "pizarro", "tumbes", "piura"], tipo="oficial", medio="EFE/Primicias (28 oct)", fecha_aprox=True,
         texto="Senamhi: la lluvia del 1 al 26 de octubre fue 70 a 80 veces la normal en la costa norte. Estaciones: El Salto 102 mm en 24 h "
               "(máximo del mes, supera su pico previo de 99,3 mm), Puerto Pizarro 45,2 mm, Campamento Sede 25,1 mm, Puente Tumbes 12,9 mm; "
               "en Piura, Hualcuy 34,7 mm y Paimas 24,5 mm. La nota no da el periodo de cada lectura salvo El Salto."),
    dict(id="N11", fecha=_d(2026, 10, 28, 20, 15), zonas=["chulucanas"], tipo="noticia", medio="América TV (28 oct)",
         texto="Desde las 20:15 la lluvia forma aniegos más altos que las veredas en la urbanización Ignacio Merino de Chulucanas y "
               "se suspende en parte el transporte; el radar de Senamhi marca 3,2 mm en la primera hora. Senamhi emite el aviso N.° 445, nivel rojo, "
               "del 30 oct al 1 nov. (La nota dice «martes 28», pero el 28 de octubre de 2026 es miércoles [?].)"),
    dict(id="N12", fecha=_d(2026, 11, 2, 2), zonas=["zarumilla"], tipo="noticia", medio="El Búho (2 nov)",
         texto="Tras las lluvias de la noche del domingo 1 y la madrugada del lunes 2, el asentamiento Puerto Perú (Aguas Verdes) queda "
               "con las calles totalmente inundadas; los vecinos describen el agua hasta las rodillas. La nota no da cifras oficiales."),
    dict(id="N3", fecha=_d(2026, 11, 2, 3), zonas=["zarumilla"], tipo="oficial", medio="Caretas (3 nov)",
         texto="En la madrugada del lunes 2 se desborda el río Zarumilla en Puerto Perú, Villa Perú y la ampliación Tomás Arizola: "
               "más de 300 familias afectadas y pérdida de cultivos de banano. Fuentes: aviso hidrológico Senamhi N.° 1667 y alerta COEN N.° 304-2026."),
    dict(id="N4", fecha=_d(2026, 11, 2, 5), zonas=["tumbes", "zarumilla"], tipo="oficial", medio="El Búho (2 nov)",
         texto="COEN: el río Tumbes llega a 1 021,33 m³/s a las 5:00 en la estación El Tigre, sobre el umbral rojo; en Zarumilla se desborda "
               "la quebrada Marco Felipe y aísla el sector Primero de Agosto. La alerta roja la emite el Comando FEN."),
    dict(id="N5", fecha=_d(2026, 11, 2, 6), zonas=["zarumilla", "tumbes"], tipo="medicion", medio="Andina (2 nov, 17:11)", fecha_aprox=True,
         texto="Senamhi: El Salto (Zarumilla) registra 110,3 mm en la madrugada (lo normal de noviembre son unos 9 mm) y ya había marcado 102 mm "
               "el 27 de octubre; el río Tumbes supera los 1 000 m³/s y luego baja a alerta amarilla. Zarumilla es la zona más afectada."),
    dict(id="N6", fecha=_d(2026, 11, 2, 12), zonas=["salitral", "piura"], tipo="oficial", medio="El Peruano (2 nov, 19:42)",
         texto="Se activa la quebrada Serrán en Salitral (Morropón); el Ejército instala un «puente terrestre» con un camión para cruzar el río. "
               "En Piura ciudad drenan agua de lluvia en Las Azucenas y la avenida Sánchez Cerro. Sin cifras."),
    dict(id="N13", fecha=_d(2026, 11, 3, 12), zonas=["chulucanas"], tipo="noticia", medio="América TV (3 nov)", fecha_aprox=True,
         texto="La lluvia inunda en minutos las calles de Chulucanas junto al cementerio y afecta a los comerciantes. La nota no da la fecha exacta ni cifras."),
    dict(id="N14", fecha=_d(2026, 11, 3, 15), zonas=["tumbes", "zarumilla", "pizarro", "piura"], tipo="oficial", medio="AFP/Primicias (3 nov)",
         texto="Un decreto publicado el 3 de noviembre declara 60 días de emergencia por peligro inminente en 1 380 distritos (más del 70 %). "
               "Tumbes y Piura son las más afectadas; el COEN reporta en Tumbes 324 damnificados y 110 viviendas inhabitables. Sin cifras para Piura."),
    dict(id="N15", fecha=_d(2026, 11, 4, 19), zonas=["tumbes", "zarumilla"], tipo="medicion", medio="El Búho (5 nov)",
         texto="Tormenta la noche del miércoles 4 de noviembre: la estación Cabo Inga registra 74,4 mm en tres horas (16:00–19:00). "
               "Las provincias de Tumbes y Zarumilla son las más afectadas (Zarumilla, Aguas Verdes, Matapalo); Casitas queda incomunicado."),
    dict(id="N16", fecha=_d(2026, 11, 8, 8, 51), zonas=["zarumilla", "tumbes"], tipo="oficial", medio="El Peruano (8 nov)",
         texto="Tres albergues: Villa Primavera (Aguas Verdes) con 48 familias de Puerto Perú que perdieron su casa por el desborde del Zarumilla; "
               "I.E. El Gran Chilimasa (Nuevo Aguas Verdes); y el complejo Alberto Terranova en Tumbes, para 168 familias."),
]

CONTEXTO = [
    dict(id="N17", medio="Panamericana (probablemente sáb. 31 oct; la página no da la fecha completa)", tipo="oficial",
         texto="El Comunicado Oficial ENFEN N.° 19-2026 ratifica la «alerta de El Niño Costero»: magnitud extraordinaria en la región Niño 1+2 "
               "hasta febrero de 2027 y luego un declive gradual hacia junio de 2027."),
]

# --- Umbrales de clasificación heredados del código del equipo (R15) — [?] sin referencia bibliográfica
UMBRALES = dict(agua_min=-22.0, agua_max=-14.0, inund_hh=-3.5, inund_dif=7.0)

# --- Umbrales de la capa "impacto" del mapa: parámetros de análisis elegidos por nosotros [A], sin referencia [?].
#     Δσ⁰_HH ≥ +2 dB sobre tierra estable → "suelo más húmedo o más rugoso"; ≤ −2 dB → "suelo más seco o más liso".
UMBRALES_IMPACTO = dict(dsig_humedo_db=2.0, dsig_seco_db=-2.0)

# --- Ángulo de incidencia de respaldo: punto medio de 33–47° (R13 [V]); usarlo es una aproximación [A]
THETA_RESPALDO_DEG = 40.0
