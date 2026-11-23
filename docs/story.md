# The story (working draft)

## Characters

**The player: the quest taker.** Not luci3D. Inside the chips you play a mini creature, armed with a weapon made from electronics, from one of five guilds (drafts in [`../art/sprites/`](../art/sprites/)):

| Guild | Creature | Weapon |
|---|---|---|
| BNF | A sturdy stock critter with a camera-module head, red casing | Propeller-blade sword and prop-guard shield (the starter kit) |
| DIY Punk | A grinning purple gremlin: pink wire mohawk, teal goggles, patched vest, copper coil on the arm, JST-plug tail | Soldering-iron lance with a glowing tip |
| Raiders | A hooded scavenger crow: beak respirator, red eyes, ragged scrap cloak, LiPo bandolier | Antenna-whip bow, pin-header arrows |
| Racers | A yellow-and-black wasp: pink compound eyes, teal wings, a stinger | Twin carbon-fibre daggers |
| Whitespace | A floating white egg-bot with a teal visor and floating hands | Gimbal staff with a glowing orb (the caster) |

Inspired by Hyper Light Drifter and Risk of Rain: small, chunky, readable silhouettes. All designs are our own. No real brand names in the game: the clean-futurist camp is Whitespace.

**luci3D, the snake: your pet companion and guide.** Small and black (the logo is white only to contrast on dark backgrounds), with a grey highlight, a purple rim light and a teal eye so it stands out on black boards. The logo from the back of the open-dvr board, and it came from a hand-drawn zine of maze puzzles: tracing a maze and routing a trace are the same act. The snake runs inside the traces and sees the circuit from the inside. It gives hints, teaches new mechanics, and shows you the way to **the lab**.

**The lab.** luci3D's workshop, hidden in the circuit. You replenish yourself there and get power-ups and items.

**luci3D, the human (background).** An underdog FPV electronics bootlegger. He repairs the micro components before he gives up on a board, always tries to get things back in the air, and squeezes the most out of old equipment. The one you call to crack firmware, modify electronics or build something custom. One of the few 3D flight pilots in the human world. He flies digital too, but analog is king. How he relates to the snake is open.

## The world: boards are cities

Inspired by the first time you opened a 90s PC and saw a micro metropolis. Every board is a city, and old boards are old cities: graffiti, grime, flux stains, scorch marks, bodge wires. Big-city grime is part of the look on purpose.

The first city is **the Stack**: an old FPV flight controller and its 4-in-1 ESC side by side, floating over the quad's carbon frame, joined by the 8-wire cable (generic parts, not specific products):

| On the board | In the city |
|---|---|
| Traces | Roads and avenues. Wide power traces are highways |
| MCU | Downtown, the skyscraper |
| Big electrolytic capacitor (on the ESC battery pads) | The water tower |
| OSD chip | The TV station: it writes onto the analog video |
| CAM and VTX pads | Where analog video enters and leaves the city |
| Motor pads | The industrial edge, scorched and re-soldered many times. Motor wires lead off the map |
| ESC MOSFETs | The factory district. One is blown |
| The torn ESC label | What's left of an old billboard |
| The 8-wire FC–ESC cable | The bridge between the two cities, over the carbon-frame abyss |
| micro SD card | Sticks out over the edge: the city's archive |
| Mounting holes | City gates |
| Vias | Manholes, tunnels between layers |
| Ground pour | Open plazas |
| Bodge wire | luci3D's signature: a repair instead of a replacement |
| Burnt parts, magic smoke | Where something died. Can it be brought back? |
| USB port | The harbour, the link to the outside world |
| Silkscreen | Street signs. Graffiti tags sit on top of them |

**Two cities, two jobs.** The beaten Stack above is the game's world. The Clean Stack is the showroom for the website and the shop: a 4-in-1 ESC, a flight controller and our all-in-one DVR in mint condition, wires bundled, every LED lit, data running. The FC and ESC there are generic, laid out after the TBS Lucid F4 FC and 4in1 ESC drawings, with no TBS branding.

## Tone

- Underdog, resourceful, fix-it-don't-bin-it.
- Grimy but warm; never sterile tech marketing.
- Real electronics vocabulary used correctly. The audience builds this stuff and will notice.
- Influences: the 90s "computer world" cartoons and the real-time Mega Man games on handhelds. Inspiration only. All characters and designs are our own.

## Open questions

- Who gives out the quests? The human luci3D, the guilds, or the boards' own residents?
- Enemies: corrosion, cold joints, ESD sparks, firmware locks, magic smoke spirits?
- Zine symbols are decided (entry/exit, story blocks, items): see [`../zine/README.md`](../zine/README.md). What the items do is still open.
