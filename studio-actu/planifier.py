#!/usr/bin/env python3
"""Planificateur : jour JSON + vidéos rendues → sorties/<date>/plan.json (documents prêts pour la régie Studio KORVEX).
python3 planifier.py jours/<date>.json sorties/<date>"""
import json, os, sys, datetime
jour_p, out = sys.argv[1], sys.argv[2]
jour = json.load(open(jour_p)); date = jour['date']
we = datetime.date.fromisoformat(date).weekday() >= 5
# créneau → réseaux autorisés (ORCHESTRE.md) ; LinkedIn : un seul par jour, en semaine
AUTORISE = {'07:45': {'linkedin', 'tiktok'}, '10:30': {'tiktok', 'instagram', 'facebook'}, '12:30': {'instagram', 'facebook', 'tiktok', 'linkedin'},
            '15:00': {'tiktok', 'facebook'}, '17:30': {'facebook', 'tiktok'}, '19:30': {'instagram', 'facebook', 'tiktok'}, '21:00': {'facebook', 'tiktok'}}
PLAF = {'tiktok': 8, 'instagram': 2, 'facebook': 3, 'linkedin': 0 if we else 1}
compte = {k: 0 for k in PLAF}; docs = []
for v in sorted(jour['videos'], key=lambda x: x.get('creneau', '')):
    base = os.path.join(out, f"{date}-{v['id']}")
    if not os.path.exists(base + '.mp4'): continue
    res = []
    for r in v.get('reseaux') or ['tiktok']:
        ok = AUTORISE.get(v.get('creneau'), {r})
        if r not in ok or compte.get(r, 0) >= PLAF.get(r, 9): continue
        txtp = base + f'.{r}.txt'
        texte = open(txtp).read().strip() if os.path.exists(txtp) else open(base + '.txt').read().strip()
        res.append({'nom': r, 'heure': v.get('creneau', ''), 'texte': texte}); compte[r] = compte.get(r, 0) + 1
    if not res:
        res = [{'nom': 'tiktok', 'heure': v.get('creneau', ''), 'texte': open(base + '.txt').read().strip()}]
    types = [s.get('type') for s in v.get('scenes', [])]
    docs.append({'_id': f"{date}-{v['id']}", 'date': date, 'heure': v.get('creneau', ''), 'titre': v.get('titre', ''), 'offre': v.get('offre', ''),
                 'metier': v.get('metier', ''), 'hook_type': v.get('hook_type', ''), 'format': ' · '.join(dict.fromkeys(t for t in types if t)),
                 'source': v.get('source', ''), 'reseaux': res, 'publie': {}, 'stats': {},
                 'fichier_video': base + '.mp4', 'fichier_cover': base + '.jpg'})
json.dump(docs, open(os.path.join(out, 'plan.json'), 'w'), ensure_ascii=False, indent=1)
print(f"{len(docs)} vidéos planifiées ·", ', '.join(f'{k} {n}' for k, n in compte.items() if n))
