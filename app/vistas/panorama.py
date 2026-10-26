"""Panorama: estado general del destino y el par enlazado V1-V2-V3."""

from __future__ import annotations

import altair as alt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import datos as dt
from componentes import (aplicar_estilo, dinero, grupo, kpi, lectura, miles,
                         mostrar, mostrar_tactil, nota, par_columnas,
                         sin_datos, titulo_grafica)
from config import (AZUL, COLOR_DESTINO, DIVERGENTE, GRIS, IOS_SEC, LINEA,
                    NARANJA, ROSA, TINTA, VERDE)


# --------------------------------------------------------------------------
def _kpis(df: pd.DataFrame, previo: pd.DataFrame) -> None:
    llegadas = df["llegadas"].sum()
    gasto = df["gasto_total_usd"].sum()
    peso = max(df["llegadas"].sum(), 1)
    estancia = (df["estancia_promedio"] * df["llegadas"]).sum() / peso
    satisf = (df["satisfaccion_promedio"] * df["llegadas"]).sum() / peso

    v_lleg = dt.variacion(llegadas, previo["llegadas"].sum()) if len(previo) else None
    v_gasto = dt.variacion(gasto, previo["gasto_total_usd"].sum()) if len(previo) else None
    sub = "frente al periodo anterior"

    c1, c2, c3, c4 = st.columns(4, gap="small")
    with c1:
        with st.container(border=True):
            kpi("Visitantes", miles(llegadas),
                sub if v_lleg is not None else "sin periodo comparable",
                "azul", v_lleg)
    with c2:
        with st.container(border=True):
            kpi("Derrama economica", dinero(gasto),
                sub if v_gasto is not None else "sin periodo comparable",
                "naranja", v_gasto)
    with c3:
        with st.container(border=True):
            kpi("Estancia media", f"{estancia:.1f} noches",
                "noches por visitante", "verde")
    with c4:
        with st.container(border=True):
            kpi("Satisfaccion", f"{satisf:.2f} / 5",
                "encuesta a pie de destino", "morado")


def _mapa(df: pd.DataFrame, foco: str | None):
    resumen = (df.groupby(["destino", "region", "lat", "lon"], as_index=False)
                 .agg(llegadas=("llegadas", "sum"),
                      gasto=("gasto_total_usd", "sum"),
                      presion=("presion_turistica", "mean"),
                      satisfaccion=("satisfaccion_promedio", "mean")))
    resumen["gasto_fmt"] = resumen["gasto"].map(dinero)
    anchos = [3.5 if d == foco else 1.0 for d in resumen["destino"]]
    bordes = [TINTA if d == foco else "white" for d in resumen["destino"]]

    fig = px.scatter_geo(
        resumen, lat="lat", lon="lon", size="llegadas",
        color="presion", color_continuous_scale=DIVERGENTE,
        range_color=(0.4, 1.3), size_max=44,
        custom_data=["destino", "llegadas", "gasto_fmt", "presion", "satisfaccion"])
    fig.update_traces(
        marker=dict(line=dict(width=anchos, color=bordes)),
        hovertemplate=("<b>%{customdata[0]}</b><br>"
                       "Visitantes: %{customdata[1]:,.0f}<br>"
                       "Derrama: %{customdata[2]}<br>"
                       "Presion turistica: %{customdata[3]:.2f}<br>"
                       "Satisfaccion: %{customdata[4]:.2f} / 5<extra></extra>"))
    fig.update_geos(lonaxis_range=[-92.7, -87.9], lataxis_range=[13.3, 18.1],
                    projection_type="mercator", resolution=50,
                    showcountries=True, countrycolor="#C9CBD4",
                    showsubunits=True, subunitcolor="#E2E3EA",
                    landcolor="#FAFAFC", lakecolor="#E6F2FA",
                    showocean=True, oceancolor="#EDF4FA",
                    showframe=False, coastlinecolor="#C9CBD4")
    aplicar_estilo(fig, alto=420,
                   coloraxis_colorbar=dict(
                       title="Presion", thickness=10, len=0.62, x=1.0,
                       tickvals=[0.5, 0.9, 1.25],
                       ticktext=["Holgura", "Equilibrio", "Saturacion"],
                       tickfont=dict(size=10)))
    return fig


