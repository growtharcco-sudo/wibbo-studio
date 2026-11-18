"""spec.json -> voices -> mix -> video + cover -> queue/<id>/

Usage:
  python pipeline/make_reel.py specs/<id>.json --check   # channel rules only (captions, sources, math, voices)
  python pipeline/make_reel.py specs/<id>.json --sheet   # ONE check image: frame 0 + the end of every scene + cover
  python pipeline/make_reel.py specs/<id>.json           # full render into queue/<id>/
"""
import datetime as dt, json, math, os, re, shutil, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EM_DASH, EN_DASH = "\u2014", "\u2013"
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
BRAND_TAG = "#wibbo"
SLOTS = {"morning": "08:00 IST", "evening": "18:30 IST", "test": "end-to-end test only"}


def check_spec(spec, allow_old_sources=False):
    """Channel hard rules. Fails loudly instead of posting something wrong."""
    errs = []
    every = json.dumps(spec, ensure_ascii=False)
    if EM_DASH in every: errs.append("em dash found (channel rule: no em dashes)")
    if EN_DASH in every: errs.append("en dash found (use a comma, colon, 'to' or a hyphen)")
    if spec.get("voices") != kit.VOICES: errs.append("voices differ from the locked channel voices (build the spec with kit.py)")
    post = spec.get("post", {})
    for k in ("post_at", "slot", "instagram_caption", "youtube_title", "youtube_description"):
        if not post.get(k): errs.append(f"post.{k} is missing")
    if post.get("slot") and post["slot"] not in SLOTS: errs.append(f"post.slot must be one of {list(SLOTS)}")
    try:
        if dt.datetime.fromisoformat(post.get("post_at", "")).tzinfo is None: errs.append("post.post_at needs a timezone, like 2026-11-14T18:30:00+05:30")
    except ValueError: errs.append("post.post_at is not an ISO time, like 2026-11-14T18:30:00+05:30")
    if post.get("made_for_kids") is not True: errs.append("post.made_for_kids must be true (YouTube COPPA setting)")
    # Instagram caption: ends with a real question, then exactly 5 hashtags including #wibbo
    ig = post.get("instagram_caption", "")
    paras = [p.strip() for p in ig.strip().split("\n\n") if p.strip()]
    tags = re.findall(r"#\w+", ig)
    if len(tags) != 5: errs.append(f"Instagram caption needs exactly 5 hashtags, has {len(tags)}")
    if BRAND_TAG not in [t.lower() for t in tags]: errs.append(f"Instagram caption must include {BRAND_TAG}")
    if paras and not all(w.startswith("#") for w in paras[-1].split()): errs.append("Instagram caption must end with the hashtag line")
    if len(paras) < 2 or not paras[-2].rstrip().endswith("?"): errs.append("Instagram caption: the line just before the hashtags must be a real question")
    if len(ig) > 2200: errs.append("Instagram caption over 2,200 characters")
    yt = post.get("youtube_description", "")
    if len(post.get("youtube_title", "")) > 70: errs.append("YouTube title over 70 characters")
    if "#" in post.get("youtube_title", ""): errs.append("no hashtags in the YouTube title")
    if "Sources:" not in yt: errs.append("YouTube description needs a 'Sources:' list")
    if "#Shorts" not in yt: errs.append("YouTube description must end with 3 hashtags including #Shorts")
    if len(re.findall(r"#\w+", yt)) != 3: errs.append("YouTube description needs exactly 3 hashtags")
    # no age groups and no posting schedule anywhere public
    low = every.lower()
    for bad in (r"\byear[- ]olds?\b", r"\byears old\b", r"\bages? \d", r"\bfor (toddlers|preschoolers)\b",
                r"\b(video|videos|episode|episodes|reel|reels) every (day|week)\b", r"\bdaily (videos|episodes|reels|uploads)\b"):
        if re.search(bad, low): errs.append(f"forbidden public wording (no ages, no posting schedule): {bad}")
    # every fact from a reputable source fetched the same day; every number in math, checked in Python
    src = spec.get("sources", [])
    if not src: errs.append("sources is empty: every Reel teaches one real fact, and it needs a source")
    today = dt.datetime.now(IST).date().isoformat()
    for i, s in enumerate(src):
        if not isinstance(s, dict) or not s.get("url", "").startswith("http"): errs.append(f"sources[{i}] needs fact, url and fetched"); continue
        if not allow_old_sources and s.get("fetched") != today: errs.append(f"sources[{i}] must be fetched today ({today}), has {s.get('fetched')}")
    for i, m in enumerate(spec.get("math", [])):
        try:
            v = eval(m["expr"], {"__builtins__": {}}, {"round": round, "abs": abs, "min": min, "max": max, "int": int, "float": float, "sum": sum, "math": math})
            if abs(v - float(m["expect"])) > float(m.get("tol", 0.005)) * max(1, abs(float(m["expect"]))):
                errs.append(f"math[{i}] {m['expr']} = {v}, but the script says {m['expect']}")
        except Exception as e:
            errs.append(f"math[{i}] could not run: {e}")
    # numbers: digits in captions, or number words spoken outside the countdown, must be backed by math
    count_beats, prev = set(), 0
    for sc in spec["scenes"]:
        end = len(spec["phrases"]) if sc["until"] == "end" else sc["until"]
        if sc["kind"] == "countdown": count_beats.update(range(prev, end))
        prev = end
    NUMW = r"\b(two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|twenty|thirty|forty|fifty|hundred|thousand|million)\b"
    spoken = [p.get("say", "") for i, p in enumerate(spec.get("phrases", [])) if i not in count_beats]
    caps = [e.get("text", "") for sc in spec["scenes"] for e in sc["els"] if e["t"] == "cap"]
    if (re.search(r"\d", " ".join(caps)) or re.search(NUMW, " ".join(spoken).lower())) and not spec.get("math"):
        errs.append("the Reel states a number but math is empty: put every number in math, checked in Python")
    if not any(e.get("at") == -1 for e in spec["scenes"][0]["els"]): errs.append("scene 1 needs the hook on frame 0 (build the spec with kit.py)")
    if errs: raise SystemExit("SPEC CHECK FAILED:\n- " + "\n- ".join(errs))


