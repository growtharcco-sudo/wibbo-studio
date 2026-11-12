# Wibbo Studio

Makes Reels/Shorts for **Wibbo** (YouTube @HelloWibbo, Instagram @hellowibbo). Follow `ROUTINE.md` step by step.
Write a short brief, build it with `pipeline/kit.py`, check ONE sheet image, then render. Never hand-write coordinates.

Hard rules:
- Voices are locked (Kokoro): Wibbo = am_fenrir 0.95, pitched 1.35 with shifted formants; narrator = af_heart 0.95;
  duck = af_bella 0.9, pitched 1.6. Catchphrase "No, Wibbo!". Tagline "Silly Wibbo. Smart kids."
- No em dashes or en dashes anywhere. No age groups and no posting schedule in anything public.
- Every fact a Reel teaches is checked against a reputable source fetched the same day and listed in `sources`.
- Instagram caption: 3 to 5 hashtags including #wibbo. YouTube: made for kids = true, title under 70 characters.
- Quality: 1080x1920, 30 fps, x264 CRF 14 slow, AAC 256k. Never lower it. Do not change the look of the videos.
- James makes nothing himself: Claude owns script, voice, animation and sound.

Layout: `pipeline/kit.py` (brief -> spec + layout check), `pipeline/make_reel.py` (voices, mix, render, `--sheet`),
`pipeline/engine/` (the HTML/SVG engine: Wibbo, props, icons, the two sets), `assets/` (Poppins OFL font,
Kenney CC0 sounds). The Kokoro model downloads into `models/` on first run.
