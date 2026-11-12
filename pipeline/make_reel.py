"""spec.json -> voices -> mix -> video + cover -> queue/<id>/

Usage:
  python pipeline/make_reel.py specs/<id>.json --sheet   # ONE check image: frame 0 + the end of every scene + cover
  python pipeline/make_reel.py specs/<id>.json           # full render into queue/<id>/
"""
import json, os, re, shutil, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit, voice, audio, render

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EM_DASH, EN_DASH = "—", "–"


def check_spec(spec):
    """Channel hard rules. Fails loudly instead of making something wrong."""
    errs = []
    every = json.dumps(spec, ensure_ascii=False)
    if EM_DASH in every or EN_DASH in every: errs.append("em/en dash found (channel rule: no em dashes)")
    if spec.get("voices") != kit.VOICES: errs.append("voices differ from the locked channel voices (do not edit them)")
    post = spec.get("post", {})
    for k in ("instagram_caption", "youtube_title", "youtube_description"):
        if not post.get(k): errs.append(f"post.{k} is missing")
    if post.get("made_for_kids") is not True: errs.append("post.made_for_kids must be true (YouTube COPPA setting)")
    ig = post.get("instagram_caption", "")
    tags = [w for w in ig.split() if w.startswith("#")]
    if not 3 <= len(tags) <= 5: errs.append(f"Instagram caption needs 3 to 5 hashtags, has {len(tags)}")
    if "#wibbo" not in [t.lower() for t in tags]: errs.append("Instagram caption must include #wibbo")
    if len(post.get("youtube_title", "")) > 70: errs.append("YouTube title over 70 characters")
    low = every.lower()
    for bad in (r"\byear[- ]olds?\b", r"\byears old\b", r"\bages? \d", r"\bfor (toddlers|preschoolers)\b",
                r"\bevery (day|week)\b", r"\bdaily\b", r"\bnew (video|episode)s? every\b"):
        if re.search(bad, low): errs.append(f"forbidden public wording (no ages, no posting schedule): {bad}")
    teaches = any(s["kind"] in ("lesson", "right") for s in spec["scenes"])
    if teaches and not spec.get("sources"): errs.append("this Reel teaches a fact: add the source to 'sources'")
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
    check_spec(spec)
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
    json.dump(spec["post"], open(os.path.join(out, "post.json"), "w"), indent=1, ensure_ascii=False)
    print(f"ready: {mp4} ({total:.1f}s)")


if __name__ == "__main__":
    main()