def resolve(spec, times, total):
    """Turn beat indices into seconds: every dict with "at" gets "T"; scenes get t0/t1; captions get E."""
    starts = [t[0] for t in times]
    def T(d): return (0.0 if d["at"] == -1 else starts[d["at"]]) + d.get("delay", 0.0)
    def walk(o):
        if isinstance(o, dict):
            if "at" in o: o["T"] = round(max(0.0, T(o)), 3)
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(spec["scenes"])
    t0s = [0.0]
    for i in range(1, len(spec["scenes"])):   # a scene starts just before its first beat, or earlier if a visual leads in
        first = spec["scenes"][i - 1]["until"]
        lead = [e["T"] for e in spec["scenes"][i]["els"] if e["t"] not in ("sfx", "duckmusic", "cap") and e.get("at") == first]
        t0s.append(round(min([starts[first] - 0.15] + lead), 3))
    for i, sc in enumerate(spec["scenes"]):
        sc["t0"] = t0s[i]; sc["t1"] = t0s[i + 1] if i + 1 < len(t0s) else total
        for e in sc["els"]:
            e["t1"] = sc["t1"]
            if e["t"] == "cap": e["E"] = sc["t1"] if e["to"] == "end" else round(starts[e["to"]] - 0.15, 3)
    spec["total"] = total
    spec["phrases"] = [dict(p, T=times[i][0], T1=times[i][1]) for i, p in enumerate(spec["phrases"])]
    return spec


def main():
    path = sys.argv[1]
    spec = json.load(open(path))
    check_spec(spec, "--allow-old-sources" in sys.argv)
    if "--check" in sys.argv: print("spec check ok"); return
    import voice, audio, render
    out = os.path.join(ROOT, "queue", spec["id"]); os.makedirs(out, exist_ok=True)
    tracks, times, total = voice.synth(spec["phrases"], spec["voices"])
    spec = resolve(spec, times, total)
    wav, lips_p = os.path.join(out, "mix.wav"), os.path.join(out, "lips.json")
    audio.mix(spec, tracks, times, total, wav, lips_p)
    lips = json.load(open(lips_p))
    json.dump({"phrase_times": times, "total": total}, open(os.path.join(out, "timing.json"), "w"), indent=1)
    cov = os.path.join(out, "cover.png")
    if "--sheet" in sys.argv:   # cheap check: one image, one frame per scene with all its elements on screen
        ends = [(sc["t1"] - 0.1) if sc["until"] != "end" else total - 0.3 for sc in spec["scenes"]]
        ts = [0.0] + [round(t, 2) for t in ends]
        files = render.stills(spec, lips, ts, os.path.join(out, "check"))
        render.cover(spec, lips, cov)
        from PIL import Image, ImageDraw, ImageFont
        ims = [Image.open(f).resize((360, 640)) for f in files]
        cols = min(4, len(ims)); rows = (len(ims) + cols - 1) // cols
        sheet = Image.new("RGB", (360 * cols, 640 * rows + 360), "white")
        font = ImageFont.truetype(kit.FONT, 22); d = ImageDraw.Draw(sheet)
        labels = ["frame 0"] + [f"{sc['kind']} end {t:.1f}s" for sc, t in zip(spec["scenes"], ts[1:])]
        for i, im in enumerate(ims):
            x, y = (i % cols) * 360, (i // cols) * 640
            sheet.paste(im, (x, y)); d.rectangle([x, y, x + 360, y + 30], fill=(0, 0, 0)); d.text((x + 8, y + 3), labels[i], fill="white", font=font)
        sheet.paste(Image.open(cov).resize((202, 360)), (0, 640 * rows))
        d.text((214, 640 * rows + 10), f"cover  |  {spec['id']}  |  {total:.1f}s", fill="black", font=font)
        sheet.save(os.path.join(out, "sheet.png"))
        for f in files: os.remove(f)
        print("check sheet:", os.path.join(out, "sheet.png"), f"({total:.1f}s)"); return
    mp4 = os.path.join(out, "video.mp4")
    render.video(spec, lips, total, wav, mp4)
    render.cover(spec, lips, cov)
    os.remove(wav)
    shutil.copy(path, os.path.join(out, "spec.json"))
    post = dict(spec["post"], youtube_tags=spec["post"].get("youtube_tags") or spec.get("keywords", []))
    json.dump(post, open(os.path.join(out, "post.json"), "w"), indent=1, ensure_ascii=False)
    print(f"ready: {mp4} ({total:.1f}s)")


if __name__ == "__main__":
    main()
