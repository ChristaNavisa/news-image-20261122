# Sum up 22 November's world news in one image

[![news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/c/news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/ChristaNavisa/news-image-20261122/rank.svg)](https://make.fun/c/news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/ChristaNavisa/news-image-20261122/reward.svg)](https://make.fun/c/news-image-20261122)

A one-page visual newspaper of Sunday 22 November 2026, drawn from scratch
in pure Python (standard library only): a hand-written PNG encoder and a
5x7 bitmap font render the masthead, the date, and six stories with
procedurally drawn scenes.

Stories: COP31 nears a final deal in Antalya; drones hit the Russian cargo
ship Sparta II in the Gulf of Finland; Iran strikes reported in the Gulf;
an M6.8 quake shakes Peru's Andes; cartel kingpin "El Chapo Isidro" is
arrested in Mexico; India pass 520 for a record Test total in New Zealand.
Plus an "Also today" strip: Zelensky on the Crimea Bridge strikes, Denmark's
assassination-plot accusation, Estonia's border closure, Trump in Shenzhen
for APEC, the FBI crime-database hack probe, and the $7.25bn Roundup payout.

Run it with:

```
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

It writes `out/entry.png` (1024x1024, under 1 MiB). Two runs write
byte-identical files.
