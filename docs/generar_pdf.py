"""
Convierte el documento de diseno de Markdown a PDF.

Flujo: Markdown -> HTML con la identidad visual del tablero -> PDF impreso
por Chrome en modo headless. Se eligio asi, y no pandoc o weasyprint, porque
no necesita instalar nada fuera del entorno de Python: Chrome ya esta en la
maquina y es el mismo motor que renderiza el tablero, de modo que el PDF
hereda la misma paleta y la misma tipografia.

Uso:
    python docs/generar_pdf.py                       # documento_diseno.md
    python docs/generar_pdf.py docs/codebook.md      # cualquier otro .md
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import markdown

DOCS = Path(__file__).resolve().parent
RAIZ = DOCS.parent
sys.path.insert(0, str(RAIZ / "app"))

from config import (AZUL, CELESTE, IOS_SEC, LINEA, MORADO, NARANJA, ROSA,  # noqa: E402
                    TINTA, TINTA_2, VERDE, VIOLETA)

NAVEGADORES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    shutil.which("google-chrome") or "",
    shutil.which("chromium") or "",
]

HOJA = f"""
@page {{
    size: Letter;
    margin: 20mm 17mm 18mm 17mm;
}}

:root {{ color-scheme: light; }}

body {{
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", Inter,
                 "Helvetica Neue", Arial, sans-serif;
    color: {TINTA};
    font-size: 10.2pt;
    line-height: 1.5;
    margin: 0;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
}}

/* ----------------------------------------------------------- portada -- */
.portada {{
    background: linear-gradient(135deg, {VIOLETA} 0%, {AZUL} 62%, {CELESTE} 100%);
    color: #fff;
    border-radius: 16px;
    padding: 26px 28px;
    margin-bottom: 22px;
}}
.portada .marca {{ font-size: 9.5pt; letter-spacing: .08em;
    text-transform: uppercase; opacity: .85; }}
.portada h1 {{ font-size: 23pt; margin: 6px 0 2px 0; color: #fff;
    border: 0; padding: 0; letter-spacing: -.02em; }}
.portada .sub {{ font-size: 12pt; opacity: .92; }}

/* --------------------------------------------------------- jerarquia -- */
h1 {{ font-size: 16.5pt; margin: 26px 0 8px 0; color: {TINTA};
     border-bottom: 2px solid {AZUL}; padding-bottom: 5px;
     page-break-after: avoid; letter-spacing: -.015em; }}
h2 {{ font-size: 13.5pt; margin: 22px 0 7px 0; color: {TINTA};
     page-break-after: avoid; letter-spacing: -.012em; }}
h3 {{ font-size: 11.5pt; margin: 16px 0 5px 0; color: {AZUL};
     page-break-after: avoid; }}
h1 + h2 {{ margin-top: 10px; }}

p {{ margin: 7px 0; text-align: justify; }}
ul, ol {{ margin: 7px 0 7px 18px; padding-left: 8px; }}
li {{ margin: 3px 0; }}
strong {{ color: {TINTA}; font-weight: 650; }}
hr {{ border: 0; border-top: 1px solid {LINEA}; margin: 20px 0; }}

