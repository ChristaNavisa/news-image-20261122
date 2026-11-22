# news-image-20261122: The World in One Day, 22 November 2026

[![news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/ChristaNavisa/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/ChristaNavisa/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122)

One image summing up the world's news of Sunday 22 November 2026:
a classic broadsheet front page, "THE WORLD IN ONE DAY".

39 verified stories across 7 regions, each dated Sunday 22 November
2026 and checked against wire reporting that day (Reuters, AP, AFP,
BBC, The Guardian, Al Jazeera, Ukrainian Air Force, the Hong Kong
government, ESA, F1, Cricinfo, Vatican News):

- A huge dated masthead, a six-number stats strip and a region strip.
- Three illustrated leads with drawn scenes, a headline, a 2-3 sentence
  body, a source line and a certainty tag: COP31 collapses with no deal
  after the EU rejects a text that never names fossil fuels; Russia
  fires 186 drones at Ukraine overnight, 161 downed, a block collapses
  in Dymer with 14 missing; Iran claims two US Patriot radars hit in
  Bahrain, Bahrain denies it.
- Fifteen illustrated cards: Hong Kong's record 98.79% Election
  Committee turnout, Verstappen winning the Las Vegas GP, India's
  record 720/9 in Wellington, the Sparta II still burning off Finland,
  the Cikande candy-factory fire, the Nigeria funeral-boat toll rising
  to 24, the Pope's lunch for 1,300 poor guests, BepiColombo reaching
  Mercury orbit, Iran's rolling power cuts, Wembanyama's 50 points,
  Bolsonaro in intensive care, the FBI database-hack probe, Belgian
  flights grounded, the Manipur toxic-liquor toll at 19, and Hamas
  seeking urgent talks on Gaza.
- A world map with numbered pins matching the story numbers, 21 more
  dated stories under "ALSO ON SUNDAY 22 NOVEMBER", and a DATE CHECK
  box listing the near-miss events left out because they happened on
  other days (the 400-drone barrage, the Kryvyi Rih double-tap,
  "El Chapo Isidro" captured, the Peru quake, and more).
- Certainty tags on every story: CONFIRMED (official or 2+ outlets),
  REPORTED (carried by the day's wires), CLAIM (one side's account,
  labelled as such), FORECAST (still to happen when drawn).

The image is drawn from scratch by `main.py` (Python 3.13,
standard library only: its own PNG encoder, its own 5x7 bitmap
font, its own drawn scenes and world map), so it runs the same way
twice and produces byte-identical output.

Run it:

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

That writes `out/entry.png` (1024x1024, about 50 KB, under the
1 MiB cap). Without `MAKEFUN_OUTPUT_DIR` it writes
`/output/entry.png`, as the grader runs it.

License: MIT.
