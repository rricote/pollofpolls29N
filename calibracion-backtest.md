# Backtest y calibración del reparto provincial (9-nov-2026)

Datos: resultados provinciales del Ministerio del Interior (ficheros 07 y 08 de 2011, 2015, 2016, abril 2019, noviembre 2019 y 2023), agrupados en PP, PSOE, Vox, Cs, UPyD, Izquierda (Podemos, IU, ECP, Mareas, Compromís, Más País, Sumar), ERC, Junts/CiU/CDC, Bildu, PNV, BNG, CC, UPN, otros y blanco. Los totales por grupo coinciden con los oficiales (p. ej. 2023: PP 137, PSOE 121, Vox 33, Sumar 31).

## Qué se ha medido
Backtest 3: se parte de una elección A, se da al modelo el resultado nacional real de la elección B y se mide cuánto falla al repartirlo por provincias con el método actual (voto de A, factor regional, raking a la media nacional, D'Hondt con 3 %). Tránsitos: 2015→16, 2016→abril 19, abril 19→nov 19, nov 19→23, y los de más largo plazo 2016→nov 19, 2015→abril 19, 2011→15 y 2011→16.

Este primer backtest mide solo el error de la traducción territorial (se da al modelo el resultado nacional real). El error de las propias encuestas se mide aparte, más abajo, con las encuestas finales de abril 2019, noviembre 2019 y 2023 (tablas nacionales de Wikipedia).

## Resultados del método actual
- Solo con el dato nacional: el error medio provincial de voto es 2,3 puntos y se asignan mal 29 de 350 escaños.
- Con información regional (peso 0,6 hacia el resultado real de cada comunidad): 1,35 puntos y 22 escaños. La información regional es lo que más mejora el modelo; por eso importa el tamaño de las muestras regionales del CIS y del 40dB.
- Incluso con la comunidad conocida, 20 escaños de media quedan mal asignados: es el límite de este método.

## Backtest 1: tendencia previa (A−1 → A)
Añadir una corrección por la tendencia anterior de cada provincia no mejora el error (el mejor valor del coeficiente es 0). Descartado.

## Backtest 2: perfil territorial
Se probaron un exponente sobre la cuota provincial de A, la media histórica de cada provincia y una regresión con la cuota de los demás partidos en la provincia (regresión con penalización, validación dejando un tránsito fuera).
- El exponente sí aporta algo, pero depende de la dirección del cambio: los partidos que suben se reparten de forma más plana que su voto de partida (exponente 0,7 a 0,9 en la validación), y los que bajan o se mantienen se reparten proporcionalmente (exponente 1,0 a 1,1).
- La regresión con las cuotas de los demás partidos mejora el error un 4-5 % pero no los escaños y no aguanta la validación cruzada. Descartada.

## Calibración aplicada al modelo
1. Exponente 0,8 sobre la cuota provincial de 2023 para PP, PSOE, Vox, SALF (que copia a Vox) y Frente Amplio solo cuando su media nacional supera a la de 2023; si baja, proporcional. Hoy solo afecta a Vox y SALF. Ganancia en el backtest: error medio de 1,35 a 1,28-1,31 puntos y de 21,6 a 20,9 escaños; en los tránsitos con poco movimiento (2015→16, abril→noviembre 2019) empeora ligeramente. La mejora es modesta.
2. Dispersión regional por partido (el valor que se usa para encoger el factor regional, antes 0,18 para todos): PP 0,11, PSOE 0,10, Vox 0,16, Frente Amplio 0,18. Salen del error del reparto regional cuando solo se conoce el dato nacional (0,096 a 0,108 en PP y PSOE, 0,13 a 0,16 en Vox con base real, 0,18 en la izquierda).
3. Ruido provincial por partido (antes 0,05 para todos): PP 0,06, PSOE 0,08, Vox 0,08, Frente Amplio y Podemos 0,10, ERC y Junts 0,15, BNG 0,12, CC 0,15, Bildu 0,06, PNV 0,04. Es el error del voto provincial una vez conocida la comunidad.

## Error nacional de las encuestas (sdSys)
Se agregaron las encuestas de las últimas semanas de cada elección (media por casa con vida media de 14 días, después entre casas con peso raíz de la muestra, sin efectos casa) y se comparó con el resultado. Errores de la media (estimada menos real, en puntos):
- 2023: PSOE -3,2, PP +0,6, Vox +0,8, Sumar +1,1.
- Noviembre 2019: PSOE -0,7, PP +0,2, Vox -2,0, Unidas Podemos -0,5, Cs +2,3.
- Abril 2019: PSOE +0,1, PP +3,6, Vox +0,7, Unidas Podemos -0,6, Cs -1,0.

El error absoluto medio es 1,25 puntos. Expresado en la escala del modelo (error dividido por la raíz del voto en %) el valor implícito de sdSys es 0,42, frente al 0,28 que se usaba; son solo 14 observaciones y sus errores están correlacionados, pero indican que los rangos eran demasiado estrechos. **sdSys pasa de 0,28 a 0,40** (algo por debajo de 0,42 porque el modelo corrige efectos casa y usa microdatos, que el backtest no replica). En los tres casos el PSOE quedó subestimado o el PP sobreestimado (PP +3,6 en abril 2019, PSOE -3,2 en 2023), pero con tres elecciones no se aplica ninguna corrección de sesgo.

## Efecto en la proyección de hoy
La estimación central casi no cambia: PP 129, PSOE 108 (antes 109), Vox 69 y Frente Amplio + confluencias 12-13. Los rangos del 90 % se ensanchan bastante por el nuevo sdSys: PP 113-145, PSOE 94-123, Vox 56-84, Frente Amplio + confluencias 6-20. PSOE, Frente Amplio y socios llegan a 176 en el 1 % de las simulaciones.

## Recalibración provincial (9-nov-2026, 2.ª pasada)
Motivo: resultados poco realistas, como Vox primera fuerza en una provincia canaria.
- **Causa raíz**: Vox no se presentó en Santa Cruz de Tenerife en 2023, así que su base provincial era 0 y se imputaba mal; eso inflaba el factor regional de Canarias (Vox 1,39). Ahora Tenerife usa una base ajustada (Vox 11,7 %, resto reescalado) y el factor de Canarias baja a 1,09.
- **Factores regionales agrupados**: se combinan CIS 3582, CIS 3577 y 40dB (muestras regionales con n≥20) contra la base ajustada; el CEO usa la misma base.
- **Perfiles propios**: SALF usa su resultado de las europeas 2024 por provincia (donde no hay dato, copia a Vox); Adelante Andalucía usa su resultado de las andaluzas 2026 por provincia, relativo a la media ponderada.
- **Descartado**: usar las desviaciones de las europeas 2024 como señal regional (no predicen las de las generales), tendencia previa, efectos provinciales persistentes (los residuos no se repiten entre elecciones) y sobredispersión del ruido regional de las encuestas.
- **Resultado**: PP 129 [114-147], PSOE 107 [94-122], Vox 69 [55-82], Frente Amplio + confluencias 12. Las Palmas: PSOE 25,7 / PP 24,8 / Vox 23,0. S.C. Tenerife: PP 30,3 / PSOE 23,3 / Vox 19,5.
- Versión de datos '11-20261109' (reinicia las ediciones locales guardadas en el navegador).

## Autonómicas 2019-2026 y europeas provincia a provincia (9-nov-2026, 3.ª pasada)
Datos: todas las autonómicas desde 2019 (incluidas Extremadura dic. 2025, Aragón feb. 2026, Castilla y León mar. 2026 y Andalucía may. 2026) y las europeas de 2019 y 2024 por provincia. Se mide si el patrón provincial o regional de esas elecciones predice el cambio posterior en las generales, con validación dejando una comunidad fuera.

**1. Cambio provincial dentro de la comunidad: no ayuda.** Añadir el cambio autonómico (o el de las europeas) al reparto provincial no reduce el error fuera de muestra: PP 0,070 → 0,068, PSOE 0,061 → 0,061, Vox 0,122 → 0,117. Con las europeas 2019 (abril → noviembre 2019) tampoco (PP 0,050 → 0,049, PSOE 0,038, Vox 0,050 → 0,053). El patrón de las europeas 2024 correlaciona mucho con las generales 2023 (0,7-0,8), pero eso es porque ya recoge lo ocurrido en 2023, no porque anticipe cambios futuros. La reversión a la media dentro de la comunidad solo aparece en noviembre 2019 → 2023 y no se repite en las demás transiciones. Descartado.

**2. Nivel de la comunidad frente a España: sí ayuda al PP.** Con 15-17 comunidades, el cambio de la razón región/nacional en la autonómica predice el de las generales: PP error 0,108 → 0,060 (correlación 0,77), PSOE 0,147 → 0,138, Vox sin mejora. Muestra pequeña, pero el efecto del PP es estable con varias formulaciones.

**Aplicado:** prior del factor regional en Andalucía, Aragón, Castilla y León y Extremadura (las únicas con autonómica en 2025-26): el factor estimado con las encuestas se encoge hacia w·(z+dreg)/2 en vez de hacia 0, con w = 0,30 PP y 0,20 PSOE (Vox 0). Para el PP en esas comunidades la dispersión regional baja de 0,11 a 0,07. Los priors valen entre -0,05 y +0,06 en logaritmo (1-6 % del voto relativo). Efecto en la proyección: PP 129, PSOE 108 (antes 107), BNG 1 (antes 2); el resto igual. Se usa como referencia nacional de las autonómicas 2025-26 la media actual de encuestas (PP 30,9, PSOE 26,8).

**Comprobación con las autonómicas 2026:** dentro de cada comunidad, el reparto actual del modelo se mueve poco (±0,03 en logaritmo) frente a ±0,1-0,2 en las autonómicas (Vox sube más en Huesca, Teruel, Almería, Huelva y Soria). Con la evidencia del backtest, ese movimiento adicional no es predecible, así que se deja a la incertidumbre provincial de la simulación.

## Qué queda por hacer
- Ampliar el backtest de encuestas con 2015, 2016 y 2011 para tener más de 14 observaciones.
- Calibrar los partidos regionales con más datos (solo hay cuatro provincias catalanas y los cambios de 2017 distorsionan ERC y Junts).
- Los ficheros y scripts del backtest están en la carpeta `backtest` (load.py, build_hist.py, bt.py, fit.py, fit2.py, hist.json, bt_report.txt, polls_hist.py, poll_err.py, poll_err.txt).
