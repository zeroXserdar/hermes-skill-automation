from __future__ import annotations

import argparse


def register_cli(subparser: argparse.ArgumentParser) -> None:
    subparser.set_defaults(skill_factory_action=None)
    nested = subparser.add_subparsers(dest="skill_factory_action")

    status = nested.add_parser("status", help="Show capture status for one session")
    status.add_argument("--session-id", help="Specific session id to inspect")

    export = nested.add_parser("export", help="Export a markdown workflow summary")
    export.add_argument("--session-id", help="Specific session id to export")

    propose = nested.add_parser("propose", help="Create an agent-facing proposal packet from a captured session")
    propose.add_argument("--session-id", help="Specific session id to propose from")
    propose.add_argument("--skill-name", help="Optional explicit candidate skill name")

    recent = nested.add_parser("recent", help="List recent finalized sessions")
    recent.add_argument("--limit", type=int, default=5, help="Maximum sessions to show")


def status_command(state, args: argparse.Namespace) -> None:
    print(state.render_status(getattr(args, "session_id", None)))


def export_command(state, args: argparse.Namespace) -> None:
    print(state.export_summary_command(getattr(args, "session_id", None)))


def propose_command(state, args: argparse.Namespace) -> None:
    print(
        state.propose_skill_command(
            session_id=getattr(args, "session_id", None),
            skill_name=getattr(args, "skill_name", None),
        )
    )


def recent_command(state, args: argparse.Namespace) -> None:
    print(state.render_recent(limit=max(1, int(getattr(args, "limit", 5) or 5))))
