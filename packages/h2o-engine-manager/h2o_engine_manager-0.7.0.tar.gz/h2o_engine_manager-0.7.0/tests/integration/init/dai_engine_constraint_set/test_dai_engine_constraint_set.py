def test_get_dai_engine_constraint_set(dai_engine_constraint_set_client):
    """DAIEngineConstraintSet is a singleton. Testing that it does not fail when we want to fetch it.
    Indirectly testing, that a DAISetup exists (that it was created during application startup) even when it wasn't
    created manually via kubectl.
    """
    cs = dai_engine_constraint_set_client.get_constraint_set(workspace_id="foo")
    assert cs.name == "workspaces/foo/daiEngineConstraintSet"
