# news-image-20261122: The World in One Day, 22 November 2026

[![news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/ChristaNavisa/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/ChristaNavisa/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122)

One image summing up the world's news of Sunday 22 November 2026:
a one-page illustrated newspaper with 36 verified stories across
7 regions.

The front page leads with the day's three biggest stories — the
COP31 final text in Antalya (10 pages, 94 paragraphs, no mention
of fossil fuels, 35% electrification by 2035), Iran's strikes on
US bases in Bahrain, and Russia's triple-tap strike on Kryvyi
Rih — each with its own drawn scene. Below them a dot-matrix
world map marks the day's 10 hotspots, then 12 illustrated story
cards (the Sparta II burning off Finland, India's record 720-9
in Wellington, Hong Kong's record 98.37% turnout, the Peru
quake, the Bayelsa boat sinking, the capture of "El Chapo
Isidro", the EU-Indonesia trade deal, Columbus stunning Messi's
Miami 3-0, France reaching the rugby final, Bolsonaro in
intensive care, Leeds routing Chelsea), a 21-item brief grid, a
"By the numbers" band (148 drones, 720-9, 98.37%, 35%, 6.7, 24)
and a UTC timeline with a date check.

Every story was checked against reporting from 20-22 November
2026 (Reuters, AP, CNN, BBC, the COP31 presidency, the Hong
Kong Elections Office, BCCI); claims are attributed where they
are claims, and the image carries its own date check and source
line.

The image is drawn from scratch by `main.py` (Python 3.13,
standard library only: its own PNG encoder, its own 5x7 bitmap
font, its own world map, fixed-seed grain), so it runs the same
way twice and produces byte-identical output.

Run it:

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

That writes `out/entry.png` (1024x1024, about 178 KB, under the
1 MiB cap). Without `MAKEFUN_OUTPUT_DIR` it writes
`/output/entry.png`, as the grader runs it.

License: MIT.
