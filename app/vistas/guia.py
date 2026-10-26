"""Guia de lectura: alcance, glosario y limitaciones del tablero."""

from __future__ import annotations

import streamlit as st

from componentes import aviso, nota
from config import AZUL, MORADO, NARANJA, ROSA, VERDE, VIOLETA, CELESTE, SALMON

GLOSARIO = [
    ("Presion turistica",
     "Visitantes del mes divididos entre la capacidad de carga estimada del "
     "sitio. Un valor de 1.0 significa que la visita iguala lo que el sitio "
     "puede absorber sin deteriorarse."),
    ("Capacidad de carga",
     "Numero de visitantes por mes que el sitio soporta segun estudios de "
     "sitio. Es una estimacion tecnica, no una medicion exacta."),
    ("Derrama economica",
     "Gasto total de los visitantes en el destino: alojamiento, alimentacion, "
     "transporte, actividades y compras."),
    ("Estancia media",
     "Noches que en promedio pasa un visitante en el destino."),
    ("Promotor",
     "Visitante que declara que recomendaria el destino a otras personas."),
    ("Desacople",
     "Situacion en la que la visita crece mas rapido que su huella ambiental. "
     "Es el objetivo central de una estrategia de turismo sostenible."),
    ("MAPE",
     "Error porcentual medio del pronostico. Un MAPE de 6% quiere decir que, "
     "en promedio, el modelo se equivoca en 6 de cada 100 visitantes."),
    ("AUC",
     "Mide que tan bien un modelo separa dos grupos. 0.5 equivale a lanzar una "
     "moneda; 1.0 seria perfecto. Entre 0.70 y 0.80 es util para priorizar."),
    ("Matriz de confusion",
     "Tabla de dos por dos que cruza lo que el modelo predijo con lo que "
     "realmente paso."),
]


def _muestra_color(hex_: str, nombre: str, significado: str) -> str:
    return (f'<div style="display:flex;align-items:center;gap:10px;margin:6px 0">'
            f'<span style="width:26px;height:26px;border-radius:7px;'
            f'background:{hex_};display:inline-block;border:1px solid #DFE3F2"></span>'
            f'<span><b>{nombre}</b> <code>{hex_}</code> — {significado}</span></div>')


def render(ctx: dict) -> None:
    st.markdown("### Como usar este tablero")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("#### Alcance")
        st.markdown(
            "- Cubre **7 destinos** de Guatemala, con serie mensual de "
            "**2017 a 2025** y una encuesta a pie de destino desde **2023**.\n"
            "- Responde preguntas de **gestion de destino**: cuanta visita hay, "
            "de donde viene, cuanto deja, cuanta presion genera y que se espera "
            "para los proximos 12 meses.\n"
            "- **No** sustituye estudios de impacto ambiental, ni mide efectos "
            "causales de politicas concretas, ni contiene datos de empresas "
            "individuales."
        )

        st.markdown("#### Tres reglas de lectura")
        st.markdown(
            "1. **Linea continua = dato observado. Linea punteada y color "
            "morado = estimacion de un modelo.**\n"
            "2. Las graficas marcadas como *Enlazada* cambian cuando usted "
            "selecciona algo en su pareja.\n"
            "3. Cuando una seleccion se queda sin datos, el tablero lo dice de "
            "forma explicita en lugar de mostrar una grafica vacia."
        )

        aviso("Las relaciones que muestra el tablero son <b>asociaciones</b>. "
              "Que dos cosas se muevan juntas no demuestra que una cause la "
              "otra: para eso hace falta un diseno de evaluacion especifico.")

    with col2:
        st.markdown("#### Significado de los colores")
        st.markdown(
            _muestra_color(AZUL, "Azul", "demanda: visitantes y volumen") +
            _muestra_color(NARANJA, "Naranja", "economia: gasto, ingresos y empleo") +
            _muestra_color(VERDE, "Verde", "sostenibilidad en buen estado") +
            _muestra_color(ROSA, "Rosa", "presion, alerta o resultado desfavorable") +
            _muestra_color(MORADO, "Morado", "estimaciones y pronosticos") +
            _muestra_color(CELESTE, "Celeste", "serie de apoyo o contexto") +
            _muestra_color(VIOLETA, "Violeta", "navegacion y encabezados"),
            unsafe_allow_html=True)
        nota("El semaforo de presion turistica usa los tres colores de la paleta "
             "(verde, naranja, rosa) y <b>siempre</b> va acompanado de la palabra "
             "correspondiente, para no depender solo del color.")

    st.divider()
    st.markdown("#### Glosario")
    for termino, definicion in GLOSARIO:
        with st.expander(termino):
            st.write(definicion)

    st.divider()
    st.markdown("#### Origen de los datos y limitaciones")
    st.markdown(
        "Las tres tablas se generan con `data/generar_datos.py`, con semilla "
        "fija y reproducible. Reproducen la estacionalidad, la caida por la "
        "pandemia y los ordenes de magnitud que reportan INGUAT y la OMT para "
        "los destinos de Guatemala, pero **no son cifras oficiales**: el "
        "tablero esta construido para que, al sustituir los CSV por registros "
        "oficiales con las mismas columnas, funcione sin ningun otro cambio. "
        "Las columnas estan documentadas en `docs/codebook.md`."
    )
