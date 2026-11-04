"""Une escenas animadas con narracion, fondo sonoro y efectos discretos. Uso: mix_final.py <en|es>"""
import json
import subprocess
import sys
from pathlib import Path

BASE = Path("D:/Dev/mathdb-video")
AUDIO = Path("D:/Dev/docker-phonon/out")
SFX = BASE / "sfx"
PAD = 0.6


def run(*args):
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *args], check=True)


def main():
    lang = sys.argv[1]
    work = BASE / lang
    timeline = json.loads((work / "timeline.json").read_text(encoding="utf-8"))
    total = timeline[-1]["start"] + timeline[-1]["duration"]

    # Video: mismas escenas en orden, sin recodificar.
    video_list = work / "anim_list.txt"
    video_list.write_text("".join(f"file 'anim/scene_{s['n']:02d}.mp4'\n" for s in timeline), encoding="utf-8")
    run("-f", "concat", "-safe", "0", "-i", str(video_list), "-c", "copy", str(work / "video_only.mp4"))

    # Narracion: cada escena con su silencio final exacto segun la linea de tiempo.
    voices = []
    for s in timeline:
        wav = AUDIO / lang / f"scene_{s['n']:02d}.wav"
        voices += ["-i", str(wav)]
    parts = "".join(f"[{i}:a]aresample=48000,apad=whole_dur={s['duration']}[v{i}];" for i, s in enumerate(timeline))
    joined = "".join(f"[v{i}]" for i in range(len(timeline)))
    run(*voices, "-filter_complex", f"{parts}{joined}concat=n={len(timeline)}:v=0:a=1[o]", "-map", "[o]", str(work / "narration.wav"))

    # Fondo original: acorde grave lento y ruido marron muy filtrado.
    expr = "0.5*sin(2*PI*55*t)*(0.7+0.3*sin(2*PI*t/11))+0.3*sin(2*PI*82.41*t)*(0.7+0.3*sin(2*PI*t/17))+0.2*sin(2*PI*110*t)*(0.7+0.3*sin(2*PI*t/23))"
    run("-f", "lavfi", "-i", f"aevalsrc={expr}:s=48000:d={total}", "-f", "lavfi", "-i", f"anoisesrc=color=brown:r=48000:a=0.4:d={total}",
        "-filter_complex", f"[1:a]lowpass=f=300[n];[0:a][n]amix=inputs=2:weights='1 0.5':normalize=0,afade=t=in:d=4,afade=t=out:st={total - 5}:d=5,volume=0.045[o]",
        "-map", "[o]", str(work / "bed.wav"))

    # Efectos sintetizados por make_sfx.py, muy bajos bajo la voz.
    starts = {s["n"]: s["start"] for s in timeline}
    durations = {s["n"]: s["duration"] for s in timeline}
    cues = [("water.wav", 0.2, 0.09)]
    cues += [("whoosh.wav", starts[n] - 0.4, 0.09) for n in range(2, 12)]
    cues.append(("riser.wav", starts[4] + durations[4] - 4.6, 0.09))
    cues.append(("ding.wav", starts[9] + durations[9] * 0.72, 0.08))

    inputs = ["-i", str(work / "narration.wav"), "-i", str(work / "bed.wav")]
    filters = []
    labels = "[1:a][2:a]"
    for i, (name, at, gain) in enumerate(cues):
        inputs += ["-i", str(SFX / name)]
        delay = int(max(at, 0) * 1000)
        filters.append(f"[{i + 3}:a]aresample=48000,aformat=channel_layouts=mono,volume={gain},adelay={delay}:all=1[s{i}]")
        labels += f"[s{i}]"
    graph = ";".join(filters) + f";{labels}amix=inputs={len(cues) + 2}:normalize=0:duration=first,loudnorm=I=-16:TP=-1.5:LRA=11[o]"
    final = work / f"navier_stokes_{lang}_v4.mp4"
    run("-i", str(work / "video_only.mp4"), *inputs, "-filter_complex", graph,
        "-map", "0:v", "-map", "[o]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(final))
    print(final)


if __name__ == "__main__":
    main()
