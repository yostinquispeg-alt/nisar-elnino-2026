# NISAR · El Niño 2026 en la costa norte del Perú (Tumbes y Piura)

Reto **Dancing with the SARs** (NASA Space Apps 2026). Cruza escenas NISAR L2 GCOV (banda L) con noticias de las inundaciones de octubre y noviembre de 2026 en Tumbes y Piura. Mide el agua, la humedad del suelo y la vegetación con indicadores sensibles a la **rugosidad** y a la **constante dieléctrica**.

## Las dos partes

| Carpeta | Qué hay | Cómo se usa |
|---|---|---|
| **`1_jupyter/`** | `NISAR_analisis.ipynb`: el análisis paso a paso, explicado y con fuentes en cada sección | Ábrelo en VS Code, elige el kernel y pulsa **Run All**. Al final abre el mapa. |
| **`2_mapa/`** | `generar_mapa.py`: procesa las escenas y escribe las capas del mapa. `MAPA_NISAR.html`: el mapa | `python 2_mapa/generar_mapa.py` y luego doble clic en `MAPA_NISAR.html` (se abre solo) |

Las dos partes usan el mismo código (`nisar_cn/`) y escriben en la misma carpeta `salidas/`. Basta con correr una de las dos para que el mapa muestre los resultados.

## Estructura

```
NISAR_ElNino_2026/
├── 1_jupyter/
│   └── NISAR_analisis.ipynb      análisis con datos reales (MODO = "REAL")
├── 2_mapa/
│   ├── generar_mapa.py           script: procesa y genera las capas del mapa
│   └── MAPA_NISAR.html           mapa interactivo
├── nisar_cn/                     código compartido, un archivo por etapa
│   ├── config.py                 zonas, eventos, noticias, colecciones, umbrales
│   ├── fisica.py                 Dubois (HH) + Topp: sensibilidad a rugosidad y ε
│   ├── busqueda.py               CMR, nombres de producto, pares antes/después
│   ├── acceso.py                 streaming HTTPS con la llave del .env
│   ├── lectura.py                ventana de cada zona dentro del HDF5
│   ├── indicadores.py            agua, vegetación inundada, Δσ⁰, Δε′, HV, capa "impacto"
│   ├── mapas.py                  capas PNG en lat/lon para el mapa
│   ├── exportar.py               CSV de storytelling + manifiesto del mapa
│   └── pipeline.py               orquesta las etapas
├── salidas/                      resultados: CSV, manifiesto y capas PNG
├── docs/                         REFERENCIAS.md (R1–R15, N1–N6, huecos [?]) e investigación
├── extras/                       notebook DEMO (datos sintéticos) y visor de vistas previas NASA
├── requirements.txt
└── (ocultos en VS Code: .env, cache/, .vscode/, .gitignore)
```

## Primera vez

1. **Copia tu `.env`** dentro de esta carpeta. Si no lo copias, el código usa el de `Descargas\NassaSpaceAppChallenge` mientras siga ahí. Solo imprime los nombres de las variables, nunca sus valores.
2. Abre la carpeta en VS Code (**Archivo → Abrir carpeta…**) y en la terminal ejecuta:
   ```
   python -m pip install -r requirements.txt
   python 2_mapa/generar_mapa.py --probar
   ```
   La prueba debe terminar con **"Acceso a NASA: OK — HDF5 válido"**.
3. Corre el notebook (`1_jupyter`) o el script (`python 2_mapa/generar_mapa.py`).

## Capas del mapa

| Grupo | Capa | Qué mide | Estatus |
|---|---|---|---|
| Todo | Impacto | agua permanente, inundación nueva, agua retirada, vegetación inundada, suelo más húmedo/rugoso, suelo más seco/liso | cortes ±2 dB [A][?] |
| Agua | Antes / Después / Cambio | σ⁰ HH bajo umbral de Otsu acotado (agua en calma = reflexión especular) | umbrales [?] |
| Humedad del suelo | Δε′ | constante dieléctrica por Dubois con rugosidad constante; ε′ sube con la humedad (Topp) | [A] |
| Humedad del suelo | Δσ⁰ HH | cambio de retrodispersión sobre tierra; con HH/HV no se separa humedad de rugosidad | física [V], lectura [A] |
| Vegetación | HV antes / después / ΔHV | dispersión de volumen | física [V], ΔHV como vegetación [A] |
| Radar | HH, RGB (R=HH, G=HV, B=HH−HV) | imagen de base | colores [A] |

El modo DEMO (`extras/NISAR_analisis_DEMO.ipynb` o `python 2_mapa/generar_mapa.py --modo DEMO`) usa archivos **sintéticos**: sirve para probar el código y **no son resultados**. El mapa lo avisa con una franja naranja.

Las fuentes y los huecos pendientes están en `docs/REFERENCIAS.md`.
