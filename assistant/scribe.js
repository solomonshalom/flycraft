// scribe.js — the research assistant's Minecraft body.  It follows the flies, watches them, and carries out
// guidance (staging encounters, placing stimuli) on behalf of assistant.py, which talks to it over a local WebSocket.
//
//   node assistant/scribe.js --name observer --port 25566 --roster logs/roster_live.json --follow fly1 --ws 8790
//        [--distance 4] [--height 2] [--gamemode spectator|creative|none] [--host 127.0.0.1] [--version 1.20.4]
//
// The body is a *ghost* to the flies: bot/observe.js never lets a player named observer*/scribe* (or rostered as
// 'ghost') into a fly's eyes, antennae or contact sense, and bot.js never lets a fly attack it. In spectator mode it
// also has no collision box, so it cannot push a fly.  It never emits ♪ (song) and never touches a non-fly player.
//
// Protocol (JSON lines over ws://127.0.0.1:<ws>):
//   -> {type:'snapshot', t, flies:[{name,sex,x,y,z,yaw,on_ground,block_below,on_food,in_water}], pairs:[{a,b,dist}],
//       humans:[{name,x,y,z}], mobs:[{name,dist_to_followed}], following, time_of_day, raining}       every second
//   -> {type:'event', t, kind, ...}   chat | song | feed | reject | hurt | died | joined | left | respawn
//   <- {id, cmd:'follow'|'tp'|'bring'|'place_near'|'clear_near'|'setblock'|'fill'|'summon'|'time'|'weather'|'say'|'cmd'|'snapshot', ...}
//   -> {type:'result', id, ok, msg}
const fs = require('fs')
const path = require('path')
module.paths.unshift(path.join(__dirname, '..', 'bot', 'node_modules'))   // share the fly body's dependencies
const mineflayer = require('mineflayer')
const { WebSocketServer } = require('ws')
const { Vec3 } = require('vec3')
const argv = require('minimist')(process.argv.slice(2))
const { FOOD } = require('../bot/observe')

const NAME = argv.name || 'observer'
const HOST = argv.host || '127.0.0.1'
const PORT = +(argv.port || 25566)
const WS_PORT = +(argv.ws || 8790)
const MC_VERSION = argv.version || '1.20.4'
const GAMEMODE = argv.gamemode || 'spectator'
const DIST = +(argv.distance || 4)
const HEIGHT = +(argv.height || 2)
let following = argv.follow || 'nearest'          // fly name | 'nearest' | 'none'
const roster = argv.roster && fs.existsSync(argv.roster) ? JSON.parse(fs.readFileSync(argv.roster, 'utf8')) : {}
const WATER = new Set(['water', 'bubble_column', 'kelp', 'seagrass'])

const isFly = (n) => !!(n && roster[n] !== 'ghost' && (roster[n] || /^fly\d/i.test(n)))
const sexOf = (n) => roster[n] || (/^fly\d*m/i.test(n || '') ? 'male' : 'female')
const isGhost = (n) => !!(n && (roster[n] === 'ghost' || /^(observer|scribe)/i.test(n)))
const r2 = (v) => Math.round(v * 100) / 100
const log = (...a) => console.log(`[${NAME}]`, ...a)

const bot = mineflayer.createBot({ host: HOST, port: PORT, username: NAME, version: MC_VERSION, auth: 'offline' })
const clients = new Set()
let lastTp = 0, lastTpPos = null
let smoothHeading = null      // the fly turns constantly; follow a slowly-averaged heading so the camera does not whip around

function send(obj) {
  const s = JSON.stringify(obj)
  for (const c of clients) if (c.readyState === 1) c.send(s)
}
const event = (kind, extra = {}) => send({ type: 'event', t: Date.now() / 1000, kind, ...extra })

function flyEntities() {
  const out = []
  for (const e of Object.values(bot.entities)) {
    if (e === bot.entity || e.type !== 'player' || !e.position || !isFly(e.username)) continue
    out.push(e)
  }
  return out
}
function flyByName(name) { return flyEntities().find(e => e.username === name) || null }

