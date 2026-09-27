// observe.js — turn the bot's surroundings into fly sensory input (all values in [0,1]).
// Every mapping here is a modelling decision; see the paper's Note 11 and brain/flybrain/senses.py.
const { Vec3 } = require('vec3')

// Each eye: a square image covering 150 deg of azimuth (front-lateral) and 150 deg of elevation, at roughly the
// fly's own resolution (a fly has ~30 ommatidia across 150 deg). The optic-lobe model (flyvis) samples it on a
// hexagonal lattice of 721 columns; the plain LIF path samples it at each photoreceptor's retinotopic position.
const EYE = { w: +(process.env.FLY_EYE_W || 24), h: +(process.env.FLY_EYE_H || 24), range: 32 }
// per-eye field of view: azimuth in degrees relative to heading (+ = left), elevation +/-75
const EYES = {
  L: { azFrom: 120, azTo: -30 },   // left eye looks front-left; column 0 = leftmost
  R: { azFrom: 30, azTo: -120 },
}
const EL_FROM = 75, EL_TO = -75

// luminance of block surfaces (albedo-ish). unknown blocks -> 0.45
const LUM = [
  [/snow|white|quartz|diorite|ice|glass|calcite|bone/, 0.95],
  [/sand|birch|end_stone|sandstone|light_gray|yellow|gold|iron_block/, 0.8],
  [/stone|gravel|andesite|granite|cobble|concrete|clay|gray|planks|oak|honey|cake|hay/, 0.55],
  [/grass|leaves|moss|green|vine|melon|pumpkin|bush|flower|poppy|dandelion|tulip|orchid|allium|daisy|cornflower|lily|sunflower|lilac|rose|peony|sugar_cane/, 0.4],
  [/water|blue/, 0.5],
  [/dirt|log|wood|brown|mud|podzol|farmland|path|spruce|dark|netherrack|soul|magma|obsidian|black|coal|deepslate|basalt|blackstone/, 0.2],
  [/lava|fire|glowstone|lantern|torch|sea_lantern|shroomlight|campfire/, 1.0],
]
const lumCache = new Map()
function blockLum(name) {
  if (lumCache.has(name)) return lumCache.get(name)
  let v = 0.45
  for (const [re, l] of LUM) if (re.test(name)) { v = l; break }
  lumCache.set(name, v)
  return v
}

// Odor identity: which block smells of what is OUR design; the odor classes map onto the fly's own glomeruli in
// brain/flybrain/senses.py (ODOR_LIBRARY). Flower families by colour, so the classes are visible in the world:
//   ester  (red/pink flowers)   vinegar (yellow flowers)   floral (blue/purple flowers)   green (white flowers)
//   sweet  (honey, cake, berries, melon, pumpkin, cane)    aversive (soul sand, mould, mushrooms, ...)
const ODOR_CLASS = {
  poppy: 'ester', red_tulip: 'ester', rose_bush: 'ester', peony: 'ester', pink_tulip: 'ester', pink_petals: 'ester',
  dandelion: 'vinegar', sunflower: 'vinegar', orange_tulip: 'vinegar', torchflower: 'vinegar',
  cornflower: 'floral', blue_orchid: 'floral', allium: 'floral', lilac: 'floral', pitcher_plant: 'floral',
  oxeye_daisy: 'green', azure_bluet: 'green', white_tulip: 'green', lily_of_the_valley: 'green', cherry_leaves: 'green',
  flowering_azalea: 'green', flowering_azalea_leaves: 'green',
  honey_block: 'sweet', honeycomb_block: 'sweet', cake: 'sweet', sweet_berry_bush: 'sweet', melon: 'sweet', pumpkin: 'sweet',
  hay_block: 'sweet', sugar_cane: 'sweet',
  soul_sand: 'aversive', soul_soil: 'aversive', mycelium: 'aversive', brown_mushroom: 'aversive', red_mushroom: 'aversive',
  slime_block: 'aversive', composter: 'aversive', netherrack: 'aversive', magma_block: 'aversive', sculk: 'aversive',
  moss_block: 'aversive', mud: 'aversive', nether_wart_block: 'aversive', warped_wart_block: 'aversive', wither_rose: 'aversive',
}
const FOOD_CLASSES = new Set(['ester', 'vinegar', 'floral', 'green', 'sweet'])
const FOOD = new Set(Object.keys(ODOR_CLASS).filter(b => FOOD_CLASSES.has(ODOR_CLASS[b])))
const SWEET = new Set(Object.keys(ODOR_CLASS).filter(b => ODOR_CLASS[b] === 'sweet'))
const AVERSIVE = new Set(Object.keys(ODOR_CLASS).filter(b => ODOR_CLASS[b] === 'aversive'))
const BITTER = new Set(['cactus', 'dead_bush', 'brown_mushroom', 'red_mushroom', 'netherrack', 'magma_block'])
const HOT = new Set(['lava', 'fire', 'magma_block', 'campfire', 'soul_fire', 'soul_campfire'])
const COLD = new Set(['snow', 'snow_block', 'ice', 'packed_ice', 'blue_ice', 'powder_snow', 'frosted_ice'])
const WATER = new Set(['water', 'bubble_column', 'kelp', 'seagrass'])

