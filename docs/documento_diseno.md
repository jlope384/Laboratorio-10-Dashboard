# Documento de diseno
## Observatorio de Turismo Sostenible — Guatemala

**Laboratorio 10 · Visualizacion Interactiva · CC3084 · UVG**
**Fecha:** 25 de octubre de 2026

## 1. Alcance del tablero

**A quien va dirigido.** Directivos y tomadores de decision del sector
turistico —direccion de INGUAT, mancomunidades, camaras de turismo, gerencias
de destino— que no necesariamente tienen formacion estadistica.

**Que cubre.**

- 7 destinos de Guatemala: Antigua Guatemala, Lago de Atitlan, Tikal y Peten,
  Rio Dulce y Livingston, Quetzaltenango, Semuc Champey y Ciudad de Guatemala.
- Serie mensual 2017-2025 de demanda, economia, empleo y huella ambiental.
- Encuesta a pie de destino 2023-2025 (9 000 cuestionarios) para el perfil del
  visitante.
- Pronostico de demanda a 12 meses y clasificacion de visitantes promotores,
  **reutilizando** los modelos de los laboratorios 1 y 2 del curso.

**Que NO cubre (limites declarados en la propia aplicacion).**

- No sustituye un estudio de impacto ambiental ni una evaluacion de capacidad
  de carga: la capacidad de carga entra como parametro, no se calcula aqui.
- No mide efectos causales de politicas. Todo lo que muestra son
  **asociaciones**.
- No contiene datos de empresas individuales.
- Los pronosticos proyectan la continuidad del patron historico: no incorporan
  nuevas rutas aereas, crisis sanitarias ni campanas de promocion.

**Origen de los datos.** Las tres tablas son sinteticas y reproducibles
(`data/generar_datos.py`, semilla fija). Reproducen estacionalidad, caida por
pandemia y ordenes de magnitud reportados por INGUAT y la OMT, pero no son
cifras oficiales. La capa de datos esta aislada en `app/datos.py`: al sustituir
los CSV por registros oficiales con las mismas columnas (`docs/codebook.md`),
el tablero funciona sin ningun otro cambio.

---

## 2. Preguntas exploratorias que dieron origen al diseno

El tablero no se organizo por tipo de dato sino por **decision que habilita**.
Estas son las preguntas que el equipo planteo primero, y la navegacion es su
consecuencia directa.

### Bloque A — "¿Como vamos?" → seccion **Panorama**

1. ¿Cuanta visita y cuanta derrama tuvimos en el periodo, y como se compara con
   el periodo anterior equivalente?
2. ¿Que destinos concentran la visita y cuales se estan acercando a su
   capacidad de carga?
3. ¿Como se mueve la demanda en el tiempo y como se compara un destino concreto
   con el conjunto?
4. ¿Que destinos reciben mucha gente y cuales reciben gente que gasta mas?

### Bloque B — "¿De donde viene y en que gasta?" → seccion **Explorar los datos**

5. ¿En que mercados emisores se concentra la demanda?
6. ¿En que meses conviene concentrar promocion, personal y mantenimiento, y
   cambia ese calendario segun el mercado?
7. ¿Que parte de la derrama queda en alojamiento, alimentacion, transporte,
   actividades y artesanias?
8. ¿Llenar mas los hoteles viene acompanado de mayor gasto por visitante?
9. ¿Que segmento de visitante deja mas gasto y cual se queda mas noches?
10. ¿Que tipo de alojamiento domina en cada destino?

### Bloque C — "¿A que costo?" → seccion **Sostenibilidad**

11. ¿Crece la huella ambiental al mismo ritmo que la visita?
12. ¿Que destinos estan por encima de su capacidad de carga estimada?
13. ¿En que dimensiones de sostenibilidad gana y pierde cada destino?
14. ¿El turismo esta dejando empleo local y empujando la certificacion?

### Bloque D — "¿Que esperar y a quien atender?" → seccion **Modelos**

