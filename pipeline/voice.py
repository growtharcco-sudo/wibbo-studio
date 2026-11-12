"""Free voices with Kokoro (Apache-2.0, commercial use allowed). Locked channel voices, see kit.VOICES:
  Wibbo    am_fenrir at 0.95, pitched up 1.35 with shifted formants, then polished
  narrator af_heart at 0.95
  duck     af_bella at 0.9, pitched up 1.6
Each phrase is made separately, so we know exactly when every beat starts and ends.
"""
import os, subprocess, tempfile, urllib.request
import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.environ.get("KOKORO_DIR", os.path.join(ROOT, "models"))
BASE = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
FILES = ["kokoro-v1.0.onnx", "voices-v1.0.bin"]
POLISH = "highshelf=f=7000:g=-3,equalizer=f=3500:t=q:w=1.2:g=-2,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120"
SR = 24000


def ensure_model():
    os.makedirs(MODEL_DIR, exist_ok=True)
    for f in FILES:
        p = os.path.join(MODEL_DIR, f)
        if not os.path.exists(p) or os.path.getsize(p) < 1_000_000:
            print("downloading", f)
            try: urllib.request.urlretrieve(BASE + f, p)
            except Exception: subprocess.run(["curl", "-sSL", "-o", p, BASE + f], check=True)
    return [os.path.join(MODEL_DIR, f) for f in FILES]


def _trim(a):
    i = np.where(np.abs(a) > 0.01)[0]
    return a[max(0, i[0] - 400):i[-1] + 1200] if len(i) else a


def synth(phrases, voices):
    """Returns (tracks, times, total). tracks = {"wibbo": array, "other": array} at 24 kHz, times = [(start, end)]."""
    from kokoro_onnx import Kokoro
    k = Kokoro(*ensure_model())
    clips, times, t = [], [], 0.0
    tmp = tempfile.mkdtemp()
    for i, ph in enumerate(phrases):
        t += float(ph.get("pause", 0.35))
        if "hold" in ph:
            times.append((round(t, 3), round(t + ph["hold"], 3))); t += ph["hold"]; continue
        v = voices[ph["by"]]
        a, sr = k.create(ph["say"], voice=v["voice"], speed=float(ph.get("speed", v["speed"])), lang="en-us")
        a = _trim(a)
        if v.get("fx"):
            src, dst = os.path.join(tmp, "a.wav"), os.path.join(tmp, "b.wav")
            sf.write(src, a, sr)
            af = v["fx"] + ("," + POLISH if v.get("polish") else "") + f",aresample={SR}"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-af", af, dst], check=True)
            a, sr = sf.read(dst)
        a = np.asarray(a, dtype=np.float64)
        if a.ndim > 1: a = a.mean(1)
        clips.append((ph["by"], t, a)); times.append((round(t, 3), round(t + len(a) / SR, 3))); t += len(a) / SR
    total = round(t + 0.9, 2)
    n = int(total * SR) + SR
    tracks = {"wibbo": np.zeros(n), "other": np.zeros(n)}
    for by, st, a in clips:
        i = int(st * SR); tr = tracks["wibbo" if by == "wibbo" else "other"]
        tr[i:i + len(a)] += a[:n - i] * (0.9 if by == "duck" else 1.0)
    return tracks, times, total
