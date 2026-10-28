-- Shortcode {{< schedule FORMAT >}}: the schedule of one format, built from
-- schedules/FORMAT.yml and the modules in schedules/modules.yml. Without
-- FORMAT, the format in event.yml. Module links are relative to the site's
-- root folder, so use it on pages there.
--
-- A course file (weeks:) becomes one table, a week per row and a session per
-- column. A workshop file (days:) becomes a table per day, with times
-- computed from the day in event.yml, and a list of the modules it leaves
-- out. In the render output, warnings flag a session that holds more
-- minutes than it has, a morning that runs into lunch, a day that runs past
-- its end, and unknown module ids.

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

local function as_list(value)
  if value == nil then
    return {}
  end
  local t = pandoc.utils.type(value)
  if t == "Inlines" or t == "Blocks" or t == "string" then
    return { value }
  end
  return value
end

local function warn(msg)
  quarto.log.warning("schedule: " .. msg)
end

local function read_yaml(name)
  local path = pandoc.path.join({ quarto.project.directory, "schedules", name })
  local f = io.open(path, "r")
  if f == nil then
    return nil
  end
  local text = f:read("a")
  f:close()
  return pandoc.read("---\n" .. text .. "\n---\n", "markdown").meta
end

-- modules.yml: the modules by id, and their ids in file order
local function read_modules()
  local meta = read_yaml("modules.yml")
  local by_id, order = {}, {}
  for _, m in ipairs(meta and meta.modules or {}) do
    local id = stringify(m.id)
    by_id[id] = m
    table.insert(order, id)
  end
  return by_id, order
end

local function module_inlines(m)
  local out = pandoc.Inlines({ pandoc.Link(as_inlines(m.title):clone(), stringify(m.page)) })
  if m.detail then
    out:insert(pandoc.Space())
    out:extend(as_inlines(m.detail):clone())
  end
  return out
end

