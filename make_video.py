#!/usr/bin/env python3
"""
make_video.py — Genera video MP4 de la presentación PPTX con voz gratuita.

Usa edge-tts (Microsoft Edge TTS — sin API key, misma calidad que Azure Neural).

Flujo:
  1. Exporta cada lámina a PNG  (PowerPoint COM en Windows, LibreOffice en otros)
  2. Genera audio MP3 por lámina  (edge-tts voz masculina es-PE-AlexNeural)
  3. Combina imagen + audio en clip y concatena todo el video  (ffmpeg)

Requisitos:
  pip install edge-tts
  ffmpeg en PATH  (https://ffmpeg.org/download.html)
  PowerPoint instalado (Windows) — o LibreOffice como alternativa

Uso:
  python make_video.py
"""

# ════════════════════════════════════════════════════════════════
#  CONFIGURACIÓN  —  edita aquí antes de correr
# ════════════════════════════════════════════════════════════════

PPTX_PATH     = "Constructabilidad_CII_V10.pptx"  # ruta al archivo PPTX
OUTPUT_VIDEO  = "Constructabilidad_CII.mp4"        # video final

# Voz: masculina peruana.  Lista completa: edge-tts --list-voices | grep es-
#   Masculino:  "es-PE-AlexNeural"   (Perú)
#               "es-MX-JorgeNeural"  (México)
#               "es-ES-AlvaroNeural" (España)
#   Femenino:   "es-PE-CamilaNeural" (Perú)
VOICE_NAME    = "es-PE-AlexNeural"

# Velocidad de la voz  (-20% = más lento, 0% = normal, +20% = más rápido)
SPEECH_RATE   = "-5%"

# Pausa entre láminas en el video (segundos)
PAUSE_SECONDS = 0.8

# Resolución de exportación de láminas
SLIDE_WIDTH   = 1920
SLIDE_HEIGHT  = 1080

# Rango de láminas a procesar (None = todas)
SLIDE_START   = None   # ej. 1
SLIDE_END     = None   # ej. 10

# ════════════════════════════════════════════════════════════════
#  IMPORTS
# ════════════════════════════════════════════════════════════════

import asyncio
import os
import re
import struct
import subprocess
import sys
import wave
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


# ════════════════════════════════════════════════════════════════
#  EXTRACCIÓN DE TEXTO  —  lee directamente el XML del PPTX
# ════════════════════════════════════════════════════════════════

def extract_slide_text(slide_xml_bytes: bytes) -> str:
    """Extrae texto visible de una lámina en orden de lectura (arriba→abajo)."""
    try:
        root = ET.fromstring(slide_xml_bytes)
    except ET.ParseError:
        return ""

    shapes = []
    for sp in root.iter('{http://schemas.openxmlformats.org/presentationml/2006/main}sp'):
        off = sp.find('.//{http://schemas.openxmlformats.org/drawingml/2006/main}off')
        y = int(off.get('y', '0')) if off is not None else 0
        x = int(off.get('x', '0')) if off is not None else 0
        para_texts = []
        for para in sp.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}p'):
            runs = ''.join(
                r.text or '' for r in
                para.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}t'))
            if runs.strip():
                para_texts.append(runs.strip())
        if para_texts:
            shapes.append((y, x, '\n'.join(para_texts)))

    shapes.sort(key=lambda s: (s[0], s[1]))

    parts = []
    seen = set()
    for _, _, txt in shapes:
        for line in txt.split('\n'):
            line = line.strip()
            if (not line or len(line) <= 2 or line.isdigit()
                    or re.match(r'^[\d\.\-\—\–]+$', line)
                    or line in seen):
                continue
            line = (line.replace('&quot;', '"').replace('&amp;', 'y')
                    .replace('&lt;', '<').replace('&gt;', '>'))
            seen.add(line)
            parts.append(line)

    return '.  '.join(parts)


def load_notes(notes_xml_bytes: bytes) -> str:
    """Extrae texto de notas del orador."""
    try:
        root = ET.fromstring(notes_xml_bytes)
        texts = []
        for t in root.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}t'):
            if t.text and t.text.strip():
                texts.append(t.text.strip())
        return ' '.join(texts)
    except Exception:
        return ""


def get_slide_texts(pptx_path: str) -> list:
    """Devuelve lista de (slide_num, texto_narracion) para todas las láminas."""
    results = []
    with zipfile.ZipFile(pptx_path) as z:
        slide_files = sorted(
            [n for n in z.namelist() if re.match(r'ppt/slides/slide\d+\.xml$', n)],
            key=lambda n: int(re.search(r'\d+', n).group()))
        for sfile in slide_files:
            snum = int(re.search(r'\d+', sfile).group())
            xml_bytes = z.read(sfile)

            notes_path = sfile.replace('slides/slide', 'notesSlides/notesSlide')
            if notes_path in z.namelist():
                notes_text = load_notes(z.read(notes_path))
                if len(notes_text) > 20:
                    results.append((snum, notes_text))
                    continue

            text = extract_slide_text(xml_bytes)
            results.append((snum, text))
    return results


