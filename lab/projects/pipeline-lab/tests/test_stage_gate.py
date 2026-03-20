from app.services.stage_gate import StageGate


def test_stage_gate_sequential():
    gate = StageGate()
    assert gate.can_advance("source_policy", "source_manifest")
    assert not gate.can_advance("source_policy", "chunking")
