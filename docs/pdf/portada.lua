-- Filtro de pandoc para los PDF de docs/.
--
-- 1. Convierte el encabezado del documento (# titulo, ## subtitulo y el
--    parrafo "**Laboratorio ...** / **Fecha:** ...") en la portada con el
--    degradado del tablero.
-- 2. Antepone un cuadrito del color a cada codigo hexadecimal (`#4361EE`).

local function escapar(s)
  return (s:gsub("&", "&amp;"):gsub("<", "&lt;"):gsub(">", "&gt;"))
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
  local subtitulo, marca = "", ""
  local i = 2

  if bloques[i] and bloques[i].t == "Header" and bloques[i].level == 2 then
    subtitulo = pandoc.utils.stringify(bloques[i])
    i = i + 1
  end

  if bloques[i] and bloques[i].t == "Para" then
    local texto = pandoc.utils.stringify(bloques[i])
    if texto:match("^Laboratorio") then
      local lab, fecha = texto:match("^(.-)%s*Fecha:%s*(.*)$")
      marca = lab and (lab .. " · " .. fecha) or texto
      i = i + 1
    end
  end

  local portada = string.format(
    '<div class="portada"><div class="marca">%s</div>'
      .. '<h1>%s</h1><div class="sub">%s</div></div>',
    escapar(marca), escapar(titulo), escapar(subtitulo))

  local resto = { pandoc.RawBlock("html", portada) }
  for j = i, #bloques do
    resto[#resto + 1] = bloques[j]
  end

  doc.blocks = resto
  doc.meta.pagetitle = doc.meta.pagetitle or titulo
  return doc
end
