"""Exploracion libre: mercados, estacionalidad, gasto y perfil del visitante."""

from __future__ import annotations

import altair as alt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import datos as dt
from componentes import (aplicar_estilo, grupo, lectura, miles, mostrar,
                         mostrar_tactil, nota, par_columnas, sin_datos,
                         titulo_grafica)
from config import (AZUL, CATEGORICA, COLOR_DESTINO, GRIS, IOS_SEC, LINEA,
                    MORADO, NARANJA, ROSA, SECUENCIAL, VERDE)

NOMBRES_MES = dt.NOMBRES_MES


def _mercados_tactil(mercados: pd.DataFrame, foco: str | None):
    """V5 en Altair: el toque sobre un mercado es el origen del enlace con V6."""
    r = (mercados.groupby("mercado", as_index=False)["llegadas"].sum())
    total = max(r["llegadas"].sum(), 1)
    r["parte"] = r["llegadas"] / total * 100
    r["etiqueta"] = r["parte"].map(lambda p: f"{p:.1f}%")

    toque = alt.selection_point(fields=["mercado"], name="toque", empty=True)
    base = alt.Chart(r).encode(
        y=alt.Y("mercado:N", sort="-x", title=None,
                axis=alt.Axis(labelLimit=180)),
        x=alt.X("llegadas:Q", title="Visitantes del periodo",
                axis=alt.Axis(format="~s")))
    barras = base.mark_bar(cornerRadiusEnd=7, height=20).encode(
        color=alt.condition(
            toque if foco is None else alt.datum.mercado == foco,
            alt.value(AZUL), alt.value("#D8D8DE")),
        tooltip=[alt.Tooltip("mercado:N", title="Mercado"),
                 alt.Tooltip("llegadas:Q", title="Visitantes", format=",.0f"),
                 alt.Tooltip("parte:Q", title="Participacion", format=".1f")],
    ).add_params(toque)
    texto = base.mark_text(align="left", dx=6, fontSize=11, color=IOS_SEC
                           ).encode(text="etiqueta:N")
    return (barras + texto).properties(height=max(200, 40 * len(r)))


def _estacionalidad(mercados: pd.DataFrame, foco: str | None, normalizar: bool):
    base = mercados if not foco else mercados[mercados["mercado"] == foco]
    if base.empty:
        return None
    tabla = base.pivot_table(index="anio", columns="mes", values="llegadas",
                             aggfunc="sum").reindex(columns=range(1, 13))
    titulo_barra = "Visitantes"
    texto = tabla.map(lambda v: "" if pd.isna(v) else miles(v))
    if normalizar:
        # Indice: 100 = mes promedio de ese ano. Compara la FORMA del ano y no
        # su tamano, que es lo util para planificar temporadas.
        tabla = tabla.div(tabla.mean(axis=1), axis=0) * 100
        texto = tabla.map(lambda v: "" if pd.isna(v) else f"{v:.0f}")
        titulo_barra = "Indice<br>100 = mes<br>promedio"

    fig = go.Figure(go.Heatmap(
        z=tabla.values, x=[NOMBRES_MES[m - 1] for m in tabla.columns],
        y=tabla.index.astype(str), colorscale=SECUENCIAL,
        text=texto.values, texttemplate="%{text}", textfont=dict(size=10),
        xgap=3, ygap=3,
        hovertemplate="%{y} · %{x}<br>%{z:,.0f}<extra></extra>",
        colorbar=dict(title=titulo_barra, thickness=10, len=0.8,
                      tickfont=dict(size=10))))
    aplicar_estilo(fig, alto=390, xaxis_title="", yaxis_title="Ano")
    # El ano es una etiqueta, no una magnitud: sin esto plotly dibuja
    # marcas intermedias como 2022.5.
    fig.update_yaxes(type="category", autorange="reversed")
    return fig


