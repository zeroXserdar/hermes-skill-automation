# Contributing

Thanks for considering improvements to **Hermes Skill Factory Native v1**.

## Project intent
This repo is intentionally narrow in scope:
- capture deterministic workflow evidence from real Hermes plugin hooks
- export that evidence into reviewable artifacts
- prepare proposal packets and draft skill scaffolds for human/agent refinement

Please keep contributions aligned with that scope. Avoid claims of fully automatic skill synthesis unless they are grounded in real Hermes extension points.

## Local development
### Prerequisites
- Python 3.11+
- a local Hermes checkout at `/usr/local/lib/hermes-agent` for the current test configuration

### Run tests
```bash
pytest
```

### Optional smoke test
```bash
PYTHONPATH=.:/usr/local/lib/hermes-agent python3 - <<'PY'
from pathlib import Path
from tempfile import TemporaryDirectory
from plugin.skill_factory_v1.state import SkillFactoryState

with TemporaryDirectory() as td:
    root = Path(td) / 'state'
    s = SkillFactoryState(root)
    s.record_tool_call('pre', session_id='demo', platform='telegram', tool_name='read_file', args={'path':'README.md'})
    s.record_tool_call('post', session_id='demo', platform='telegram', tool_name='read_file', args={'path':'README.md'}, result={'content':'ok'})
    s.finalize_session(session_id='demo', platform='telegram')
    proposal_path, draft_path = s.propose_skill('demo', skill_name='demo-read-file')
    print(proposal_path)
    print(draft_path)
PY
```

## Repo structure
- `plugin/skill_factory_v1/` — plugin implementation
- `skills/workflow-to-skill/` — helper skill copy for development/reference
- `examples/` — synthetic example artifacts generated from the real state logic
- `tests/` — unit tests for registration and state/export behavior

## Pull request guidelines
- Keep behavior grounded in current Hermes plugin APIs.
- Add or update tests for user-visible behavior changes.
- Update `README.md` if command surface, install flow, or limitations change.
- Prefer explicit "verification required" placeholders over guessed behavior.
- Include before/after examples when changing export, proposal, or scaffold formats.

## Non-goals
- Hidden network dependencies for tests
- Claims of zero-review automatic skill generation
- Plugin behavior that depends on undocumented Hermes internals