-- "(40)" at the end of an item: its minutes
local function trailing_minutes(inlines)
  local last = inlines[#inlines]
  if last and last.t == "Str" then
    local n = last.text:match("^%((%d+)%)$")
    if n then
      return tonumber(n)
    end
  end
  return nil
end

local function without_trailing_minutes(inlines)
  local out = inlines:clone()
  if trailing_minutes(out) then
    out:remove(#out)
    if out[#out] and out[#out].t == "Space" then
      out:remove(#out)
    end
  end
  return out
end

-- An item is a module id, maybe followed by text ("04-git-branches (70)"),
-- or any other text. Returns its inlines and its minutes; marks the module
-- as used.
local function parse_item(item, modules, used, where)
  local inlines = as_inlines(item)
  local first = inlines[1] and inlines[1].t == "Str" and inlines[1].text or ""
  local m = modules[first]
  if m == nil then
    if first:match("^%d%d%w*%-%w") or first:match("^S%d+%-%w") then
      warn(where .. ": unknown module '" .. first .. "' (not in schedules/modules.yml)")
    end
    return inlines:clone(), trailing_minutes(inlines) or 0
  end
  used[first] = true
  local out = module_inlines(m)
  local rest = pandoc.Inlines({})
  for i = 2, #inlines do
    rest:insert(inlines[i])
  end
  if rest[1] and rest[1].t == "Space" then
    rest:remove(1)
  end
  if #rest > 0 then
    out:insert(pandoc.Space())
    out:extend(rest:clone())
  end
  return out, trailing_minutes(inlines) or tonumber(stringify(m.minutes)) or 0
end

local function cell(inlines)
  return { pandoc.Plain(inlines) }
end

-- widths: fractions of the page width (optional; default: automatic)
local function make_table(headers, rows, widths)
  local aligns = {}
  widths = widths or {}
  for i = 1, #headers do
    aligns[i] = pandoc.AlignDefault
    widths[i] = widths[i] or 0
  end
  return pandoc.utils.from_simple_table(pandoc.SimpleTable({}, aligns, widths, headers, rows))
end

local function course(name, sched, modules, order)
  local used = {}
  local headers = { cell(pandoc.Inlines("Week")), cell(pandoc.Inlines("Topic")) }
  for _, s in ipairs(sched.sessions) do
    local title = stringify(s.title)
    if s.minutes then
      title = title .. " (" .. stringify(s.minutes) .. " min)"
    end
    table.insert(headers, cell(pandoc.Inlines(title)))
  end
  local rows = {}
  for w, week in ipairs(sched.weeks) do
    local row = { cell(pandoc.Inlines(tostring(w))), cell(as_inlines(week.topic)) }
    for _, s in ipairs(sched.sessions) do
      local label = "week " .. w .. ", " .. stringify(s.title)
      local inlines, total = pandoc.Inlines({}), 0
      for i, item in ipairs(as_list(week[stringify(s.id)])) do
        local shown, minutes = parse_item(item, modules, used, name .. ", " .. label)
        if i > 1 then
          inlines:extend({ pandoc.Str(";"), pandoc.Space() })
        end
        inlines:extend(shown)
        total = total + minutes
      end
      local length = s.minutes and tonumber(stringify(s.minutes))
      if length and total > length then
        warn(name .. ", " .. label .. ": " .. total .. " minutes planned, the session has " .. length)
      end
      table.insert(row, cell(inlines))
    end
    table.insert(rows, row)
  end
  local unused = {}
  for _, id in ipairs(order) do
    if not used[id] then
      table.insert(unused, id)
    end
  end
  if #unused > 0 then
    io.stderr:write("schedule: " .. name .. ": modules in no session: " .. table.concat(unused, ", ") .. "\n")
  end
  return { make_table(headers, rows) }
end

local function clock(minutes)
  return string.format("%02d:%02d", minutes // 60, minutes % 60)
end

local function minutes_of_day(text, default)
  local h, m = (text or ""):match("^%s*(%d+):(%d+)%s*$")
  if h then
    return tonumber(h) * 60 + tonumber(m)
  end
  return default
end

local number_words = { "one", "two", "three", "four", "five", "six", "seven" }

local function workshop(name, sched, modules, order, event)
  local day = event and event.day or {}
  local start = minutes_of_day(day.start and stringify(day.start), 9 * 60)
  local lunch_at = minutes_of_day(day.lunch and stringify(day.lunch), 12 * 60)
  local day_end = minutes_of_day(day["end"] and stringify(day["end"]), 17 * 60)
  local lunch_len = tonumber(day["lunch-minutes"] and stringify(day["lunch-minutes"]) or "") or 60
  local break_len = tonumber(day["break-minutes"] and stringify(day["break-minutes"]) or "") or 15

  -- dates only for the format this site is set up for
  local first_day
  if event and stringify(event.format or "") == name then
    local y, mo, d = stringify(event["start-date"] or ""):match("^(%d%d%d%d)-(%d%d)-(%d%d)$")
    if y then
      first_day = os.time({ year = tonumber(y), month = tonumber(mo), day = tonumber(d), hour = 12 })
    end
  end

  local blocks, used = pandoc.Blocks({}), {}
  for d, dayplan in ipairs(sched.days) do
    local t, rows = start, {}
    local function add(len, inlines)
      table.insert(rows, { cell(pandoc.Inlines(clock(t) .. "–" .. clock(t + len))), cell(inlines) })
      t = t + len
    end
    for _, item in ipairs(as_list(dayplan.blocks)) do
      local word = stringify(item)
      if word == "break" then
        add(break_len, pandoc.Inlines("Break"))
      elseif word == "lunch" then
        if t > lunch_at then
          warn(name .. ", day " .. d .. ": the morning runs to " .. clock(t) .. ", past lunch at " .. clock(lunch_at))
        end
        t = math.max(t, lunch_at)
        add(lunch_len, pandoc.Inlines("Lunch"))
      else
        local shown, minutes = parse_item(item, modules, used, name .. ", day " .. d)
        add(minutes, without_trailing_minutes(shown))
      end
    end
    if t > day_end then
      warn(name .. ", day " .. d .. ": ends at " .. clock(t) .. ", after " .. clock(day_end))
    end
    local heading = "Day " .. d
    if first_day then
      heading = heading .. ", " .. os.date("%a %d %b", first_day + (d - 1) * 86400)
    end
    local title = pandoc.Inlines(heading .. ": ")
    title:extend(as_inlines(dayplan.title):clone())
    blocks:insert(pandoc.Header(3, title, pandoc.Attr(name .. "-day-" .. d)))
    -- the same column widths every day, so the days line up
    blocks:insert(make_table({ cell(pandoc.Inlines("Time")), cell(pandoc.Inlines("Session")) }, rows, { 0.2, 0.8 }))
  end

  -- what this format leaves out (setup is done before day 1)
  local left_out = pandoc.Inlines({})
  for _, id in ipairs(order) do
    if not used[id] and not modules[id].before then
      if #left_out > 0 then
        left_out:extend({ pandoc.Str(";"), pandoc.Space() })
      end
      left_out:extend(module_inlines(modules[id]))
    end
  end
  if #left_out > 0 then
    local n = #sched.days
    local intro = pandoc.Inlines({ pandoc.Strong(pandoc.Inlines("Not in the " .. (number_words[n] or tostring(n)) .. " days")) })
    intro:extend(pandoc.Inlines(" (self-paced afterwards): "))
    intro:extend(left_out)
    blocks:insert(pandoc.Para(intro))
  end
  return blocks
end

return {
  ["schedule"] = function(args, kwargs, meta)
    local event = meta.event
    local name = args[1] and stringify(args[1]) or stringify(event and event.format or "")
    local sched = read_yaml(name .. ".yml")
    if sched == nil then
      warn("no schedules/" .. name .. ".yml")
      return pandoc.Blocks({})
    end
    local modules, order = read_modules()
    if sched.weeks then
      return course(name, sched, modules, order)
    elseif sched.days then
      return workshop(name, sched, modules, order, event)
    end
    warn("schedules/" .. name .. ".yml has neither weeks: nor days:")
    return pandoc.Blocks({})
  end,
}
