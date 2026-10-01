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

def transformar_cuadro2(raw: pd.DataFrame) -> pd.DataFrame:
    es_dato = raw[0].map(lambda v: isinstance(v, datetime))
    cuadro2 = raw.loc[es_dato, [0, 1, 2, 3, 5, 6, 8, 9, 10]].copy()   # 4 y 7: separadoras
    cuadro2.columns = [
        "periodo",
        "idx_corriente", "var_ia_corriente", "var_acum_corriente",
        "idx_constante", "var_ia_constante",
        "idx_precios_impl", "var_ia_precios_impl", "var_mensual_precios_impl",
    ]
    cuadro2["periodo"] = pd.to_datetime(cuadro2["periodo"])
    numericas = cuadro2.columns[1:]
    # "…" (dato no disponible) y cualquier texto → NaN
    cuadro2[numericas] = cuadro2[numericas].apply(pd.to_numeric, errors="coerce")

    log.info("Cuadro 2: %d filas (%s a %s)", len(cuadro2),
             cuadro2["periodo"].min().date(), cuadro2["periodo"].max().date())

    return cuadro2

def transformar_cuadro4(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    es_dato = raw[0].map(lambda v: isinstance(v, datetime))

    # 1. Elegir columnas por posición y nombrarlas (como en el Cuadro 1)
    df = raw.loc[es_dato, [0, 1, 3, 4, 6, 7, 8, 9]].copy()        # 2 y 5: separadoras
    df.columns = ["periodo", "total", "salon", "online",
                  "efectivo", "debito", "credito", "otros"]
    df["periodo"] = pd.to_datetime(df["periodo"])
    numericas = df.columns[1:]
    df[numericas] = df[numericas].apply(pd.to_numeric, errors="coerce")

    # 2. Validar contra el total (después se descarta)
    dif_canal = (df["salon"] + df["online"] - df["total"]).abs() / df["total"]
    dif_pago = (df[["efectivo", "debito", "credito", "otros"]].sum(axis=1) - df["total"]).abs() / df["total"]
    if dif_canal.max() > 0.001 or dif_pago.max() > 0.001:
        log.warning("Cuadro 4: las partes no suman el total (máx. dif. canal %.4f%%, pago %.4f%%)",
                    dif_canal.max() * 100, dif_pago.max() * 100)

    # 3. De ancho a largo: dos tablas independientes
    canal = df.melt(id_vars="periodo", value_vars=["salon", "online"],
                    var_name="canal", value_name="ventas_miles")
    medio_pago = df.melt(id_vars="periodo", value_vars=["efectivo", "debito", "credito", "otros"],
                         var_name="medio_pago", value_name="ventas_miles")

    log.info("Cuadro 4: %d meses | canal %d filas | medio de pago %d filas",
             len(df), len(canal), len(medio_pago))
    return canal, medio_pago

def transformar_cuadro5(raw: pd.DataFrame) -> pd.DataFrame:
    es_dato = raw[0].map(lambda v: isinstance(v, datetime))

    # Fila 2 = jurisdicción (combinada), fila 3 = categoría → rellenar hacia la derecha
    enc = raw.iloc[2:4, 1:].ffill(axis=1)
    valores = raw.loc[es_dato, 1:].copy()
    valores.index = pd.DatetimeIndex(raw.loc[es_dato, 0], name="periodo")
    valores.columns = pd.MultiIndex.from_arrays(
        [enc.iloc[0].str.strip(), enc.iloc[1].str.strip()],
        names=["jurisdiccion", "categoria"],
        )
    valores = valores.dropna(axis=1, how="all")   # borra las columnas separadoras vacías
    # De ancho a largo: una fila por período × jurisdicción × categoría
    ventas = (valores.stack(["jurisdiccion", "categoria"], future_stack=True)
        .rename("ventas_miles").reset_index())
    ventas["es_confidencial"] = ventas["ventas_miles"].eq("s")   # secreto estadístico
    ventas["ventas_miles"] = pd.to_numeric(ventas["ventas_miles"], errors="coerce")
    ventas["es_total_pais"] = ventas["jurisdiccion"].eq("Total del país")
    ventas["es_total_categoria"] = ventas["categoria"].eq("Total")   
    n_jur = ventas["jurisdiccion"].nunique()
    n_cat = ventas["categoria"].nunique()
    n_conf = int(ventas["es_confidencial"].sum())
    log.info("Cuadro 5: %d filas | %d jurisdicciones | %d categorías | %d confidenciales",
        len(ventas), n_jur, n_cat, n_conf)
    if (n_jur, n_cat) != (26, 12):   # 24 provincias con Buenos Aires dividida en GBA y resto, CABA y el total del país
        log.warning("Cuadro 5: estructura inesperada, revisar encabezados del Excel")
    return ventas


def main() -> None:
    log.info("ETL iniciado")
    try:
        SALIDA.mkdir(parents=True, exist_ok=True)

        # Cuadro 1 - Indices Ventas
        cuadro1 = transformar_cuadro1(leer_hoja("Cuadro 1"))
        cuadro1.to_csv(SALIDA / "indices_ventas.csv", index=False)
        log.info("Guardado %s", SALIDA / "indices_ventas.csv")

        # Cuadro 2 - Indices Ventas
        cuadro2 = transformar_cuadro2(leer_hoja("Cuadro 2"))
        diff = (cuadro2["idx_constante"].values - cuadro1["idx_original"].values)
        if abs(diff).max() > 0.001:
            log.warning("Cuadro 2: idx_constante no coincide con Cuadro 1")
        cuadro2.to_csv(SALIDA / "indices_precios.csv", index=False)
        log.info("Guardado %s", SALIDA / "indices_precios.csv")

        # Cuadro 4 - Ventas por Canal y Medio de Pago
        canal, medio_pago = transformar_cuadro4(leer_hoja("Cuadro 4."))
        canal.to_csv(SALIDA / "ventas_canal.csv", index=False)
        medio_pago.to_csv(SALIDA / "ventas_medio_pago.csv", index=False)
        log.info("Guardado %s", SALIDA / "ventas_canal.csv")
        log.info("Guardado %s", SALIDA / "ventas_medio_pago.csv")

        # Cuadro 5 - Ventas Totales
        cuadro5 = transformar_cuadro5(leer_hoja("Cuadro 5."))
        cuadro5.to_csv(SALIDA / "ventas_categoria_jurisdiccion.csv", index=False)
        log.info("Guardado %s", SALIDA / "ventas_categoria_jurisdiccion.csv")
    except Exception:
        log.exception("ETL ERROR")        # guarda el traceback completo
        sys.exit(1)
    finally:
        log.info("ETL terminado")


if __name__ == "__main__":
    main()
