# Fuente de datos

**Encuesta de Supermercados – INDEC** (Dirección Nacional de Estadísticas Económicas).

- Página: https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-1-34
- Archivo: https://www.indec.gob.ar/ftp/cuadros/economia/serie_supermercados.xlsx
- Versión descargada: publicada por el INDEC el 23/09/2026 (Last-Modified del servidor), datos **enero 2017 – julio 2026** (115 meses).
- Periodicidad: mensual. Base de los índices: 2017 = 100.
- Metodología: https://www.indec.gob.ar/ftp/cuadros/economia/nota_metodologica_supermercados.pdf

> Hay una serie histórica anterior (`sh_super_mayoristas.xls`, metodología previa, hasta 2022) que **no** se usa: no es comparable con la base 2017.

## Hojas del Excel

| Hoja | Contenido | Unidad | Columnas |
|---|---|---|---|
| Índice | Índice de cuadros | – | – |
| Cuadro 1 | Índice de ventas a **precios constantes**: serie original, desestacionalizada y tendencia-ciclo, con variaciones % | Número índice / % | ~10 |
| Cuadro 2 | Índice a precios corrientes, a precios constantes e **índice de precios implícitos**, con variaciones % | Número índice / % | ~11 |
| Cuadro 3. | Ventas totales a precios corrientes y constantes, variación i.a. | **Millones** de pesos / % | 6 |
| Cuadro 4. | Ventas por **canal** (salón / online) y **medio de pago** (efectivo, débito, crédito, otros) | **Miles** de pesos | 10 |
| Cuadro 5. | Ventas por **grupo de artículos** (12) × **jurisdicción** (24 + total país) | Miles de pesos | 338 |
| Cuadro 6. | Ventas, cantidad de **bocas**, **superficie** (m²), **operaciones**, ventas por boca / m² / operación × jurisdicción | Miles de pesos, unidades, m², pesos | 208 |

## Problemas de calidad a resolver en la limpieza (pandas)

1. **Encabezados multinivel con celdas combinadas**: 2–3 filas de encabezado (jurisdicción → variable → unidad). Hay que hacer *forward fill* horizontal y aplanar.
2. **Formato ancho → largo**: Cuadros 5 y 6 tienen una columna por jurisdicción × variable. Se pasan a formato *tidy* (`periodo, jurisdiccion, categoria, valor`).
3. **Columnas separadoras vacías** entre bloques de jurisdicciones.
4. **Marcadores no numéricos**:
   - `s` = dato bajo **secreto estadístico** (690 celdas en Cuadro 5) → `NaN` + flag `es_confidencial`. No imputar.
   - `…` = dato no disponible (variaciones del primer año, 24 celdas en Cuadro 1) → `NaN`.
5. **Filas de notas y fuente** al pie de cada hoja → descartar.
6. **Unidades mezcladas**: millones (Cuadro 3), miles (Cuadros 4–6) y pesos (ventas por m² y por operación). Normalizar a pesos o documentar.
7. **Pesos nominales con alta inflación**: comparar montos en el tiempo exige deflactar. El Cuadro 2 trae el índice de precios implícitos del sector → se usa como deflactor. Para provincias es una **aproximación** (el deflactor es nacional).
8. Nombres de jurisdicción con espacios finales / texto truncado (p. ej. "24 partidos del Gran Buenos Aires ") → `strip()` y tabla de códigos.