15. ¿Cuanta visita se espera en los proximos 12 meses y con que margen?
16. ¿Que tan confiable es cada modelo cuando se le pone a prueba contra meses
   que no vio al entrenar?
17. De cada visitante que llega, ¿quien termina recomendando el destino?
18. ¿Sobre que palancas puede actuar la gestion del destino para ganar
   promotores?

La **quinta seccion, Guia de lectura**, nacio de una pregunta distinta, de
usabilidad: "si abro esto sin que nadie me lo explique, ¿entiendo que significa
cada color y cada termino?".

---

## 3. Herramienta, lenguaje y framework

### Decision: Python + Streamlit, con Plotly y Altair para los graficos

**Por que Streamlit y no las otras opciones permitidas.**

| Opcion | Por que se descarto |
|---|---|
| R Shiny | El equipo trabajo los laboratorios 1 y 2 en Python (pandas, statsmodels, scikit-learn). Reescribir los modelos en R para este laboratorio contradice la instruccion de **reutilizar** los modelos ya construidos y agrega una fuente de error sin aportar nada al tablero. |
| Plotly Dash | Da mas control sobre el layout, pero exige escribir a mano todo el ciclo de callbacks. Para un tablero de 20 visualizaciones con filtros globales eso es mucho codigo de infraestructura y poco codigo de analisis, con un calendario de dos semanas. |
| Voila / Panel | Voila publica un notebook: mezcla analisis y presentacion, y el resultado hereda la estetica de Jupyter, poco apropiada para directivos. Panel es potente pero el equipo no lo conoce. |
| **Streamlit** | **Elegido.** Mismo lenguaje que los modelos ya entrenados; el estado y el re-render son automaticos, asi que el codigo que escribimos es el del analisis; `st.cache_data` evita recalcular modelos en cada interaccion; y permite inyectar CSS propio, que es lo que hace posible el lenguaje visual descrito en la seccion 4. |

**Por que dos librerias de graficos.** Plotly cubre 18 de las 20
visualizaciones: mapas, dobles ejes, treemaps, radares, matrices y subplots con
una sola API y tooltips ricos. Las dos graficas que **originan** un enlace (V3 y
V5) se hicieron en Altair porque, en la version de Streamlit usada, el evento de
seleccion de Plotly no llega al servidor y el de Altair si. Es decir: la
eleccion no es estetica, es la unica via por la que el toque del usuario sobre
una barra puede cambiar otra grafica. Las dos librerias comparten paleta y
tipografia, de modo que la diferencia es invisible para el usuario.

**Dependencias.** `streamlit`, `plotly<7`, `altair`, `pandas`, `numpy`,
`scikit-learn`, `statsmodels`. Todas libres y de codigo abierto. `plotly` se fija
por debajo de 7 porque a partir de esa version Streamlit deja de entregar los
eventos de seleccion.

---

## 4. Paleta de colores, tipografia e interfaz

### 4.1 Paleta

Se parte de la paleta institucional del equipo (esquema principal de 8 colores,
familias extendidas de rosas, azules y morados, y el semaforo de 3 colores). Es
una paleta de **alto croma**, lo que la vuelve memorable pero tambien ruidosa si
se aplica sin reglas. Las tres reglas que la hacen funcionar en un tablero:

**Regla 1 — Un color, un significado, en toda la aplicacion.**

| Color | Hex | Significado fijo |
|---|---|---|
| Azul | `#4361EE` | Demanda: visitantes, llegadas, volumen |
| Naranja | `#FFA630` | Economia: gasto, ingresos, empleo |
| Verde | `#60A125` | Sostenibilidad en buen estado / resultado favorable |
| Rosa | `#F72585` | Presion, alerta, resultado desfavorable |
| Morado | `#A2158D` | Estimaciones y pronosticos de modelos |
| Celeste | `#4CC9F0` | Serie de apoyo o contexto |
| Violeta | `#4D0A99` | Navegacion y encabezados |
| Salmon | `#FFA5A3` | Categoria complementaria de baja prioridad |

