# El Niño 2026 en la costa norte del Perú: zonas más afectadas en NISAR y en los medios

14 nov 2026 · Yostin Leonardo · Hackatón NASA Space Apps 2026, reto Dancing with the SARs

Leyenda de estatus: **[V]** verificado en una fuente abierta en esta sesión · **[A]** aproximación o razonamiento físico mío, sin fuente abierta aquí · **[?]** por verificar.

**Corrección de estatus (14 nov, 17:30):** usé [V] para afirmaciones que solo vi en el fragmento del buscador, sin abrir la página. En esta sesión abrí de verdad solo estas páginas: el catálogo CMR de NASA (escenas, IDs y enlaces HDF5), la página de recursos del reto, Andina del 2 nov (Tumbes) y El Peruano del 2 nov (Morropón). Todo lo demás marcado [V] (las otras noticias, ENFEN, Cenepred, las páginas de ASF y Earthdata, el archivo de El Comercio) debe leerse como **[V-fragmento]**: dato leído en el resumen del buscador, pendiente de abrir la página.

## Resumen

Las dos zonas donde El Niño 2026 se ve a la vez en los medios y en NISAR son **Tumbes** (Zarumilla–Aguas Verdes, Puerto Pizarro, valle del río Tumbes) y **Piura** (Chulucanas–Alto Piura, Piura–Castilla, Sullana–Chira, sierra de Ayabaca y Morropón). Para los dos eventos de octubre hay escenas NISAR de antes y de después en la misma órbita: el de Piura del 19–20 y el de Tumbes del 23 y 27. [V]

- **Por qué estas zonas:** el decreto de emergencia de noviembre señala a Tumbes y Piura como las más afectadas en los primeros días del mes. Cenepred pone a Piura como la segunda región con más población expuesta a inundación (1,36 millones). [V]
- **Qué se puede medir con NISAR:** agua de inundación en zonas urbanas y agrícolas, quebradas activadas, cambios del cauce, humedad del suelo, manglar inundado y deslizamientos en la sierra. Las variables, la firma y el producto de cada una están en la matriz.
- **Datos:** colecciones NISAR L2 GCOV, GSLC y GUNW y L3 SME2, versiones PROVISIONAL (desde junio de 2026) y Validated (desde el 22–24 de octubre). En Tumbes y Piura casi todas las escenas son de doble polarización (HH + HV). [V]
- **Hueco principal:** todavía no hay escena posterior al evento del 1–2 de noviembre en Tumbes (río Tumbes por encima de 1 000 m³/s). Al 14 de noviembre, la última escena publicada es del 31 de octubre. [V]
- **Secundarias:** Lambayeque y La Libertad tienen escenas hasta el 5 de noviembre, pero la prensa de octubre y noviembre las describe en preparación más que con daños. Por eso quedan como zonas de control. [V]

## Marco temporal

El registro NISAR calibrado de la costa norte empieza el 21 de junio de 2026. Cubre la fase de lluvias de octubre y noviembre, pero no las inundaciones de febrero–marzo de 2026. [V]

