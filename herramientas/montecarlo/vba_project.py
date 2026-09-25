"""Genera un vbaProject.bin (MS-OVBA dentro de un Compound File Binary) a partir
de codigo fuente VBA en texto.

El proyecto se escribe SIN cache de p-code (_VBA_PROJECT version 0xFFFF y
MODULEOFFSET = 0), tal como permite la especificacion MS-OVBA: Excel compila el
codigo fuente al abrir el libro. Por eso el mismo archivo funciona en Excel de
32 y 64 bits y en cualquier idioma.
"""

import struct
import uuid

CODEPAGE = "cp1252"

DOC_ATTRS = {
    "workbook": "0{00020819-0000-0000-C000-000000000046}",
    "worksheet": "0{00020820-0000-0000-C000-000000000046}",
}


# ---------------------------------------------------------------------------
# Compresion MS-OVBA (2.4.1)
# ---------------------------------------------------------------------------

def _compress_chunk(chunk: bytes) -> bytes:
    out = bytearray()
    pos = 0
    n = len(chunk)
    heads = {}  # prefijo de 3 bytes -> lista de posiciones
    while pos < n:
        flag_pos = len(out)
        out.append(0)
        flags = 0
        for bit in range(8):
            if pos >= n:
                break
            bitcount = 4
            while (1 << bitcount) < pos:
                bitcount += 1
            max_len = (0xFFFF >> bitcount) + 3
            best_len, best_off = 0, 0
            if pos + 3 <= n:
                cands = heads.get(chunk[pos:pos + 3], ())
                for cand in reversed(cands[-512:]):
                    ln = 0
                    lim = min(max_len, n - pos)
                    while ln < lim and chunk[cand + ln] == chunk[pos + ln]:
                        ln += 1
                    if ln > best_len:
                        best_len, best_off = ln, pos - cand
                        if ln == lim:
                            break
            if best_len >= 3:
                token = ((best_off - 1) << (16 - bitcount)) | (best_len - 3)
                out += struct.pack("<H", token)
                flags |= 1 << bit
                step = best_len
            else:
                out.append(chunk[pos])
                step = 1
            for p in range(pos, pos + step):
                if p + 3 <= n:
                    heads.setdefault(chunk[p:p + 3], []).append(p)
            pos += step
        out[flag_pos] = flags
    return bytes(out)


def compress(data: bytes) -> bytes:
    out = bytearray(b"\x01")
    for start in range(0, max(len(data), 1), 4096):
        chunk = data[start:start + 4096]
        body = _compress_chunk(chunk)
        if len(body) > 4094:
            if len(chunk) != 4096:
                raise ValueError("bloque no comprimible")
            out += struct.pack("<H", 0x3FFF & 0x0FFF | 0x3000) + chunk  # sin comprimir
            continue
        header = (len(body) + 2 - 3) | 0x3000 | 0x8000
        out += struct.pack("<H", header) + body
    return bytes(out)


# ---------------------------------------------------------------------------
# Registros del stream "dir" (2.3.4.2)
# ---------------------------------------------------------------------------

def _rec(rid: int, data: bytes) -> bytes:
    return struct.pack("<HI", rid, len(data)) + data


def _u16(s: str) -> bytes:
    return s.encode("utf-16-le")


def _mb(s: str) -> bytes:
    return s.encode(CODEPAGE)