def _treemap(df: pd.DataFrame, profundidad: str):
    rutas = {"Region": ["region"],
             "Region y destino": ["region", "destino"],
             "Region, destino y categoria": ["region", "destino", "categoria"]}[profundidad]
    por = [c for c in rutas if c != "categoria"]
    largo = dt.gasto_largo(df, por)
    if "categoria" not in rutas:
        largo = largo.groupby(por, as_index=False)["gasto_usd"].sum()

    fig = px.treemap(largo, path=[px.Constant("Total"), *rutas],
                     values="gasto_usd", color="gasto_usd",
                     # Escala clara: el texto de cada rectangulo debe leerse
                     # sin depender de que el color sea oscuro o no.
                     color_continuous_scale=["#EDEFFA", "#C7CEF2", "#9AA8EA",
                                             "#7487DB"])
    fig.update_traces(
        root_color="#F5F6FD",
        textfont=dict(size=12, color="#2E3B73"),
        marker=dict(cornerradius=10, line=dict(color="white", width=2)),
        textinfo="label+percent parent",
        hovertemplate="<b>%{label}</b><br>Gasto: US$ %{value:,.0f}<br>"
                      "%{percentParent:.1%} de %{parent}<extra></extra>")
    aplicar_estilo(fig, alto=420, coloraxis_showscale=False,
                   margin=dict(l=2, r=2, t=28, b=2))
    return fig


def _ocupacion_gasto(df: pd.DataFrame, nivel: str):
    agg = dt.agregar_tiempo(df, nivel, por=["destino"])
    fig = px.scatter(agg, x="ocupacion_hotelera", y="gasto_diario_usd",
                     size="llegadas", color="destino",
                     color_discrete_map=COLOR_DESTINO, size_max=26,
                     opacity=0.75, trendline="ols", trendline_scope="overall",
                     trendline_color_override=GRIS,
                     custom_data=["destino", "etiqueta", "llegadas"])
    fig.update_traces(
        selector=dict(mode="markers"),
        hovertemplate=("<b>%{customdata[0]}</b> · %{customdata[1]}<br>"
                       "Ocupacion: %{x:.1f}%<br>"
                       "Gasto diario: US$ %{y:,.0f}<br>"
                       "Visitantes: %{customdata[2]:,.0f}<extra></extra>"))
    aplicar_estilo(fig, alto=400, xaxis_title="Ocupacion hotelera (%)",
                   yaxis_title="Gasto diario por visitante (USD)")
    return fig


def _caja(visitantes: pd.DataFrame, variable: str):
    etiqueta = {"gasto_diario_usd": "Gasto diario (USD)",
                "noches": "Noches de estancia",
                "calificacion_general": "Calificacion (1 a 5)"}[variable]
    fig = px.box(visitantes, x="grupo_viaje", y=variable, color="grupo_viaje",
                 points=False, color_discrete_sequence=CATEGORICA,
                 category_orders={"grupo_viaje": ["Solo", "Pareja", "Familia",
                                                  "Amigos", "Negocios"]})
    fig.update_traces(hovertemplate="<b>%{x}</b><br>Mediana y rango "
                                    "intercuartilico<extra></extra>")
    aplicar_estilo(fig, alto=370, showlegend=False, xaxis_title="",
                   yaxis_title=etiqueta)
    return fig


def _alojamiento(visitantes: pd.DataFrame):
    r = (visitantes.groupby(["destino", "tipo_alojamiento"], as_index=False)
                   .size().rename(columns={"size": "visitantes"}))
    total = r.groupby("destino")["visitantes"].transform("sum")
    r["parte"] = r["visitantes"] / total * 100
    orden = ["Hotel", "Hostal", "Airbnb / casa", "Ecolodge", "Casa de familiares"]
    fig = px.bar(r, x="parte", y="destino", color="tipo_alojamiento",
                 orientation="h", color_discrete_sequence=CATEGORICA,
                 category_orders={"tipo_alojamiento": orden},
                 custom_data=["tipo_alojamiento", "visitantes"])
    fig.update_traces(hovertemplate=("<b>%{y}</b><br>%{customdata[0]}: %{x:.1f}% "
                                     "(%{customdata[1]:,.0f} encuestados)"
                                     "<extra></extra>"))
    aplicar_estilo(fig, alto=390, barmode="stack",
                   xaxis_title="Participacion del alojamiento (%)", yaxis_title="")
    return fig


