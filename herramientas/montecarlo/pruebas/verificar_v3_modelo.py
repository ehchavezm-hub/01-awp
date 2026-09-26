"""Modelo completo, casos en memoria, bordes, 5.a dimension, validacion y hojas de salida (LibreOffice)."""
import os
import numpy as np
from run_lo import main
from referencia_numpy import simular, construir_riesgos, DIMS

N = 10000
calls = [("PruebaModelo", [N, 12345.0, "EJEMPLOS"]), ("PruebaModelo", [N, 12345.0, "REAL_INDEP"]),
         ("PruebaModelo", [N, 12345.0, "REAL"]), ("PruebaModelo", [N, 12345.0, "REAL"]),
         ("PruebaModelo", [N, 999.0, "REAL"]),
         ("PruebaMemoria", ["CORREL"]), ("PruebaMemoria", ["OPORT"]), ("PruebaMemoria", ["DESPUES"]),
         ("PruebaBordes", []), ("PruebaQuintaDimension", []), ("PruebaValidacion", []),
         ("PruebaSalidas", [N])]
os.environ["SAVE_AS"] = "salida_lo_v3.xlsx"
out = main("MonteCarlo_Prueba.xlsm", calls)

def parse(s):
    d = {}
    for kv in s.split("|"):
        if "=" in kv:
            k, v = kv.split("=", 1); d[k] = v
    return d

riesgos, _ = construir_riesgos("../entrada/Ejemplo.xlsm")
ref = {"EJEMPLOS": simular(riesgos, 400000, 3, False, solo="EJ-"),
       "REAL_INDEP": simular(riesgos, 400000, 3, False), "REAL": simular(riesgos, 400000, 3, True)}
todo = True
for (fn, args), r in zip(calls[:3], out[:3]):
    modo = args[2]; p = parse(r)
    print("\n=== %s  (VBA N=%d semilla 12345 vs numpy N=400 000)  NR=%s ND=%s tiempo LibreOffice=%ss" % (modo, N, p.get("NR"), p.get("ND"), p.get("T")))
    for d in DIMS:
        if d not in p: continue
        m, p50, p80, p90, vme = [float(x) for x in p[d].split(";")]
        x = ref[modo][d]
        rm, r50, r80, r90 = x.mean(), *np.percentile(x, [50, 80, 90])
        if rm == 0: continue
        dif = [(m-rm)/rm*100, (p50-r50)/r50*100, (p80-r80)/r80*100, (p90-r90)/r90*100]
        dvme = (vme - m) / m * 100
        ok = abs(dif[0]) <= 2 and abs(dif[1]) <= 3 and abs(dif[2]) <= 3 and abs(dvme) <= 2
        todo &= ok
        print("  %-10s media %+6.2f%%  P50 %+6.2f%%  P80 %+6.2f%%  P90 %+6.2f%%  | VME vs media simulada %+6.2f%%  %s   (P80 VBA=%s)" %
              (d, *dif, dvme, "OK" if ok else "REVISAR", format(p80, ",.1f")))
    for k, v in p.items():
        if k.startswith("G_"):
            o, l, n = v.split(";"); print("  grupo %-16s n=%s rho objetivo %.2f  lograda %.3f" % (k[2:], n, float(o), float(l)))
print("\nReproducibilidad: misma semilla -> identico:", out[2] == out[3] if False else parse(out[2]).get("COSTO") == parse(out[3]).get("COSTO"),
      "| otra semilla -> distinto:", parse(out[2]).get("COSTO") != parse(out[4]).get("COSTO"))
p = parse(out[2]); q = parse(out[1])
print("Correlacion sube el P80 de COSTO:", float(p["COSTO"].split(";")[2]) > float(q["COSTO"].split(";")[2]))
print("\nMEMORIA CORREL:", out[5]); c = parse(out[5]); ok = abs(float(c["LOG"]) - 0.6) <= 0.05; todo &= ok; print("   ->", "OK" if ok else "REVISAR")
print("MEMORIA OPORT:", out[6]); c = parse(out[6]); ok = abs(float(c["DIF"]) - float(c["DOS_VME"])) / float(c["DOS_VME"]) <= 0.02; todo &= ok; print("   ->", "OK" if ok else "REVISAR")
print("MEMORIA DESPUES:", out[7]); c = parse(out[7]); ok = abs(float(c["P80_DESPUES"]) - 3000) < 1e-6 and abs(float(c["MIN"]) - 3000) < 1e-6; todo &= ok; print("   ->", "OK" if ok else "REVISAR")
print("BORDES:", out[8]); todo &= ("ERROR" not in out[8] and "False" not in out[8].split("|OCC")[0])
print("QUINTA DIMENSION:", out[9][:400]); todo &= ("ND=5" in out[9] and "CALIDAD=" in out[9])
print("VALIDACION:", out[10][:1500])
print("SALIDAS:", out[11][:300]); todo &= out[11].startswith("OK")
print("\nRESULTADO:", "TODO OK" if todo else "HAY DIFERENCIAS")
