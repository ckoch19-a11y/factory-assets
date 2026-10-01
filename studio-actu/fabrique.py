#!/usr/bin/env python3
"""Usine vidéo KORVEX « L'actu des TPE & PME ».
python3 fabrique.py jour.json [--out sorties] [--only ID] [--workers 3]
Une vidéo verticale 1080x1920 30 i/s par entrée de jour.json : voix off (Piper, voix fixe),
sous-titres karaoké, musique originale synthétisée, sortie normalisée -14 LUFS."""
import json, os, sys, subprocess, wave, argparse, urllib.request, shutil
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import musique, re, difflib
HERE_ = os.path.dirname(os.path.abspath(__file__))
CB_PY = os.environ.get('KX_CB_PY', os.path.expanduser('~/.korvex-cb/bin/python'))
REF = os.path.join(HERE_, 'voix-ref.wav')
_cb = None; _asr = None

def oral(t):
    """Texte lu par la voix : sigles prononçables (« IA » → « i-a »)."""
    t = re.sub(r"\bI\.?\s?A\.?(?=[\s,;:!?)]|$)", "i-a", t)
    return t.replace('%', ' pour cent').replace('€', ' euros')

def norm(t):
    t = t.lower().replace('i-a', 'ia').replace('iha', 'ia').replace('i a ', 'ia ').replace('%', ' pour cent')
    t = re.sub(r"[^a-z0-9àâçéèêëîïôûùüÿœ ]", " ", t.replace("'", " "))
    return t.split()

def asr(path):
    global _asr
    if _asr is None:
        from faster_whisper import WhisperModel
        _asr = WhisperModel(os.environ.get('KX_ASR', 'small'), device='cpu', compute_type='int8')
    segs, _ = _asr.transcribe(path, language='fr'); return ' '.join(x.text for x in segs)

def _lire_json():
    while True:
        l = _cb.stdout.readline()
        if not l: raise RuntimeError('moteur voix Chatterbox arrêté')
        try: return json.loads(l)
        except ValueError: continue

def cb(texte, out, seed, _retry=False):
    global _cb
    if _cb is None:
        _cb = subprocess.Popen([CB_PY, os.path.join(HERE_, 'voix_cb.py'), REF], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=open(os.path.join(os.environ.get('TMPDIR','/tmp'),'korvex-voix.err'),'a'), text=True)
        while not _lire_json().get('pret'): pass
    try:
        _cb.stdin.write(json.dumps({"texte": texte, "out": out, "seed": seed}) + "\n"); _cb.stdin.flush()
        while True:
            if _lire_json().get('out') == out: return
    except (BrokenPipeError, RuntimeError):
        if _retry: raise
        print('  moteur voix redémarré', flush=True); _cb = None; return cb(texte, out, seed, _retry=True)

VOIX = os.environ.get('KX_VOIX', 'fr/fr_FR/tom/medium/fr_FR-tom-medium')
VITESSE = float(os.environ.get('KX_VITESSE', '0.9'))   # < 1 = plus rapide
CACHE = os.path.expanduser('~/.cache/korvex-voix')
SR = 48000
CTA_VOIX = os.environ.get("KX_CTA", "KORVEX crée des agents IA sur mesure pour les petites et moyennes entreprises. Suivez-nous.")

CTA_OFFRES = {  # offre -> (texte écran, voix de fin)
    'A': ('<span class="acc" style="color:var(--acc)">Agents IA sur mesure</span><br>pour les PME.', "KORVEX crée des agents IA sur mesure pour les petites entreprises. Suivez-nous."),
    'V': ('Des sites que<br><span class="acc" style="color:var(--acc)">l’IA recommande.</span>', "KORVEX crée des sites que Google et l'IA recommandent. Suivez-nous."),
    'B': ('<span class="acc" style="color:var(--acc)">Devis, factures, relances</span><br>au même endroit.', "KORVEX crée des back-offices sur mesure, prêts pour la facture électronique. Suivez-nous."),
    'L': ('Le premier appelé<br><span class="acc" style="color:var(--acc)">dans votre ville.</span>', "KORVEX vous rend visible dans votre ville, sur Google comme sur l'IA. Suivez-nous."),
}
def cta_de(v):
    o = (v.get('offre') or 'A').split('+')[0].strip().upper()
    return CTA_OFFRES.get(o, CTA_OFFRES['A'])

def sh(*a): subprocess.run(a, check=True)

def modele():
    os.makedirs(CACHE, exist_ok=True)
    base = os.path.join(CACHE, os.path.basename(VOIX))
    for ext in ('.onnx', '.onnx.json'):
        if not os.path.exists(base + ext):
            urllib.request.urlretrieve(f'https://huggingface.co/rhasspy/piper-voices/resolve/main/{VOIX}{ext}', base + ext)
    return base + '.onnx'

