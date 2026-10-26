-- Filtro de pandoc para los PDF de docs/.
--
-- 1. Sustituye el encabezado del documento (# titulo, ## subtitulo y el
--    parrafo "**Laboratorio ...** / **Fecha:** ...") por la portada de la
--    UVG, con los datos de docs/pdf/portada.yaml.
-- 2. Antepone un cuadrito del color a cada codigo hexadecimal (`#4361EE`).

local function escapar(s)
  return (s:gsub("&", "&amp;"):gsub("<", "&lt;"):gsub(">", "&gt;"))
end

local function texto(valor)
  return valor and escapar(pandoc.utils.stringify(valor)) or ""
end

function Code(el)
  if el.text:match("^#%x%x%x%x%x%x$") then
    local cuadro = string.format(
      '<span style="display:inline-block;width:9px;height:9px;'
        .. "border-radius:2px;background:%s;"
        .. 'border:1px solid rgba(0,0,0,.15);margin-right:5px"></span>',
      el.text)
    return { pandoc.RawInline("html", cuadro), el }
  end
end

function Pandoc(doc)
  local bloques = doc.blocks
  if #bloques == 0 or bloques[1].t ~= "Header" or bloques[1].level ~= 1 then
    return doc
  end

  local titulo = pandoc.utils.stringify(bloques[1])
  local subtitulo = ""
  local i = 2

  if bloques[i] and bloques[i].t == "Header" and bloques[i].level == 2 then
    subtitulo = pandoc.utils.stringify(bloques[i])
    i = i + 1
  end

  -- La linea "Laboratorio ... / Fecha: ..." ya la da la portada.
  if bloques[i] and bloques[i].t == "Para"
      and pandoc.utils.stringify(bloques[i]):match("^Laboratorio") then
    i = i + 1
  end

  local p = doc.meta.portada or {}
  local documento = escapar(titulo)
  if subtitulo ~= "" then
    documento = documento .. ": " .. escapar(subtitulo)
  end

  local integrantes = {}
  for _, nombre in ipairs(p.integrantes or {}) do
    integrantes[#integrantes + 1] = "<div>" .. texto(nombre) .. "</div>"
  end

  local portada = table.concat({
    '<section class="portada">',
    '<div class="encabezado">',
    '<div class="universidad">' .. texto(p.universidad) .. "</div>",
    "<div>" .. texto(p.curso) .. "</div>",
    "</div>",
    '<img class="logo" src="docs/pdf/logo-uvg.png" alt="Universidad del Valle de Guatemala">',
    '<div class="laboratorio">' .. texto(p.laboratorio) .. "</div>",
    '<div class="tema">' .. texto(p.tema) .. "</div>",
    '<div class="documento">' .. documento .. "</div>",
    '<div class="integrantes">' .. table.concat(integrantes) .. "</div>",
    '<div class="lugar">' .. texto(p.lugar) .. "</div>",
    '<div class="fecha">' .. texto(p.fecha) .. "</div>",
    "</section>",
  })

  local resto = { pandoc.RawBlock("html", portada) }
  for j = i, #bloques do
    resto[#resto + 1] = bloques[j]
  end

  doc.blocks = resto
  doc.meta.pagetitle = doc.meta.pagetitle or titulo
  return doc
end