Si el azul es demanda en la portada, es demanda en la seccion de modelos. El
usuario aprende el codigo una vez.

**Regla 2 — El color saturado se reserva para el dato.** Fondo, tarjetas,
rejilla, separadores y texto usan neutros derivados de la familia azul de la
paleta (`#B5BDE3`, `#2E3B73`), no los colores del esquema principal. Asi la
tinta de color no compite con la informacion. Contrastes sobre blanco: texto
principal `#2E3B73` 8.9:1 y texto secundario `#5A6798` 5.1:1, ambos por encima
del minimo AA (4.5:1).

**Regla 3 — Ninguna lectura depende solo del color.** La paleta no es
segura para daltonismo —azul `#4361EE` y morado `#A2158D` se confunden bajo
deuteranopia, y rosa `#F72585` con verde `#60A125` bajo protanopia severa—, asi
que cada grafica agrega un canal redundante:

- El semaforo de presion (V12) escribe la palabra: "Holgura", "Al limite",
  "Saturacion".
- Las series y barras llevan etiqueta directa o leyenda con nombre.
- Las estimaciones se distinguen ademas por **linea punteada**, no solo por ser
  moradas.
- Las magnitudes se escriben como texto sobre la barra en V3 y V5.

**Escalas derivadas.**

- *Secuencial* (una sola magnitud, de menos a mas): familia azul,
  `#EDEFFA → #B5BDE3 → #7487DB → #4361EE → #2E3B73 → #0B2183`. Se usa en el
  mapa de calor (V6), el treemap (V7) y las matrices de confusion (V17).
- *Divergente con umbral* (presion turistica): el semaforo de la paleta,
  verde → naranja → rosa, con el 1.0 marcado explicitamente. Se usa en V1 y V12.
- *Categorica* (destinos, mercados, categorias de gasto): el esquema principal
  ordenado alternando familias, para que dos categorias contiguas nunca sean
  vecinas en tono.

Cada destino tiene su color fijo en todo el tablero, y cada modelo tambien.

### 4.2 Tipografia

Pila del sistema: `-apple-system, BlinkMacSystemFont, "SF Pro Text", Inter,
"Helvetica Neue", Arial`. En equipos Apple se resuelve a **SF Pro**, la fuente
que el usuario ya lee en su telefono; en el resto, a Inter, que comparte
proporciones y tiene cifras tabulares. Ventajas: coste de aprendizaje cero,
excelente legibilidad en cifras y ninguna descarga bloqueante.

Escala tipografica (patron *Large Title* de iOS):

| Elemento | Tamano | Peso |
|---|---|---|
| Titulo de seccion | 2.05 rem | 700 |
| Cifra de tarjeta (KPI) | 1.75 rem, cifras tabulares | 700 |
| Titulo de visualizacion | 1.02 rem | 650 |
| Pregunta de gestion | 0.84 rem | 400, color secundario |
| Rotulo de grupo | 0.76 rem, mayusculas, +5% tracking | 600 |
| Nota al pie / lectura | 0.86 rem | 400 |

Las cifras usan `font-variant-numeric: tabular-nums` para que las columnas de
numeros queden alineadas, y los miles se separan con espacio fino.

### 4.3 Bosquejo de la interfaz y navegacion

Se descarto el panel lateral clasico de Streamlit por dos razones: come ancho
util en una pantalla llena de graficas y no se parece a nada que el usuario use
a diario. En su lugar, **patrones de iOS**, que el directivo ya domina de su
telefono:

