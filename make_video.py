#!/usr/bin/env python3
"""
make_video.py — Genera video MP4 de la presentación PPTX con voz Azure TTS.

Flujo:
  1. Exporta cada lámina a PNG  (PowerPoint COM en Windows, LibreOffice en otros)
  2. Genera audio WAV por lámina  (Azure TTS voz masculina es-PE)
  3. Combina imagen + audio en clip y concatena todo el video  (ffmpeg)

Requisitos:
  pip install azure-cognitiveservices-speech python-pptx pillow
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

# Azure Speech Service
AZURE_KEY     = "TU_CLAVE_AZURE"    # clave del recurso Azure Speech
AZURE_REGION  = "eastus"             # región, p.ej. "eastus", "westus2", "brazilsouth"

# Voz: masculina peruana.  Otras opciones:
#   Masculino:  "es-PE-AlexNeural"  (Perú)   "es-MX-JorgeNeural"  "es-ES-AlvaroNeural"
#   Femenino:   "es-PE-CamilaNeural"          "es-MX-DaliaNeural"  "es-ES-ElviraNeural"
VOICE_NAME    = "es-PE-AlexNeural"

# Velocidad de la voz  (0.75 = lento, 1.0 = normal, 1.2 = rápido)
SPEECH_RATE   = "0.95"

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

import os, sys, re, subprocess, platform, textwrap
from pathlib import Path
import xml.etree.ElementTree as ET

# ════════════════════════════════════════════════════════════════
#  EXTRACCIÓN DE TEXTO  —  lee directamente el XML del PPTX
# ════════════════════════════════════════════════════════════════

NS = {
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
}

def extract_slide_text(slide_xml_bytes: bytes) -> str:
    """
    Extrae el texto visible de una lámina en orden de lectura (arriba→abajo).
    Devuelve un párrafo listo para narrar.
    """
    # Primero busca notas del orador (si existen las agrega al inicio)
    try:
        root = ET.fromstring(slide_xml_bytes)
    except ET.ParseError:
        return ""

    # Recolectar todas las formas con su posición y texto
    shapes = []
    for sp in root.iter('{http://schemas.openxmlformats.org/presentationml/2006/main}sp'):
        # posición
        off = sp.find('.//{http://schemas.openxmlformats.org/drawingml/2006/main}off')
        y = int(off.get('y', '0')) if off is not None else 0
        x = int(off.get('x', '0')) if off is not None else 0
        # texto
        para_texts = []
        for para in sp.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}p'):
            runs = ''.join(r.text or '' for r in
                           para.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}t'))
            if runs.strip():
                para_texts.append(runs.strip())
        if para_texts:
            shapes.append((y, x, '\n'.join(para_texts)))

    # Ordenar por posición vertical (luego horizontal)
    shapes.sort(key=lambda s: (s[0], s[1]))

    # Construir texto de narración
    parts = []
    seen = set()
    for _, _, txt in shapes:
        for line in txt.split('\n'):
            line = line.strip()
            # Filtrar: números de página, cadenas muy cortas, repetidos
            if (not line or len(line) <= 2 or line.isdigit()
                    or re.match(r'^[\d\.\-\—\–]+$', line)
                    or line in seen):
                continue
            # Limpiar entidades HTML
            line = (line.replace('&quot;', '"').replace('&amp;', 'y')
                    .replace('&lt;', '<').replace('&gt;', '>'))
            seen.add(line)
            parts.append(line)

    return '.  '.join(parts)


def load_notes(notes_xml_bytes: bytes) -> str:
    """Extrae texto de notas del orador si el archivo existe."""
    try:
        root = ET.fromstring(notes_xml_bytes)
        texts = []
        for t in root.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}t'):
            if t.text and t.text.strip():
                texts.append(t.text.strip())
        return ' '.join(texts)
    except Exception:
        return ""


def get_slide_texts(pptx_path: str) -> list[tuple[int, str]]:
    """Devuelve lista de (slide_num, texto_narracion) para todas las láminas."""
    import zipfile
    results = []
    with zipfile.ZipFile(pptx_path) as z:
        slide_files = sorted(
            [n for n in z.namelist() if re.match(r'ppt/slides/slide\d+\.xml$', n)],
            key=lambda n: int(re.search(r'\d+', n).group()))
        for sfile in slide_files:
            snum = int(re.search(r'\d+', sfile).group())
            xml_bytes = z.read(sfile)

            # Prefer speaker notes if available
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
                          width: int = 1920, height: int = 1080) -> list[str]:
    """Exporta láminas a PNG usando PowerPoint COM (Windows)."""
    import comtypes.client
    pptx_abs = str(Path(pptx_path).resolve())
    out_abs   = str(Path(out_dir).resolve())
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


def export_slides_libreoffice(pptx_path: str, out_dir: str) -> list[str]:
    """Exporta a PNG vía LibreOffice (macOS/Linux/Windows alternativo)."""
    import glob
    pptx_abs = str(Path(pptx_path).resolve())
    out_abs   = str(Path(out_dir).resolve())
    subprocess.run([
        "soffice", "--headless", "--convert-to", "png",
        "--outdir", out_abs, pptx_abs
    ], check=True)
    # LibreOffice exporta sólo la primera página del PPTX a PNG con este método.
    # Para múltiples láminas hay que exportar a PDF primero y luego a imágenes.
    pdf_path = os.path.join(out_abs, Path(pptx_path).stem + ".pdf")
    subprocess.run([
        "soffice", "--headless", "--convert-to", "pdf",
        "--outdir", out_abs, pptx_abs
    ], check=True)
    # Convertir PDF → PNG (requiere poppler/pdftoppm o ImageMagick)
    subprocess.run([
        "pdftoppm", "-r", "150", "-png", pdf_path,
        os.path.join(out_abs, "slide")
    ], check=True)
    paths = sorted(glob.glob(os.path.join(out_abs, "slide*.png")))
    return paths


def export_slides(pptx_path: str, out_dir: str) -> list[str]:
    os.makedirs(out_dir, exist_ok=True)
    system = platform.system()
    if system == "Windows":
        try:
            return export_slides_windows(pptx_path, out_dir, SLIDE_WIDTH, SLIDE_HEIGHT)
        except ImportError:
            print("  comtypes no disponible, usando LibreOffice...")
    return export_slides_libreoffice(pptx_path, out_dir)


# ════════════════════════════════════════════════════════════════
#  SÍNTESIS DE VOZ  —  Azure TTS
# ════════════════════════════════════════════════════════════════

def text_to_wav(text: str, out_wav: str, voice: str = VOICE_NAME,
                key: str = AZURE_KEY, region: str = AZURE_REGION,
                rate: str = SPEECH_RATE) -> bool:
    """Convierte texto a WAV con Azure TTS. Retorna True si tuvo éxito."""
    try:
        import azure.cognitiveservices.speech as speechsdk
    except ImportError:
        sys.exit("Instala el SDK: pip install azure-cognitiveservices-speech")

    # SSML para control de voz y velocidad
    ssml = textwrap.dedent(f"""\
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"
               xml:lang="es-PE">
          <voice name="{voice}">
            <prosody rate="{rate}">
              {text}
            </prosody>
          </voice>
        </speak>""")

    cfg    = speechsdk.SpeechConfig(subscription=key, region=region)
    audio  = speechsdk.audio.AudioOutputConfig(filename=out_wav)
    synth  = speechsdk.SpeechSynthesizer(speech_config=cfg, audio_config=audio)
    result = synth.speak_ssml_async(ssml).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        return True
    elif result.reason == speechsdk.ResultReason.Canceled:
        details = result.cancellation_details
        print(f"\n  ✗ Azure TTS error (lámina): {details.reason} — {details.error_details}")
        return False
    return False


def generate_audio_files(texts: list[tuple[int, str]], out_dir: str) -> list[tuple[int, str]]:
    """Genera WAV por lámina. Devuelve lista (snum, wav_path)."""
    os.makedirs(out_dir, exist_ok=True)
    results = []
    total = len(texts)
    for i, (snum, text) in enumerate(texts, 1):
        wav = os.path.join(out_dir, f"slide_{snum:03d}.wav")
        print(f"  TTS {i}/{total}: lámina {snum}", end=' ')
        if os.path.exists(wav):
            print("(caché)")
        elif not text.strip():
            # Lámina sin texto: generar silencio de 2s
            _make_silence(wav, duration=2.0)
            print("(silencio)")
        else:
            ok = text_to_wav(text, wav)
            print("✓" if ok else "✗")
            if not ok:
                _make_silence(wav, duration=2.0)
        results.append((snum, wav))
    return results


def _make_silence(out_wav: str, duration: float = 2.0, sample_rate: int = 16000):
    """Genera un archivo WAV de silencio."""
    import struct, wave
    n_samples = int(sample_rate * duration)
    with wave.open(out_wav, 'w') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sample_rate)
        wf.writeframes(struct.pack('<' + 'h' * n_samples, *([0] * n_samples)))


# ════════════════════════════════════════════════════════════════
#  CONSTRUCCIÓN DEL VIDEO  —  ffmpeg
# ════════════════════════════════════════════════════════════════

def get_audio_duration(wav_path: str) -> float:
    """Obtiene duración de audio con ffprobe."""
    r = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'default=noprint_wrappers=1:nokey=1', wav_path],
        capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 2.0


def image_audio_to_clip(img_path: str, wav_path: str,
                        out_mp4: str, pause: float = PAUSE_SECONDS):
    """Combina una imagen y un audio en un clip MP4."""
    duration = get_audio_duration(wav_path) + pause
    subprocess.run([
        'ffmpeg', '-y', '-loglevel', 'error',
        '-loop', '1', '-framerate', '1', '-i', img_path,
        '-i', wav_path,
        '-c:v', 'libx264', '-preset', 'fast', '-tune', 'stillimage',
        '-c:a', 'aac', '-b:a', '128k',
        '-pix_fmt', 'yuv420p',
        '-t', f'{duration:.3f}',
        out_mp4
    ], check=True)


def build_video(images: list[str], audios: list[tuple[int, str]],
                clips_dir: str, output: str):
    """
    Genera un clip MP4 por lámina y luego los concatena en el video final.
    images: lista de rutas PNG ordenada por lámina.
    audios: lista (snum, wav_path) ordenada.
    """
    os.makedirs(clips_dir, exist_ok=True)
    clip_paths = []
    total = min(len(images), len(audios))

    print(f"\n[3/3] Generando {total} clips de video...")
    for i, (img, (snum, wav)) in enumerate(zip(images, audios), 1):
        clip = os.path.join(clips_dir, f"clip_{i:03d}.mp4")
        if not os.path.exists(clip):
            print(f"  Clip {i}/{total}", end='\r')
            image_audio_to_clip(img, wav, clip)
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
    start = (SLIDE_START or 1) - 1
    end   = SLIDE_END or len(images)
    images = images[start:end]

    # ── 2. Extraer texto y generar audio ──────────────────────────
    print("\n[2/3] Generando audio con Azure TTS...")
    all_texts = get_slide_texts(pptx)
    slide_texts = all_texts[start:end]

    if AZURE_KEY == "TU_CLAVE_AZURE":
        print("  ⚠  AZURE_KEY no configurada — se generarán silencios en lugar de voz.")
        print("     Edita AZURE_KEY en la sección CONFIGURACIÓN del script.")
        audios = []
        for snum, _ in slide_texts:
            wav = os.path.join(audio_dir, f"slide_{snum:03d}.wav")
            os.makedirs(audio_dir, exist_ok=True)
            _make_silence(wav, 3.0)
            audios.append((snum, wav))
    else:
        audios = generate_audio_files(slide_texts, audio_dir)

    # ── 3. Construir video ────────────────────────────────────────
    build_video(images, audios, clips_dir, OUTPUT_VIDEO)

    size_mb = Path(OUTPUT_VIDEO).stat().st_size / (1024 * 1024)
    print(f"\n✓ Video generado: {OUTPUT_VIDEO}  ({size_mb:.1f} MB)")
    print(f"  Láminas: {len(images)}  |  Duración estimada: ~{sum(get_audio_duration(a) for _, a in audios)/60:.1f} min")


if __name__ == "__main__":
    main()
