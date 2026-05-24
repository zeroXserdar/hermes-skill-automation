from __future__ import annotations

import argparse
from pathlib import Path

from hermes_constants import get_hermes_home

from .cli import (
    export_command,
    propose_command,
    recent_command,
    register_cli,
    status_command,
)
from .state import SkillFactoryState


def register(ctx) -> None:
    state = SkillFactoryState(get_hermes_home() / "plugins" / "skill_factory_v1" / "state")

    skill_path = Path(__file__).resolve().parent / "skills" / "workflow-to-skill" / "SKILL.md"
    ctx.register_skill(
        name="workflow-to-skill",
        path=skill_path,
        description="Turn exported workflow summaries into polished Hermes skills.",
    )

    ctx.register_hook("pre_tool_call", lambda **kw: state.record_tool_call("pre", **kw))
    ctx.register_hook("post_tool_call", lambda **kw: state.record_tool_call("post", **kw))
    ctx.register_hook("on_session_finalize", lambda **kw: state.finalize_session(**kw))
    ctx.register_hook("on_session_reset", lambda **kw: state.mark_reset(**kw))

    ctx.register_command(
        name="skillfactory-status",
        handler=lambda raw_args="": state.render_status(raw_args.strip() or None),
        description="Show Hermes Skill Automation capture status for the active or latest session.",
        args_hint="[session_id]",
    )
    ctx.register_command(
        name="skillfactory-last",
        handler=lambda raw_args="": state.render_last_session(),
        description="Show the latest finalized session known to Hermes Skill Automation.",
    )
    ctx.register_command(
        name="skillfactory-export",
        handler=lambda raw_args="": state.export_summary_command(raw_args.strip() or None),
        description="Export a markdown workflow summary for the given or latest session.",
        args_hint="[session_id]",
    )
    ctx.register_command(
        name="skillfactory-propose",
        handler=lambda raw_args="": _handle_propose_command(state, raw_args),
        description="Create an agent-facing proposal packet and draft scaffold from the given or latest session.",
        args_hint="[session_id] [skill_name]",
    )

    ctx.register_cli_command(
        name="skill-factory-v1",
        help="Inspect and export Hermes Skill Automation workflow captures",
        setup_fn=register_cli,
        handler_fn=skill_factory_v1_command,
        description="Hermes-native workflow capture exporter for turning repeated sessions into reusable skills.",
    )


def _handle_propose_command(state: SkillFactoryState, raw_args: str) -> str:
    parts = [p for p in raw_args.split() if p]
    session_id = parts[0] if parts else None
    skill_name = parts[1] if len(parts) > 1 else None
    return state.propose_skill_command(session_id=session_id, skill_name=skill_name)


def skill_factory_v1_command(args: argparse.Namespace) -> None:
    state = SkillFactoryState(get_hermes_home() / "plugins" / "skill_factory_v1" / "state")
    action = getattr(args, "skill_factory_action", None)
    if action == "status":
        status_command(state, args)
    elif action == "export":
        export_command(state, args)
    elif action == "propose":
        propose_command(state, args)
    elif action == "recent":
        recent_command(state, args)
    else:
        raise SystemExit("Unknown Hermes Skill Automation action")
