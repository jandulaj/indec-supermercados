-- Borrador de modelo en PostgreSQL (esquema estrella simple).
-- Se carga desde data/processed/*.csv generados por src/transform.py.

CREATE SCHEMA IF NOT EXISTS super;

CREATE TABLE IF NOT EXISTS super.dim_periodo (
    periodo      DATE PRIMARY KEY,          -- primer día del mes
    anio         SMALLINT NOT NULL,
    mes          SMALLINT NOT NULL,
    trimestre    SMALLINT NOT NULL
);

CREATE TABLE IF NOT EXISTS super.dim_jurisdiccion (
    jurisdiccion_id  SMALLINT PRIMARY KEY,
    nombre           TEXT NOT NULL UNIQUE,
    region           TEXT                    -- NOA, NEA, Cuyo, Pampeana, Patagonia, GBA
);

CREATE TABLE IF NOT EXISTS super.dim_categoria (
    categoria_id  SMALLINT PRIMARY KEY,
    nombre        TEXT NOT NULL UNIQUE,
    tipo          TEXT                        -- 'básico' | 'discrecional'
);

-- Cuadros 1-2: indicadores nacionales mensuales
CREATE TABLE IF NOT EXISTS super.fact_indices (
    periodo              DATE PRIMARY KEY REFERENCES super.dim_periodo,
    idx_constante        NUMERIC,
    idx_constante_desest NUMERIC,
    idx_tendencia        NUMERIC,
    idx_corriente        NUMERIC,
    idx_precios_impl     NUMERIC
);

-- Cuadro 4: canal y medio de pago (total país)
CREATE TABLE IF NOT EXISTS super.fact_canal_pago (
    periodo      DATE REFERENCES super.dim_periodo,
    dimension    TEXT CHECK (dimension IN ('canal','medio_pago')),
    valor_dim    TEXT,
    ventas_miles NUMERIC,
    PRIMARY KEY (periodo, dimension, valor_dim)
);

-- Cuadro 5: ventas por categoría y jurisdicción
CREATE TABLE IF NOT EXISTS super.fact_ventas_categoria (
    periodo          DATE REFERENCES super.dim_periodo,
    jurisdiccion_id  SMALLINT REFERENCES super.dim_jurisdiccion,
    categoria_id     SMALLINT REFERENCES super.dim_categoria,
    ventas_miles     NUMERIC,                 -- NULL si secreto estadístico
    es_confidencial  BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (periodo, jurisdiccion_id, categoria_id)
);

-- Cuadro 6: estructura y productividad por jurisdicción
CREATE TABLE IF NOT EXISTS super.fact_estructura (
    periodo          DATE REFERENCES super.dim_periodo,
    jurisdiccion_id  SMALLINT REFERENCES super.dim_jurisdiccion,
    ventas_miles     NUMERIC,
    bocas            INTEGER,
    superficie_m2    NUMERIC,
    operaciones      BIGINT,
    PRIMARY KEY (periodo, jurisdiccion_id)
);
-- Ventas por boca / m2 / operación se recalculan en vistas (no se almacenan).
