# Observatorio de Turismo Sostenible — Guatemala

Cuadro de mando interactivo para directivos y tomadores de decision del sector
turistico. Laboratorio 10 (Visualizacion Interactiva), CC3084, UVG.

El tablero responde preguntas de gestion de destino —cuanta visita hay, de
donde viene, cuanto deja, cuanta presion genera y que se espera para los
proximos 12 meses— sin exigirle al usuario formacion estadistica.

## Como correrlo

```bash
python -m venv .venv
source .venv/bin/activate          # macOS / Linux
.venv\Scripts\activate             # Windows
pip install -r requirements.txt
streamlit run app/app.py
```

La primera ejecucion genera sola los datos (`data/generar_datos.py`, semilla
fija). Para regenerarlos a mano:

```bash
python data/generar_datos.py
```

## Estructura

```
app/
  app.py              barra superior, navegacion y filtros; arma el contexto
  config.py           paleta, tipografia y hoja de estilos (lenguaje iOS)
  componentes.py      tarjetas, chips, titulos de grafica, helpers de grafico
  datos.py            carga, cache y agregaciones (el unico modulo que toca CSV)
  modelos.py          3 modelos de pronostico + 3 de clasificacion
  vistas/
    panorama.py       V1-V4    estado general (par enlazado V3 -> V1/V2)
    exploracion.py    V5-V10   mercados, estacionalidad, gasto, perfil
    sostenibilidad.py V11-V14  presion, huella y beneficio local
    modelos_vista.py  V15-V20  pronostico, matrices, ROC, aprendizaje
    guia.py           alcance, colores, glosario y limitaciones
data/
  generar_datos.py    generador reproducible de las tres tablas
  turismo_mensual.csv serie mensual por destino
  mercados.csv        llegadas por mercado emisor
  visitantes.csv      encuesta a pie de destino
docs/
  documento_diseno.md documento de diseno del laboratorio
  documento_diseno.pdf  el mismo, listo para entregar
  codebook.md         descripcion de cada columna
  generar_pdf.py      convierte cualquier .md de docs/ a PDF
```

## Documento de diseno

`docs/documento_diseno.md` es la fuente; el PDF que se entrega se regenera con:

```bash
python docs/generar_pdf.py                    # documento_diseno.md -> .pdf
python docs/generar_pdf.py docs/codebook.md   # cualquier otro .md de docs/
```

El script convierte el Markdown a HTML con la misma paleta y tipografia del
tablero y lo imprime con Chrome en modo headless, asi que no hace falta
instalar pandoc ni LaTeX. Solo necesita `pip install markdown`.

## Que trae

- **20 visualizaciones interactivas**, repartidas en cuatro secciones.
- **Dos pares enlazados por toque**: V3 (ranking) cambia V1, V2 y las secciones
  de detalle; V5 (mercados) cambia V6 (calendario de la demanda).
- **Nivel de detalle ajustable**: agregacion temporal (ano / trimestre / mes),
  profundidad del contenido (resumen ejecutivo / analisis completo) y
  profundidad jerarquica del treemap de gasto.
- **Seleccion de que graficas ver** en cada seccion.
- **Seis modelos reutilizados de los laboratorios 1 y 2**: tres de pronostico
  (tendencia + estacionalidad, Holt-Winters, SARIMA) y tres de clasificacion
  (regresion logistica, arbol de decision, k vecinos), con sus tablas
  comparativas.

## Nota sobre los datos

Las tres tablas son **sinteticas y reproducibles**: reproducen la
estacionalidad, la caida por la pandemia y los ordenes de magnitud que
reportan INGUAT y la OMT para los destinos de Guatemala, pero **no son cifras
oficiales**. Para enchufar datos reales basta con reemplazar los CSV
respetando los nombres de columna de `docs/codebook.md`; ningun otro archivo
necesita cambios.
