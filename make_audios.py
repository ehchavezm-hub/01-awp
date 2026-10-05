#!/usr/bin/env python3
"""
make_audios.py — Genera los audios MP3 por lámina usando edge-tts (voz Alex, Microsoft Azure).

Requisitos:
  pip install edge-tts

Uso:
  python make_audios.py

Resultado:
  Carpeta  audios/  con archivos  slide_001.mp3, slide_002.mp3, ...
  Archivo  audios/textos.txt  con el texto narrado por lámina (para revisión).
"""

# ════════════════════════════════════════════════════════════════
#  CONFIGURACIÓN
# ════════════════════════════════════════════════════════════════

PPTX_PATH   = "Constructabilidad_CII_V10.pptx"   # debe estar en la misma carpeta
OUT_DIR     = "audios"                             # carpeta de salida

# Voz masculina peruana (Alex de Microsoft Azure vía Edge TTS)
VOICE       = "es-PE-AlexNeural"

# Velocidad: "-10%" más lento, "0%" normal, "+10%" más rápido
RATE        = "-5%"

# Rango de láminas (None = todas)
SLIDE_START = None   # ej. 1
SLIDE_END   = None   # ej. 10

# ════════════════════════════════════════════════════════════════

import asyncio, os, re, sys, xml.etree.ElementTree as ET, zipfile
from pathlib import Path


# ── Extracción de texto ──────────────────────────────────────────

def extract_slide_text(slide_xml_bytes: bytes) -> str:
    try:
        root = ET.fromstring(slide_xml_bytes)
    except ET.ParseError:
        return ""

    shapes = []
    NS_P = '{http://schemas.openxmlformats.org/presentationml/2006/main}'
    NS_A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
    for sp in root.iter(NS_P + 'sp'):
        off = sp.find('.//' + NS_A + 'off')
        y = int(off.get('y', '0')) if off is not None else 0
        x = int(off.get('x', '0')) if off is not None else 0
        para_texts = []
        for para in sp.iter(NS_A + 'p'):
            runs = ''.join(r.text or '' for r in para.iter(NS_A + 't'))
            if runs.strip():
                para_texts.append(runs.strip())
        if para_texts:
            shapes.append((y, x, '\n'.join(para_texts)))

    shapes.sort(key=lambda s: (s[0], s[1]))
    parts, seen = [], set()
    for _, _, txt in shapes:
        for line in txt.split('\n'):
            line = line.strip()
            if (not line or len(line) <= 2 or line.isdigit()
                    or re.match(r'^[\d\.\-\—\–]+$', line)
                    or line in seen):
                continue
            line = line.replace('&quot;', '"').replace('&amp;', 'y')
            seen.add(line)
            parts.append(line)
    return '.  '.join(parts)


def load_notes(notes_xml_bytes: bytes) -> str:
    try:
        root = ET.fromstring(notes_xml_bytes)
        NS_A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
        texts = [t.text.strip() for t in root.iter(NS_A + 't')
                 if t.text and t.text.strip()]
        return ' '.join(texts)
    except Exception:
        return ""


def get_slide_texts(pptx_path: str) -> list:
    results = []
    with zipfile.ZipFile(pptx_path) as z:
        slide_files = sorted(
            [n for n in z.namelist() if re.match(r'ppt/slides/slide\d+\.xml$', n)],
            key=lambda n: int(re.search(r'\d+', n).group()))
        for sfile in slide_files:
            snum = int(re.search(r'\d+', sfile).group())
            notes_path = sfile.replace('slides/slide', 'notesSlides/notesSlide')
            if notes_path in z.namelist():
                notes = load_notes(z.read(notes_path))
                if len(notes) > 20:
                    results.append((snum, notes))
                    continue
            results.append((snum, extract_slide_text(z.read(sfile))))
    return results


# ── Síntesis con edge-tts ────────────────────────────────────────

async def _synth(text: str, out_mp3: str, voice: str, rate: str):
    try:
        import edge_tts
    except ImportError:
        sys.exit("Instala edge-tts:  pip install edge-tts")
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(out_mp3)


def synth(text: str, out_mp3: str, voice: str, rate: str) -> bool:
    try:
        asyncio.run(_synth(text, out_mp3, voice, rate))
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


# ── Main ─────────────────────────────────────────────────────────

def main():
    if not Path(PPTX_PATH).exists():
        sys.exit(f"No se encontró: {PPTX_PATH}")

    os.makedirs(OUT_DIR, exist_ok=True)

    print(f"Leyendo láminas de {PPTX_PATH}...")
    all_texts = get_slide_texts(PPTX_PATH)

    start = (SLIDE_START or 1) - 1
    end   = SLIDE_END or len(all_texts)
    texts = all_texts[start:end]

    print(f"Generando {len(texts)} audios con voz {VOICE}...\n")

    # Guardar lista de textos para revisión
    log_path = os.path.join(OUT_DIR, "textos.txt")
    with open(log_path, 'w', encoding='utf-8') as log:
        for snum, text in texts:
            log.write(f"=== Lámina {snum} ===\n{text}\n\n")

    ok_count = 0
    for i, (snum, text) in enumerate(texts, 1):
        mp3 = os.path.join(OUT_DIR, f"slide_{snum:03d}.mp3")
        print(f"  [{i}/{len(texts)}] lámina {snum:3d}", end="  ")

        if os.path.exists(mp3):
            print("(ya existe, omitiendo)")
            ok_count += 1
            continue

        if not text.strip():
            # Silencio de 2 s para láminas sin texto
            try:
                import subprocess
                subprocess.run([
                    'ffmpeg', '-y', '-loglevel', 'error',
                    '-f', 'lavfi', '-i', 'anullsrc=r=24000:cl=mono',
                    '-t', '2', '-c:a', 'libmp3lame', '-b:a', '64k', mp3
                ], check=True)
                print("(silencio)")
            except Exception:
                # Sin ffmpeg: crea MP3 vacío de 1 byte (ffmpeg lo manejará en el ensamblado)
                open(mp3, 'wb').close()
                print("(vacío — sin ffmpeg)")
            ok_count += 1
            continue

        ok = synth(text, mp3, VOICE, RATE)
        print("✓" if ok else "✗ (revisa la conexión a Internet)")
        if ok:
            ok_count += 1

    print(f"\n{'='*50}")
    print(f"Audios generados: {ok_count}/{len(texts)}")
    print(f"Carpeta: {os.path.abspath(OUT_DIR)}/")
    print(f"Textos narrados: {log_path}")
    print("\nEnvía la carpeta 'audios/' de vuelta para que ensamble el video.")


if __name__ == "__main__":
    main()