```
┌──────────────────────────────────────────────────────────────────────┐
│ 🧭  Observatorio de Turismo Sostenible · Panorama        [nav bar]   │  fija, translucida
├──────────────────────────────────────────────────────────────────────┤
│ [ Panorama | Explorar | Sostenibilidad | Modelos | Guia ]            │  control segmentado
│                                                                      │
│ Panorama                                              [large title]  │
│ Que esta pasando ahora mismo en los destinos                         │
│                                                                      │
│ (Periodo 2022-2025 ▾) (Lugar ▾) (Detalle ▾) (Graficas ▾) (Restablecer)│  barra de herramientas
│ ⟨2022-2025⟩ ⟨Todos los destinos⟩ ⟨Enfoque: Lago de Atitlan ×⟩        │  chips de estado
├──────────────────────────────────────────────────────────────────────┤
│ RESUMEN DEL PERIODO                                     [rotulo]     │
│ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐                          │
│ │ 16.2 M │ │ 4.7 mil│ │  2.5   │ │ 4.31/5 │   tarjetas tipo widget   │
│ └────────┘ └────────┘ └────────┘ └────────┘                          │
│ DONDE Y CUANDO                                                       │
│ ┌──────────────────┐ ┌────────────────────┐                          │
│ │ V1 mapa          │ │ V2 serie de tiempo │   tarjetas blancas       │
│ └──────────────────┘ └────────────────────┘   sobre fondo gris       │
│ PESO DE CADA DESTINO                                                 │
│ ┌──────────────────┐ ┌────────────────────┐                          │
│ │ V3 ranking ←toque│ │ V4 volumen / valor │                          │
│ └──────────────────┘ └────────────────────┘                          │
└──────────────────────────────────────────────────────────────────────┘
```

Elementos y su justificacion (HCI / UX):

- **Barra de navegacion fija y translucida.** El usuario siempre sabe donde
  esta; el desenfoque de fondo da sensacion de profundidad sin robar atencion.
- **Control segmentado** para las 5 secciones: todas las opciones visibles a la
  vez, un solo toque entre ellas. Es el patron de iOS para 2-5 alternativas
  excluyentes, y evita el menu desplegable que esconde el mapa mental.
- **Barra de herramientas con menus emergentes.** Cada filtro es una pildora que
  muestra su valor actual en la etiqueta ("Periodo · 2022-2025"), de modo que el
  estado se lee sin abrir nada. Al tocarla se despliega el control. Esto cumple
  la heuristica de Nielsen de *visibilidad del estado del sistema* ocupando una
  sola linea.
- **Chips de estado** debajo: resumen en una linea que esta viendo el usuario, y
  el enfoque activo se puede quitar desde ahi (*control y libertad del usuario*).
- **Tarjetas agrupadas** con rotulo en mayusculas: la estructura de las listas
  de Ajustes de iOS. Agrupa visualizaciones que responden la misma pregunta y
  deja respirar el contenido (ley de proximidad).
- **Cada visualizacion se presenta igual**: numero (V1…V20), titulo, la pregunta
  de gestion que responde y chips que dicen el tipo de grafica y si esta
  enlazada. El usuario sabe para que sirve antes de mirarla (*reconocer en vez
  de recordar*).
- **Mensajes de vacio explicitos**: cuando una combinacion de filtros se queda
  sin datos, el tablero lo dice con una frase que explica como salir del
  callejon, en vez de mostrar una grafica vacia (*prevencion y recuperacion de
  errores*).
- **Boton Restablecer** siempre visible: salida de emergencia hacia la vista
  inicial.

**Nivel de detalle (tres mecanismos independientes).**

1. *Agregacion temporal* (Ano / Trimestre / Mes): afecta a V2, V8 y V11. A nivel
   ano se ve la senal de fondo; a nivel mes, la dispersion real.
2. *Profundidad del contenido* (Resumen ejecutivo / Analisis completo): oculta o
   muestra las notas metodologicas de cada grafica.
3. *Profundidad jerarquica* del treemap V7: Region → Region y destino → Region,
   destino y categoria, mas el zoom propio del treemap.

**Graficas enlazadas (dos pares, por toque directo).**