# ════════════════════════════════════════════════════════════════
#  EXPORTAR LÁMINAS A PNG
# ════════════════════════════════════════════════════════════════

def export_slides_windows(pptx_path: str, out_dir: str,
                          width: int = 1920, height: int = 1080) -> list:
    """Exporta láminas a PNG usando PowerPoint COM (Windows)."""
    import comtypes.client
    pptx_abs = str(Path(pptx_path).resolve())
    out_abs  = str(Path(out_dir).resolve())
    ppt = comtypes.client.CreateObject("PowerPoint.Application")
    ppt.Visible = True
    prs = ppt.Presentations.Open(pptx_abs, ReadOnly=True)
    paths = []
    for i, slide in enumerate(prs.Slides, start=1):
        img = os.path.join(out_abs, f"slide_{i:03d}.png")
        slide.Export(img, "PNG", width, height)
        paths.append(img)
        print(f"  Exportada lámina {i}/{prs.Slides.Count}", end='\r')
    prs.Close()
    ppt.Quit()
    print()
    return sorted(paths)


def export_slides_libreoffice(pptx_path: str, out_dir: str) -> list:
    """Exporta a PNG vía LibreOffice (macOS/Linux)."""
    import glob
    pptx_abs = str(Path(pptx_path).resolve())
    out_abs  = str(Path(out_dir).resolve())
    pdf_path = os.path.join(out_abs, Path(pptx_path).stem + ".pdf")
    subprocess.run([
        "soffice", "--headless", "--convert-to", "pdf",
        "--outdir", out_abs, pptx_abs
    ], check=True)
    subprocess.run([
        "pdftoppm", "-r", "150", "-png", pdf_path,
        os.path.join(out_abs, "slide")
    ], check=True)
    paths = sorted(glob.glob(os.path.join(out_abs, "slide*.png")))
    return paths


def export_slides(pptx_path: str, out_dir: str) -> list:
    os.makedirs(out_dir, exist_ok=True)
    import platform
    if platform.system() == "Windows":
        try:
            return export_slides_windows(pptx_path, out_dir, SLIDE_WIDTH, SLIDE_HEIGHT)
        except ImportError:
            print("  comtypes no disponible, usando LibreOffice...")
    return export_slides_libreoffice(pptx_path, out_dir)


# ════════════════════════════════════════════════════════════════
#  SÍNTESIS DE VOZ  —  edge-tts (sin API key)
# ════════════════════════════════════════════════════════════════

async def _synthesize_edge(text: str, out_mp3: str,
                            voice: str, rate: str) -> bool:
    """Llama a edge-tts y guarda en out_mp3. Retorna True si tuvo éxito."""
    try:
        import edge_tts
    except ImportError:
        sys.exit("Instala edge-tts:  pip install edge-tts")
    try:
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        await communicate.save(out_mp3)
        return True
    except Exception as e:
        print(f"\n  ✗ edge-tts error: {e}")
        return False


def text_to_mp3(text: str, out_mp3: str,
                voice: str = VOICE_NAME, rate: str = SPEECH_RATE) -> bool:
    """Versión síncrona de _synthesize_edge."""
    return asyncio.run(_synthesize_edge(text, out_mp3, voice, rate))


def _make_silence_mp3(out_mp3: str, duration: float = 2.0):
    """Genera un MP3 de silencio vía ffmpeg."""
    subprocess.run([
        'ffmpeg', '-y', '-loglevel', 'error',
        '-f', 'lavfi', '-i', f'anullsrc=r=24000:cl=mono',
        '-t', str(duration),
        '-c:a', 'libmp3lame', '-b:a', '64k',
        out_mp3
    ], check=True)


def generate_audio_files(texts: list, out_dir: str) -> list:
    """Genera MP3 por lámina. Devuelve lista (snum, mp3_path)."""
    os.makedirs(out_dir, exist_ok=True)
    results = []
    total = len(texts)
    for i, (snum, text) in enumerate(texts, 1):
        mp3 = os.path.join(out_dir, f"slide_{snum:03d}.mp3")
        print(f"  TTS {i}/{total}: lámina {snum}", end=' ')
        if os.path.exists(mp3):
            print("(caché)")
        elif not text.strip():
            _make_silence_mp3(mp3, duration=2.0)
            print("(silencio)")
        else:
            ok = text_to_mp3(text, mp3)
            print("✓" if ok else "✗")
            if not ok:
                _make_silence_mp3(mp3, duration=2.0)
        results.append((snum, mp3))
    return results


