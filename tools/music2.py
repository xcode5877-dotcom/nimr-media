import numpy as np, sys
from scipy.signal import butter, sosfilt
from scipy.io import wavfile
# usage: music2.py out.wav dur style drop end
SR=48000; out,dur,style=sys.argv[1],float(sys.argv[2]),sys.argv[3]; DROP=float(sys.argv[4]); END=float(sys.argv[5])
N=int(SR*dur); mix=np.zeros((N,2)); rng=np.random.default_rng(11)
def note(m): return 440*2**((m-69)/12)
def lp(x,f): return sosfilt(butter(2,f,'low',fs=SR,output='sos'),x)
def hp(x,f): return sosfilt(butter(2,f,'high',fs=SR,output='sos'),x)
def bp(x,a,b): return sosfilt(butter(2,[a,b],'band',fs=SR,output='sos'),x)
def add(s,st,g=1,pan=0):
    i=int(st*SR)
    if i<0 or i>=N: return
    j=min(N,i+len(s)); s=s[:j-i]*g; mix[i:j,0]+=s*(1-pan); mix[i:j,1]+=s*(1+pan)
def env(n,a,d): t=np.arange(n)/SR; return np.minimum(1,t/a)*np.exp(-t*d)
def kick(f0=50,b=110,d=8):
    n=int(.4*SR); t=np.arange(n)/SR; return np.tanh(2.2*np.sin(2*np.pi*(f0+b*np.exp(-t*30))*t)*np.exp(-t*d))
def snap():
    n=int(.12*SR); t=np.arange(n)/SR; return bp(rng.standard_normal(n),1500,6000)*np.exp(-t*45)
def shaker():
    n=int(.06*SR); t=np.arange(n)/SR; return hp(rng.standard_normal(n),6000)*np.sin(np.pi*t/t[-1])
def piano(m,d=1.6):
    n=int(d*SR); t=np.arange(n)/SR; f=note(m)
    x=sum(np.sin(2*np.pi*f*k*t)*np.exp(-t*(2+k*1.5))/k**1.3 for k in range(1,8))
    return x*np.minimum(1,t/.004)
def marimba(m):
    n=int(.5*SR); t=np.arange(n)/SR; f=note(m)
    return (np.sin(2*np.pi*f*t)+.3*np.sin(2*np.pi*4*f*t)*np.exp(-t*30))*np.exp(-t*9)
def string(m,d):
    n=int(d*SR); t=np.arange(n)/SR; f=note(m)
    x=sum(np.sin(2*np.pi*f*(1+v)*t+ k) for k,v in enumerate([-.004,0,.004]))
    return lp(x,1800)*np.minimum(1,t/.8)*np.minimum(1,(d-t)/.5)/3
def subbass(m,d):
    n=int(d*SR); t=np.arange(n)/SR; return np.sin(2*np.pi*note(m-24)*t)*env(n,.01,1.5)

if style=='bright':   # chat reel: 104 bpm, major, marimba + snaps, playful
    bpm=104; beat=60/bpm; prog=[(60,[60,64,67]),(67,[67,71,74]),(69,[69,72,76]),(65,[65,69,72])]  # C G Am F
    bar=4*beat; pat=[0,2,1,2,0,2,1,2]
    for bi in range(int(dur/bar)+1):
        t0=bi*bar; r,ch=prog[bi%4]
        for i in range(8):
            st=t0+i*beat/2
            if st<dur: add(marimba(ch[pat[i]]+12),st,.22 if st>=DROP else .14,pan=(.25 if i%2 else -.25))
        if t0>=DROP and t0<END:
            for i in range(4):
                add(kick(55,90,10),t0+i*beat,.38 if i%2==0 else .0)
                if i%2: add(snap(),t0+i*beat,.35)
                for s in range(2): add(shaker(),t0+i*beat+s*beat/2+beat/4,.12,pan=.4)
            add(subbass(r,bar*.9),t0,.35)
        elif t0>=END: add(piano(ch[0]+12,2.5),t0,.18)
    add(kick(60,140,6),DROP,.6)
elif style=='tension':  # case reel: 88 bpm, minor, ticking + strings, cinematic
    bpm=88; beat=60/bpm; bar=4*beat; prog=[(57,[57,60,64]),(57,[57,60,65]),(53,[53,57,60]),(52,[52,56,59])]  # Am Am(F/A) F E
    for bi in range(int(dur/bar)+1):
        t0=bi*bar; r,ch=prog[bi%4]
        add(sum(string(m,bar+.4) for m in ch),t0,.22 if t0<DROP else .16)
        for i in range(8):  # clock tick 8ths
            n=int(.03*SR); add(bp(rng.standard_normal(n),2500,5000)*np.exp(-np.arange(n)/SR*120),t0+i*beat/2,.10)
        if DROP<=t0<END:
            add(kick(45,100,6),t0,.55); add(kick(45,100,6),t0+2*beat,.45); add(kick(45,100,6),t0+2.5*beat,.3)
            add(snap()*1.2,t0+beat,.25); add(snap()*1.2,t0+3*beat,.25)
            add(subbass(r,bar),t0,.45)
            for i in range(4): add(piano(ch[i%3]+24,1.2),t0+i*beat,.10)
        if t0>=END: add(piano(ch[0]+12,3),t0,.2)
    n=int(1.2*SR); t=np.arange(n)/SR; add(hp(rng.standard_normal(n),300)*(t/t[-1])**3,DROP-1.2,.18)
    add(kick(40,160,4),DROP,.7)
elif style=='piano':  # emotional: 76 bpm, piano arps + soft pulse
    bpm=76; beat=60/bpm; bar=4*beat; prog=[(62,[62,65,69]),(58,[58,62,65]),(60,[60,64,67]),(57,[57,61,64])]  # Dm Bb C A
    for bi in range(int(dur/bar)+1):
        t0=bi*bar; r,ch=prog[bi%4]
        for i,m in enumerate([0,1,2,1,0,2,1,2]):
            add(piano(ch[m]+12,1.8),t0+i*beat/2,.17 if t0>=DROP else .13,pan=(.2 if i%2 else -.2))
        add(piano(r-12,3),t0,.2)
        if DROP<=t0<END:
            add(kick(48,80,7),t0,.42); add(kick(48,80,7),t0+2*beat,.35)
            add(snap(),t0+beat,.18); add(snap(),t0+3*beat,.18)
            add(sum(string(m+12,bar+.3) for m in ch),t0,.12)
    add(kick(45,150,5),DROP,.55)
fade=np.ones(N); fo=int(1.5*SR); fade[-fo:]=np.linspace(1,0,fo); mix*=fade[:,None]
mix=np.tanh(mix*1.3); mix/=np.max(np.abs(mix))+1e-9; mix*=.85
wavfile.write(out,SR,(mix*32767).astype(np.int16)); print('ok',style)
