"""Serveur voix Chatterbox (lancé dans le venv) : lit des lignes JSON {texte, out, seed} sur stdin,
écrit le WAV et répond {ok, out} — le modèle n'est chargé qu'une fois."""
import sys, json, torch, torchaudio as ta
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
m = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
REF = sys.argv[1]
print(json.dumps({"pret": True}), flush=True)
for l in sys.stdin:
    r = json.loads(l); torch.manual_seed(r.get("seed", 7))
    w = m.generate(r["texte"], language_id="fr", audio_prompt_path=REF, exaggeration=0.45, cfg_weight=0.5)
    ta.save(r["out"], w, m.sr); print(json.dumps({"ok": True, "out": r["out"]}), flush=True)
