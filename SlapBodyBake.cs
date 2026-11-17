using System;
using System.Globalization;
using UnityEngine;
using SimpleJSON;

// Pose-calibrated Timeline data authoring, not a second runtime animation driver.
public class SlapBodyBake : MVRScript
{
    private const string Input = "Saves/PluginData/animations/HeadRelativeAdjustable/All_3_RightToLeft_Arc_V2.json";
    private const string Output = "Saves/PluginData/animations/HeadRelativeAdjustable/All_3_FullBody_V3.json";
    private JSONStorableString status;
    private JSONStorableFloat intensity;
    private static readonly CultureInfo CI = CultureInfo.InvariantCulture;

    public override void Init()
    {
        status = new JSONStorableString("Status", "Pause Timeline, pose Person#2 and position the reference.\nClick Bake, then import All_3_FullBody_V3.json.\nThis tool captures the current chest/shoulder/elbow pose; it does not animate by itself.");
        CreateTextField(status).height = 260f;
        intensity = new JSONStorableFloat("Body intensity", 1f, .25f, 1.5f);
        RegisterFloat(intensity);
        CreateSlider(intensity);
        CreateButton("Capture current pose + bake V3").button.onClick.AddListener(Bake);
        CreateButton("Enable required controller channels").button.onClick.AddListener(EnableControls);
    }

    private FreeControllerV3 Control(string id)
    {
        FreeControllerV3 c = containingAtom.GetStorableByID(id) as FreeControllerV3;
        if (c == null) throw new Exception("Missing controller: " + id);
        return c;
    }

    // Hermite smoothstep phases with zero derivative at preparation/recovery extremes.
    private float Drive(float t)
    {
        float[] times = { 0f, .40f, .54f, .75f, .87f, 1.03f, 1.80f, 2.10f };
        float[] values = { 0f, -1f, -1f, .55f, 1f, .80f, 0f, 0f };
        if (t <= 0f) return 0f;
        for (int i = 0; i < times.Length - 1; i++)
        {
            if (t > times[i+1]) continue;
            float u = Mathf.Clamp01((t-times[i])/(times[i+1]-times[i]));
            return Mathf.Lerp(values[i], values[i+1], u*u*(3f-2f*u));
        }
        return 0f;
    }

    private void Bake()
    {
        try
        {
            if (containingAtom.uid != "Person#2") throw new Exception("Load this tool on Person#2.");
            foreach (string id in containingAtom.GetStorableIDs())
            {
                if (id.IndexOf("VamTimeline", StringComparison.OrdinalIgnoreCase) < 0) continue;
                JSONStorable storable = containingAtom.GetStorableByID(id);
                JSONStorableBool playing = storable.GetBoolJSONParam("Is Playing");
                if (playing != null && playing.val) throw new Exception("Pause Timeline before capturing the pose.");
            }
            Atom reference = SuperController.singleton.GetAtomByUid("SlapReference_Person2");
            if (reference == null) throw new Exception("Create SlapReference_Person2 first using SlapReferenceSetup.");
            JSONClass data = SuperController.singleton.LoadJSON(Input).AsObject;
            if (data == null || data["Clips"].AsArray == null) throw new Exception("V2 input file was not found.");
            FreeControllerV3 chest = Control("chestControl");
            FreeControllerV3 shoulder = Control("rShoulderControl");
            FreeControllerV3 elbow = Control("rElbowControl");
            Vector3 origin = chest.transform.position;
            Vector3 up = containingAtom.mainController.transform.up;
            // Project the current reference strike direction into the torso plane.
            Vector3 direction = Vector3.ProjectOnPlane(reference.mainController.transform.right, up).normalized;
            if (direction.sqrMagnitude < .1f) direction = chest.transform.right;
            Vector3 forward = Vector3.ProjectOnPlane(chest.transform.forward, up).normalized;
            float sign = Vector3.Dot(Vector3.Cross(up, forward), direction) >= 0f ? 1f : -1f;
            foreach (JSONClass clip in data["Clips"].AsArray)
            {
                clip["AnimationName"] = clip["AnimationName"].Value.Replace("_V2", "_FullBody_V3");
                JSONArray controllers = clip["Controllers"].AsArray;
                if (controllers == null || controllers.Count != 1 || controllers[0]["Controller"].Value != "rHandControl")
                    throw new Exception("Expected original V2 input with exactly one right-hand track.");
                JSONArray timeKeys = controllers[0]["X"].AsArray;
                JSONClass chestTrack = NewTrack("chestControl", false, true);
                JSONClass shoulderTrack = NewTrack("rShoulderControl", true, true);
                // Elbow position controls bend; avoid forcing forearm roll.
                JSONClass elbowTrack = NewTrack("rElbowControl", true, false);
                Quaternion? lastChest = null, lastShoulder = null, lastElbow = null;
                foreach (JSONClass key in timeKeys)
                {
                    float t = float.Parse(key["t"].Value, CI);
                    float cycle = t > 2.1f ? t - 2.1f : t;
                    float lead = .045f * Mathf.Sin(Mathf.PI * Mathf.Clamp01(cycle / 1.8f));
                    float torso = Drive(cycle + lead) * intensity.val;
                    float scapula = Drive(cycle) * intensity.val;
                    float arm = Drive(cycle - .035f) * intensity.val;
                    Quaternion turn = Quaternion.AngleAxis(13f * sign * torso, up);
                    Quaternion lean = Quaternion.AngleAxis(-2.5f * torso, chest.transform.right);
                    Quaternion delta = turn * lean;
                    Vector3 chestPos = origin;
                    Quaternion chestRot = delta * chest.transform.rotation;
                    Vector3 shoulderPos = origin + delta * (shoulder.transform.position-origin)
                        + direction * (.018f * scapula) + up * (.004f * Mathf.Abs(scapula));
                    Quaternion shoulderRot = delta * Quaternion.AngleAxis(4f*sign*scapula, up) * shoulder.transform.rotation;
                    Vector3 elbowPos = origin + delta * (elbow.transform.position-origin)
                        + direction * (.075f*arm) + up * (.025f*Mathf.Abs(arm));
                    AddPose(chestTrack, chest, t, chestPos, chestRot, ref lastChest);
                    AddPose(shoulderTrack, shoulder, t, shoulderPos, shoulderRot, ref lastShoulder);
                    AddPose(elbowTrack, elbow, t, elbowPos, elbow.transform.rotation, ref lastElbow);
                }
                controllers.Add(chestTrack);
                controllers.Add(shoulderTrack);
                controllers.Add(elbowTrack);
            }
            SuperController.singleton.SaveJSON(data, Output);
            status.val = "Baked 3 V3 clips from CURRENT pose.\nImport: " + Output
                + "\nEnable required controller channels, then play a FullBody_V3 clip."
                + "\nHand still follows the draggable head-linked reference. For major direction/pose changes, pause and bake again."
                + "\nDo not run another layer on chest/right shoulder/right elbow.";
        }
        catch (Exception e)
        {
            status.val = "Bake failed: " + e.Message;
            SuperController.LogError("SlapBodyBake: " + e);
        }
    }