def _dir_stream(modules):
    d = bytearray()
    d += _rec(0x01, struct.pack("<I", 1))            # PROJECTSYSKIND: Win32
    d += _rec(0x4A, struct.pack("<I", 2))            # PROJECTCOMPATVERSION
    d += _rec(0x02, struct.pack("<I", 0x0409))       # PROJECTLCID
    d += _rec(0x14, struct.pack("<I", 0x0409))       # PROJECTLCIDINVOKE
    d += _rec(0x03, struct.pack("<H", 1252))         # PROJECTCODEPAGE
    d += _rec(0x04, _mb("VBAProject"))               # PROJECTNAME
    d += _rec(0x05, b"") + _rec(0x40, b"")           # PROJECTDOCSTRING
    d += _rec(0x06, b"") + _rec(0x3D, b"")           # PROJECTHELPFILEPATH
    d += _rec(0x07, struct.pack("<I", 0))            # PROJECTHELPCONTEXT
    d += _rec(0x08, struct.pack("<I", 0))            # PROJECTLIBFLAGS
    d += struct.pack("<HIIH", 0x09, 4, 1, 0)         # PROJECTVERSION
    d += _rec(0x0C, b"") + _rec(0x3C, b"")           # PROJECTCONSTANTS
    # Referencias: stdole y Office
    refs = [
        ("stdole", "*\\G{00020430-0000-0000-C000-000000000046}#2.0#0#"
                   "C:\\Windows\\System32\\stdole2.tlb#OLE Automation"),
        ("Office", "*\\G{2DF8D04C-5BFA-101B-BDE5-00AA0044DE52}#2.0#0#"
                   "C:\\Program Files\\Common Files\\Microsoft Shared\\OFFICE16\\MSO.DLL"
                   "#Microsoft Office 16.0 Object Library"),
    ]
    for name, libid in refs:
        d += _rec(0x16, _mb(name)) + _rec(0x3E, _u16(name))
        lib = _mb(libid)
        body = struct.pack("<I", len(lib)) + lib + struct.pack("<IH", 0, 0)
        d += _rec(0x0D, body)
    d += _rec(0x0F, struct.pack("<H", len(modules)))  # PROJECTMODULES
    d += _rec(0x13, struct.pack("<H", 0xFFFF))        # PROJECTCOOKIE
    for m in modules:
        name = m["name"]
        d += _rec(0x19, _mb(name)) + _rec(0x47, _u16(name))
        d += _rec(0x1A, _mb(name)) + _rec(0x32, _u16(name))
        d += _rec(0x1C, b"") + _rec(0x48, b"")
        d += _rec(0x31, struct.pack("<I", 0))          # MODULEOFFSET: sin p-code
        d += _rec(0x1E, struct.pack("<I", 0))
        d += _rec(0x2C, struct.pack("<H", 0xFFFF))
        d += _rec(0x22 if m["kind"] != "module" else 0x21, b"")
        d += _rec(0x2B, b"")
    d += _rec(0x10, b"")
    return bytes(d)


def _project_stream(modules, project_id):
    lines = ['ID="{%s}"' % project_id]
    for m in modules:
        if m["kind"] == "module":
            lines.append("Module=%s" % m["name"])
        else:
            lines.append("Document=%s/&H00000000" % m["name"])
    lines += [
        'Name="VBAProject"',
        'HelpContextID="0"',
        'VersionCompatible32="393222000"',
        'CMG="7F7DA5285BD8DEDCDEDCDEDCDEDC"',
        'DPB="FEFC24A9DC575A585A585A"',
        'GC="7D7FA72659A45AA45A5B"',
        "",
        "[Host Extender Info]",
        "&H00000001={3832D640-CF90-11CF-8E43-00A0C911005A};VBE;&H00000000",
        "",
        "[Workspace]",
    ]
    for m in modules:
        lines.append("%s=0, 0, 0, 0, C" % m["name"])
    return ("\r\n".join(lines) + "\r\n").encode(CODEPAGE)


def _projectwm_stream(modules):
    out = bytearray()
    for m in modules:
        out += _mb(m["name"]) + b"\x00" + _u16(m["name"]) + b"\x00\x00"
    return bytes(out + b"\x00\x00")