const rad = d => d * Math.PI / 180
const conc = s => 1 - Math.exp(-2 * s)   // sum of 1/(1+d^2) -> [0,1]
// Antennae: odor is sampled at two points either side of the head so the brain receives a
// bilateral (left/right) signal, as real flies do (Borst & Heisenberg 1982; Gaudry et al. 2013).
// A fly's antennae sit ~20% of body length apart; for a 1.8-block body that is ~0.4 blocks. We
// use 1.0 block by default (configurable) because Minecraft odor sources are block-quantized.
const ANTENNA_SPACING = 1.0
// player names that are ghosts to the flies (the assistant's body); see Observer.isGhost
const GHOST = /^(observer|scribe)/i

class Observer {
  constructor(bot, opts = {}) {
    this.bot = bot
    this.trial = opts.trial || ''
    this.roster = opts.roster || {}          // {name: 'male'|'female'} written by the launcher; the authority on who is a fly and of which sex
    this.sex = opts.sex || 'female'
    // sex of other flies: roster, else opts.sexOf(name), else names with 'm' after 'fly<N>' are male (e.g. fly1m)
    this.sexOf = (name) => this.roster[name] || (opts.sexOf ? opts.sexOf(name) : (/^fly\d*m/i.test(name || '') ? 'male' : 'female'))
    // only rostered bots or bots named fly<N> are flies; any other player (e.g. a human spectator) is a large animal = CO2 source only
    this.isFly = (name) => !!(name && (this.roster[name] !== 'ghost') && (this.roster[name] || /^fly\d/i.test(name)))
    // ghosts are not part of the fly's world at all: the research assistant's body (assistant/scribe.js, default name
    // 'observer') and anything rostered as 'ghost' are never seen, smelled or touched
    this.isGhost = (name) => !!(name && (this.roster[name] === 'ghost' || GHOST.test(name)))
    this.selfName = bot.username
    this.lastHealth = 20
    this.hitUntil = 0
    this.soundUntil = 0
    this.tick = 0
    // which blocks taste of sugar (the reward): 'all' = every food block (flowers have nectar; default), 'none', or a
    // comma list of odor classes ('sweet' = only honey, cake, berries, ...; 'ester' = only red/pink flowers) so that
    // the other flowers are pure odor cues. --bitter likewise lists the classes whose blocks taste bitter (punishment).
    this.nectar = String(opts.nectar || 'all')
    this.bitter = String(opts.bitter || '')
    const classSet = (spec) => new Set(Object.keys(ODOR_CLASS).filter(b => spec.split(',').includes(ODOR_CLASS[b])))
    this.sugarSet = this.nectar === 'all' ? FOOD : (this.nectar === 'none' ? new Set() : classSet(this.nectar))
    this.bitterSet = new Set([...BITTER, ...(this.bitter ? classSet(this.bitter) : [])])
    this.smellCache = { food: 0, aversive: 0, hot: 0, cold: 0, odors: {} }
    this.blockIds = null
    bot.on('health', () => {
      if (bot.health < this.lastHealth) this.hitUntil = Date.now() + 300
      this.lastHealth = bot.health
    })
    bot.on('entityHurt', (e) => { if (e === bot.entity) this.hitUntil = Date.now() + 300 })
    bot.on('chat', (username, message) => {
      if (username !== this.selfName && /♪/.test(message)) this.soundUntil = Date.now() + 600
    })
  }

  daylight() {
    const t = this.bot.time.timeOfDay % 24000
    return (t < 12500 || t > 23500) ? 1.0 : 0.15
  }

