#!/usr/bin/env python3
"""Prépare les documents de la régie Studio KORVEX.
python3 regie.py sorties/<date> urls.json [orchestre.json]
urls.json = {"<nom de fichier>": "/_blob/<id>", ...} (résultat du téléversement des MP4 et JPG)
Écrit sorties/<date>/regie/<doc_id>.json (collection videos) et orchestre-<date>.json, plus batch.json (liste {op, collection, doc_id, file_path})."""
import json, os, sys
out, urls = sys.argv[1], json.load(open(sys.argv[2]))
plan = json.load(open(os.path.join(out, 'plan.json'))); R = os.path.join(out, 'regie'); os.makedirs(R, exist_ok=True); batch = []
for d in plan:
    doc = {k: v for k, v in d.items() if not k.startswith('_') and not k.startswith('fichier_')}
    doc['video_url'] = urls.get(os.path.basename(d['fichier_video']), ''); doc['cover_url'] = urls.get(os.path.basename(d['fichier_cover']), '')
    p = os.path.join(R, d['_id'] + '.json'); json.dump(doc, open(p, 'w'), ensure_ascii=False)
    batch.append({'op': 'set', 'collection': 'videos', 'doc_id': d['_id'], 'file_path': os.path.abspath(p)})
if len(sys.argv) > 3:
    o = json.load(open(sys.argv[3])); p = os.path.join(R, 'orchestre.json'); json.dump(o, open(p, 'w'), ensure_ascii=False)
    batch.append({'op': 'set', 'collection': 'orchestre', 'doc_id': o['date'], 'file_path': os.path.abspath(p)})
json.dump(batch, open(os.path.join(R, 'batch.json'), 'w'), indent=1); print(json.dumps(batch))
