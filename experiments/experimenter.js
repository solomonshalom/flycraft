// experimenter.js — the experimenter's hand: log in as the ghost op player, run a few server commands, leave.
// Used by learn_in_world.sh to place the fly in a patch (as a T-maze experimenter puts a fly into an odor tube).
//   node experiments/experimenter.js --port 25565 --cmd "/tp fly1 -6 64 0" [--cmd "..."] [--name observer]
// The player name must be an op and a ghost to the flies (observer* / scribe*; see bot/observe.js).
const path = require('path')
module.paths.unshift(path.join(__dirname, '..', 'bot', 'node_modules'))
const mineflayer = require('mineflayer')
const argv = require('minimist')(process.argv.slice(2))
const cmds = [].concat(argv.cmd || [])
if (!cmds.length) { console.log('nothing to do'); process.exit(0) }
const bot = mineflayer.createBot({ host: argv.host || '127.0.0.1', port: +(argv.port || 25565), username: argv.name || 'observer', version: argv.version || '1.20.4', auth: 'offline' })
bot.once('spawn', async () => {
  for (const c of cmds) { bot.chat(String(c)); await new Promise(r => setTimeout(r, 300)) }
  console.log(`[experimenter] ran ${cmds.length} command(s)`)
  setTimeout(() => { bot.quit(); process.exit(0) }, 500)
})
bot.on('error', (e) => { console.log(`[experimenter] error: ${e.message}`); process.exit(1) })
setTimeout(() => { console.log('[experimenter] timeout'); process.exit(1) }, 20000)
