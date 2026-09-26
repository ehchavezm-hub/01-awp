"""Generador MRG32k3a y las 20 distribuciones: VBA (LibreOffice) vs. teoria / referencia Python."""
import math
from run_lo import main

# Referencia Python del MRG32k3a
m1, m2 = 4294967087, 4294944443
def mrg(estado, n):
    s1, s2 = list(estado[:3]), list(estado[3:]); out = []
    for _ in range(n):
        p1 = (1403580 * s1[1] - 810728 * s1[0]) % m1; s1 = [s1[1], s1[2], p1]
        p2 = (527612 * s2[2] - 1370589 * s2[0]) % m2; s2 = [s2[1], s2[2], p2]
        out.append(((p1 - p2) if p1 > p2 else (p1 - p2 + m1)) * 2.328306549295727688e-10)
    return out
def sembrar(semilla):
    x = abs(int(semilla)) % 2**32; v = []
    for _ in range(6):
        x = (69069 * x + 1) % 2**32; v.append(x)
    return [v[0] % m1, v[1] % m1, v[2] % m1, v[3] % m2, v[4] % m2, v[5] % m2]

G = math.gamma
def tri_sd(a, m, b): return math.sqrt((a*a + m*m + b*b - a*m - a*b - m*b) / 18)
def beta_ms(al, be, a, b):
    mu = al / (al + be); var = al * be / ((al + be) ** 2 * (al + be + 1))
    return a + (b - a) * mu, (b - a) * math.sqrt(var)
def pert_ms(a, m, b, lam=4):
    return beta_ms(1 + lam * (m - a) / (b - a), 1 + lam * (b - m) / (b - a), a, b)
def tn_ms(mu, s, a, b):
    phi = lambda z: math.exp(-z*z/2) / math.sqrt(2*math.pi); Phi = lambda z: 0.5*(1+math.erf(z/math.sqrt(2)))
    al, be = (a-mu)/s, (b-mu)/s; Z = Phi(be) - Phi(al)
    mean = mu + s*(phi(al)-phi(be))/Z
    var = s*s*(1 + (al*phi(al) - be*phi(be))/Z - ((phi(al)-phi(be))/Z)**2)
    return mean, math.sqrt(var)
# (codigo, P1, P2, P3, P4, media, desv, nombre)
casos = [
 (1, 250000, "", "", "", 250000, 0, "CONSTANTE"),
 (2, 10, 40, "", "", 25, 30/math.sqrt(12), "UNIFORME"),
 (3, 10, 20, 45, "", 25, tri_sd(10,20,45), "TRIANGULAR"),
 (4, 5, 12, 30, 10, None, None, "TRIGEN"),
 (5, 800000, 2500000, 6000000, "", *pert_ms(800000, 2500000, 6000000), "PERT"),
 (6, 10, 15, 40, 8, *pert_ms(10, 15, 40, 8), "PERT_MODIFICADA"),
 (7, 2, 5, 0, 100, *beta_ms(2, 5, 0, 100), "BETA_GENERAL"),
 (8, 50000, 25000, "", "", 50000, 25000, "NORMAL"),
 (9, 20, 10, 0, 35, *tn_ms(20, 10, 0, 35), "NORMAL_TRUNCADA"),
 (10, 100, 30, "", "", 100, 30, "LOGNORMAL"),
 (11, 2.5, 400, "", "", 1000, math.sqrt(2.5)*400, "GAMMA"),
 (12, 10, "", "", "", 10, 10, "EXPONENCIAL"),
 (13, 2, 12, "", "", 12*G(1.5), 12*math.sqrt(G(2)-G(1.5)**2), "WEIBULL"),
 (14, 10, 4, "", "", 10+0.5772156649*4, math.pi*4/math.sqrt(6), "GUMBEL"),
 (15, 15, 3, "", "", 15, math.pi*3/math.sqrt(3), "LOGISTICA"),
 (16, 4.5, 100, "", "", 4.5*100/3.5, 100*math.sqrt(4.5/(3.5**2*2.5)), "PARETO"),
 (17, 3, "", "", "", 3, math.sqrt(3), "POISSON"),
 (17, 80, "", "", "", 80, math.sqrt(80), "POISSON (lambda 80, PTRS)"),
 (18, 40, 0.15, "", "", 6, math.sqrt(40*.15*.85), "BINOMIAL"),
 (18, 500, 0.3, "", "", 150, math.sqrt(500*.3*.7), "BINOMIAL (n 500, inversion)"),
 (19, 0, 2, "", "", 1, math.sqrt((9-1)/12), "DISCRETA_UNIFORME"),
 (20, "0;150000;400000", "0.6;0.3;0.1", "", "", 85000, math.sqrt(0.3*150000**2+0.1*400000**2-85000**2), "DISCRETA"),
]
N = 60000
calls = [("PruebaGenerador", [])] + [("PruebaDist", [c[0], c[1], c[2], c[3], c[4], N]) for c in casos]
out = main("MonteCarlo_Prueba.xlsm", calls)

