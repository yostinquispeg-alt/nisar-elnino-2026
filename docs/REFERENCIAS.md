# Referencias del proyecto

Convención: **[V]** verificado en fuente abierta (14 nov 2026) · **[A]** deducción propia a partir de una fuente citada · **[?]** hueco, falta referencia.


| ID | Referencia | Qué respalda | Estatus |
|---|---|---|---|
| R1 | NASA Space Apps Challenge 2026, reto *Dancing with the SARs*, pestaña *Details*, sección *Background*. https://www.spaceappschallenge.org/2026/challenges/dancing-with-the-sars/?tab=details | El radar es más sensible a la rugosidad y a la constante dieléctrica; el agua tiene constante dieléctrica alta | [V] |
| R2 | ASF DAAC, *NISAR Data User Guide*, página «Geocoded Polarimetric Covariance (GCOV)». https://nisar-docs.asf.alaska.edu/gcov/ (cita a Shiroma, G. H. X. (2026), *Level-2 Geocoded Polarimetric Covariance*, JPL D-102274 Rev. F) | Rutas HDF5 (`HHHH`, `HVHV`, `numberOfLooks`, `mask`, `rtcGammaToSigmaFactor`), γ⁰ con RTC, píxel de 10/20 m según ancho de banda, convención de nombres (`MODE`, `POLE`, `CRID`) | [V] |
| R3 | ASF DAAC, *NISAR Data User Guide*, «Data Products Overview». https://nisar-docs.asf.alaska.edu/products-overview/ | Madurez BETA/PROVISIONAL/VALIDATED, precaución al mezclarlas, VALIDATED desde 21 oct 2026, SME2 a 200 m con 3 algoritmos (DSG, PMI, TSR) | [V] |
| R4 | ASF DAAC, *NISAR Data User Guide*, «GUNW». https://nisar-docs.asf.alaska.edu/gunw/ | GUNW: solo co-pol (HH o VV), pares de 12 días, coherencia a 20 y 80 m | [V] |
| R5 | ASF DAAC, *NISAR Data User Guide*, «About NISAR», tabla 1. https://nisar-docs.asf.alaska.edu/nisar-intro/ | Frecuencia central de la banda A según el modo (40+5 MHz → 1239 MHz; 20+5 MHz → 1229 MHz) | [V] |
| R6 | NASA Earthdata, «Synthetic Aperture Radar (SAR)». https://www.earthdata.nasa.gov/learn/earth-observation-data-basics/sar | Mecanismos: superficie rugosa (sensible a VV), volumen (sensible a HV/VH), rebote doble por troncos o vegetación inundada (sensible a HH); la banda L (~23 cm) penetra el dosel | [V] |
| R7 | Meyer, F. J. (2023). *GEOS 657 Microwave Remote Sensing*, Lecture 17 «Surface Water Mapping from SAR», University of Alaska Fairbanks, diapositivas 5, 6, 7 y 10. https://radar.community.uaf.edu/wp-content/uploads/sites/667/2023/04/2023-Lectures17-SurfaceWaterMapping-handouts.pdf | El agua en calma da reflexión especular y retrodispersión baja; la tierra es más rugosa; rebote doble bajo vegetación inundada; σ⁰ sube con la humedad del suelo en terreno abierto | [V] |
| R8 | Dubois, P., van Zyl, J., Engman, T. (1995). «Measuring soil moisture with imaging radars». *IEEE Trans. Geosci. Remote Sens.* 33(4), 915–926. doi:10.1109/36.406677 | Modelo semiempírico σ⁰_HH(ε, ks, θ, λ) y límites de validez. **El artículo original no se abrió**: la ecuación se tomó de la implementación SENSE (`sense.surface.dubois95`, que cita a Ulaby 2014, cap. 10.6, ec. 10.41) y los límites de arXiv:2412.11874 | [V] (fuente secundaria) |
| R9 | Topp, G. C., Davis, J. L., Annan, A. P. (1980). «Electromagnetic determination of soil water content: measurements in coaxial transmission lines». *Water Resour. Res.* 16, 574–582 | ε = 3.03 + 9.3 m_v + 146.0 m_v² − 76.7 m_v³. **Original no abierto**: tomada de arXiv:1006.4307 | [V] (fuente secundaria) |
| R10 | Otsu, N. (1979). «A Threshold Selection Method from Gray-Level Histograms». *IEEE Trans. Syst. Man Cybern.* 9(1), 62–66. doi:10.1109/TSMC.1979.4310076 | Umbral de Otsu (el que usa el código del equipo). Metadatos vistos en resultados de búsqueda; **artículo no abierto** | [?] |
| R11 | NASA Earthdata, alerta «Permanent NISAR Instrument Data Gap» (28 ago 2026). https://www.earthdata.nasa.gov/data/alerts-outages/permanent-nisar-instrument-data-gap | Corte de datos de 2026-07-27 22:03:25 a 2026-08-10 00:55:27 UTC | [V] |
| R12 | NASA Earthdata, alerta «NISAR provisional data product production paused». https://www.earthdata.nasa.gov/data/alerts-outages/nisar-provisional-data-product-production-paused | Producción PROVISIONAL detenida el 2026-10-23 23:53 UTC; reanudación con atrasado después del 6 nov 2026 | [V] |
| R13 | WMO OSCAR, instrumento «SAR-L (NISAR)». https://space.oscar.wmo.int/instruments/view/sar_l_nisar | Ángulo de incidencia 33–47°, banda 1.215–1.3 GHz, modos de polarización | [V] |
| R14 | NASA CMR (Common Metadata Repository), consultas del 14 nov 2026. https://cmr.earthdata.nasa.gov/search/ | IDs de colección y escenas concretas (fechas, track, frame, enlaces HDF5) | [V] |
| R15 | Código del equipo `nsac-project-main` (`pipeline/fetch_nisar.py`, `README.md`) | Estructura del pipeline, sesión de Earthdata, lectura de la ventana, umbrales de clasificación | [V] (como código) |

