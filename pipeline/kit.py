"""Reel kit: a short BRIEF -> a full spec, so nobody hand-writes timings or coordinates.

Usage:  python pipeline/kit.py briefs/<id>.json      -> writes specs/<id>.json, or prints LAYOUT PROBLEMS and exits 1

A brief is:
  id, style ("mystery" or "tries"), series, keywords
  beats: one beat = one spoken phrase (or one silent action)
     say    what is spoken (words, not digits)            by     "wibbo" | "narrator" (default) | "duck"
     cap    on-screen caption for this beat ("|" = new line, "" = clear)   big   true/false to force caption size
     pause  seconds of silence BEFORE this beat (default 0.35)             speed  voice speed override
     hold   silent beat of this many seconds instead of "say" (an action with no words, e.g. a crack)
     show   {"kind": ..., fields}  starts a new scene. Beat 0 must have one, and its elements are on screen at frame 0.
  cover {"title": "...", "icon": "egg"}, sources, post: copied as-is.

Scene kinds (fields in brackets). Every kind works in both styles; positions come from the style's set.
  hook      [hold: icon Wibbo holds, inside: what is in the egg (mystery)]   Wibbo waves / shows the item, big caption
  crack     [peek: foot|tuft|<icon>, sound: "Quack!"]   (mystery) the egg cracks, something peeks out, Wibbo jumps back
  guess     [icon]                                      Wibbo's wrong guess in a thought bubble, proud pose
  wrong     [how: antenna|toomuch|upside]               (tries) Wibbo does it the wrong way with the held item
  no        [head: true]                                NO, WIBBO! stamp, squash, sad. 2nd beat = calm correction.
                                                         head (mystery, after hatch): the hatchling jumps on his head
  lesson    [icon]                                      the right fact, big caption, icon in a callout (pea, timer, ...)
  right     [timer: true]                               (tries) the right way: shows item, then brushes/rubs, foam;
                                                         timer: a 2-minute dial on the last beat
  ask       []                                          question to the viewer ("What do YOU think?")
  countdown []                                          one beat per number: 3 beats -> 3, 2, 1
  hatch     []                                          (mystery) the egg hatches, the inside pops out with stars
  cheer     [sparkle: true]                             Wibbo celebrates; sparkle = sparkly grin and stars
  ending    [buddy: duck|<icon>]                        end card: WIBBO logo, tagline, waving Wibbo
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(ROOT, "assets", "fonts", "Poppins-Bold.ttf")

# Locked voices (channel rule). make_reel.py refuses a spec whose voices differ.
VOICES = {
    "wibbo": {"voice": "am_fenrir", "speed": 0.95, "fx": "rubberband=pitch=1.35:formant=shifted:pitchq=quality", "polish": True},
    "narrator": {"voice": "af_heart", "speed": 0.95},
    "duck": {"voice": "af_bella", "speed": 0.9, "fx": "rubberband=pitch=1.6:formant=shifted:pitchq=quality"},
}
STYLES = {  # must match pipeline/engine/sets.js
    "mystery": {"capY": 250, "capBig": 120, "stampY": 430, "digitY": 470, "egg": [640, 1060], "bubble": [250, 820]},
    "tries": {"capY": 260, "capBig": 118, "stampY": 470, "digitY": 470, "bubble": [330, 700]},
}
ICONS = ["carrot", "bus", "duck", "pea", "egg", "toothbrush", "toothpaste", "apple", "banana", "ball", "sun", "moon",
         "star", "heart", "fish", "cookie", "cup", "soap", "sock", "shoe", "book", "car", "tree", "flower", "cake", "timer"]
BIG_KINDS = {"hook", "lesson", "hatch", "ending"}


def E(t, at, **k):
    return dict(t=t, at=at, **k)


# ---------- scene kinds: (fields, first beat, beats in scene, context) -> elements ----------
def k_hook(f, b, nb, ctx):
    els = [E("act", -1, do="intro", **({"hold": f["hold"]} if f.get("hold") else {}))]
    if ctx["style"] == "mystery" and not f.get("hold"):
        ctx["egg"] = E("egg", -1, inside=f.get("inside", "duck"), cracks=[])
        els.append(ctx["egg"])
    return els

def k_crack(f, b, nb, ctx):
    if not ctx.get("egg"): ctx["errors"].append("crack needs a mystery hook with the egg first")
    else: ctx["egg"]["cracks"].append({"at": b, "delay": 0.0, "peek": f.get("peek"), "sound": f.get("sound")})
    return [E("act", b, do="surprise"), E("sfx", b, name="crack")] + \
           ([E("sfx", b, delay=0.25, name="drop")] if f.get("peek") else [])

def k_guess(f, b, nb, ctx):
    return [E("act", b, do="guess"), E("bubble", b, icon=f.get("icon", "star")), E("sfx", b, delay=0.5, name="drop")]

def k_wrong(f, b, nb, ctx):
    how = f.get("how", "upside")
    return [E("act", b, do=how), E("sfx", b, name="wrong_" + how)]

def k_no(f, b, nb, ctx):
    act = E("act", b, do="no")
    if f.get("head"):
        act["head"] = True
        if ctx.get("egg"): ctx["egg"]["jump"] = {"at": b, "delay": 0.1}
    later = [i for i in range(b + 1, b + nb) if ctx["beats"][i].get("by", "narrator") == "narrator"]
    if later: act["recover"] = {"at": later[0]}
    return [E("stamp", b), act, E("sfx", b, name="no" + ("_head" if f.get("head") else ""))]

def k_lesson(f, b, nb, ctx):
    ic = f.get("icon")
    shrink = ctx.get("pile", 0) > 100
    if shrink: ctx["pile"] = 13
    els = [E("act", b, do="lesson")]
    if ic == "timer": els.append(E("timer", b))
    elif ic: els.append(E("callout", b, icon=ic, delay2=1.3 if shrink else 0.3))
    if shrink: els.append(E("sfx", b, delay=0.6, name="shrink"))
    return els

def k_right(f, b, nb, ctx):
    ctx["pile"] = 0
    act = E("act", b, do="right", rub={"at": b + 1, "delay": 1.2} if nb > 1 else {"at": b, "delay": 1.6})
    if nb > 1: act["calm"] = {"at": b + 1}
    els = [act, E("sfx", act["rub"]["at"], delay=act["rub"]["delay"], name="rub")]
    if f.get("timer"): els.append(E("timer", b + nb - 1))
    return els

def k_ask(f, b, nb, ctx):
    return [E("act", b, do="lean" if ctx["style"] == "mystery" else "smile"), E("sfx", b, delay=-0.1, name="question")]

def k_countdown(f, b, nb, ctx):
    n = nb
    if ctx.get("egg"): ctx["egg"]["rumble"] = {"at": b}
    els = [E("digit", b + i, n=str(n - i)) for i in range(n)]
    els += [E("sfx", b + i, delay=-0.02, name="tick") for i in range(n)]
    els.append(E("act", b, do="lean", digits=[{"at": b + i} for i in range(n)]))
    els.append(E("duckmusic", b, delay=-0.3))
    return els

def k_hatch(f, b, nb, ctx):
    if not ctx.get("egg"): ctx["errors"].append("hatch needs a mystery hook with the egg first"); return []
    ctx["egg"]["hatch"] = {"at": b, "delay": -0.2}
    ctx["hatched"] = True
    return [E("act", b, delay=-0.2, do="shock"), E("sfx", b, delay=-0.2, name="hatch")]

def k_cheer(f, b, nb, ctx):
    els = [E("act", b, do="cheer", **({"sparkle": True} if f.get("sparkle") else {}))]
    if f.get("sparkle"): els.append(E("sfx", b, delay=-0.15, name="sparkle"))
    return els

def k_ending(f, b, nb, ctx):
    buddy = f.get("buddy", ctx["egg"].get("inside") if ctx.get("hatched") else None)
    return [E("end", b, delay=-0.5, **({"buddy": buddy} if buddy else {})), E("sfx", b, delay=-0.5, name="end")]

KINDS = {"hook": k_hook, "crack": k_crack, "guess": k_guess, "wrong": k_wrong, "no": k_no, "lesson": k_lesson,
         "right": k_right, "ask": k_ask, "countdown": k_countdown, "hatch": k_hatch, "cheer": k_cheer, "ending": k_ending}
MIN_PAUSE = {"crack": 0.2, "no": 0.15, "hatch": 0.45, "ending": 0.6}


def build_spec(brief):
    style = brief.get("style", "mystery")
    if style not in STYLES: raise SystemExit(f"unknown style {style!r}: use one of {list(STYLES)}")
    beats = brief["beats"]
    if not beats or "show" not in beats[0]: raise SystemExit("beat 0 must have a 'show' (the hook frame)")
    ctx = {"style": style, "errors": [], "pile": 0, "beats": beats}
    phrases, starts = [], [i for i, bt in enumerate(beats) if "show" in bt]
    for i, bt in enumerate(beats):
        kind = None
        for s in reversed(starts):
            if s <= i: kind = beats[s]["show"]["kind"]; break
        ph = {"by": bt.get("by", "narrator"), "pause": float(bt.get("pause", 0.35))}
        if "show" in bt and bt["show"]["kind"] in MIN_PAUSE and i > 0: ph["pause"] = max(ph["pause"], MIN_PAUSE[bt["show"]["kind"]])
        if "hold" in bt: ph["hold"] = float(bt["hold"])
        else: ph["say"] = bt["say"]
        if "speed" in bt: ph["speed"] = float(bt["speed"])
        if i == 0: ph["pause"] = 0.3
        phrases.append(ph)
    scenes = []
    for si, s in enumerate(starts):
        end = starts[si + 1] if si + 1 < len(starts) else len(beats)
        show = beats[s]["show"]; kind = show.get("kind")
        if kind not in KINDS: ctx["errors"].append(f"beat {s}: unknown kind {kind!r}"); continue
        f = {k: v for k, v in show.items() if k != "kind"}
        if kind == "wrong" and f.get("how") == "toomuch": ctx["pile"] = 215
        els = KINDS[kind](f, s, end - s, ctx)
        if si == 0:
            for e in els:
                if e.get("at") == 0: e["at"] = -1
        # captions: one per beat that has "cap", shown until the next caption in this scene or the scene end
        capbeats = [i for i in range(s, end) if "cap" in beats[i]]
        for j, i in enumerate(capbeats):
            if not beats[i]["cap"]: continue
            big = beats[i].get("big", kind in BIG_KINDS or (kind == "cheer" and f.get("sparkle"))
                               or (kind == "ask" and style == "tries") or (kind == "right" and f.get("timer") and i == end - 1))
            to = capbeats[j + 1] if j + 1 < len(capbeats) else "end"
            els.append(E("cap", -1 if i == 0 else i, text=beats[i]["cap"], big=bool(big), to=to))
        scenes.append({"kind": kind, "until": end if end < len(beats) else "end", "els": els})
    spec = {"id": brief["id"], "style": style, "series": brief.get("series", ""), "voices": VOICES,
            "keywords": brief.get("keywords", []), "phrases": phrases, "scenes": scenes,
            "cover": brief.get("cover", {}), "sources": brief.get("sources", []), "math": brief.get("math", []),
            "post": brief.get("post", {})}
    return spec, ctx["errors"]


# ---------- layout check ----------
SAFE = (40, 1040, 130, 1450)   # x min, x max, top, bottom: Instagram's buttons and caption cover the rest

def text_w(text, size):
    from PIL import ImageFont
    return ImageFont.truetype(FONT, size).getlength(text)

def layout_check(spec, brief):
    st = STYLES[spec["style"]]; probs = []
    def box(text, size, cx, top, stroke, label):
        w = text_w(text, size) + stroke
        if cx - w / 2 < SAFE[0] or cx + w / 2 > SAFE[1]: probs.append(f"{label}: '{text}' is {w:.0f}px wide, max {SAFE[1]-SAFE[0]} (shorten it)")
        if top < SAFE[2] or top + size > SAFE[3]: probs.append(f"{label}: '{text}' is outside the safe area (y {top:.0f})")
    def caption(text, big, label):
        lines = text.split("|"); fs = st["capBig"] if big else 96
        if len(lines) > 2: probs.append(f"{label}: caption has {len(lines)} lines, max 2"); return
        for i, l in enumerate(lines):
            base = st["capY"] + (i - (len(lines) - 1) / 2) * fs * 1.14 + fs * 0.35
            box(l, fs, 540, base - fs * 0.75, 24, label)
    for si, sc in enumerate(spec["scenes"]):
        for e in sc["els"]:
            lab = f"scene {si} ({sc['kind']})"
            if e["t"] == "cap": caption(e["text"], e["big"], lab)
            if e["t"] in ("bubble", "callout") and e["icon"] not in ICONS: probs.append(f"{lab}: unknown icon {e['icon']!r}")
            if e["t"] == "act" and e.get("hold") and e["hold"] not in ICONS: probs.append(f"{lab}: unknown held icon {e['hold']!r}")
            if e["t"] == "egg" and e["inside"] not in ICONS: probs.append(f"{lab}: unknown egg inside {e['inside']!r}")
            if e["t"] == "egg":
                for c in e["cracks"]:
                    if c.get("peek") and c["peek"] not in ICONS + ["foot", "tuft"]: probs.append(f"{lab}: unknown peek {c['peek']!r}")
                    if c.get("sound"):  # floats up from the egg's top right corner
                        w = text_w(c["sound"], 92) + 20
                        if st["egg"][0] + 230 + w / 2 > SAFE[1] + 20: probs.append(f"{lab}: sound word '{c['sound']}' too wide ({w:.0f}px, max {2*(SAFE[1]+20-st['egg'][0]-230):.0f})")
            if e["t"] == "act" and e["do"] in ("antenna", "toomuch", "upside") and not any(
                    x.get("hold") for s2 in spec["scenes"] for x in s2["els"] if x["t"] == "act"):
                probs.append(f"{lab}: 'wrong' needs the hook to 'hold' an item")
            if e["t"] == "digit" and len(sc["els"]) and int(e["n"]) > 5: probs.append(f"{lab}: countdown longer than 5")
    box("NO, WIBBO!", 140, 540, st["stampY"] - 50, 40, "stamp")
    cv = spec.get("cover", {})
    if cv.get("title"): caption(cv["title"], True, "cover title")
    else: probs.append("cover.title is missing")
    if cv.get("icon") and cv["icon"] not in ICONS: probs.append(f"cover: unknown icon {cv['icon']!r}")
    for i, p in enumerate(spec["phrases"]):
        s = p.get("say", "")
        if re.search(r"\d", s): probs.append(f"beat {i}: write numbers as words in 'say' ({s!r})")
        if "say" not in p and "hold" not in p: probs.append(f"beat {i}: needs 'say' or 'hold'")
        if p["by"] not in VOICES: probs.append(f"beat {i}: 'by' must be one of {list(VOICES)}")
    kinds = [s["kind"] for s in spec["scenes"]]
    if kinds and kinds[-1] != "ending": probs.append("the last scene must be 'ending' (the end card)")
    if "no" not in kinds: probs.append("every Reel needs at least one 'no' scene (NO, WIBBO!)")
    if any(k in kinds for k in ("crack", "hatch")) and spec["style"] != "mystery": probs.append("crack and hatch are mystery-style kinds")
    return probs


def main():
    path = sys.argv[1]
    brief = json.load(open(path))
    spec, errs = build_spec(brief)
    probs = errs + layout_check(spec, brief)
    if probs:
        print("LAYOUT PROBLEMS:\n- " + "\n- ".join(probs)); sys.exit(1)
    os.makedirs(os.path.join(ROOT, "specs"), exist_ok=True)
    out = os.path.join(ROOT, "specs", spec["id"] + ".json")
    json.dump(spec, open(out, "w"), indent=1, ensure_ascii=False)
    print(f"layout ok -> {out} ({len(spec['scenes'])} scenes, {len(spec['phrases'])} beats)")


if __name__ == "__main__":
    main()
