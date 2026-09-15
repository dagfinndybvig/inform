# The Goddess in the Cellar — Gameplay

A Lovecraftian text adventure in Inform 6. You are Randolph Carter, a
dreamer from Arkham who returns to a dreamworld he has explored before but
cannot remember. A grandfather clock in a dark cellar is a gate to an alien
world where a flaming goddess demands tribute — and a crumpled note in your
pocket is the key to waking up.

## Premise

You wake in a dreamworld — though "wake" is not the right word. You do not
remember arriving. You do not remember who you are. You find yourself before
an ancient, foreboding cottage of cyclopean stone, seeking refuge from forces
you dare not name. Within lies a grandfather clock that is no mere timepiece
— it is a gate between worlds. Beyond the Forest, a Stone Circle of standing
stones forms a labyrinth around an altar bearing an ornate box with a violet
bloom essential for survival beyond.

You have been here before. The dreamworld strips your waking memory each time
you enter, so you left breadcrumbs for yourself: a tattered notebook with
clues, a brass lantern for the dark cellar, and a crumpled note in your
pocket reading "Remember: You are Randolph Carter." Examining the note is
the key to the final awakening — once the goddess is appeased and the note
has been read, returning through the clock wakes you in your bed in Arkham.
A still pond in the Garden offers another clue: its reflection shows a
scholarly gentleman in a suit and hat, not the figure you appear to be in
this neolithic dreamworld.

## Walkthrough

### 1. The Cottage

You begin in the Cottage. Three objects are here, and you are carrying one:

- **crumpled note** (in your inventory) — a scrap of paper in your own hand,
  though you do not recall writing it. Examining it (`examine note`) reads
  "Remember: You are Randolph Carter" and awards 10 points. You must read
  the note at some point to win the game — either early, or after returning
  from the alien world.

- **rusty key** — hidden beneath a loose hearthstone by the hearth.
  Examine the hearthstone (`examine hearthstone`) to discover the key, then
  `take key`. You can also `take hearthstone`, `push hearthstone`,
  `pull hearthstone`, or `look under hearthstone` to reveal it. Unlocks the
  ornate box at the altar in the Stone Circle labyrinth.
- **brass lantern** — on a shelf. Switchable; grants light when lit. Essential
  for the dark Cellar below.
- **tattered notebook** — on the floor. Reading it (`read notebook`) reveals
  four pieces of advice, penned by a trembling hand:
  1. Eat the violet bloom that lies within the ornate box at the altar in the
     Stone Circle labyrinth before crossing through the clock. The air beyond
     is death to mortal lungs.
  2. The goddess of blue flame demands her sacrifice — the gold coin. Offer
     it freely, or be unmade.
  3. The stones form a ring. Enter from the south, go east or west around, and
     seek the gap to the north. Map it if you would not be lost.
  4. I will hide the key.

### 2. The Garden

Go north to the Garden. A **still pond** reflects the bruise-coloured sky.
Examining it (`examine pond`) reveals a reflection that is not your own:
a scholarly gentleman in a suit and hat, a jarring vision that belongs
to no neolithic dreamworld. The reflection vanishes when you blink.
This is a dream-logic foreshadowing of your true identity as Randolph
Carter.

From the Garden, proceed east to the **Dark Forest**.

### 3. The Forest

Go east to the **Dark Forest**. A faint path leads north to a clearing.

A **twig** lies among the gnarled roots. Take it — you will need it in the
Cellar to pry the gold coin from the crack.

### 4. The Stone Circle and Labyrinth

North of the Forest stands a ring of weathered menhirs. Going north from the
clearing funnels you into a labyrinth of standing stones — a ring of 4 rooms
(South, East, North, West) plus a Blind Alley dead end branching
east off Labyrinth East (5 rooms total). Navigate clockwise
(east) or counterclockwise (west) around the ring to Labyrinth North, then go
north to reach the **Altar Chamber** at the centre. There you find:

- **stone altar** — a dark slab stained by ancient sacrifice.
- **ornate wooden box** — sits atop the altar, locked, carved with shifting
  patterns.

To proceed:

1. Return to the Cottage and examine the **loose hearthstone** to reveal the
   **rusty key**, then take it
