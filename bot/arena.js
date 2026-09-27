// arena.js — build a walled, flower-dotted test arena around the origin (bot must be op).
const sleep = ms => new Promise(r => setTimeout(r, ms))
const FLOWERS = ['poppy', 'dandelion', 'cornflower', 'oxeye_daisy', 'blue_orchid', 'allium']

async function buildArena(bot, argv = {}) {
  const R = +(argv.arenaRadius || 16)
  const y = +(argv.arenaY || -60)          // superflat: grass top at y=-61, players stand at y=-60
  const say = async (cmd) => { bot.chat(cmd); await sleep(+(argv.cmdDelay || 150)) }
  console.log(`[arena] building radius ${R} at y=${y}`)
  await say('/gamerule doDaylightCycle false')
  await say('/gamerule doWeatherCycle false')
  await say('/gamerule doMobSpawning false')
  await say('/gamerule sendCommandFeedback false')
  await say('/time set 6000')
  await say('/weather clear')
  await say('/kill @e[type=!player]')
  await say(`/fill ${-R - 1} ${y} ${-R - 1} ${R + 1} ${y + 3} ${R + 1} minecraft:air`)
  await say(`/fill ${-R - 1} ${y - 1} ${-R - 1} ${R + 1} ${y - 1} ${R + 1} minecraft:grass_block`)
  for (const [x1, z1, x2, z2] of [[-R - 1, -R - 1, R + 1, -R - 1], [-R - 1, R + 1, R + 1, R + 1],
                                  [-R - 1, -R - 1, -R - 1, R + 1], [R + 1, -R - 1, R + 1, R + 1]]) {
    await say(`/fill ${x1} ${y} ${z1} ${x2} ${y + 2} ${z2} minecraft:white_concrete`)
  }
  // features scale with the chamber: a dark "shelter" cluster, a bright patch, food, aversive patch
  const f = Math.max(1, Math.floor(R / 4))
  await say(`/fill ${R - f} ${y} ${-f} ${R - 1} ${y + 2} ${f - 1} minecraft:dark_oak_log`)
  await say(`/fill ${-R + 1} ${y - 1} ${-f} ${-R + f} ${y - 1} ${f - 1} minecraft:snow_block`)
  const rng = mulberry32(+(argv.seed || 7))
  if (argv.layout === 'patches') {
    // two flower patches of different odor classes on opposite sides (conditioning in the world): --patchA poppy
    // (ester, west) vs --patchB dandelion (vinegar, east), each a solid (2*--patchR+1)-block square (one /fill each —
    // per-block commands get the bot kicked for spam)
    const A = argv.patchA || 'poppy', B = argv.patchB || 'dandelion', PR = +(argv.patchR || 2)
    const cx = Math.max(PR + 1, Math.round(R * 0.55))
    for (const [name, x0] of [[A, -cx], [B, cx]]) {
      await say(`/fill ${x0 - PR} ${y} ${-PR} ${x0 + PR} ${y} ${PR} minecraft:${name}`)
    }
    await say(`/tp ${bot.username} 0 ${y} 0`)
    console.log(`[arena] patches: ${A} at x=${-cx}, ${B} at x=${cx}, ${(2 * PR + 1) ** 2} flowers each`)
    return
  }
  const nFlowers = argv.noFood ? 0 : Math.max(4, Math.round(R * 1.5))   // --noFood: odor-free chamber (no flowers/honey/cake/soul sand)
  for (let i = 0; i < nFlowers; i++) {
    const x = Math.floor(1 + rng() * (R - 2)), z = Math.floor(1 + rng() * (R - 2))
    await say(`/setblock ${x} ${y} ${z} minecraft:${FLOWERS[i % FLOWERS.length]}`)
  }
  if (!argv.noFood) {
    await say(`/setblock ${Math.floor(R / 2)} ${y} ${Math.floor(R / 2)} minecraft:honey_block`)
    await say(`/setblock ${Math.min(R - 1, Math.floor(R / 2) + 1)} ${y} ${Math.floor(R / 2)} minecraft:cake`)
    await say(`/fill ${-R + 1} ${y - 1} ${-R + 1} ${-R + f} ${y - 1} ${-R + f} minecraft:soul_sand`)
  }
  await say(`/tp ${bot.username} 0 ${y} 0`)
  console.log('[arena] done')
}

function mulberry32(a) {
  return function () {
    a |= 0; a = a + 0x6D2B79F5 | 0
    let t = Math.imul(a ^ a >>> 15, 1 | a)
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t
    return ((t ^ t >>> 14) >>> 0) / 4294967296
  }
}

module.exports = { buildArena }