# ════════════════════════════════════════════════════════════════
#  CONSTRUCCIÓN DEL VIDEO  —  ffmpeg
# ════════════════════════════════════════════════════════════════

def get_audio_duration(audio_path: str) -> float:
    """Obtiene duración de audio con ffprobe."""
    r = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'default=noprint_wrappers=1:nokey=1', audio_path],
        capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 2.0


def image_audio_to_clip(img_path: str, audio_path: str,
                        out_mp4: str, pause: float = PAUSE_SECONDS):
    """Combina una imagen y un audio en un clip MP4."""
    duration = get_audio_duration(audio_path) + pause
    subprocess.run([
        'ffmpeg', '-y', '-loglevel', 'error',
        '-loop', '1', '-framerate', '1', '-i', img_path,
        '-i', audio_path,
        '-c:v', 'libx264', '-preset', 'fast', '-tune', 'stillimage',
        '-c:a', 'aac', '-b:a', '128k',
        '-pix_fmt', 'yuv420p',
        '-t', f'{duration:.3f}',
        out_mp4
    ], check=True)


def build_video(images: list, audios: list, clips_dir: str, output: str):
    """
    Genera un clip MP4 por lámina y luego los concatena en el video final.
    images: lista de rutas PNG ordenada por lámina.
    audios: lista (snum, mp3_path) ordenada.
    """
    os.makedirs(clips_dir, exist_ok=True)
    clip_paths = []
    total = min(len(images), len(audios))

    print(f"\n[3/3] Generando {total} clips de video...")
    for i, (img, (snum, audio)) in enumerate(zip(images, audios), 1):
        clip = os.path.join(clips_dir, f"clip_{i:03d}.mp4")
        if not os.path.exists(clip):
            print(f"  Clip {i}/{total}", end='\r')
            image_audio_to_clip(img, audio, clip)
        clip_paths.append(clip)
    print()

    print(f"Concatenando {len(clip_paths)} clips → {output}")
    list_txt = os.path.join(clips_dir, "concat_list.txt")
    with open(list_txt, 'w', encoding='utf-8') as f:
        for p in clip_paths:
            f.write(f"file '{Path(p).resolve()}'\n")

    subprocess.run([
        'ffmpeg', '-y', '-loglevel', 'info',
        '-f', 'concat', '-safe', '0',
        '-i', list_txt,
        '-c:v', 'libx264', '-crf', '22', '-preset', 'medium',
        '-c:a', 'aac', '-b:a', '128k',
        output
    ], check=True)


# ════════════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════════════

def main():
    pptx = PPTX_PATH
    if not Path(pptx).exists():
        sys.exit(f"No se encontró: {pptx}")

    base_dir  = Path(pptx).stem + "_video_assets"
    imgs_dir  = os.path.join(base_dir, "images")
    audio_dir = os.path.join(base_dir, "audio")
    clips_dir = os.path.join(base_dir, "clips")

    # ── Verificar ffmpeg ──────────────────────────────────────────
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        sys.exit("ffmpeg no encontrado. Descarga desde https://ffmpeg.org/download.html")

    # ── 1. Exportar láminas a PNG ─────────────────────────────────
    print("[1/3] Exportando láminas a PNG...")
    images = export_slides(pptx, imgs_dir)
    if not images:
        sys.exit("No se generaron imágenes de láminas.")
    print(f"  {len(images)} imágenes exportadas")

    # ── Filtrar rango si se definió ───────────────────────────────
    start  = (SLIDE_START or 1) - 1
    end    = SLIDE_END or len(images)
    images = images[start:end]

    # ── 2. Extraer texto y generar audio ──────────────────────────
    print(f"\n[2/3] Generando audio con edge-tts ({VOICE_NAME})...")
    all_texts   = get_slide_texts(pptx)
    slide_texts = all_texts[start:end]
    audios      = generate_audio_files(slide_texts, audio_dir)

    # ── 3. Construir video ────────────────────────────────────────
    build_video(images, audios, clips_dir, OUTPUT_VIDEO)

    size_mb = Path(OUTPUT_VIDEO).stat().st_size / (1024 * 1024)
    total_dur = sum(get_audio_duration(a) for _, a in audios)
    print(f"\n✓ Video generado: {OUTPUT_VIDEO}  ({size_mb:.1f} MB)")
    print(f"  Láminas: {len(images)}  |  Duración: ~{total_dur/60:.1f} min")


if __name__ == "__main__":
    main()
