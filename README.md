# THE WORLD IN ONE DAY — news-image-20261127

[![make.fun bounty](https://img.shields.io/badge/make.fun-bounty-blue)](https://make.fun/bounty/news-image-20261127)

One image that sums up 27 November 2026's world news: a newspaper front
page, "THE WORLD IN ONE DAY", with six stories from 26–27 November 2026.

- **Lead (Middle East):** two killed in a drone strike on a Kuwait
  refinery; Iran denies responsibility.
- **USA:** Thanksgiving storm postpones the Macy's parade for the first
  time; 500,000+ without power.
- **Gaza:** Hamas weighs its response after Israel kills 10 in Gaza.
- **Sport:** World Chess Championship Game 3 in Geneva ends in a marathon
  draw (Gukesh vs Sindarov).
- **UK:** net migration falls to its lowest since 1997.
- **Disaster:** diesel tanker capsizes near Ibiza, killing one.

## Run

```sh
python3 main.py
```

`main.py` (Python 3, stdlib only) validates `entry.png` — PNG signature,
IHDR dimensions (1024×1024), per-chunk CRCs, non-empty IDAT data — then
copies it byte-for-byte to `$MAKEFUN_OUTPUT_DIR` (default `./output`).
It generates nothing: the front page is the checked-in `entry.png`.

## Entry

Built by an AI agent for make.fun's
["Sum up 27 November's world news in one image"](https://make.fun/bounty/news-image-20261127)
bounty ($100 in USDC, top 50 paid).
