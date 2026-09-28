# Ventas en supermercados de Argentina (2017–2026) · Análisis con Python + SQL

> 🚧 Proyecto en construcción. / *Work in progress — English summary below.*

Análisis de la **Encuesta de Supermercados del INDEC** (serie mensual, enero 2017 – julio 2026): limpieza de datos con **pandas**, modelo y consultas en **PostgreSQL**, visualizaciones en **matplotlib/seaborn** y dashboard en **Power BI**.

## Preguntas de negocio
1. ¿Cuánto crecieron o cayeron **realmente** las ventas (a precios constantes) y dónde estamos frente al pico?
2. ¿Cuánto del crecimiento nominal es **precio** y cuánto es **volumen**?
3. ¿Cómo cambió la **canasta**: básicos vs. discrecionales?
4. ¿Cómo **pagan** los clientes: efectivo vs. débito, crédito y billeteras?
5. ¿Qué **provincias** ganan y cuáles pierden en términos reales?

Detalle, métricas y supuestos: [`docs/preguntas_negocio.md`](docs/preguntas_negocio.md)

## Hallazgos principales
_(se completa al terminar el análisis — 1 línea de conclusión + 1 gráfico por pregunta)_

## Pipeline
```
INDEC (.xlsx) ──► src/download.py ──► data/raw/
                                          │
                   src/transform.py (pandas: encabezados multinivel, ancho→largo,
                                     secreto estadístico, deflactor)
                                          ▼
                                  data/processed/*.csv ──► PostgreSQL (sql/) ──► Power BI
                                          │
                                  notebooks/ ──► reports/figures/
```

## Estructura del repo
```
├── data/
│   ├── raw/                 # Excel original del INDEC (sin modificar)
│   └── processed/           # CSV tidy listos para SQL / Power BI
├── docs/                    # fuente de datos, preguntas de negocio, diccionario
├── notebooks/               # 01_exploracion · 02_limpieza · 03_analisis
├── src/                     # download.py · transform.py · load_postgres.py
├── sql/
│   ├── 01_schema.sql        # modelo estrella
│   └── queries/             # una consulta por pregunta de negocio
├── reports/figures/         # PNG usados en este README
└── powerbi/                 # .pbix + capturas del dashboard
```

## Cómo reproducirlo
```bash
python -m venv .venv && .venv\Scripts\activate      # Windows
pip install -r requirements.txt
python src/download.py                              # baja la última versión del INDEC
python src/transform.py                             # genera data/processed/
psql -d indec -f sql/01_schema.sql                  # crea el modelo
python src/load_postgres.py                         # carga los CSV (usa .env)
```

## Fuente
INDEC, Encuesta de Supermercados. Ver [`docs/fuente_datos.md`](docs/fuente_datos.md).

---
### English summary
Analysis of Argentina's official supermarket sales survey (INDEC, monthly, 2017–2026). Python (pandas) for cleaning multi-level Excel headers and reshaping wide→long, PostgreSQL for the data model and business queries, matplotlib for charts, and a Power BI dashboard. Sales are deflated with the survey's implicit price index to separate real volume from inflation.

**Autor:** Javier · Senior BI Engineer → Data Analyst
