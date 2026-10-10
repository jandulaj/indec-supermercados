-- q1a: evolución anual del volumen de ventas
WITH anual AS (
    SELECT EXTRACT(YEAR FROM periodo)::int AS anio,
           COUNT(*)                        AS meses,
           AVG(idx_original)               AS idx_prom
    FROM super.fact_indices
    GROUP BY 1
)
SELECT anio, meses,
       ROUND(idx_prom::numeric, 1) AS idx_prom,
       ROUND(((idx_prom / LAG(idx_prom) OVER (ORDER BY anio) - 1) * 100)::numeric, 1) AS var_anual_pct
FROM anual
ORDER BY anio;

-- q1b: pico, piso y distancia actual al pico (serie desestacionalizada)
WITH pico   AS (SELECT periodo, idx_desest FROM super.fact_indices ORDER BY idx_desest DESC LIMIT 1),
     piso   AS (SELECT periodo, idx_desest FROM super.fact_indices ORDER BY idx_desest ASC  LIMIT 1),
     ultimo AS (SELECT periodo, idx_desest FROM super.fact_indices ORDER BY periodo   DESC LIMIT 1)
SELECT p.periodo AS mes_pico,   ROUND(p.idx_desest::numeric, 1) AS idx_pico,
       s.periodo AS mes_piso,   ROUND(s.idx_desest::numeric, 1) AS idx_piso,
       u.periodo AS ultimo_mes, ROUND(u.idx_desest::numeric, 1) AS idx_ultimo,
       ROUND(((u.idx_desest / p.idx_desest - 1) * 100)::numeric, 1) AS dist_pico_pct
FROM pico p CROSS JOIN piso s CROSS JOIN ultimo u;
