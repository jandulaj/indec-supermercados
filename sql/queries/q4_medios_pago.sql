SELECT p.anio,
       m.medio_pago,
       ROUND(100.0 * SUM(m.ventas_miles)
             / SUM(SUM(m.ventas_miles)) OVER (PARTITION BY p.anio), 1) AS participacion_pct
FROM super.fact_ventas_medio_pago m
JOIN super.dim_periodo p USING (periodo)
GROUP BY p.anio, m.medio_pago
ORDER BY p.anio, participacion_pct DESC;
