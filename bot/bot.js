// bot.js — a Minecraft body for a fly brain.
//   node bot.js --name fly1 --brain ws://127.0.0.1:8765 --viewer 3007 [--sex female|male] [--roster roster.json]
//               [--host 127.0.0.1 --port 25565] [--build-arena] [--tp x,y,z] [--yaw deg] [--duration s] [--trial label]
//               [--tick 50] [--no-reflexes] [--others male|female] [--nectar all|none|<odor classes>] [--bitter <odor classes>]
//
// The brain returns continuous drives (walk, back, turn in [0,1] / [-1,1]) and discrete acts it has already
// drawn as Poisson events from its own motor-neuron rates (jump, attack, feed, sing, ...). The body applies the
// drives every physics tick: walking is a duty cycle, so speed follows the motor-neuron rate; turning is a yaw
// rate. Nothing here thresholds a neural signal.
//
// Body-level reflexes (the fly's nerve cord has these; the FlyWire brain does not include the nerve cord), on
// by default, --no-reflexes turns them off:  step up onto a one-block obstacle when walking into it; float when
// in water. They never start or stop walking and never turn the body.
const fs = require('fs')
const mineflayer = require('mineflayer')
const WebSocket = require('ws')
const argv = require('minimist')(process.argv.slice(2))
const { Observer } = require('./observe')
const { buildArena } = require('./arena')

const NAME = argv.name || 'fly1'
const HOST = argv.host || '127.0.0.1'
const PORT = +(argv.port || 25565)
const BRAIN = argv.brain || 'ws://127.0.0.1:8765'
const VIEWER = argv.viewer === undefined ? 3007 : +argv.viewer
const TICK_MS = +(argv.tick || 50)            // observation period; the brain simulates its --brain-ms per observation
const TURN_RATE = +(argv.turnRate || 0.12)    // rad per physics tick (50 ms) at |turn| = 1  (~140 deg/s max)
const MC_VERSION = argv.version || '1.20.4'
const REFLEXES = !argv['no-reflexes']
// Brain time vs world time: when the brain cannot keep up with real time, the body slows down by the same factor so
// that behaviour per second of *brain* time is unchanged (a fly whose brain runs at 0.3x walks at 0.3x speed).
// --no-realtime-scale lets the world run at full speed regardless.
const RT_SCALE = !argv['no-realtime-scale']
let rtRatio = 1.0
const roster = argv.roster && fs.existsSync(argv.roster) ? JSON.parse(fs.readFileSync(argv.roster, 'utf8')) : {}
const MY_SEX = argv.sex || roster[NAME] || (/^fly\d*m/i.test(NAME) ? 'male' : 'female')

const bot = mineflayer.createBot({ host: HOST, port: PORT, username: NAME, version: MC_VERSION, auth: 'offline' })
let ws = null, busy = false, obs = null, sentAt = 0
const drive = { walk: 0, back: 0, turn: 0 }   // continuous targets from the brain
let accWalk = 0, accBack = 0, jumpUntil = 0
const stats = { ticks: 0, jumps: 0, attacks: 0, feeds: 0, sings: 0, eggs: 0, accepts: 0, rejects: 0, courts: 0, deaths: 0, steps: 0, brain_ms: 0, wall_ms: 0 }

function connectBrain() {
  ws = new WebSocket(BRAIN)
  ws.on('open', () => console.log(`[${NAME}] connected to brain ${BRAIN}`))
  ws.on('message', (m) => { apply(JSON.parse(m.toString())); busy = false })
  ws.on('close', () => { console.log(`[${NAME}] brain disconnected, retrying in 2s`); busy = false; setTimeout(connectBrain, 2000) })
  ws.on('error', (e) => console.log(`[${NAME}] brain ws error: ${e.message}`))
}

function nearestTarget(maxDist) {
  let best = null, bd = maxDist
  for (const e of Object.values(bot.entities)) {
    if (e === bot.entity || !e.position) continue
    if (!['player', 'mob', 'animal', 'hostile'].includes(e.type)) continue
    if (e.type === 'player' && !obs.isFly(e.username)) continue   // never attack a human spectator or the assistant's body (a ghost)
    const d = e.position.distanceTo(bot.entity.position)
    if (d < bd) { bd = d; best = e }
  }
  return best
}

function apply(reply) {
  const c = reply.controls
  if (!c) return
  stats.brain_ms += reply.brain_ms || 0; stats.wall_ms += Date.now() - sentAt
  const r = (reply.brain_ms || 50) / Math.max(1, Date.now() - sentAt)
  rtRatio = 0.9 * rtRatio + 0.1 * Math.min(1, r)
  drive.walk = +c.walk || 0; drive.back = +c.back || 0; drive.turn = +c.turn || 0
  const now = Date.now()
  if (c.jump) { jumpUntil = now + 150; stats.jumps++ }
  if (c.attack) { const e = nearestTarget(3.5); if (e) { bot.attack(e); stats.attacks++ } }
  if (c.feed) { bot.swingArm('right'); stats.feeds++ }                        // proboscis extension
  if (c.sing) { bot.chat('♪'); stats.sings++ }                                // song: other flies hear it (JO-A)
  if (c.court) stats.courts++
  if (c.egg) stats.eggs++
  if (c.accept) stats.accepts++
  if (c.reject) { bot.swingArm('left'); stats.rejects++ }                     // ovipositor extrusion, shown as the other arm
}