/* ----------------------------------------------------------- tablas -- */
table {{
    width: 100%; border-collapse: collapse; margin: 12px 0;
    font-size: 8.8pt; page-break-inside: auto;
}}
thead {{ display: table-header-group; }}
tr {{ page-break-inside: avoid; }}
th {{
    background: {AZUL}; color: #fff; text-align: left;
    padding: 7px 9px; font-weight: 600; font-size: 8.6pt;
    border: 1px solid {AZUL};
}}
td {{ padding: 6px 9px; border: 1px solid {LINEA}; vertical-align: top; }}
tbody tr:nth-child(even) td {{ background: #F5F6FD; }}

/* ------------------------------------------------- codigo y bosquejo -- */
pre {{
    background: #F5F6FD; border: 1px solid {LINEA}; border-radius: 10px;
    padding: 12px 14px; font-size: 7.4pt; line-height: 1.32;
    overflow: visible; white-space: pre-wrap; page-break-inside: avoid;
    font-family: "SF Mono", ui-monospace, Menlo, Consolas, monospace;
    color: {TINTA_2};
}}
code {{
    font-family: "SF Mono", ui-monospace, Menlo, Consolas, monospace;
    font-size: 8.6pt; background: #EDEFFA; color: {MORADO};
    padding: 1px 4px; border-radius: 4px;
}}
pre code {{ background: none; color: inherit; padding: 0; font-size: 7.4pt; }}

/* --------------------------------------------------------- citas ------ */
blockquote {{
    margin: 12px 0; padding: 10px 14px; border-left: 3px solid {NARANJA};
    background: #FFF6EA; border-radius: 0 10px 10px 0;
    color: {TINTA_2}; font-size: 9.4pt;
}}
blockquote p {{ margin: 0; text-align: left; }}

/* ------------------------------------------------- muestras de color -- */
td code {{ background: none; color: {TINTA_2}; }}
"""

MUESTRAS = {  # hex -> se pinta un cuadrito antes del codigo en las tablas
    "#4361EE": AZUL, "#FFA630": NARANJA, "#60A125": VERDE, "#F72585": ROSA,
    "#A2158D": MORADO, "#4D0A99": VIOLETA, "#4CC9F0": CELESTE,
    "#FFA5A3": "#FFA5A3", "#B5BDE3": "#B5BDE3", "#2E3B73": "#2E3B73",
    "#5A6798": "#5A6798",
}


def _pintar_muestras(html: str) -> str:
    """Antepone un cuadrito del color a cada codigo hexadecimal de la tabla."""
    for hexa, color in MUESTRAS.items():
        cuadro = (f'<span style="display:inline-block;width:9px;height:9px;'
                  f'border-radius:2px;background:{color};'
                  f'border:1px solid rgba(0,0,0,.15);margin-right:5px"></span>')
        html = html.replace(f"<code>{hexa}</code>",
                            f"{cuadro}<code>{hexa}</code>")
    return html


def _portada(cuerpo: str) -> tuple[str, str]:
    """Separa el encabezado del documento y lo convierte en portada."""
    lineas = cuerpo.splitlines()
    titulo = subtitulo = marca = ""
    resto = lineas
    for i, linea in enumerate(lineas):
        if linea.startswith("# "):
            titulo = linea[2:].strip()
        elif linea.startswith("## ") and titulo and not subtitulo:
            subtitulo = linea[3:].strip()
        elif linea.startswith("**Laboratorio"):
            marca = linea.replace("**", "").strip()
        elif linea.startswith("**Fecha:**"):
            marca += " · " + linea.replace("**Fecha:**", "").replace("**", "").strip()
            resto = lineas[i + 1:]
            break
    portada = (f'<div class="portada"><div class="marca">{marca}</div>'
               f'<h1>{titulo}</h1><div class="sub">{subtitulo}</div></div>')
    return portada, "\n".join(resto)


def convertir(origen: Path) -> Path:
    destino = origen.with_suffix(".pdf")
    texto = origen.read_text(encoding="utf-8")
    portada, cuerpo = _portada(texto)

    cuerpo_html = markdown.markdown(
        cuerpo, extensions=["tables", "fenced_code", "sane_lists", "attr_list"])
    cuerpo_html = _pintar_muestras(cuerpo_html)

    html = (f'<!doctype html><html lang="es"><head><meta charset="utf-8">'
            f"<title>{origen.stem}</title><style>{HOJA}</style></head>"
            f"<body>{portada}{cuerpo_html}</body></html>")

    navegador = next((n for n in NAVEGADORES if n and Path(n).exists()), None)
    if navegador is None:
        raise SystemExit("No se encontro Chrome, Chromium ni Edge para imprimir "
                         "el PDF. Instale uno o exporte el HTML a mano.")

    with tempfile.TemporaryDirectory() as tmp:
        ruta_html = Path(tmp) / "documento.html"
        ruta_html.write_text(html, encoding="utf-8")
        subprocess.run(
            [navegador, "--headless", "--disable-gpu", "--no-sandbox",
             f"--user-data-dir={tmp}/perfil",      # no toca el perfil del usuario
             "--no-pdf-header-footer",
             "--virtual-time-budget=4000",
             f"--print-to-pdf={destino}", ruta_html.as_uri()],
            check=True, capture_output=True)
    return destino


if __name__ == "__main__":
    entrada = Path(sys.argv[1]) if len(sys.argv) > 1 else DOCS / "documento_diseno.md"
    salida = convertir(entrada.resolve())
    print(f"{salida}  ({salida.stat().st_size / 1024:.0f} KB)")