| Origen | Destino | Que cambia |
|---|---|---|
| **V3** Ranking de destinos | **V1** mapa, **V2** serie y las secciones *Explorar* y *Sostenibilidad* | Al tocar una barra, el mapa resalta ese destino con un anillo oscuro, la serie dibuja su linea de color sobre el total (que queda en gris de referencia) y las dos secciones de detalle se recalculan solo para el. |
| **V5** Mercados emisores | **V6** Calendario de la demanda | Al tocar un mercado, el mapa de calor pasa de mostrar todos los mercados a mostrar solo la estacionalidad de ese mercado. |

El enfoque activo nunca es invisible: aparece como chip en la barra superior y
se quita desde ahi.

---

## 5. Justificacion del tipo de grafica, visualizacion por visualizacion

| # | Visualizacion | Tipo elegido | Por que este tipo y no otro |
|---|---|---|---|
| **V1** | Donde esta la presion turistica | Mapa de burbujas con escala divergente | La pregunta es geografica ("¿donde?"): una tabla obligaria al usuario a reconstruir el mapa de memoria. El tamano codifica volumen (comparacion de area, aceptable para una lectura gruesa) y el color codifica presion con el semaforo, que es la variable de alerta. |
| **V2** | Evolucion de la visita | Serie de tiempo con area de referencia | Para una variable continua en el tiempo, la linea es la unica forma que deja leer tendencia, estacionalidad y rupturas de un vistazo. El total va en area gris de fondo y el destino enfocado en linea de color: comparacion parte-todo sin apilar. |
| **V3** | Ranking de destinos | Barras horizontales ordenadas | Comparacion de magnitud entre 7 categorias nominales: la barra (posicion sobre eje comun) es la codificacion mas precisa. Horizontal porque los nombres de destino son largos. Se descarto el pastel: con 7 porciones las diferencias pequenas no se distinguen. |
| **V4** | Volumen frente a valor | Dispersion con cuadrantes | La pregunta cruza dos variables continuas y busca *posicion relativa*, no magnitud. Las lineas de promedio crean cuadrantes que convierten la grafica en una matriz de decision. |
| **V5** | De donde viene el visitante | Barras horizontales con porcentaje | Igual que V3: ranking de categorias nominales. El porcentaje al final de la barra responde la pregunta de participacion sin necesidad de un segundo grafico. |
| **V6** | Calendario de la demanda | Mapa de calor mes x ano | La pregunta es un patron de doble entrada (¿que meses? ¿en que anos?). El mapa de calor muestra las 108 celdas a la vez; 9 lineas superpuestas serian ilegibles. El conmutador de indice (100 = mes promedio) permite comparar la *forma* del ano entre anos de tamano muy distinto. |
| **V7** | En que se gasta | Treemap jerarquico | Composicion anidada (region → destino → categoria) donde importa el peso relativo. El area muestra la proporcion y la jerarquia permite subir y bajar de nivel sin cambiar de grafica, que es justo el requisito de nivel de detalle. |
| **V8** | Ocupacion frente a gasto diario | Dispersion con linea de tendencia | La pregunta es de relacion entre dos variables continuas. La nube muestra la dispersion real —el mensaje importante aqui— y la linea resume la asociacion. Se etiqueta explicitamente como asociacion, no causa. |
| **V9** | Perfil segun con quien viaja | Diagrama de caja | El gasto turistico tiene casos extremos que mueven la media; la caja muestra mediana y rango intercuartilico, que es lo que un directivo necesita para dimensionar un segmento. Un grafico de barras de promedios escondria esa asimetria. |
| **V10** | Donde se hospeda cada destino | Barras apiladas al 100% | La pregunta es de composicion y de comparacion entre destinos de tamano muy distinto. Normalizar a 100% hace comparable la mezcla de alojamiento de Semuc Champey con la de Ciudad de Guatemala. |
| **V11** | Crecimiento frente a huella | Doble eje Y | La pregunta es de **ritmos** (¿cual crece mas rapido?), no de niveles, y las dos series tienen unidades incomparables. El doble eje es la forma honesta de ponerlas juntas, acompanada de una nota que advierte que solo deben compararse pendientes. |
| **V12** | Semaforo de presion turistica | Barras con umbral de referencia | Hay un valor critico (1.0 = capacidad de carga) y la pregunta es de posicion respecto a ese umbral. La linea de referencia lo hace explicito y el color + la palabra clasifican cada destino. |
| **V13** | Perfil de sostenibilidad | Radar (hasta 3 destinos) | Compara un mismo destino en 6 dimensiones normalizadas. El radar hace visible la *forma* del perfil (en que gana y en que pierde) de un vistazo. Se limita a 3 series porque mas poligonos superpuestos se vuelven ilegibles, y todos los ejes se orientan de modo que "mas es mejor". |
| **V14** | Beneficio local y certificacion | Dispersion con cuadrantes y tamano | Dos variables de politica publica mas una tercera (derrama) en el tamano. Los cuadrantes definen el objetivo deseado y permiten detectar el caso incomodo: mucho dinero, poco beneficio local. |
| **V15** | Pronostico de visitantes | Serie de tiempo con banda de confianza | Continuidad visual entre lo observado (linea continua) y lo estimado (linea punteada morada). La banda comunica la incertidumbre, que es la informacion que mas suele faltar en un pronostico presentado a directivos. |
| **V16** | Prueba contra la realidad | Serie de tiempo observado vs. estimado | Superponer prediccion y realidad sobre el mismo eje temporal hace visible *donde* se equivoca cada modelo, algo que la tabla de errores no puede mostrar. |
| **V17** | Aciertos y errores | Matrices de confusion | Es la forma estandar de mostrar los dos tipos de error de un clasificador. Se rotula en lenguaje llano ("Lo que paso en realidad" / "Lo que dijo el modelo") y se anotan los dos errores con su consecuencia de negocio: falsa alarma y oportunidad perdida. |
| **V18** | Capacidad de discriminar | Curvas ROC comparadas | Permite comparar los tres modelos en un solo grafico, independientemente del umbral elegido. La diagonal del azar da la referencia que convierte el AUC en algo interpretable. |
| **V19** | ¿Sirve seguir encuestando? | Curva de aprendizaje | Traduce una pregunta tecnica (sobreajuste, tamano de muestra) en una pregunta de presupuesto: si la curva se aplana, mas encuestas del mismo tipo no mejoran nada. |
| **V20** | Que mueve la recomendacion | Barras divergentes de coeficientes | Para la regresion logistica, la barra con signo muestra direccion y magnitud a la vez: verde suma, rosa resta. Para arbol y k-vecinos, que no tienen direccion, se muestra importancia en barras simples y se advierte la diferencia. |

