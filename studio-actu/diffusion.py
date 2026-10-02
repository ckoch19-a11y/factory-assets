#!/usr/bin/env python3
"""Diffuseur : prépare le travail de l'agent Chrome (taches/diffusion.md) et convertit ses relevés en écritures pour la régie.

python3 diffusion.py todo <export_dir> <date> [HH:MM]
    <export_dir> : dossier où ArtifactData (query/list avec out_dir) a écrit les documents « videos »
    → diffusion/<date>-todo.json = {"programmer": [...], "relever": [...]}
      programmer : une ligne par (vidéo, réseau) pas encore programmée, triée par heure ;
                   « trop_tard » si le créneau tombe à moins de 25 min de HH:MM (heure de Paris)
      relever    : publications des 7 derniers jours dont il faut relever les stats
python3 diffusion.py ecritures <export_dir> <faits.json> <versions.json>
    faits.json    : [{"doc_id"?, "texte"?, "reseau", "statut"?: "programme"|"publie"|"echec", "detail"?,
                      "vues"?, "likes"?, "commentaires"?, "partages"?, "enregistrements"?}]
                    sans doc_id, la ligne est rattachée à sa vidéo par le début de sa légende
    versions.json : {"<doc_id>": <version>} recopiées du résultat ArtifactData
    → diffusion/maj/<doc_id>.json et, sur la sortie standard, le tableau `writes` prêt pour ArtifactData batch
"""
import datetime as dt, glob, json, os, re, sys, unicodedata
from zoneinfo import ZoneInfo

H = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(H, 'diffusion')
PARIS = ZoneInfo('Europe/Paris')
STUDIO = '/mnt/user-data/outputs/studio'
PLATEFORME = {'tiktok': 'tiktok', 'instagram': 'meta', 'facebook': 'meta', 'linkedin': 'linkedin'}
CHIFFRES = ('vues', 'likes', 'commentaires', 'partages', 'enregistrements')
RANG = {'echec': 0, 'programme': 1, 'publie': 2}


def charger(export_dir):
    docs = {}
    for f in glob.glob(os.path.join(export_dir, '**', '*.json'), recursive=True):
        try:
            x = json.load(open(f))
        except Exception:
            continue
        if isinstance(x, dict):
            x = x.get('data', x) if 'reseaux' not in x else x
            if 'reseaux' in x and 'date' in x:
                docs[os.path.basename(f)[:-5]] = x
    return docs


def norm(t):
    t = unicodedata.normalize('NFKD', t or '').encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', ' ', t).strip()


def asset_id(url):
    m = re.search(r'[0-9a-f]{32}', url or '')
    return m.group(0) if m else None


def todo(export_dir, date, maintenant=None):
    docs = charger(export_dir)
    jour = dt.date.fromisoformat(date)
    seuil = None
    if maintenant:
        h, m = map(int, maintenant.split(':'))
        seuil = dt.datetime(jour.year, jour.month, jour.day, h, m, tzinfo=PARIS) + dt.timedelta(minutes=25)
    prog, rel = [], []
    for did, d in docs.items():
        diff = d.get('diffusion') or {}
        if d.get('date') == date:
            for r in d.get('reseaux', []):
                if (diff.get(r['nom']) or {}).get('statut') in ('programme', 'publie'):
                    continue
                heure = r.get('heure') or d.get('heure') or '12:30'
                hh, mm = map(int, heure.split(':'))
                quand = dt.datetime(jour.year, jour.month, jour.day, hh, mm, tzinfo=PARIS)
                prog.append({'doc_id': did, 'reseau': r['nom'], 'plateforme': PLATEFORME.get(r['nom'], r['nom']),
                             'date': date, 'heure': heure, 'quand': quand.isoformat(), 'titre': d.get('titre', ''),
                             'texte': r.get('texte', ''), 'asset_id': asset_id(d.get('video_url')),
                             'fichier': f'{STUDIO}/{did}.mp4', 'trop_tard': bool(seuil and quand < seuil)})
        try:
            age = (jour - dt.date.fromisoformat(d.get('date', ''))).days
        except ValueError:
            continue
        if 0 <= age <= 7:
            for nom, st in diff.items():
                if (st or {}).get('statut') in ('programme', 'publie'):
                    txt = next((r.get('texte', '') for r in d.get('reseaux', []) if r['nom'] == nom), '')
                    rel.append({'doc_id': did, 'reseau': nom, 'date': d.get('date'), 'heure': (st or {}).get('heure') or d.get('heure'),
                                'debut_legende': txt[:80], 'stats_actuelles': (d.get('stats') or {}).get(nom, {})})
    prog.sort(key=lambda x: (x['quand'], x['plateforme'], x['reseau']))
    rel.sort(key=lambda x: (x['date'], x['heure'] or ''))
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, f'{date}-todo.json')
    json.dump({'programmer': prog, 'relever': rel}, open(p, 'w'), ensure_ascii=False, indent=1)
    print(f'{len(prog)} programmations à faire, {len(rel)} relevés de stats → {p}')
    for x in prog:
        print(f"  {x['heure']} {x['reseau']:<9} {x['doc_id']}{'  ⚠ trop tard' if x['trop_tard'] else ''}")


