from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class SessionIndexEntry:
    session_id: str
    platform: str
    finalized_at: str
    event_count: int
    pre_tool_calls: int
    post_tool_calls: int
    log_path: str


class SkillFactoryState:
    """Persist deterministic workflow evidence for later skill authoring.

    This class deliberately captures only what Hermes plugin hooks can observe
    reliably today: tool-call boundaries and session lifecycle markers.
    """

    def __init__(self, root: Path) -> None:
        self.root = root
        self.sessions_dir = self.root / "sessions"
        self.exports_dir = self.root / "exports"
        self.proposals_dir = self.root / "proposals"
        self.drafts_dir = self.root / "drafts"
        self.index_path = self.root / "index.json"
        self.root.mkdir(parents=True, exist_ok=True)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.exports_dir.mkdir(parents=True, exist_ok=True)
        self.proposals_dir.mkdir(parents=True, exist_ok=True)
        self.drafts_dir.mkdir(parents=True, exist_ok=True)

    # ---- recording -----------------------------------------------------

    def record_tool_call(self, phase: str, **kwargs: Any) -> None:
        session_id = self._extract_session_id(kwargs)
        if not session_id:
            return
        event = {
            "ts": _utc_now(),
            "type": f"tool_{phase}",
            "session_id": session_id,
            "platform": kwargs.get("platform") or "unknown",
            "tool_name": kwargs.get("tool_name") or "unknown",
            "task_id": kwargs.get("task_id"),
            "args_keys": sorted(list((kwargs.get("args") or {}).keys())) if isinstance(kwargs.get("args"), dict) else [],
            "result_preview": self._result_preview(kwargs.get("result")) if phase == "post" else None,
        }
        self._append_event(session_id, event)

    def finalize_session(self, **kwargs: Any) -> None:
        session_id = kwargs.get("session_id")
        if not session_id:
            return
        event = {
            "ts": _utc_now(),
            "type": "session_finalize",
            "session_id": session_id,
            "platform": kwargs.get("platform") or "unknown",
        }
        self._append_event(session_id, event)
        self._update_index(session_id=session_id, platform=event["platform"])

    def mark_reset(self, **kwargs: Any) -> None:
        session_id = kwargs.get("session_id")
        if not session_id:
            return
        event = {
            "ts": _utc_now(),
            "type": "session_reset",
            "session_id": session_id,
            "platform": kwargs.get("platform") or "unknown",
        }
        self._append_event(session_id, event)

    # ---- render/export -------------------------------------------------

    def render_status(self, session_id: Optional[str] = None) -> str:
        sid = session_id or self._latest_session_id()
        if not sid:
            return "Hermes Skill Automation: no captured sessions yet."
        events = self._load_events(sid)
        if not events:
            return f"Hermes Skill Automation: no events found for session `{sid}`."
        counts = Counter(e.get("type") for e in events)
        tools = Counter(e.get("tool_name") for e in events if str(e.get("type", "")).startswith("tool_"))
        top_tools = ", ".join(f"{name}×{count}" for name, count in tools.most_common(6)) or "none"
        return (
            f"Hermes Skill Automation\n"
            f"- session: `{sid}`\n"
            f"- events: {len(events)}\n"
            f"- pre_tool_call: {counts.get('tool_pre', 0)}\n"
            f"- post_tool_call: {counts.get('tool_post', 0)}\n"
            f"- resets: {counts.get('session_reset', 0)}\n"
            f"- finalized: {counts.get('session_finalize', 0)}\n"
            f"- top tools: {top_tools}\n"
            f"- log: `{self._session_log_path(sid)}`"
        )

    def render_last_session(self) -> str:
        entry = self._latest_index_entry()
        if not entry:
            return "Hermes Skill Automation: no finalized sessions yet."
        return (
            f"Latest finalized session\n"
            f"- session: `{entry['session_id']}`\n"
            f"- platform: {entry.get('platform', 'unknown')}\n"
            f"- finalized_at: {entry.get('finalized_at', 'unknown')}\n"
            f"- events: {entry.get('event_count', 0)}\n"
            f"- log: `{entry.get('log_path', '')}`"
        )

    def render_recent(self, limit: int = 5) -> str:
        index = self._load_index()
        if not index:
            return "Hermes Skill Automation: no finalized sessions yet."
        rows = sorted(index, key=lambda x: x.get("finalized_at", ""), reverse=True)[:limit]
        lines = ["Recent Hermes Skill Automation sessions"]
        for row in rows:
            lines.append(
                f"- `{row['session_id']}` | {row.get('platform', 'unknown')} | "
                f"events={row.get('event_count', 0)} | finalized={row.get('finalized_at', 'unknown')}"
            )
        return "\n".join(lines)

    def export_summary_command(self, session_id: Optional[str] = None) -> str:
        sid = session_id or self._latest_session_id()
        if not sid:
            return "Hermes Skill Automation: no captured sessions to export."
        export_path = self.export_summary(sid)
        return f"Exported workflow summary to `{export_path}`"

    def propose_skill_command(self, session_id: Optional[str] = None, skill_name: Optional[str] = None) -> str:
        sid = session_id or self._latest_session_id()
        if not sid:
            return "Hermes Skill Automation: no captured sessions to propose from."
        proposal_path, draft_path = self.propose_skill(sid, skill_name=skill_name)
        return (
            f"Created proposal packet at `{proposal_path}`\n"
            f"Created draft scaffold at `{draft_path}`"
        )

    def export_summary(self, session_id: str) -> Path:
        events = self._load_events(session_id)
        if not events:
            raise FileNotFoundError(f"No events found for session {session_id}")
        counts = Counter(e.get("type") for e in events)
        tools = Counter(e.get("tool_name") for e in events if str(e.get("type", "")).startswith("tool_"))
        first_ts = events[0].get("ts", "")
        last_ts = events[-1].get("ts", "")

        lines = [
            f"# Hermes Skill Automation Workflow Export — {session_id}",
            "",
            "> Generated from deterministic plugin hook capture.",
            "",
            "## Session Summary",
            f"- Session ID: `{session_id}`",
            f"- First event: {first_ts}",
            f"- Last event: {last_ts}",
            f"- Total events: {len(events)}",
            f"- pre_tool_call count: {counts.get('tool_pre', 0)}",
            f"- post_tool_call count: {counts.get('tool_post', 0)}",
            "",
            "## Tool Frequency",
        ]
        if tools:
            for name, count in tools.most_common():
                lines.append(f"- `{name}` × {count}")
        else:
            lines.append("- none captured")

        lines.extend([
            "",
            "## Event Timeline",
        ])
        for event in events:
            kind = event.get("type", "unknown")
            ts = event.get("ts", "")
            tool = event.get("tool_name")
            args_keys = event.get("args_keys") or []
            preview = event.get("result_preview")
            bullet = f"- {ts} — `{kind}`"
            if tool:
                bullet += f" — tool=`{tool}`"
            if args_keys:
                bullet += f" — args={', '.join(args_keys)}"
            if preview:
                bullet += f" — preview={preview}"
            lines.append(bullet)

        lines.extend([
            "",
            "## Suggested Next Step",
            "Load `skill_factory_v1:workflow-to-skill`, then ask Hermes to convert this export into a reusable skill via `skill_manage`.",
            "",
        ])
        out = self.exports_dir / f"{session_id}.md"
        out.write_text("\n".join(lines), encoding="utf-8")
        return out

    def propose_skill(self, session_id: str, skill_name: Optional[str] = None) -> Tuple[Path, Path]:
        export_path = self.export_summary(session_id)
        events = self._load_events(session_id)
        if not events:
            raise FileNotFoundError(f"No events found for session {session_id}")

        tools = Counter(e.get("tool_name") for e in events if str(e.get("type", "")).startswith("tool_"))
        top_tools = [name for name, _count in tools.most_common(5)]
        candidate_skill = self._normalize_skill_name(skill_name or self._suggest_skill_name(session_id, top_tools))
        tool_tags = ", ".join(top_tools) if top_tools else "verification required"

        proposal_lines = [
            f"# Hermes Skill Automation Proposal Packet — {session_id}",
            "",
            "## Intent",
            "This packet is meant for an LLM agent session, not as a final skill by itself.",
            "Use it to create or refine a reusable `SKILL.md` with human review.",
            "",
            "## Candidate Skill",
            f"- Suggested name: `{candidate_skill}`",
            f"- Dominant tools: {tool_tags}",
            f"- Source export: `{export_path}`",
            "",
            "## Agent Prompt",
            "```text",
            f"Load `skill_factory_v1:workflow-to-skill`. Read `{export_path}`. Convert it into a polished reusable Hermes skill named `{candidate_skill}`. Use only facts present in the export. If a field is missing, mark it as verification required instead of guessing. Return: (1) a proposed skill outline, (2) the final SKILL.md content, and (3) any supporting references/templates worth splitting out.",
            "```",
            "",
            "## Observed Tool Pattern",
        ]
        if top_tools:
            for name, count in tools.most_common(8):
                proposal_lines.append(f"- `{name}` × {count}")
        else:
            proposal_lines.append("- verification required")

        proposal_lines.extend([
            "",
            "## Review Checklist",
            "- [ ] Skill name matches the actual repeated workflow",
            "- [ ] No inferred steps were added without evidence",
            "- [ ] Pitfalls and verification steps were included",
            "- [ ] Any unresolved facts are marked 'verification required'",
            "",
        ])

        proposal_path = self.proposals_dir / f"{session_id}--{candidate_skill}.md"
        proposal_path.write_text("\n".join(proposal_lines), encoding="utf-8")

        draft_lines = self._draft_skill_template(candidate_skill, export_path, top_tools)
        draft_path = self.drafts_dir / f"{candidate_skill}.SKILL.md"
        draft_path.write_text("\n".join(draft_lines), encoding="utf-8")
        return proposal_path, draft_path

    # ---- storage helpers ------------------------------------------------

    def _session_log_path(self, session_id: str) -> Path:
        return self.sessions_dir / f"{session_id}.jsonl"

    def _append_event(self, session_id: str, event: Dict[str, Any]) -> None:
        path = self._session_log_path(session_id)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, ensure_ascii=False) + "\n")

    def _load_events(self, session_id: str) -> List[Dict[str, Any]]:
        path = self._session_log_path(session_id)
        if not path.exists():
            return []
        rows: List[Dict[str, Any]] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
        return rows

    def _load_index(self) -> List[Dict[str, Any]]:
        if not self.index_path.exists():
            return []
        try:
            data = json.loads(self.index_path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def _save_index(self, rows: Iterable[Dict[str, Any]]) -> None:
        self.index_path.write_text(json.dumps(list(rows), ensure_ascii=False, indent=2), encoding="utf-8")

    def _update_index(self, session_id: str, platform: str) -> None:
        events = self._load_events(session_id)
        counts = Counter(e.get("type") for e in events)
        entry = SessionIndexEntry(
            session_id=session_id,
            platform=platform or "unknown",
            finalized_at=_utc_now(),
            event_count=len(events),
            pre_tool_calls=counts.get("tool_pre", 0),
            post_tool_calls=counts.get("tool_post", 0),
            log_path=str(self._session_log_path(session_id)),
        )
        rows = [r for r in self._load_index() if r.get("session_id") != session_id]
        rows.append(entry.__dict__)
        rows.sort(key=lambda x: x.get("finalized_at", ""), reverse=True)
        self._save_index(rows)

    def _latest_index_entry(self) -> Optional[Dict[str, Any]]:
        rows = self._load_index()
        if not rows:
            return None
        rows.sort(key=lambda x: x.get("finalized_at", ""), reverse=True)
        return rows[0]

    def _latest_session_id(self) -> Optional[str]:
        entry = self._latest_index_entry()
        if entry:
            return str(entry.get("session_id"))
        candidates = sorted(self.sessions_dir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not candidates:
            return None
        return candidates[0].stem

    @staticmethod
    def _extract_session_id(kwargs: Dict[str, Any]) -> Optional[str]:
        session_id = kwargs.get("session_id")
        if session_id:
            return str(session_id)
        parent_agent = kwargs.get("parent_agent")
        sid = getattr(parent_agent, "session_id", None)
        return str(sid) if sid else None

    @staticmethod
    def _result_preview(result: Any, limit: int = 120) -> Optional[str]:
        if result is None:
            return None
        text = str(result).replace("\n", " ").strip()
        if not text:
            return None
        return text[:limit] + ("..." if len(text) > limit else "")

    @staticmethod
    def _normalize_skill_name(raw: str) -> str:
        name = re.sub(r"[^a-z0-9_-]+", "-", raw.strip().lower())
        name = re.sub(r"-+", "-", name).strip("-")
        return name or "workflow-skill"

    def _suggest_skill_name(self, session_id: str, top_tools: List[str]) -> str:
        if top_tools:
            basis = "-".join(top_tools[:2])
            return f"workflow-{basis}"
        return f"workflow-{session_id[:12]}"

    @staticmethod
    def _draft_skill_template(skill_name: str, export_path: Path, top_tools: List[str]) -> List[str]:
        tags = ", ".join(top_tools[:5]) if top_tools else "workflow, verification-required"
        related = ", ".join([tool for tool in top_tools[:3] if tool]) or ""
        related_list = f"[{related}]" if related else "[]"
        return [
            "---",
            f"name: {skill_name}",
            'description: "Use when this captured workflow recurs and should become a reusable Hermes skill. Facts not present in the export must remain verification required."',
            "version: 0.1.0",
            "author: Hermes Agent",
            "license: MIT",
            "metadata:",
            "  hermes:",
            f"    tags: [{tags}]",
            f"    related_skills: {related_list}",
            "---",
            "",
            f"# {skill_name}",
            "",
            "## Overview",
            f"Draft scaffold generated from `{export_path}`.",
            "Refine this with the `skill_factory_v1:workflow-to-skill` helper skill before publishing.",
            "",
            "## When to Use",
            "- Use when this workflow repeats often enough to justify a reusable skill.",
            "- If any critical step is not evidenced in the export, mark it as verification required.",
            "",
            "## Workflow Evidence",
            f"- Source export: `{export_path}`",
            f"- Dominant observed tools: {', '.join(top_tools) if top_tools else 'verification required'}",
            "",
            "## Draft Procedure",
            "1. Review the source export carefully.",
            "2. Extract only repeated, evidenced steps.",
            "3. Split pitfalls and verification into their own sections.",
            "4. Replace any uncertain detail with 'verification required'.",
            "",
            "## Common Pitfalls",
            "1. Inferring intent or missing steps from tool names alone.",
            "2. Publishing the scaffold without human/agent refinement.",
            "",
            "## Verification Checklist",
            "- [ ] Every procedure step is grounded in the export",
            "- [ ] Missing facts are marked verification required",
            "- [ ] Tool-specific commands and pitfalls were refined",
        ]
