"""Original synthesized music for KORVEX motion videos (no third-party audio).
usage: python3 music.py config.json out.wav"""
import json, sys, numpy as np
from scipy.signal import fftconvolve, butter, sosfilt

SR = 48000
rng = np.random.default_rng(7)
NOTE = {'C':0,'C#':1,'Db':1,'D':2,'D#':3,'Eb':3,'E':4,'F':5,'F#':6,'Gb':6,'G':7,'G#':8,'Ab':8,'A':9,'A#':10,'Bb':10,'B':11}
def hz(n):  # 'A4'
    name, octv = n[:-1], int(n[-1]); m = NOTE[name] + 12*(octv+1); return 440*2**((m-69)/12)

def env_adsr(n, a, d, s, r, total):
    t = np.arange(total)/SR; e = np.ones(total)*s
    A=int(a*SR); D=int(d*SR); R=int(r*SR)
    e[:A] = np.linspace(0,1,A,endpoint=False) if A>0 else e[:A]
    e[A:A+D] = np.linspace(1,s,max(1,min(D,total-A)))[:len(e[A:A+D])]
    rel_start = max(0,n-R) if n<total else total-R
    if R>0: e[rel_start:rel_start+R] *= np.linspace(1,0,len(e[rel_start:rel_start+R]))
    e[rel_start+R:] = 0
    return e

def lp(x, f, order=2):
    sos = butter(order, f/(SR/2), 'low', output='sos'); return sosfilt(sos, x)
def hp(x, f, order=2):
    sos = butter(order, f/(SR/2), 'high', output='sos'); return sosfilt(sos, x)
def bp(x, lo, hi):
    sos = butter(2, [lo/(SR/2), hi/(SR/2)], 'band', output='sos'); return sosfilt(sos, x)

def pad_note(f, dur, amp):
    n=int(dur*SR); t=np.arange(n)/SR; y=np.zeros(n)
    for det in (-0.12, 0, 0.11):
        ff=f*2**(det/12)
        for h,a in ((1,1),(2,.35),(3,.18),(4,.08)):
            y+=a*np.sin(2*np.pi*ff*h*t+rng.random()*6.28)
    e=np.minimum(1,t/1.2)*np.minimum(1,(dur-t)/1.0).clip(0)
    return lp(y*e*amp,2200)

def pluck(f, dur, amp, bright=1.0):
    n=int(dur*SR); t=np.arange(n)/SR; y=np.zeros(n)
    for h in range(1,9):
        y+= (1/h**1.3)*np.sin(2*np.pi*f*h*t*(1+0.0004*h*h))*np.exp(-t*(2.2+h*1.1/bright))
    y*=np.minimum(1,t/0.004)
    return y*amp

def bell(f, dur, amp):
    n=int(dur*SR); t=np.arange(n)/SR; y=np.zeros(n)
    for r,a,dk in ((1,1,1.2),(2.76,.5,2.2),(5.4,.25,3.5),(8.93,.12,5)):
        y+=a*np.sin(2*np.pi*f*r*t)*np.exp(-t*dk)
    return y*np.minimum(1,t/0.002)*amp

def kick(amp):
    n=int(.45*SR); t=np.arange(n)/SR; f=48+90*np.exp(-t*28)
    ph=2*np.pi*np.cumsum(f)/SR; return np.sin(ph)*np.exp(-t*7)*amp
def hat(amp):
    n=int(.08*SR); x=rng.standard_normal(n); return hp(x,7000)*np.exp(-np.arange(n)/SR*55)*amp
def whoosh(dur, amp, rise=True):
    n=int(dur*SR); x=rng.standard_normal(n); t=np.arange(n)/SR; out=np.zeros(n)
    seg=2048
    for i in range(0,n,seg):
        p=i/n; c=300+ (6000 if rise else 6000*(1-p))*(p if rise else 1)
        lo=max(80,c*0.5); hi=min(SR/2-100,c*1.6)
        out[i:i+seg]=bp(x[i:i+seg+4096],lo,hi)[:len(out[i:i+seg])]
    e=np.sin(np.pi*np.clip(t/dur,0,1))**2
    if rise: e*= (t/dur)**1.5*2
    return out*e*amp
