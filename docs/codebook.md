# Codebook del Observatorio de Turismo Sostenible

Tres tablas, generadas por `data/generar_datos.py` con semilla fija (2026).
Son datos **sinteticos**: imitan la estacionalidad, la caida por la pandemia y
los ordenes de magnitud de los destinos de Guatemala, pero no son cifras
oficiales. Para sustituirlos por datos reales basta respetar estos nombres de
columna.

## 1. `turismo_mensual.csv` — 756 filas (7 destinos x 108 meses, 2017-01 a 2025-12)

| Variable | Tipo | Descripcion |
|---|---|---|
| fecha | datetime | Primer dia del mes observado |
| anio, mes, trimestre | int / str | Derivadas de `fecha` |
| destino | str | Uno de los 7 destinos del observatorio |
| region | str | Region turistica a la que pertenece el destino |
| perfil | str | cultural, naturaleza, arqueologico o urbano |
| lat, lon | float | Coordenadas del destino (para el mapa V1) |
| llegadas | int | Visitantes del mes |
| estancia_promedio | float | Noches por visitante |
| noches_totales | int | `llegadas * estancia_promedio` |
| ocupacion_hotelera | float | Porcentaje de ocupacion (0-100) |
| gasto_diario_usd | float | Gasto por visitante y noche, en USD |
| gasto_total_usd | float | Derrama del mes, en USD |
| gasto_alojamiento_usd … gasto_artesanias_usd | float | Reparto de la derrama en 5 categorias; suman `gasto_total_usd` |
| empleos_turisticos | int | Empleos asociados a la actividad del mes |
| empleo_local_pct | float | Porcentaje del empleo turistico de origen local |
| empresas_certificadas_pct | float | Porcentaje de empresas con certificacion sostenible |
| residuos_ton | float | Residuos solidos generados por la visita, en toneladas |
| agua_miles_m3 | float | Consumo de agua asociado, en miles de m3 |
| co2_ton | float | Emisiones asociadas, en toneladas |
| capacidad_carga | int | Visitantes/mes que el sitio soporta segun estudios de sitio |
| presion_turistica | float | `llegadas / capacidad_carga`. 1.0 = en el limite |
| satisfaccion_promedio | float | Calificacion media del destino (1 a 5) |

## 2. `mercados.csv` — 6 048 filas (7 destinos x 108 meses x 8 mercados)

| Variable | Tipo | Descripcion |
|---|---|---|
| fecha, anio, mes | datetime / int | Mes observado |
| destino, region | str | Destino al que llegan |
| mercado | str | Mercado emisor: Estados Unidos, El Salvador, Mexico, Honduras, Europa, Canada, Sudamerica, Asia y otros |
| llegadas | int | Visitantes de ese mercado en ese destino y mes |

La suma de `llegadas` por destino-mes coincide con `turismo_mensual.llegadas`.

## 3. `visitantes.csv` — 9 000 filas (encuesta a pie de destino, 2023-2025)

Una fila por visitante entrevistado. El muestreo es proporcional a las
llegadas de cada destino-mes.

| Variable | Tipo | Descripcion |
|---|---|---|
| id_visitante | int | Identificador del cuestionario |
| fecha, anio, mes | datetime / int | Mes de la entrevista |
| destino, region | str | Lugar de la entrevista |
| mercado | str | Mercado emisor del visitante |
| edad | int | Anos cumplidos (18-79) |
| grupo_viaje | str | Solo, Pareja, Familia, Amigos, Negocios |
| noches | int | Noches de estancia |
| gasto_diario_usd | float | Gasto declarado por dia |
| gasto_total_usd | float | `gasto_diario_usd * noches` |
| tipo_alojamiento | str | Hotel, Hostal, Airbnb / casa, Ecolodge, Casa de familiares |
| transporte_principal | str | Tour operador, Vehiculo propio, Transporte publico, Shuttle turistico |
| anticipacion_reserva_dias | int | Dias entre la reserva y el viaje |
| uso_guia_local | int | 1 si contrato guia local |
| actividades_culturales | int | Numero de actividades culturales realizadas |
| actividades_naturaleza | int | Numero de actividades de naturaleza realizadas |
| incidencias_reportadas | int | Problemas reportados durante el viaje (0-2) |
| presion_destino | float | Presion turistica del destino-mes de la entrevista |
| certificacion_destino_pct | float | Certificacion del destino-mes de la entrevista |
| calificacion_general | int | Calificacion del viaje (1 a 5) |
| promotor | int | **Variable objetivo.** 1 si recomendaria el destino |

### Variables usadas por los modelos de clasificacion

Numericas: `edad`, `noches`, `gasto_diario_usd`, `anticipacion_reserva_dias`,
`uso_guia_local`, `actividades_culturales`, `actividades_naturaleza`,
`incidencias_reportadas`, `presion_destino`, `certificacion_destino_pct`.

Categoricas: `destino`, `mercado`, `grupo_viaje`, `tipo_alojamiento`,
`transporte_principal`.

`calificacion_general` **se excluye a proposito**: se conoce despues del hecho
que se quiere anticipar y meterla seria fuga de informacion.
