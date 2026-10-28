-- Steps that need an HPC cluster sit in divs with the class cluster-only:
--
--   ::: {.cluster-only}
--   ...
--   :::
--
-- When event.yml sets a cluster (cluster: enabled: true), they show as
-- written. Otherwise they fold into a collapsed note, so a run without a
-- cluster does not walk through them, and readers with a cluster of their
-- own can still open them.

local enabled = false

local function read_meta(meta)
  local c = meta.event and meta.event.cluster
  enabled = c ~= nil and c.enabled == true
end

local function fold(div)
  if not div.classes:includes("cluster-only") then
    return nil
  end
  if enabled then
    return div.content
  end
  return pandoc.Div(div.content, pandoc.Attr("", { "callout-note" }, {
    collapse = "true",
    title = "Optional: on an HPC cluster",
  }))
end

return {
  { Meta = read_meta },
  { Div = fold },
}
