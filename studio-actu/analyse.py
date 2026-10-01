#!/usr/bin/env python3
"""Boucle d'apprentissage. Entrées :
  publications/<date>.json : [{video_id, date, creneau, serie, metier, hook_type, reseau, post_id}]
  stats/brut/<post_id>.json : sortie brute de `postiz analytics:post <post_id> -d 7`
Sorties : stats/historique.csv (1 ligne par post×réseau) + stats/APPRENTISSAGES.md (à lire avant d'écrire un jour)."""
import json, glob, os, csv, collections, statistics as st
H = os.path.dirname(os.path.abspath(__file__))
def metr(raw):
    out = {}
    for m in raw if isinstance(raw, list) else raw.get('data', []) if isinstance(raw, dict) else []:
        lab = (m.get('label') or m.get('name') or '').lower()
        pts = m.get('data') or m.get('values') or []
        try: v = sum(float(p.get('total', p.get('value', 0)) or 0) for p in pts) if pts and isinstance(pts[0], dict) else float(m.get('total', m.get('value', 0)) or 0)
        except Exception: v = 0
        for k, keys in {'vues': ('view', 'impression', 'vue', 'play'), 'likes': ('like', 'reaction'), 'commentaires': ('comment',),
                        'partages': ('share', 'repost', 'send'), 'enregistrements': ('save', 'bookmark'), 'portee': ('reach',)}.items():
            if any(x in lab for x in keys): out[k] = out.get(k, 0) + v
    return out
rows = []
for f in sorted(glob.glob(os.path.join(H, 'publications', '*.json'))):
    for p in json.load(open(f)):
        b = os.path.join(H, 'stats', 'brut', f"{p.get('post_id')}.json")
        if not os.path.exists(b): continue
        m = metr(json.load(open(b))); v = m.get('vues', 0) or m.get('portee', 0)
        eng = m.get('likes', 0) + 2 * m.get('commentaires', 0) + 3 * m.get('partages', 0) + 3 * m.get('enregistrements', 0)
        rows.append({**{k: p.get(k, '') for k in ('date', 'video_id', 'creneau', 'serie', 'metier', 'hook_type', 'reseau', 'post_id')},
                     **{k: int(m.get(k, 0)) for k in ('vues', 'likes', 'commentaires', 'partages', 'enregistrements')},
                     'score': round(eng / v * 100, 2) if v else 0})
os.makedirs(os.path.join(H, 'stats'), exist_ok=True)
cols = ['date', 'video_id', 'creneau', 'serie', 'metier', 'hook_type', 'reseau', 'post_id', 'vues', 'likes', 'commentaires', 'partages', 'enregistrements', 'score']
with open(os.path.join(H, 'stats', 'historique.csv'), 'w', newline='') as fh:
    w = csv.DictWriter(fh, cols); w.writeheader(); w.writerows(rows)
L = ['# Apprentissages (généré par analyse.py — ne pas éditer à la main)', '']
if len(rows) < 10:
    L.append(f'Pas assez de données ({len(rows)} posts mesurés). Continuer à varier hooks, séries et métiers.')
else:
    L.append(f'{len(rows)} posts mesurés. Score = engagement pondéré / vues ×100 (commentaires ×2, partages et enregistrements ×3).')
    for dim in ('reseau', 'serie', 'hook_type', 'metier', 'creneau'):
        g = collections.defaultdict(list)
        for r in rows: g[r[dim] or '?'].append(r)
        tab = sorted(((k, len(v), st.median(x['vues'] for x in v), st.mean(x['score'] for x in v)) for k, v in g.items()), key=lambda t: -t[2] * (1 + t[3] / 10))
        L += ['', f'## Par {dim}', '| valeur | n | vues médianes | score moyen |', '|---|---|---|---|'] + [f'| {k} | {n} | {int(vm)} | {sc:.2f} |' for k, n, vm, sc in tab]
    top = sorted(rows, key=lambda r: -r['vues'])[:5]; bas = sorted(rows, key=lambda r: r['vues'])[:5]
    L += ['', '## Top 5 (à imiter : même hook_type / angle)'] + [f"- {r['date']} {r['video_id']} ({r['reseau']}) : {r['vues']} vues, score {r['score']}" for r in top]
    L += ['', '## Flop 5 (à ne pas refaire tel quel)'] + [f"- {r['date']} {r['video_id']} ({r['reseau']}) : {r['vues']} vues, score {r['score']}" for r in bas]
open(os.path.join(H, 'stats', 'APPRENTISSAGES.md'), 'w').write('\n'.join(L) + '\n'); print('\n'.join(L[:12]))
