using System;
using System.Collections;
using UnityEngine;

// Load on Person#2 once before importing the reference-based Timeline clips.
// Native VaM ParentLink owns following and interactive offset editing.
// This script does not overwrite the handle transform during playback.
public class SlapReferenceSetup : MVRScript
{
    private const string ReferenceUid = "SlapReference_Person2";
    private JSONStorableString status;
    private bool busy;

    public override void Init()
    {
        status = new JSONStorableString("Status", "Preparing reference...");
        CreateTextField(status).height = 230f;
        CreateButton("Create / reconnect reference").button.onClick.AddListener(() => StartCoroutine(Setup(false)));
        CreateButton("Select reference handle").button.onClick.AddListener(SelectReference);
        CreateButton("Reset reference to default contact").button.onClick.AddListener(() => StartCoroutine(Setup(true)));
        StartCoroutine(Setup(false));
    }

    private IEnumerator Setup(bool reset)
    {
        if (busy) yield break;
        busy = true;
        try
        {
            while (SuperController.singleton.isLoading) yield return null;
            if (containingAtom == null || containingAtom.uid != "Person#2")
            {
                status.val = "Load this setup plugin on Person#2. No scene objects were changed.";
                yield break;
            }
            Rigidbody head = null;
            foreach (Rigidbody rb in containingAtom.linkableRigidbodies)
                if (rb.name == "head") { head = rb; break; }
            if (head == null)
            {
                status.val = "Person#2 has no linkable head rigidbody.";
                yield break;
            }
            Atom reference = SuperController.singleton.GetAtomByUid(ReferenceUid);
            bool created = reference == null;
            if (created)
            {
                yield return SuperController.singleton.AddAtomByType("Empty", ReferenceUid);
                reference = SuperController.singleton.GetAtomByUid(ReferenceUid);
            }
            if (reference == null || reference.type != "Empty")
            {
                status.val = "Cannot create reference, or its UID is occupied by a non-Empty atom.";
                yield break;
            }
            FreeControllerV3 control = reference.mainController;
            bool alreadyLinked = control.linkToRB == head
                && control.currentPositionState == FreeControllerV3.PositionState.ParentLink
                && control.currentRotationState == FreeControllerV3.RotationState.ParentLink;
            if (created || reset || !alreadyLinked)
            {
                control.currentPositionState = FreeControllerV3.PositionState.On;
                control.currentRotationState = FreeControllerV3.RotationState.On;
                if (created || reset)
                {
                    control.transform.position = head.transform.TransformPoint(new Vector3(.14f, -.03f, .08f));
                    control.transform.rotation = head.transform.rotation;
                }
                control.SetLinkToAtom(containingAtom.uid);
                control.SetLinkToRigidbodyObject("head");
                control.currentPositionState = FreeControllerV3.PositionState.ParentLink;
                control.currentRotationState = FreeControllerV3.RotationState.ParentLink;
            }
            control.canGrabPosition = true;
            control.canGrabRotation = true;
            reference.hidden = false;
            status.val = "Ready: " + ReferenceUid + " follows Person#2/head.\n"
                + "Import All_3_Adjustable_Reference.json into Person#2 Timeline.\n"
                + "Select this Empty atom to move/rotate the entire motion while playing.\n"
                + "Keep Position and Rotation in ParentLink. Save your scene to retain this handle.";
        }
        finally { busy = false; }
    }

    private void SelectReference()
    {
        Atom reference = SuperController.singleton.GetAtomByUid(ReferenceUid);
        if (reference != null) SuperController.singleton.SelectController(reference.mainController);
    }
}
