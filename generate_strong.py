"""Head-relative strong slap studies with wrist rotation and open-hand morphs."""
import argparse
import json
import math
from pathlib import Path
from generate import make_clip


def multiply(a, b):
    x, y, z, w = a
    X, Y, Z, W = b
    return (w*X+x*W+y*Z-z*Y, w*Y-x*Z+y*W+z*X,
            w*Z+x*Y-y*X+z*W, w*W-x*X-y*Y-z*Z)


def euler(x, y, z):
    # Unity Quaternion.Euler: Z then X then Y.
    x, y, z = [math.radians(v)/2 for v in (x, y, z)]
    return multiply(multiply((0, math.sin(y), 0, math.cos(y)),
                             (math.sin(x), 0, 0, math.cos(x))),
                    (0, 0, math.sin(z), math.cos(z)))


# time, offset X/Y/Z, curve type, wrist angle offset.
# Contact remains at the original configurable reference point.
SWEEP = [
    (0, .18, -.12, .10, 1, -12),
    (.40, .37, .08, .05, 1, -32),
    (.62, .39, .10, .02, 1, -38),
    (.74, .22, .06, .01, 2, -20),
    (.82, .045, .01, 0, 2, -4),
    (.85, 0, 0, 0, 2, 0),
    (.90, -.015, -.015, .035, 1, 8),
    (1.08, .10, -.045, .08, 1, -8),
    (1.70, .18, -.12, .10, 1, -12),
    (2.1, .18, -.12, .10, 1, -12),
]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--atom', required=True)
    p.add_argument('--anchor', nargs=3, type=float, default=[.14, -.03, .08])
    p.add_argument('--palm-euler', nargs=3, type=float, default=[0, 0, 90],
                   help='Contact wrist orientation in head-local Unity Euler degrees; calibrate in scene')
    p.add_argument('--output', type=Path, default=Path(__file__).parent/'output_strong')
    a = p.parse_args()
    if not a.atom.strip():
        p.error('Atom UID cannot be empty')
    downward = [(t, x*.8, y + .22*(x/.39), z, c, angle)
                for t,x,y,z,c,angle in SWEEP]
    double = SWEEP[:8] + [(round(t+1.08, 3), x,y,z,c,ang) for t,x,y,z,c,ang in SWEEP[1:]]
    clips = []
    for name, frames in [('04_Strong_Sweep', SWEEP),
                         ('05_Strong_Diagonal', downward),
                         ('06_Strong_Double', double)]:
        clip = make_clip(name, [f[:5] for f in frames], a.atom, a.anchor, 1)
        clip['AnimationLayer'] = 'HeadRelativeTap'
        track = clip['Controllers'][0]
        track['ControlRotation'] = '1'
        quats = [euler(a.palm_euler[0], a.palm_euler[1]+f[5], a.palm_euler[2]) for f in frames]
        for i in range(1, len(quats)):
            if sum(x*y for x,y in zip(quats[i-1], quats[i])) < 0:
                quats[i] = tuple(-v for v in quats[i])
        for i, key in enumerate(['RotX','RotY','RotZ','RotW']):
            track[key] = [{'t': str(f[0]), 'v': str(round(q[i], 8)), 'c': str(f[4])}
                          for f,q in zip(frames, quats)]
        # Reset grasp/fist and spreading morphs to their neutral open-hand pose.
        clip['FloatParams'] = [
            {'Storable': 'geometry', 'Name': name,
             'Value': [{'t': str(f[0]), 'v': '0', 'c': '1'} for f in frames]}
            for name in ['Right Fingers Fist', 'Right Fingers Grasp',
                         'Right Fingers In-Out', 'Right Thumb In-Out']]
        for key in ['Y','Z','RotX','RotY','RotZ','RotW']:
            assert [k['t'] for k in track[key]] == [k['t'] for k in track['X']]
        assert all(f[0] < g[0] for f,g in zip(frames, frames[1:]))
        assert all(abs(sum(v*v for v in q)-1)<1e-6 for q in quats)
        clips.append(clip)
    a.output.mkdir(parents=True, exist_ok=True)
    for name, selected in [('All_3_Strong_HeadRelative', clips)] + [(c['AnimationName'], [c]) for c in clips]:
        path = a.output/(name+'.json')
        path.write_text(json.dumps({'SerializeVersion':283, 'AtomType':'Person', 'Clips':selected}, indent=2)+'\n', encoding='utf-8')
        json.loads(path.read_text(encoding='utf-8'))
        print(path)


if __name__ == '__main__':
    main()