g = out[0].split("|")
vba10 = [float(x) for x in g[0].split(";") if x]
ref10 = mrg([12345]*6, 10)
print("GENERADOR estado 12345x6: max |VBA - Python| =", max(abs(a-b) for a, b in zip(vba10, ref10)))
print("   primeros valores VBA:", [round(x, 10) for x in vba10[:5]])
vbs = [float(x) for x in g[1].split(";") if x]
print("GENERADOR Semilla=12345: max |VBA - Python| =", max(abs(a-b) for a, b in zip(vbs, mrg(sembrar(12345), 3))))
todo = True
print("\n%-28s %14s %14s %8s %14s %14s %8s  %s" % ("DISTRIBUCION", "media VBA", "media teo", "dif", "desv VBA", "desv teo", "dif", "estado"))
for c, r in zip(casos, out[1:]):
    if r.startswith("ERROR"):
        print(c[7], r); todo = False; continue
    p = r.split("|")
    mv, sv = float(p[0]), float(p[1]); mteo_vba = float(p[4])
    mt, st = c[5], c[6]
    if c[7] == "TRIGEN":
        a, b = [float(x) for x in p[5].split(";")]
        mt, st = (a + 12 + b) / 3, tri_sd(a, 12, b)
        # comprobar percentiles 10/90 de la triangular resuelta
        F = lambda x: (x-a)**2/((b-a)*(12-a)) if x <= 12 else 1-(b-x)**2/((b-a)*(b-12))
        print("   TRIGEN resuelto: min=%.4f max=%.4f  P(X<5)=%.4f  P(X>30)=%.4f" % (a, b, F(5), 1-F(30)))
    dm = (mv-mt)/abs(mt)*100
    ds = (sv-st)/st*100 if st else 0
    tol_m, tol_s = 1.0, (4.0 if "PARETO" in c[7] else 2.0)
    ok = abs(dm) <= tol_m and (st == 0 or abs(ds) <= tol_s) and abs(mteo_vba-mt)/abs(mt) < 1e-4
    todo &= ok
    print("%-28s %14.4f %14.4f %7.2f%% %14.4f %14.4f %7.2f%%  %s" % (c[7], mv, mt, dm, sv, st, ds, "OK" if ok else "REVISAR"))
    if c[7] in ("POISSON", "DISCRETA_UNIFORME"):
        fr = [float(x) for x in p[6].split(";") if x]
        if c[7] == "POISSON":
            teo = [math.exp(-3)*3**k/math.factorial(k) for k in range(6)]
        else:
            teo = [1/3, 1/3, 1/3, 0, 0, 0]
        print("   frecuencias 0..5 VBA:", [round(x, 4) for x in fr], " teoria:", [round(x, 4) for x in teo])
print("\nRESULTADO:", "TODAS OK" if todo else "HAY DIFERENCIAS")
