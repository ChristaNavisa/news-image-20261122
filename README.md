# news-image-20261122: The World in One Day, 22 November 2026

[![news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/ChristaNavisa/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/ChristaNavisa/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122)

One image summing up the world's news of Sunday 22 November 2026:
a one-day timeline infographic, not a newspaper. A night-sky
canvas carries a sun arc from moon to sun, and the day is told
as six chapters — NIGHT, DAWN, MORNING, MIDDAY, AFTERNOON,
EVENING — each a row of six pictogram-led story cells joined by
a timeline spine that snakes left-to-right, then right-to-left.

36 verified stories across 7 regions, each with a drawn
pictogram, a two-line headline and a dated sub-line: the COP31
talks in double overtime in Antalya (draft drops fossil fuels,
concedes 1.5C), Russia's 186-drone night barrage on Ukraine and
the Sparta II burning in the Baltic, Iran's strikes on Bahrain,
Poland's airspace breach, Hong Kong's Election Committee polls
(89.8% turnout by 1pm), the capture of "El Chapo Isidro", the
Geneva killer-robot talks, and Alcaraz reaching the ATP final.

Every story was checked against reporting from 22 November
2026 (Reuters, AP, the COP31 presidency, the Hong Kong
Elections Office, Finnish Border Guard); claims are attributed
where they are claims, and the image carries its own date and
source line.

The image is drawn from scratch by `main.py` (Python 3.13,
standard library only: its own PNG encoder, its own 5x7 bitmap
font, its own pictograms and sun arc, fixed-seed grain), so it
runs the same way twice and produces byte-identical output.

Run it:

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

That writes `out/entry.png` (1024x1024, about 234 KB, under the
1 MiB cap). Without `MAKEFUN_OUTPUT_DIR` it writes
`/output/entry.png`, as the grader runs it.

License: MIT.
