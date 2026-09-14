# The Goddess in the Cellar — Gameplay

A Lovecraftian text adventure in Inform 6. The player seeks refuge in a
decaying dwelling and discovers a passage to an alien world, where a flaming
goddess demands tribute.

## Premise

You find yourself before an ancient, foreboding cottage, seeking refuge from
forces you dare not name. Within lies a grandfather clock that is no mere
timepiece — it is a gate between worlds. Beyond the Forest, a Stone Circle
of standing stones forms a labyrinth around an altar bearing an ornate box
with a violet bloom essential for survival beyond.

## Walkthrough

### 1. The Cottage

You begin in the Cottage. Three objects are here:

- **rusty key** — on the floor. Unlocks the ornate box at the altar in the Stone Circle labyrinth.
- **brass lantern** — on a shelf. Switchable; grants light when lit. Essential
  for the dark Cellar below.
- **tattered notebook** — on the floor. Reading it (`read notebook`) reveals
  two pieces of advice, penned by a trembling hand:
  1. Eat the violet bloom that lies within the ornate box at the altar in the
     Stone Circle labyrinth before crossing through the clock. The air beyond
     is death to mortal lungs.
  2. The goddess of blue flame demands her sacrifice — the gold coin. Offer
     it freely, or be unmade.

### 2. The Garden

Go north to the Garden. This area is now a throughway to the Forest.
From here, proceed east to the **Dark Forest**.

### 3. The Forest

Go east to the **Dark Forest**. A faint path leads north to a clearing.

### 4. The Stone Circle and Labyrinth

North of the Forest stands a ring of weathered menhirs. Going north from the
clearing funnels you into a labyrinth of standing stones — a ring of 5 rooms
(South, East, North, West) plus a Blind Alley dead end. Navigate clockwise
(east) or counterclockwise (west) around the ring to Labyrinth North, then go
north to reach the **Altar Chamber** at the centre. There you find:

- **stone altar** — a dark slab stained by ancient sacrifice.
- **ornate wooden box** — sits atop the altar, locked, carved with shifting
  patterns.

To proceed:

1. Return to the Cottage and take the **rusty key**
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
- **gold coin** — glinting in the dust. This is the goddess's demanded
  sacrifice.

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

### 8. The Return

Enter the clock again to return to the Cellar. If the goddess has been
appeased, the game ends in victory: the clock's symbols go quiet, the
dwelling settles, and you have survived the beyond.

## Death conditions

| Cause | Trigger |
|-------|---------|
| Asphyxiation | Entering the Alien World without having eaten the flower |
| Lightning bolt | Performing any action in the goddess's presence except giving her the coin |
| Lightning bolt | Giving the goddess anything other than the coin |

## Win condition

Eat the flower from the ornate box, obtain the coin from the Cellar, appease
the goddess with the coin, then return through the clock to the Cellar. The
game ends with `*** You have won ***`.

## Required sequence

```
read notebook          # learn the two rules
take key              # for the ornate box
take lantern          # for the dark Cellar
n                      # to Garden
e                      # to Forest
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
take coin             # the goddess's tribute
enter clock           # teleport to Alien World
give coin to goddess  # appease her
enter clock           # return to Cellar — victory
```