def impact(amp):
    n=int(2.2*SR); t=np.arange(n)/SR; f=55+40*np.exp(-t*6)
    y=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*1.8)
    y+=lp(rng.standard_normal(n),900)*np.exp(-t*9)*0.5
    return y*amp

def reverb(x, sec=2.6, mix=.28):
    n=int(sec*SR); t=np.arange(n)/SR
    irL=rng.standard_normal(n)*np.exp(-t*3.2/sec*2); irR=rng.standard_normal(n)*np.exp(-t*3.2/sec*2)
    irL=lp(irL,6000); irR=lp(irR,6000); irL/=np.sqrt((irL**2).sum()); irR/=np.sqrt((irR**2).sum())
    wl=fftconvolve(x[:,0],irL)[:len(x)]; wr=fftconvolve(x[:,1],irR)[:len(x)]
    return np.stack([x[:,0]*(1-mix)+wl*mix*3, x[:,1]*(1-mix)+wr*mix*3],1)

def add(buf, sig, at, pan=0.0):
    i=int(at*SR); j=min(len(buf), i+len(sig))
    if j<=i: return
    l=np.cos((pan+1)*np.pi/4); r=np.sin((pan+1)*np.pi/4)
    buf[i:j,0]+=sig[:j-i]*l; buf[i:j,1]+=sig[:j-i]*r

def render(cfg, out):
    D=cfg['dur']; N=int(D*SR); dry=np.zeros((N,2)); fx=np.zeros((N,2))
    bpm=cfg['bpm']; beat=60/bpm; bar=4*beat
    chords=cfg['chords']  # list of [root, [notes...]] per bar group
    bars_per=cfg.get('bars_per_chord',2)
    start=cfg.get('music_start',0.0); end=cfg.get('music_end',D)
    t=start; ci=0
    style=cfg.get('style','piano')
    while t<end:
        root, notes = chords[ci%len(chords)]; L=bars_per*bar
        for nn in notes: add(dry, pad_note(hz(nn), L+1.2, .055), t, pan=rng.uniform(-.4,.4))
        add(dry, pad_note(hz(root)/2, L+1.0, .10), t)  # bass pad
        # arpeggio
        seq = notes + notes[::-1][1:-1]
        steps=int(L/(beat/2))
        for k in range(steps):
            tt=t+k*beat/2
            if tt>=end-0.2: break
            if cfg.get('intro_sparse') and tt< cfg['intro_sparse'] and k%2: continue
            f=hz(seq[k%len(seq)])*2
            add(dry, pluck(f, 1.6, .07 if style=='piano' else .055, 1.2 if style=='piano' else .7), tt, pan=(-.35 if k%2 else .35))
        if style=='pulse' and tt>cfg.get('beat_in',0):
            for k in range(bars_per*4):
                tb=t+k*beat
                if tb<cfg.get('beat_in',0) or tb>=cfg.get('beat_out',end): continue
                add(dry, kick(.42), tb); add(dry, hat(.05), tb+beat/2, pan=.2)
                if k%2: add(dry, hat(.035), tb+beat*0.75, pan=-.2)
        t+=L; ci+=1
    for c in cfg.get('cues',[]):
        k=c['type']; at=c['t']
        if k=='whoosh': s=whoosh(c.get('dur',1.0), c.get('amp',.10), c.get('rise',True)); add(fx, s, at-(c.get('dur',1.0) if c.get('rise',True) else 0))
        elif k=='impact': add(fx, impact(c.get('amp',.35)), at)
        elif k=='bell': add(fx, bell(hz(c.get('note','D6')), 4, c.get('amp',.12)), at, pan=c.get('pan',0))
        elif k=='tick': add(fx, bell(hz(c.get('note','A6')), 1.2, c.get('amp',.05)), at, pan=c.get('pan',0))
    mix=reverb(dry, 2.8, .32)+reverb(fx,2.0,.22)
    tt=np.arange(N)/SR
    fade=np.minimum(1, tt/cfg.get('fade_in',1.5))*np.clip((D-tt)/cfg.get('fade_out',2.0),0,1)
    mix*=fade[:,None]
    mix=np.tanh(mix*1.4)/1.4
    mix/=np.abs(mix).max()+1e-9; mix*=.89
    import wave
    w=wave.open(out,'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix*32767).astype('<i2').tobytes()); w.close()

if __name__=='__main__':
    render(json.load(open(sys.argv[1])), sys.argv[2])
