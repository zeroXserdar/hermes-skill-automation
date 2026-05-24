# Hermes Skill Factory Native v1

> A Hermes-native workflow capture plugin that turns repeated agent sessions into exportable workflow evidence, proposal packets, and draft `SKILL.md` scaffolds.

## Why this repo exists

The original *Skill Factory* idea is strong: when a workflow repeats, Hermes should help turn it into reusable operational knowledge instead of forcing the user to recreate it from scratch every time.

This repo focuses on the part that is both **useful today** and **honest about current Hermes capabilities**:

- capture deterministic evidence from real Hermes plugin hooks
- persist it across sessions
- export a reviewable workflow summary
- generate an agent-facing proposal packet
- generate a draft `SKILL.md` scaffold for refinement

In short: **deterministic capture first, agent-assisted polishing second**.

## What makes this repo different

This is not a hand-wavy prototype that assumes privileged internals or imaginary plugin APIs.
It is grounded in extension points Hermes supports today:

- `plugin.yaml`
- `__init__.py` with `register(ctx)`
- plugin hooks such as `pre_tool_call`, `post_tool_call`, `on_session_finalize`, and `on_session_reset`
- slash commands registered with `ctx.register_command(...)`
- CLI subcommands registered with `ctx.register_cli_command(...)`
- plugin-provided namespaced skills registered with `ctx.register_skill(...)`

That constraint is deliberate. The goal is to ship something real, inspectable, and maintainable.

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

### 6) Plugin-bundled helper skill
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
hermes-skill-factory-native/
├── .gitignore
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
