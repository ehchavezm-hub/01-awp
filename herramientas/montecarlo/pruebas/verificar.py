"""Compara el motor VBA (ejecutado en LibreOffice) con una simulacion numpy independiente."""
import math, numpy as np
from run_lo import main

rng = np.random.default_rng(2026)
M = 1_000_000

def tri(a, m, b, n): return rng.triangular(a, m, b, n)
def pert(a, m, b, n):
    al = 1 + 4 * (m - a) / (b - a); be = 1 + 4 * (b - m) / (b - a)
    return a + (b - a) * rng.beta(al, be, n)

occ3 = rng.random(M) < 0.35
occ4 = rng.random(M) < 0.20
costo = rng.normal(50000, 25000, M) + np.where(occ3, pert(30000, 80000, 200000, M), 0)
plazo = tri(7, 14, 28, M) + np.where(occ3, pert(10, 25, 60, M), 0) + \
        np.where(occ4, tri(5, 15, 45, M), 0) + rng.uniform(10, 40, M)
ref = {"C50": np.percentile(costo, 50), "C80": np.percentile(costo, 80), "C90": np.percentile(costo, 90),
       "T50": np.percentile(plazo, 50), "T80": np.percentile(plazo, 80), "T90": np.percentile(plazo, 90),
       "Cmean": costo.mean(), "Tmean": plazo.mean(), "occ3": 0.35, "occ4": 0.20}

dists = [  # (codigo, p1, p2, p3, media teorica, desv teorica, nombre)
    (1, 7, 14, 28, (7 + 14 + 28) / 3, math.sqrt((49 + 196 + 784 - 98 - 196 - 392) / 18), "TRIANGULAR"),
    (2, 30000, 80000, 200000, None, None, "PERT"),
    (3, 50000, 25000, 0, 50000, 25000, "NORMAL"),
    (4, 10, 40, 0, 25, 30 / math.sqrt(12), "UNIFORME"),
    (5, 100, 30, 0, 100, 30, "LOGNORMAL"),
    (6, 10, 0, 0, 10, 10, "EXPONENCIAL"),
    (7, 2, 10, 0, 10 * math.gamma(1.5), 10 * math.sqrt(math.gamma(2) - math.gamma(1.5) ** 2), "WEIBULL"),
]
# PERT teorico
a, m, b = 30000, 80000, 200000
al = 1 + 4 * (m - a) / (b - a); be = 1 + 4 * (b - m) / (b - a)
mu = a + (b - a) * al / (al + be); var = (b - a) ** 2 * al * be / ((al + be) ** 2 * (al + be + 1))
dists[1] = (2, a, m, b, mu, math.sqrt(var), "PERT")

calls = [("PruebaInterna", [10000, 12345.0]), 
         ("PruebaInterna", [100000, 999.0]), ("PruebaBordes", [])]
calls += [("PruebaSalidas", [3000]), ("PruebaParseRango", ["B12:N61"]), ("PruebaDatosMalos", [])]
calls += [("PruebaDist", [d[0], float(d[1]), float(d[2]), float(d[3]), 200000]) for d in dists]
out = dict(zip([(n, tuple(a)) for n, a in calls], main("MonteCarlo_Prueba.xlsm", calls)))

def parse(s):
    return {k: v for k, v in (x.split("=", 1) for x in s.split("|"))}

r1 = parse(out[("PruebaInterna", (10000, 12345.0))])
print("\n=== Escenario de ejemplo, semilla 12345, N = 10,000 (VBA) vs numpy N = 1,000,000 ===")
ok_all = True
for k in ["C50", "C80", "C90", "T50", "T80", "T90", "Cmean", "Tmean", "occ3", "occ4"]:
    v = float(r1[k].replace(",", ".")); dv = (v - ref[k]) / ref[k] * 100
    ok = abs(dv) <= 3
    if k.startswith("occ"):   # frecuencia observada: ruido muestral, informativo
        ok = abs(v - ref[k]) < 4 * (ref[k] * (1 - ref[k]) / 10000) ** 0.5
    ok_all &= ok
    print("%-6s VBA=%14.2f  numpy=%14.2f  dif=%+6.2f%%  %s" % (k, v, ref[k], dv, "OK" if ok else "FUERA"))
print("Tornado costo:", [r1[k].split(":")[0] for k in r1 if k.startswith("SC")])
print("Tornado plazo:", [r1[k].split(":")[0] for k in r1 if k.startswith("ST")])
print("Salidas:", out[("PruebaSalidas", (3000,))])
print("Parser tabla ejemplo:", out[("PruebaParseRango", ("B12:N61",))][:60], "...")
dm = out[("PruebaDatosMalos", ())]
print("Validacion datos malos: ok=False?", "ok=False" in dm, "| errores detectados:", dm.count(" / "),
      "| marcas rojo/amarillo:", dm.split("|")[-3:])
print("\n=== Distribuciones (VBA, 200,000 muestras) vs teoria ===")
for d in dists:
    s = out[("PruebaDist", (d[0], float(d[1]), float(d[2]), float(d[3]), 200000))].split("|")
    mv, sv = float(s[0]), float(s[1])
    em, es = (mv - d[4]) / d[4] * 100, (sv - d[5]) / d[5] * 100
    ok = abs(em) < 1.5 and abs(es) < 2.5; ok_all &= ok
    print("%-12s media %10.3f (teo %10.3f, %+5.2f%%)  desv %10.3f (teo %10.3f, %+5.2f%%)  min %.3f max %.3f  %s"
          % (d[6], mv, d[4], em, sv, d[5], es, float(s[2]), float(s[3]), "OK" if ok else "REVISAR"))
print("\nRESULTADO GLOBAL:", "TODO OK" if ok_all else "HAY DIFERENCIAS")
