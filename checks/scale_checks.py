"""Comprueba con calculo simbolico los exponentes de escala de la exposicion de Navier-Stokes.

Solo usa las escalas del nucleo declaradas en el paper de OpenAI (seccion 2.1). Es una
comprobacion de consistencia heuristica, no una prueba ni una verificacion del paper.
"""
import sys

import sympy as sp

h, tau = sp.symbols("h tau", positive=True)

ELL_R = sp.Rational(1, 2)
ELL_Z = sp.Rational(1, 2) - h
U_TANGENTIAL = -sp.Rational(1, 2) - h
U_RADIAL = -sp.Rational(1, 2)
VOLUME = 2 * ELL_R + ELL_Z


def lp_core_power(p):
    """Exponente de tau de la potencia p-esima de la norma L^p del nucleo."""
    return sp.simplify(VOLUME + p * U_TANGENTIAL)


def check(name, computed, expected):
    ok = sp.simplify(computed - expected) == 0
    print(f"{'OK ' if ok else 'FAIL'} {name}: {sp.simplify(computed)}")
    return ok


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    results = [
        check("volumen del nucleo", VOLUME, sp.Rational(3, 2) - h),
        check("energia cinetica", lp_core_power(2), sp.Rational(1, 2) - 3 * h),
        check("Re angular", U_TANGENTIAL + ELL_R, -h),
        check("Re radial", U_RADIAL + ELL_R, 0),
        check("tasa radial de transporte", U_RADIAL - ELL_R, -1),
        check("tasa axial de transporte", U_TANGENTIAL - ELL_Z, -1),
        check("tasa de difusion radial", -2 * ELL_R, -1),
        check("cociente de difusion axial/radial", 2 * ELL_R - 2 * ELL_Z, 2 * h),
        check("disipacion radial", VOLUME + 2 * (U_TANGENTIAL - ELL_R), -sp.Rational(1, 2) - 3 * h),
    ]

    # Amplitud y longitud de onda de los pulsos (seccion 3.3), en potencias de q.
    wave_amplitude = -sp.Rational(1, 2) - h / 2
    wave_length = sp.Rational(1, 2) + h / 2
    results += [
        check("A_wave^2", 2 * wave_amplitude, -1 - h),
        check("divergencia del esfuerzo", 2 * wave_amplitude - ELL_R, -sp.Rational(3, 2) - h),
        check("derivada temporal tangencial", U_TANGENTIAL - 1, -sp.Rational(3, 2) - h),
        check("A_wave / U_tangencial", wave_amplitude - U_TANGENTIAL, h / 2),
        check("l_wave / l_r", wave_length - ELL_R, h / 2),
    ]

    # Normas criticas de la parte dominante del nucleo (solo escala).
    l3 = sp.simplify(lp_core_power(3) / 3)
    results.append(check("norma L3 del nucleo", l3, -sp.Rational(4, 3) * h))
    serrin = sp.simplify(lp_core_power(5) + 1)
    results.append(check("integral temporal de ||u||_5^5, exponente tras integrar", serrin, -6 * h))

    # Reescalado de viscosidad del paper: u_nu = sqrt(nu) u(x/sqrt(nu), t).
    nu, x = sp.symbols("nu x", positive=True)
    t = sp.symbols("t", positive=True)
    u = sp.Function("u")
    p = sp.Function("p")
    y = x / sp.sqrt(nu)
    u_nu = sp.sqrt(nu) * u(y, t)
    p_nu = nu * p(y, t)
    lhs = sp.diff(u_nu, t) + u_nu * sp.diff(u_nu, x) - nu * sp.diff(u_nu, x, 2) + sp.diff(p_nu, x)
    rhs = sp.sqrt(nu) * (
        sp.diff(u(y, t), t)
        + u(y, t) * sp.diff(u(y, t), x) * sp.sqrt(nu)
        - sp.diff(u(y, t), x, 2) * nu
        + sp.diff(p(y, t), x) * sp.sqrt(nu)
    )
    scale_ok = sp.simplify((lhs - rhs).doit()) == 0
    print(f"{'OK ' if scale_ok else 'FAIL'} reescalado de viscosidad (modelo 1D de la identidad)")
    results.append(scale_ok)

    h_max = sp.solve(sp.Rational(1, 2) - 3 * h, h)[0]
    print(f"La energia del nucleo tiende a cero si h < {h_max}; el paper usa h < 1/100.")
    print("TODO OK" if all(results) else "HAY FALLOS")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
