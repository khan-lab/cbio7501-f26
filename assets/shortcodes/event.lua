-- Shortcode {{< event KEY >}}: text built from the settings in event.yml,
-- for the places where a plain {{< meta event.KEY >}} would leave stray
-- punctuation when a setting is empty.
--
--   kicker        "CBIO7501 @ MBZUAI - Fall 2026" (code, institution, and
--                 the term or the workshop's dates; empty parts left out)
--   name          "CBIO7501: The Art of ..." or just the title
--   lesson NN     "CBIO7501 · Lesson NN" or "Lesson NN" (deck subtitles)
--   grade KEY     " (40% of the course grade)" for grading: KEY when grading
--                 is enabled, else nothing; `grade KEY short` gives " (40%)"
--   share KEY     just "40", or nothing: for text that is already shown only
--                 when grading is enabled (a {{< meta >}} there would warn
--                 in builds whose event.yml has no such key)
--   instructors   "A", "A and B", "A, B and C"; also helpers
--   dates         a workshop's dates, "18–21 Jan 2027" (from start-date
--                 and the number of days in schedules/FORMAT.yml)
--   cluster       the cluster's name, or "your cluster" when none is set
--   cluster-info  a sentence with the cluster's login host and user guide,
--                 or nothing
--   details       the workshop's facts, two to a row: when, where,
--                 registration, contact, people and links; empty settings
--                 are left out (styles: "Event details" in styles.scss)
--   register      a "Register" button for links: registration, or nothing

local stringify = pandoc.utils.stringify

local function text(value)
  if value == nil then
    return ""
  end
  return stringify(value)
end