    private JSONClass NewTrack(string id, bool position, bool rotation)
    {
        JSONClass track = new JSONClass();
        track["Controller"] = id;
        track["TargetsPosition"] = "1"; track["TargetsRotation"] = "1";
        track["ControlPosition"] = position ? "1" : "0";
        track["ControlRotation"] = rotation ? "1" : "0";
        track["Weight"] = "1";
        foreach (string k in new[] { "X","Y","Z","RotX","RotY","RotZ","RotW" }) track[k] = new JSONArray();
        return track;
    }

    private void AddPose(JSONClass track, FreeControllerV3 controller, float t, Vector3 pos, Quaternion rot, ref Quaternion? previous)
    {
        Transform parent = controller.transform.parent;
        Vector3 p = parent != null ? parent.InverseTransformPoint(pos) : pos;
        Quaternion q = parent != null ? Quaternion.Inverse(parent.rotation)*rot : rot;
        if (previous.HasValue && Quaternion.Dot(previous.Value, q) < 0f) q = new Quaternion(-q.x,-q.y,-q.z,-q.w);
        previous = q;
        string[] names = { "X","Y","Z","RotX","RotY","RotZ","RotW" };
        float[] vals = { p.x,p.y,p.z,q.x,q.y,q.z,q.w };
        for (int i=0; i<names.Length; i++)
        {
            JSONClass key = new JSONClass();
            key["t"] = t.ToString("R", CI);
            key["v"] = vals[i].ToString("R", CI);
            key["c"] = "2";
            track[names[i]].AsArray.Add(key);
        }
    }

    private void EnableControls()
    {
        try
        {
            Control("chestControl").currentRotationState = FreeControllerV3.RotationState.On;
            Control("rShoulderControl").currentPositionState = FreeControllerV3.PositionState.On;
            Control("rShoulderControl").currentRotationState = FreeControllerV3.RotationState.On;
            Control("rElbowControl").currentPositionState = FreeControllerV3.PositionState.On;
            Control("rHandControl").currentPositionState = FreeControllerV3.PositionState.On;
            Control("rHandControl").currentRotationState = FreeControllerV3.RotationState.On;
            status.val = "Required channels set to On. Play an imported FullBody_V3 clip.";
        }
        catch (Exception e) { status.val = e.Message; }
    }
}
