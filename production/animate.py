"""Renderiza el video animado de la exposicion. Uso: animate.py <en|es> [--still] [--scene N]

Las animaciones son esquemas propios: no muestran datos numericos de la solucion real.
"""
import json
import math
import random
import re
import subprocess
import sys
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1920, 1080, 30
PAD = 0.6
BASE = Path("D:/Dev/mathdb-video")
SCENES = Path("D:/Dev/docker-phonon/scenes.json")
AUDIO = Path("D:/Dev/docker-phonon/out")

BG = (11, 18, 32)
PANEL = (24, 34, 54)
INK = (238, 242, 247)
MUTED = (148, 163, 184)
BLUE = (96, 165, 250)
ORANGE = (251, 146, 60)
GREEN = (74, 222, 128)
RED = (248, 113, 113)
FONTS = "C:/Windows/Fonts/"


def font(name, size, cache={}):
    key = (name, size)
    if key not in cache:
        cache[key] = ImageFont.truetype(FONTS + name, size)
    return cache[key]


def f_title(size=60):
    return font("seguisb.ttf", size)


def f_body(size=38):
    return font("segoeui.ttf", size)


def f_math(size=44):
    return font("cambria.ttc", size)


def f_mono(size=34):
    return font("consola.ttf", size)


TEXT = {
    "en": {
        1: {"title": "A Vortex, a Force and a Loophole",
            "sub": "OpenAI's claimed blowup for forced Navier–Stokes"},
        2: {"title": "Four doors. Any one solves the problem.",
            "doors": [("A", "fluid alone", "whole space", "unsolved"), ("B", "fluid alone", "periodic box", "unsolved"),
                      ("C", "with a push", "whole space", "claimed by OpenAI"), ("D", "with a push", "periodic box", "claimed by OpenAI")]},
        3: {"title": "The trick: choose the flow first", "eq_label": "Push = whatever is left over",
            "items": ["Any flow solves the equation with some push", "The real rule: speed blows up, the push stays perfectly smooth", "So the fluid must make the explosion by itself"]},
        4: {"title": "A whirlpool collapses into a needle", "speed": "peak speed", "energy": "energy in the core",
            "note": "Schematic. Thinning exaggerated."},
        5: {"title": "The gap: the ring at the edge", "core": "core: balanced", "ring": "ring: missing force", "far": "far away: balanced",
            "items": ["The missing piece grows without limit", "An outside push cannot fill it", "The fluid must"]},
        6: {"title": "Waves that carry force", "grow": "shear amplifies", "decay": "viscosity wins",
            "env": "one pulse (schematic)", "items": ["Zero on average, yet it transports momentum", "This effect is called Reynolds stress"]},
        7: {"title": "Fixing the fixes, forever", "round": "round", "err": "remaining error (schematic)",
            "law": "error exponent improves every round", "end": "The push stays smooth through t = 1, and fades to zero at the blowup point"},
        8: {"title": "Our own rough test (not a proof)", "x": "time remaining before the singularity", "speed": "peak speed",
            "l3": "L³ norm of the core", "energy": "core energy", "radius": "core radius",
            "note": "h = 0.05 shown for visibility. Scale estimates only."},
        9: {"title": "What does the Lean proof really tell us?",
            "cards": [("1", "Does the code pass the checker?", "We ran it on a clean setup: two checking programs accepted it."),
                      ("2", "Does its final statement match the official problem?", "We think so. Experts should confirm."),
                      ("3", "Is the written paper right, line by line?", "Lean does not answer that.")],
            "paper": "paper (8.19): m + 4", "lean": "Lean: w.length + 5", "credit": "reported by Bastounis, Circelli, Hansen; confirmed by us"},
        10: {"title": "Where things stand",
             "items": ["No independent peer review known to us", "MathDB still lists the problem as open",
                       "Reports: experts find the proof hard to read; OpenAI will not claim the prize",
                       "A dispute over credit is unresolved. We take no side."]},
        11: {"title": "Can a fluid left alone do the same?", "answer": "Nobody knows.",
             "items": ["All mathematics: the cited authors. Explanation made with AI assistance.",
                       "Sources: OpenAI paper and Lean repository; arXiv:2610.08144; Fefferman (Clay)"]},
    },
    "es": {
        1: {"title": "Un vórtice, una fuerza y un resquicio",
            "sub": "El estallido que OpenAI afirma para Navier–Stokes con fuerza"},
        2: {"title": "Cuatro puertas. Basta con abrir una.",
            "doors": [("A", "fluido solo", "todo el espacio", "sin resolver"), ("B", "fluido solo", "caja periódica", "sin resolver"),
                      ("C", "con empujón", "todo el espacio", "lo afirma OpenAI"), ("D", "con empujón", "caja periódica", "lo afirma OpenAI")]},
        3: {"title": "El truco: elegir primero el flujo", "eq_label": "Empujón = lo que sobra",
            "items": ["Cualquier flujo resuelve la ecuación con algún empujón", "La regla real: la velocidad estalla y el empujón sigue suave", "Así que el fluido debe hacer la explosión por sí mismo"]},
        4: {"title": "Un remolino colapsa en una aguja", "speed": "velocidad máxima", "energy": "energía en el núcleo",
            "note": "Esquema. Adelgazamiento exagerado."},
        5: {"title": "El hueco: el anillo del borde", "core": "núcleo: equilibrado", "ring": "anillo: falta fuerza", "far": "lejos: equilibrado",
            "items": ["Lo que falta crece sin límite", "Un empujón externo no puede llenarlo", "Debe hacerlo el fluido"]},
        6: {"title": "Ondas que transportan fuerza", "grow": "la cizalla amplifica", "decay": "gana la viscosidad",
            "env": "un pulso (esquema)", "items": ["Promedio cero, pero transporta momento", "A este efecto se le llama esfuerzo de Reynolds"]},
        7: {"title": "Arreglar los arreglos, sin fin", "round": "ronda", "err": "error restante (esquema)",
            "law": "el exponente del error mejora en cada ronda", "end": "El empujón sigue suave en t = 1 y se desvanece en el punto del estallido"},
        8: {"title": "Nuestra prueba aproximada (no es una demostración)", "x": "tiempo restante antes de la singularidad", "speed": "velocidad máxima",
            "l3": "norma L³ del núcleo", "energy": "energía del núcleo", "radius": "radio del núcleo",
            "note": "h = 0,05 para que se vea. Solo estimaciones de escala."},
        9: {"title": "¿Qué nos dice de verdad la prueba en Lean?",
            "cards": [("1", "¿El código pasa el verificador?", "Lo ejecutamos en un entorno limpio: dos programas distintos lo aceptaron."),
                      ("2", "¿Su enunciado final coincide con el problema oficial?", "Creemos que sí. Deben confirmarlo expertos."),
                      ("3", "¿El artículo es correcto línea por línea?", "Lean no responde a eso.")],
            "paper": "artículo (8.19): m + 4", "lean": "Lean: w.length + 5", "credit": "informado por Bastounis, Circelli y Hansen; confirmado por nosotros"},
        10: {"title": "Cómo están las cosas",
             "items": ["No conocemos ninguna revisión independiente por pares", "MathDB todavía marca el problema como abierto",
                       "Según las noticias: a los expertos les cuesta leerla; OpenAI no reclamará el premio",
                       "Hay una disputa sobre el crédito sin resolver. No tomamos partido."]},
        11: {"title": "¿Puede un fluido solo hacer lo mismo?", "answer": "Nadie lo sabe.",
             "items": ["Toda la matemática: los autores citados. Explicación hecha con ayuda de IA.",
                       "Fuentes: artículo y repositorio Lean de OpenAI; arXiv:2610.08144; Fefferman (Clay)"]},
    },
}


