# World News, 26 November 2026 — Storm Grounds the Parade

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/fatarichi/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/fatarichi/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

One image summing up the world news of Thursday 26 November 2026 — drawn entirely
in code, not text-only: a storm scene for the postponed 100th Macy's Thanksgiving
Day Parade, a container ship for the new US tariff proposals, a refinery at dusk
for the Houthi strikes pushing Brent near $95, and a London Tube train for the
tube strike, plus a markets strip and 24 more stories with drawn pictograms.

**Hero:** Thanksgiving storm grounds the 100th Macy's parade — the first weather
postponement in its history; the march moves to Saturday as gusts hit 60 mph.

**Inside:** 28 verified stories, each with its region and source, across the
Americas, Europe, the Middle East, Asia, Africa, markets and the Ukraine war —
plus a stats strip (Nikkei, KOSPI, Taiwan, Euro Stoxx futures, Brent) and a
DATE CHECK box confirming every story happened or was first reported on
26 November 2026, by event date.

`main.ts` (Node 22, standard library only) draws `entry.png` (1024×1024,
under 1 MiB) itself — a hand-rolled PNG encoder, a 5×7 bitmap font and drawing
primitives, no network, no clock, no randomness — and writes it to the output
directory. Run it with:

```
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```
