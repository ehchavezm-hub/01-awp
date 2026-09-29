"""Genera el video explicativo (MP4 1080p) de la presentación AWP con narración en español latinoamericano.

Pasos:
  1. Renderiza las 122 láminas de implementacion_awp.pptx a PNG 1920x1080 (LibreOffice + pdftoppm).
  2. Sintetiza la narración de cada lámina, frase por frase, con una voz neuronal Piper es_MX
     ejecutada localmente con sherpa-onnx (sin servicios en la nube).
  3. Arma el audio, los subtítulos (SRT) sincronizados por frase y los capítulos por módulo.
  4. Codifica el MP4 (H.264 + AAC) con subtítulos incrustados como pista opcional.

Uso:
  python presentacion/video/generar_video.py [--voz DIR_MODELO] [--velocidad 0.9] [--laminas 1-10]

Requisitos: sherpa-onnx, soundfile, numpy, ffmpeg, LibreOffice, pdftoppm y un modelo Piper
en formato sherpa-onnx, por ejemplo:
  https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-es_MX-claude-high.tar.bz2
"""
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from guion_a import GUION_A  # noqa: E402
from guion_b import GUION_B  # noqa: E402
from pronunciacion import pronunciar  # noqa: E402

GUION = {**GUION_A, **GUION_B}
PPTX = AQUI.parent / "implementacion_awp.pptx"
SALIDA = AQUI / "implementacion_awp.mp4"
SRT = AQUI / "implementacion_awp.srt"
TRABAJO = Path(os.environ.get("AWP_VIDEO_TMP", "/tmp/awp_video"))

# Primera lámina de cada capítulo (portada y separadores de módulo).
CAPITULOS = [
    (1, "Apertura"), (5, "1. Por qué AWP"), (13, "2. Qué es AWP"), (25, "3. Preparar la organización"),
    (35, "4. Fase 1: Planificación preliminar"), (47, "5. Fase 2: Ingeniería y compras"),
    (59, "6. Fase 3: Construcción y Workface Planning"), (75, "7. Fase 4: Puesta en marcha"),
    (80, "8. Información y tecnología"), (87, "9. Roles y organización"), (96, "10. Medición"),
    (103, "11. Escalar y adoptar"), (111, "12. Errores y lecciones"), (119, "13. Hoja de ruta"),
]
SEPARADORES = {n for n, _ in CAPITULOS if n > 1}

PAUSA_FRASE = 0.35      # silencio entre frases (s)
ENTRADA = 0.6           # silencio al inicio de cada lámina
SALIDA_LAMINA = 0.9     # silencio al final de cada lámina
SALIDA_SEPARADOR = 1.6  # los separadores se sostienen un poco más


def frases(texto):
    """Divide en frases para sintetizar y subtitular."""
    partes = re.split(r"(?<=[.!?])\s+", texto.strip())
    return [p for p in partes if p]


def trozos_subtitulo(frase, maximo=90):
    """Parte frases largas en trozos legibles (por comas o punto y coma), sin dejar colas cortas."""
    if len(frase) <= maximo:
        return [frase]
    piezas = re.split(r"(?<=[,;:])\s+", frase)
    salida, actual = [], ""
    for p in piezas:
        if actual and len(actual) + len(p) + 1 > maximo:
            salida.append(actual)
            actual = p
        else:
            actual = f"{actual} {p}".strip()
    if actual:
        salida.append(actual)
    # Une trozos muy cortos con el vecino si el resultado sigue siendo legible.
    i = 0
    while i < len(salida):
        if len(salida[i]) < 32 and len(salida) > 1:
            j = i - 1 if i > 0 else i + 1
            a, b = sorted((i, j))
            unido = f"{salida[a]} {salida[b]}"
            if len(unido) <= 120:
                salida[a:b + 1] = [unido]
                i = 0
                continue
        i += 1
    return salida


def hms(t):
    h, r = divmod(t, 3600)
    m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s - int(s)) * 1000)) % 1000:03d}"


def renderizar_laminas(destino):
    destino.mkdir(parents=True, exist_ok=True)
    pdf = destino / "laminas.pdf"
    if not pdf.exists():
        perfil = f"file://{TRABAJO}/lo_perfil"
        subprocess.run(["soffice", f"-env:UserInstallation={perfil}", "--headless", "--convert-to", "pdf",
                        "--outdir", str(destino), str(PPTX)], check=True, capture_output=True)
        (destino / (PPTX.stem + ".pdf")).rename(pdf)
    if not glob.glob(str(destino / "l-*.png")):
        subprocess.run(["pdftoppm", "-png", "-scale-to-x", "1920", "-scale-to-y", "1080", str(pdf),
                        str(destino / "l")], check=True)
    return sorted(glob.glob(str(destino / "l-*.png")))


