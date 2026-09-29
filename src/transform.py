"""Transforma el Excel del INDEC en CSV limpios (data/processed/)."""
import logging
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

# Rutas relativas al repo: funcionan en Linux, Windows y en la PC de quien lo clone
BASE = Path(__file__).resolve().parents[1]
ARCHIVO = BASE / "data" / "raw" / "serie_supermercados.xlsx"
SALIDA = BASE / "data" / "processed"
LOGS = BASE / "logs"

LOGS.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOGS / "etl.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),          # también a la consola
    ],
)
log = logging.getLogger(__name__)


def leer_hoja(hoja: str) -> pd.DataFrame:
    return pd.read_excel(ARCHIVO, sheet_name=hoja, header=None)


def transformar_cuadro1(raw: pd.DataFrame) -> pd.DataFrame:
    es_dato = raw[0].map(lambda v: isinstance(v, datetime))
    cuadro1 = raw.loc[es_dato, [0, 1, 2, 3, 5, 6, 8, 9]].copy()   # 4 y 7: separadoras
    cuadro1.columns = [
        "periodo",
        "idx_original", "var_ia", "var_acum",
        "idx_desest", "var_mensual_desest",
        "idx_tendencia", "var_mensual_tendencia",
    ]
    cuadro1["periodo"] = pd.to_datetime(cuadro1["periodo"])
    numericas = cuadro1.columns[1:]
    # "…" (dato no disponible) y cualquier texto → NaN
    cuadro1[numericas] = cuadro1[numericas].apply(pd.to_numeric, errors="coerce")

    log.info("Cuadro 1: %d filas (%s a %s)", len(cuadro1),
             cuadro1["periodo"].min().date(), cuadro1["periodo"].max().date())
    return cuadro1


def main() -> None:
    log.info("ETL iniciado")
    try:
        SALIDA.mkdir(parents=True, exist_ok=True)
        cuadro1 = transformar_cuadro1(leer_hoja("Cuadro 1"))
        cuadro1.to_csv(SALIDA / "indices_ventas.csv", index=False)
        log.info("Guardado %s", SALIDA / "indices_ventas.csv")
    except Exception:
        log.exception("ETL ERROR")        # guarda el traceback completo
        sys.exit(1)
    finally:
        log.info("ETL terminado")


if __name__ == "__main__":
    main()
