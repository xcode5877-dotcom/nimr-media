"""Original synthesized soundtrack for NM reels: warm piano-pad chords, soft pulse,
whooshes on scene wipes, a low 'hit' on the hook. Usage:
  python3 soundtrack.py OUT.wav DURATION BOUNDARY1,BOUNDARY2,... [CUES.json]
CUES.json: [{"t":seconds,"k":"pop|impact|thud|swoosh|zip|tick|shimmer|riser|chime|wipe"}]
"""
import json
import sys, numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile

SR = 48000
out, dur = sys.argv[1], float(sys.argv[2])
bounds = [float(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 and sys.argv[3] else []
cues = json.load(open(sys.argv[4])) if len(sys.argv) > 4 else [{'t':0.42,'k':'impact'}]+[{'t':b,'k':'wipe'} for b in bounds]
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
    if s0 < (bounds[0] - 0.1 if bounds else 2.9): continue
    if i % 2 == 0:
        n = int(0.25 * SR); tt = np.arange(n) / SR
        kick = np.sin(2 * np.pi * (50 + 90 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 14)
        add(kick, s0, 0.30)
    n = int(0.06 * SR); hh = bp(rng.standard_normal(n), 6000, 12000) * np.exp(-np.arange(n) / SR * 60)
    add(hh, s0, 0.05, pan=0.4); add(hh, s0 + beat / 2, 0.035, pan=-0.4)

# ---------- motion SFX driven by cues ----------
def noise(n): return rng.standard_normal(n)
def sweep_noise(n, f0, f1, q=0.5):
    x = noise(n); y = np.zeros(n); seg = 1024
    for k0 in range(0, n, seg):
        r = k0 / max(1, n); fc = f0 * (f1 / f0) ** r
        y[k0:k0+seg] = bp(x[k0:k0+seg], max(60, fc*(1-q)), min(SR/2-100, fc*(1+q)))
    return y
def bell(f, d, decay):
    n = int(d*SR); tt = np.arange(n)/SR
    return (np.sin(2*np.pi*f*tt) + 0.4*np.sin(2*np.pi*2.76*f*tt) + 0.2*np.sin(2*np.pi*5.4*f*tt)) * np.exp(-tt*decay)

def sfx(k):
    if k == 'pop':
        n = int(0.12*SR); tt = np.arange(n)/SR
        return np.sin(2*np.pi*(320 + 900*np.exp(-tt*45))*tt) * np.exp(-tt*38), 0.32
    if k == 'impact':
        n = int(1.4*SR); tt = np.arange(n)/SR
        boom = np.sin(2*np.pi*(38 + 70*np.exp(-tt*9))*tt) * np.exp(-tt*2.8)
        crack = lp(noise(n), 3500) * np.exp(-tt*16)
        return boom + 0.35*crack, 0.62
    if k == 'thud':
        n = int(0.35*SR); tt = np.arange(n)/SR
        return np.sin(2*np.pi*(70 + 140*np.exp(-tt*25))*tt) * np.exp(-tt*11) + 0.15*lp(noise(n),1800)*np.exp(-tt*40), 0.42
    if k == 'swoosh':
        n = int(0.38*SR); tt = np.arange(n)/SR
        return sweep_noise(n, 500, 3500, 0.35) * np.sin(np.pi*tt/tt[-1])**2, 0.20
    if k == 'zip':
        n = int(0.26*SR); tt = np.arange(n)/SR
        tone = np.sin(2*np.pi*np.cumsum(900 + 2600*(tt/tt[-1]))/SR) * 0.25
        return (sweep_noise(n, 2000, 9000, 0.25) + tone) * np.sin(np.pi*tt/tt[-1]), 0.16
    if k == 'tick':
        n = int(0.05*SR); tt = np.arange(n)/SR
        return bp(noise(n), 2500, 7000) * np.exp(-tt*120), 0.22
    if k == 'shimmer':
        out_ = np.zeros(int(1.3*SR))
        for i, m in enumerate([81, 84, 88, 91, 93]):
            b_ = bell(note(m), 1.0, 5.5); s_ = int(i*0.07*SR); out_[s_:s_+len(b_)] += b_[:len(out_)-s_]
        return out_, 0.07
    if k == 'riser':
        n = int(1.0*SR); tt = np.arange(n)/SR
        return sweep_noise(n, 300, 6000, 0.3) * (tt/tt[-1])**2 * np.exp(-np.maximum(0, tt-0.9)*30), 0.22
    if k == 'chime':
        a_ = bell(note(76), 1.6, 3.2); b_ = bell(note(83), 1.6, 3.2)
        out_ = np.zeros(len(a_) + int(0.12*SR)); out_[:len(a_)] += a_; out_[int(0.12*SR):] += b_
        return out_, 0.12
    if k == 'wipe':
        n = int(0.9*SR); tt = np.arange(n)/SR
        w_ = sweep_noise(n, 250, 6500, 0.4) * np.sin(np.pi*tt/tt[-1])**2
        sub = np.sin(2*np.pi*(55+40*np.exp(-np.maximum(0,tt-0.45)*10))*tt) * np.exp(-np.maximum(0, tt-0.45)*7) * (tt>0.42)
        return w_ + 0.5*sub, 0.30
    return np.zeros(10), 0

PAN = {'swoosh': -0.35, 'zip': 0.35, 'tick': 0.25, 'shimmer': 0.2}
for c in cues:
    sig, g = sfx(c['k'])
    off = 0.45 if c['k'] == 'wipe' else 0.0
    if c['k'] == 'wipe':
        add(sig, c['t'] - off, g, pan=-0.5); add(np.roll(sig, 500), c['t'] - off, g, pan=0.5)
    else:
        add(sig, c['t'], g, pan=PAN.get(c['k'], 0.0))

# master: fade in/out, normalize, gentle saturation
fade = np.ones(N); fi = int(0.15 * SR); fo = int(1.8 * SR)
fade[:fi] = np.linspace(0, 1, fi); fade[-fo:] = np.linspace(1, 0, fo)
mix *= fade[:, None]
mix = np.tanh(mix * 1.4)
mix /= np.max(np.abs(mix)) + 1e-9
mix *= 0.89
wavfile.write(out, SR, (mix * 32767).astype(np.int16))
print('ok', out, dur)
