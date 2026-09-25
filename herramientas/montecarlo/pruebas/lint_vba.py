"""Chequeos estaticos del modulo VBA (complementan la ejecucion en LibreOffice)."""
import re, sys
src = open(sys.argv[1], encoding="ascii").read()          # falla si hay bytes no ASCII
lines = src.splitlines()

# 1) Declaraciones de modulo antes del primer procedimiento
proc_re = re.compile(r"^\s*(Public |Private )?(Sub|Function) (\w+)", re.I)
first_proc = next(i for i, l in enumerate(lines) if proc_re.match(l))
bad = [i + 1 for i, l in enumerate(lines[first_proc:], first_proc)
       if re.match(r"^\s*(Private |Public )?(Type |Const |Enum )", l, re.I) and not l.strip().startswith("'")
       and not re.match(r"^\s{4,}", l)]
print("1) Type/Const despues del primer procedimiento:", bad or "ninguno")

# 2) Array() asignado a arreglo tipado
typed = set(m.group(1).lower() for m in re.finditer(r"(\w+)\(\)\s+As\s+(?!Variant)\w+", src))
arr = [(i + 1, m.group(1)) for i, l in enumerate(lines) for m in [re.match(r"\s*(\w+)\s*=\s*Array\(", l)] if m]
print("2) Array() -> arreglo tipado:", [a for a in arr if a[1].lower() in typed] or "ninguno",
      "| asignaciones Array():", len(arr))

# 3) Identificadores no declarados (analisis aproximado por procedimiento)
code = re.sub(r'"[^"\n]*"', '""', src)
code = "\n".join(l.split("'")[0] for l in code.splitlines())
code = re.sub(r" _\n", " ", code)
builtin = set("""
and or not xor mod is new nothing true false to step then else elseif end if for next each in do loop while wend until
select case exit sub function dim redim preserve as byval byref optional private public const type set let call on error
goto resume with option explicit long integer double single string boolean variant object date byte currency
range worksheet worksheets workbook chart chartobject series listobject application err me
abs int fix sqr log exp cos sin cdbl clng cstr cint csng ubound lbound len left right mid trim ucase lcase instr replace
format isnumeric isempty isnull iserror vartype chrw chr rgb rnd randomize timer now doevents msgbox iif array
left$ right$ mid$ trim$ ucase$ lcase$ format$ chrw$ chr$
vbinformation vbexclamation vbcritical vbquestion vbyesno vbno vbyes vblf vbcrlf vbstring vbboolean vbbinarycompare vbobjecterror
xlcalculationmanual xlcalculationautomatic xlcontinuous xlcenter xlxyscattersmoothnomarkers xlxyscatterlinesnomarkers
xlcolumnclustered xlbarclustered xlvalue xlcategory xlticklabelpositionlow xllegendpositionbottom xllabelpositionright xlmaximum
shinicio shparam shres shcurva shtornado shrangos shsim attribute vb_name
""".split())
module_names = set()
for m in re.finditer(r"^\s*(?:Private |Public )?(?:Const|Dim)\s+(.+)$", code[:code.lower().find("\nprivate sub") if False else len(code)], re.M):
    pass
head = "\n".join(code.splitlines()[:first_proc])
for m in re.finditer(r"^\s*(?:Private|Public|Dim)\s+(?:Const\s+)?(\w+)", head, re.M | re.I):
    module_names.add(m.group(1).lower())
for m in re.finditer(r"^\s*(?:Private |Public )?Type (\w+)", head, re.M | re.I):
    module_names.add(m.group(1).lower())
procs = {m.group(3).lower() for m in proc_re.finditer(code)} | set(re.findall(r"(?im)^\s*(?:Private |Public )?(?:Sub|Function) (\w+)", code))
procs = {p.lower() for p in procs}
problems = []
blocks = re.split(r"(?im)^(?=[ \t]*(?:Public |Private )?(?:Sub|Function) )", code)
for b in blocks[1:]:
    mm = proc_re.match(b)
    if not mm:
        print("bloque no reconocido:", b[:60]); continue
    name = mm.group(3)
    body = b[:re.search(r"(?im)^\s*End (Sub|Function)", b).end()]
    local = set()
    sig = body.lstrip("\n").split("\n", 1)[0]
    for m in re.finditer(r"(?:ByVal |ByRef |Optional )*(\w+)(?:\(\))?\s+As\b", sig):
        local.add(m.group(1).lower())
    for m in re.finditer(r"(?im)^\s*Dim\s+(.+)$", body):
        for part in m.group(1).split(","):
            local.add(re.match(r"\s*(\w+)", part).group(1).lower())
    labels = set(x.lower() for x in re.findall(r"(?m)^(\w+):\s*$", body))
    rest = body[len(sig):]
    for m in re.finditer(r"(?<![\.\w])([A-Za-z_]\w*\$?)", rest):
        w = m.group(1).lower()
        if w in builtin or w in local or w in module_names or w in procs or w in labels or w == name.lower():
            continue
        after = rest[m.end():m.end() + 2]
        if after.startswith(":="):  # argumento con nombre
            continue
        problems.append((name, m.group(1)))
print("3) Identificadores sin declarar:", sorted(set(problems)) or "ninguno")
