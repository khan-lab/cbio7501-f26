-- Shortcode {{< pixi-version >}}: the version of the Pixi that builds the site,
-- for the page footer (Quarto's own {{< version >}} gives Quarto's).
-- `pixi run` sets PIXI_EXE to the Pixi it runs with; without it, the `pixi`
-- on the PATH is asked. Prints nothing if no Pixi can be found.
local cached

local function pixi_version()
  if cached == nil then
    cached = ""
    local exe = os.getenv("PIXI_EXE") or "pixi"
    local handle = io.popen('"' .. exe .. '" --version')
    if handle ~= nil then
      local out = handle:read("*a") or ""
      handle:close()
      cached = out:match("pixi%s+(%S+)") or ""
    end
  end
  return cached
end

return {
  ["pixi-version"] = function()
    return pandoc.Str(pixi_version())
  end,
}
