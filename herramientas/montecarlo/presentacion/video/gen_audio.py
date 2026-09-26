import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tts import gen
D = os.path.dirname(os.path.abspath(__file__))
os.makedirs(D + '/audio', exist_ok=True)
tot = 0
for n in json.load(open(D + '/narracion.json')):
    out = D + '/audio/%02d.wav' % n['lamina']
    d = gen(n['texto'], out, speed=1.0)
    tot += d
    print(n['lamina'], round(d, 1), flush=True)
print('TOTAL min', round(tot / 60, 1))
