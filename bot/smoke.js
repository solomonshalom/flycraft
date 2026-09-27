// smoke.js — connect, build the arena, print one observation, exit. (no brain needed)
const mineflayer = require('mineflayer')
const { Observer } = require('./observe')
const { buildArena } = require('./arena')
const argv = require('minimist')(process.argv.slice(2))
const bot = mineflayer.createBot({ host: '127.0.0.1', port: +(argv.port || 25565), username: argv.name || 'fly1', version: '1.20.4', auth: 'offline' })
bot.once('spawn', async () => {
  console.log('spawned', bot.entity.position)
  if (argv['build-arena']) await buildArena(bot, argv)
  if (argv.tp) { const [x, y, z] = String(argv.tp).split(',').map(Number); bot.chat(`/tp ${bot.username} ${x} ${y} ${z}`) }
  await new Promise(r => setTimeout(r, 4000))
  const obs = new Observer(bot)
  const t0 = Date.now()
  const o = obs.observe()
  const dt = Date.now() - t0
  const img = (e) => { let s = ''; for (let r = 0; r < e.h; r++) { for (let c = 0; c < e.w; c++) s += ' .:-=+*#%@'[Math.min(9, Math.floor(e.px[r * e.w + c] * 9.99))]; s += '\n' } return s }
  console.log(`observe() took ${dt} ms`)
  console.log('LEFT EYE\n' + img(o.eyes.L)); console.log('RIGHT EYE\n' + img(o.eyes.R))
  const { eyes, ...rest } = o
  console.log(JSON.stringify(rest))
  process.exit(0)
})
bot.on('kicked', r => { console.log('kicked', r); process.exit(1) })
bot.on('error', e => { console.log('error', e.message); process.exit(1) })
