"""Replace only the wrist choreography in a pose-baked Timeline bundle."""
import argparse
import json
from pathlib import Path
from generate_strong import euler


# Reference-local wrist poses: seconds, XYZ metres and palm Euler angles.
POSES = [
    (0, -.16, -.17, .16, 18, 18, -55),
    (.28, -.26, -.02, .20, 8, 35, -65),
    (.48, -.36, .14, .16, -12, 56, -75),
    (.58, -.34, .18, .12, -17, 62, -80),
    (.69, -.26, .17, .07, -12, 54, -85),
    (.78, -.14, .10, .025, -6, 32, -90),
    (.85, 0, 0, 0, 0, 0, -90),
    (.94, .16, -.09, .04, 10, -27, -98),
    (1.05, .21, -.115, .10, 17, -39, -103),
    (1.30, .10, -.22, .19, 24, -14, -72),
    (1.65, -.12, -.24, .22, 22, 12, -50),
    (1.85, -.16, -.17, .16, 18, 18, -55),
    (2.10, -.16, -.17, .16, 18, 18, -55),
]


def redraw(clip):
    hand, = [t for t in clip['Controllers'] if t['Controller'] == 'rHandControl']
    keys = ('X', 'Y', 'Z', 'RotX', 'RotY', 'RotZ', 'RotW')
    for key in keys:
        hand[key] = []
    name = clip['AnimationName']
    for cycle in range(2 if 'Double' in name else 1):
        for t, x, y, z, pitch, yaw, roll in POSES:
            if cycle and t == 0:
                continue
            if 'Diagonal' in name:
                y -= .35*x
                x *= .86
            values = (x, y, z, *euler(pitch, yaw, roll))
            for key, value in zip(keys, values):
                hand[key].append(dict(t=str(round(t+cycle*2.1, 3)), v=str(round(value, 8)), c='1' if t in (0, 1.85, 2.1) else '3'))
    assert float(hand['X'][-1]['t']) == float(clip['AnimationLength'])
    clip['AnimationName'] = name.split('_FullBody_V3')[0].split('_V2')[0] + '_PalmSweep_V4'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    data = json.loads(args.source.read_text(encoding='utf-8-sig'))
    for clip in data['Clips']:
        redraw(clip)
        print(clip['AnimationName'], [t['Controller'] for t in clip['Controllers']])
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
