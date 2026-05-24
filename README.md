# Hermes Skill Automation

> A Hermes-native workflow capture plugin that turns repeated agent sessions into exportable workflow evidence, proposal packets, and draft `SKILL.md` scaffolds.

## What this is

**Hermes Skill Automation** is the public-facing name of this project.

It captures real Hermes workflow evidence through supported plugin hooks, preserves that evidence across sessions, and turns it into reviewable artifacts that can be refined into reusable skills.

Core outputs:

- deterministic workflow exports
- agent-facing proposal packets
- draft `SKILL.md` scaffolds

## Branding and compatibility

This repository is branded as **Hermes Skill Automation** everywhere user-facing.

For compatibility with the current implementation, some internal identifiers still remain:

- plugin id: `skill_factory_v1`
- CLI namespace: `skill-factory-v1`
- slash commands: `/skillfactory-*`
- helper skill: `skill_factory_v1:workflow-to-skill`

Those internal names are kept intentionally so the current plugin keeps working without a breaking migration.

## Why this repo exists

The underlying idea is simple: repeated Hermes workflows should not disappear at the end of a session.

This project focuses on what is both **realistic today** and **compatible with current Hermes extension points**:

- capture deterministic evidence from real Hermes plugin hooks
- persist it locally across sessions
- export a clean workflow summary
- generate a proposal packet for agent refinement
- generate a draft `SKILL.md` scaffold for publication

In short: **deterministic capture first, agent-assisted polishing second**.

## What makes this implementation credible

This repo is grounded in real Hermes extension points, not imagined APIs:

- `plugin.yaml`
- `__init__.py` with `register(ctx)`
- plugin hooks such as `pre_tool_call`, `post_tool_call`, `on_session_finalize`, and `on_session_reset`
- slash commands registered with `ctx.register_command(...)`
- CLI subcommands registered with `ctx.register_cli_command(...)`
- plugin-provided namespaced skills registered with `ctx.register_skill(...)`

That constraint is deliberate. The point is to ship something real, inspectable, and maintainable.

## What you get

### 1) Passive workflow capture
The plugin records hook-visible workflow evidence, including:

- tool call boundaries
- session finalize events
- session reset events
- stable metadata available from current plugin hooks

State is stored under:

- `~/.hermes/plugins/skill_factory_v1/state/sessions/<session_id>.jsonl`
- `~/.hermes/plugins/skill_factory_v1/state/index.json`

### 2) Markdown workflow exports
A captured session can be exported into a concise markdown artifact that shows:

- session summary
- tool frequency
- event timeline
- suggested next step

### 3) Proposal generation
A captured session can be turned into:

- an **agent-facing proposal packet**
- a **draft `SKILL.md` scaffold**

The proposal packet includes:

- suggested skill name
- dominant observed tools
- exact agent prompt
- review checklist

### 4) In-session slash commands
Available commands:

- `/skillfactory-status`
- `/skillfactory-last`
- `/skillfactory-export [session_id]`
- `/skillfactory-propose [session_id] [skill_name]`

### 5) Operator CLI
Available CLI surface:

```bash
hermes skill-factory-v1 status [--session-id SID]
hermes skill-factory-v1 export [--session-id SID]
hermes skill-factory-v1 propose [--session-id SID] [--skill-name NAME]
hermes skill-factory-v1 recent [--limit N]
```

### 6) Helper skill
The plugin registers a namespaced helper skill:

- `skill_factory_v1:workflow-to-skill`

Use it to convert an exported workflow summary or proposal packet into a polished reusable Hermes skill.

## Workflow in one glance

```text
Hermes session
  -> plugin hooks capture evidence
  -> session state persisted locally
  -> export markdown summary
  -> generate proposal packet
  -> generate draft SKILL.md scaffold
  -> refine with skill_factory_v1:workflow-to-skill
  -> publish final reusable skill
```

## Quickstart

### Install the plugin

```bash
bash install.sh
hermes plugins enable skill_factory_v1
hermes gateway restart
```

### Use it inside Hermes

```text
/skillfactory-status
/skillfactory-last
/skillfactory-export
/skillfactory-propose
```

### Use it from the terminal

```bash
hermes skill-factory-v1 recent --limit 5
hermes skill-factory-v1 status
hermes skill-factory-v1 export --session-id <sid>
hermes skill-factory-v1 propose --session-id <sid> --skill-name <name>
```

## Example outputs

This repo includes synthetic examples generated from the real implementation:

- `examples/example-export.md`
- `examples/example-proposal.md`
- `examples/example-draft.SKILL.md`

These are included so the output shape is easy to inspect without exposing real user session data.

## Recommended usage pattern

1. Let the plugin observe a real workflow.
2. Export the captured session.
3. Generate a proposal packet and draft scaffold.
4. Load `skill_factory_v1:workflow-to-skill`.
5. Convert the exported artifact into a reusable, reviewed skill.
6. Publish only after refinement and verification.

## Repository layout

```text
hermes-skill-automation/
├── .gitignore
├── ACKNOWLEDGMENTS.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── examples/
│   ├── README.md
│   ├── example-draft.SKILL.md
│   ├── example-export.md
│   └── example-proposal.md
├── install.sh
├── plugin/
│   └── skill_factory_v1/
│       ├── __init__.py
│       ├── cli.py
│       ├── plugin.yaml
│       ├── state.py
│       └── skills/
│           └── workflow-to-skill/
│               └── SKILL.md
├── pyproject.toml
├── skills/
│   └── workflow-to-skill/
│       └── SKILL.md
└── tests/
    ├── test_plugin_registration.py
    └── test_state.py
```

## Attribution

This repository builds on the original idea and public base repo from:

- [Romanescu11/hermes-skill-factory](https://github.com/Romanescu11/hermes-skill-factory)

That repo was the conceptual and structural starting point for this work.

This implementation reworked the idea into a stricter Hermes-native version centered on:

- current plugin compatibility
- deterministic hook-visible evidence
- explicit proposal handoff instead of overstated automation

See `ACKNOWLEDGMENTS.md` for the explicit credit note.

## Development

Run tests:

```bash
pytest
```

What is currently covered:

- plugin registration of hooks, slash commands, CLI commands, and helper skill
- session recording
- export generation
- proposal generation
- recent-session and last-session views

## Public artifact readiness

This repo is prepared to be shared publicly.

Included handoff materials:

- `CONTRIBUTING.md` — contribution standards and scope boundaries
- `examples/README.md` — explains how sample artifacts were produced
- `examples/example-export.md` — synthetic workflow export
- `examples/example-proposal.md` — synthetic proposal packet
- `examples/example-draft.SKILL.md` — synthetic draft skill scaffold

## Honest limitations

This repo intentionally does **not** claim more than it can prove.

Current limitations:

- it does **not** auto-generate complete plugin implementations from observed workflows
- it does **not** auto-run an LLM proposal at session end
- it does **not** inspect full raw conversation history directly
- it captures **hook-visible evidence**, not total session semantics
- proposal generation is **scaffold-first**, then **agent-assisted refinement**

Those are deliberate scope cuts to keep the system correct, auditable, and compatible with current Hermes.

## When this is the right tool

Use this repo when you want to:

- preserve valuable repeated workflows
- turn real Hermes usage into reusable skills
- keep the evidence chain inspectable
- avoid pretending the platform already supports fully autonomous skill synthesis

## License

MIT
