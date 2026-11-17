"""Adjustable right-to-left arc studies; direction corrected from scene feedback."""
import json
import math
from pathlib import Path
from generate import make_clip
from generate_strong import euler

ROOT = Path(__file__).parent
# time, swing angle (radians), angular velocity (radians/sec).
# Continuous Hermite velocity: slow wind-up, accelerating strike, follow-through,
# then a separate slower recovery. No stop or reversal at the contact point.
KNOTS = [(0, -.50, 0), (.42, -1.18, 0), (.56, -1.20, 0),
         (.68, -1.06, 3), (.77, -.65, 7), (.85, 0, 8),
         (.93, .40, 2), (1.04, .48, 0), (1.30, .12, -1.5),
         (1.80, -.50, 0), (2.10, -.50, 0)]


def swing(t):
    for (a, x, v), (b, y, w) in zip(KNOTS, KNOTS[1:]):
        if a <= t <= b:
            d = b-a
            u = (t-a)/d
            return ((2*u**3-3*u*u+1)*x + (u**3-2*u*u+u)*d*v
                    + (-2*u**3+3*u*u)*y + (u**3-u*u)*d*w)
    return KNOTS[-1][1]


def build(name, diagonal=False, double=False):
    frames, quats = [], []
    duration = 4.2 if double else 2.1
    for tick in range(round(duration*100)+1):
        t = tick/100
        local_t = t if t <= 2.1 else t-2.1
        angle = swing(local_t)
        # Corrected side: negative local X wind-up, positive X follow-through.
        x = .40*math.sin(angle)
        z = .40*(1-math.cos(angle))
        y = -.23*x if diagonal else -.08*x
        # Hand lowers away from the contact plane on recovery.
        if 1.04 < local_t < 1.80:
            u = (local_t-1.04)/.76
            y -= .08*math.sin(math.pi*u)**2
            z += .05*math.sin(math.pi*u)**2
        frames.append((t, x, y, z, 2))
        # Palm orientation turns with the arc; a small delayed wrist release
        # peaks after contact rather than preceding the arm swing.
        release = 7*math.exp(-((local_t-.94)/.12)**2)
        quats.append(euler(0, -math.degrees(angle)*.65 + release, -90))
    clip = make_clip(name, frames, 'Person#2', (0,0,0), 1)
    track = clip['Controllers'][0]
    track['Parent'] = {'Atom':'SlapReference_Person2', 'Rigidbody':'control'}
    track['ControlRotation'] = '1'
    for i in range(1, len(quats)):
        if sum(a*b for a,b in zip(quats[i-1], quats[i])) < 0:
            quats[i] = tuple(-v for v in quats[i])
    for axis, key in enumerate(('RotX','RotY','RotZ','RotW')):
        track[key] = [{'t':str(f[0]), 'v':str(round(q[axis],8)), 'c':'2'} for f,q in zip(frames,quats)]
    clip['FloatParams'] = [
        {'Storable':'geometry', 'Name':m,
         'Value':[{'t':'0','v':'0','c':'1'}, {'t':str(duration),'v':'0','c':'1'}]}
        for m in ('Right Fingers Fist','Right Fingers Grasp','Right Fingers In-Out','Right Thumb In-Out')]
    times = [k['t'] for k in track['X']]
    assert all([k['t'] for k in track[key]] == times for key in ('Y','Z','RotX','RotY','RotZ','RotW'))
    assert all(abs(sum(v*v for v in q)-1)<1e-6 for q in quats)
    assert frames[56][1] < 0 < frames[93][1]
    assert abs(frames[85][1])+abs(frames[85][2])+abs(frames[85][3]) < 1e-8
    assert all(frames[i+1][1] > frames[i][1] for i in range(57, 103))
    speed = lambda i: math.sqrt(sum((frames[i+1][j]-frames[i][j])**2 for j in (1,2,3)))*100
    assert speed(84) > 3*speed(60)
    assert all(abs(a-b)<1e-8 for a,b in zip(frames[0][1:4],frames[-1][1:4]))
    print(name, 'keys:', len(frames), 'near-contact speed m/s:', round(speed(84),2))
    return clip


clips = [build('07_RightToLeft_Arc_V2'), build('08_RightToLeft_Diagonal_V2', True),
         build('09_RightToLeft_Double_V2', double=True)]
out = ROOT/'output_arc_v2'
out.mkdir(exist_ok=True)
for name, selected in [('All_3_RightToLeft_Arc_V2', clips)] + [(c['AnimationName'],[c]) for c in clips]:
    path = out/(name+'.json')
    path.write_text(json.dumps({'SerializeVersion':283,'AtomType':'Person','Clips':selected},indent=2)+'\n',encoding='utf-8')
    json.loads(path.read_text(encoding='utf-8'))
