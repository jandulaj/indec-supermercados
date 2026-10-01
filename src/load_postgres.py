"""Carga los CSV de data/processed/ en PostgreSQL y construye el modelo.

Flujo ELT:
  1. CSV  -> schema "stg"   (copia tal cual, la hace pandas)
  2. stg  -> schema "super" (dimensiones y hechos, lo hace SQL: sql/01_modelo.sql)

Uso:  python src/load_postgres.py      (conexión tomada de .env)
"""
import logging
import os
import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

BASE = Path(__file__).resolve().parents[1]
PROCESADOS = BASE / "data" / "processed"
SQL_MODELO = BASE / "sql" / "01_modelo.sql"
LOGS = BASE / "logs"

# CSV -> tabla de staging
ARCHIVOS = {
    "indices_ventas.csv": "indices_ventas",
    "indices_precios.csv": "indices_precios",
    "ventas_canal.csv": "ventas_canal",
    "ventas_medio_pago.csv": "ventas_medio_pago",
    "ventas_categoria_jurisdiccion.csv": "ventas_categoria_jurisdiccion",
}

LOGS.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOGS / "etl.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)


def crear_engine():
    load_dotenv(BASE / ".env")
    url = (
        f"postgresql+psycopg2://{os.environ['PG_USER']}:{os.environ['PG_PASSWORD']}"
        f"@{os.environ['PG_HOST']}:{os.environ['PG_PORT']}/{os.environ['PG_DB']}"
    )
    return create_engine(url)


def cargar_staging(engine) -> None:
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS stg"))
    for archivo, tabla in ARCHIVOS.items():
        df = pd.read_csv(PROCESADOS / archivo, parse_dates=["periodo"])
        df.to_sql(tabla, engine, schema="stg", if_exists="replace", index=False,
                  method="multi", chunksize=5000)
        log.info("stg.%s: %d filas", tabla, len(df))
        with engine.begin() as conn:                # to_sql recrea la tabla: reactivar RLS
            conn.execute(text(f"ALTER TABLE stg.{tabla} ENABLE ROW LEVEL SECURITY"))


def construir_modelo(engine) -> None:
    sql = SQL_MODELO.read_text(encoding="utf-8")
    with engine.begin() as conn:                    # una sola transacción: todo o nada
        # cursor del driver sin parámetros: el SQL tiene '%' (LIKE) que no debe interpretarse
        conn.connection.cursor().execute(sql)
        for tabla in ["dim_periodo", "dim_jurisdiccion", "dim_categoria", "fact_indices",
                      "fact_ventas_canal", "fact_ventas_medio_pago", "fact_ventas_categoria"]:
            n = conn.execute(text(f"SELECT count(*) FROM super.{tabla}")).scalar()
            log.info("super.%s: %d filas", tabla, n)

        # Validación: toda jurisdicción debe tener región asignada (si el INDEC cambia un nombre, el CASE no la reconoce)
        sin_region = conn.execute(text(
            "SELECT string_agg(nombre, ', ') FROM super.dim_jurisdiccion WHERE region IS NULL")).scalar()
        if sin_region:
            log.warning("Jurisdicciones sin región asignada: %s", sin_region)


def main() -> None:
    log.info("Carga a PostgreSQL iniciada")
    try:
        engine = crear_engine()
        cargar_staging(engine)
        construir_modelo(engine)
    except Exception:
        log.exception("CARGA ERROR")
        sys.exit(1)
    finally:
        log.info("Carga terminada")


if __name__ == "__main__":
    main()
