#!/usr/bin/env python3
"""
assemble_video.py — Exporta láminas a PNG y ensambla el video final.

Prerequisitos:
  - Windows con PowerPoint instalado
  - pip install comtypes pillow
  - ffmpeg en PATH  (https://ffmpeg.org/download.html)
  - Carpeta audios/ con slide_001.mp3 ... slide_126.mp3

Uso:
  Pon este script en la misma carpeta que:
    Constructabilidad_CII_V10.pptx
    audios/  (con todos los MP3)
  Luego ejecuta:
    python assemble_video.py
"""

# ════════════════════════════════════════════════════════════════
#  CONFIGURACIÓN
# ════════════════════════════════════════════════════════════════

PPTX_PATH    = "Constructabilidad_CII_V10.pptx"
AUDIO_DIR    = "audios"
OUTPUT_VIDEO = "Constructabilidad_CII.mp4"

# Resolución de exportación (1920×1080 = Full HD)
SLIDE_WIDTH  = 1920
SLIDE_HEIGHT = 1080

# Pausa entre láminas (segundos)
PAUSE        = 0.8

# ════════════════════════════════════════════════════════════════

import os, re, subprocess, sys
from pathlib import Path


def find_ffmpeg() -> str:
    """Busca ffmpeg: primero en la carpeta del script, luego en PATH."""
    local = Path(__file__).parent / "ffmpeg.exe"
    if local.exists():
        return str(local)
    local2 = Path(__file__).parent / "ffmpeg"
    if local2.exists():
        return str(local2)
    return "ffmpeg"  # confía en el PATH


FFMPEG = find_ffmpeg()


def check_ffmpeg():
    try:
        subprocess.run([FFMPEG, '-version'], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        sys.exit(
            "❌ ffmpeg no encontrado.\n"
            "   Descarga ffmpeg-release-essentials.zip desde https://www.gyan.dev/ffmpeg/builds/\n"
            "   Extrae y copia ffmpeg.exe a la misma carpeta que este script."
        )


def export_slides_ppt(pptx_path: str, out_dir: str,
                      width: int, height: int) -> list:
    """Exporta cada lámina a PNG usando PowerPoint COM."""
    try:
        import comtypes.client
    except ImportError:
        sys.exit("❌ Instala comtypes:  pip install comtypes")

    pptx_abs = str(Path(pptx_path).resolve())
    out_abs  = str(Path(out_dir).resolve())
    os.makedirs(out_abs, exist_ok=True)

    print("  Abriendo PowerPoint...")
    ppt = comtypes.client.CreateObject("PowerPoint.Application")
    ppt.Visible = True
    # WithWindow=True evita el error "could not open the file" en modo protegido
    prs = ppt.Presentations.Open(pptx_abs, ReadOnly=True, WithWindow=True)
    total = prs.Slides.Count
    paths = []
    for i in range(1, total + 1):
        img = os.path.join(out_abs, f"slide_{i:03d}.png")
        if not os.path.exists(img):
            prs.Slides(i).Export(img, "PNG", width, height)
        paths.append(img)
        print(f"  Exportando lámina {i}/{total}", end='\r')
    prs.Close()
    ppt.Quit()
    print(f"\n  {total} láminas exportadas.")
    return sorted(paths)


def get_duration(audio_path: str) -> float:
    """Obtiene duración con ffmpeg (no necesita ffprobe separado)."""
    r = subprocess.run(
        [FFMPEG, '-i', audio_path],
        capture_output=True, text=True)
    # ffmpeg escribe la duración en stderr: "Duration: HH:MM:SS.ss"
    import re
    m = re.search(r'Duration:\s*(\d+):(\d+):([\d.]+)', r.stderr)
    if m:
        h, mn, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
        return h * 3600 + mn * 60 + s
    return 3.0


def make_clip(img: str, audio: str, out_mp4: str, pause: float):
    duration = get_duration(audio) + pause
    subprocess.run([
        FFMPEG, '-y', '-loglevel', 'error',
        '-loop', '1', '-framerate', '1', '-i', img,
        '-i', audio,
        '-c:v', 'libx264', '-preset', 'fast', '-tune', 'stillimage',
        '-c:a', 'aac', '-b:a', '128k',
        '-pix_fmt', 'yuv420p',
        '-t', f'{duration:.3f}',
        out_mp4
    ], check=True)


def main():
    check_ffmpeg()

    if not Path(PPTX_PATH).exists():
        sys.exit(f"❌ No se encontró: {PPTX_PATH}")
    if not Path(AUDIO_DIR).exists():
        sys.exit(f"❌ No se encontró la carpeta: {AUDIO_DIR}/")

    # Buscar audios disponibles
    audio_files = sorted(Path(AUDIO_DIR).glob("slide_*.mp3"))
    if not audio_files:
        sys.exit(f"❌ No hay archivos slide_NNN.mp3 en {AUDIO_DIR}/")
    print(f"Audios encontrados: {len(audio_files)}")

    # Exportar láminas
    imgs_dir  = "video_images"
    clips_dir = "video_clips"
    print("\n[1/3] Exportando láminas a PNG con PowerPoint...")
    images = export_slides_ppt(PPTX_PATH, imgs_dir, SLIDE_WIDTH, SLIDE_HEIGHT)

    # Emparejar imágenes con audios
    pairs = []
    for audio_path in audio_files:
        snum = int(re.search(r'(\d+)', audio_path.stem).group(1))
        img_path = os.path.join(imgs_dir, f"slide_{snum:03d}.png")
        if os.path.exists(img_path):
            pairs.append((img_path, str(audio_path), snum))
        else:
            print(f"  ⚠  Sin imagen para lámina {snum}, omitiendo")

    print(f"\n[2/3] Generando {len(pairs)} clips de video...")
    os.makedirs(clips_dir, exist_ok=True)
    clip_paths = []
    for i, (img, audio, snum) in enumerate(pairs, 1):
        clip = os.path.join(clips_dir, f"clip_{snum:03d}.mp4")
        if not os.path.exists(clip):
            print(f"  Clip {i}/{len(pairs)} (lámina {snum})", end='\r')
            make_clip(img, audio, clip, PAUSE)
        clip_paths.append(clip)
    print()

    print(f"[3/3] Concatenando {len(clip_paths)} clips → {OUTPUT_VIDEO}")
    list_txt = os.path.join(clips_dir, "concat.txt")
    with open(list_txt, 'w', encoding='utf-8') as f:
        for p in clip_paths:
            f.write(f"file '{Path(p).resolve()}'\n")

    subprocess.run([
        FFMPEG, '-y', '-loglevel', 'warning',
        '-f', 'concat', '-safe', '0',
        '-i', list_txt,
        '-c:v', 'libx264', '-crf', '22', '-preset', 'medium',
        '-c:a', 'aac', '-b:a', '128k',
        OUTPUT_VIDEO
    ], check=True)

    size_mb = Path(OUTPUT_VIDEO).stat().st_size / 1024 / 1024
    total_s  = sum(get_duration(a) for _, a, _ in pairs)
    print(f"\n✅ Video listo: {OUTPUT_VIDEO}")
    print(f"   Láminas: {len(pairs)}  |  Duración: {total_s/60:.1f} min  |  Tamaño: {size_mb:.0f} MB")


if __name__ == "__main__":
    main()