def _serie(df: pd.DataFrame, nivel: str, foco: str | None):
    total = dt.agregar_tiempo(df, nivel)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=total["periodo"], y=total["llegadas"], name="Todos los destinos",
        mode="lines", line=dict(color=GRIS, width=2, shape="spline"),
        fill="tozeroy", fillcolor="rgba(128,137,168,0.10)",
        hovertemplate="%{x|%b %Y}<br>Total: %{y:,.0f} visitantes<extra></extra>"))

    if foco:
        sub = dt.agregar_tiempo(df[df["destino"] == foco], nivel)
        if len(sub):
            fig.add_trace(go.Scatter(
                x=sub["periodo"], y=sub["llegadas"], name=foco, mode="lines",
                line=dict(color=COLOR_DESTINO.get(foco, AZUL), width=3,
                          shape="spline"),
                hovertemplate="%{x|%b %Y}<br>" + foco + ": %{y:,.0f}<extra></extra>"))

    aplicar_estilo(fig, alto=420, yaxis_title="Visitantes", xaxis_title="",
                   hovermode="x unified")
    if total["periodo"].min() <= pd.Timestamp("2020-03-01") <= total["periodo"].max():
        # Igual que en la seccion de modelos: la banda va sin etiqueta y la
        # etiqueta se agrega aparte, por el mismo fallo de plotly con fechas.
        fig.add_vrect(x0="2020-03-01", x1="2021-06-01", fillcolor=ROSA,
                      opacity=0.07, line_width=0)
        fig.add_annotation(x="2020-03-01", xref="x", yref="paper", y=1.0,
                           yanchor="bottom", xanchor="left", showarrow=False,
                           text="Cierre por pandemia",
                           font=dict(size=11, color=ROSA))
    return fig


def _ranking_tactil(df: pd.DataFrame, foco: str | None):
    """V3 en Altair: el toque sobre una barra es el origen del enlace."""
    r = (df.groupby("destino", as_index=False)
           .agg(llegadas=("llegadas", "sum"), gasto=("gasto_total_usd", "sum")))
    r["gasto_visitante"] = r["gasto"] / r["llegadas"]
    r["etiqueta"] = r["llegadas"].map(miles)

    toque = alt.selection_point(fields=["destino"], name="toque", empty=True)
    dominio = list(COLOR_DESTINO)
    rango = [COLOR_DESTINO[d] for d in dominio]

    base = alt.Chart(r).encode(
        y=alt.Y("destino:N", sort="-x", title=None,
                axis=alt.Axis(labelLimit=180)),
        x=alt.X("llegadas:Q", title="Visitantes del periodo",
                axis=alt.Axis(format="~s")),
    )
    barras = base.mark_bar(cornerRadiusEnd=7, height=20).encode(
        color=alt.condition(
            toque if foco is None else alt.datum.destino == foco,
            alt.Color("destino:N",
                      scale=alt.Scale(domain=dominio, range=rango), legend=None),
            alt.value("#D8D8DE")),
        tooltip=[alt.Tooltip("destino:N", title="Destino"),
                 alt.Tooltip("llegadas:Q", title="Visitantes", format=",.0f"),
                 alt.Tooltip("gasto_visitante:Q", title="Gasto por visitante",
                             format="$,.0f")],
    ).add_params(toque)
    texto = base.mark_text(align="left", dx=6, fontSize=11, color=IOS_SEC
                           ).encode(text="etiqueta:N")
    return (barras + texto).properties(height=max(180, 42 * len(r)))


def _volumen_valor(df: pd.DataFrame):
    r = (df.groupby(["destino", "region"], as_index=False)
           .agg(llegadas=("llegadas", "sum"),
                gasto=("gasto_total_usd", "sum"),
                estancia=("estancia_promedio", "mean"),
                satisfaccion=("satisfaccion_promedio", "mean")))
    r["gasto_visitante"] = r["gasto"] / r["llegadas"]
    fig = px.scatter(r, x="llegadas", y="gasto_visitante", size="estancia",
                     color="destino", color_discrete_map=COLOR_DESTINO,
                     size_max=40, text="destino",
                     custom_data=["destino", "estancia", "satisfaccion"])
    fig.update_traces(textposition="top center", textfont=dict(size=10),
                      hovertemplate=("<b>%{customdata[0]}</b><br>"
                                     "Visitantes: %{x:,.0f}<br>"
                                     "Gasto por visitante: US$ %{y:,.0f}<br>"
                                     "Estancia: %{customdata[1]:.1f} noches<br>"
                                     "Satisfaccion: %{customdata[2]:.2f}"
                                     "<extra></extra>"))
    fig.add_hline(y=r["gasto_visitante"].mean(), line_dash="dot", line_color=LINEA)
    fig.add_vline(x=r["llegadas"].mean(), line_dash="dot", line_color=LINEA)
    aplicar_estilo(fig, alto=380, showlegend=False,
                   xaxis_title="Visitantes del periodo",
                   yaxis_title="Gasto por visitante (USD)")
    return fig