def mix(a, b, k):
    k = max(0.0, min(1.0, k))
    return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


def fade(t, start, dur=0.6):
    return max(0.0, min(1.0, (t - start) / dur))


def wrap(draw, text, fnt, width):
    lines, line = [], ""
    for word in text.split():
        trial = (line + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def text_block(d, x, y, text, fnt, color, width, gap=10):
    for line in wrap(d, text, fnt, width):
        d.text((x, y), line, font=fnt, fill=color)
        y += fnt.size + gap
    return y


def centered(d, cx, y, text, fnt, color):
    d.text((cx - d.textlength(text, font=fnt) / 2, y), text, font=fnt, fill=color)


def title(d, text, t, size=60):
    d.text((90, 56), text, font=f_title(size), fill=mix(BG, INK, fade(t, 0.1)))


def items(d, x, y, width, entries, t, T, size=40, start=0.08, span=0.8):
    for i, entry in enumerate(entries):
        k = fade(t, T * (start + span * i / len(entries)))
        if k <= 0:
            continue
        color = mix(BG, INK, k)
        d.ellipse((x, y + size * 0.42, x + 14, y + size * 0.42 + 14), fill=mix(BG, BLUE, k))
        y = text_block(d, x + 36, y, entry, f_body(size), color, width - 36) + 20
    return y


class Particles:
    """Particulas en vista lateral: entran hacia el eje y salen axialmente."""

    def __init__(self, n, seed=7):
        rng = random.Random(seed)
        self.p = [(rng.random(), rng.random() * math.tau, rng.uniform(-1, 1), rng.uniform(0.6, 1.4)) for _ in range(n)]

    def draw(self, d, cx, cy, radius, height, t, spin, color_a=BLUE, color_b=ORANGE, size=3, flow=0.09):
        for rho0, th0, z0, speed in self.p:
            rho = 1 - ((1 - rho0 + flow * speed * t) % 1)
            th = th0 + spin * speed * t / (0.25 + rho)
            depth = 0.55 + 0.45 * math.sin(th)
            z = z0 * (0.35 + 0.65 * (1 - rho))
            x = cx + radius * rho * math.cos(th)
            y = cy + height * z * math.sqrt(max(0.0, 1 - min(1.0, rho) ** 2 * 0.6))
            c = mix(BG, mix(color_b, color_a, rho), depth)
            s = size * (0.6 + 0.6 * depth)
            d.ellipse((x - s, y - s, x + s, y + s), fill=c)


PARTICLES = Particles(1500)


def scene1(d, t, T, x):
    PARTICLES.draw(d, W / 2, 500, 520, 300, t, 1.2)
    k = fade(t, 1.0, 1.0)
    fnt = f_title(78)
    centered(d, W / 2, 120, x["title"], fnt, mix(BG, INK, k))
    centered(d, W / 2, 830, x["sub"], f_body(40), mix(BG, MUTED, fade(t, 2, 1.0)))


def scene2(d, t, T, x):
    title(d, x["title"], t)
    glow = fade(t, T * 0.45, 1.2)
    for i, (letter, a, b, status) in enumerate(x["doors"]):
        left = 150 + i * 420
        top, w, h = 210, 360, 600
        k = fade(t, 0.5 + i * 0.6)
        open_door = i >= 2
        edge = mix(MUTED, ORANGE, glow) if open_door else MUTED
        d.rounded_rectangle((left, top, left + w, top + h), 20, fill=mix(BG, PANEL, k), outline=mix(BG, edge, k), width=5)
        centered(d, left + w / 2, top + 50, letter, f_title(120), mix(BG, edge if open_door else INK, k))
        centered(d, left + w / 2, top + 250, a, f_body(36), mix(BG, INK, k))
        centered(d, left + w / 2, top + 305, b, f_body(32), mix(BG, MUTED, k))
        color = mix(MUTED, ORANGE, glow) if open_door else MUTED
        status_font = f_title(30)
        centered(d, left + w / 2, top + 480, status, status_font, mix(BG, color, k))


def scene3(d, t, T, x):
    title(d, x["title"], t)
    k = fade(t, 1.0)
    eq = "f  =  ∂ₜu + (u·∇)u − νΔu + ∇p"
    d.rounded_rectangle((150, 200, W - 150, 400), 18, fill=mix(BG, PANEL, k))
    centered(d, W / 2, 232, eq, f_math(64), mix(BG, INK, k))
    centered(d, W / 2, 330, x["eq_label"], f_body(36), mix(BG, ORANGE, fade(t, T * 0.15)))
    items(d, 170, 470, 1580, x["items"], t, T, 44, start=0.2, span=0.7)


def scene4(d, t, T, x):
    title(d, x["title"], t)
    u = min(1.0, t / (T * 0.9))
    tau = math.exp(-5.0 * u)
    radius = 500 * tau**0.5
    height = 340 * tau**0.33
    PARTICLES.draw(d, 660, 530, radius, height, t, 1.0 / tau**0.45, flow=0.12)
    d.line((660, 170, 660, 890), fill=(60, 72, 95), width=2)
    speed = min(1.0, tau**-0.55 / (math.exp(5 * 0.55)))
    energy = tau**0.35
    for i, (name, value, color) in enumerate([(x["speed"], speed, ORANGE), (x["energy"], energy, BLUE)]):
        y = 300 + i * 230
        d.text((1270, y), name, font=f_body(36), fill=INK)
        d.rounded_rectangle((1270, y + 60, 1790, y + 110), 12, fill=PANEL)
        d.rounded_rectangle((1270, y + 60, 1270 + max(14, int(520 * value)), y + 110), 12, fill=color)
    d.text((1270, 790), x["note"], font=f_body(28), fill=MUTED)


def scene5(d, t, T, x):
    title(d, x["title"], t)
    cx, cy = 620, 530
    pulse = 0.5 + 0.5 * math.sin(t * 3.2)
    k = fade(t, T * 0.25)
    far = fade(t, T * 0.1)
    for i in range(70):
        angle = i / 70 * math.tau + t * 0.15
        r = 410 + 40 * math.sin(i * 1.7)
        x0, y0 = cx + r * math.cos(angle), cy + 0.82 * r * math.sin(angle)
        x1, y1 = cx + r * math.cos(angle + 0.05), cy + 0.82 * r * math.sin(angle + 0.05)
        d.line((x0, y0, x1, y1), fill=mix(BG, GREEN, far * 0.6), width=3)
    width = int(30 + 22 * pulse * (1 + t / T))
    d.ellipse((cx - 300, cy - 245, cx + 300, cy + 245), outline=mix(BG, mix(RED, ORANGE, pulse), k), width=width)
    PARTICLES.draw(d, cx, cy, 190, 165, t, 2.0)
    labels = [(x["core"], BLUE, 0.0), (x["ring"], RED, 0.25), (x["far"], GREEN, 0.1)]
    for i, (label, color, start) in enumerate(labels):
        d.ellipse((1140, 216 + i * 60, 1164, 240 + i * 60), fill=mix(BG, color, fade(t, T * start)))
        d.text((1180, 204 + i * 60), label, font=f_body(36), fill=mix(BG, INK, fade(t, T * start)))
    items(d, 1140, 450, 680, x["items"], t, T, 40, start=0.45, span=0.45)


def scene6(d, t, T, x):
    title(d, x["title"], t)
    period = 7.0
    phase = (t % period) / period
    amp = math.exp(-((phase - 0.5) ** 2) / (2 * 0.13**2))
    cx, cy, base = 500, 510, 300
    points = []
    for i in range(721):
        a = i / 720 * math.tau
        r = base + 62 * amp * math.sin(36 * a - t * 5)
        points.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.ellipse((cx - 170, cy - 170, cx + 170, cy + 170), fill=PANEL)
    PARTICLES.draw(d, cx, cy, 150, 150, t, 1.5, size=2)
    d.line(points, fill=mix(BLUE, ORANGE, amp), width=5)
    left, right, top, bottom = 980, 1800, 220, 560
    d.rectangle((left, top, right, bottom), fill=PANEL)
    mid = (left + right) / 2
    d.text((left + 20, top + 12), x["grow"], font=f_body(28), fill=ORANGE)
    w = d.textlength(x["decay"], font=f_body(28))
    d.text((right - w - 20, top + 12), x["decay"], font=f_body(28), fill=GREEN)
    d.line((mid, top + 60, mid, bottom), fill=(70, 84, 110), width=2)
    curve = []
    for i in range(int(phase * 400) + 1):
        p = i / 400
        e = math.exp(-((p - 0.5) ** 2) / (2 * 0.13**2))
        curve.append((left + p * (right - left), bottom - 20 - e * 240))
    if len(curve) > 1:
        d.line(curve, fill=BLUE, width=5)
    px, py = curve[-1]
    d.ellipse((px - 10, py - 10, px + 10, py + 10), fill=ORANGE)
    d.text((left, bottom + 10), x["env"], font=f_body(28), fill=MUTED)
    items(d, 990, 650, 820, x["items"], t, T, 36, start=0.2, span=0.6)


def scene7(d, t, T, x):
    title(d, x["title"], t)
    left, bottom = 150, 760
    rounds = 12
    d.text((left, 170), x["err"], font=f_body(34), fill=MUTED)
    for j in range(rounds):
        k = fade(t, 0.5 + j * (T * 0.62) / rounds, 0.4)
        if k <= 0:
            continue
        height = 500 * 0.68**j * k
        x0 = left + j * 138
        d.rounded_rectangle((x0, bottom - max(height, 3), x0 + 100, bottom), 8, fill=mix(ORANGE, GREEN, j / (rounds - 1)))
        centered(d, x0 + 50, bottom + 10, str(j), f_body(30), MUTED)
    d.text((left, bottom + 54), f'{x["round"]}   ·   σⱼ = 1/5 + j/10  →  ∞', font=f_math(36), fill=INK)
    d.text((left + 760, bottom + 58), x["law"], font=f_body(30), fill=MUTED)
    k = fade(t, T * 0.72)
    if k > 0:
        d.rounded_rectangle((980, 210, 1810, 470), 18, fill=mix(BG, PANEL, k))
        text_block(d, 1020, 250, x["end"], f_title(42), mix(BG, GREEN, k), 750)


def scene8(d, t, T, x):
    title(d, x["title"], t, 54)
    left, right, top, bottom = 200, 1320, 190, 780
    d.rectangle((left, top, right, bottom), fill=PANEL)
    h = 0.05
    series = [(x["speed"], -0.5 - h, ORANGE), (x["l3"], -4 * h / 3, GREEN), (x["energy"], 0.5 - 3 * h, BLUE), (x["radius"], 0.5, MUTED)]
    ymin, ymax = -3.5, 3.5
    for tick in range(0, 7):
        px = left + tick / 6 * (right - left)
        d.line((px, top, px, bottom), fill=(44, 56, 80), width=1)
        centered(d, px, bottom + 8, "10⁻" + "⁰¹²³⁴⁵⁶"[tick] if tick else "1", f_math(28), MUTED)
    centered(d, (left + right) / 2, bottom + 52, x["x"], f_body(30), MUTED)
    u = min(1.0, t / (T * 0.7))
    for i, (name, slope, color) in enumerate(series):
        k = min(1.0, max(0.0, u * 1.25 - i * 0.08))
        pts = []
        for n in range(int(200 * k) + 1):
            s = n / 200
            logtau = -6 * s
            val = slope * logtau
            pts.append((left + s * (right - left), bottom - (val - ymin) / (ymax - ymin) * (bottom - top)))
        if len(pts) > 1:
            d.line(pts, fill=color, width=5)
        d.rectangle((1370, 240 + i * 90, 1410, 250 + i * 90), fill=color)
        exponent = {0: "τ^(−1/2−h)", 1: "τ^(−4h/3)", 2: "τ^(1/2−3h)", 3: "τ^(1/2)"}[i]
        d.text((1425, 216 + i * 90), name, font=f_body(30), fill=INK)
        d.text((1425, 256 + i * 90), exponent, font=f_math(26), fill=MUTED)
    text_block(d, 1370, 640, x["note"], f_body(28), MUTED, 460)


def scene9(d, t, T, x):
    title(d, x["title"], t)
    for i, (num, question, answer) in enumerate(x["cards"]):
        k = fade(t, T * (0.1 + i * 0.2))
        y = 180 + i * 180
        d.rounded_rectangle((120, y, W - 120, y + 160), 18, fill=mix(BG, PANEL, k))
        d.text((160, y + 36), num, font=f_title(72), fill=mix(BG, BLUE, k))
        d.text((260, y + 26), question, font=f_title(38), fill=mix(BG, INK, k))
        d.text((260, y + 90), answer, font=f_body(34), fill=mix(BG, ORANGE, k))
    k = fade(t, T * 0.72)
    d.text((160, 740), x["paper"], font=f_mono(44), fill=mix(BG, GREEN, k))
    d.text((1000, 740), x["lean"], font=f_mono(44), fill=mix(BG, ORANGE, k))
    d.text((160, 805), x["credit"], font=f_body(28), fill=mix(BG, MUTED, k))


def scene10(d, t, T, x):
    title(d, x["title"], t)
    items(d, 170, 230, 1580, x["items"], t, T, 46, start=0.05, span=0.85)


def scene11(d, t, T, x):
    dim = 0.28
    for rho0, th0, z0, speed in PARTICLES.p[::2]:
        th = th0 + speed * t * 0.9
        px = W / 2 + 760 * rho0 * math.cos(th)
        py = 440 + 330 * z0
        d.ellipse((px - 2, py - 2, px + 2, py + 2), fill=mix(BG, BLUE, dim * (0.5 + 0.5 * math.sin(th))))
    centered(d, W / 2, 190, x["title"], f_title(72), mix(BG, INK, fade(t, T * 0.45)))
    centered(d, W / 2, 310, x["answer"], f_title(96), mix(BG, ORANGE, fade(t, T * 0.62)))
    y = 560
    for i, line in enumerate(x["items"]):
        color = mix(BG, INK, fade(t, T * (0.78 + 0.06 * i)))
        centered(d, W / 2, y, line, f_body(34), color)
        y += 60


DRAW = {1: scene1, 2: scene2, 3: scene3, 4: scene4, 5: scene5, 6: scene6, 7: scene7, 8: scene8, 9: scene9, 10: scene10, 11: scene11}


def sentence_cues(text, duration):
    sentences = re.findall(r"[^.!?]+[.!?]+", text) or [text]
    total = sum(len(s) for s in sentences)
    cues, start = [], 0.0
    for s in sentences:
        length = duration * len(s) / total
        cues.append((start, start + length, s.strip()))
        start += length
    return cues


def draw_caption(d, cues, t):
    for start, end, text in cues:
        if start <= t < end:
            fnt = f_body(36)
            lines = wrap(d, text, fnt, 1560)
            y = H - 40 - len(lines) * 48
            for line in lines:
                w = d.textlength(line, font=fnt)
                d.rounded_rectangle(((W - w) / 2 - 16, y - 4, (W + w) / 2 + 16, y + 44), 8, fill=(0, 0, 0))
                d.text(((W - w) / 2, y - 2), line, font=fnt, fill=(255, 255, 255))
                y += 48
            return


def wav_seconds(path):
    with wave.open(str(path), "rb") as handle:
        return handle.getnframes() / handle.getframerate()


def fmt(seconds):
    ms = int(round(seconds * 1000))
    return f"{ms // 3600000:02d}:{ms % 3600000 // 60000:02d}:{ms % 60000 // 1000:02d},{ms % 1000:03d}"


def main():
    lang = sys.argv[1]
    still = "--still" in sys.argv
    only = int(sys.argv[sys.argv.index("--scene") + 1]) if "--scene" in sys.argv else None
    scenes = json.loads(SCENES.read_text(encoding="utf-8"))
    out = BASE / lang / "anim"
    out.mkdir(parents=True, exist_ok=True)
    background = Image.new("RGB", (W, H), BG)
    srt, offset, index = [], 0.0, 1
    timeline = []
    for scene in scenes:
        n = scene["n"]
        audio = AUDIO / lang / f"scene_{n:02d}.wav"
        spoken = wav_seconds(audio)
        duration = spoken + PAD
        cues = sentence_cues(scene[lang], spoken)
        for start, end, text in cues:
            srt.append(f"{index}\n{fmt(offset + start)} --> {fmt(offset + end)}\n{text}\n")
            index += 1
        timeline.append({"n": n, "start": round(offset, 3), "duration": round(duration, 3)})
        offset += duration
        if only and n != only:
            continue
        if still:
            for name, moment in (("a", duration * 0.35), ("b", duration * 0.85)):
                image = background.copy()
                d = ImageDraw.Draw(image)
                DRAW[n](d, moment, duration, TEXT[lang][n])
                draw_caption(d, cues, moment)
                image.save(out / f"still_{n:02d}{name}.png")
            continue
        command = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                   "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                   "-pix_fmt", "yuv420p", str(out / f"scene_{n:02d}.mp4")]
        pipe = subprocess.Popen(command, stdin=subprocess.PIPE)
        for frame in range(int(duration * FPS)):
            moment = frame / FPS
            image = background.copy()
            d = ImageDraw.Draw(image)
            DRAW[n](d, moment, duration, TEXT[lang][n])
            draw_caption(d, cues, moment)
            pipe.stdin.write(image.tobytes())
        pipe.stdin.close()
        pipe.wait()
        print(f"escena {n} lista", flush=True)
    (BASE / lang / f"navier_stokes_{lang}.srt").write_text("\n".join(srt), encoding="utf-8")
    (BASE / lang / "timeline.json").write_text(json.dumps(timeline), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
