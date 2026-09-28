# Preguntas de negocio

Contexto: se analiza el desempeño del canal supermercados en Argentina (2017–2026) desde la óptica de un **retailer o proveedor de consumo masivo** que necesita decidir dónde crecer, qué surtido priorizar y cómo cobrar.

| # | Pregunta | Datos | Métrica clave | Gráfico propuesto |
|---|---|---|---|---|
| 1 | **¿Cuánto crecieron o cayeron realmente las ventas?** ¿Cuáles fueron los años de contracción y de recuperación, y dónde estamos hoy frente al pico? | Cuadro 1 (desestacionalizada) | Índice real base 2017=100, var. i.a., distancia al máximo | Línea: serie original vs desestacionalizada |
| 2 | **¿Cuánto del crecimiento nominal es precio y cuánto es volumen?** | Cuadro 2 | Índice corriente vs constante; índice de precios implícitos | Líneas en escala log / área de brecha |
| 3 | **¿Cómo cambió la canasta?** ¿Los consumidores migraron hacia básicos (almacén, limpieza) y resignaron discrecionales (electrónica, indumentaria) en las crisis? | Cuadro 5 (total país) | Participación % de cada grupo en las ventas, por año | Área 100 % apilada o *slope chart* 2017 vs 2025 |
| 4 | **¿Cómo pagan los clientes?** ¿Qué tan rápido cayó el efectivo y creció "otros medios" (billeteras / QR)? | Cuadro 4 | Participación % por medio de pago | Área 100 % apilada |
| 5 | **¿El canal online llegó para quedarse?** ¿Qué pasó después del salto de 2020? | Cuadro 4 | % ventas online | Línea con anotación de la pandemia |
| 6 | **¿Qué provincias ganan y cuáles pierden?** | Cuadros 5–6 deflactados | Var. real acumulada por jurisdicción | Barras horizontales ordenadas |
| 7 | **¿Hay diferencias de productividad entre jurisdicciones?** | Cuadro 6 | Ventas reales por m², por boca y ticket promedio real (ventas / operación) | Mapa de calor jurisdicción × año |
| 8 | **¿Cuál es el patrón estacional?** ¿Qué tan fuerte es el pico de diciembre y el valle de febrero? | Cuadro 1 (original vs desest.) | Factor estacional por mes | Barras por mes / heatmap año × mes |

**Alcance para el README:** preguntas 1, 2, 3, 4 y 6 (5 gráficos). Las 5, 7 y 8 quedan para el dashboard de Power BI, donde el filtrado por jurisdicción y período agrega más valor.

## Supuestos y limitaciones (a declarar en el README)
- El deflactor (índice de precios implícitos) es **nacional**; aplicarlo a provincias y categorías es una aproximación.
- Los grupos con secreto estadístico (`s`) se excluyen de rankings provinciales; no se imputan.
- La encuesta cubre supermercados (empresas medianas y grandes), no almacenes de barrio ni mayoristas: no es "todo el consumo".