// Minecraft yaw (degrees): 0 = south (+z), 90 = west (-x); entity.yaw (radians) uses the same convention
const headingOf = (e) => new Vec3(-Math.sin(e.yaw), 0, -Math.cos(e.yaw))
function lookAngles(from, to) {
  const d = to.minus(from)
  const yaw = -Math.atan2(d.x, d.z) * 180 / Math.PI
  const pitch = -Math.asin(d.y / Math.max(1e-6, d.norm())) * 180 / Math.PI
  return { yaw: r2(yaw), pitch: r2(pitch) }
}

// find standing room for a block/entity near (x, y, z): the first air block with something solid under it, +-3 blocks
function groundAt(x, y, z) {
  for (const dy of [0, 1, -1, 2, -2, 3, -3]) {
    const p = new Vec3(Math.floor(x), Math.floor(y + dy), Math.floor(z))
    const here = bot.blockAt(p), below = bot.blockAt(p.offset(0, -1, 0))
    if (here && below && here.name === 'air' && below.boundingBox === 'block') return p
  }
  return null
}

function blockInfo(e) {
  const p = e.position
  const below = bot.blockAt(p.offset(0, -0.5, 0).floored())
  let onFood = false, inWater = false
  for (const off of [[0, 0, 0], [0, -1, 0], [1, 0, 0], [-1, 0, 0], [0, 0, 1], [0, 0, -1]]) {
    const b = bot.blockAt(p.floored().offset(...off))
    if (!b) continue
    if (FOOD.has(b.name)) onFood = true
    if (WATER.has(b.name)) inWater = true
  }
  return { block_below: below ? below.name : null, on_food: onFood, in_water: inWater }
}

function snapshot() {
  const flies = flyEntities().map(e => ({
    name: e.username, sex: sexOf(e.username), x: r2(e.position.x), y: r2(e.position.y), z: r2(e.position.z),
    yaw: r2(e.yaw), on_ground: !!e.onGround, dist_to_me: r2(e.position.distanceTo(bot.entity.position)), ...blockInfo(e),
  }))
  const pairs = []
  const ents = flyEntities()
  for (let i = 0; i < ents.length; i++) for (let j = i + 1; j < ents.length; j++)
    pairs.push({ a: ents[i].username, b: ents[j].username, dist: r2(ents[i].position.distanceTo(ents[j].position)) })
  const humans = [], mobs = []
  const target = currentTarget()
  for (const e of Object.values(bot.entities)) {
    if (e === bot.entity || !e.position) continue
    if (e.type === 'player' && !isFly(e.username) && !isGhost(e.username))
      humans.push({ name: e.username, x: r2(e.position.x), y: r2(e.position.y), z: r2(e.position.z) })
    else if (['mob', 'animal', 'hostile'].includes(e.type) && target) {
      const d = e.position.distanceTo(target.position)
      if (d < 16) mobs.push({ name: e.name, dist_to_followed: r2(d) })
    }
  }
  return { type: 'snapshot', t: Date.now() / 1000, flies, pairs, humans, mobs, following: target ? target.username : null,
           me: { x: r2(bot.entity.position.x), y: r2(bot.entity.position.y), z: r2(bot.entity.position.z) },
           time_of_day: bot.time ? bot.time.timeOfDay : null, raining: !!bot.isRaining }
}

function currentTarget() {
  if (following === 'none') return null
  if (following === 'nearest') {
    let best = null, bd = Infinity
    for (const e of flyEntities()) { const d = e.position.distanceTo(bot.entity.position); if (d < bd) { bd = d; best = e } }
    return best
  }
  return flyByName(following)
}

