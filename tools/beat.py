import numpy as np, sys
from scipy.signal import butter, sosfilt
from scipy.io import wavfile
SR=48000; dur=float(sys.argv[2]); DROP=float(sys.argv[3]); BREAK=float(sys.argv[4]); OUTRO=float(sys.argv[5])
N=int(SR*dur); mix=np.zeros((N,2)); rng=np.random.default_rng(3)
def note(m): return 440*2**((m-69)/12)
def lp(x,fc): return sosfilt(butter(2,fc,'low',fs=SR,output='sos'),x)
def hp(x,fc): return sosfilt(butter(2,fc,'high',fs=SR,output='sos'),x)
def add(sig,st,g=1,pan=0):
    i=int(st*SR)
    if i>=N or i<0: return
    j=min(N,i+len(sig)); s=sig[:j-i]*g; mix[i:j,0]+=s*(1-pan); mix[i:j,1]+=s*(1+pan)
BPM=120; beat=60/BPM; s16=beat/4; bar=4*beat
prog=[(57,[57,60,64]),(53,[53,57,60]),(48,[48,52,55]),(55,[55,59,62])]  # Am F C G
def kick():
    n=int(.35*SR); t=np.arange(n)/SR; return np.tanh(2.5*np.sin(2*np.pi*(45+120*np.exp(-t*35))*t)*np.exp(-t*9))
def clap():
    n=int(.25*SR); t=np.arange(n)/SR; x=hp(rng.standard_normal(n),900)
    e=np.exp(-t*22)+0.6*np.exp(-np.maximum(0,t-.012)*40)*(t>.012)+0.5*np.exp(-np.maximum(0,t-.024)*40)*(t>.024)
    return lp(x*e,6000)
def hat(o=False):
    n=int((.18 if o else .05)*SR); t=np.arange(n)/SR; return hp(rng.standard_normal(n),7000)*np.exp(-t*(18 if o else 90))
def bass808(m,d):
    n=int(d*SR); t=np.arange(n)/SR; f=note(m-12)
    x=np.sin(2*np.pi*f*t+0.8*np.sin(2*np.pi*f*t))*np.minimum(1,t*80)*np.exp(-t*1.2)
    return np.tanh(1.8*x)
def pluck(m):
    n=int(.35*SR); t=np.arange(n)/SR; f=note(m)
    saw=sum(np.sin(2*np.pi*f*k*t)/k for k in range(1,7))
    return lp(saw,3500)*np.exp(-t*12)
def pad(ch,d):
    n=int(d*SR); t=np.arange(n)/SR; x=sum(np.sin(2*np.pi*note(m)*t*(1+dt))for m in ch for dt in(-.003,.003))
    e=np.minimum(1,t/.3)*np.minimum(1,(d-t)/.3); return lp(x,1500)*e/len(ch)
nb=int(dur/bar)+1
for bi in range(nb):
    t0=bi*bar; root,ch=prog[bi%4]
    full = (DROP<=t0<BREAK) or (t0>=BREAK+bar/2 and t0<OUTRO)
    intro = t0<DROP
    add(pad([m+12 for m in ch],bar+.3),t0,.10 if intro else .07)
    # arp plucks 16ths
    pat=[0,1,2,1,0,2,1,2]
    for i in range(16):
        st=t0+i*s16
        if st>=dur: break
        if intro and st<DROP-bar: continue
        m=ch[pat[i%8]]+24
        g=.10 if full else .07
        add(pluck(m),st,g,pan=(.3 if i%2 else -.3))
    if full or (t0>=OUTRO):
        light = t0>=OUTRO
        for i in range(4):
            st=t0+i*beat
            if i in(0,) or (i==2): add(kick(),st,.55 if not light else .35)
            if i in(1,3): add(clap(),st,.30 if not light else .2)
        if not light:
            add(kick(),t0+2.75*beat,.4)
            for i in range(16): add(hat(i%4==2),t0+i*s16,.07 if i%2 else .045,pan=.35)
            add(bass808(root,bar*.48),t0,.42); add(bass808(root,bar*.45),t0+2*beat,.38)
# riser + downlifter into drop
n=int(1.6*SR); t=np.arange(n)/SR
r=hp(rng.standard_normal(n),400)*(t/t[-1])**2.5
add(lp(r,9000),DROP-1.6,.20)
add(kick()*1.2,DROP,.7)  # drop hit
# master
fade=np.ones(N); fo=int(1.5*SR); fade[-fo:]=np.linspace(1,0,fo); mix*=fade[:,None]
mix=np.tanh(mix*1.2); mix/=np.max(np.abs(mix))+1e-9; mix*=.85
wavfile.write(sys.argv[1],SR,(mix*32767).astype(np.int16)); print('beat ok')
