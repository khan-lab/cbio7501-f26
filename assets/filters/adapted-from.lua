--[[
Turns the `adapted_from:` and `sources:` front matter of a deck into
attribution that cannot be forgotten: RevealJS decks get a final "Sources"
slide (adapted material first, then the `sources:` list: papers, figures we
link to, data).

On HTML pages `adapted_from:` is a record only: nothing is shown on the page.
Adapted material is credited on pages/credits.qmd, which every page links to
from its footer.

Front matter shape (see CONTRIBUTING.md):

adapted_from:
  - title: "Tools for Reproducible Research: Git"
    url: https://nbisweden.github.io/workshop-reproducible-research/pages/git.html
    authors: "NBIS"
    license: "CC BY 4.0"
    license_url: https://creativecommons.org/licenses/by/4.0/
    accessed: 2026-10-24
    version: "commit 1bce220"
    changes: "Swapped the example for the LTEE project."
sources:
  - "Baker M (2016). 1,500 scientists lift the lid on reproducibility. *Nature* 533:452. <https://doi.org/10.1038/533452a>"
]]

local stringify = pandoc.utils.stringify

local function field(entry, key)
  local value = entry[key]
  if value == nil then
    return nil
  end
  local text = stringify(value)
  if text == "" then
    return nil
  end
  return text
end

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

local function entry_blocks(entry)
  local inl = pandoc.Inlines({})
  local title = field(entry, "title") or field(entry, "url") or "Untitled source"
  local url = field(entry, "url")
  if url then
    inl:insert(pandoc.Link(pandoc.Inlines({ pandoc.Emph(pandoc.Inlines(title)) }), url))
  else
    inl:insert(pandoc.Emph(pandoc.Inlines(title)))
  end
  local authors = field(entry, "authors")
  if authors then
    inl:extend(pandoc.Inlines(" by " .. authors))
  end
  inl:insert(pandoc.Str("."))
  local license = field(entry, "license")
  if license then
    inl:insert(pandoc.Space())
    local license_url = field(entry, "license_url")
    if license_url then
      inl:extend(pandoc.Inlines("License: "))
      inl:insert(pandoc.Link(pandoc.Inlines(license), license_url))
      inl:insert(pandoc.Str("."))
    else
      inl:extend(pandoc.Inlines("License: " .. license .. "."))
    end
  end
  local version = field(entry, "version")
  local accessed = field(entry, "accessed")
  if version or accessed then
    local bits = {}
    if version then table.insert(bits, "version " .. version) end
    if accessed then table.insert(bits, "accessed " .. accessed) end
    inl:insert(pandoc.Space())
    inl:extend(pandoc.Inlines("(" .. table.concat(bits, ", ") .. ")."))
  end
  local blocks = pandoc.Blocks({ pandoc.Plain(inl) })
  if entry["changes"] ~= nil then
    local changes = pandoc.Inlines({ pandoc.Strong(pandoc.Inlines("What we changed:")), pandoc.Space() })
    changes:extend(as_inlines(entry["changes"]))
    blocks:insert(pandoc.Plain(changes))
  end
  return blocks
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
  local adapted = list_of(doc.meta.adapted_from)
  local sources = list_of(doc.meta.sources)

  if quarto.doc.is_format("revealjs") then
    if #adapted == 0 and #sources == 0 then
      return doc
    end
    local items = {}
    for _, entry in ipairs(adapted) do
      local b = entry_blocks(entry)
      b:insert(1, pandoc.Plain(pandoc.Inlines({ pandoc.Strong(pandoc.Inlines("Adapted from:")) })))
      table.insert(items, b)
    end
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
  return doc
end