**Noticias (todas abiertas el 14 nov 2026)**

| ID | Medio y fecha | Contenido usado |
|---|---|---|
| N1 | América TV, 23 oct 2026. https://www.americatv.com.pe/noticias/amp/actualidad/tumbes-lluvia-mas-ocho-horas-provoca-inundaciones-n523751 | Más de 8 h de lluvia en Tumbes; Zarumilla, Puerto Pizarro y Tumbes ciudad afectados; 52 mm en Puerto Pizarro según Senamhi |
| N2 | Caretas, 20 oct 2026. https://caretas.pe/?p=840084 | Lluvias desde la noche del 19 oct; ~30 cm de agua en el mercado de Chulucanas; también Tambogrande, Castilla, Sullana y Paita; alerta por quebradas en Ayabaca y Huancabamba |
| N3 | Caretas, 3 nov 2026. https://caretas.pe/?p=842604 | Desborde del río Zarumilla la madrugada del 2 nov en Puerto Perú (Aguas Verdes): más de 300 familias; El Tigre 1 021,33 m³/s; El Salto 104,1 mm/24 h |
| N4 | El Búho, 2 nov 2026. https://elbuho.pe/?p=441556 | Río Tumbes 1 021,33 m³/s (El Tigre, 05:00); desborde de la quebrada Marco Felipe (Zarumilla); Corrales y San Juan de la Virgen inundados; 70 % de la lluvia anual en menos de 30 días (aeropuerto) |
| N5 | Andina, 2 nov 2026. https://andina.pe/agencia/noticia-el-nino-tumbes-endures-extraordinary-rainfall-of-up-to-110-liters-per-square-meter-1098315.aspx | Zarumilla, la provincia más afectada; El Salto 110,3 mm el 2 nov y 102 mm el 27 oct; aviso rojo para Zarumilla, Sullana y parte de Ayabaca |
| N6 | El Peruano, 2 nov 2026. https://elperuano.pe/noticia/308191-fuerzas-armadas-activan-puente-terrestre-para-evitar-que-morropon-quede-aislada-por-el-nino | Quebrada Serrán activada en Salitral (Morropón); drenaje en Las Azucenas y en la av. Sánchez Cerro (Piura) |

> **Nota:** N3 da 104,1 mm/24 h para El Salto y N5 da 110,3 mm. Son dos cifras distintas para la misma estación y no las concilio aquí.

## 9. Pendientes y huecos (para cerrar antes de la presentación)

1. **[?] Referencia de los umbrales en dB** (−22, −14, −3.5 y 7 dB) del código del equipo (R15).
2. **[?] Valores de la capa `mask`** del GCOV: especificación JPL D-102274 Rev. F, sección 4.3 (Shiroma, 2026).
3. **[?] Interpolar el cubo `incidenceAngle`** a la grilla de la zona. Su existencia está verificada en la guía, página «Metadata». Mientras tanto se usan 40°.
4. **[?] Ruta de la coherencia (GUNW)**: ejecutar la sección 7 en modo REAL y fijarla. La de humedad (`/science/LSAR/SME2/grids/soilMoisture`) ya está verificada.
5. **[?] Coordenadas de los sectores** que nombran las noticias, desde una fuente cartográfica.
6. **[?] Efecto del viento sobre la superficie del agua**: falta referencia.
7. **[?] Otsu (R10)**: abrir el artículo original para pasar a [V].
8. **R8 y R9 en fuente secundaria**: conviene abrir Dubois et al. (1995) y Topp et al. (1980) originales.
9. **Escenas posteriores al 2 nov** en Tumbes: la producción PROVISIONAL estuvo pausada hasta el 6 nov (R12). Hay que volver a correr la sección 3 en modo REAL.
10. **Mezcla de madurez** PROVISIONAL → VALIDATED en todos los pares de octubre (R3). Antes de atribuir el Δσ⁰ al terreno, comparar zonas estables (roca, desierto sin lluvia). Esa comparación es una propuesta mía **[A]** sin referencia.