local function names(list)
  local out = {}
  for _, v in ipairs(list or {}) do
    local s = text(v)
    if s ~= "" then
      table.insert(out, s)
    end
  end
  if #out <= 1 then
    return out[1] or ""
  end
  return table.concat(out, ", ", 1, #out - 1) .. " and " .. out[#out]
end

local function days_in(format)
  local path = pandoc.path.join({ quarto.project.directory, "schedules", format .. ".yml" })
  local f = io.open(path, "r")
  if f == nil then
    return nil
  end
  local yaml = f:read("a")
  f:close()
  local meta = pandoc.read("---\n" .. yaml .. "\n---\n", "markdown").meta
  return meta.days and #meta.days or nil
end

local function dates(event)
  local y, m, d = text(event["start-date"]):match("^(%d%d%d%d)-(%d%d)-(%d%d)$")
  local n = days_in(text(event.format))
  if not y or not n then
    return ""
  end
  local first = os.time({ year = tonumber(y), month = tonumber(m), day = tonumber(d), hour = 12 })
  local last = first + (n - 1) * 86400
  local function day(t) return tostring(tonumber(os.date("%d", t))) end
  if n == 1 then
    return day(first) .. " " .. os.date("%b %Y", first)
  elseif os.date("%m%Y", first) == os.date("%m%Y", last) then
    return day(first) .. "–" .. day(last) .. " " .. os.date("%b %Y", last)
  end
  return day(first) .. " " .. os.date("%b", first) .. " – " .. day(last) .. " " .. os.date("%b %Y", last)
end

-- grading: KEY from event.yml, or "" when grading is off or KEY is not set
local function share_of(event, key)
  local g = event.grading or {}
  if g.enabled ~= true then
    return ""
  end
  return text(g[key])
end

local function cluster_name(event)
  local c = event.cluster
  if c and c.enabled == true and text(c.name) ~= "" then
    return text(c.name)
  end
  return "your cluster"
end

local function md(s)
  return pandoc.read(s, "markdown").blocks
end

local function md_inlines(s)
  return pandoc.utils.blocks_to_inlines(md(s))
end

local function details(event)
  local facts = {}
  local function add(label, value)
    if value ~= "" then
      table.insert(facts, "::: {.event-fact}\n[" .. label .. "]{.event-fact-label} ["
        .. value .. "]{.event-fact-value}\n:::")
    end
  end
  local when = dates(event)
  local day = event.day or {}
  if when ~= "" and text(day.start) ~= "" and text(day["end"]) ~= "" then
    when = when .. ", " .. text(day.start) .. "–" .. text(day["end"])
  end
  add("When", when)
  local where = text(event.venue)
  if text(event.online) ~= "" then
    where = (where ~= "" and where .. "; " or "") .. "online: <" .. text(event.online) .. ">"
  end
  add("Where", where)
  local links = event.links or {}
  if text(links.registration) ~= "" then
    add("Registration", "[Register for the workshop](" .. text(links.registration) .. ")")
  end
  if text(event.contact) ~= "" then
    add("Contact", "<" .. text(event.contact) .. ">")
  end
  add("Instructors", names(event.instructors))
  add("Helpers", names(event.helpers))
  local shown = {}
  for _, pair in ipairs({
    { "notes", "Shared notes" }, { "chat", "Chat" },
    { "pre-survey", "Survey before" }, { "post-survey", "Survey after" },
    { "code-of-conduct", "Code of conduct" },
  }) do
    local url = text(links[pair[1]])
    if url ~= "" then
      table.insert(shown, "[" .. pair[2] .. "](" .. url .. ")")
    end
  end
  add("Links", table.concat(shown, " · "))
  if #facts == 0 then
    return pandoc.Blocks({})
  end
  return md(":::: {.event-details}\n" .. table.concat(facts, "\n") .. "\n::::")
end

return {
  ["event"] = function(args, kwargs, meta)
    local event = meta.event or {}
    local key = args[1] and text(args[1]) or ""
    local code, title = text(event.code), text(event.title)
    if key == "kicker" then
      local s = code
      if text(event.institution) ~= "" then
        s = s .. (s ~= "" and " @ " or "") .. text(event.institution)
      end
      local when = text(event.term)
      if when == "" then
        when = dates(event)
      end
      if when ~= "" then
        s = s .. (s ~= "" and " - " or "") .. when
      end
      return pandoc.Inlines(s)
    elseif key == "name" then
      return pandoc.Inlines(code ~= "" and (code .. ": " .. title) or title)
    elseif key == "lesson" then
      local n = args[2] and text(args[2]) or ""
      return pandoc.Inlines((code ~= "" and (code .. " · ") or "") .. "Lesson " .. n)
    elseif key == "grade" then
      local share = args[2] and share_of(event, text(args[2])) or ""
      if share == "" then
        return pandoc.Inlines({})
      end
      local short = args[3] and text(args[3]) == "short"
      local out = pandoc.Inlines({ pandoc.Space() })
      out:extend(pandoc.Inlines("(" .. share .. "%" .. (short and ")" or " of the course grade)")))
      return out
    elseif key == "share" then
      return pandoc.Inlines(args[2] and share_of(event, text(args[2])) or "")
    elseif key == "instructors" or key == "helpers" then
      return pandoc.Inlines(names(event[key]))
    elseif key == "dates" then
      return pandoc.Inlines(dates(event))
    elseif key == "cluster" then
      return pandoc.Inlines(cluster_name(event))
    elseif key == "cluster-info" then
      local c = event.cluster or {}
      if c.enabled ~= true then
        return pandoc.Blocks({})
      end
      local parts = {}
      if text(c.login) ~= "" then
        table.insert(parts, "log in with `ssh YOUR-USER@" .. text(c.login) .. "`")
      end
      if text(c.docs) ~= "" then
        table.insert(parts, "see its [user guide](" .. text(c.docs) .. ")")
      end
      if #parts == 0 then
        return pandoc.Blocks({})
      end
      return md("On " .. cluster_name(event) .. ", " .. table.concat(parts, " and ") .. ".")
    elseif key == "details" then
      return details(event)
    elseif key == "register" then
      local url = text((event.links or {}).registration)
      if url == "" then
        return pandoc.Inlines({})
      end
      return pandoc.Inlines({ pandoc.Link("Register", url, "",
        pandoc.Attr("", { "btn", "btn-primary", "home-register" })) })
    end
    quarto.log.warning("event: unknown key '" .. key .. "'")
    return pandoc.Inlines({})
  end,
}
