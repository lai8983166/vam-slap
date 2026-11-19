using System;
using System.Collections.Generic;
using UnityEngine;

// Attach to the Person. Timeline continues to drive the hand target.
public class SlapContactGrip : MVRScript
{
    private JSONStorableFloat amount, positionSpring, rotationSpring;
    private readonly List<ContactGripRelay> sensors = new List<ContactGripRelay>();
    private readonly HashSet<Rigidbody> localBodies = new HashSet<Rigidbody>();
    private bool active;
    private float basePosition, baseRotation;

    public override void Init()
    {
        try
        {
            JSONStorable hand = containingAtom.GetStorableByID("rHandControl");
            if (hand == null) throw new Exception("Load this plugin on the Person that owns the right hand.");
            positionSpring = hand.GetFloatJSONParam("holdPositionSpring");
            rotationSpring = hand.GetFloatJSONParam("holdRotationSpring");
            if (positionSpring == null || rotationSpring == null) throw new Exception("Hand spring parameters unavailable.");
            amount = new JSONStorableFloat("Contact stiffness", .45f, 0f, 1f);
            RegisterFloat(amount);
            CreateSlider(amount);
            foreach (Rigidbody rb in containingAtom.GetComponentsInChildren<Rigidbody>(true))
            {
                localBodies.Add(rb);
                string n = rb.name;
                if (n != "rHand" && !n.StartsWith("rIndex") && !n.StartsWith("rMid")
                    && !n.StartsWith("rRing") && !n.StartsWith("rPinky") && !n.StartsWith("rThumb")) continue;
                ContactGripRelay relay = rb.gameObject.AddComponent<ContactGripRelay>();
                sensors.Add(relay);
                relay.owner = this;
            }
            if (sensors.Count == 0) throw new Exception("No right-hand physics bodies found.");
            CreateTextField(new JSONStorableString("Help", "0 = original springs. Higher values hold the wrist more firmly during physical contact.")).height = 90f;
        }
        catch (Exception e) { SuperController.LogError("SlapContactGrip: " + e.Message); }
    }

    public bool Accept(Collider other)
    {
        Rigidbody rb = other.attachedRigidbody;
        if (rb == null) return !other.transform.IsChildOf(containingAtom.transform);
        return !localBodies.Contains(rb) || rb.name == "head";
    }

    private void FixedUpdate()
    {
        bool touching = false;
        foreach (ContactGripRelay sensor in sensors)
            if (sensor != null && sensor.touching) { touching = true; break; }
        if (!touching || amount == null || amount.val <= 0f) { Restore(); return; }
        if (!active)
        {
            basePosition = positionSpring.val;
            baseRotation = rotationSpring.val;
            active = true;
        }
        positionSpring.val = Mathf.Clamp(basePosition * (1f + 2f * amount.val), positionSpring.min, positionSpring.max);
        rotationSpring.val = Mathf.Clamp(baseRotation * (1f + 2f * amount.val), rotationSpring.min, rotationSpring.max);
    }

    private void Restore()
    {
        if (!active) return;
        active = false;
        positionSpring.val = basePosition;
        rotationSpring.val = baseRotation;
    }
    private void OnDisable() { Restore(); }
    private void OnDestroy()
    {
        Restore();
        foreach (ContactGripRelay sensor in sensors) if (sensor != null) Destroy(sensor);
    }
}

public class ContactGripRelay : MonoBehaviour
{
    public SlapContactGrip owner;
    private readonly HashSet<Collider> contacts = new HashSet<Collider>();
    public bool touching
    {
        get
        {
            contacts.RemoveWhere(c => c == null || !c.enabled || !c.gameObject.activeInHierarchy);
            return contacts.Count != 0;
        }
    }
    private void OnCollisionEnter(Collision c) { Track(c.collider); }
    private void OnCollisionStay(Collision c) { Track(c.collider); }
    private void OnCollisionExit(Collision c) { contacts.Remove(c.collider); }
    private void OnDisable() { contacts.Clear(); }
    private void Track(Collider c)
    {
        if (owner != null && owner.Accept(c)) contacts.Add(c);
    }
}
