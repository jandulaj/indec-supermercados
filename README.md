# Argentina Supermarket Sales (2017–2026) · Python · PostgreSQL · Power BI

*[Leer en español](README.es.md)*

End-to-end analysis of Argentina's official **Supermarket Survey (INDEC)**, a monthly series from January 2017 to July 2026. The raw Excel file is cleaned with **pandas**, loaded into a **PostgreSQL** star schema, queried with **SQL** to answer four business questions, and presented in a **Power BI** dashboard.

The central challenge is inflation. Sales in pesos grew 68-fold over the period, so nominal figures say almost nothing on their own. The analysis uses the survey's implicit price index to separate **real volume** from **price**.

## Business questions
1. How much did sales **really** grow or shrink at constant prices, and how far are we from the peak?
2. How much of the nominal growth is **price**, and how much is **volume**?
3. How did the **basket** change between basic and discretionary goods?
4. How do customers **pay**: cash, debit, credit or digital wallets?

Metrics, assumptions and limitations: [`docs/preguntas_negocio.md`](docs/preguntas_negocio.md) (in Spanish).

## Key findings

### 1. Real sales are 22 % below their 2017 peak
![Sales evolution](reports/figures/evolucion_ventas.png)

In July 2026, the seasonally adjusted volume index stands at 81.2 (2017 = 100). That is **21.7 % below the series peak** (January 2017) and only 1 % above the March 2024 low. The decline came in two steps: 2018–2019 (−12 % cumulative) and 2024 (−11 % in a single year), which erased the slow 2020–2023 recovery. After a rebound in 2025 (+2 %), January–July 2026 is down again (−2.7 % year over year).

> *Hypothesis:* both steps coincide with the devaluations and inflation spikes of 2018–2019 and late 2023–2024.

### 2. All the nominal growth was inflation
![Price vs. volume](reports/figures/precio_volumen.png)

Between 2017 and 2025, sales in pesos grew **×68** while supermarket prices grew **×82**, so **volume fell 17 %**. The two largest annual volume drops match the two price jumps: **2019** (prices +60 %, volume −9.8 %) and **2024** (prices +229 %, volume −11.0 %).

**2023 is the exception:** prices rose 141 % while volume was flat (+0.9 %).

> *Hypothesis:* consumers bought ahead of the expected devaluation, which is consistent with the December 2023 spike in the monthly series.
>
> *Note:* the price index is the survey's implicit deflator for supermarket sales, not the official CPI.

### 3. The basket shifted toward basics during crises
![Basket mix](reports/figures/mix_canasta.png)

Discretionary goods (electronics, home goods and apparel) fell from **9.2 % of spending in 2017 to 6.6 % in 2026**. They dropped in 2019 and 2024, the same years as the volume declines, recovered partially in 2020–2022, and have not recovered since 2024. Among basics, **meat gained 3.1 percentage points** (9.7 % → 12.8 % in 2025).

> *Limitation:* these are shares of nominal spending, so part of the shift may come from relative prices rather than quantities.

### 4. Cash use fell by more than half
![Payment methods](reports/figures/medios_pago.png)

Cash went from **35.5 % of sales in 2017 to 16.8 % in 2026** (−18.7 pp), with the sharpest drop in 2024. Credit became the main payment method (43 %), and "other methods" (digital wallets and QR) nearly tripled after 2023, reaching 15 %.

> *Hypothesis:* installment financing in a high-inflation context, plus the adoption of digital payments. *(2026: January–July.)*

## Power BI dashboard
Three pages built on the same PostgreSQL model. They are versioned as a **PBIP** project, so the semantic model (TMDL) and the report (JSON) are plain text and diffable in git.

| Sales evolution and payments | Basket mix | Price vs. volume |
|---|---|---|
| ![Page 1](reports/dashboard/p1_evolucion.png) | ![Page 2](reports/dashboard/p2_canasta.png) | ![Page 3](reports/dashboard/p3_precio_volumen.png) |

DAX highlights:
- Dynamic year bounds (first year and last complete year) shared across measures.
- Virtual tables with `ADDCOLUMNS` + `TOPN` for "worst year" and "top gaining/losing category".
- Deflated sales with `SUMX`.
- Combined chart with a secondary axis for annual price vs. volume change.

## Pipeline
```
INDEC (.xlsx) ──► src/download.py ──► data/raw/
                                          │
              src/transform.py  (pandas: multi-level headers, wide → long,
                                 statistical-secrecy markers, validations)
                                          ▼
                                 data/processed/*.csv
                                          │
              src/load_postgres.py  (CSV → stg schema → star schema via sql/01_modelo.sql)
                                          ▼
                        PostgreSQL ──► sql/queries/ (one query per question)
                                   └─► Power BI (PBIP)
```

**Data model:** a constellation schema with four fact tables at different grains (indices, sales by channel, by payment method, and by category × province). They share a continuous date dimension plus province and category dimensions. The load runs in a single transaction and is idempotent.

**SQL techniques:** CTEs, window functions (`LAG`, `FIRST_VALUE`, `SUM() OVER (PARTITION BY …)`) and annual aggregation of monthly indices.

## Repository structure
```
├── data/
│   ├── raw/                 # original INDEC Excel (unchanged)
│   └── processed/           # tidy CSVs
├── docs/                    # data source, business questions (Spanish)
├── src/                     # download.py · transform.py · load_postgres.py
├── sql/
│   ├── 01_modelo.sql        # star schema (stg → super), run by load_postgres.py
│   └── queries/             # q1–q4, one per business question
├── reports/
│   ├── figures/             # charts used in this README
│   └── dashboard/           # Power BI screenshots
├── powerbi/                 # PBIP project (Indec.pbip) + theme
└── docker-compose.yml       # optional local PostgreSQL
```

## How to reproduce
```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # fill in the PostgreSQL connection
docker compose up -d               # optional: local PostgreSQL instead of a cloud instance

python src/download.py             # INDEC Excel → data/raw/
python src/transform.py            # Excel → data/processed/*.csv
python src/load_postgres.py        # CSV → PostgreSQL (staging + star schema)
```
Then open `powerbi/Indec.pbip` in Power BI Desktop and point the data source to your database.

## Source
INDEC, *Encuesta de Supermercados*. See [`docs/fuente_datos.md`](docs/fuente_datos.md). This is an independent analysis, not affiliated with INDEC.

## Next steps
- Provinces: real growth by jurisdiction, deflated with the national price index.
- Online channel share after 2020.
- Automated monthly refresh when INDEC publishes new data.

---
**Author:** Javier Jandula · Senior BI Engineer → Data Analyst
