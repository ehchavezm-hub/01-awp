"""Referencia independiente en numpy del modelo v3 (misma lógica que la macro)."""
import math, sys
import numpy as np
sys.path.insert(0, "..")
from datos_riesgos import construir_riesgos

DIMS = ["COSTO", "PLAZO", "ING_DISENO", "ING_CAMPO"]

def muestra(rng, spec, n):
    d, a, b, c = spec
    if d == "PERT":
        al = 1 + 4 * (b - a) / (c - a); be = 1 + 4 * (c - b) / (c - a)
        return a + (c - a) * rng.beta(al, be, n)
    if d == "TRIANGULAR":
        return rng.triangular(a, b, c, n)
    if d == "UNIFORME":
        return rng.uniform(a, b, n)
    if d == "NORMAL":
        return rng.normal(a, b, n)
    raise ValueError(d)

def simular(riesgos, N, seed=1, correlacion=True, solo=None):
    rng = np.random.default_rng(seed)
    act = [r for r in riesgos if (r["ACTIVO"] == "SI" if solo is None else r["ID"].startswith(solo))]
    tot = {d: np.zeros(N) for d in DIMS}
    vals = []
    for r in act:
        occ = rng.random(N) < r["PROB"]
        v = {}
        for d in DIMS:
            if r["DIMS"][d]:
                v[d] = np.where(occ, muestra(rng, r["DIMS"][d], N), 0.0)
        vals.append((r, v))
    if correlacion:
        grupos = {}
        for r, v in vals:
            if r["GRUPO"]:
                grupos.setdefault(r["GRUPO"], []).append((r, v))
        for g, miembros in grupos.items():
            rho = miembros[0][0]["RHO"]; rn = 2 * math.sin(math.pi * rho / 6)
            W = rng.standard_normal(N)
            if len(miembros) < 2: continue
            for r, v in miembros:
                clave = v[next(d for d in DIMS if d in v)]
                S = math.sqrt(rn) * W + math.sqrt(1 - rn) * rng.standard_normal(N)
                ixk = np.argsort(clave, kind="stable"); ixs = np.argsort(S, kind="stable")
                perm = np.empty(N, dtype=int); perm[ixs] = ixk
                for d in v: v[d] = v[d][perm]
    for r, v in vals:
        for d in v: tot[d] += v[d]
    return tot

if __name__ == "__main__":
    riesgos, _ = construir_riesgos("../entrada/Ejemplo.xlsm")
    N = 400000
    for corr in (False, True):
        t = simular(riesgos, N, 7, corr)
        print("CORRELACION" if corr else "INDEPENDIENTE")
        for d in DIMS:
            x = t[d]; print("  %-10s media=%14.2f P50=%14.2f P80=%14.2f P90=%14.2f" % (d, x.mean(), *np.percentile(x, [50, 80, 90])))
    t = simular(riesgos, N, 7, False, solo="EJ-")
    print("EJEMPLOS (5 de la v1)")
    for d in ("COSTO", "PLAZO"):
        x = t[d]; print("  %-10s media=%14.2f P50=%14.2f P80=%14.2f P90=%14.2f" % (d, x.mean(), *np.percentile(x, [50, 80, 90])))
