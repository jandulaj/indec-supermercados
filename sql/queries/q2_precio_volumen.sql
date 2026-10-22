-- Pregunta 2: ¿cuánto del crecimiento nominal es precio y cuánto es volumen?
-- Promedios anuales de los índices (base 2017 = 100).
-- nominal = volumen × precio / 100 (la identidad no es exacta con promedios anuales).
-- 2026 es parcial (ene–jul): su variación contra 2025 está sesgada.

WITH anual AS (
    SELECT p.anio,
           AVG(i.idx_corriente)    AS nominal,
           AVG(i.idx_original)     AS volumen,
           AVG(i.idx_precios_impl) AS precio
    FROM super.fact_indices i
    JOIN super.dim_periodo p USING (periodo)
    GROUP BY p.anio
)
SELECT anio,
       ROUND(nominal::numeric, 1) AS nominal,
       ROUND(volumen::numeric, 1) AS volumen,
       ROUND(precio::numeric, 1)  AS precio,
       ROUND(((nominal / LAG(nominal) OVER w - 1) * 100)::numeric, 1) AS var_nominal,
       ROUND(((volumen / LAG(volumen) OVER w - 1) * 100)::numeric, 1) AS var_volumen,
       ROUND(((precio  / LAG(precio)  OVER w - 1) * 100)::numeric, 1) AS var_precio,
       ROUND(((volumen * precio / 100 / nominal - 1) * 100)::numeric, 1) AS dif_identidad_pct,
       ROUND((nominal / FIRST_VALUE(nominal) OVER w)::numeric, 1) as acu_nominal,
       ROUND(((volumen / FIRST_VALUE(volumen) OVER w - 1) * 100)::numeric, 1) AS vol_vs_2017_pct,
       ROUND((precio / FIRST_VALUE(precio) OVER w)::numeric, 1) as acu_precio
FROM anual
WINDOW w AS (ORDER BY anio)
ORDER BY anio;
