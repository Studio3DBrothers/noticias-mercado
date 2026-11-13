# Código de los informes de Análisis fundamental

Base para la tarea "NO BORRAR · Análisis 3:00". Es el código con el que se armaron los informes aprobados (AAPL, MSFT, KO, NU).

- `sec.py`: lee el companyfacts de la SEC (anual, instante, últimos 12 meses, último trimestre).
- `trim.py`: series trimestrales y de 12 meses.
- `calc.py`: métricas, 10 años, semáforo y puntaje (criterios fijos).
- `sankey2.py`: el gráfico de flujo A4.
- `salud.py`: las tarjetas de Salud financiera.
- `informe.py`: colores, formato de números y controles.
- `build3.py`: arma datos.json, informe.pdf, hoja-1.jpg y hoja-2.jpg. Tiene adentro los datos del día de los informes de prueba: PX, RATIO, FECHA y DATOS.
- `datos_in.py`: los textos y números de cada empresa (dict E), en el formato que espera build3.py. Trae como ejemplo AAPL, MSFT, KO y NU (banco).

Uso:
1. Bajá los datos a `AF_BASE` (por defecto `./trabajo/`): raw/cf_<CIK>.json, raw/px_<T>.json, raw/live_cedears.json y calc.json.
2. Escribí la entrada de cada empresa en datos_in.py.
3. Ajustá PX, RATIO, FECHA y DATOS en build3.py.
4. Corré `AF_REPO=<ruta del repo>/ python3 build3.py`.
