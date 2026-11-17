"""Rebase strong clips on a draggable contact handle without changing initial poses."""
import json
from pathlib import Path

ROOT = Path(__file__).parent
ANCHOR = (.14, -.03, .08)
data = json.loads((ROOT/'output_strong/All_3_Strong_HeadRelative.json').read_text())
for clip in data['Clips']:
    clip['AnimationName'] += '_Adjustable'
    for track in clip['Controllers']:
        track['Parent'] = {'Atom': 'SlapReference_Person2', 'Rigidbody': 'control'}
        for axis, offset in zip(('X', 'Y', 'Z'), ANCHOR):
            for key in track[axis]:
                before = float(key['v'])
                key['v'] = str(round(before-offset, 6))
                assert abs(float(key['v'])+offset-before) < 1e-6
        for axis in ('Y','Z','RotX','RotY','RotZ','RotW'):
            assert [k['t'] for k in track[axis]] == [k['t'] for k in track['X']]
out = ROOT/'output_adjustable'
out.mkdir(exist_ok=True)
for name, clips in [('All_3_Adjustable_Reference', data['Clips'])] + [(c['AnimationName'], [c]) for c in data['Clips']]:
    path = out/(name+'.json')
    path.write_text(json.dumps(dict(data, Clips=clips), indent=2)+'\n', encoding='utf-8')
    print(path)
