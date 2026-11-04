"""Sintetiza las escenas del guion con Phonon. Uso: synth.py <en|es> <escena|all>"""
import json
import sys
from pathlib import Path

import ptts

WORK = Path("/work")
CONFIG = {
    "en": {"model": "hf://gradium/phonon-31m-en", "lang": "en", "voice": "Preston"},
    "es": {"model": "hf://gradium/phonon-40m-es", "lang": "es", "voice": "Yael"},
}


def main() -> int:
    language, which = sys.argv[1], sys.argv[2]
    config = CONFIG[language]
    scenes = json.loads((WORK / "scenes.json").read_text(encoding="utf-8"))
    tts = ptts.TTS(config["model"], lang=config["lang"], quant="q8")
    out = WORK / "out" / language
    out.mkdir(parents=True, exist_ok=True)
    for scene in scenes:
        if which != "all" and str(scene["n"]) != which:
            continue
        path = out / f"scene_{scene['n']:02d}.wav"
        tts.save(str(path), scene[language], voice=config["voice"])
        print(path, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