def module_source(name, kind, code=""):
    """Texto completo del modulo (con atributos) listo para almacenar."""
    if kind == "module":
        head = 'Attribute VB_Name = "%s"\r\n' % name
    else:
        head = (
            'Attribute VB_Name = "%s"\r\n'
            'Attribute VB_Base = "%s"\r\n'
            "Attribute VB_GlobalNameSpace = False\r\n"
            "Attribute VB_Creatable = False\r\n"
            "Attribute VB_PredeclaredId = True\r\n"
            "Attribute VB_Exposed = True\r\n"
            "Attribute VB_TemplateDerived = False\r\n"
            "Attribute VB_Customizable = True\r\n" % (name, DOC_ATTRS[kind])
        )
    code = code.replace("\r\n", "\n").replace("\n", "\r\n")
    return (head + code).encode(CODEPAGE)


# ---------------------------------------------------------------------------
# Compound File Binary (MS-CFB, version 3, sectores de 512 bytes)
# ---------------------------------------------------------------------------

FREESECT, ENDOFCHAIN, FATSECT, NOSTREAM = 0xFFFFFFFF, 0xFFFFFFFE, 0xFFFFFFFD, 0xFFFFFFFF
SECTOR, MINI, CUTOFF = 512, 64, 4096


class _Entry:
    def __init__(self, name, kind, data=b""):
        self.name, self.kind, self.data = name, kind, data  # kind: 5 root, 1 storage, 2 stream
        self.children = []
        self.left = self.right = self.child = NOSTREAM
        self.color = 1
        self.start = ENDOFCHAIN
        self.size = 0
        self.sid = None


def _cfb_key(e):
    return (len(e.name), e.name.upper())


def _build_tree(children, depth=0, info=None):
    """Arbol binario balanceado; nodos del nivel mas profundo en rojo."""
    if not children:
        return None
    mid = len(children) // 2
    node = children[mid]
    node._depth = depth
    info.append(node)
    node._l = _build_tree(children[:mid], depth + 1, info)
    node._r = _build_tree(children[mid + 1:], depth + 1, info)
    return node


def _black_height(n):
    if n is None:
        return 1
    lh, rh = _black_height(n._l), _black_height(n._r)
    assert lh == rh, "arbol rojo-negro invalido"
    if n.color == 0:
        assert (n._l is None or n._l.color == 1) and (n._r is None or n._r.color == 1)
    return lh + (1 if n.color == 1 else 0)


