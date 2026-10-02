# Tâche « Orchestre » — produire le lot de vidéos de J (la veille au soir)

Lancée chaque jour à 20:25 (heure de Paris) par la tâche planifiée « KORVEX — Orchestre vidéos ». Elle tourne dans le cloud, sans le Mac.
J = demain. Si la tâche est lancée avant 12:00, J = aujourd'hui (rattrapage).
Régie : https://claude.ai/artifact/CUgQUZ6Fmv9A3ft2ULHcWz (collections `videos` et `orchestre`).
La diffusion (programmation sur les réseaux et relevé des stats) est une AUTRE tâche, sur le Mac : `taches/diffusion.md`. Ici, on produit et on dépose dans la régie.

Règle d'or : la tâche ne se termine jamais sans avoir écrit son état dans la régie (`orchestre/J`).
- Dès le départ : `{"date": J, "statut": "en cours"}`.
- À la fin : `"pret"` ou `"erreur"`, avec le champ `erreur` (étape et cause).
- Si une étape casse : corrige-la si c'est rapide (≤ 2 essais), sinon écris l'erreur, pousse ce qui existe et termine.

## 0. Installation (≈ 1 min)
```bash
git clone -q https://github.com/ckoch19-a11y/factory-assets fa && cd fa/studio-actu && bash installer.sh
```
ArtifactData `query` sur `videos` :
- filtre `where [["date", ">=", J-14]]`, `limit` 300 ;
- `out_dir` = `$PWD/stats/export` (c'est le dossier que lit l'analyste).

## 1. Analyste et Veilleur, en parallèle (deux sous-agents avec l'outil Agent, lancés dans le même message)
- **Analyste** : lance `python3 analyse.py J`, lis `stats/APPRENTISSAGES.md` et `stats/recommandation.json`. Rends 8 lignes :
  - ce qui marche, par offre, accroche, format, métier, réseau et heure ;
  - ce qui échoue ;
  - le volume recommandé.
- **Veilleur** : avec WebSearch, trouve 8 à 10 faits datés de moins de 48 h, utiles aux dirigeants de TPE/PME.
  - Thèmes : IA et agents, recherche par IA, facture électronique 2026-2027, impayés et trésorerie, visibilité locale, cybersécurité.
  - Pour chaque fait : le chiffre, la source, la date et l'URL.
  - Ajoute un problème concret par métier ciblé.
  - Aucun chiffre sans source vérifiable.

## 2. Décisions du chef d'orchestre (toi) — `ORCHESTRE.md`
- **Volume** : celui de `recommandation.json`, +1 si le Veilleur rapporte au moins 2 faits forts de moins de 24 h. Minimum 5, maximum 8.
- **Mix d'offres** : A ≈ 35 %, V 30 %, B 25 %, L 10 %. Au moins 3 offres différentes.
- **Créneaux, réseaux et hashtags** : selon les tableaux d'`ORCHESTRE.md`. Le week-end, pas de LinkedIn.
- **Métiers** : en rotation (`LIGNE-EDITORIALE.md` §2).
- Note 3 à 5 décisions et une leçon : elles serviront à `orchestre.json`.

## 3. Scénariste et directeur artistique (toi)
- Écris `jours/J.json` en suivant `LIGNE-EDITORIALE.md`, notamment le §7 (champs obligatoires), avec `exemples/demo-objets.json` comme modèle.
- Pour chaque vidéo :
  - écris 2 accroches candidates et garde la meilleure : un chiffre ou une perte concrète, plus le métier, en 9 mots maximum à l'écran ;
  - prévois au moins 2 objets ;
  - choisis le thème et le fond, en les variant d'une vidéo à l'autre.
- Règles de voix pour Vivienne : les nombres en chiffres, jamais les sigles PME ou TPE prononcés.

## 4. Contrôleur (un sous-agent neuf, qui n'a pas vu l'écriture)
- Il relit `jours/J.json` en le confrontant à `LIGNE-EDITORIALE.md` et aux sources du Veilleur. Il vérifie :
  - aucun chiffre sans source ;
  - aucun nom de client ou d'entreprise réelle inventé ;
  - ni prix ni gain promis ;
  - les sigles et la longueur des textes.
- Il renvoie une liste de corrections. Applique-les.

## 5. Rendu (≈ 2 min par vidéo)
```bash
KX_WORKERS=$(nproc) ./lancer.sh J
```
- Sont produits :
  - les vidéos `sorties/J/<J>-<id>.mp4` ;
  - leurs copies de diffusion `.pub.mp4` (≤ 9,3 Mo) ;
  - les couvertures `.jpg` ;
  - les légendes par réseau ;
  - `plan.json` ;
  - la planche de contrôle `controle.png`.
- Regarde `sorties/J/controle.png` avec Read. Si une vidéo est cassée (texte qui déborde, objet qui chevauche, écran vide), corrige son JSON et relance.

## 6. Dépôt dans la régie
1. Envoie les fichiers dans les assets de la régie : Artifact `publish`, `asset: true`, `url` = la régie, `file_paths` = tous les `<J>-<id>.pub.mp4` et `<J>-<id>.jpg` (25 fichiers maximum par appel).
2. Écris `sorties/J/urls.json` : `{"<J>-<id>.mp4": "<url du .pub.mp4>", "<J>-<id>.jpg": "<url du .jpg>"}`. La clé reste en `.mp4`, mais l'URL est celle du `.pub.mp4`.
3. Écris `sorties/J/orchestre.json` : `{"date", "volume", "resume", "decisions": [...], "lecon"}`.
4. Lance `python3 regie.py sorties/J sorties/J/urls.json sorties/J/orchestre.json`, puis applique les écritures qu'il affiche (aussi dans `sorties/J/regie/batch.json`) avec ArtifactData `batch`.
5. Mets à jour `orchestre/J` : `"statut": "pret"`.

## 7. Git et message
```bash
git add jours/ stats/ && git commit -m "jour J : N vidéos" && git push
```
Message final de 5 lignes maximum : volume et mix, les 2 meilleures accroches, la leçon de l'analyste, le statut.
