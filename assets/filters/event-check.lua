-- Warn when the site is built with a profile that does not match the format
-- in event.yml, e.g. a workshop built with plain `quarto render` (which uses
-- the default profile, course). `pixi run render` picks the right one.

-- format in event.yml -> Quarto profile (keep in step with scripts/site.py)
local profile_of = {
  ["course-7week"] = "course",
  ["workshop-4day"] = "workshop",
  ["workshop-5day"] = "workshop",
  ["self-paced"] = "self-paced",
}

function Meta(meta)
  -- check once per build, on the home page
  local home = pandoc.path.join({ quarto.project.directory, "index.qmd" })
  if pandoc.path.normalize(quarto.doc.input_file) ~= pandoc.path.normalize(home) then
    return
  end
  local format = meta.event and pandoc.utils.stringify(meta.event.format or "") or ""
  local wanted = profile_of[format]
  if not wanted then
    quarto.log.warning("event.yml: unknown format '" .. format .. "'")
    return
  end
  local active = quarto.project.profile or {}
  if type(active) == "string" then active = { active } end
  for _, p in ipairs(active) do
    if p == wanted then return end
  end
  quarto.log.warning("event.yml asks for " .. format .. ", but this build uses the profile '"
    .. table.concat(active, ",") .. "'. Build with `pixi run render`, or add --profile "
    .. wanted .. ".")
end