def motor_voz(dir_modelo):
    import sherpa_onnx
    onnx = glob.glob(os.path.join(dir_modelo, "*.onnx"))[0]
    cfg = sherpa_onnx.OfflineTtsConfig(
        model=sherpa_onnx.OfflineTtsModelConfig(
            vits=sherpa_onnx.OfflineTtsVitsModelConfig(
                model=onnx, tokens=os.path.join(dir_modelo, "tokens.txt"),
                data_dir=os.path.join(dir_modelo, "espeak-ng-data")),
            num_threads=4))
    return sherpa_onnx.OfflineTts(cfg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voz", default=os.environ.get("AWP_VOZ", "/tmp/claude-0/tts/vits-piper-es_MX-claude-high"))
    ap.add_argument("--velocidad", type=float, default=0.9)
    ap.add_argument("--laminas", default="1-122")
    args = ap.parse_args()
    a, b = (int(x) for x in args.laminas.split("-"))
    numeros = list(range(a, b + 1))
    assert set(GUION) == set(range(1, 123)), "El guion debe cubrir las 122 láminas"

    TRABAJO.mkdir(parents=True, exist_ok=True)
    pngs = renderizar_laminas(TRABAJO / "img")
    assert len(pngs) == 122, f"Se esperaban 122 láminas y hay {len(pngs)}"

    tts = motor_voz(args.voz)
    sr = tts.sample_rate
    silencio = lambda s: np.zeros(int(s * sr), dtype=np.float32)  # noqa: E731

    pistas, subtitulos, duraciones = [], [], []
    t = 0.0
    for n in numeros:
        bloque = [silencio(ENTRADA)]
        t_lamina = t + ENTRADA
        for i, fr in enumerate(frases(GUION[n])):
            audio = tts.generate(pronunciar(fr), sid=0, speed=args.velocidad)
            voz = np.asarray(audio.samples, dtype=np.float32)
            dur = len(voz) / sr
            # Subtítulos: reparte la duración de la frase entre sus trozos según su largo.
            trozos = trozos_subtitulo(fr)
            total = sum(len(x) for x in trozos)
            t0 = t_lamina
            for tr in trozos:
                d = dur * len(tr) / total
                subtitulos.append((t0, t0 + d, tr))
                t0 += d
            bloque.append(voz)
            t_lamina += dur
            if i < len(frases(GUION[n])) - 1:
                bloque.append(silencio(PAUSA_FRASE))
                t_lamina += PAUSA_FRASE
        cola = SALIDA_SEPARADOR if n in SEPARADORES else SALIDA_LAMINA
        bloque.append(silencio(cola))
        audio_lamina = np.concatenate(bloque)
        # Duración en múltiplos de 1/25 s para que audio e imagen no se desfasen.
        fotogramas = int(np.ceil(len(audio_lamina) / sr * 25))
        audio_lamina = np.pad(audio_lamina, (0, fotogramas * sr // 25 - len(audio_lamina)))
        pistas.append(audio_lamina)
        duraciones.append(len(audio_lamina) / sr)
        t += duraciones[-1]
        print(f"lámina {n:3d}: {duraciones[-1]:5.1f} s", flush=True)

    audio = np.concatenate(pistas)
    wav = TRABAJO / "narracion.wav"
    sf.write(wav, audio, sr)

    # Subtítulos SRT.
    with open(SRT, "w", encoding="utf-8") as f:
        for i, (ini, fin, txt) in enumerate(subtitulos, 1):
            f.write(f"{i}\n{hms(ini)} --> {hms(fin)}\n{txt}\n\n")

    # Lista de imágenes con su duración (demuxer concat).
    lista = TRABAJO / "imagenes.txt"
    with open(lista, "w") as f:
        for n, d in zip(numeros, duraciones):
            f.write(f"file '{pngs[n - 1]}'\nduration {d:.3f}\n")
        f.write(f"file '{pngs[numeros[-1] - 1]}'\n")

    # Capítulos (metadatos FFMETADATA).
    inicio = {}
    acum = 0.0
    for n, d in zip(numeros, duraciones):
        inicio[n] = acum
        acum += d
    meta = TRABAJO / "capitulos.txt"
    caps = [(inicio[n], nombre) for n, nombre in CAPITULOS if n in inicio]
    with open(meta, "w", encoding="utf-8") as f:
        f.write(";FFMETADATA1\ntitle=Implementar AWP: guía práctica fase por fase\nlanguage=spa\n")
        for k, (ini, nombre) in enumerate(caps):
            fin = caps[k + 1][0] if k + 1 < len(caps) else acum
            f.write(f"\n[CHAPTER]\nTIMEBASE=1/1000\nSTART={int(ini * 1000)}\nEND={int(fin * 1000)}\ntitle={nombre}\n")

    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "concat", "-safe", "0", "-i", str(lista),
           "-i", str(wav), "-i", str(SRT), "-i", str(meta),
           "-map", "0:v", "-map", "1:a", "-map", "2:s", "-map_metadata", "3", "-map_chapters", "3",
           "-vf", "fps=25,format=yuv420p", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-tune", "stillimage", "-g", "250",
           "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "128k", "-ar", "48000",
           "-c:s", "mov_text", "-metadata:s:s:0", "language=spa", "-metadata:s:a:0", "language=spa",
           "-movflags", "+faststart", str(SALIDA)]
    subprocess.run(cmd, check=True)
    print(json.dumps({"video": str(SALIDA), "duracion_min": round(acum / 60, 1), "laminas": len(numeros),
                      "subtitulos": len(subtitulos)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
