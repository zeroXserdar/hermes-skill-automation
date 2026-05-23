from pathlib import Path

from plugin.skill_factory_v1.state import SkillFactoryState


def test_records_and_exports(tmp_path: Path):
    state = SkillFactoryState(tmp_path / "state")
    state.record_tool_call("pre", session_id="sess-1", platform="telegram", tool_name="read_file", args={"path": "a.txt"})
    state.record_tool_call("post", session_id="sess-1", platform="telegram", tool_name="read_file", result="ok")
    state.finalize_session(session_id="sess-1", platform="telegram")

    exported = state.export_summary("sess-1")
    text = exported.read_text(encoding="utf-8")
    assert exported.exists()
    assert "Skill Factory Workflow Export" in text
    assert "`read_file` × 2" in text


def test_propose_creates_packet_and_draft(tmp_path: Path):
    state = SkillFactoryState(tmp_path / "state")
    state.record_tool_call("pre", session_id="sess-2", platform="telegram", tool_name="read_file", args={"path": "a.txt"})
    state.record_tool_call("post", session_id="sess-2", platform="telegram", tool_name="patch", result="done")
    state.finalize_session(session_id="sess-2", platform="telegram")

    proposal_path, draft_path = state.propose_skill("sess-2", skill_name="custom-skill")
    assert proposal_path.exists()
    assert draft_path.exists()
    proposal = proposal_path.read_text(encoding="utf-8")
    draft = draft_path.read_text(encoding="utf-8")
    assert "custom-skill" in proposal
    assert "Load `skill_factory_v1:workflow-to-skill`" in proposal
    assert "name: custom-skill" in draft
