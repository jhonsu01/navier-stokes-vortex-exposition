"""Genera las figuras originales de la exposicion en ingles y espanol.

Son esquemas propios: las proporciones se exageran y asi se indica en cada pie de figura.
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Ellipse, FancyArrowPatch, FancyBboxPatch

OUT = Path(__file__).resolve().parent / "figures"
INK = "#1f2933"
BLUE = "#1f6fb2"
ORANGE = "#d9730d"
GREEN = "#2f855a"
GRAY = "#7b8794"

TEXT = {
    "en": {
        "times": ["$\\tau = 1$", "$\\tau = 0.25$", "$\\tau = 0.04$"],
        "axis": "axis of rotation",
        "core_title": "A core that gets thinner faster than it gets shorter",
        "tau": "time remaining before the singularity, $\\tau = 1 - t$",
        "scale": "size (arbitrary units, log scale)",
        "speed": "peak speed $\\sim \\tau^{-1/2-h}$",
        "l3": "$L^3$ norm of the core $\\sim \\tau^{-4h/3}$",
        "energy": "core energy $\\sim \\tau^{1/2-3h}$",
        "radius": "core radius $\\sim \\tau^{1/2}$",
        "scales_title": "Speed explodes while energy vanishes ($h = 0.05$ shown for visibility)",
        "bg": "Collapsing vortex\nresidual blows up",
        "pulses": "Oscillating pulses\nmomentum flux cancels\nthe singular part",
        "cycle": "Correction cycle\neach pass improves\nthe decay of the error",
        "force": "Smooth force $f$\nthrough $t = 1$",
        "repeat": "repeat infinitely often",
        "cycle_title": "How the singular residual becomes a smooth force",
        "slot": "pulse time (normalized)",
        "amp": "amplitude (normalized)",
        "grow": "shear amplifies",
        "decay": "viscosity wins",
        "pulse_title": "One pulse: growth, then decay (schematic)",
        "cone_title": "Two wave families span the needed stress",
        "cone": "reachable with\npositive weights",
        "flux1": "angular-momentum flux",
        "flux2": "axial-momentum flux",
    },
    "es": {
        "times": ["$\\tau = 1$", "$\\tau = 0{,}25$", "$\\tau = 0{,}04$"],
        "axis": "eje de rotación",
        "core_title": "Un núcleo que adelgaza más rápido de lo que se acorta",
        "tau": "tiempo restante antes de la singularidad, $\\tau = 1 - t$",
        "scale": "tamaño (unidades arbitrarias, escala log)",
        "speed": "velocidad máxima $\\sim \\tau^{-1/2-h}$",
        "l3": "norma $L^3$ del núcleo $\\sim \\tau^{-4h/3}$",
        "energy": "energía del núcleo $\\sim \\tau^{1/2-3h}$",
        "radius": "radio del núcleo $\\sim \\tau^{1/2}$",
        "scales_title": "La velocidad explota y la energía se desvanece ($h = 0{,}05$ para que se vea)",
        "bg": "Vórtice que colapsa\nel residuo explota",
        "pulses": "Pulsos oscilantes\nsu flujo de momento cancela\nla parte singular",
        "cycle": "Ciclo de corrección\ncada pasada mejora\nel decaimiento del error",
        "force": "Fuerza suave $f$\na través de $t = 1$",
        "repeat": "se repite infinitas veces",
        "cycle_title": "Cómo el residuo singular se convierte en una fuerza suave",
        "slot": "tiempo del pulso (normalizado)",
        "amp": "amplitud (normalizada)",
        "grow": "la cizalla amplifica",
        "decay": "gana la viscosidad",
        "pulse_title": "Un pulso: crecimiento y luego decaimiento (esquema)",
        "cone_title": "Dos familias de ondas generan el esfuerzo necesario",
        "cone": "alcanzable con\npesos positivos",
        "flux1": "flujo de momento angular",
        "flux2": "flujo de momento axial",
    },
}


def core_figure(t, path):
    fig, axes = plt.subplots(1, 3, figsize=(8, 3.1), sharex=True, sharey=True)
    for ax, tau, label in zip(axes, [1.0, 0.25, 0.04], t["times"]):
        # El exponente h se exagera a 0.15 para hacer visible la esbeltez.
        radius, height = tau**0.5, tau**0.35
        ax.add_patch(Ellipse((0, 0), 2 * radius, 2 * height, color=BLUE, alpha=0.25))
        ax.add_patch(Ellipse((0, 0), 2 * radius, 2 * height, fill=False, ec=BLUE, lw=1.5))
        ax.axvline(0, color=GRAY, ls="--", lw=1)
        ax.annotate("", xy=(0.06 * radius, 0), xytext=(radius * 0.8, 0),
                    arrowprops=dict(arrowstyle="->", color=ORANGE, lw=1.6))
        ax.annotate("", xy=(-0.06 * radius, 0), xytext=(-radius * 0.8, 0),
                    arrowprops=dict(arrowstyle="->", color=ORANGE, lw=1.6))
        ax.annotate("", xy=(0, height * 0.9), xytext=(0, 0.1 * height),
                    arrowprops=dict(arrowstyle="->", color=GREEN, lw=1.6))
        ax.annotate("", xy=(0, -height * 0.9), xytext=(0, -0.1 * height),
                    arrowprops=dict(arrowstyle="->", color=GREEN, lw=1.6))
        ax.set_title(label, color=INK)
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-1.2, 1.2)
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
    fig.suptitle(t["core_title"], color=INK, fontsize=12)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def scales_figure(t, path):
    h = 0.05
    tau = np.logspace(0, -6, 200)
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    series = [
        (tau ** (-0.5 - h), t["speed"], ORANGE, "-"),
        (tau ** (-4 * h / 3), t["l3"], GREEN, "--"),
        (tau ** (0.5 - 3 * h), t["energy"], BLUE, "-"),
        (tau**0.5, t["radius"], GRAY, ":"),
    ]
    for values, label, color, style in series:
        ax.loglog(tau, values, color=color, ls=style, lw=2, label=label)
    ax.invert_xaxis()
    ax.set_xlabel(t["tau"], color=INK)
    ax.set_ylabel(t["scale"], color=INK)
    ax.set_title(t["scales_title"], color=INK, fontsize=11)
    ax.grid(alpha=0.25, which="both")
    ax.legend(frameon=False, fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def cycle_figure(t, path):
    fig, ax = plt.subplots(figsize=(8.2, 2.7))
    ax.set_xlim(0, 10.4)
    ax.set_ylim(0, 3)
    ax.axis("off")
    boxes = [(0.1, t["bg"], "#fde8d7"), (2.75, t["pulses"], "#dbeafe"),
             (5.4, t["cycle"], "#e5e7eb"), (8.05, t["force"], "#d7f0e1")]
    for x, label, color in boxes:
        ax.add_patch(FancyBboxPatch((x, 0.7), 2.25, 1.5, boxstyle="round,pad=0.04",
                                    fc=color, ec=INK, lw=1))
        ax.text(x + 1.125, 1.45, label, ha="center", va="center", fontsize=8.5, color=INK)
    for x in [2.4, 5.05, 7.7]:
        ax.add_patch(FancyArrowPatch((x, 1.45), (x + 0.32, 1.45), arrowstyle="->",
                                     mutation_scale=14, color=INK, lw=1.3))
    ax.add_patch(FancyArrowPatch((7.3, 2.25), (5.8, 2.25), connectionstyle="arc3,rad=0.7",
                                 arrowstyle="->", mutation_scale=13, color=GRAY, lw=1.2))
    ax.text(6.55, 2.82, t["repeat"], ha="center", fontsize=8, color=GRAY)
    ax.set_title(t["cycle_title"], color=INK, fontsize=11, y=-0.08)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def pulse_figure(t, path):
    fig, (left, right) = plt.subplots(1, 2, figsize=(8.2, 3.3))
    v = np.linspace(0, 1, 500)
    envelope = np.exp(-((v - 0.5) ** 2) / (2 * 0.11**2))
    left.plot(v, envelope, color=BLUE, lw=2)
    left.plot(v, envelope * np.cos(70 * v), color=BLUE, lw=0.6, alpha=0.5)
    left.plot(v, -envelope, color=BLUE, lw=1, alpha=0.4)
    left.axvspan(0, 0.5, color=ORANGE, alpha=0.08)
    left.axvspan(0.5, 1, color=GREEN, alpha=0.08)
    left.text(0.25, 1.12, t["grow"], ha="center", fontsize=8.5, color=ORANGE)
    left.text(0.75, 1.12, t["decay"], ha="center", fontsize=8.5, color=GREEN)
    left.set_ylim(-1.1, 1.3)
    left.set_xlabel(t["slot"], color=INK, fontsize=9)
    left.set_ylabel(t["amp"], color=INK, fontsize=9)
    left.set_title(t["pulse_title"], color=INK, fontsize=10)

    v1, v2 = np.array([1.0, 0.25]), np.array([0.3, 1.0])
    target = 0.7 * v1 + 0.6 * v2
    right.fill([0, 1.6 * v1[0], 1.6 * v2[0]], [0, 1.6 * v1[1], 1.6 * v2[1]],
               color=BLUE, alpha=0.14)
    for vec, name, color in [(v1, "$v_1$", BLUE), (v2, "$v_2$", BLUE), (target, "$T$", ORANGE)]:
        right.annotate("", xy=vec, xytext=(0, 0), arrowprops=dict(arrowstyle="->", color=color, lw=2))
        right.text(vec[0] + 0.04, vec[1] + 0.04, name, color=color, fontsize=11)
    right.text(0.98, 1.2, t["cone"], fontsize=8.5, color=INK, ha="center")
    right.set_xlim(0, 1.5)
    right.set_ylim(0, 1.5)
    right.set_xticks([])
    right.set_yticks([])
    right.set_xlabel(t["flux1"], color=INK, fontsize=9)
    right.set_ylabel(t["flux2"], color=INK, fontsize=9)
    right.set_title(t["cone_title"], color=INK, fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def main() -> int:
    OUT.mkdir(exist_ok=True)
    for lang, t in TEXT.items():
        core_figure(t, OUT / f"core_{lang}.png")
        scales_figure(t, OUT / f"scales_{lang}.png")
        cycle_figure(t, OUT / f"cycle_{lang}.png")
        pulse_figure(t, OUT / f"pulse_{lang}.png")
    print(sorted(p.name for p in OUT.glob("*.png")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
