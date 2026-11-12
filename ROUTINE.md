# Routine: making a Wibbo Reel

**Wibbo** is a kids' learning channel: YouTube "Wibbo" @HelloWibbo, Instagram @hellowibbo.
Wibbo is a silly teal creature who gets things wrong; the narrator says "No, Wibbo!" and the kids learn the right answer.
Tagline: "Silly Wibbo. Smart kids." Work in this repo and follow every rule below.

## 1. Pick the idea
- Pick a style (both look exactly like the first two episodes):
  - `mystery` (sky, grass, mystery egg): Wibbo guesses wrong, the viewer guesses, a countdown, the reveal.
  - `tries` (bathroom): Wibbo tries an everyday task the wrong way, gets corrected, then does it right.
- Check `specs/` so a topic or hook is not repeated within 30 days. Alternate styles when you can.
- 20 to 30 seconds. Something on screen changes every 2 to 3 seconds.

## 2. Write the script (house style)
- Hook in the first 2 seconds: Wibbo says what is happening ("Ooh! A mystery egg!", "Time to brush my teeth!").
- At least one wrong guess or wrong try, then the "No, Wibbo!" beat. Two wrong tries is the sweet spot.
- One question to the viewer ("What do you think it is?", "Did you brush your teeth today?").
- Short, simple words a small child knows. Wibbo is silly, never mean; nobody is ever laughed at.
- `say` is for the voice, numbers in words ("two whole minutes"); `cap` is what kids read ("2 whole minutes!").
- Captions: 1 to 4 words, max 2 lines (`|` breaks the line). UPPERCASE one word for emphasis ("Brush your TEETH!").
- Never write an age group or a posting schedule anywhere public (no "for 3 year olds", no "new video every day").
- No em dashes or en dashes anywhere (use commas, colons or "...").

## 3. Fact-check (any Reel that teaches something)
- Every fact a Reel teaches (how long to brush, how much toothpaste, why we wash hands) needs a reputable source
  fetched TODAY (health body, dental or medical association, government, encyclopedia). Put it in `sources`.
- If you cannot confirm it, change the lesson. Keep advice to safe, everyday habits; nothing medical.

## 4. Write a BRIEF, not a spec (the Reel kit, saves usage)
Write `briefs/<NNN>_<slug>.json` (NNN = next number after the highest in `specs/`), then build the spec:
```
python pipeline/kit.py briefs/<id>.json
```
The kit lays out every scene from ready, tested blocks. You only choose the scene kind and fill in the words.
**Never hand-write scene coordinates or timings, and never edit the engine for a single Reel.**
- Templates: `briefs/000_kit_example.json` (mystery egg) and `briefs/000_kit_tries_example.json` (brushing teeth).
  Copy the closest one. All scene kinds and fields are listed at the top of `pipeline/kit.py`.
- One beat = one spoken phrase. `by`: `wibbo`, `narrator` (default) or `duck`. A beat with `"show"` starts a
  new scene; beat 0 must have one (it is on screen at frame 0). `hold` = a silent action beat (e.g. a crack).
- Kinds: hook, crack, guess, wrong, no, lesson, right, ask, countdown, hatch, cheer, ending.
  Every Reel needs a `no` scene and ends with `ending`. `crack` and `hatch` are mystery only.
- Icons (thought bubbles, callouts, held items, what is in the egg): carrot, bus, duck, pea, egg, toothbrush,
  toothpaste, apple, banana, ball, sun, moon, star, heart, fish, cookie, cup, soap, sock, shoe, book, car, tree,
  flower, cake, timer. Need a new one? Add it to `ICONS` in `pipeline/engine/props.js` AND `kit.py`, once, in the same flat style.
- If `kit.py` prints LAYOUT PROBLEMS, shorten that text (or fix the field) and run it again.
- `cover`: `title` (2 short lines max, a question works best) and an optional `icon`.
- `post`: `instagram_caption` (hook line, blank line, one line that invites a comment, blank line,
  "Silly Wibbo. Smart kids.", blank line, 3 to 5 hashtags including #wibbo), `youtube_title` (under 70 characters,
  ends with "No, Wibbo!" when it fits), `youtube_description`, `"made_for_kids": true`.

## 5. Build and check
```
pip install -r requirements.txt --break-system-packages -q
python pipeline/make_reel.py specs/<id>.json --sheet   # ONE image: frame 0 + the end of every scene + cover. Read it once.
python pipeline/make_reel.py specs/<id>.json           # full render into queue/<id>/ (about 2.5 minutes)
```
Read only `queue/<id>/sheet.png` (do not open single stills). Check: the hook is readable at frame 0, no text cut
off, nothing covering Wibbo's face, captions match the script, the stamp lands on "No, Wibbo!".
Fix the brief, re-run kit.py and the sheet until clean. The spec checker refuses specs that break the hard rules.

## 6. Deliver
- `git add briefs specs && git commit -m "reel <id>" && git push` (videos stay out of git).
- Send James `queue/<id>/video.mp4` and `queue/<id>/cover.png` with SendUserFile, plus the Instagram caption
  and YouTube title/description in one message. On YouTube, set "Made for kids: yes".
