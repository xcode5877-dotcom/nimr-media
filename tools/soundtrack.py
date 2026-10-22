"""Original synthesized soundtrack for NM reels: warm piano-pad chords, soft pulse,
whooshes on scene wipes, a low 'hit' on the hook. Usage:
  python3 soundtrack.py OUT.wav DURATION BOUNDARY1,BOUNDARY2,...
"""
import sys, numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile

SR = 48000
out, dur = sys.argv[1], float(sys.argv[2])
bounds = [float(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 and sys.argv[3] else []
N = int(SR * dur)
t = np.arange(N) / SR
mix = np.zeros((N, 2))
rng = np.random.default_rng(7)

def note(f): return 440.0 * 2 ** ((f - 69) / 12)
def env(n, a, r):
    e = np.ones(n); ai = int(a * SR); ri = int(r * SR)
    if ai: e[:ai] = np.linspace(0, 1, ai)
    if ri: e[-ri:] *= np.linspace(1, 0, ri)
    return e
def lp(x, fc, order=2): return sosfilt(butter(order, fc, 'low', fs=SR, output='sos'), x)
def bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], 'band', fs=SR, output='sos'), x)

def add(sig, start, gain=1.0, pan=0.0):
    i = int(start * SR); j = min(N, i + len(sig))
    if i >= N: return
    s = sig[: j - i] * gain
    mix[i:j, 0] += s * (1 - pan) ; mix[i:j, 1] += s * (1 + pan)

BPM = 92; beat = 60 / BPM; bar = 4 * beat
# A minor, hopeful: Am - F - C - G (voicings in MIDI)
prog = [[57, 60, 64, 69], [53, 57, 60, 65], [48, 55, 60, 64], [55, 59, 62, 67]]
bass = [45, 41, 48, 43]

# pad
k = 0; st = 0.0
while st < dur:
    ch = prog[k % 4]; n = int(bar * SR) + int(0.6 * SR); tt = np.arange(n) / SR
    pad = np.zeros(n)
    for m in ch:
        f = note(m)
        for det in (-0.12, 0.12):
            pad += np.sin(2 * np.pi * f * (1 + det / 100) * tt) * 0.5 + 0.18 * np.sin(2 * np.pi * 2 * f * tt)
    pad = lp(pad, 1800) * env(n, 0.6, 0.8)
    add(pad / len(ch), st, 0.11, pan=0.0)
    # bass
    nb = int(bar * SR); tb = np.arange(nb) / SR
    b = np.sin(2 * np.pi * note(bass[k % 4]) * tb) * env(nb, 0.02, 0.4)
    add(b, st, 0.16)
    # soft piano plucks (arpeggio 8ths)
    for i in range(8):
        m = ch[[0, 1, 2, 3, 2, 1, 2, 3][i]] + 12
        n2 = int(1.2 * SR); t2 = np.arange(n2) / SR
        pl = (np.sin(2 * np.pi * note(m) * t2) + 0.3 * np.sin(2 * np.pi * 2 * note(m) * t2)) * np.exp(-t2 * 4.5)
        add(pl, st + i * beat / 2, 0.06, pan=(-0.3 if i % 2 else 0.3))
    st += bar; k += 1

# soft pulse: kick on 1 and 3, shaker on 8ths, starts after hook
for i in range(int(dur / beat) + 1):
    s0 = i * beat
    if s0 < 2.9: continue
    if i % 2 == 0:
        n = int(0.25 * SR); tt = np.arange(n) / SR
        kick = np.sin(2 * np.pi * (50 + 90 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 14)
        add(kick, s0, 0.30)
    n = int(0.06 * SR); hh = bp(rng.standard_normal(n), 6000, 12000) * np.exp(-np.arange(n) / SR * 60)
    add(hh, s0, 0.05, pan=0.4); add(hh, s0 + beat / 2, 0.035, pan=-0.4)

# hook impact at t=0.3 (when big word lands) — sub boom + noise burst
n = int(1.6 * SR); tt = np.arange(n) / SR
boom = np.sin(2 * np.pi * (40 + 60 * np.exp(-tt * 8)) * tt) * np.exp(-tt * 3)
add(boom, 0.30, 0.55)
nb = lp(rng.standard_normal(int(0.5 * SR)), 2500) * np.exp(-np.arange(int(0.5 * SR)) / SR * 9)
add(nb, 0.30, 0.12)

# whooshes centred on each wipe
for b0 in bounds:
    n = int(0.9 * SR); tt = np.arange(n) / SR
    noise = rng.standard_normal(n)
    w = np.zeros(n); seg = 2048
    for s in range(0, n, seg):
        x = s / n; fc = 300 + 5000 * np.sin(np.pi * x) ** 2
        w[s:s + seg] = bp(noise[s:s + seg], max(100, fc * 0.6), min(20000, fc * 1.4))
    w *= np.sin(np.pi * tt / tt[-1]) ** 2
    for c, pan in ((w, -0.6), (np.roll(w, 400), 0.6)):
        add(c, b0 - 0.45, 0.22, pan=pan)

# master: fade in/out, normalize, gentle saturation
fade = np.ones(N); fi = int(0.15 * SR); fo = int(1.8 * SR)
fade[:fi] = np.linspace(0, 1, fi); fade[-fo:] = np.linspace(1, 0, fo)
mix *= fade[:, None]
mix = np.tanh(mix * 1.4)
mix /= np.max(np.abs(mix)) + 1e-9
mix *= 0.89
wavfile.write(out, SR, (mix * 32767).astype(np.int16))
print('ok', out, dur)