  // --- vision: one luminance image per eye, sampled by ray casting -------------
  eye(side) {
    const bot = this.bot
    const cfg = EYES[side]
    const eyePos = bot.entity.position.offset(0, bot.entity.height * 0.9, 0)
    const yaw = bot.entity.yaw
    const day = this.daylight()
    const px = new Float32Array(EYE.w * EYE.h)
    // entities as dark blobs (looming stimuli)
    const ents = []
    for (const e of Object.values(bot.entities)) {
      if (e === bot.entity || !e.position) continue
      if (!['player', 'mob', 'animal', 'hostile', 'water_creature', 'ambient'].includes(e.type)) continue
      if (e.type === 'player' && this.isGhost(e.username)) continue
      const d = e.position.offset(0, (e.height || 1) / 2, 0).minus(eyePos)
      const dist = d.norm()
      if (dist > EYE.range || dist < 0.01) continue
      const az = Math.atan2(-d.x, -d.z) - yaw          // + = left
      const el = Math.asin(d.y / dist)
      const size = Math.atan((e.height || 1.8) * 0.5 / dist)
      ents.push({ az, el, size, lum: e.type === 'player' ? 0.1 : 0.15 })
    }
    for (let r = 0; r < EYE.h; r++) {
      const el = rad(EL_FROM + (EL_TO - EL_FROM) * (r + 0.5) / EYE.h)
      for (let c = 0; c < EYE.w; c++) {
        const azDeg = cfg.azFrom + (cfg.azTo - cfg.azFrom) * (c + 0.5) / EYE.w
        const a = yaw + rad(azDeg)
        const dir = new Vec3(-Math.sin(a) * Math.cos(el), Math.sin(el), -Math.cos(a) * Math.cos(el))
        let lum
        const hit = bot.world.raycast(eyePos, dir, EYE.range)
        if (hit) {
          // light is stored on the air block in front of the surface, not on the opaque block itself
          const front = hit.intersect ? bot.blockAt(hit.intersect.minus(dir.scaled(0.05))) : null
          const light = front ? Math.max(front.light || 0, (front.skyLight || 0) * day) / 15 : day
          lum = blockLum(hit.name) * (0.25 + 0.75 * light)
        } else {
          lum = el > 0 ? 1.0 * day : 0.6 * day
        }
        for (const e of ents) {
          let da = rad(azDeg) - e.az
          da = Math.atan2(Math.sin(da), Math.cos(da))
          if (Math.abs(da) < e.size && Math.abs(el - e.el) < e.size * 1.6) lum = e.lum
        }
        px[r * EYE.w + c] = lum
      }
    }
    return { w: EYE.w, h: EYE.h, px: Array.from(px, v => Math.round(v * 100) / 100) }
  }

  // --- chemosensation ---------------------------------------------------------
  ensureIds() {
    if (this.blockIds) return
    const reg = this.bot.registry
    const ids = (set) => [...set].map(n => reg.blocksByName[n]).filter(Boolean).map(b => b.id)
    this.blockIds = { food: ids(FOOD), aversive: ids(AVERSIVE), hot: ids(HOT), cold: ids(COLD), odorous: ids(new Set(Object.keys(ODOR_CLASS))) }
    this.classOfId = new Map(Object.keys(ODOR_CLASS).map(n => [reg.blocksByName[n] && reg.blocksByName[n].id, ODOR_CLASS[n]]))
  }

  antennae() {
    const bot = this.bot
    const p = bot.entity.position.offset(0, bot.entity.height * 0.9, 0)
    const yaw = bot.entity.yaw
    // heading = (-sin yaw, -cos yaw); left = rotate heading +90deg
    const left = new Vec3(-Math.cos(yaw), 0, Math.sin(yaw)).scaled(ANTENNA_SPACING / 2)
    return { L: p.plus(left), R: p.minus(left) }
  }

  scanSmell() {
    this.ensureIds()
    const bot = this.bot
    const ant = this.antennae()
    const sum = (ids, maxDistance, count) => {
      if (!ids.length) return { L: 0, R: 0 }
      let L = 0, R = 0
      for (const pos of bot.findBlocks({ matching: ids, maxDistance, count })) {
        const c = pos.offset(0.5, 0.5, 0.5)
        L += 1 / (1 + c.distanceSquared(ant.L)); R += 1 / (1 + c.distanceSquared(ant.R))
      }
      return { L, R }
    }
    const lr = (x, k = 1) => ({ L: conc(k * x.L), R: conc(k * x.R) })
    // odor identity: one concentration per odor class at each antenna
    const byClass = {}
    for (const pos of bot.findBlocks({ matching: this.blockIds.odorous, maxDistance: 16, count: 300 })) {
      const b = bot.blockAt(pos)
      const cls = b && this.classOfId.get(b.type)
      if (!cls) continue
      const c = pos.offset(0.5, 0.5, 0.5)
      const acc = byClass[cls] || (byClass[cls] = { L: 0, R: 0 })
      acc.L += 1 / (1 + c.distanceSquared(ant.L)); acc.R += 1 / (1 + c.distanceSquared(ant.R))
    }
    const odors = {}
    let food = { L: 0, R: 0 }, aversive = { L: 0, R: 0 }
    for (const [cls, acc] of Object.entries(byClass)) {
      odors[cls] = lr(acc)
      if (FOOD_CLASSES.has(cls)) { food.L += acc.L; food.R += acc.R } else if (cls === 'aversive') { aversive.L += acc.L; aversive.R += acc.R }
    }
    this.smellCache = {
      food: lr(food),           // undifferentiated totals, kept for the log and for brains without the odor library
      aversive: lr(aversive),
      odors,
      hot: lr(sum(this.blockIds.hot, 5, 30), 2),
      cold: lr(sum(this.blockIds.cold, 3, 30), 2),
    }
  }

