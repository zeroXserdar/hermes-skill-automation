from pathlib import Path

from plugin.skill_factory_v1.state import SkillFactoryState


def test_records_exports_and_proposes(tmp_path: Path):
    state = SkillFactoryState(tmp_path / "state")

    state.record_tool_call(
        "pre",
        session_id="sess-1",
        platform="telegram",
        tool_name="read_file",
        args={"path": "README.md"},
    )
    state.record_tool_call(
        "post",
        session_id="sess-1",
        platform="telegram",
        tool_name="read_file",
        args={"path": "README.md"},
        result={"content": "hello"},
    )
    state.finalize_session(session_id="sess-1", platform="telegram")

    status = state.render_status("sess-1")
    assert "session: `sess-1`" in status
    assert "read_file×2" in status

    export_path = state.export_summary("sess-1")
    export_text = export_path.read_text(encoding="utf-8")
    assert "# Skill Factory Workflow Export — sess-1" in export_text
    assert "`read_file` × 2" in export_text

    proposal_path, draft_path = state.propose_skill("sess-1", skill_name="read-file-workflow")
    proposal_text = proposal_path.read_text(encoding="utf-8")
    draft_text = draft_path.read_text(encoding="utf-8")

    assert "# Skill Factory Proposal Packet — sess-1" in proposal_text
    assert "Suggested name: `read-file-workflow`" in proposal_text
    assert "Load `skill_factory_v1:workflow-to-skill`" in proposal_text
    assert "name: read-file-workflow" in draft_text
    assert "## Verification Checklist" in draft_text


def test_recent_and_last_session_views(tmp_path: Path):
    state = SkillFactoryState(tmp_path / "state")
    state.record_tool_call("pre", session_id="sess-a", platform="cli", tool_name="search_files", args={})
    state.finalize_session(session_id="sess-a", platform="cli")

    recent = state.render_recent(limit=5)
    latest = state.render_last_session()

    assert "Recent Skill Factory sessions" in recent
    assert "`sess-a`" in recent
    assert "Latest finalized session" in latest
    assert "`sess-a`" in latest