# --------------------------------------------------------------------------
def render(ctx: dict) -> None:
    df = ctx["mensual"]
    nivel = ctx["nivel_tiempo"]
    detalle = ctx["detalle"]
    activas = ctx["graficas_activas"]

    if df.empty:
        sin_datos("No hay informacion para la combinacion de filtros elegida. "
                  "Amplie el periodo o quite filtros de lugar en la barra "
                  "superior.")
        return

    grupo("Resumen del periodo")
    _kpis(df, ctx["mensual_previo"])

    foco = st.session_state.get("destino_foco")
    ver = {v: v in activas for v in
           ["V1 Mapa de presion", "V2 Evolucion de la visita",
            "V3 Ranking de destinos", "V4 Volumen frente a valor"]}

    if ver["V1 Mapa de presion"] or ver["V2 Evolucion de la visita"]:
        grupo("Donde y cuando")
        col_a, col_b = par_columnas(ver["V1 Mapa de presion"],
                                    ver["V2 Evolucion de la visita"],
                                    (1, 1.18))

        if ver["V1 Mapa de presion"]:
            with col_a, st.container(border=True):
                titulo_grafica("V1", "Donde esta la presion turistica",
                               "¿Que destinos concentran la visita y cuales se "
                               "acercan a su capacidad de carga?",
                               ["Mapa", "Enlazada con V3"])
                mostrar(_mapa(df, foco), clave="mapa_destinos")

        if ver["V2 Evolucion de la visita"]:
            with col_b, st.container(border=True):
                titulo_grafica("V2", "Evolucion de la visita",
                               "¿Como se mueve la demanda y como se compara el "
                               "destino enfocado con el conjunto?",
                               ["Serie de tiempo", "Enlazada con V3"])
                mostrar(_serie(df, nivel, foco), clave="serie_panorama")

    if ver["V3 Ranking de destinos"] or ver["V4 Volumen frente a valor"]:
        grupo("Peso de cada destino")
        col_c, col_d = par_columnas(ver["V3 Ranking de destinos"],
                                    ver["V4 Volumen frente a valor"],
                                    (1, 1.05))

        if ver["V3 Ranking de destinos"]:
            with col_c, st.container(border=True):
                titulo_grafica("V3", "Ranking de destinos",
                               "¿Cual es el peso relativo de cada destino en el "
                               "total de visitantes?",
                               ["Barras", "Toque para enfocar",
                                "Enlazada con V1 y V2"])
                elegido = mostrar_tactil(_ranking_tactil(df, foco),
                                         clave="ranking_destinos",
                                         campo="destino")
                if elegido and elegido != foco:
                    st.session_state["destino_foco"] = elegido
                    st.rerun()
                if foco:
                    lectura(
                        f"<b>Enfoque activo: {foco}.</b> El mapa (V1) lo resalta "
                        "con un anillo oscuro, la serie (V2) dibuja su linea de "
                        "color sobre el total, y las secciones <i>Explorar</i> y "
                        "<i>Sostenibilidad</i> se recalculan solo para ese "
                        "destino. Para volver al total, use <i>Quitar enfoque</i> "
                        "arriba.")
                else:
                    lectura("Toque una barra para enfocar un destino: cambian el "
                            "mapa (V1), la serie de tiempo (V2) y las secciones "
                            "de detalle.")

        if ver["V4 Volumen frente a valor"]:
            with col_d, st.container(border=True):
                titulo_grafica("V4", "Volumen frente a valor",
                               "¿Que destinos reciben mucha gente y cuales "
                               "reciben gente que gasta mas?",
                               ["Dispersion"])
                mostrar(_volumen_valor(df), clave="volumen_valor")
                if detalle != "Resumen ejecutivo":
                    nota("Las lineas punteadas marcan el promedio de cada eje. "
                         "Arriba a la derecha: mucha visita y alto gasto. Abajo a "
                         "la derecha: visita masiva con bajo gasto por persona, "
                         "donde conviene revisar la oferta antes que atraer mas "
                         "volumen.")
