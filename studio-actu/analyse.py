#!/usr/bin/env python3
"""Analyste : stats/export.json (liste des documents `videos` de la régie Studio KORVEX, tels que renvoyés par ArtifactData list)
→ stats/historique.csv + stats/APPRENTISSAGES.md + stats/recommandation.json (volume du jour, créneaux, offres, accroches)."""
import json, os, csv, collections, statistics as st, datetime, sys
H = os.path.dirname(os.path.abspath(__file__)); S = os.path.join(H, 'stats'); os.makedirs(S, exist_ok=True)
src = os.path.join(S, 'export.json')
raw = json.load(open(src)) if os.path.exists(src) else []
import glob  # export via ArtifactData list … out_dir=stats/export → stats/export/videos/<id>.json
for f in glob.glob(os.path.join(S, 'export', '**', '*.json'), recursive=True):
    try:
        x = json.load(open(f)); x = x.get('data', x) if isinstance(x, dict) else x
        if isinstance(x, dict): x.setdefault('_id', os.path.basename(f)[:-5]); raw.append(x)
    except Exception: pass
if isinstance(raw, dict): raw = raw.get('documents') or raw.get('docs') or raw.get('items') or []
docs = [d.get('data', d) if isinstance(d, dict) else {} for d in raw]
today = datetime.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else datetime.date.today()
rows = []; pub_ratio = collections.defaultdict(lambda: [0, 0])
for d in docs:
    date = d.get('date', '')
    for r in d.get('reseaux', []):
        k = r.get('nom'); p = bool((d.get('publie') or {}).get(k)); s = (d.get('stats') or {}).get(k) or {}
        pub_ratio[date][1] += 1; pub_ratio[date][0] += p
        v = int(s.get('vues') or 0)
        if not p or not v: continue
        eng = int(s.get('likes') or 0) + 2 * int(s.get('commentaires') or 0) + 3 * int(s.get('partages') or 0) + 3 * int(s.get('enregistrements') or 0)
        rows.append({'date': date, 'id': d.get('_id', d.get('titre', '')), 'heure': r.get('heure') or d.get('heure', ''), 'reseau': k,
                     'offre': (d.get('offre') or '?').split('+')[0], 'format': d.get('format', ''), 'hook_type': d.get('hook_type', ''),
                     'metier': d.get('metier', ''), 'vues': v, 'score': round(eng / v * 100, 2)})
cols = ['date', 'id', 'heure', 'reseau', 'offre', 'format', 'hook_type', 'metier', 'vues', 'score']
with open(os.path.join(S, 'historique.csv'), 'w', newline='') as fh:
    w = csv.DictWriter(fh, cols); w.writeheader(); w.writerows(rows)

def fen(a, b):  # jours [today-a, today-b[
    return [r for r in rows if r['date'] and a >= (today - datetime.date.fromisoformat(r['date'])).days > b]
# --- volume recommandé (ORCHESTRE.md)
d7 = [d for d in pub_ratio if d and 0 < (today - datetime.date.fromisoformat(d)).days <= 7]
pub, tot = sum(pub_ratio[d][0] for d in d7), sum(pub_ratio[d][1] for d in d7)
ratio = pub / tot if tot else None
r7, r14 = fen(7, 0), fen(14, 7)
m7 = st.median([r['vues'] for r in r7]) if r7 else None; m14 = st.median([r['vues'] for r in r14]) if r14 else None
volume = 5; raisons = []
if ratio is not None and ratio >= .8:
    volume += 1; raisons.append(f'publication {ratio:.0%} ≥ 80 %')
    if m14 is None or (m7 or 0) >= m14: volume += 1; raisons.append('vues stables ou en hausse')
else:
    raisons.append('publication < 80 % (ou inconnue) : rester à 5' if ratio is not None else 'pas encore de publication saisie : 5')
L = ['# Apprentissages (généré par analyse.py — ne pas éditer)', '',
     f'Volume recommandé : **{volume}** vidéos (+1 possible si ≥ 2 actus fortes < 24 h, max 8) — ' + ' ; '.join(raisons) + '.',
     f'Taux de publication 7 j : {ratio:.0%}' if ratio is not None else 'Taux de publication 7 j : inconnu.',
     f'Vues médianes 7 j : {m7}, 7 j précédents : {m14}.' if m7 is not None else 'Vues : pas encore de données.', '']
reco = {'volume': volume, 'raisons': raisons}
if len(rows) < 8:
    L.append(f'{len(rows)} publications mesurées : trop peu pour conclure. Continuer à varier offres, formats, accroches, métiers et créneaux.')
else:
    L.append(f'{len(rows)} publications mesurées. Score = engagement pondéré / vues ×100.')
    for dim in ('offre', 'hook_type', 'format', 'reseau', 'heure', 'metier'):
        g = collections.defaultdict(list)
        for r in rows: g[r[dim] or '?'].append(r)
        tab = sorted(((k, len(v), st.median(x['vues'] for x in v), st.mean(x['score'] for x in v)) for k, v in g.items()), key=lambda t: -t[2] * (1 + t[3] / 10))
        reco['meilleur_' + dim] = tab[0][0]
        L += ['', f'## Par {dim}', '| valeur | n | vues médianes | score |', '|---|---|---|---|'] + [f'| {k} | {n} | {int(vm)} | {sc:.2f} |' for k, n, vm, sc in tab]
    top = sorted(rows, key=lambda r: -r['vues'])[:5]; bas = sorted(rows, key=lambda r: r['vues'])[:5]
    L += ['', '## Top 5 (imiter l\'accroche et le format)'] + [f"- {r['date']} {r['id']} ({r['reseau']} {r['heure']}) : {r['vues']} vues, score {r['score']}" for r in top]
    L += ['', '## Flop 5 (ne pas refaire tel quel)'] + [f"- {r['date']} {r['id']} ({r['reseau']} {r['heure']}) : {r['vues']} vues, score {r['score']}" for r in bas]
open(os.path.join(S, 'APPRENTISSAGES.md'), 'w').write('\n'.join(L) + '\n')
json.dump(reco, open(os.path.join(S, 'recommandation.json'), 'w'), ensure_ascii=False, indent=1)
print('\n'.join(L[:5]))