# --------------------------------------------------------------------------
def render(ctx: dict) -> None:
    df = ctx["mensual"]
    mercados = ctx["mercados"]
    visitantes = ctx["visitantes"]
    nivel = ctx["nivel_tiempo"]
    detalle = ctx["detalle"]
    activas = ctx["graficas_activas"]

    if df.empty:
        sin_datos("No hay informacion para la combinacion de filtros elegida.")
        return

    foco_m = st.session_state.get("mercado_foco")

    # ---- V5 y V6: el segundo par enlazado ---------------------------------
    if "V5 Mercados emisores" in activas or "V6 Estacionalidad" in activas:
        grupo("De donde viene y cuando llega")
        col_a, col_b = par_columnas("V5 Mercados emisores" in activas,
                                    "V6 Estacionalidad" in activas,
                                    (1, 1.3))

        if "V5 Mercados emisores" in activas:
            with col_a, st.container(border=True):
                titulo_grafica("V5", "De donde viene el visitante",
                               "¿En que mercados emisores se concentra la "
                               "demanda?",
                               ["Barras", "Toque para enfocar",
                                "Enlazada con V6"])
                elegido = mostrar_tactil(_mercados_tactil(mercados, foco_m),
                                         clave="mercados_bar", campo="mercado")
                if elegido and elegido != foco_m:
                    st.session_state["mercado_foco"] = elegido
                    st.rerun()
                if foco_m:
                    lectura(f"<b>Mercado enfocado: {foco_m}.</b> El calendario "
                            "de la derecha muestra solo a ese mercado. Toque "
                            "otra barra para cambiarlo.")
                else:
                    lectura("Toque una barra para que el calendario (V6) muestre "
                            "la estacionalidad de ese mercado. Los mercados de "
                            "larga distancia y los vecinos no llegan en los "
                            "mismos meses.")

        if "V6 Estacionalidad" in activas:
            with col_b, st.container(border=True):
                etiqueta = foco_m or "todos los mercados"
                titulo_grafica("V6", f"Calendario de la demanda · {etiqueta}",
                               "¿En que meses conviene concentrar promocion, "
                               "personal y mantenimiento?",
                               ["Mapa de calor", "Enlazada con V5"])
                normalizar = st.toggle(
                    "Comparar la forma del ano (indice 100 = mes promedio)",
                    value=False, key="normalizar_heatmap",
                    help="Neutraliza el tamano de cada ano y deja ver solo el "
                         "patron estacional. Util para comparar 2020 con 2025.")
                fig = _estacionalidad(mercados, foco_m, normalizar)
                if fig is None:
                    sin_datos("El mercado seleccionado no tiene registros en "
                              "este periodo ni en estos destinos.")
                else:
                    mostrar(fig, clave="heatmap_estacional")

    # ---- V7 ---------------------------------------------------------------
    if "V7 Composicion del gasto" in activas:
        grupo("En que se gasta")
        with st.container(border=True):
            titulo_grafica("V7", "En que se gasta el dinero del turismo",
                           "¿Que parte de la derrama queda en alojamiento, "
                           "alimentacion, transporte, actividades y artesanias?",
                           ["Treemap", "Nivel de detalle ajustable"])
            profundidad = st.segmented_control(
                "Nivel de detalle",
                ["Region", "Region y destino", "Region, destino y categoria"],
                default="Region y destino", key="prof_treemap",
                label_visibility="collapsed") or "Region y destino"
            mostrar(_treemap(df, profundidad), clave="treemap_gasto")
            if detalle != "Resumen ejecutivo":
                nota("El area de cada rectangulo es proporcional al gasto. "
                     "Ademas del control de arriba, puede tocar un rectangulo "
                     "para bajar un nivel y la barra superior para volver.")

    # ---- V8 ---------------------------------------------------------------
    if "V8 Ocupacion y gasto" in activas:
        grupo("Ocupacion y valor")
        col_c, col_d = st.columns([1.35, 1], gap="small")
        with col_c, st.container(border=True):
            titulo_grafica("V8", "Ocupacion frente a gasto diario",
                           "¿Llenar mas los hoteles viene acompanado de mayor "
                           "gasto por visitante?",
                           ["Dispersion con tendencia"])
            mostrar(_ocupacion_gasto(df, nivel), clave="ocup_gasto")
        with col_d, st.container(border=True):
            lectura(f"Cada punto es un <b>{nivel.lower()}</b> de un destino. "
                    "Cambie <i>Detalle</i> en la barra superior: a nivel mes vera "
                    "la dispersion real; a nivel ano, la senal de fondo. La linea "
                    "gris es la tendencia general y describe una "
                    "<b>asociacion</b>, no una relacion de causa y efecto.")
            corr = df[["ocupacion_hotelera", "gasto_diario_usd"]].corr().iloc[0, 1]
            nota(f"Correlacion observada en el periodo: <b>{corr:.2f}</b>. "
                 "Cerca de 0 significa que ocupacion y gasto se mueven de forma "
                 "practicamente independiente: llenar el hotel no garantiza que "
                 "el visitante gaste mas.")

    # ---- V9 y V10 ---------------------------------------------------------
    quiere_perfil = ("V9 Perfil del visitante" in activas
                     or "V10 Alojamiento" in activas)
    if not quiere_perfil:
        return
    grupo("Perfil del visitante")
    if visitantes.empty:
        sin_datos("La encuesta a pie de destino cubre 2023 en adelante. Amplie "
                  "el periodo en la barra superior para ver el perfil del "
                  "visitante.")
        return

    col_e, col_f = par_columnas("V9 Perfil del visitante" in activas,
                                "V10 Alojamiento" in activas)
    if "V9 Perfil del visitante" in activas:
        with col_e, st.container(border=True):
            titulo_grafica("V9", "Perfil segun con quien viaja",
                           "¿Que segmento deja mas gasto y cual se queda mas "
                           "noches?",
                           ["Diagrama de caja"])
            variable = st.segmented_control(
                "Variable",
                ["gasto_diario_usd", "noches", "calificacion_general"],
                default="gasto_diario_usd", key="var_caja",
                label_visibility="collapsed",
                format_func=lambda v: {"gasto_diario_usd": "Gasto diario",
                                       "noches": "Noches",
                                       "calificacion_general": "Calificacion"}[v]
                ) or "gasto_diario_usd"
            mostrar(_caja(visitantes, variable), clave="caja_perfil")
            if detalle != "Resumen ejecutivo":
                nota("La caja cubre a la mitad central de los encuestados y la "
                     "linea interior es la mediana. Se eligio esta grafica, y no "
                     "un promedio, porque el gasto turistico tiene casos "
                     "extremos que mueven la media.")

    if "V10 Alojamiento" in activas:
        with col_f, st.container(border=True):
            titulo_grafica("V10", "Donde se hospeda cada destino",
                           "¿Que tipo de alojamiento domina y donde tiene "
                           "espacio la oferta certificada?",
                           ["Barras apiladas al 100%"])
            mostrar(_alojamiento(visitantes), clave="alojamiento")
            if detalle != "Resumen ejecutivo":
                nota("Las barras suman 100% en cada destino, asi que comparan "
                     "composicion y no tamano. Los destinos con mucha casa de "
                     "familiares o alojamiento informal son los que menos "
                     "derrama capturan por el lado del hospedaje.")
