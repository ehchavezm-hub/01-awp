"""Chequeos estaticos del modulo VBA (complementan la ejecucion en LibreOffice).

1) Type/Const/variables de modulo antes del primer procedimiento
2) Array() asignado a un arreglo tipado
3) Identificadores sin declarar (analisis por procedimiento)
4) Variables locales o parametros con el mismo nombre (sin distinguir mayusculas)
   que un procedimiento llamado dentro del mismo procedimiento
5) Textos con secuencias \\uXXXX fuera de una llamada U(...)
"""
import re, sys
src = open(sys.argv[1], encoding="ascii").read()          # falla si hay bytes no ASCII
lines = src.splitlines()
proc_re = re.compile(r"^\s*(Public |Private )?(Sub|Function) (\w+)", re.I)
first_proc = next(i for i, l in enumerate(lines) if proc_re.match(l))
bad = [i + 1 for i, l in enumerate(lines[first_proc:], first_proc)
       if re.match(r"^(Private |Public )?(Type |Const |Enum )", l, re.I)]
print("1) Declaraciones de modulo despues del primer procedimiento:", bad or "ninguna")

typed = set(m.group(1).lower() for m in re.finditer(r"(\w+)\(\)\s+As\s+(?!Variant)\w+", src))
arr = [(i + 1, m.group(1)) for i, l in enumerate(lines) for m in [re.match(r"\s*(\w+)\s*=\s*Array\(", l)] if m]
print("2) Array() -> arreglo tipado:", [a for a in arr if a[1].lower() in typed] or "ninguno", "| asignaciones Array():", len(arr))

# Codigo sin comentarios ni textos, con continuaciones unidas
def sin_textos(t):
    out = []
    for l in t.splitlines():
        l2 = re.sub(r'"[^"\n]*"', '""', l)
        out.append(l2.split("'")[0])
    return "\n".join(out)
code = sin_textos(src)
code = re.sub(r" _\n", " ", code)
builtin = set("""
and or not xor mod is new nothing true false to step then else elseif end if for next each in do loop while wend until
select case exit sub function dim redim preserve as byval byref optional private public const type set let call on error
goto resume with option explicit long integer double single string boolean variant object date byte currency
range worksheet worksheets workbook chart chartobject series listobject listcolumn listrow application err me
abs int fix sqr log exp cos sin cdbl clng cstr cint csng ubound lbound len left right mid trim ucase lcase instr replace
format isnumeric isempty isnull iserror vartype chrw chr rgb rnd randomize timer now second minute doevents msgbox inputbox
iif array split val empty
left$ right$ mid$ trim$ ucase$ lcase$ format$ chrw$ chr$
vbinformation vbexclamation vbcritical vbquestion vbyesno vbno vbyes vblf vbcrlf vbstring vbboolean vbbinarycompare
xlcalculationmanual xlcalculationautomatic xlcontinuous xlcenter xlright xltop xlxyscattersmoothnomarkers xlxyscatterlinesnomarkers
xlcolumnclustered xlbarclustered xlvalue xlcategory xlticklabelpositionlow xllegendpositionbottom xllabelpositionright xlmaximum
hjinicio hjguia hjparametros hjresultados hjcurvas hjtornado hjrangos hjmatriz hjcomparacion hjsimulacion hjteoria
attribute vb_name type1 alertstyle operator formula1
""".split())
head = "\n".join(code.splitlines()[:first_proc])
modnames = set()
for m in re.finditer(r"^\s*(?:Private|Public|Dim)\s+(?:Const\s+)?(\w+)", head, re.M | re.I):
    modnames.add(m.group(1).lower())
for m in re.finditer(r"^\s*(?:Private |Public )?Type (\w+)", head, re.M | re.I):
    modnames.add(m.group(1).lower())
procs = {p.lower() for p in re.findall(r"(?im)^\s*(?:Private |Public )?(?:Sub|Function) (\w+)", code)}
problems, choques = [], []
blocks = re.split(r"(?im)^(?=[ \t]*(?:Public |Private )?(?:Sub|Function) )", code)
for b in blocks[1:]:
    mm = proc_re.match(b)
    name = mm.group(3)
    body = b[:re.search(r"(?im)^\s*End (Sub|Function)", b).end()]
    sig = body.lstrip("\n").split("\n", 1)[0]
    local = set()
    for m in re.finditer(r"(?:ByVal |ByRef |Optional )*(\w+)(?:\(\))?\s+As\b", sig):
        local.add(m.group(1).lower())
    for m in re.finditer(r"(?im)^\s*(?:Dim|Const)\s+(.+)$", body):
        for part in re.split(r",(?![^(]*\))", m.group(1)):
            mm2 = re.match(r"\s*(\w+)", part)
            if mm2: local.add(mm2.group(1).lower())
    labels = set(x.lower() for x in re.findall(r"(?m)^(\w+):\s*$", body))
    rest = body[len(sig):]
    usados = set()
    for m in re.finditer(r"(?<![\.\w])([A-Za-z_]\w*\$?)", rest):
        w = m.group(1).lower()
        usados.add(w.rstrip("$"))
        if w in builtin or w in local or w in modnames or w in procs or w in labels or w == name.lower():
            continue
        if rest[m.end():m.end() + 2].startswith(":="):
            continue
        problems.append((name, m.group(1)))
    for v in local:
        if v in procs and v != name.lower() and re.search(r"(?<![\.\w])%s\s*\(" % re.escape(v), rest, re.I):
            choques.append((name, v))
print("3) Identificadores sin declarar:", sorted(set(problems)) or "ninguno")
print("4) Variables que ocultan un procedimiento usado:", sorted(set(choques)) or "ninguna")

# 5) \uXXXX fuera de U(...)
logico = re.sub(r" _\n\s*", " ", "\n".join(l for l in src.splitlines() if not l.strip().startswith("'")))
malos = []
for ln in logico.splitlines():
    # tramos U( ... ) balanceados
    spans, i = [], 0
    while True:
        m = re.search(r"(?<![\w\.])U\(", ln[i:])
        if not m: break
        a = i + m.start(); depth = 0; j = a + 1; enstr = False
        while j < len(ln):
            ch = ln[j]
            if ch == '"': enstr = not enstr
            elif not enstr and ch == "(": depth += 1
            elif not enstr and ch == ")":
                depth -= 1
                if depth == 0: break
            j += 1
        spans.append((a, j)); i = j
    for m in re.finditer(r'"[^"]*\\u[0-9A-Fa-f]{4}[^"]*"', ln):
        if not any(a <= m.start() <= b for a, b in spans):
            malos.append(m.group(0)[:70])
print("5) Textos \\uXXXX fuera de U():", malos or "ninguno")
