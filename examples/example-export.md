# Hermes Skill Automation Workflow Export — demo-session-001

> Generated from deterministic plugin hook capture.

## Session Summary
- Session ID: `demo-session-001`
- First event: 2026-05-24T15:42:25.239696+00:00
- Last event: 2026-05-24T15:42:25.240136+00:00
- Total events: 7
- pre_tool_call count: 3
- post_tool_call count: 3

## Tool Frequency
- `read_file` × 2
- `search_files` × 2
- `write_file` × 2

## Event Timeline
- 2026-05-24T15:42:25.239696+00:00 — `tool_pre` — tool=`read_file` — args=path
- 2026-05-24T15:42:25.239881+00:00 — `tool_post` — tool=`read_file` — args=path — preview={'content': '# Hermes Skill Automation'}
- 2026-05-24T15:42:25.239991+00:00 — `tool_pre` — tool=`search_files` — args=pattern, target
- 2026-05-24T15:42:25.240035+00:00 — `tool_post` — tool=`search_files` — args=pattern, target — preview={'matches': [{'path': 'plugin/skill_factory_v1/state.py'}]}
- 2026-05-24T15:42:25.240073+00:00 — `tool_pre` — tool=`write_file` — args=path
- 2026-05-24T15:42:25.240103+00:00 — `tool_post` — tool=`write_file` — args=path — preview={'path': 'ACKNOWLEDGMENTS.md', 'status': 'ok'}
- 2026-05-24T15:42:25.240136+00:00 — `session_finalize`

## Suggested Next Step
Load `skill_factory_v1:workflow-to-skill`, then ask Hermes to convert this export into a reusable skill via `skill_manage`.
