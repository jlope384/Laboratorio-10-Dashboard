"""Modelos: pronostico de demanda y clasificacion de visitantes promotores."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

import datos as dt
import modelos as mo
from componentes import (aplicar_estilo, grupo, lectura, miles, mostrar,
                         nota, par_columnas, sin_datos, titulo_grafica)
from config import (AZUL, CATEGORICA, CELESTE, COLOR_MODELO, GRIS, LINEA,
                    MORADO, NARANJA, ROSA, SECUENCIAL, TINTA, TINTA_2, VERDE)


# --------------------------------------------------------------------------
# Pronostico
# --------------------------------------------------------------------------
def _grafica_pronostico(serie: pd.DataFrame,
                        resultados: dict[str, mo.ResultadoSerie],
                        elegidos: list[str], con_banda: str | None):
    fig = go.Figure()

    if con_banda and con_banda in resultados:
        fut = resultados[con_banda].futuro
        fig.add_trace(go.Scatter(
            x=list(fut["fecha"]) + list(fut["fecha"][::-1]),
            y=list(fut["superior"]) + list(fut["inferior"][::-1]),
            fill="toself", fillcolor="rgba(162,21,141,0.13)",
            line=dict(width=0), hoverinfo="skip",
            name=f"Rango probable · {con_banda}"))

    fig.add_trace(go.Scatter(
        x=serie["fecha"], y=serie["llegadas"], name="Observado",
        mode="lines", line=dict(color=TINTA, width=2.5),
        hovertemplate="%{x|%b %Y}<br>Observado: %{y:,.0f}<extra></extra>"))

    ultima = serie.iloc[-1]
    for nombre in elegidos:
        r = resultados[nombre]
        color = COLOR_MODELO[nombre]
        x = [ultima["fecha"]] + list(r.futuro["fecha"])
        y = [ultima["llegadas"]] + list(r.futuro["estimado"])
        fig.add_trace(go.Scatter(
            x=x, y=y, name=f"{nombre} (estimado)", mode="lines",
            line=dict(color=color, width=2.5, dash="dot"),
            hovertemplate="%{x|%b %Y}<br>" + nombre + ": %{y:,.0f}<extra></extra>"))

    # La linea de corte se dibuja como forma y la etiqueta como anotacion
    # aparte: `add_vline` con `annotation_text` falla sobre un eje de fechas
    # en esta version de plotly.
    corte = pd.Timestamp(ultima["fecha"]).strftime("%Y-%m-%d")
    fig.add_shape(type="line", x0=corte, x1=corte, xref="x", yref="paper",
                  y0=0, y1=1, line=dict(color=GRIS, width=1.5, dash="dash"))
    fig.add_annotation(x=corte, xref="x", yref="paper", y=1.0, yanchor="bottom",
                       xanchor="right", showarrow=False,
                       text="Fin del dato observado",
                       font=dict(size=11, color=TINTA_2))
    aplicar_estilo(fig, alto=430, yaxis_title="Visitantes por mes",
                   xaxis_title="", hovermode="x unified")
    return fig


def _grafica_validacion(resultados: dict[str, mo.ResultadoSerie],
                        elegidos: list[str]):
    fig = go.Figure()
    base = next(iter(resultados.values())).prueba
    fig.add_trace(go.Scatter(
        x=base["fecha"], y=base["real"], name="Observado", mode="lines+markers",
        line=dict(color=TINTA, width=3), marker=dict(size=7),
        hovertemplate="%{x|%b %Y}<br>Observado: %{y:,.0f}<extra></extra>"))
    for nombre in elegidos:
        r = resultados[nombre]
        fig.add_trace(go.Scatter(
            x=r.prueba["fecha"], y=r.prueba["estimado"], name=nombre,
            mode="lines+markers", marker=dict(size=6),
            line=dict(color=COLOR_MODELO[nombre], width=2, dash="dot"),
            hovertemplate="%{x|%b %Y}<br>" + nombre + ": %{y:,.0f}<extra></extra>"))
    aplicar_estilo(fig, alto=380, yaxis_title="Visitantes por mes",
                   xaxis_title="Meses reservados para la prueba",
                   hovermode="x unified")
    return fig


# --------------------------------------------------------------------------
# Clasificacion
# --------------------------------------------------------------------------
ETIQUETAS_CLASE = ["No recomienda", "Recomienda"]


def _matrices(resultados: dict[str, mo.ResultadoClase], elegidos: list[str]):
    fig = make_subplots(rows=1, cols=len(elegidos),
                        subplot_titles=elegidos, horizontal_spacing=0.09)
    for i, nombre in enumerate(elegidos, start=1):
        m = resultados[nombre].matriz
        pct = m / m.sum() * 100
        texto = [[f"{m[r][c]:,}<br>{pct[r][c]:.1f}%" for c in range(2)]
                 for r in range(2)]
        fig.add_trace(go.Heatmap(
            z=pct, x=ETIQUETAS_CLASE, y=ETIQUETAS_CLASE,
            text=texto, texttemplate="%{text}", textfont=dict(size=12),
            colorscale=SECUENCIAL, showscale=False, zmin=0, zmax=60,
            hovertemplate="Real: %{y}<br>Modelo dijo: %{x}<br>"
                          "%{z:.1f}% de los casos<extra></extra>"),
            row=1, col=i)
        fig.update_xaxes(title_text="Lo que dijo el modelo", row=1, col=i,
                         title_font=dict(size=11))
        fig.update_yaxes(autorange="reversed", row=1, col=i)
    fig.update_yaxes(title_text="Lo que paso en realidad", row=1, col=1,
                     title_font=dict(size=11))
    aplicar_estilo(fig, alto=330)
    fig.update_annotations(font_size=13)
    return fig


def _roc(resultados: dict[str, mo.ResultadoClase], elegidos: list[str]):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="Azar",
                             line=dict(color=GRIS, width=1.5, dash="dash"),
                             hoverinfo="skip"))
    for nombre in elegidos:
        fpr, tpr = resultados[nombre].roc
        auc = resultados[nombre].metricas["AUC"]
        fig.add_trace(go.Scatter(
            x=fpr, y=tpr, mode="lines", name=f"{nombre} · AUC {auc:.3f}",
            line=dict(color=COLOR_MODELO[nombre], width=2.5),
            hovertemplate="Falsas alarmas: %{x:.2f}<br>Aciertos: %{y:.2f}<extra></extra>"))
    aplicar_estilo(fig, alto=380,
                   xaxis_title="Falsas alarmas (dijo que si y era no)",
                   yaxis_title="Aciertos (dijo que si y era si)")
    fig.update_xaxes(range=[0, 1], constrain="domain")
    fig.update_yaxes(range=[0, 1], scaleanchor="x", scaleratio=1,
                     constrain="domain")
    return fig


def _aprendizaje(resultados: dict[str, mo.ResultadoClase], elegidos: list[str]):
    fig = go.Figure()
    for nombre in elegidos:
        c = resultados[nombre].curva_aprendizaje
        color = COLOR_MODELO[nombre]
        fig.add_trace(go.Scatter(
            x=c["tamano"], y=c["entrenamiento"], name=f"{nombre} · entrenamiento",
            mode="lines", line=dict(color=color, width=1.6, dash="dot"),
            hovertemplate="%{x:,.0f} casos<br>Entrenamiento: %{y:.3f}<extra></extra>"))
        fig.add_trace(go.Scatter(
            x=c["tamano"], y=c["validacion"], name=f"{nombre} · validacion",
            mode="lines+markers", line=dict(color=color, width=2.8),
            marker=dict(size=6),
            hovertemplate="%{x:,.0f} casos<br>Validacion: %{y:.3f}<extra></extra>"))
    aplicar_estilo(fig, alto=380,
                   xaxis_title="Casos usados para entrenar",
                   yaxis_title="Capacidad de discriminar (AUC)")
    return fig


def _importancia(resultado: mo.ResultadoClase):
    d = resultado.importancia.sort_values("magnitud")
    if resultado.tipo_importancia == "coeficiente":
        colores = [VERDE if v > 0 else ROSA for v in d["peso"]]
        titulo_x = "Efecto sobre la probabilidad de recomendar"
        texto = [f"{v:+.2f}" for v in d["peso"]]
    else:
        colores = [AZUL] * len(d)
        titulo_x = ("Perdida de capacidad predictiva al quitar la variable"
                    if resultado.tipo_importancia == "permutacion"
                    else "Peso en las reglas del arbol")
        texto = [f"{v:.3f}" for v in d["peso"]]

    fig = go.Figure(go.Bar(
        x=d["peso"], y=d["variable"], orientation="h", marker_color=colores,
        text=texto, textposition="outside", textfont=dict(size=10),
        hovertemplate="<b>%{y}</b><br>%{x:.3f}<extra></extra>"))
    aplicar_estilo(fig, alto=430, xaxis_title=titulo_x, yaxis_title="",
                   bargap=0.3)
    return fig


# --------------------------------------------------------------------------
def render(ctx: dict) -> None:
    df = ctx["mensual"]
    historia = ctx.get("mensual_completo", df)
    visitantes = ctx["visitantes"]
    activas = ctx["graficas_activas"]

    st.markdown(
        '<div class="ots-nota">Los modelos de esta seccion no son nuevos: son '
        'las familias trabajadas en los laboratorios anteriores del curso, '
        're-entrenadas con los datos del observatorio. <b>Todo lo que aparece '
        'en morado o con linea punteada es una estimacion</b>, no un dato '
        'observado.</div>', unsafe_allow_html=True)

    tab_a, tab_b = st.tabs(["Pronostico de demanda",
                            "Quien recomienda el destino"])

    # ======================= PRONOSTICO ==================================
    with tab_a:
        opciones = ["Todos los destinos filtrados"] + sorted(historia["destino"].unique())
        col1, col2 = st.columns([1.3, 1])
        with col1:
            cual = st.selectbox("Serie a pronosticar", opciones, key="serie_pron")
        with col2:
            desde = st.selectbox(
                "Entrenar con datos desde", [2017, 2022, 2023], index=1,
                key="anio_entrena",
                help="2022 en adelante deja fuera el desplome de la pandemia, "
                     "que no se espera que se repita y distorsiona la tendencia.")

        base = (historia if cual == "Todos los destinos filtrados"
                else historia[historia["destino"] == cual])
        serie = dt.serie_nacional(base[base["anio"] >= desde])

        if len(serie) < 36:
            sin_datos("Hacen falta al menos 3 anos de historia mensual para "
                      "entrenar los modelos estacionales. Cambie el ano de "
                      "inicio del entrenamiento o quite filtros de lugar.")
            return

        resultados = mo.pronosticar(serie)
        tabla = mo.tabla_serie(resultados)
        mejor = tabla.iloc[0]["Modelo"]

        elegidos = st.multiselect("Modelos a mostrar", mo.MODELOS_SERIE,
                                  default=mo.MODELOS_SERIE, key="modelos_serie")
        if not elegidos:
            sin_datos("Seleccione al menos un modelo para ver el pronostico.")
            return

        if "V15 Pronostico" in activas:
            grupo("Proximos 12 meses")
            with st.container(border=True):
                titulo_grafica("V15", f"Pronostico de visitantes · {cual}",
                               "¿Cuanta visita se espera en los proximos 12 "
                               "meses y con que margen de error?",
                               ["Serie de tiempo", "Estimacion"])
                banda = st.segmented_control(
                    "Rango probable", ["Sin rango"] + elegidos,
                    default=elegidos[0], key="banda_pron",
                    label_visibility="collapsed") or "Sin rango"
                mostrar(_grafica_pronostico(
                    serie, resultados, elegidos,
                    None if banda == "Sin rango" else banda), clave="pronostico")

                prox = resultados[mejor].futuro
                lectura(
                    f"<b>Lectura para decidir.</b> El modelo con menor error en "
                    f"la prueba es <b>{mejor}</b>. Estima "
                    f"{miles(prox['estimado'].sum())} visitantes en los proximos "
                    f"12 meses, con un rango probable de "
                    f"{miles(prox['inferior'].sum())} a "
                    f"{miles(prox['superior'].sum())}. Planifique capacidad con "
                    "el extremo alto del rango y compromisos de ingreso con el "
                    "bajo. El modelo proyecta la continuidad del patron "
                    "historico: no incorpora nuevas rutas aereas, crisis ni "
                    "campanas de promocion.")

        grupo("Comparacion de los tres modelos de pronostico")
        col3, col4 = st.columns([1, 1.2], gap="small")
        with col3, st.container(border=True):
            st.dataframe(
                tabla, hide_index=True, width="stretch",
                column_config={
                    "Error medio (visitantes)": st.column_config.NumberColumn(
                        format="%d", help="MAE: en cuantos visitantes se "
                                          "equivoca en promedio cada mes."),
                    "RMSE": st.column_config.NumberColumn(
                        format="%d", help="Penaliza mas los errores grandes."),
                    "Error porcentual (MAPE)": st.column_config.NumberColumn(
                        format="%.2f %%",
                        help="Error medio como porcentaje del valor real."),
                })
            for nombre in mo.MODELOS_SERIE:
                st.markdown(f"<div class='ots-nota'><b>{nombre}.</b> "
                            f"{mo.EXPLICACION_SERIE[nombre]}</div>",
                            unsafe_allow_html=True)
        with col4:
            if "V16 Validacion del pronostico" in activas:
                with st.container(border=True):
                    titulo_grafica("V16", "Prueba contra la realidad",
                                   "¿Que tan cerca estuvo cada modelo en los "
                                   "ultimos 12 meses, que no vio al entrenar?",
                                   ["Serie de tiempo", "Validacion"])
                    mostrar(_grafica_validacion(resultados, elegidos),
                            clave="validacion_pron")
                    nota("Los modelos se entrenaron sin estos 12 meses y luego "
                         "se les pidio adivinarlos. Es la forma honesta de "
                         "comparar: medir el error sobre datos que el modelo no "
                         "habia visto.")

    # ======================= CLASIFICACION ================================
    with tab_b:
        if visitantes.empty or visitantes["promotor"].nunique() < 2:
            sin_datos("La encuesta a visitantes cubre 2023 en adelante. Amplie "
                      "el periodo en la barra superior para habilitar los "
                      "modelos de clasificacion.")
            return

        st.markdown(
            '<div class="ots-lectura"><b>Pregunta de gestion:</b> de cada '
            'visitante que llega, ¿quien termina recomendando el destino? '
            'Identificarlo con anticipacion permite decidir donde invertir en '
            'experiencia y a que segmento dirigir la promocion.</div>',
            unsafe_allow_html=True)
        nota("La calificacion que el visitante dio al final del viaje <b>no</b> "
             "se usa como variable predictora: seria hacer trampa, porque se "
             "conoce despues del hecho que se quiere anticipar.")

        res = mo.clasificar(visitantes)
        tabla = mo.tabla_clase(res)
        mejor = tabla.iloc[0]["Modelo"]

        elegidos = st.multiselect("Modelos a mostrar", mo.MODELOS_CLASE,
                                  default=mo.MODELOS_CLASE, key="modelos_clase")
        if not elegidos:
            sin_datos("Seleccione al menos un modelo.")
            return

        if "V17 Matrices de confusion" in activas:
            grupo("Aciertos y errores")
            with st.container(border=True):
                titulo_grafica("V17", "Aciertos y errores de cada modelo",
                               "¿En que se equivoca cada modelo: deja escapar "
                               "promotores o los ve donde no los hay?",
                               ["Matriz de confusion", "Estimacion"])
                mostrar(_matrices(res, elegidos), clave="matrices")
                nota("La diagonal son los aciertos. Arriba a la derecha: el "
                     "modelo anuncio un promotor que no lo era (falsa alarma). "
                     "Abajo a la izquierda: no vio a un promotor real "
                     "(oportunidad perdida).")

        if "V18 Curvas ROC" in activas or "V19 Curva de aprendizaje" in activas:
            grupo("Desempeno de los modelos")
            col5, col6 = par_columnas("V18 Curvas ROC" in activas,
                                      "V19 Curva de aprendizaje" in activas)
            if "V18 Curvas ROC" in activas:
                with col5, st.container(border=True):
                    titulo_grafica("V18", "Capacidad de discriminar",
                                   "¿Que modelo separa mejor a quien recomienda "
                                   "de quien no?",
                                   ["Curva ROC", "Estimacion"])
                    mostrar(_roc(res, elegidos), clave="roc")
                    nota("Cuanto mas pegada a la esquina superior izquierda, "
                         "mejor. La diagonal gris es el desempeno de lanzar una "
                         "moneda (AUC 0.5).")
            if "V19 Curva de aprendizaje" in activas:
                with col6, st.container(border=True):
                    titulo_grafica("V19", "¿Sirve seguir encuestando?",
                                   "¿El modelo mejora si ampliamos la encuesta "
                                   "o ya toco techo?",
                                   ["Curva de aprendizaje", "Estimacion"])
                    mostrar(_aprendizaje(res, elegidos), clave="aprendizaje")
                    nota("La linea gruesa es el desempeno con datos nuevos. Si "
                         "se aplana, recolectar mas encuestas del mismo tipo ya "
                         "no mejora la prediccion: conviene agregar variables "
                         "nuevas. Una brecha grande con la linea punteada indica "
                         "que el modelo se esta memorizando los datos.")

        grupo("Comparacion de los tres modelos de clasificacion")
        col7, col8 = st.columns([1, 1], gap="small")
        with col7, st.container(border=True):
            st.dataframe(
                tabla, hide_index=True, width="stretch",
                column_config={
                    "Exactitud": st.column_config.NumberColumn(
                        format="%.3f", help="Porcentaje de casos bien "
                                            "clasificados."),
                    "Precision": st.column_config.NumberColumn(
                        format="%.3f", help="De los que el modelo marco como "
                                            "promotores, cuantos lo eran."),
                    "Exhaustividad": st.column_config.NumberColumn(
                        format="%.3f", help="De los promotores reales, cuantos "
                                            "detecto el modelo."),
                    "F1": st.column_config.NumberColumn(
                        format="%.3f", help="Equilibrio entre precision y "
                                            "exhaustividad."),
                    "AUC": st.column_config.NumberColumn(
                        format="%.3f", help="Capacidad global de discriminar. "
                                            "0.5 es azar, 1.0 es perfecto."),
                })
            for nombre in mo.MODELOS_CLASE:
                st.markdown(f"<div class='ots-nota'><b>{nombre}.</b> "
                            f"{mo.EXPLICACION_CLASE[nombre]}</div>",
                            unsafe_allow_html=True)
        with col8:
            if "V20 Que mueve la recomendacion" in activas:
                with st.container(border=True):
                    cual = st.selectbox(
                        "Ver los factores segun el modelo", elegidos,
                        index=elegidos.index(mejor) if mejor in elegidos else 0,
                        key="modelo_importancia")
                    titulo_grafica("V20", "Que mueve la recomendacion",
                                   "¿Sobre que factores puede actuar la gestion "
                                   "del destino para ganar promotores?",
                                   ["Barras", "Estimacion"])
                    mostrar(_importancia(res[cual]), clave="importancia")
                    if res[cual].tipo_importancia == "coeficiente":
                        nota("Verde: sube la probabilidad de recomendar. Rosa: "
                             "la baja. Son <b>asociaciones</b> medidas en la "
                             "encuesta, no relaciones de causa y efecto "
                             "demostradas.")
                    else:
                        nota("Mide cuanto aporta cada factor a la capacidad de "
                             "prediccion. No indica direccion: para saber si "
                             "suma o resta, vea la regresion logistica.")

        mejor_auc = tabla.iloc[0]["AUC"]
        lectura(f"<b>Lectura para decidir.</b> El modelo con mejor "
                f"discriminacion es <b>{mejor}</b> (AUC {mejor_auc:.3f}). Un AUC "
                "en este rango sirve para <i>priorizar</i> acciones, no para "
                "decidir caso por caso sobre un visitante concreto. La "
                "recomendacion practica es usarlo para elegir en que palancas "
                "invertir (por ejemplo guia local o reduccion de incidencias) y "
                "verificar el efecto con una medicion posterior.")
