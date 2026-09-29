# Video explicativo: Implementar AWP

Video narrado en español latinoamericano que recorre las 122 láminas de `presentacion/implementacion_awp.pptx`.

## Archivos

| Archivo | Contenido |
|---|---|
| `implementacion_awp.mp4` | Video 1920 × 1080 (54 MB) con narración, subtítulos en español (pista opcional) y capítulos por módulo. |
| `implementacion_awp_720p.mp4` | Versión ligera 1280 × 720 (27 MB), con audio mono; para enviar por correo o chat. |
| `implementacion_awp.srt` | Subtítulos sincronizados por frase, para subirlos aparte (por ejemplo, a YouTube o a una plataforma de capacitación). |
| `guion_a.py`, `guion_b.py` | Guion de narración de cada lámina (1–60 y 61–122). Es el lugar para corregir o ajustar lo que dice la voz. |
| `pronunciacion.py` | Cómo debe leer la voz las siglas (AWP → "a doble u pe") y los términos en inglés (Workface Planning → "uórkfeis plánin"). Solo afecta al audio. |
| `generar_video.py` | Genera el video completo. |

## Cómo se produjo

- **Voz:** modelo neuronal Piper `es_MX-claude-high` (español de México), ejecutado localmente con sherpa-onnx; no usa servicios en la nube.
- **Láminas:** se renderizan desde el `.pptx` con LibreOffice a 1920 × 1080.
- **Narración:** cada frase se sintetiza por separado, lo que permite sincronizar los subtítulos con la voz. Velocidad: 0,9 (unas 160 palabras por minuto).
- **Audio:** normalizado a −16 LUFS, AAC 128 kb/s.
- **Verificación:** se transcribieron muestras del audio con Whisper (local) para comprobar que las siglas y los términos en inglés se entienden, y se revisó que cada lámina aparezca en pantalla mientras suena su narración.

## Cómo regenerarlo

```bash
pip install sherpa-onnx soundfile numpy
# Voz (≈65 MB):
curl -LO https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-es_MX-claude-high.tar.bz2
tar xjf vits-piper-es_MX-claude-high.tar.bz2
# Requiere además ffmpeg, LibreOffice (Impress) y pdftoppm (poppler-utils).
python presentacion/video/generar_video.py --voz ./vits-piper-es_MX-claude-high
```

Opciones: `--velocidad 0.85` (más lento), `--laminas 59-74` (solo un tramo, útil para probar cambios).
Si cambia la presentación, regenere primero el `.pptx` con `presentacion/generar_presentacion.py`.