Las tarjetas de un solo valor, los controles, los textos explicativos y las dos
tablas comparativas son **elementos complementarios** y no se cuentan como
visualizaciones.

---

## 6. Modelos incluidos

Los seis modelos se reutilizan de los laboratorios 1 y 2; aqui solo se
re-entrenan con los datos del observatorio y se exponen sus resultados.

**Pronostico de demanda** (se evaluan reservando los ultimos 12 meses, que el
modelo no ve al entrenar):

| Modelo | Que hace | Para que sirve al directivo |
|---|---|---|
| Tendencia + estacionalidad | Regresion con tendencia y efecto fijo por mes | El mas transparente: dice cuanto crece el destino al ano y cuanto aporta cada mes |
| Suavizamiento (Holt-Winters) | Nivel, tendencia y patron anual con mas peso en lo reciente | Reacciona rapido a cambios del ultimo ano |
| SARIMA | Usa la propia historia y la del mismo mes del ano anterior | Unico con intervalo de confianza calculado, no aproximado |

Metricas comparadas: MAE, RMSE y MAPE (el ultimo es el que se comunica, por ser
el mas facil de interpretar).

**Clasificacion de visitantes promotores** (division 75/25 estratificada):

| Modelo | Que hace | Para que sirve |
|---|---|---|
| Regresion logistica | Probabilidad de recomendar, con signo por factor | Dice sobre que palancas actuar |
| Arbol de decision | Reglas encadenadas | El mas facil de explicar a un equipo operativo |
| K vecinos cercanos | Clasifica por similitud | No asume forma funcional, pero no explica el porque |

