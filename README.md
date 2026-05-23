# Hermes Skill Factory Native v1

A **Hermes-native** implementation of the Skill Factory idea.

This repo does **not** pretend to fully auto-understand a session and emit perfect reusable skills with zero review. Instead, it focuses on the parts that are both **realistic** and **compatible with current Hermes**:

- capture workflow evidence from real Hermes sessions
- persist it across CLI/gateway sessions
- expose slash commands and a CLI surface for inspection/export
- provide a plugin skill for converting captured workflows into polished `SKILL.md` files
- provide a phase-2 proposal handoff that prepares agent-facing packets and draft scaffolds

## Why this exists

The original `hermes-skill-factory` concept is strong, but its implementation assumes a plugin API that does not match current Hermes conventions. Hermes today supports plugins as:

- `plugin.yaml`
- `__init__.py` with `register(ctx)`
- plugin hooks (`pre_tool_call`, `post_tool_call`, `on_session_finalize`, ...)
- plugin slash commands via `ctx.register_command(...)`
- plugin CLI subcommands via `ctx.register_cli_command(...)`
- plugin-provided namespaced skills via `ctx.register_skill(...)`

This repo uses those real extension points.

## What this repo does

### 1. Passive workflow capture
The plugin records:
- tool calls
- session boundary events
- stable metadata visible to current Hermes plugin hooks

State is written to:
- `~/.hermes/plugins/skill_factory_v1/state/sessions/<session_id>.jsonl`
- `~/.hermes/plugins/skill_factory_v1/state/index.json`

### 2. Export captured sessions
The plugin can export a concise markdown workflow summary from hook-visible evidence.

### 3. Phase-2 proposal generation
The plugin can turn a captured session into:
- an **agent-facing proposal packet** with an exact prompt for Hermes
- a **draft `SKILL.md` scaffold** for refinement

This keeps the system honest: deterministic capture first, agent-assisted polishing second.

### 4. In-session slash commands
- `/skillfactory-status`
- `/skillfactory-last`
- `/skillfactory-export [session_id]`
- `/skillfactory-propose [session_id] [skill_name]`

### 5. Operator CLI
- `hermes skill-factory-v1 status [--session-id SID]`
- `hermes skill-factory-v1 export [--session-id SID]`
- `hermes skill-factory-v1 propose [--session-id SID] [--skill-name NAME]`
- `hermes skill-factory-v1 recent [--limit N]`

### 6. Plugin-provided helper skill
The plugin registers a namespaced skill:
- `skill_factory_v1:workflow-to-skill`

Load it explicitly when you want Hermes to convert an exported workflow or proposal packet into a polished reusable skill.

## Why it stops here
A truly automatic “watch silently and generate perfect skill + implementation” flow is still not realistic without either:
- much deeper session introspection APIs
- a privileged agent-turn injection path for gateway sessions
- or a first-class plugin-controlled LLM orchestration path with tool access

So this repo solves the **deterministic capture + explicit handoff** problem first.

## Repo layout

```text
hermes-skill-factory-native/
├── .gitignore
├── LICENSE
├── README.md
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
├── skills/
│   └── workflow-to-skill/
│       └── SKILL.md
└── tests/
    ├── test_plugin_registration.py
    └── test_state.py
```

## Installation

```bash
bash install.sh
hermes plugins enable skill_factory_v1
hermes gateway restart
```

## Usage

### In a Hermes session
```text
/skillfactory-status
/skillfactory-last
/skillfactory-export
/skillfactory-propose
```

### In the terminal
```bash
hermes skill-factory-v1 recent --limit 5
hermes skill-factory-v1 status
hermes skill-factory-v1 export --session-id <sid>
hermes skill-factory-v1 propose --session-id <sid> --skill-name <name>
```

### Converting a capture into a polished skill
1. Run `/skillfactory-export` or `/skillfactory-propose`
2. Copy the exported markdown path or proposal packet path
3. Ask Hermes to load `skill_factory_v1:workflow-to-skill`
4. Ask Hermes to turn that artifact into a reusable skill via `skill_manage`

## Honest limitations
- Does not auto-generate full plugin implementations from workflows
- Does not auto-run an LLM proposal at session end
- Does not inspect raw full conversation history directly; it captures hook-visible events and summarizes them
- Proposal generation is scaffold-first, then agent-assisted refinement

Those are deliberate scope cuts to keep the repo correct and maintainable.
