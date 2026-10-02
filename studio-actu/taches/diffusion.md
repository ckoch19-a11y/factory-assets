# Tâche « Diffusion » — programmer les vidéos et relever les stats via le Chrome de Calvin

Lancée par la tâche planifiée « KORVEX — Diffusion vidéos (Chrome) » sur le Mac de Calvin (21:50 et 06:50, heure de Paris).
Les outils `mcp__claude-in-chrome__*` pilotent son vrai Chrome, déjà connecté à ses comptes.
Régie : https://claude.ai/artifact/CUgQUZ6Fmv9A3ft2ULHcWz — collection `videos`, documents `<date>-<id>`.
Avant d'ouvrir Chrome, lis `taches/NOTES-UI.md` : ce que les passages précédents ont appris sur chaque interface. Il remplace les tâtonnements.

## Règles absolues
1. Ne programme QUE les lignes de `diffusion/<J>-todo.json` : vidéo et légende exactes de la régie. Aucune autre action sur les comptes : pas de like, commentaire, message, abonnement, suppression, ni changement de réglage.
2. Jamais de mot de passe, de code reçu par SMS ou mail, ni de CAPTCHA. Si une page demande de se connecter ou de prouver qu'on est humain, arrête ce réseau, note `echec` avec le détail « connexion requise », puis passe au réseau suivant.
3. Programmer, ne pas publier tout de suite, sauf pour une ligne « trop_tard » (voir étape 2).
4. Voix de synthèse : sur TikTok, active toujours « Contenu généré par l'IA ». Sur Meta, coche l'étiquette IA si l'option existe.
5. Avant de programmer une vidéo, vérifie qu'elle ne l'est pas déjà : cherche le début de la légende dans la liste des publications programmées du réseau. Si elle y est, note `programme` et passe à la suivante.
6. Économie de jetons : utilise d'abord `find`, `read_page` (filtre `interactive`) et `get_page_text`. Les captures se font à `scale` 0.5, et seulement pour lever un doute.
7. Après 3 échecs sur la même action, arrête ce réseau, note `echec` avec la cause et continue. Ne déclenche jamais de boîte de dialogue du navigateur.
8. Ferme tous les onglets que tu as ouverts.

## 1. Préparation (dans le conteneur)
```bash
git clone -q https://github.com/ckoch19-a11y/factory-assets fa && cd fa/studio-actu
mkdir -p /mnt/user-data/outputs/studio export
```
- Choix de J :
  - si l'heure de Paris est ≥ 15:00, J = demain ;
  - sinon J = aujourd'hui, et MAINTENANT = l'heure actuelle.
- ArtifactData `query` sur `videos` :
  - filtre `where [["date", ">=", J-7]]`, `limit` 200, `out_dir` = `$PWD/export` ;
  - recopie chaque `doc_id → version` du résultat dans `export/versions.json`.
- Lance `python3 diffusion.py todo export J [MAINTENANT]`. Tu obtiens la liste à programmer (`programmer`) et la liste à relever (`relever`).
- Pour chaque `asset_id` distinct de `programmer` :
  - récupère la vidéo avec Artifact `read` (url de la régie, `path` = asset_id) ;
  - copie le fichier reçu vers le chemin donné dans la colonne `fichier` ;
  - s'il dépasse 9,9 Mo, ré-encode-le avec `python3 publication.py source.mp4 fichier`.
- Tiens un journal `faits.json`, une liste vide au départ. Ajoute une ligne après CHAQUE action réussie ou ratée, au format `{"doc_id", "reseau", "statut": "programme"|"echec", "heure", "detail"}`.

## 2. Ordre de passage
- Traite les lignes par heure croissante et par plateforme : TikTok, puis Meta (Facebook et Instagram ensemble), puis LinkedIn.
- Une même vidéo programmée à la même heure sur Facebook ET Instagram se fait en un seul passage dans le compositeur Meta. Utilise la légende Instagram.
- Ligne « trop_tard » (créneau passé, ou à moins de 25 minutes) :
  - programme-la à la prochaine heure pleine ou demie, au moins 30 minutes après maintenant, et au plus tard à 21:30 ;
  - au-delà, note `echec` avec le détail « créneau passé ».

