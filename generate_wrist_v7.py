"""Orient the open palm to the authored sweep in reference-local X/Z."""
import copy
import json
import math
from pathlib import Path
from generate_strong import euler, multiply

ROOT = Path(__file__).parent
ROT = ('RotX', 'RotY', 'RotZ', 'RotW')


def orient(clip, twist):
    hand, = [track for track in clip['Controllers'] if track['Controller'] == 'rHandControl']
    points = [(float(k['t']), float(k['v']), float(z['v'])) for k, z in zip(hand['X'], hand['Z'])]
    previous = None
    for i, (t, _, _) in enumerate(points):
        phase = round(t % 2.1, 3)
        if .69 <= phase <= .94:
            _, x0, z0 = points[i-1]
            _, x1, z1 = points[i+1]
            yaw = math.degrees(math.atan2(z0-z1, x1-x0))
        else:
            # Art-directed entry and recovery; the palm should not flip on reversal.
            yaw = 28 if .28 <= phase <= .58 else -24 if 1.05 <= phase <= 1.3 else 6
        lift = 84 if .58 <= phase <= 1.05 else 72
        q = multiply(euler(0, yaw, lift), euler(twist, 0, 0))
        if previous and sum(a*b for a,b in zip(previous,q)) < 0:
            q = tuple(-v for v in q)
        assert abs(sum(v*v for v in q)-1) < 1e-6
        for axis, value in zip(ROT,q):
            key = hand[axis][i]
            assert float(key['t']) == t
            key['v'] = str(round(value,8))
        previous = q


if __name__ == '__main__':
    source = json.loads((ROOT/'output_open_palm/All_3_FullBody_OpenPalm_V6.json').read_text())
    result = []
    for original in source['Clips']:
        for label, angle in [('A',0), ('B',-30), ('C',30)]:
            clip = copy.deepcopy(original)
            orient(clip, angle)
            clip['AnimationName'] = clip['AnimationName'].replace('OpenPalm_V6', 'Wrist_V7_'+label)
            result.append(clip)
    source['Clips'] = result
    out = ROOT/'output_wrist_v7'
    out.mkdir(exist_ok=True)
    (out/'All_Wrist_V7.json').write_text(json.dumps(source, separators=(',', ':')), encoding='utf-8')