def build_cfb(root_children):
    """root_children: lista de ('nombre', bytes) o ('nombre', [hijos]) (storage)."""
    entries = []
    root = _Entry("Root Entry", 5)
    entries.append(root)

    def add(parent, spec):
        name, content = spec
        if isinstance(content, list):
            e = _Entry(name, 1)
            for c in content:
                add(e, c)
        else:
            e = _Entry(name, 2, content)
        parent.children.append(e)
        entries.append(e)

    for spec in root_children:
        add(root, spec)
    for i, e in enumerate(entries):
        e.sid = i

    for e in entries:
        if e.kind in (1, 5) and e.children:
            kids = sorted(e.children, key=_cfb_key)
            info = []
            top = _build_tree(kids, 0, info)
            maxd = max(n._depth for n in info)
            for n in info:
                n.color = 1
            if len(info) > 1:
                for n in info:
                    if n._depth == maxd and n._depth > 0:
                        n.color = 0
            top.color = 1
            _black_height(top)
            for n in info:
                n.left = n._l.sid if n._l else NOSTREAM
                n.right = n._r.sid if n._r else NOSTREAM
            e.child = top.sid

    streams = [e for e in entries if e.kind == 2]
    mini_data = bytearray()
    minifat = []
    big = []
    for e in streams:
        e.size = len(e.data)
        if e.size < CUTOFF:
            first = len(mini_data) // MINI
            nsec = max(1, -(-e.size // MINI)) if e.size else 0
            if nsec:
                e.start = first
                for k in range(nsec):
                    minifat.append(first + k + 1 if k < nsec - 1 else ENDOFCHAIN)
                mini_data += e.data + b"\x00" * (nsec * MINI - e.size)
            else:
                e.start = ENDOFCHAIN
        else:
            big.append(e)

    sectors = []   # contenido de cada sector (512 bytes)
    fat = []

    def alloc(data):
        if not data:
            return ENDOFCHAIN
        n = -(-len(data) // SECTOR)
        first = len(sectors)
        for k in range(n):
            sectors.append(data[k * SECTOR:(k + 1) * SECTOR].ljust(SECTOR, b"\x00"))
            fat.append(first + k + 1 if k < n - 1 else ENDOFCHAIN)
        return first

    root.start = alloc(bytes(mini_data))
    root.size = len(mini_data)
    for e in big:
        e.start = alloc(e.data)

    minifat_bytes = b"".join(struct.pack("<I", v) for v in minifat)
    if minifat_bytes:
        pad = (-len(minifat_bytes)) % SECTOR
        minifat_bytes += struct.pack("<I", FREESECT) * (pad // 4)
    first_minifat = alloc(minifat_bytes) if minifat_bytes else ENDOFCHAIN
    n_minifat = len(minifat_bytes) // SECTOR

    dir_bytes = bytearray()
    for e in entries:
        nm = e.name.encode("utf-16-le") + b"\x00\x00"
        assert len(nm) <= 64
        dir_bytes += nm.ljust(64, b"\x00")
        dir_bytes += struct.pack("<HBB", len(nm), e.kind, e.color)
        dir_bytes += struct.pack("<III", e.left, e.right, e.child)
        dir_bytes += b"\x00" * 16 + struct.pack("<I", 0) + b"\x00" * 16
        dir_bytes += struct.pack("<IQ", e.start if e.start is not None else ENDOFCHAIN, e.size)
    while len(dir_bytes) % SECTOR:
        dir_bytes += (b"\x00" * 64 + struct.pack("<HBB", 0, 0, 0) +
                      struct.pack("<III", NOSTREAM, NOSTREAM, NOSTREAM) + b"\x00" * 36 +
                      struct.pack("<IQ", 0, 0))
    first_dir = alloc(bytes(dir_bytes))

    n_other = len(sectors)
    n_fat = 1
    while n_fat * (SECTOR // 4) < n_other + n_fat:
        n_fat += 1
    assert n_fat <= 109
    fat_start = n_other
    fat += [FATSECT] * n_fat
    fat += [FREESECT] * (n_fat * (SECTOR // 4) - len(fat))
    fat_bytes = b"".join(struct.pack("<I", v) for v in fat)
    for k in range(n_fat):
        sectors.append(fat_bytes[k * SECTOR:(k + 1) * SECTOR])

    difat = [fat_start + k for k in range(n_fat)] + [FREESECT] * (109 - n_fat)
    header = bytearray()
    header += bytes.fromhex("D0CF11E0A1B11AE1") + b"\x00" * 16
    header += struct.pack("<HHHHH", 0x003E, 0x0003, 0xFFFE, 9, 6)
    header += b"\x00" * 6
    header += struct.pack("<IIIIIIIII", 0, n_fat, first_dir, 0, CUTOFF,
                          first_minifat, n_minifat, ENDOFCHAIN, 0)
    header += b"".join(struct.pack("<I", v) for v in difat)
    assert len(header) == 512
    return bytes(header) + b"".join(sectors)


def build_vba_project(modules, project_id=None):
    """modules: lista de dicts {name, kind: 'module'|'workbook'|'worksheet', code}."""
    project_id = project_id or str(uuid.uuid4()).upper()
    vba_children = [("_VBA_PROJECT", b"\xCC\x61\xFF\xFF\x00\x00\x00"),
                    ("dir", compress(_dir_stream(modules)))]
    for m in modules:
        src = module_source(m["name"], m["kind"], m.get("code", ""))
        vba_children.append((m["name"], compress(src)))
    return build_cfb([
        ("VBA", vba_children),
        ("PROJECT", _project_stream(modules, project_id)),
        ("PROJECTwm", _projectwm_stream(modules)),
    ])
