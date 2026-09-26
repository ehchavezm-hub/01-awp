import sherpa_onnx, soundfile as sf, sys, numpy as np
D='sherpa-onnx-whisper-small/'
r=sherpa_onnx.OfflineRecognizer.from_whisper(encoder=D+'small-encoder.int8.onnx',decoder=D+'small-decoder.int8.onnx',tokens=D+'small-tokens.txt',language='es',task='transcribe',num_threads=4)
for f in sys.argv[1:]:
    a,sr=sf.read(f,dtype='float32')
    import math
    # whisper: 30 s ventanas
    out=[]
    step=sr*28
    for i in range(0,len(a),step):
        s=r.create_stream(); s.accept_waveform(sr,a[i:i+step]); r.decode_stream(s); out.append(s.result.text)
    print(f, '::', ' '.join(out)); print()
