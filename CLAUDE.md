# Wibbo Studio

This repo makes and posts one Reel a day for **Wibbo** (YouTube @HelloWibbo, Instagram @hellowibbo).
For every run, follow `ROUTINE.md` step by step. Never post directly: queue it, and GitHub Actions posts at `post_at`.
Hard rules:
- Write a brief and build the spec with `pipeline/kit.py`. Never hand-write scene coordinates or edit specs by hand.
- Check a Reel with `make_reel.py --check` and `--sheet`, and read only that one sheet.png, not single stills.
- Every fact from a reputable source fetched the same day; every number in `math`, checked in Python.
- No em dashes or en dashes. No age groups and no posting schedule in anything public.
- Instagram caption ends with a real question, then exactly 5 hashtags including #wibbo.
  YouTube: made for kids = true; description has a Sources list and 3 hashtags including #Shorts.
- Voices are locked (Kokoro): Wibbo = am_fenrir 0.95 pitched 1.35 with shifted formants; narrator = af_heart 0.95;
  duck = af_bella 0.9 pitched 1.6. Catchphrase "No, Wibbo!". Tagline "Silly Wibbo. Smart kids."
  Instagram AI label and YouTube synthetic-content disclosure stay on.
- Full quality: 1080x1920, 30 fps, x264 CRF 14 slow, AAC 256k. Never lower it. Do not change the look unless James asks.
- If James replies "skip", create `queue/<id>/SKIP`, commit and push.
- Never put tokens or passwords in files or chat: they live only in GitHub Secrets.

Layout: `pipeline/` (kit.py brief -> spec + layout check; make_reel.py voices, mix, render, --check, --sheet;
engine/ the HTML/SVG engine), `poster/` (Instagram, YouTube, media branch, publish_due), `tools/` (check_keys,
deep_check, get_youtube_token, backfill_thumbnails), `.github/workflows/`, `pages/` (site served from the media branch),
`assets/` (Poppins OFL font, Kenney CC0 sounds). The Kokoro model downloads into `models/` on first run.