// --- body: apply the drives every physics tick (20 Hz) ---------------------------------------
function physics() {
  const e = bot.entity
  if (!e) return
  const now = Date.now()
  // duty-cycle locomotion: the fraction of ticks spent walking equals the drive (scaled to brain time if the brain is slow)
  const k = RT_SCALE ? rtRatio : 1
  accWalk += drive.walk * k; accBack += drive.back * k
  const goBack = accBack >= 1 && drive.back >= drive.walk
  const goWalk = !goBack && accWalk >= 1
  if (accWalk >= 1) accWalk -= 1
  if (accBack >= 1) accBack -= 1
  bot.setControlState('forward', goWalk)
  bot.setControlState('back', goBack)
  if (Math.abs(drive.turn) > 0.005) bot.look(e.yaw + drive.turn * TURN_RATE * k, 0, false)
  let jump = now < jumpUntil
  if (REFLEXES) {
    if (e.isInWater) jump = true                                            // float
    else if ((goWalk || goBack) && e.isCollidedHorizontally && e.onGround) { jump = true; stats.steps++ }   // step up
  }
  bot.setControlState('jump', jump)
  bot.setControlState('sneak', false)
}

bot.once('spawn', async () => {
  console.log(`[${NAME}] spawned at ${bot.entity.position} (mc ${bot.version}) as ${MY_SEX}; reflexes ${REFLEXES ? 'on' : 'off'}`)
  if (VIEWER > 0) {
    try {
      require('prismarine-viewer').mineflayer(bot, { port: VIEWER, firstPerson: !!argv.firstPerson })
      console.log(`[${NAME}] viewer: http://localhost:${VIEWER}`)
    } catch (e) { console.log(`[${NAME}] viewer failed: ${e.message}`) }
  }
  if (argv['build-arena']) await buildArena(bot, argv)
  if (argv.tp) {
    const [x, y, z] = String(argv.tp).split(',').map(Number)
    const yawDeg = argv.yaw !== undefined ? +argv.yaw : 0     // Minecraft yaw degrees: 0 = south(+z), 90 = west(-x), 180 = north, -90 = east
    bot.chat(`/tp ${NAME} ${x} ${y} ${z} ${yawDeg} 0`)
  }
  // --waitFor <name>: do not start the brain, the log or the trial clock until the partner fly is in the world, so that
  // neither fly walks before the other exists (the 6-s launch stagger of run_pair.sh let fly1 walk onto fly2's start
  // point in some trials; RESEARCH_NOTES 23). Off by default, so earlier series reproduce unchanged.
  // A two-phase handshake in chat: a fly whose own /tp has landed says "ready" (every 2 s); a ready fly that hears the
  // partner's "ready" says "go" and starts; a fly that hears "go" starts. Both start within one chat round trip.
  if (argv.waitFor) {
    const t0 = Date.now(), sleep = (ms) => new Promise(r => setTimeout(r, ms))
    let heardReady = false, heardGo = false
    const onChat = (username, message) => {
      if (username !== argv.waitFor) return
      if (message === 'ready') heardReady = true
      if (message === 'go') heardGo = true
    }
    bot.on('chat', onChat)
    if (argv.tp) {                                                       // wait for this fly's own /tp to land
      const [x, y, z] = String(argv.tp).split(',').map(Number)
      while (bot.entity.position.distanceTo(bot.entity.position.clone().set(x, y, z)) > 1.0 && Date.now() - t0 < 60000) await sleep(100)
    }
    let said = 0
    while (!heardGo && !heardReady && Date.now() - t0 < 180000) {
      if (Date.now() - said > 2000) { bot.chat('ready'); said = Date.now() }
      await sleep(25)
    }
    if (!heardGo) bot.chat('go')
    bot.removeListener('chat', onChat)
    console.log(`[${NAME}] handshake with ${argv.waitFor}: ${heardGo ? 'heard go' : heardReady ? 'heard ready, said go' : 'TIMED OUT'} after ${((Date.now() - t0) / 1000).toFixed(1)} s at ${bot.entity.position.floored()}; starting`)
  }
  if (argv.duration) setTimeout(() => { console.log(`[${NAME}] duration reached, exiting ${JSON.stringify(stats)}`); process.exit(0) }, +argv.duration * 1000)
  obs = new Observer(bot, { trial: argv.trial || '', roster, sex: MY_SEX, sexOf: argv.others ? (() => argv.others) : undefined, nectar: argv.nectar, bitter: argv.bitter })
  connectBrain()
  bot.on('physicsTick', physics)
  setInterval(() => {
    if (!ws || ws.readyState !== WebSocket.OPEN || busy) return
    busy = true; sentAt = Date.now()
    try { ws.send(JSON.stringify(obs.observe())) } catch (e) { busy = false; console.log(e.message) }
    stats.ticks++
    if (stats.ticks % 200 === 0) {
      const ratio = stats.wall_ms ? (stats.brain_ms / stats.wall_ms).toFixed(2) : '?'
      console.log(`[${NAME}] ${JSON.stringify(stats)} pos=${bot.entity.position.floored()} brain/wall=${ratio} body speed x${rtRatio.toFixed(2)}`)
    }
  }, TICK_MS)
})

bot.on('death', () => { stats.deaths++; console.log(`[${NAME}] died (respawning)`) })
bot.on('kicked', (r) => console.log(`[${NAME}] kicked: ${JSON.stringify(r)}`))
bot.on('error', (e) => console.log(`[${NAME}] error: ${e.message}`))
bot.on('end', () => { console.log(`[${NAME}] disconnected`); process.exit(0) })