| Fecha | Hito | Estado NISAR para la costa norte |
| --- | --- | --- |
| 13 feb 2026 | ENFEN activa la alerta de El Niño Costero ([El Búho](https://elbuho.pe/2026/02/enfen-activa-estado-de-alerta-de-el-nino-costero-y-preve-lluvias-intensas-a-partir-de-marzo/)) | Sin productos publicados para Tumbes y Piura (ni BETA) |
| 25 feb 2026 | Piura: más de 12 000 damnificados según el COER ([El Búho](https://elbuho.pe/2026/02/mas-de-12-mil-damnificados-y-mas-de-1-300-afectados-dejan-las-lluvias-en-piura/)) | Sin productos. El atrasado sep 2025–jun 2026 se publicará antes de fin de 2026 ([Earthdata Forum](https://forum.earthdata.nasa.gov/viewtopic.php?p=26145)) |
| 9 mar 2026 | Tumbes: más de 6 000 ha de cultivos afectadas por desborde de los ríos Tumbes y Zarumilla ([El Comercio](https://elcomercio.pe/peru/tumbes/)) | Sin productos |
| 17 jun 2026 | Inicio de los productos PROVISIONAL calibrados ([ASF](https://hyp3-docs.asf.alaska.edu/nisar-docs/availability-overview/)) | Primeras escenas en Tumbes y Piura: 21 jun 2026 |
| set–nov 2026 | Según ENFEN, probabilidad máxima de magnitud extraordinaria en Niño 1+2 ([El Comercio](https://elcomercio.pe/peru/fenomeno-el-nino-enfen-mantiene-alerta-y-preve-magnitud-extraordinaria-hasta-enero-de-2027-ultimas-noticia/)) | Serie cada 12 días por órbita, dos órbitas por zona |
| 19–20 oct 2026 | Primeras inundaciones en Piura y Chulucanas | Antes: 19 oct · después: 31 oct |
| 23 oct 2026 | Tumbes: más de 8 h de lluvia, inundaciones en Zarumilla, Puerto Pizarro y Tumbes | Antes: 12 y 19 oct · después: 24 y 31 oct |
| 22–24 oct 2026 | Los productos pasan a la colección Validated (CRID P05036) | Para unir la serie, cambio de versión de procesamiento |
| 1–2 nov 2026 | Tumbes: río Tumbes por encima de 1 000 m³/s, Puerto Perú inundado | Antes: 31 oct · después: **aún no publicado** |
| 3 nov 2026 | Decreto Supremo 149-2026-PCM: emergencia en 1 380 distritos ([Caretas](https://caretas.pe/?p=842501)) | — |
| nov–dic 2026 | Máxima intensidad esperada en Niño 3.4 ([El Comercio](https://elcomercio.pe/peru/fenomeno-el-nino-enfen-mantiene-alerta-y-preve-magnitud-extraordinaria-hasta-enero-de-2027-ultimas-noticia/)) | Próximas escenas por publicar |

Las fuentes de los eventos de octubre y noviembre están en la cronología.

## Productos NISAR

Cuatro productos bastan para todos los efectos de la matriz. Todos están en el CMR de NASA con descarga directa en HDF5 (necesita cuenta de Earthdata Login). Los IDs de colección los leí del catálogo CMR en esta sesión. [V]

| Producto | ID de colección CMR (PROVISIONAL · Validated) | Qué contiene | Para qué lo usamos |
| --- | --- | --- | --- |
| [L2 GCOV](https://nisar-docs.asf.alaska.edu/gcov/) | C2854338529-ASF · C3622241360-ASF | Retrodispersión γ⁰ calibrada y con corrección de terreno; términos de covarianza HHHH, HVHV, HHHV… según el modo | Agua de inundación, humedad, vegetación, cicatrices de cauce |
| L2 GSLC | C2854332392-ASF · C3622244601-ASF | Imagen compleja (amplitud + fase) geocodificada | Coherencia interferométrica entre pares: detecta cambios y daños |
| L2 GUNW | C2854335566-ASF · C3622247503-ASF | Interferograma desenrollado entre dos fechas | Deformación y deslizamientos en la sierra (Ayabaca, Morropón) |
| [L3 SME2](https://nisar-docs.asf.alaska.edu/level3) | C2854344945-ASF | Humedad del suelo de varios modelos, malla EASE 2.0 de 200 m | Saturación del suelo antes y después de las lluvias |
| L2 GOFF | C2854341702-ASF · C3622250865-ASF | Desplazamientos de píxel entre fechas | Opcional: movimientos grandes de ladera |

**Cómo leer el nombre de un archivo** (ejemplo real de Tumbes): `NISAR_L2_PR_GCOV_034_003_A_176_4005_DHDH_A_20261024T110112_…_P05036_N_F_J_001.h5`

- `034` ciclo · `003` órbita (track) · `A` ascendente o `D` descendente · `176` frame. [V: posiciones comprobadas en todos los nombres leídos]
- `DHDH` = doble polarización (HH + HV) · `SHSH` = solo HH. [A: deducido de los términos de covarianza que lista la guía GCOV]
- `4005` / `2005`: código de ancho de banda. La guía da 20 m de píxel GCOV para 20 MHz y 10 m para 40 MHz; que `4005` corresponda a 40 MHz y 10 m es una inferencia mía. [? confirmar en el archivo]
- `P05023` = PROVISIONAL · `P05036` = Validated (versión de procesamiento, CRID).

**Regla para comparar fechas:** mismo track, misma dirección, mismo frame y mismo modo de polarización. Si se mezclan geometrías, el cambio de ángulo de incidencia se confunde con un cambio en el terreno. [A]

## Matriz de efectos del Niño

De las doce variables, nueve salen directamente de NISAR, dos son potenciales sin noticia de 2026 y la lluvia no se mide con radar. La columna "Firma esperada" es física estándar de banda L que no verifiqué en una fuente de esta sesión: va toda como [A] y hay que contrastarla con la guía [Intro to SAR](https://www.earthdata.nasa.gov/learn/earth-observation-data-basics/sar) antes de presentarla.

| # | Efecto del Niño | Firma esperada en banda L [A] | Producto | Indicador a calcular | Evidencia en medios 2026 |
| --- | --- | --- | --- | --- | --- |
| 1 | Desborde de ríos (Tumbes, Zarumilla, Piura) | Agua lisa en la llanura: HH y HV muy bajos (reflexión especular) | GCOV HHHH, HVHV | Área inundada (km²) = píxeles de agua nuevos × área de píxel; ancho del cauce en transectos | Zarumilla 242 m³/s y Puerto Perú inundado; río Tumbes > 1 000 m³/s (1–2 nov) [V] |
| 2 | Inundación urbana por lluvia (aniegos, cuencas ciegas) | Agua junto a muros: más rebote doble (sube HH); calles anegadas oscuras | GCOV HH + coherencia GSLC | Δγ⁰ (dB) en manzanas; caída de coherencia | Piura y Chulucanas (20 oct); Tumbes, Zarumilla, Puerto Pizarro (23 oct) [V] |
| 3 | Activación de quebradas (cauces secos que llevan agua y lodo) | Cambio fuerte en un cauce angosto: suelo húmedo o con sedimento nuevo, pérdida de coherencia | Coherencia GSLC + Δγ⁰ HH | Longitud del cauce con coherencia < umbral | Quebrada Marco Felipe en Zarumilla; quebrada Serrán en Salitral, Morropón (1–2 nov) [V] |
| 4 | Saturación del suelo (constante dieléctrica) | γ⁰ sube al subir εr; contraste máximo en suelo desértico seco | SME2 + Δγ⁰ HH | Humedad volumétrica (SME2); ΔdB en suelo desnudo | Aeropuerto de Tumbes: 70 % de la lluvia de un año normal en menos de 30 días [V] |
| 5 | Manglar inundado (Puerto Pizarro) | Agua bajo el dosel: el rebote doble tronco–agua sube HH y el cociente HH/HV | GCOV HH/HV | Cociente HH/HV en el manglar, antes y después | Puerto Pizarro entre los sectores afectados el 23 oct [V] |
| 6 | Cultivos inundados (valles de Tumbes, Chira, Alto Piura) | Parcelas con lámina de agua oscuras; arroz con rebote doble | GCOV HH, HV | Hectáreas agrícolas con agua | 6 000 ha afectadas en Tumbes en marzo, sin escena NISAR para esa fecha [V] |
| 7 | Deslizamientos y huaicos en la sierra | Pérdida de coherencia en laderas; desplazamientos de fase | GUNW, coherencia GSLC, GOFF | Polígonos con coherencia baja; desplazamiento en la línea de vista (LOS) | Senamhi con aviso rojo en Ayabaca y Huancabamba (nov) [V] |
| 8 | Cambio y colmatación del cauce | El borde agua/tierra se mueve entre fechas | Máscaras de agua GCOV | Desplazamiento de la orilla (m) | El cauce del río Piura está "colmatado" según Indeci [V] |
| 9 | Rugosidad (viento y lluvia sobre el agua, depósitos nuevos) | El agua agitada se ve brillante en HH y produce falsos negativos; en HV el agua sigue oscura | GCOV HV como control | Máscara de agua basada en HV y HH juntos | — (variable metodológica) |
| 10 | Laguna efímera en el desierto de Sechura | Agua nueva en desierto: contraste extremo | GCOV | Área de agua en la depresión | Ninguna noticia de 2026 encontrada [?] |
| 11 | Reverdecimiento del desierto semanas después | HV sube con la biomasa nueva | GCOV HV | ΔHV (dB) en algarrobal y matorral | Ninguna noticia de 2026 encontrada [?] |
| 12 | Intensidad de lluvia | El radar no la mide | — | Usar GPM IMERG (Earthdata) o estaciones de Senamhi [?] | El Salto (Zarumilla): 110,3 mm el 2 nov y 102 mm el 27 oct, frente a ~9 mm normales en noviembre [V] |

## Zonas de estudio

Nueve zonas tienen a la vez noticia de daño en 2026 y escenas NISAR. Lambayeque y La Libertad quedan como control. Los recuentos son escenas GCOV leídas del CMR el 14 nov 2026; las coordenadas son puntos aproximados que elegí para la consulta [A].

| Zona | Punto consultado (lat, lon) [A] | Tracks NISAR | Escenas GCOV PROV · Valid. | Efectos (# matriz) | Noticias 2026 |
| --- | --- | --- | --- | --- | --- |
| Tumbes – ciudad y valle | −3,57, −80,45 | 003 A f176 · 112 D f090 | 19 (21 jun–19 oct) · 2 (24 y 31 oct) | 1, 2, 4, 6, 8 | [América TV 23 oct](https://www.americatv.com.pe/noticias/amp/actualidad/tumbes-lluvia-mas-ocho-horas-provoca-inundaciones-n523751) · [Andina 2 nov](https://andina.pe/agencia/noticia-el-nino-tumbes-endures-extraordinary-rainfall-of-up-to-110-liters-per-square-meter-1098315.aspx) · [El Búho 5 nov](https://elbuho.pe/?p=441960) · [El Peruano 8 nov](https://elperuano.pe/noticia/308553-tumbes-cuenta-con-tres-albergues-temporales-para-familias-damnificadas-por-las-lluvias) |
| Zarumilla – Aguas Verdes (Puerto Perú) | −3,48, −80,25 | 003 A f176 · 112 D f090 | 19 · 2 | 1, 2, 3 | [Caretas 2 nov](https://caretas.pe/?p=842604) · [Teleamazonas 2 nov](https://www.teleamazonas.com/actualidad/noticias/internacional/emergencia-tumbes-lluvias-dejan-agua-puerto-peru-frontera-ecuador-131967/) · [El Búho 2 nov](https://elbuho.pe/?p=441556) |
| Puerto Pizarro (manglar) | −3,50, −80,39 | 003 A f176 · 112 D f090 | 19 · 2 | 5, 9 | [América TV 23 oct](https://www.americatv.com.pe/noticias/amp/actualidad/tumbes-lluvia-mas-ocho-horas-provoca-inundaciones-n523751) |
| Piura – Castilla (ciudad) | −5,19, −80,63 | 104 A f175 · 112 D f091 | 19 · 2 (31 oct) | 2, 8 | [Panamericana 20 oct](https://panamericana.pe/EstaNoche/nacionales/476125-fenomeno-nino-golpea-piura-intensas-lluvias-inundan-calles-viviendas) · [El Comercio (EC) 20 oct](https://www.elcomercio.com/actualidad/mundo/la-costa-norte-de-peru-esta-bajo-el-agua/) · [El Peruano 2 nov](https://elperuano.pe/noticia/308191-fuerzas-armadas-activan-puente-terrestre-para-evitar-que-morropon-quede-aislada-por-el-nino) |
| Chulucanas (Alto Piura) | −5,09, −80,16 | 003 A f175 · 112 D f091 | 18 · 2 (24 y 31 oct) | 2, 4, 6 | [Caretas 20 oct](https://caretas.pe/?p=840084) |
| Salitral – Morropón (quebrada Serrán) | −5,34, −79,83 | 003 A f175 · 112 D f091 | 18 · 2 | 3, 7 | [El Peruano 2 nov](https://elperuano.pe/noticia/308191-fuerzas-armadas-activan-puente-terrestre-para-evitar-que-morropon-quede-aislada-por-el-nino) |
| Sullana – valle del Chira | −4,90, −80,69 | 104 A f175 · 112 D f091 | 19 · 2 | 1, 6 | Aviso rojo de Senamhi para Sullana ([Andina 2 nov](https://andina.pe/agencia/noticia-el-nino-tumbes-endures-extraordinary-rainfall-of-up-to-110-liters-per-square-meter-1098315.aspx)) |
| Ayabaca (sierra) | −4,64, −79,71 | 003 A f175 · 112 D f091 | 18 · 2 | 7 | Aviso rojo de Senamhi ([Andina 2 nov](https://andina.pe/agencia/noticia-el-nino-tumbes-endures-extraordinary-rainfall-of-up-to-110-liters-per-square-meter-1098315.aspx)) |
| Sechura (desierto) | −5,95, −80,55 | 104 A f174/f175 · 112 D f091 | 29 · 2 | 4, 10, 11 | Ninguna de daño encontrada [?] |
| *Control:* Chiclayo (Lambayeque) | −6,77, −79,84 | 003 A, 104 A, 011 D, 112 D | 38 · 5 (hasta 5 nov) | — | Obras de prevención en el río La Leche ([Andina](https://andina.pe/agencia/noticia-fenomeno-nino-ana-culmina-trabajos-descolmatacion-rio-leche-1098996.aspx)) |
| *Control:* Trujillo (La Libertad) | −8,11, −79,03 | 003 A f173/f174 · 011 D f093 | 22 · 3 (hasta 5 nov) | — | Ninguna de daño encontrada para oct–nov |

### Escenas clave antes y después (enlaces directos HDF5)

Mismo track y modo en cada par. El paso de PROVISIONAL (P05023) a Validated (P05036) cambia la versión de procesamiento entre el antes y el después. Esto se discute en Limitaciones.

| Zona y par | Antes | Después |
| --- | --- | --- |
| Tumbes–Zarumilla, ascendente 003 A f176, evento 23 oct | [12 oct 2026, PROV](https://nisar.asf.earthdatacloud.nasa.gov/NISAR/NISAR_L2_GCOV_PROVISIONAL_V1/NISAR_L2_PR_GCOV_033_003_A_176_4005_DHDH_A_20261012T110112_20261012T110148_P05023_N_F_J_001/NISAR_L2_PR_GCOV_033_003_A_176_4005_DHDH_A_20261012T110112_20261012T110148_P05023_N_F_J_001.h5) | [24 oct 2026, Validated](https://nisar.asf.earthdatacloud.nasa.gov/NISAR/NISAR_L2_GCOV_V1/NISAR_L2_PR_GCOV_034_003_A_176_4005_DHDH_A_20261024T110112_20261024T110149_P05036_N_F_J_001/NISAR_L2_PR_GCOV_034_003_A_176_4005_DHDH_A_20261024T110112_20261024T110149_P05036_N_F_J_001.h5) (06:01 hora Lima, la mañana siguiente a la lluvia) |
| Tumbes–Zarumilla, descendente 112 D f090, eventos 23 y 27 oct | [19 oct 2026, PROV](https://nisar.asf.earthdatacloud.nasa.gov/NISAR/NISAR_L2_GCOV_PROVISIONAL_V1/NISAR_L2_PR_GCOV_033_112_D_090_4005_DHDH_A_20261019T233944_20261019T234018_P05023_N_F_J_001/NISAR_L2_PR_GCOV_033_112_D_090_4005_DHDH_A_20261019T233944_20261019T234018_P05023_N_F_J_001.h5) | [31 oct 2026, Validated](https://nisar.asf.earthdatacloud.nasa.gov/NISAR/NISAR_L2_GCOV_V1/NISAR_L2_PR_GCOV_034_112_D_090_4005_DHDH_A_20261031T233944_20261031T234018_P05036_N_F_J_001/NISAR_L2_PR_GCOV_034_112_D_090_4005_DHDH_A_20261031T233944_20261031T234018_P05036_N_F_J_001.h5) |
| Tumbes, línea base seca (ascendente) | [13 ago 2026, PROV](https://nisar.asf.earthdatacloud.nasa.gov/NISAR/NISAR_L2_GCOV_PROVISIONAL_V1/NISAR_L2_PR_GCOV_028_003_A_176_4005_DHDH_A_20260813T110112_20260813T110148_P05023_N_F_J_001/NISAR_L2_PR_GCOV_028_003_A_176_4005_DHDH_A_20260813T110112_20260813T110148_P05023_N_F_J_001.h5) | — |
| Piura–Castilla, ascendente 104 A f175, evento 20 oct | 19 oct 2026, PROV (`033_104_A_175_2005_DHDH`; buscar en la consulta CMR de abajo) | [31 oct 2026, Validated](https://nisar.asf.earthdatacloud.nasa.gov/NISAR/NISAR_L2_GCOV_V1/NISAR_L2_PR_GCOV_034_104_A_175_2005_DHDH_A_20261031T110900_20261031T110935_P05036_N_F_J_001/NISAR_L2_PR_GCOV_034_104_A_175_2005_DHDH_A_20261031T110900_20261031T110935_P05036_N_F_J_001.h5) |
| Piura–Castilla, descendente 112 D f091 | 19 oct 2026, PROV (`033_112_D_091_4005_DHDH`) | [31 oct 2026, Validated](https://nisar.asf.earthdatacloud.nasa.gov/NISAR/NISAR_L2_GCOV_V1/NISAR_L2_PR_GCOV_034_112_D_091_4005_DHDH_A_20261031T234017_20261031T234052_P05036_N_F_J_001/NISAR_L2_PR_GCOV_034_112_D_091_4005_DHDH_A_20261031T234017_20261031T234052_P05036_N_F_J_001.h5) |
| Chulucanas y Salitral, ascendente 003 A f175 | 12 oct 2026, PROV (`033_003_A_175`) [?: fecha inferida del ciclo de 12 días] | 24 oct 2026, Validated (`034_003_A_175_2005_DHDH`) |

### Consultas CMR para reproducir cada lista

Cambiar `point=lon,lat` por el punto de cada zona y `collection_concept_id` por el producto. Ejemplo para Tumbes, GCOV PROVISIONAL: `https://cmr.earthdata.nasa.gov/search/granules.json?collection_concept_id=C2854338529-ASF&point=-80.45,-3.57&sort_key=start_date&page_size=200`

Con Python: `asf_search` o `seppo_nisar_search` de [OpenSEPPO](https://openseppo.readthedocs.io/en/latest/).

## Cronología cruzada NISAR–noticias

La historia tiene tres actos: costa seca de base en agosto, primeras inundaciones del 19–27 de octubre (con escenas de antes y después) y golpe del 1–2 de noviembre (con escena previa y la posterior pendiente). Va en orden cronológico porque es el orden del relato. La columna "Qué debería verse" es una hipótesis [A] que los datos deben confirmar o refutar.

| Fecha | Zona | Qué dicen los medios | Escena NISAR | Qué debería verse [A] |
| --- | --- | --- | --- | --- |
| 17 jun 2026 | Piura | Senamhi: Piura ya siente el calentamiento del mar y podría tener lluvias intensas hacia fines de 2026 ([Andina](https://andina.pe/agencia/noticia-senamhi-advierte-piura-ya-experimenta-efectos-evento-del-fenomeno-nino-costero-1079806.aspx)) | Serie desde el 21 jun | Referencia sin lluvia |
| 13 ago 2026 | Tumbes | Sin evento: línea base seca | 003 A f176, PROV | Valle seco, cauces con poca agua |
| 19–20 oct 2026 | Piura, Chulucanas | Calles y viviendas inundadas; hasta 30 cm de agua en el mercado de Chulucanas ([Panamericana](https://panamericana.pe/EstaNoche/nacionales/476125-fenomeno-nino-golpea-piura-intensas-lluvias-inundan-calles-viviendas), [Caretas](https://caretas.pe/?p=840084)) | Antes 19 oct · después 24 oct (003 A) y 31 oct (104 A, 112 D) | Δγ⁰ en manzanas bajas; suelo más húmedo en SME2 |
| 23 oct 2026 | Tumbes, Zarumilla, Puerto Pizarro | Más de 8 horas de lluvia y sectores inundados; un colegio suspende clases ([América TV](https://www.americatv.com.pe/noticias/amp/actualidad/tumbes-lluvia-mas-ocho-horas-provoca-inundaciones-n523751)) | Antes 12 oct · después 24 oct (003 A f176) | Agua en campos y bordes urbanos; cociente HH/HV más alto en el manglar |
| 27 oct 2026 | Zarumilla (El Salto) | 102 mm en un día ([Andina](https://andina.pe/agencia/noticia-el-nino-tumbes-endures-extraordinary-rainfall-of-up-to-110-liters-per-square-meter-1098315.aspx)) | Antes 19 oct · después 31 oct (112 D f090) | Saturación acumulada del suelo |
| 31 oct 2026 | Tumbes | — | Última escena antes del gran evento | Estado previo al 1–2 nov |
| 1–2 nov 2026 | Zarumilla – Aguas Verdes | Desborde del Zarumilla (242 m³/s); Puerto Perú inundado; más de 300 familias afectadas ([Caretas](https://caretas.pe/?p=842604), [Teleamazonas](https://www.teleamazonas.com/actualidad/noticias/internacional/emergencia-tumbes-lluvias-dejan-agua-puerto-peru-frontera-ecuador-131967/)) | Posterior **pendiente** | Llanura del Zarumilla con agua |
| 2 nov 2026 | Valle del Tumbes | Río Tumbes por encima del umbral rojo de 1 000 m³/s; 70 % de la lluvia anual en menos de 30 días en el aeropuerto ([El Búho](https://elbuho.pe/?p=441556)) | Posterior pendiente | Desborde en la llanura baja del Tumbes |
| 2 nov 2026 | Salitral (Morropón), Piura ciudad | Quebrada Serrán activada; puente terrestre militar; drenaje en Las Azucenas y en la av. Sánchez Cerro ([El Peruano](https://elperuano.pe/noticia/308191-fuerzas-armadas-activan-puente-terrestre-para-evitar-que-morropon-quede-aislada-por-el-nino)) | Posterior pendiente (antes: 24 y 31 oct) | Coherencia baja a lo largo de la quebrada |
| 3 nov 2026 | Nacional | DS 149-2026-PCM: emergencia en 1 380 distritos ([Caretas](https://caretas.pe/?p=842501)) | — | — |
| 4 nov 2026 | Tumbes, Casitas | Tormenta: calles inundadas, distrito de Casitas aislado ([El Búho](https://elbuho.pe/?p=441960)) | Pendiente | — |
| 8 nov 2026 | Tumbes | Indeci instala tres albergues temporales para 168 familias ([El Peruano](https://elperuano.pe/noticia/308553-tumbes-cuenta-con-tres-albergues-temporales-para-familias-damnificadas-por-las-lluvias)) | Pendiente | — |

Que el 2 de noviembre la prensa señale a Zarumilla como la provincia más afectada ([Andina](https://andina.pe/agencia/noticia-el-nino-tumbes-endures-extraordinary-rainfall-of-up-to-110-liters-per-square-meter-1098315.aspx)) da la pregunta central para la demo: ¿la escena posterior al 1–2 nov muestra en Zarumilla el mayor cambio de área de agua de toda la costa norte?

## Pipeline de procesamiento

Son siete pasos, del catálogo a la tabla que une indicador y titular. Para cada escena GCOV se calculan los indicadores 1–9 de la matriz, así cada dato en bruto aporta todo lo que puede. Los métodos son estándar en SAR pero no los verifiqué en fuentes de esta sesión [A], salvo donde se indica.

1. **Buscar:** consulta CMR o `asf_search` por punto y colección. Se filtra por track + dirección + frame + `DHDH`.
2. **Descargar y leer:** HDF5 con Earthdata Login; capas `/science/LSAR/GCOV/grids/frequencyA/HHHH` y `HVHV` [V-fragmento: ruta de la guía GCOV]. Se recorta a la zona.
3. **Pasar a dB y filtrar speckle:** filtro multitemporal sobre la pila de la misma geometría.
4. **Indicadores por escena:**
    - Máscara de agua: umbral de Otsu sobre HH y HV en dB, con HV como control frente a la rugosidad.
    - Cociente HH/HV para manglar, cultivos y rebote doble urbano.
    - Δγ⁰ respecto de la línea base seca de agosto y respecto de la escena previa al evento.
5. **Coherencia:** entre pares GSLC de 12 días (OpenSEPPO trae `seppo_nisar_coherence` [V-fragmento]). Se marcan quebradas y laderas con caída de coherencia.
6. **Humedad:** serie SME2 por zona; comparar con la lluvia de estaciones de Senamhi o GPM.
7. **Unir con las noticias:** tabla `fecha · zona · indicador · valor · titular · enlace`, que alimenta el storytelling.

Fórmulas base:

```latex
\gamma^0_{\mathrm{dB}} = 10\,\log_{10}\gamma^0
```

```latex
\Delta_{\mathrm{dB}} = 10\,\log_{10}\!\left(\frac{\gamma^0_{t_2}}{\gamma^0_{t_1}}\right)
```

```latex
A_{\mathrm{agua}} = N_{\mathrm{p\acute{i}xeles\ agua}} \times (\Delta x)^2
```

```latex
|\gamma| = \frac{\left|\langle s_1 s_2^{*}\rangle\right|}{\sqrt{\langle |s_1|^2\rangle\,\langle |s_2|^2\rangle}}
```

Para Δx hay que leer el espaciado de píxel del propio archivo; no conviene suponer 10 o 20 m [?]. La lectura de Δ_dB como cambio de constante dieléctrica supone que la rugosidad no cambió entre t₁ y t₂. Con 5 a 12 días entre fechas es razonable en suelo agrícola, pero no donde hubo depósito de lodo (quebradas) [A].

## Limitaciones y huecos

El riesgo mayor es que la escena posterior al pico del 1–2 de noviembre todavía no está publicada. Lo demás se controla con disciplina en la comparación.

- **Escena posterior al 1–2 nov pendiente.** Al 14 nov, entre el 1 y el 14 de noviembre la costa norte solo tiene escenas Validated del track 011 D (5 nov, frames f091–f092), que no cubren Tumbes ni Piura ciudad [V]. Las próximas pasadas de los tracks 003 A y 112 D pueden aparecer en cualquier momento. Conviene revisar el CMR antes de la demo.
- **Febrero–marzo 2026 sin NISAR.** Las inundaciones más grandes del año en Piura (más de 12 000 damnificados) y Tumbes (6 000 ha) ocurrieron antes del 21 jun. El atrasado de sep 2025–jun 2026 debe publicarse antes de fin de 2026 [V-fragmento].
- **Dos versiones de procesamiento en cada par.** El antes es PROVISIONAL (P05023) y el después es Validated (P05036). Parte del ΔdB puede venir de la calibración y no del terreno. La forma de controlarlo es medir el ΔdB en zonas estables (roca, desierto sin lluvia) y restarlo [A].
- **Modos mezclados.** Algunas fechas son `SHSH` (solo HH; p. ej. Piura 25 set 2026, 104 A). En esas fechas no hay cociente HH/HV [V].
- **Sin climatología NISAR.** No hay un año anterior para separar El Niño de la estación normal. En la costa norte, octubre normalmente es seco: el aeropuerto de Tumbes con 70 % de la lluvia anual en menos de 30 días [V-fragmento] es la mejor prueba de que el cambio es anómalo. SAOCOM, también en banda L y entre los recursos del reto, puede dar años anteriores [?].
- **Coordenadas aproximadas.** Los puntos de consulta son míos [A]. Para el análisis final hay que trazar polígonos sobre los sectores que nombran las noticias (Puerto Perú, Las Azucenas, quebrada Serrán).
- **Productos de respuesta urgente.** NISAR tiene una colección Urgent Response con escenas de ago–set 2026 sobre el sur de Ecuador y el norte de Amazonas y Cajamarca (track 011 D). No encontré a qué evento corresponden [?]. Ninguna cubre Tumbes ni Piura.
- **Lluvia y temperatura del mar** no se miden con NISAR y vienen de otras fuentes [?].

## Fuentes

**Páginas abiertas en esta sesión (base de los [V] estrictos)**

- [Catálogo CMR de NASA](https://cmr.earthdata.nasa.gov/search/collections.json?platform=NISAR&page_size=60), consultado el 14 nov 2026: colecciones, escenas y enlaces HDF5
- [Recursos del reto Dancing with the SARs](https://www.spaceappschallenge.org/2026/challenges/dancing-with-the-sars/?tab=resources)
- [Andina, 2 nov 2026 (Tumbes)](https://andina.pe/agencia/noticia-el-nino-tumbes-endures-extraordinary-rainfall-of-up-to-110-liters-per-square-meter-1098315.aspx)
- [El Peruano, 2 nov 2026 (Morropón)](https://elperuano.pe/noticia/308191-fuerzas-armadas-activan-puente-terrestre-para-evitar-que-morropon-quede-aislada-por-el-nino)

**Leídas solo como fragmento del buscador ([V-fragmento], pendientes de abrir)**

- Datos NISAR: [Disponibilidad (ASF)](https://hyp3-docs.asf.alaska.edu/nisar-docs/availability-overview/) · [Earthdata Forum](https://forum.earthdata.nasa.gov/viewtopic.php?p=26145) · [Guía GCOV](https://nisar-docs.asf.alaska.edu/gcov/) · [Productos L3](https://nisar-docs.asf.alaska.edu/level3) · [Resumen de productos](https://nisar-docs.asf.alaska.edu/products-overview/) · [OpenSEPPO](https://openseppo.readthedocs.io/en/latest/)
- El Niño y emergencias: [El Comercio, ENFEN](https://elcomercio.pe/peru/fenomeno-el-nino-enfen-mantiene-alerta-y-preve-magnitud-extraordinaria-hasta-enero-de-2027-ultimas-noticia/) · [Primicias, emergencia](https://www.primicias.ec/internacional/peru-emergencia-fenomeno-nino-municipios-lluvias-inundaciones-136308/) · [Caretas, DS 149-2026-PCM](https://caretas.pe/?p=842501) · [El Peruano, Cenepred](https://elperuano.pe/noticia/300908-fen-instan-a-fortalecer-medidas-de-prevencion) · [Primicias, puntos críticos](https://www.primicias.ec/internacional/fenomeno-nino-peru-posibles-danos-perdidas-agricultura-pesca-viviendas-131166/)
- Tumbes: [América TV, 23 oct](https://www.americatv.com.pe/noticias/amp/actualidad/tumbes-lluvia-mas-ocho-horas-provoca-inundaciones-n523751) · [El Búho, 2 nov](https://elbuho.pe/?p=441556) · [Caretas, 2 nov](https://caretas.pe/?p=842604) · [Teleamazonas, 2 nov](https://www.teleamazonas.com/actualidad/noticias/internacional/emergencia-tumbes-lluvias-dejan-agua-puerto-peru-frontera-ecuador-131967/) · [El Búho, 5 nov](https://elbuho.pe/?p=441960) · [El Peruano, 8 nov](https://elperuano.pe/noticia/308553-tumbes-cuenta-con-tres-albergues-temporales-para-familias-damnificadas-por-las-lluvias) · [El Comercio, archivo Tumbes](https://elcomercio.pe/peru/tumbes/)
- Piura: [Andina, 17 jun](https://andina.pe/agencia/noticia-senamhi-advierte-piura-ya-experimenta-efectos-evento-del-fenomeno-nino-costero-1079806.aspx) · [Panamericana, 20 oct](https://panamericana.pe/EstaNoche/nacionales/476125-fenomeno-nino-golpea-piura-intensas-lluvias-inundan-calles-viviendas) · [Caretas, 20 oct](https://caretas.pe/?p=840084) · [El Comercio (EC), 20 oct](https://www.elcomercio.com/actualidad/mundo/la-costa-norte-de-peru-esta-bajo-el-agua/) · [El Búho, 25 feb](https://elbuho.pe/2026/02/mas-de-12-mil-damnificados-y-mas-de-1-300-afectados-dejan-las-lluvias-en-piura/) · [El Búho, 13 feb (ENFEN)](https://elbuho.pe/2026/02/enfen-activa-estado-de-alerta-de-el-nino-costero-y-preve-lluvias-intensas-a-partir-de-marzo/)
- Lambayeque (control): [Andina, río La Leche](https://andina.pe/agencia/noticia-fenomeno-nino-ana-culmina-trabajos-descolmatacion-rio-leche-1098996.aspx)