def lire(path):
    sh('ffmpeg', '-v', 'error', '-y', '-i', path, '-ac', '1', '-ar', str(SR), '-f', 'f32le', path + '.raw')
    x = np.fromfile(path + '.raw', dtype='<f4'); os.remove(path + '.raw'); return x

MOTEUR = os.environ.get('KX_MOTEUR', 'edge')          # edge (défaut) | cb | piper
VOIX_EDGE = os.environ.get('KX_VOIX_EDGE', 'fr-FR-VivienneMultilingualNeural')
EDGE_RATE, EDGE_PITCH = os.environ.get('KX_RATE', '+4%'), os.environ.get('KX_PITCH', '-2Hz')

def _edge_ssl():
    import ssl, edge_tts.communicate as c
    ca = '/root/.ccr/ca-bundle.crt'
    if os.path.exists(ca): c._SSL_CTX = ssl.create_default_context(cafile=ca)

def voix_edge(texte, out):
    """Voix neuronale lue d'un seul trait + horodatage exact de chaque mot (sous-titres karaoké au mot près)."""
    import asyncio, edge_tts
    _edge_ssl()
    mp3 = out + '.mp3'; mots = []
    async def go():
        cm = edge_tts.Communicate(texte, VOIX_EDGE, rate=EDGE_RATE, pitch=EDGE_PITCH, boundary='WordBoundary',
                                  proxy=os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy'))
        with open(mp3, 'wb') as f:
            async for ch in cm.stream():
                if ch['type'] == 'audio': f.write(ch['data'])
                elif ch['type'] == 'WordBoundary': mots.append([ch['text'], ch['offset'] / 1e7, (ch['offset'] + ch['duration']) / 1e7])
    for essai in range(3):
        try: mots.clear(); asyncio.run(go()); break
        except Exception as e:
            if essai == 2: raise
            __import__('time').sleep(3)
    a0 = max(0.0, (mots[0][1] if mots else 0) - 0.04); a1 = (mots[-1][2] + 0.14) if mots else None
    sh('ffmpeg', '-v', 'error', '-y', '-i', mp3, '-ss', f'{a0:.3f}', *(['-to', f'{a1:.3f}'] if a1 else []), '-af',
       'highpass=f=70,equalizer=f=3500:t=q:w=1.4:g=1.5,acompressor=threshold=-22dB:ratio=2:attack=10:release=150:makeup=2', '-ar', str(SR), out)
    os.remove(mp3)
    json.dump([[w, round(a - a0, 3), round(b - a0, 3)] for w, a, b in mots], open(out + '.mots.json', 'w'), ensure_ascii=False)
    open(out + '.txt', 'w').write(texte); return lire(out)

def aligne(texte, mots):
    """Rattache les mots horodatés du moteur aux mots du texte (ponctuation conservée pour les sous-titres)."""
    nz = lambda w: re.sub(r'[^0-9a-zàâçéèêëîïôûùüÿœæ]', '', w.lower())
    toks = texte.split(); res = []; j = 0
    for tk in toks:
        cible = nz(tk)
        if not cible:
            if res: res[-1]['w'] += ' ' + tk
            continue
        if j >= len(mots): return None
        a = mots[j][1]; acc = ''; b = mots[j][2]
        while j < len(mots) and len(acc) < len(cible):
            acc += nz(mots[j][0]); b = mots[j][2]; j += 1
        res.append({'w': tk, 'a': a, 'b': b})
    return res

def voix(texte, out, mdl):
    if os.path.exists(out) and os.path.exists(out + '.txt') and open(out + '.txt').read() == texte:
        return lire(out)   # cache : même texte déjà généré
    raw = out + '.brut.wav'
    if MOTEUR == 'edge':
        return voix_edge(texte, out)
    if os.path.exists(CB_PY) and MOTEUR == 'cb':
        # Chatterbox + contrôle Whisper : on garde la prise la plus fidèle au texte (3 essais max)
        best = None
        for seed in (7, 11, 23):
            cb(oral(texte), raw + f'.{seed}.wav', seed)
            att, eu = norm(texte), norm(asr(raw + f'.{seed}.wav'))
            sc = difflib.SequenceMatcher(None, att, eu).ratio()
            if best is None or sc > best[0]: best = (sc, raw + f'.{seed}.wav')
            print(f'  voix seed {seed} : fidélité {sc:.2f}', flush=True)
            if sc >= 0.88: break
        if best[0] < 0.8: print(f'  ⚠ voix douteuse ({best[0]:.2f}) : {texte[:60]}', flush=True)
        os.replace(best[1], raw)
        for f in os.listdir(os.path.dirname(out)):
            if f.startswith(os.path.basename(raw) + '.'): os.remove(os.path.join(os.path.dirname(out), f))
        chain = 'atempo=1.07,highpass=f=80,equalizer=f=3200:t=q:w=1.2:g=2,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=3,'
    else:
        subprocess.run([sys.executable, '-m', 'piper', '-m', mdl, '--length-scale', str(VITESSE), '--sentence-silence', '0.12', '-f', raw],
                       input=texte.encode(), check=True, capture_output=True)
        chain = 'highpass=f=85,lowpass=f=12000,equalizer=f=200:t=q:w=1:g=-2,equalizer=f=3200:t=q:w=1.2:g=3,acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=4,aecho=0.8:0.5:28:0.12,'
    sh('ffmpeg', '-v', 'error', '-y', '-i', raw, '-af', chain +
       'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse',
       '-ar', str(SR), out)
    os.remove(raw); open(out + '.txt', 'w').write(texte); return lire(out)

def voix_seules(v, outdir, mdl):
    work = os.path.join(outdir, '_w_' + v['id']); os.makedirs(work, exist_ok=True)
    for k, sc in enumerate(v['scenes']): voix(sc['voix'], os.path.join(work, f'v{k}.wav'), mdl)
    voix(cta_de(v)[1], os.path.join(work, 'cta.wav'), mdl)

def stop_voix():
    global _cb
    if _cb: _cb.stdin.close(); _cb.wait(timeout=60); _cb = None

def fabriquer(v, jour, outdir, mdl, workers):
    vid = v['id']; work = os.path.join(outdir, '_w_' + vid); os.makedirs(work, exist_ok=True)
    t = 0.35; scenes = []; pistes = []
    for k, sc in enumerate(v['scenes']):
        wf = os.path.join(work, f'v{k}.wav'); x = voix(sc['voix'], wf, mdl)
        d = len(x) / SR
        serre = MOTEUR == 'edge'
        v0 = t + ((0.35 if serre else 0.45) if k == 0 else (0.12 if serre else 0.25)); v1 = v0 + d
        t1 = max(v1 + (0.28 if serre else 0.4), t + (2.4 if k == 0 else 2.0))
        s = dict(sc); s.update(t0=round(t, 3), t1=round(t1, 3), v0=round(v0, 3), v1=round(v1, 3))
        if os.path.exists(wf + '.mots.json'):
            al = aligne(sc['voix'], json.load(open(wf + '.mots.json')))
            if al: s['mots'] = [{'w': m['w'], 'a': round(v0 + m['a'], 3), 'b': round(v0 + m['b'], 3)} for m in al]
        scenes.append(s)
        pistes.append((v0, x)); t = t1
    cta = t; xc = voix(cta_de(v)[1], os.path.join(work, 'cta.wav'), mdl); pistes.append((cta + 0.9, xc))
    duree = round(cta + max(3.4, 0.9 + len(xc) / SR + 0.7), 2)
    N = int(duree * SR); vt = np.zeros(N)
    for at, x in pistes:
        i = int(at * SR); vt[i:i + len(x)] += x[:max(0, N - i)]
    # musique originale, accordée au thème
    pulse = v.get('theme', 'papier') in ('encre', 'ardoise') or v.get('style') == 'pulse'
    progs = [[["A2", ["A3", "C4", "E4", "B4"]], ["F2", ["F3", "A3", "C4", "E4"]], ["C3", ["C4", "E4", "G4", "D5"]], ["G2", ["G3", "B3", "D4", "E4"]]],
             [["D3", ["D4", "F#4", "A4", "E5"]], ["B2", ["B3", "D4", "F#4", "A4"]], ["G2", ["G3", "B3", "D4", "F#4"]], ["A2", ["A3", "D4", "E4", "A4"]]],
             [["E2", ["E3", "G3", "B3", "F#4"]], ["C3", ["C4", "E4", "G4", "B4"]], ["G2", ["G3", "B3", "D4", "A4"]], ["D3", ["D4", "F#4", "A4", "E5"]]]]
    h = sum(map(ord, vid + jour.get('date', ''))) % 3
    cues = [{"type": "whoosh", "t": s['t0'], "dur": 0.7, "amp": 0.05} for s in scenes[1:]]
    cues += [{"type": "whoosh", "t": cta, "dur": 1.0, "amp": 0.10}, {"type": "impact", "t": cta, "amp": 0.22},
             {"type": "bell", "t": cta + 0.35, "note": "A5", "amp": 0.10}, {"type": "tick", "t": 0.5, "note": "E6", "amp": 0.04}]
    cfg = {"dur": duree, "bpm": 100 if pulse else 84, "bars_per_chord": 1, "style": "pulse" if pulse else "piano",
           "fade_in": 0.6, "fade_out": 1.6, "beat_in": scenes[0]['t1'] if pulse else 99, "beat_out": duree - 0.8,
           "chords": progs[h], "cues": cues}
    musique.rng = np.random.default_rng(h + 7)
    mw = os.path.join(work, 'musique.wav'); musique.render(cfg, mw)
    m = lire(mw); m = np.pad(m, (0, max(0, N - len(m))))[:N]
    # musique uniquement hors parole : masque voix élargi de 0,5 s, fondus de 0,3 s
    actif = np.zeros(N)
    for at, x in pistes:
        a = max(0, int((at - 0.5) * SR)); b = min(N, int((at + len(x) / SR + 0.5) * SR)); actif[a:b] = 1
    k = int(.3 * SR); g = 1 - np.convolve(actif, np.ones(k) / k, 'same').clip(0, 1)
    mix = vt * 1.0 + m * 0.30 * g
    mix = np.tanh(mix * 1.1) / 1.1
    st = np.stack([mix, mix], 1)
    aw = os.path.join(work, 'mix.wav')
    with wave.open(aw, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st / max(1e-9, np.abs(st).max()) * 0.9 * 32767).astype('<i2').tobytes())
    an = os.path.join(work, 'mix-norm.wav')
    sh('ffmpeg', '-v', 'error', '-y', '-i', aw, '-af', 'loudnorm=I=-14:TP=-1.0:LRA=9', '-ar', str(SR), an)
    FONDS = ['bandes', 'grille', 'halo', 'lignes', 'points']
    fond = v.get('fond') or FONDS[(h + sum(map(ord, vid))) % len(FONDS)]
    spec = {"fps": 30, "duree": duree, "cta_t0": cta, "fond": fond, "cta_txt": cta_de(v)[0], "theme": v.get('theme', 'papier'), "serie": v['serie'],
            "date_courte": jour.get('date_courte', ''), "source": v.get('source', ''), "scenes": scenes}
    sp = os.path.join(work, 'spec.json'); json.dump(spec, open(sp, 'w'), ensure_ascii=False)
    muet = os.path.join(work, 'muet.mp4')
    sh('node', os.path.join(HERE, 'rendu.mjs'), sp, muet, str(workers))
    final = os.path.join(outdir, f"{jour['date']}-{vid}.mp4")
    sh('ffmpeg', '-v', 'error', '-y', '-i', muet, '-i', an, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', final)
    cover = final[:-4] + '.jpg'
    sh('ffmpeg', '-v', 'error', '-y', '-ss', str(max(0.5, scenes[0]['t1'] - 0.4)), '-i', muet, '-frames:v', '1', '-q:v', '3', cover)
    leg = final[:-4] + '.txt'
    src = ('\n\nSource : ' + v['source']) if v.get('source') and 'KORVEX' not in v['source'] else ''
    open(leg, 'w').write(v.get('legende', '').strip() + src + '\n')
    for res, tags in (v.get('hashtags') or {}).items():
        if tags: open(final[:-4] + f'.{res}.txt', 'w').write(v.get('legende', '').strip() + src + '\n\n' + ' '.join(tags) + '\n')
    if not os.environ.get('KX_GARDER'): shutil.rmtree(work, ignore_errors=True)
    return {"id": vid, "reseaux": v.get('reseaux', []), "metier": v.get('metier', ''), "hook_type": v.get('hook_type', ''), "serie": v.get('serie', ''), "video": final, "cover": cover, "legende": leg, "duree": duree, "titre": v.get('titre', ''), "creneau": v.get('creneau', '')}

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('jour'); ap.add_argument('--out', default='sorties')
    ap.add_argument('--only'); ap.add_argument('--workers', type=int, default=max(2, os.cpu_count() or 2)); a = ap.parse_args()
    jour = json.load(open(a.jour)); os.makedirs(a.out, exist_ok=True); mdl = modele() if MOTEUR == 'piper' else None; res = []
    # phase 1 : toutes les voix (le modèle voix occupe ~4 Go : on le libère avant le rendu navigateur)
    for v in jour['videos']:
        if a.only and v['id'] != a.only: continue
        t0 = __import__('time').time(); voix_seules(v, a.out, mdl); stop_voix(); print(f"voix {v['id']} : {__import__('time').time()-t0:.0f} s", flush=True)
    stop_voix()
    for v in jour['videos']:
        if a.only and v['id'] != a.only: continue
        try: r = fabriquer(v, jour, a.out, mdl, a.workers); res.append(r); print('OK', r['video'], r['duree'], 's', flush=True)
        except Exception as e: print('ECHEC', v.get('id'), e, flush=True); res.append({"id": v.get('id'), "erreur": str(e)})
    json.dump(res, open(os.path.join(a.out, f"{jour['date']}-manifeste.json"), 'w'), ensure_ascii=False, indent=1)