def rattacher(f, docs):
    if f.get('doc_id') in docs:
        return f['doc_id']
    cible = norm(f.get('texte'))[:60]
    if len(cible) < 20:
        return None
    meilleur, score = None, 0
    for did, d in docs.items():
        for r in d.get('reseaux', []):
            if f.get('reseau') and r['nom'] != f['reseau']:
                continue
            t = norm(r.get('texte'))
            n = len(os.path.commonprefix([cible, t[:60]]))
            if n > score:
                meilleur, score = did, n
    return meilleur if score >= 20 else None


def ecritures(export_dir, faits_p, versions_p):
    docs = charger(export_dir)
    faits = json.load(open(faits_p))
    versions = json.load(open(versions_p)) if os.path.exists(versions_p) else {}
    maint = dt.datetime.now(PARIS).isoformat(timespec='minutes')
    touches, orphelins = {}, []
    for f in faits:
        did = rattacher(f, docs)
        if not did:
            orphelins.append(f)
            continue
        d = touches.setdefault(did, {k: dict(docs[did].get(k) or {}) for k in ('diffusion', 'publie', 'stats')})
        nom = f['reseau']
        st = f.get('statut') or ('publie' if any(k in f for k in CHIFFRES) else None)
        if st:
            avant = (d['diffusion'].get(nom) or {}).get('statut')
            if avant is None or RANG.get(st, 0) >= RANG.get(avant, 0) or avant == 'echec':
                d['diffusion'][nom] = {k: v for k, v in {'statut': st, 'le': maint, 'detail': f.get('detail'), 'heure': f.get('heure')}.items() if v}
        if any(k in f for k in CHIFFRES):
            d['publie'][nom] = True
            # un chiffre absent de la page reste inconnu (pas 0) : on garde l'ancienne valeur
            d['stats'][nom] = {**(d['stats'].get(nom) or {}), **{k: int(f[k]) for k in CHIFFRES if f.get(k) is not None}}
    os.makedirs(os.path.join(OUT, 'maj'), exist_ok=True)
    writes = []
    for did, data in touches.items():
        p = os.path.join(OUT, 'maj', f'{did}.json')
        json.dump(data, open(p, 'w'), ensure_ascii=False, indent=1)
        w = {'op': 'update', 'collection': 'videos', 'doc_id': did, 'file_path': p}
        if did in versions:
            w['if_version'] = versions[did]
        else:
            print(f'⚠ version inconnue pour {did} : relire le document avant d\'écrire', file=sys.stderr)
        writes.append(w)
    print(json.dumps(writes, ensure_ascii=False))
    if orphelins:
        print(f'⚠ {len(orphelins)} ligne(s) non rattachée(s) : {json.dumps(orphelins, ensure_ascii=False)[:600]}', file=sys.stderr)


if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == 'todo':
        todo(a[1], a[2], a[3] if len(a) > 3 else None)
    elif a and a[0] == 'ecritures':
        ecritures(a[1], a[2], a[3])
    else:
        print(__doc__)
