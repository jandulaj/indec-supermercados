SELECT p.anio, c.nombre, c.tipo,
       ROUND(100.0 * SUM(f.ventas_miles)
             / SUM(SUM(f.ventas_miles)) OVER (PARTITION BY p.anio), 1) AS participacion_pct
FROM super.fact_ventas_categoria f
JOIN super.dim_periodo      p USING (periodo)
JOIN super.dim_categoria    c USING (categoria_id)
JOIN super.dim_jurisdiccion j USING (jurisdiccion_id)
WHERE j.es_total            -- solo "Total del país": dato completo, sin secreto estadístico
  AND NOT c.es_total        -- excluye la categoría "Total"
GROUP BY p.anio, c.nombre, c.tipo
ORDER BY p.anio, participacion_pct DESC;