// follow: hover DIST blocks behind and HEIGHT blocks above the fly, looking at it (teleports are cheap for a spectator)
function follow() {
  const t = currentTarget()
  if (!t) return
  const h = headingOf(t)
  smoothHeading = smoothHeading ? smoothHeading.scaled(0.92).plus(h.scaled(0.08)) : h      // ~3 s time constant at 4 Hz
  const hn = smoothHeading.norm() > 0.05 ? smoothHeading.scaled(1 / smoothHeading.norm()) : h
  const want = t.position.minus(hn.scaled(DIST)).offset(0, HEIGHT, 0)
  const me = bot.entity.position
  const now = Date.now()
  const slack = Math.max(1.0, 0.15 * DIST)
  if (me.distanceTo(want) < slack && lastTpPos && lastTpPos.distanceTo(t.position) < 0.7) return
  if (now - lastTp < (me.distanceTo(want) > 3 * slack ? 400 : 1000)) return
  const look = lookAngles(want, t.position.offset(0, 1, 0))
  bot.chat(`/tp ${NAME} ${r2(want.x)} ${r2(want.y)} ${r2(want.z)} ${look.yaw} ${look.pitch}`)
  lastTp = now; lastTpPos = t.position.clone()
}

// --- guidance commands (only ever reach flies, blocks and mobs; never a human player) ------------------------
const commands = {
  snapshot: () => ({ ok: true, msg: 'snapshot', snapshot: snapshot() }),
  follow: ({ who }) => { following = who || 'nearest'; lastTpPos = null; smoothHeading = null; return { ok: true, msg: `following ${following}` } },
  say: ({ text }) => { const s = String(text || '').replace(/♪/g, '').slice(0, 250); if (!s) return { ok: false, msg: 'empty' }; bot.chat(s); return { ok: true, msg: 'said' } },
  tp: ({ who, x, y, z, yaw }) => {
    if (who !== NAME && !isFly(who)) return { ok: false, msg: `${who} is not a fly` }
    bot.chat(`/tp ${who} ${x} ${y} ${z}${yaw !== undefined ? ` ${yaw} 0` : ''}`)
    return { ok: true, msg: `teleported ${who} to ${x},${y},${z}` }
  },
  // put fly `who` `dist` blocks in front of fly `to`, facing it (stage an encounter)
  bring: ({ who, to, dist }) => {
    const target = flyByName(to); if (!target) return { ok: false, msg: `${to} not in view` }
    if (!isFly(who)) return { ok: false, msg: `${who} is not a fly` }
    const d = +(dist || 3)
    const p = target.position.plus(headingOf(target).scaled(d))
    const g = groundAt(p.x, p.y, p.z) || p.floored()
    const yaw = lookAngles(g.offset(0.5, 0, 0.5), target.position).yaw
    bot.chat(`/tp ${who} ${g.x + 0.5} ${g.y} ${g.z + 0.5} ${yaw} 0`)
    return { ok: true, msg: `${who} placed ${d} blocks in front of ${to}, facing it` }
  },
  // put a block (default: a poppy = food odor + sugar) `dist` blocks in front of fly `who`
  place_near: ({ who, block, dist }) => {
    const e = flyByName(who); if (!e) return { ok: false, msg: `${who} not in view` }
    const d = +(dist || 3), b = block || 'poppy'
    const p = e.position.plus(headingOf(e).scaled(d))
    const g = groundAt(p.x, p.y, p.z); if (!g) return { ok: false, msg: 'no ground there' }
    bot.chat(`/setblock ${g.x} ${g.y} ${g.z} ${b}`)
    return { ok: true, msg: `${b} placed at ${g.x},${g.y},${g.z} (${d} blocks in front of ${who})` }
  },
  // remove blocks of the given kinds (default: every food block) within `radius` of fly `who`
  clear_near: ({ who, radius, blocks }) => {
    const e = flyByName(who); if (!e) return { ok: false, msg: `${who} not in view` }
    const r = Math.min(+(radius || 8), 16), p = e.position.floored()
    const kinds = blocks && blocks.length ? blocks : [...FOOD]
    for (const k of kinds) bot.chat(`/fill ${p.x - r} ${p.y - 2} ${p.z - r} ${p.x + r} ${p.y + 3} ${p.z + r} air replace ${k}`)
    return { ok: true, msg: `cleared ${kinds.length} block kinds within ${r} of ${who}` }
  },
  setblock: ({ x, y, z, block }) => { bot.chat(`/setblock ${x} ${y} ${z} ${block}`); return { ok: true, msg: `setblock ${block}` } },
  fill: ({ x1, y1, z1, x2, y2, z2, block }) => { bot.chat(`/fill ${x1} ${y1} ${z1} ${x2} ${y2} ${z2} ${block}`); return { ok: true, msg: 'fill sent' } },
  summon: ({ entity, near, dist, x, y, z }) => {
    let p = null
    if (near) { const e = flyByName(near); if (!e) return { ok: false, msg: `${near} not in view` }; const q = e.position.plus(headingOf(e).scaled(+(dist || 4))); p = groundAt(q.x, q.y, q.z) || q.floored() }
    else p = new Vec3(+x, +y, +z)
    bot.chat(`/summon ${entity || 'sheep'} ${p.x + 0.5} ${p.y} ${p.z + 0.5}`)
    return { ok: true, msg: `${entity || 'sheep'} summoned at ${p.x},${p.y},${p.z}` }
  },
  time: ({ value }) => { bot.chat(`/time set ${value || 'day'}`); return { ok: true, msg: `time set ${value || 'day'}` } },
  weather: ({ value }) => { bot.chat(`/weather ${value || 'clear'}`); return { ok: true, msg: `weather ${value || 'clear'}` } },
  cmd: ({ text }) => { if (!/^\//.test(text || '')) return { ok: false, msg: 'raw commands must start with /' }; bot.chat(text); return { ok: true, msg: `sent ${text}` } },
}

function handle(msg) {
  let m
  try { m = JSON.parse(msg) } catch (e) { return { ok: false, msg: 'bad json' } }
  const fn = commands[m.cmd]
  if (!fn) return { id: m.id, ok: false, msg: `unknown cmd ${m.cmd}` }
  try { return { type: 'result', id: m.id, ...fn(m) } } catch (e) { return { type: 'result', id: m.id, ok: false, msg: e.message } }
}

// --- watching ---------------------------------------------------------------------------------------------
bot.on('chat', (username, message) => {
  if (username === NAME) return
  if (isFly(username) && /♪/.test(message)) return event('song', { who: username })
  event('chat', { who: username, text: message, is_fly: isFly(username) })
})
// arm animations: the fly body shows a proboscis extension as the main hand (0) and a rejection as the off hand (3)
bot._client.on('animation', (packet) => {
  const e = bot.entities[packet.entityId]
  if (!e || e.type !== 'player' || !isFly(e.username)) return
  if (packet.animation === 0) event('feed', { who: e.username })
  else if (packet.animation === 3) event('reject', { who: e.username })
})
bot.on('entityHurt', (e) => { if (e.type === 'player' && isFly(e.username)) event('hurt', { who: e.username }) })
bot.on('entityDead', (e) => { if (e && e.type === 'player' && isFly(e.username)) event('died', { who: e.username }) })
bot.on('playerJoined', (p) => { if (isFly(p.username)) event('joined', { who: p.username }) })
bot.on('playerLeft', (p) => { if (isFly(p.username)) event('left', { who: p.username }) })

bot.once('spawn', () => {
  log(`spawned at ${bot.entity.position.floored()} on ${HOST}:${PORT}; following '${following}' at ${DIST} blocks; roster ${JSON.stringify(roster)}`)
  if (GAMEMODE !== 'none') {
    bot.chat(`/gamemode ${GAMEMODE} ${NAME}`)
    bot.physicsEnabled = false      // the server moves us (/tp); no client-side physics fighting it
  }
  const wss = new WebSocketServer({ host: '127.0.0.1', port: WS_PORT })
  wss.on('connection', (c) => {
    clients.add(c); log('assistant connected')
    c.on('message', (m) => { const r = handle(m.toString()); if (r) c.send(JSON.stringify(r)) })
    c.on('close', () => clients.delete(c))
  })
  log(`listening on ws://127.0.0.1:${WS_PORT}`)
  setInterval(follow, 250)
  setInterval(() => { try { send(snapshot()) } catch (e) { log('snapshot failed:', e.message) } }, 1000)
})
bot.on('kicked', (r) => log('kicked:', JSON.stringify(r)))
bot.on('error', (e) => log('error:', e.message))
bot.on('end', () => { log('disconnected'); process.exit(0) })
