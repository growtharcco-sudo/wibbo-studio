"""Draw the resolved spec with the HTML engine in headless Chromium and encode it.
Same settings as episodes 1 and 2: 1080x1920, 30 fps, x264 slow, CRF 14, tune animation, AAC 256k.
"""
import json, os, subprocess, sys
from multiprocessing import Process

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = "file://" + os.path.join(HERE, "engine", "engine.html")
FPS = 30


def _page(p, spec, lips):
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1920})
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(ENGINE); pg.evaluate("document.fonts.ready")
    pg.evaluate("([s,l])=>setData(s,l)", [spec, lips])
    return b, pg, errs


def stills(spec, lips, ts, base):
    from playwright.sync_api import sync_playwright
    out = []
    with sync_playwright() as p:
        b, pg, errs = _page(p, spec, lips)
        for t in ts:
            pg.evaluate(f"render({t})"); f = f"{base}.still_{t:06.2f}.png"; pg.screenshot(path=f); out.append(f)
        if errs: raise SystemExit("ENGINE ERROR: " + errs[0])
        b.close()
    return out


def cover(spec, lips, path):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b, pg, errs = _page(p, spec, lips)
        pg.evaluate("c=>cover(c)", spec.get("cover", {})); pg.screenshot(path=path)
        if errs: raise SystemExit("ENGINE ERROR: " + errs[0])
        b.close()


def _part(spec, lips, f0, f1, out):
    from playwright.sync_api import sync_playwright
    tmp = out[:-4] + ".part.mp4"
    with sync_playwright() as p:
        b, pg, errs = _page(p, spec, lips)
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-i", "-",
                               "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-tune", "animation", "-profile:v", "high",
                               "-pix_fmt", "yuv420p", "-r", str(FPS), tmp], stdin=subprocess.PIPE)
        for f in range(f0, f1):
            pg.evaluate(f"render({f / FPS})"); ff.stdin.write(pg.screenshot(type="png"))
        ff.stdin.close()
        if errs: print("ENGINE ERROR:", errs[0], file=sys.stderr)
        if ff.wait() == 0 and not errs: os.rename(tmp, out)
        b.close()


def video(spec, lips, total, wav, mp4, workers=2):
    nf = int(round(total * FPS)); work = os.path.join(os.path.dirname(mp4), "parts"); os.makedirs(work, exist_ok=True)
    cuts = [round(nf * i / workers) for i in range(workers + 1)]
    parts = [os.path.join(work, f"p{i}.mp4") for i in range(workers)]
    procs = [Process(target=_part, args=(spec, lips, cuts[i], cuts[i + 1], parts[i])) for i in range(workers)]
    [p.start() for p in procs]; [p.join() for p in procs]
    missing = [p for p in parts if not os.path.exists(p)]
    if missing: raise SystemExit(f"render failed: {missing}")
    lst = os.path.join(work, "list.txt")
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", wav,
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
                    "-shortest", "-movflags", "+faststart", mp4], check=True)
    for p in parts: os.remove(p)
    os.remove(lst); os.rmdir(work)
