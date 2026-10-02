#!/usr/bin/env python3
"""Copie de diffusion ≤ 9,3 Mo de chaque vidéo (l'envoi de fichier par Chrome est plafonné à 10 Mo par appel).
python3 publication.py sorties/<date>            → <id>.pub.mp4 à côté de chaque <id>.mp4
python3 publication.py entree.mp4 sortie.mp4     → un seul fichier
Encodage x264 deux passes, preset slow, débit calculé sur la durée (plafond 4,5 Mb/s), AAC 128 k, faststart."""
import os, subprocess, sys, tempfile, glob

CIBLE_MO = 9.3


def duree(f):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]).strip())


def encode(src, dst):
    if os.path.getsize(src) <= CIBLE_MO * 1024 * 1024 and src != dst:
        # déjà assez léger : simple remux faststart, aucune perte
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-c', 'copy', '-movflags', '+faststart', dst], check=True)
        return
    br = int(min(4500, CIBLE_MO * 8 * 1024 / duree(src) - 160))
    with tempfile.TemporaryDirectory() as t:
        log = os.path.join(t, 'p')
        v = ['-c:v', 'libx264', '-preset', 'slow', '-b:v', f'{br}k', '-pix_fmt', 'yuv420p', '-passlogfile', log]
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, *v, '-pass', '1', '-an', '-f', 'null', os.devnull], check=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, *v, '-maxrate', f'{br * 2}k', '-bufsize', f'{br * 2}k', '-pass', '2',
                        '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', dst], check=True)
    if os.path.getsize(dst) > 9.9 * 1024 * 1024:
        raise SystemExit(f'{dst} dépasse 9,9 Mo')


if __name__ == '__main__':
    a = sys.argv[1:]
    if len(a) == 2 and a[0].endswith('.mp4'):
        encode(a[0], a[1])
    else:
        for f in sorted(glob.glob(os.path.join(a[0], '*.mp4'))):
            if f.endswith(('.pub.mp4', '.part.mp4')):
                continue
            d = f[:-4] + '.pub.mp4'
            if not os.path.exists(d):
                tmp = d[:-4] + '.part.mp4'   # écriture atomique : jamais de fichier tronqué si le rendu est coupé
                encode(f, tmp)
                os.replace(tmp, d)
            print(f'{os.path.basename(d)} {os.path.getsize(d) / 1048576:.1f} Mo')