  entitiesSmell() {
    const bot = this.bot
    const p = bot.entity.position
    const ant = this.antennae()
    const co2 = { L: 0, R: 0 }, fly = { L: 0, R: 0 }, cva = { L: 0, R: 0 }
    let nearFly = null
    for (const e of Object.values(bot.entities)) {
      if (e === bot.entity || !e.position) continue
      if (!['player', 'mob', 'animal', 'hostile'].includes(e.type)) continue
      if (e.type === 'player' && this.isGhost(e.username)) continue
      const d2 = e.position.distanceSquared(p)
      if (d2 > 24 * 24) continue
      const src = e.position.offset(0, (e.height || 1) * 0.9, 0)
      const dL = 1 / (1 + src.distanceSquared(ant.L)), dR = 1 / (1 + src.distanceSquared(ant.R))
      // CO2 emission scales with body size: a fly-sized emitter is ~5% of a mob/human plume
      const co2k = (e.type === 'player' && this.isFly(e.username)) ? 0.05 : 1.0
      co2.L += co2k * dL; co2.R += co2k * dR
      if (e.type === 'player' && this.isFly(e.username)) {
        fly.L += dL; fly.R += dR
        if (this.sexOf(e.username) === 'male') { cva.L += dL; cva.R += dR }
        const dist = Math.sqrt(d2)
        if (!nearFly || dist < nearFly.dist) {
          const d = e.position.minus(p)
          let az = Math.atan2(-d.x, -d.z) - bot.entity.yaw
          az = Math.atan2(Math.sin(az), Math.cos(az))
          nearFly = { name: e.username || e.name, dist: Math.round(dist * 100) / 100, az: Math.round(az * 100) / 100 }
        }
      }
    }
    return { co2: { L: conc(co2.L), R: conc(co2.R) }, fly: { L: conc(2 * fly.L), R: conc(2 * fly.R) }, cva: { L: conc(2 * cva.L), R: conc(2 * cva.R) }, nearFly }
  }

  taste() {
    const bot = this.bot
    const p = bot.entity.position.floored()
    const names = []
    for (const off of [[0, 0, 0], [0, -1, 0], [1, 0, 0], [-1, 0, 0], [0, 0, 1], [0, 0, -1], [0, 1, 0]]) {
      const b = bot.blockAt(p.offset(...off))
      if (b) names.push(b.name)
    }
    let fly_female = 0, fly_male = 0
    for (const e of Object.values(bot.entities)) {
      if (e !== bot.entity && e.type === 'player' && this.isFly(e.username) && e.position && e.position.distanceTo(bot.entity.position) < 1.3) {
        if (this.sexOf(e.username) === 'male') fly_male = 1; else fly_female = 1
      }
    }
    return {
      sugar: names.some(n => this.sugarSet.has(n)) ? 1 : 0,
      water: names.some(n => WATER.has(n)) ? 1 : 0,
      bitter: names.some(n => this.bitterSet.has(n)) ? 1 : 0,
      fly_female, fly_male,   // touching another fly -> contact-pheromone GRNs (ppk25 / ppk23)
    }
  }

  observe() {
    const bot = this.bot
    this.tick++
    if (this.tick % 4 === 1) this.scanSmell()
    const es = this.entitiesSmell()
    const v = bot.entity.velocity
    const speed = Math.min(1, Math.hypot(v.x, v.z) / 0.2)
    const now = Date.now()
    const pos = bot.entity.position
    return {
      eyes: { L: this.eye('L'), R: this.eye('R') },
      smell: { food: this.smellCache.food, co2: es.co2, fly: es.fly, cva: es.cva, aversive: this.smellCache.aversive, odors: this.smellCache.odors },
      taste: this.taste(),
      mechano: {
        speed, wind: bot.isRaining ? 0.3 : 0,
        hit: now < this.hitUntil, collided: !!bot.entity.isCollidedHorizontally,
        on_ground: !!bot.entity.onGround, in_water: !!bot.entity.isInWater,
      },
      sound: now < this.soundUntil ? 1 : 0,
      thermo: { hot: this.smellCache.hot, cold: this.smellCache.cold },
      meta: {
        x: Math.round(pos.x * 100) / 100, y: Math.round(pos.y * 100) / 100, z: Math.round(pos.z * 100) / 100,
        yaw: Math.round(bot.entity.yaw * 1000) / 1000, hp: bot.health, game_tick: bot.time.age,
        near_fly: es.nearFly, trial: this.trial, sex: this.sex, on_ground: !!bot.entity.onGround,
      },
    }
  }
}

module.exports = { Observer, FOOD, ODOR_CLASS, SWEET }