Démarre Chrome avec `tabs_context_mcp` (`createIfEmpty`), puis ouvre un onglet par plateforme avec `tabs_create_mcp`. Si Chrome ne répond pas après 2 essais :
- note `echec` avec le détail « Chrome injoignable » pour toutes les lignes ;
- passe directement à l'étape 6.

## 3. TikTok — TikTok Studio (à affiner dans NOTES-UI.md)
1. Va sur `https://www.tiktok.com/tiktokstudio/upload`. Si l'adresse contient `login`, c'est un échec de connexion.
2. Avec `find`, trouve l'« input fichier vidéo », puis envoie la vidéo avec `file_upload` (paths = [fichier]). Ne clique jamais sur le bouton qui ouvre le sélecteur de fichiers.
3. Attends que l'éditeur et le champ « Description » apparaissent (`wait` de 3 s, 60 s au total).
4. Description : clique dans le champ, sélectionne tout (`cmd+a`) puis `Backspace`, car TikTok y met le nom du fichier. Tape ensuite la légende. Si une liste de suggestions de hashtags reste ouverte, appuie sur `Escape`. Vérifie les 30 premiers caractères.
5. « Quand publier » : choisis « Programmer », puis règle la date J et l'heure (le sélecteur est à l'heure du Mac, donc l'heure de Paris).
6. Qui peut regarder : « Tout le monde ». Commentaires autorisés.
7. « Afficher plus » : active « Contenu généré par l'IA ».
8. Clique le bouton final « Programmer ». Attends la confirmation, puis ajoute le fait `programme`.

## 4. Meta — Facebook et Instagram via Meta Business Suite (à affiner)
1. Va sur `https://business.facebook.com/latest/reels_composer`. Si la page demande de se connecter ou si aucune Page n'existe, c'est un échec avec le détail « pas de page ».
2. Destinations : coche la Page Facebook et/ou le compte Instagram selon la ligne.
3. Ajoute la vidéo par l'input fichier (`file_upload`), puis colle la légende.
4. Coche l'étiquette IA si elle est proposée.
5. Options de planification : « Programmer », règle la date et l'heure, puis clique « Programmer ». Ajoute un fait par réseau.

## 5. LinkedIn — profil de Calvin (à affiner)
1. Va sur `https://www.linkedin.com/feed/`, clique « Commencer un post », puis « Média ».
2. Envoie la vidéo par l'input fichier (`file_upload`), puis clique « Suivant ».
3. Tape le texte.
4. Clique l'icône horloge « Programmer », règle la date et l'heure, clique « Suivant », puis « Programmer ».
5. Ajoute le fait.

## 6. Relevé des stats (passage de 21:50 seulement)
Pour chaque ligne de `relever`, retrouve la publication par le début de sa légende et ajoute à `faits.json` :
`{"texte": début de légende, "reseau", "vues", "likes", "commentaires", "partages", "enregistrements"}`
N'inscris que les chiffres affichés. Un chiffre absent reste absent, n'écris jamais 0 à sa place.

Où lire les chiffres :
- TikTok : `https://www.tiktok.com/tiktokstudio/content` avec `get_page_text`.
- Meta : `https://business.facebook.com/latest/insights/content` (Facebook et Instagram).
- LinkedIn : `https://www.linkedin.com/in/me/recent-activity/all/` (les « impressions » comptent comme vues).

## 7. Écriture dans la régie, mémoire, message
- Lance `python3 diffusion.py ecritures export faits.json export/versions.json`, puis passe le tableau `writes` à ArtifactData `batch` (50 entrées maximum par appel).
- Ajoute à `taches/NOTES-UI.md`, en 10 lignes maximum, ce que tu as appris sur les interfaces : libellés exacts, pièges, ce qui a changé. Supprime ce qui est devenu faux. Puis :
  ```bash
  git add taches/NOTES-UI.md && git commit -m "diffusion J : notes UI" && git push
  ```
- Message final de 5 lignes maximum :
  - le nombre de vidéos programmées par réseau, par exemple « TikTok 5/5 · Instagram 2/2 » ;
  - les échecs et leur cause ;
  - les stats relevées ;
  - ce que Calvin doit faire, uniquement s'il y a quelque chose : se reconnecter à un compte, créer une Page, etc.
