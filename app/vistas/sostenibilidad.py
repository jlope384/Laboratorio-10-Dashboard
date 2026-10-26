"""Sostenibilidad: presion sobre el destino, huella y beneficio local."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import datos as dt
from componentes import (aplicar_estilo, aviso, grupo, lectura, miles, mostrar,
                         nota, par_columnas, sin_datos, titulo_grafica)
from config import (AZUL, CATEGORICA, CELESTE, COLOR_DESTINO, DIVERGENTE, GRIS,
                    LINEA, MORADO, NARANJA, ROSA, SEMAFORO, TINTA_2, VERDE)

INDICADORES = {
    "co2_ton": ("Emisiones de CO2", "toneladas"),
    "residuos_ton": ("Residuos solidos", "toneladas"),
    "agua_miles_m3": ("Consumo de agua", "miles de m3"),
}


def _desacople(df: pd.DataFrame, indicador: str, nivel: str):
    agg = dt.agregar_tiempo(df, nivel)
    etiqueta, unidad = INDICADORES[indicador]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=agg["periodo"], y=agg["llegadas"], name="Visitantes",
        mode="lines", line=dict(color=AZUL, width=3),
        hovertemplate="%{x|%b %Y}<br>Visitantes: %{y:,.0f}<extra></extra>"))
    fig.add_trace(go.Scatter(
        x=agg["periodo"], y=agg[indicador], name=etiqueta, yaxis="y2",
        mode="lines", line=dict(color=ROSA, width=3),
        hovertemplate="%{x|%b %Y}<br>" + etiqueta + ": %{y:,.0f} " + unidad +
                      "<extra></extra>"))
    aplicar_estilo(fig, alto=400, hovermode="x unified",
                   yaxis=dict(title="Visitantes", gridcolor=LINEA,
                              title_font=dict(color=AZUL)),
                   yaxis2=dict(title=f"{etiqueta} ({unidad})", overlaying="y",
                               side="right", showgrid=False,
                               title_font=dict(color=ROSA)))
    return fig, agg


def _semaforo_presion(df: pd.DataFrame):
    r = (df.groupby("destino", as_index=False)
           .agg(presion=("presion_turistica", "mean"),
                llegadas=("llegadas", "sum"),
                carga=("capacidad_carga", "max"))
           .sort_values("presion"))

    def color(p):
        if p >= 1.0:
            return SEMAFORO["alto"]
        if p >= 0.85:
            return SEMAFORO["medio"]
        return SEMAFORO["bajo"]

    def estado(p):
        if p >= 1.0:
            return "Saturacion"
        if p >= 0.85:
            return "Al limite"
        return "Holgura"

    r["color"] = r["presion"].map(color)
    r["estado"] = r["presion"].map(estado)

    fig = go.Figure(go.Bar(
        x=r["presion"], y=r["destino"], orientation="h",
        marker_color=r["color"], customdata=r[["estado", "llegadas", "carga"]],
        text=[f"{p:.2f} · {e}" for p, e in zip(r["presion"], r["estado"])],
        textposition="outside", textfont=dict(size=11),
        hovertemplate=("<b>%{y}</b><br>Presion media: %{x:.2f}<br>"
                       "Estado: %{customdata[0]}<br>"
                       "Visitantes del periodo: %{customdata[1]:,.0f}<br>"
                       "Capacidad estimada: %{customdata[2]:,.0f} por mes"
                       "<extra></extra>")))
    fig.add_vline(x=1.0, line_dash="dash", line_color=TINTA_2,
                  annotation_text="Capacidad de carga",
                  annotation_position="top",
                  annotation_font=dict(size=11, color=TINTA_2))
    aplicar_estilo(fig, alto=380, xaxis_title="Visitantes / capacidad de carga",
                   yaxis_title="", bargap=0.35)
    fig.update_xaxes(range=[0, max(1.35, r["presion"].max() * 1.35)])
    return fig, r


def _radar(df: pd.DataFrame, destinos: list[str]):
    base = (df.groupby("destino", as_index=False)
              .agg(presion=("presion_turistica", "mean"),
                   empleo=("empleo_local_pct", "mean"),
                   certificacion=("empresas_certificadas_pct", "mean"),
                   satisfaccion=("satisfaccion_promedio", "mean"),
                   llegadas=("llegadas", "sum"),
                   noches=("noches_totales", "sum"),
                   co2=("co2_ton", "sum"),
                   residuos=("residuos_ton", "sum")))
    if base.empty:
        return None
    base["eficiencia_co2"] = base["co2"] / base["noches"] * 1000      # kg por noche
    base["eficiencia_res"] = base["residuos"] / base["noches"] * 1000  # kg por noche

    # Todo se lleva a 0-100 donde MAS ES MEJOR, para que el area del poligono
    # se lea de forma directa: poligono grande = destino mejor posicionado.
    ejes = {
        "Holgura de carga": 100 * (1 - base["presion"].clip(0, 1.4) / 1.4),
        "Empleo local": base["empleo"],
        "Empresas certificadas": base["certificacion"],
        "Satisfaccion": (base["satisfaccion"] - 1) / 4 * 100,
        "Eficiencia en CO2": 100 * (1 - (base["eficiencia_co2"] /
                                         base["eficiencia_co2"].max())),
        "Eficiencia en residuos": 100 * (1 - (base["eficiencia_res"] /
                                              base["eficiencia_res"].max())),
    }
    radar = pd.DataFrame(ejes)
    radar.insert(0, "destino", base["destino"])

    fig = go.Figure()
    for d in destinos:
        fila = radar[radar["destino"] == d]
        if fila.empty:
            continue
        valores = fila.iloc[0, 1:].tolist()
        color = COLOR_DESTINO.get(d, AZUL)
        fig.add_trace(go.Scatterpolar(
            r=valores + [valores[0]],
            theta=list(radar.columns[1:]) + [radar.columns[1]],
            name=d, fill="toself", opacity=0.42,
            line=dict(color=color, width=2),
            hovertemplate="<b>" + d + "</b><br>%{theta}: %{r:.0f} / 100<extra></extra>"))
    aplicar_estilo(fig, alto=430,
                   polar=dict(radialaxis=dict(range=[0, 100], gridcolor=LINEA,
                                              tickfont=dict(size=10)),
                              angularaxis=dict(gridcolor=LINEA),
                              bgcolor="rgba(0,0,0,0)"))
    return fig


def _empleo_certificacion(df: pd.DataFrame):
    r = (df.groupby(["destino", "region"], as_index=False)
           .agg(empleo=("empleo_local_pct", "mean"),
                certificacion=("empresas_certificadas_pct", "mean"),
                gasto=("gasto_total_usd", "sum"),
                satisfaccion=("satisfaccion_promedio", "mean")))
    fig = px.scatter(r, x="certificacion", y="empleo", size="gasto",
                     color="destino", color_discrete_map=COLOR_DESTINO,
                     size_max=42, text="destino",
                     custom_data=["destino", "gasto", "satisfaccion"])
    fig.update_traces(textposition="top center", textfont=dict(size=10),
                      hovertemplate=("<b>%{customdata[0]}</b><br>"
                                     "Empresas certificadas: %{x:.1f}%<br>"
                                     "Empleo local: %{y:.1f}%<br>"
                                     "Derrama: US$ %{customdata[1]:,.0f}<br>"
                                     "Satisfaccion: %{customdata[2]:.2f}<extra></extra>"))
    fig.add_hline(y=r["empleo"].mean(), line_dash="dot", line_color=LINEA)
    fig.add_vline(x=r["certificacion"].mean(), line_dash="dot", line_color=LINEA)
    aplicar_estilo(fig, alto=400, showlegend=False,
                   xaxis_title="Empresas con certificacion sostenible (%)",
                   yaxis_title="Empleo turistico de origen local (%)")
    return fig


def render(ctx: dict) -> None:
    df = ctx["mensual"]
    nivel = ctx["nivel_tiempo"]
    detalle = ctx["detalle"]
    activas = ctx["graficas_activas"]

    if df.empty:
        sin_datos("No hay informacion para la combinacion de filtros elegida.")
        return

    st.markdown(
        '<div class="ots-nota">Un destino sostenible no es el que recibe menos '
        'gente, sino aquel en que el crecimiento de la visita no arrastra al '
        'mismo ritmo el consumo de recursos y si deja beneficio en la economia '
        'local. Esta seccion mide esas dos cosas por separado.</div>',
        unsafe_allow_html=True)

    if "V11 Desacoplamiento" in activas:
        grupo("Crecimiento y huella")
        col_a, col_b = st.columns([1.4, 1], gap="small")
        with col_a, st.container(border=True):
            titulo_grafica("V11", "Crecimiento de la visita frente a su huella",
                           "¿Crece la huella ambiental al mismo ritmo que la "
                           "visita?",
                           ["Doble eje", "Nivel de detalle ajustable"])
            indicador = st.segmented_control(
                "Indicador ambiental", list(INDICADORES),
                default="co2_ton", key="ind_ambiental",
                label_visibility="collapsed",
                format_func=lambda k: INDICADORES[k][0]) or "co2_ton"
            fig, agg = _desacople(df, indicador, nivel)
            mostrar(fig, clave="desacople")
        with col_b, st.container(border=True):
            if len(agg) >= 2:
                prim, ult = agg.iloc[0], agg.iloc[-1]
                g_lleg = dt.variacion(ult["llegadas"], prim["llegadas"])
                g_ind = dt.variacion(ult[indicador], prim[indicador])
                nombre_ind = INDICADORES[indicador][0].lower()
                if g_lleg is not None and g_ind is not None:
                    if g_ind < g_lleg:
                        lectura(f"<b>Hallazgo observado.</b> Entre el primer y "
                                f"el ultimo periodo mostrados, la visita vario "
                                f"{g_lleg:+.1f}% y {nombre_ind} {g_ind:+.1f}%. "
                                "La huella crece menos que la visita: hay "
                                "<b>desacople relativo</b>.")
                    else:
                        aviso(f"<b>Atencion.</b> La visita vario {g_lleg:+.1f}% "
                              f"y {nombre_ind} {g_ind:+.1f}%: la huella crece "
                              "igual o mas rapido que la visita.")
            if detalle != "Resumen ejecutivo":
                nota("La escala izquierda (azul) son visitantes y la derecha "
                     "(rosa) el indicador ambiental. Dos ejes distintos sirven "
                     "para comparar <i>ritmos</i>, no niveles: no tiene sentido "
                     "comparar la altura de una linea con la de la otra, solo "
                     "su pendiente.")

    if "V12 Presion por destino" in activas or "V13 Perfil de sostenibilidad" in activas:
        grupo("Presion sobre el destino")
        col_c, col_d = par_columnas("V12 Presion por destino" in activas,
                                    "V13 Perfil de sostenibilidad" in activas)

        if "V12 Presion por destino" in activas:
            with col_c, st.container(border=True):
                titulo_grafica("V12", "Semaforo de presion turistica",
                               "¿Que destinos estan cerca o por encima de su "
                               "capacidad de carga estimada?",
                               ["Barras con umbral"])
                fig, tabla = _semaforo_presion(df)
                mostrar(fig, clave="semaforo_presion")
                criticos = tabla[tabla["presion"] >= 1.0]["destino"].tolist()
                if criticos:
                    aviso("<b>Por encima de la capacidad estimada:</b> "
                          + ", ".join(criticos) + ". La capacidad de carga es "
                          "una <i>estimacion</i> de estudios de sitio, no una "
                          "medicion: usela como senal para revisar aforos, no "
                          "como cifra exacta.")
                else:
                    nota("Ningun destino supera en promedio su capacidad de "
                         "carga estimada en el periodo seleccionado.")

        if "V13 Perfil de sostenibilidad" in activas:
            with col_d, st.container(border=True):
                titulo_grafica("V13", "Perfil de sostenibilidad comparado",
                               "¿En que dimensiones gana y en cuales pierde "
                               "cada destino frente a los demas?",
                               ["Radar", "Hasta 3 destinos"])
                disponibles = sorted(df["destino"].unique())
                elegidos = st.multiselect(
                    "Destinos a comparar", disponibles,
                    default=disponibles[:3], max_selections=3,
                    key="radar_destinos", label_visibility="collapsed",
                    placeholder="Elija hasta 3 destinos")
                if not elegidos:
                    sin_datos("Elija al menos un destino para dibujar el perfil.")
                else:
                    mostrar(_radar(df, elegidos), clave="radar_sostenibilidad")
                    if detalle != "Resumen ejecutivo":
                        nota("Los seis ejes van de 0 a 100 y estan orientados de "
                             "forma que <b>mas siempre es mejor</b>: un poligono "
                             "grande es un destino mejor posicionado. Las "
                             "eficiencias se miden por visitante-noche y se "
                             "comparan contra el destino de peor desempeno del "
                             "periodo.")

    if "V14 Beneficio local" in activas:
        grupo("Beneficio local")
        col_e, col_f = st.columns([1.35, 1], gap="small")
        with col_e, st.container(border=True):
            titulo_grafica("V14", "Beneficio local y certificacion",
                           "¿El turismo esta dejando empleo local y empujando "
                           "la certificacion sostenible de las empresas?",
                           ["Dispersion con cuadrantes"])
            mostrar(_empleo_certificacion(df), clave="empleo_cert")
        with col_f, st.container(border=True):
            lectura("El cuadrante superior derecho es el objetivo de politica: "
                    "mucho empleo local y muchas empresas certificadas. El "
                    "tamano del circulo es la derrama, asi que un circulo grande "
                    "en el cuadrante inferior izquierdo senala un destino que "
                    "mueve mucho dinero sin que eso se traduzca aun en empleo "
                    "local ni en certificacion.")
            nota("Las lineas punteadas son los promedios del periodo filtrado, "
                 "no metas oficiales.")
