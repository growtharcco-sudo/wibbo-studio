"""Mix: voices + the bouncy pizzicato/tuba loop + sound effects placed automatically from the scene kinds.
Same music, sounds and levels as episodes 1 and 2. Sound effects: Kenney (CC0), see assets/sfx/LICENSE-kenney.txt.
"""
import json, os
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly, butter, sosfilt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SFX = os.path.join(ROOT, "assets", "sfx")
SR, FPS = 48000, 30
MUSIC = {  # chord roots, melody (MIDI), melody octave shift
    "mystery": ([48, 48, 53, 55], [[72, None, 76, 79], [77, 76, 72, None], [77, None, 81, 84], [83, 79, 74, None]], 0, 0.16, 0.05, 0.09),
    "tries": ([53, 53, 58, 60], [[77, None, 81, 84], [82, 81, 77, None], [82, None, 86, 89], [88, 84, 79, None]], -12, 0.15, 0.045, 0.085),
}


def mix(spec, tracks, times, total, out_wav, lips_json):
    N = int(SR * total); NF = int(FPS * total); rng = np.random.default_rng(2)
    zv = resample_poly(tracks["wibbo"], SR, 24000)[:N]; nv = resample_poly(tracks["other"], SR, 24000)[:N]
    zv = np.pad(zv, (0, N - len(zv))); nv = np.pad(nv, (0, N - len(nv)))
    voice = zv + nv * 0.95
    hop = SR // FPS
    e = np.array([np.sqrt(np.mean(zv[f * hop:(f + 1) * hop] ** 2)) if f * hop < N else 0 for f in range(NF)])
    e = e / (np.percentile(e[e > 0.001], 90) + 1e-9) if (e > 0.001).any() else e
    e = np.convolve(np.clip((e - 0.08) * 1.4, 0, 1), [.25, .5, .25], "same")

    def tt(d): return np.arange(int(d * SR)) / SR
    def add(b, s, st, g=1.0):
        i = int(st * SR)
        if i < 0 or i >= N: return
        j = min(N, i + len(s)); b[i:j] += g * s[:j - i]
    def nf(m): return 440 * 2 ** ((m - 69) / 12)
    def env(n, a=0.004, r=0.3):
        x = np.ones(n); na = max(1, int(a * SR)); x[:na] = np.linspace(0, 1, na); return x * np.exp(-np.arange(n) / (r * SR))
    def pizz(f, d=0.5): t = tt(d); return (np.sin(2*np.pi*f*t) + 0.4*np.sin(4*np.pi*f*t) + 0.15*np.sin(6*np.pi*f*t)) * env(len(t), 0.002, 0.12)
    def tuba(f, d=0.35): t = tt(d); s = sum(np.sin(2*np.pi*f*k*t)/k**1.5 for k in range(1, 6)); return s * np.clip(t/0.02, 0, 1) * np.exp(-t*7)
    def bell(f, d=1.0, r=0.35): t = tt(d); return (np.sin(2*np.pi*f*t) + 0.4*np.sin(2*np.pi*f*2.76*t)*np.exp(-t*6)) * env(len(t), 0.003, r)

    # resolved element times
    els = [e2 for sc in spec["scenes"] for e2 in sc["els"]]
    end_t = next((x["T"] for x in els if x["t"] == "end"), total)

    # music
    prog, mels, sh, gb, gp, gm = MUSIC[spec["style"]]
    music = np.zeros(N); beat = 0.5; t0 = 0; bar = 0
    while t0 < end_t:
        r = prog[bar % 4]
        for q in range(4):
            add(music, tuba(nf(r - 12 if q % 2 == 0 else r - 5), 0.3), t0 + q*beat, gb)
            for m in (r + 12, r + 16, r + 19): add(music, pizz(nf(m), 0.25), t0 + q*beat + beat/2, gp)
        for q, m in enumerate(mels[bar % 4]):
            if m: add(music, pizz(nf(m + sh), 0.4), t0 + q*beat, gm)
        t0 += 4 * beat; bar += 1
    g = np.ones(N)
    for x in els:
        if x["t"] == "duckmusic":  # quieter under the countdown, until the next scene
            g[int(x["T"] * SR):int(x["t1"] * SR)] = 0.3
    g[int((end_t - 0.2) * SR):] = 0
    g = np.convolve(g, np.ones(int(0.3 * SR)) / int(0.3 * SR), "same"); music *= g
    ve = np.convolve(np.abs(voice), np.ones(int(0.25 * SR)) / int(0.25 * SR), "same"); music *= 1 - 0.5 * np.clip(ve / 0.02, 0, 1)

    # sound effects
    sfx = np.zeros(N)
    def K(name, st, g=0.5):
        a, sr = sf.read(os.path.join(SFX, name + ".wav")); a = a.mean(1) if a.ndim > 1 else a
        a = resample_poly(a, SR, sr); add(sfx, a / (np.max(np.abs(a)) + 1e-9), st, g)
    def slam(st, g=0.35): t = tt(0.25); add(sfx, np.sin(2*np.pi*70*t) * np.exp(-t*18), st, g)
    def boing(st, g=0.12): t = tt(0.5); f = 240 + 240*np.exp(-t*6)*np.cos(t*40); add(sfx, np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-t*5), st, g)
    def crackK(st, g=0.32): K("glass_002", st, g); K("glass_005", st + 0.08, g*0.8); K("scratch_001", st + 0.02, g*0.35)
    def scrub(st, g=0.10):
        d = 0.14; sos = butter(2, [1800, 6000], "band", fs=SR, output="sos"); n = sosfilt(sos, rng.standard_normal(int(d*SR))) * np.sin(np.pi*tt(d)/d); add(sfx, n, st, g)
    def squelch(st, d=1.6, g=0.24):
        t = tt(d); f = 180 + 120*np.sin(2*np.pi*3*t) + 60*t; s = np.sin(2*np.pi*np.cumsum(f)/SR) * (0.6 + 0.4*np.sin(2*np.pi*9*t))
        sos = butter(2, 900, "low", fs=SR, output="sos"); s = sosfilt(sos, s + 0.3*rng.standard_normal(len(t))); add(sfx, s*np.clip(t/0.05, 0, 1)*np.clip((d-t)/0.15, 0, 1), st, g)
    def shrinkS(st, g=0.18): t = tt(0.6); f = 900*np.exp(-t*2.5) + 300; add(sfx, np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-t*2), st, g)
    def bells(st, ms, d, r, step, g): [add(sfx, bell(nf(m), d, r), st + i*step, g) for i, m in enumerate(ms)]

    boing(0.05)
    for x in els:
        if x["t"] != "sfx": continue
        n, T = x["name"], x["T"]
        if n == "crack": crackK(T)
        elif n == "drop": K("drop_001", T, 0.22)
        elif n == "no": K("error_006", T - 0.2, 0.32); slam(T + 0.05, 0.35)
        elif n == "no_head": K("error_006", T - 0.2, 0.28); slam(T + 0.05, 0.25); K("maximize_009", T + 0.1, 0.3); K("bong_001", T + 0.7, 0.45)
        elif n == "question": K("question_001", T, 0.2)
        elif n == "tick": K("tick_004", T, 0.35)
        elif n == "hatch": crackK(T, 0.45); crackK(T + 0.12, 0.4); K("confirmation_002", T + 0.1, 0.3); bells(T + 0.15, [84, 88, 91, 96], 0.8, 0.3, 0.05, 0.07)
        elif n == "sparkle": K("confirmation_002", T, 0.3); bells(T + 0.05, [84, 88, 91, 96], 0.8, 0.3, 0.05, 0.08)
        elif n == "end": K("confirmation_004", T, 0.25); bells(T + 0.1, [72, 76, 79, 84], 1.3, 0.45, 0.11, 0.12)
        elif n == "wrong_antenna": [scrub(T + 0.85 + i*0.14, 0.09) for i in range(14)]
        elif n == "wrong_toomuch": K("drop_002", T + 0.8, 0.25); squelch(T + 0.9)
        elif n == "wrong_upside": boing(T, 0.18)
        elif n == "shrink": shrinkS(T); K("drop_001", T + 0.75, 0.25)
        elif n == "rub": [scrub(T + i*0.14, 0.07) for i in range(28)]; [K("drop_001", T + 0.3 + i*0.45, 0.10) for i in range(8)]

    m = voice * 1.05 + music * 0.55 + sfx * 0.9; m = np.tanh(m * 1.1) / 1.1
    st = np.stack([m, m], 1); st[:, 0] += 0.04 * np.roll(music + sfx, 200); st[:, 1] += 0.04 * np.roll(music + sfx, -200)
    st /= np.max(np.abs(st)) / 0.89
    sf.write(out_wav, st, SR, subtype="PCM_24")
    json.dump({"fps": FPS, "z": [round(float(x), 3) for x in e]}, open(lips_json, "w"))