Metricas comparadas: exactitud, precision, exhaustividad, F1 y AUC.
`calificacion_general` se excluye de las variables predictoras por ser fuga de
informacion.

---

## 7. Planificacion de tareas

**Integrantes:** Pedro Avila, Javier Lopez y Brandon Rivera.

| # | Tarea | Responsable | Entrega |
|---|---|---|---|
| 1 | Definicion de preguntas de gestion y alcance | Pedro Avila + todo el equipo | 13 oct 2026 |
| 2 | Paleta, tipografia y justificacion | Javier Lopez | 15 oct 2026 |
| 3 | Bosquejo de interfaz y navegacion | Javier Lopez | 16 oct 2026 |
| 4 | Capa de datos y codebook (`datos.py`, `generar_datos.py`) | Brandon Rivera | 17 oct 2026 |
| 5 | Seleccion de herramienta y montaje del proyecto | Brandon Rivera | 17 oct 2026 |
| 6 | Dos visualizaciones interactivas funcionales (V1 y V2) | Pedro Avila | 20 oct 2026 |
| 7 | **Entrega del avance** | Todo el equipo | **22 oct 2026, 5:20 pm** |
| 8 | Seccion Panorama (V1-V4) y par enlazado V3 → V1/V2 | Pedro Avila | 23 oct 2026 |
| 9 | Seccion Explorar (V5-V10) y par enlazado V5 → V6 | Javier Lopez | 23 oct 2026 |
| 10 | Seccion Sostenibilidad (V11-V14) | Brandon Rivera | 24 oct 2026 |
| 11 | Reutilizacion de modelos y seccion Modelos (V15-V20) | Pedro Avila | 24 oct 2026 |
| 12 | Guia de lectura, glosario y mensajes de estado vacio | Javier Lopez | 24 oct 2026 |
| 13 | Pruebas de interaccion y correccion de errores | Todo el equipo | 25 oct 2026 |
| 14 | Documento de diseno y exportacion a PDF | Brandon Rivera | 25 oct 2026 |
| 15 | **Entrega final** | Todo el equipo | **25 oct 2026** |

**Repositorio.** El historial de commits documenta la contribucion de cada
integrante; cada tarea de la tabla corresponde a commits de su responsable.

---

## 8. Recomendaciones que se desprenden del tablero y sus limitaciones

Las recomendaciones que el tablero sugiere estan respaldadas por lo que muestra
y vienen con su limitacion declarada:

1. **Antigua Guatemala y Semuc Champey operan por encima de su capacidad de
   carga estimada** (V12). Recomendacion: revisar aforos y escalonar horarios de
   acceso. *Limitacion*: la capacidad de carga es una estimacion de estudios de
   sitio, no una medicion; la recomendacion es revisar, no cerrar.
2. **La huella ambiental crece mas despacio que la visita** (V11): hay desacople
   relativo. *Limitacion*: desacople relativo no es reduccion absoluta; el total
   de emisiones sigue subiendo.
3. **Ocupacion y gasto diario se mueven de forma casi independiente** (V8).
   Recomendacion: las metas de ocupacion no deberian usarse como sustituto de
   metas de derrama. *Limitacion*: es una asociacion observada, no una relacion
   causal.
4. **El uso de guia local y las actividades de naturaleza son los factores con
   mayor efecto positivo sobre la recomendacion** (V20). Recomendacion: priorizar
   inversion ahi. *Limitacion*: el modelo mide asociacion en una encuesta; el
   efecto real debe verificarse con una medicion posterior a la intervencion.

---

**Repositorio:** <https://github.com/jlope384/Laboratorio-10-Dashboard>
