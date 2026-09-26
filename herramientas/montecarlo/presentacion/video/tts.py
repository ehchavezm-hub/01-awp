import sherpa_onnx, soundfile as sf, sys, json, re, os
D=os.path.dirname(os.path.abspath(__file__))+'/vits-piper-es_MX-claude-high'
cfg=sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(vits=sherpa_onnx.OfflineTtsVitsModelConfig(
  model=D+'/es_MX-claude-high.onnx', tokens=D+'/tokens.txt', data_dir=D+'/espeak-ng-data'), num_threads=4), max_num_sentences=1)
tts=sherpa_onnx.OfflineTts(cfg)
def norm(t):
    reps=[('PMI','pe eme i'),('VME','ve eme e'),('TRIGEN','tríyen'),('PERT','pert'),('Vose','Vos'),('Gumbel','Gúmbel'),('Weibull','Wáibul'),
          ('R cero cinco','erre cero cinco'),('submittals','submítals'),('NCR','ene ce erre'),('pe uno','pe uno')]
    for a,b in reps: t=re.sub(r'\b'+a+r'\b',b,t)
    return t
def gen(texto,out,speed=1.0):
    a=tts.generate(norm(texto),sid=0,speed=speed)
    sf.write(out,a.samples,a.sample_rate)
    return len(a.samples)/a.sample_rate
if __name__=='__main__':
    print(gen(sys.argv[1],sys.argv[2]))