2. Return to the Altar Chamber via the labyrinth
3. `unlock box` with the rusty key
4. `open box` to reveal its contents
5. Inside is the **blue flower** — eat it (`eat flower`) before proceeding

The flower's nectar remakes your lungs to endure the alien atmosphere. Without
this, you will asphyxiate upon entering the Alien World.

### 5. The Cellar

Return to the Cottage, then descend. The Cellar is dark — you must bring the
lantern (from the Cottage) and switch it on, or fumble in blindness. Here you
find:

- **grandfather clock** — carved with non-Euclidean symbols. Entering it
  teleports you to the Alien World.
- **dark crack** — a jagged fissure in the floor. The **gold coin** is hidden
  within, wedged too deep to reach by hand. You must `examine crack` to
  discover the coin, then pry it loose with the **twig** from the Forest
  (`pry coin with twig`, or `put twig in crack`) before you can take it.
  This is the goddess's demanded sacrifice.

### 6. The Alien World

Enter the clock. You arrive on a landscape of cyclopean stone spires beneath
a violet sky. Two things are here:

- **indescribable horror** — a shape at the edge of vision. Looking upon it
  invites madness. Leave it alone.
- **flaming goddess** — a towering obsidian effigy wreathed in cold blue
  flame. She is animate and aware. While unappeased, she kills on any action
  except `give coin to goddess`. Do nothing else in her presence.

### 7. The Offering

Give the coin to the goddess (`give coin to goddess`). She accepts it with
flashing eyes, the coin swallowed by her fire, and the oppressive dread
recedes. You are now permitted to act freely.

### 8. The Return and the Awakening

Enter the clock again to return to the Cellar. If the goddess has been
appeased **and** you have read the crumpled note, the clock's interior
dissolves into darkness — and you wake in a narrow bed in a room that
smells of old books and pipe smoke. Morning light filters through
curtains you know by heart. You are in the ancestral house in Arkham.
Your name is Randolph Carter, and you have been dreaming — but the
note is still in your hand, and outside the window, for just a moment,
the light flickers blue. The game ends with `*** You have won ***`.

If you return through the clock without having read the note, you
arrive in the Cellar instead. The goddess is appeased, but something is
unfinished — the note in your pocket pulses with a quiet insistence.
Read it (`examine note`) to trigger the waking ending.

## Death conditions

| Cause | Trigger |
|-------|---------|
| Asphyxiation | Entering the Alien World without having eaten the flower |
| Lightning bolt | Performing any action in the goddess's presence except giving her the coin |
| Lightning bolt | Giving the goddess anything other than the coin |

## Win condition

Read the crumpled note ("Remember: You are Randolph Carter"), eat the
flower from the ornate box, pry the coin loose from the Cellar crack with
the twig, appease the goddess with the coin, then return through the
clock. You wake in your bed in Arkham as Randolph Carter. The game ends
with `*** You have won ***`. The note may be read at any point — before
entering the alien world, or after returning to the Cellar with the
goddess appeased.

## Required sequence

```
examine note          # read the identity note (10 pts, required to win)
read notebook          # learn the four rules
examine hearthstone    # discover the hidden key
take key              # for the ornate box
take notebook         # scored object (4 pts)
take lantern          # for the dark Cellar
n                      # to Garden
examine pond          # see the gentleman reflection (optional, atmospheric)
e                      # to Forest
take twig             # needed to pry the coin from the crack
n                      # to Stone Circle
n                      # into Labyrinth South
e                      # to Labyrinth East
n                      # to Labyrinth North
n                      # to Altar Chamber
unlock box            # with the rusty key
open box              # reveal the flower
eat flower            # survive the alien air
s                      # to Labyrinth North
e                      # to Labyrinth East
s                      # to Labyrinth South
s                      # to Stone Circle
s                      # back to Forest
w                      # back to Garden
s                      # back to Cottage
d                      # descend to Cellar
switch on lantern      # light the Cellar
examine crack          # discover the hidden coin
pry coin with twig    # dislodge the wedged coin
take coin             # the goddess's tribute
enter clock           # teleport to Alien World
give coin to goddess  # appease her
enter clock           # wake in Arkham — victory
```
