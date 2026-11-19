"""Author a ready-to-import right palm on the existing full-body V4 clips."""
import argparse
import json
import math
from pathlib import Path

from generate_strong import euler


# Relaxed / open. Positive bend is deliberately graded toward the little finger.
HAND = {
    'Fingers Fist': (0, 0), 'Fingers Grasp': (0, 0), 'Fingers Squeeze': (0, 0),
    'Thumb Fist': (0, 0), 'Thumb Grasp': (0, 0),
    'Fingers Straighten': (.04, .18), 'Fingers In-Out': (.07, .12),
    'Index Finger Bend': (.10, .035), 'Mid Finger Bend': (.14, .055),
    'Ring Finger Bend': (.19, .085), 'Pinky Finger Bend': (.24, .12),
    'Thumb In-Out': (.14, .22), 'Thumb Bend': (.13, .08),
    'Thumb Straighten': (.03, .07),
}


def pose(clip):
    hand, = [c for c in clip['Controllers'] if c['Controller'] == 'rHandControl']
    curves = [hand[key] for key in ('RotX', 'RotY', 'RotZ', 'RotW')]
    names = {'Right '+key for key in HAND}
    clip['FloatParams'] = [p for p in clip['FloatParams']
                           if not (p['Storable'] == 'geometry' and p['Name'] in names)]
    tracks = {}
    for name in HAND:
        tracks[name] = []
        clip['FloatParams'].append(dict(Storable='geometry', Name='Right '+name, Value=tracks[name]))
    for i, key in enumerate(hand['X']):
        t = float(key['t']) % 2.1
        opening = min(max((t-.25)/.47, 0), 1) * min(max((1.65-t)/.60, 0), 1)
        opening *= opening*(3-2*opening)
        # Skeleton finger chains extend along +X and flex toward -Y.
        # Positive Z roll lifts the fingertips and turns the palm toward local +X.
        yaw = 10 - 18*math.exp(-((t-.98)/.19)**2)
        q = euler(-5 + 5*opening, yaw, 68 + 16*opening)
        assert abs(sum(v*v for v in q)-1) < 1e-6
        for curve, value in zip(curves, q):
            assert curve[i]['t'] == key['t']
            curve[i]['v'] = str(round(value, 8))
        for name, (relaxed, spread) in HAND.items():
            tracks[name].append(dict(t=key['t'], v=str(round(relaxed+(spread-relaxed)*opening, 5)), c='1'))
    clip['AnimationName'] = clip['AnimationName'].replace('PalmSweep_V4', 'OpenPalm_V6')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    data = json.loads(args.source.read_text(encoding='utf-8-sig'))
    for clip in data['Clips']:
        pose(clip)
        print(clip['AnimationName'], len(clip['Controllers']), len(clip['FloatParams']))
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
