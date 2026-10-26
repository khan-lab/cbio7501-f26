--[[
Turns the `sources:` front matter of a deck into attribution that cannot be
forgotten: RevealJS decks get a final "Sources" slide. The list starts with
the material the deck is adapted from, then papers, figures we link to, data.

On HTML pages `sources:` is a record only: nothing is shown on the page.
Adapted material is credited on pages/credits.qmd, which every page links to
from its footer.

Front matter shape (see CONTRIBUTING.md):

sources:
  - "**Adapted from:** *Tools for Reproducible Research: Git*, NBIS. [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). <https://nbisweden.github.io/workshop-reproducible-research/pages/git.html>"
  - "Baker M (2016). 1,500 scientists lift the lid on reproducibility. *Nature* 533:452. <https://doi.org/10.1038/533452a>"
]]

local stringify = pandoc.utils.stringify

local function as_inlines(value)
  if value == nil then
    return pandoc.Inlines({})
  end
  local t = pandoc.utils.type(value)
  if t == "Inlines" then
    return value
  elseif t == "Blocks" then
    return pandoc.utils.blocks_to_inlines(value)
  end
  return pandoc.Inlines({ pandoc.Str(stringify(value)) })
end

local function list_of(meta_value)
  if meta_value == nil then
    return {}
  end
  if pandoc.utils.type(meta_value) == "List" then
    return meta_value
  end
  return { meta_value }
end

local function credits_link()
  return pandoc.Link(pandoc.Inlines("Sources and credits"), "/pages/credits.qmd")
end

function Pandoc(doc)
  if not quarto.doc.is_format("revealjs") then
    return doc
  end
  local sources = list_of(doc.meta.sources)
  if #sources == 0 then
    return doc
  end
  local items = {}
  for _, s in ipairs(sources) do
    table.insert(items, pandoc.Blocks({ pandoc.Plain(as_inlines(s)) }))
  end
  local footer = pandoc.Inlines("Text and slides CC BY 4.0 unless marked otherwise. Full list: ")
  footer:insert(credits_link())
  footer:insert(pandoc.Str("."))
  doc.blocks:insert(pandoc.Header(2, pandoc.Inlines("Sources"),
    pandoc.Attr("sources", { "smaller", "scrollable", "sources-slide" })))
  doc.blocks:insert(pandoc.BulletList(items))
  doc.blocks:insert(pandoc.Para(footer))
  return doc
end
