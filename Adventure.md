quit
# The Text Adventure: A Chronicling of the Old Ways and the New

Long ago, in the before-days, when the flickering cathode-ray oracles first graced the desks of men, there existed a peculiar and wondrous art: the Text Adventure. No moving pictures nor talking heads did these works employ, but rather the purest of alchemies—words upon the glass, conjuring entire worlds from the mind's own forge.

From the primordial mainframes emerged the first grimoires: *Colossal Cave*, wherein one typed `GET LAMP` and `XYZZY` as incantations to navigate the darkness. Then came the sorcerers of Infocom—Zork, the first of their line, born of the MIT labs like Promethean fire stolen from the gods themselves. With but a keyboard and the power of prose, they forged empires: *Enchanter*, *Planetfall*, *The Hitchhiker's Guide to the Galaxy*, each a masterwork of logic and language. Their Z-machine, a marvel of compactness, ran upon any device, from the humblest home computer to the mightiest of workstations.

For a golden decade, Infocom reigned supreme, their boxes adorned with the words "Feelies" and secrets sealed within. Yet as the tide of graphics rose—pixels multiplying like the spawn of some eldritch geometry—the house of Infocom faltered. The market demanded ever more color, ever less imagination. And so, in the year of our Lord nineteen hundred and eighty-nine, the great house fell, its assets scattered, its legacy left to gather dust in the attics of history.

But the flame did not die. From the ashes rose the Phoenix of Interactive Fiction. The brothers of the new age—Graham Nelson chief among them—took up the mantle. And lo, in the year nineteen hundred and ninety-three, Nelson did unveil Inform 6, a language of C-like precision yet designed for narrative. Not the free-form natural language of later days, but a structured tongue where objects are declared with the rigor of ontology:

```inform6
Object  -> lantern "brass lantern"
    with    name "brass" "lantern",
            description "A brass lantern hangs from the ceiling.",
            has     light,
            found_in Cottage;

Object  -> key "small key"
    with    name "small" "key",
            description "An old iron key.",
            has     small portable,
            found_in Cottage;
```

Here is the ontology made manifest: each noun is a class with properties (`has light`, `portable`), each location a container for objects, each relationship explicitly declared. The Z-machine, that ancient engine, was given new life, and with it, a renaissance: *Curses*, *Anchorhead*, *Galatea*—works that proved the written word could still command the soul of the player.

Thus the tradition endures, a quiet rebellion against the tyranny of the pixel. In this age of ever-brighter screens and ever-shorter attention, the old ways persist: a keyboard, a command prompt, and the boundless power of the reader's own mind.

And now, in this modern age of coding agents and artificial intelligences, the old magic finds new purpose. For we can now wield these systems with the aid of digital scribes, automating the tedious, accelerating the imaginative. The Text Adventure, once the province of solitary authors toiling in the dark, may now be forged in collaboration with agents that understand both the logic of code and the poetry of prose.

More: we may create persistent worlds with rigorous grammars—objectified counterparts to the free associations of the large language model. Here, in the neurosymbolic realm, we build not mere text but *ontologies*. Every noun a class, every verb an action, every relationship a mapped connection. The world knows what a key unlocks, what a coin can buy, what a goddess demands. This is no ephemeral hallucination, but a structure with the solidity of mathematics and the depth of literature.

The Text Adventure lives, and evolves. The keyboard remains. The mind still conjures. And now, the future unfolds.

---

For those seeking to explore these ancient arts: the [Inform 6 website](https://www.inform-fiction.org/) (home to the [Designer's Manual](https://www.inform-fiction.org/manual/html/index.html)) and the [Inform 6 library](https://gitlab.com/DavidGriffith/inform6lib) stand as the primary grimoires, with the [compiler on GitHub](https://github.com/DavidKinder/Inform6). The [Interactive Fiction Database (IFDB)](https://ifdb.org/) serves as the great library of Alexandria for this realm, chronicling thousands of works from the earliest Zork to the latest Inform 6 creations, with reviews, ratings, and the wisdom of the community.