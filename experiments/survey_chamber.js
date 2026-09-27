// survey_chamber.js — is the encounter chamber really odor-free? Log in as the ghost op player, stand at the origin,
// list every odorous block (bot/observe.js ODOR_CLASS) within --radius blocks, and with --clear wipe everything we ever
// built around the origin (y --y0..--y1, +-radius) so that the chamber the next bot builds has nothing to smell.
// Then re-survey. The bot's odor kernel counts blocks up to 16 blocks from the antennae (observe.js scanSmell), so a
// clean chamber of radius R needs no odorous block within R + 16 of the origin; the default radius has slack.
//   node experiments/survey_chamber.js [--port 25565] [--radius 45] [--clear] [--y0 63 --y1 70] [--floor 30] [--name observer]
// After clearing, a grass floor is laid at y0 within +-floor blocks: a fly logs back in where it logged out, and a fly
// that spawns over the hole its floor left falls 124 blocks and dies before the arena builder's /tp reaches it (this
// cost the first clean-chamber trial of 18 Sep). Grass is not odorous. Exit code 0 = clean, 2 = odorous blocks remain.
const path = require('path')
module.paths.unshift(path.join(__dirname, '..', 'bot', 'node_modules'))
const mineflayer = require('mineflayer')
const { Vec3 } = require('vec3')
const argv = require('minimist')(process.argv.slice(2))
const { ODOR_CLASS } = require('../bot/observe')
const R = +(argv.radius || 45), Y0 = +(argv.y0 || 63), Y1 = +(argv.y1 || 70), Y = +(argv.y || 64), F = argv.floor === undefined ? 30 : +argv.floor
const sleep = ms => new Promise(r => setTimeout(r, ms))
const bot = mineflayer.createBot({ host: argv.host || '127.0.0.1', port: +(argv.port || 25565), username: argv.name || 'observer', version: argv.version || '1.20.4', auth: 'offline' })
const say = async (cmd) => { bot.chat(cmd); await sleep(250) }

const ORIGIN = new Vec3(0, Y, 0)
function survey() {
  const reg = bot.registry
  const ids = Object.keys(ODOR_CLASS).map(n => reg.blocksByName[n]).filter(Boolean).map(b => b.id)
  const classOf = new Map(Object.keys(ODOR_CLASS).map(n => [reg.blocksByName[n] && reg.blocksByName[n].id, ODOR_CLASS[n]]))
  const found = bot.findBlocks({ matching: ids, maxDistance: R, count: 20000, point: ORIGIN })   // measured from the chamber's origin, not from wherever the bot is
  const byClass = {}, byName = {}
  let ymin = Infinity, ymax = -Infinity
  for (const p of found) {
    const b = bot.blockAt(p); if (!b) continue
    const cls = classOf.get(b.type); byClass[cls] = (byClass[cls] || 0) + 1; byName[b.name] = (byName[b.name] || 0) + 1
    ymin = Math.min(ymin, p.y); ymax = Math.max(ymax, p.y)
  }
  const players = Object.values(bot.players).map(p => p.username).filter(n => n !== bot.username)
  return { found, byClass, byName, ymin, ymax, players }
}

function report(label, s) {
  console.log(`[survey] ${label}: ${s.found.length} odorous blocks within ${R} of the origin` +
    (s.found.length ? ` (y ${s.ymin}..${s.ymax}); by class ${JSON.stringify(s.byClass)}; by block ${JSON.stringify(s.byName)}` : '') +
    `; other players online: ${s.players.length ? s.players.join(', ') : 'none'}`)
  if (s.found.length && s.found.length <= 40) console.log('[survey]   at ' + s.found.map(p => `${p.x},${p.y},${p.z}`).join(' '))
  const near = s.found.filter(p => Math.hypot(p.x, p.z) <= 6 + 16)
  if (near.length) console.log(`[survey]   ${near.length} of them within smelling range (22 blocks) of an R = 6 chamber`)
}

bot.once('spawn', async () => {
  await say(`/gamemode spectator ${bot.username}`)   // a ghost that does not fall when the floor under it goes
  await say(`/tp ${bot.username} 0 ${Y} 0`)
  await sleep(4000)                                    // let the chunks around the origin arrive
  const before = survey(); report('before', before)
  if (argv.clear) {
    // everything we ever built around the origin sits at y >= Y0 (arena floors at ARENA_Y - 1, flowers at ARENA_Y);
    // one layer per command keeps each fill under the 32768-block limit for radius <= 90
    await say('/gamerule sendCommandFeedback false')
    for (let y = Y0; y <= Y1; y++) await say(`/fill ${-R} ${y} ${-R} ${R} ${y} ${R} minecraft:air`)
    await say('/kill @e[type=item]')
    await say(`/tp ${bot.username} 0 ${Y} 0`)
    await sleep(1500)
    const after = survey(); report('after clearing', after)
    // anything left is outside the cleared slab: report it and clear its bounding box too
    if (after.found.length) {
      for (let y = after.ymin; y <= after.ymax; y++) await say(`/fill ${-R} ${y} ${-R} ${R} ${y} ${R} minecraft:air`)
      await sleep(1500); report('after second pass', survey())
    }
    if (F > 0) { await say(`/fill ${-F} ${Y0} ${-F} ${F} ${Y0} ${F} minecraft:grass_block`); console.log(`[survey] grass floor laid at y=${Y0} within +-${F} (so that a fly logging in over the wiped slab does not fall)`) }
  }
  const final = survey()
  console.log(`[survey] ${final.found.length === 0 ? 'CLEAN' : 'NOT CLEAN'}: ${final.found.length} odorous blocks within ${R}`)
  bot.quit(); process.exit(final.found.length === 0 ? 0 : 2)
})
bot.on('kicked', (r) => { console.log(`[survey] kicked: ${r}`); process.exit(1) })
bot.on('error', (e) => { console.log(`[survey] error: ${e.message}`); process.exit(1) })
setTimeout(() => { console.log('[survey] timeout'); process.exit(1) }, 90000)
