"""Generate readable Timeline 287 import files (serialization version 283)."""
import argparse
import json
from pathlib import Path


# time, local displacement from reference point (metres), curve type.
# Flat tangents stop at poses; linear contact keys avoid spline overshoot.
DESIGNS = {
    '01_Soft_Tap': [
        (0, .16, -.04, .06, 1), (.35, .20, -.02, .08, 1),
        (.65, .02, 0, 0, 2), (.73, 0, 0, 0, 1),
        (.88, .045, .005, .015, 1), (1.45, .16, -.04, .06, 1),
        (1.8, .16, -.04, .06, 1)],
    '02_Wide_Sweep': [
        (0, .16, -.04, .06, 1), (.45, .29, .07, .04, 1),
        (.64, .16, .06, .02, 2), (.79, .025, .008, 0, 2),
        (.84, 0, 0, 0, 1), (1.02, .075, -.015, .02, 1),
        (1.65, .16, -.04, .06, 1), (2.1, .16, -.04, .06, 1)],
    '03_Double_Tap': [
        (0, .16, -.04, .06, 1), (.28, .20, .01, .04, 1),
        (.47, .02, 0, 0, 2), (.52, 0, 0, 0, 1),
        (.70, .12, .015, .03, 1), (.86, .02, 0, 0, 2),
        (.91, 0, 0, 0, 1), (1.12, .10, -.01, .035, 1),
        (1.65, .16, -.04, .06, 1), (2.0, .16, -.04, .06, 1)],
}


def make_clip(name, frames, atom, anchor, scale):
    track = {'Controller': 'rHandControl', 'TargetsPosition': '1',
             'TargetsRotation': '1', 'ControlPosition': '1',
             'ControlRotation': '0', 'Weight': '1',
             'Parent': {'Atom': atom, 'Rigidbody': 'head'}}
    for axis, key in enumerate(('X', 'Y', 'Z')):
        track[key] = [{'t': str(f[0]), 'v': str(round(anchor[axis] + scale * f[axis+1], 6)),
                       'c': str(f[4])} for f in frames]
    for key, value in [('RotX', 0), ('RotY', 0), ('RotZ', 0), ('RotW', 1)]:
        track[key] = [{'t': str(f[0]), 'v': str(value), 'c': str(f[4])} for f in frames]
    return {'AnimationName': name, 'AnimationLayer': 'HeadRelativeTap',
            'AnimationLength': str(frames[-1][0]), 'BlendDuration': '0.3',
            'Loop': '0', 'AutoPlay': '0', 'Speed': '1', 'Weight': '1',
            'EnsureQuaternionContinuity': '1', 'Controllers': [track],
            'FloatParams': [], 'Triggers': []}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--atom', required=True, help='Exact UID of the person whose head is the parent (required; no assumed scene name)')
    parser.add_argument('--anchor', nargs=3, type=float, default=[.14, -.03, .08], metavar=('X', 'Y', 'Z'))
    parser.add_argument('--scale', type=float, default=1)
    parser.add_argument('--output', type=Path, default=Path(__file__).parent / 'output')
    args = parser.parse_args()
    if not args.atom.strip():
        parser.error('--atom must not be empty')
    if args.scale <= 0:
        parser.error('--scale must be positive')
    args.output.mkdir(parents=True, exist_ok=True)
    clips = [make_clip(n, f, args.atom, args.anchor, args.scale) for n, f in DESIGNS.items()]
    for name, selected in [('All_3_HeadRelative_Taps', clips)] + [(c['AnimationName'], [c]) for c in clips]:
        payload = {'SerializeVersion': 283, 'AtomType': 'Person', 'Clips': selected}
        path = args.output / (name + '.json')
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        loaded = json.loads(path.read_text(encoding='utf-8'))
        for clip in loaded['Clips']:
            for track in clip['Controllers']:
                for key in ('X', 'Y', 'Z', 'RotX', 'RotY', 'RotZ', 'RotW'):
                    times = [float(k['t']) for k in track[key]]
                    assert times[0] == 0 and times[-1] == float(clip['AnimationLength'])
                    assert all(a < b for a, b in zip(times, times[1:]))
                    assert times == [float(k['t']) for k in track['X']], 'Position/rotation key times must match'
        print(path)


if __name__ == '__main__':
    main()
