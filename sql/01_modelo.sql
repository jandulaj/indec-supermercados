-- =====================================================================
-- Modelo dimensional (schema "super") construido a partir de staging.
-- Se ejecuta completo en cada carga (DROP + CREATE): es idempotente.
-- =====================================================================

CREATE SCHEMA IF NOT EXISTS super;

DROP TABLE IF EXISTS super.fact_ventas_categoria, super.fact_ventas_medio_pago,
                     super.fact_ventas_canal, super.fact_indices,
                     super.dim_categoria, super.dim_jurisdiccion, super.dim_periodo;

-- ---------------------------------------------------------------------
-- Dimensiones
-- ---------------------------------------------------------------------
CREATE TABLE super.dim_periodo AS
SELECT DISTINCT
       periodo::date                      AS periodo,
       EXTRACT(YEAR    FROM periodo)::int AS anio,
       EXTRACT(MONTH   FROM periodo)::int AS mes,
       EXTRACT(QUARTER FROM periodo)::int AS trimestre
FROM stg.indices_ventas;
ALTER TABLE super.dim_periodo ADD PRIMARY KEY (periodo);

CREATE TABLE super.dim_jurisdiccion AS
SELECT ROW_NUMBER() OVER (ORDER BY (nombre <> 'Total del país'), nombre)::smallint AS jurisdiccion_id,
       nombre,
       CASE WHEN nombre IN ('24 partidos del Gran Buenos Aires', 'Resto de Buenos Aires')
            THEN 'Buenos Aires'
            WHEN nombre LIKE 'Tierra del Fuego%' THEN 'Tierra del Fuego'
            ELSE nombre END                                        AS provincia,
       CASE
            WHEN nombre = 'Total del país' THEN 'Total'
            WHEN nombre IN ('Ciudad Autónoma de Buenos Aires',
                            '24 partidos del Gran Buenos Aires')   THEN 'GBA'
            WHEN nombre IN ('Resto de Buenos Aires', 'Córdoba', 'Entre Ríos',
                            'La Pampa', 'Santa Fe')                THEN 'Pampeana'
            WHEN nombre IN ('Catamarca', 'Jujuy', 'La Rioja', 'Salta',
                            'Santiago del Estero', 'Tucumán')      THEN 'NOA'
            WHEN nombre IN ('Chaco', 'Corrientes', 'Formosa', 'Misiones') THEN 'NEA'
            WHEN nombre IN ('Mendoza', 'San Juan', 'San Luis')     THEN 'Cuyo'
            WHEN nombre IN ('Chubut', 'Neuquén', 'Río Negro', 'Santa Cruz')
                 OR nombre LIKE 'Tierra del Fuego%'                THEN 'Patagonia'
       END                                                          AS region,
       nombre = 'Total del país'                                    AS es_total
FROM (SELECT DISTINCT jurisdiccion AS nombre FROM stg.ventas_categoria_jurisdiccion) j;
ALTER TABLE super.dim_jurisdiccion ADD PRIMARY KEY (jurisdiccion_id);

CREATE TABLE super.dim_categoria AS
SELECT ROW_NUMBER() OVER (ORDER BY (nombre <> 'Total'), nombre)::smallint AS categoria_id,
       nombre,
       CASE
            WHEN nombre = 'Total' THEN 'Total'
            WHEN nombre LIKE 'Indumentaria%' OR nombre LIKE 'Electrónicos%' THEN 'Discrecional'
            WHEN nombre = 'Otros' THEN 'Otros'
            ELSE 'Básico'
       END                                                          AS tipo,
       nombre = 'Total'                                             AS es_total
FROM (SELECT DISTINCT categoria AS nombre FROM stg.ventas_categoria_jurisdiccion) c;
ALTER TABLE super.dim_categoria ADD PRIMARY KEY (categoria_id);

-- ---------------------------------------------------------------------
-- Hechos
-- ---------------------------------------------------------------------
CREATE TABLE super.fact_indices AS
SELECT v.periodo::date AS periodo,
       v.idx_original, v.idx_desest, v.idx_tendencia,
       v.var_ia, v.var_acum, v.var_mensual_desest,
       p.idx_corriente, p.idx_precios_impl, p.var_ia_precios_impl
FROM stg.indices_ventas v
JOIN stg.indices_precios p USING (periodo);
ALTER TABLE super.fact_indices ADD PRIMARY KEY (periodo),
    ADD FOREIGN KEY (periodo) REFERENCES super.dim_periodo;

CREATE TABLE super.fact_ventas_canal AS
SELECT periodo::date AS periodo, canal, ventas_miles::numeric(18,3) AS ventas_miles
FROM stg.ventas_canal;
ALTER TABLE super.fact_ventas_canal ADD PRIMARY KEY (periodo, canal),
    ADD FOREIGN KEY (periodo) REFERENCES super.dim_periodo;

CREATE TABLE super.fact_ventas_medio_pago AS
SELECT periodo::date AS periodo, medio_pago, ventas_miles::numeric(18,3) AS ventas_miles
FROM stg.ventas_medio_pago;
ALTER TABLE super.fact_ventas_medio_pago ADD PRIMARY KEY (periodo, medio_pago),
    ADD FOREIGN KEY (periodo) REFERENCES super.dim_periodo;

-- Los totales (país / categoría) quedan en la tabla: se filtran con dim.es_total
CREATE TABLE super.fact_ventas_categoria AS
SELECT s.periodo::date AS periodo, j.jurisdiccion_id, c.categoria_id,
       s.ventas_miles::numeric(18,3) AS ventas_miles, s.es_confidencial       
FROM stg.ventas_categoria_jurisdiccion s
JOIN super.dim_jurisdiccion j ON j.nombre = s.jurisdiccion
JOIN super.dim_categoria    c ON c.nombre = s.categoria;
ALTER TABLE super.fact_ventas_categoria ADD PRIMARY KEY (periodo, jurisdiccion_id, categoria_id),
    ADD FOREIGN KEY (periodo)         REFERENCES super.dim_periodo,
    ADD FOREIGN KEY (jurisdiccion_id) REFERENCES super.dim_jurisdiccion,
    ADD FOREIGN KEY (categoria_id)    REFERENCES super.dim_categoria;

-- ---------------------------------------------------------------------
-- Seguridad (Supabase): RLS activado y sin políticas = la API pública
-- (claves anon / authenticated) no puede leer estas tablas.
-- El usuario "postgres" (dueño de las tablas, el que usan Python y
-- Power BI) no se ve afectado.
-- ---------------------------------------------------------------------
ALTER TABLE super.dim_periodo            ENABLE ROW LEVEL SECURITY;
ALTER TABLE super.dim_jurisdiccion       ENABLE ROW LEVEL SECURITY;
ALTER TABLE super.dim_categoria          ENABLE ROW LEVEL SECURITY;
ALTER TABLE super.fact_indices           ENABLE ROW LEVEL SECURITY;
ALTER TABLE super.fact_ventas_canal      ENABLE ROW LEVEL SECURITY;
ALTER TABLE super.fact_ventas_medio_pago ENABLE ROW LEVEL SECURITY;
ALTER TABLE super.fact_ventas_categoria  ENABLE ROW LEVEL SECURITY;
