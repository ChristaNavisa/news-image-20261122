# news-image-20261122: The November Ledger, 22 November 2026

[![news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/ChristaNavisa/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/ChristaNavisa/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122)

One image summing up the world's news of Sunday 22 November 2026: a
one-page visual newspaper with 36 verified stories across 6 regions.

The front page leads with the day's three biggest stories — COP31 in
double overtime in Antalya, Iran's strikes on Bahrain, and Russia's
second strike on Kryvyi Rih — then a dot-matrix world map with the
day's eight hotspots, three columns of news (war and diplomacy, the
Gulf, climate and trade, Asia-Pacific, sport, and the day in brief),
a "By the numbers" band (India's record 720/9, Pant's 128, the
EU-Indonesia deal cutting 98.5% of tariffs, 5,700 Hong Kong voters,
Brent near $90), and a UTC timeline of the day.

The image is drawn from scratch by `main.py` (Python 3.13, standard
library only: its own PNG encoder, its own 5x7 bitmap font, and a
hand-built world map), so it runs the same way twice and produces
byte-identical output. Every story was checked against the day's
reporting (Reuters, AFP, COP31 live coverage, the Hong Kong election
office); claims are attributed where they are claims.

Run it:

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

That writes `out/entry.png` (1024x1024, about 30 KB, under the 1 MiB cap).
Without `MAKEFUN_OUTPUT_DIR` it writes `/output/entry.png`, as the
grader runs it.

License: MIT.
