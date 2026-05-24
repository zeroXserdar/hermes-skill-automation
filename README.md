     1|# Hermes Skill Factory Native v1
     2|
     3|A **Hermes-native** implementation of the Skill Factory idea.
     4|
     5|This repo does **not** pretend to fully auto-understand a session and emit perfect reusable skills with zero review. Instead, it focuses on the parts that are both **realistic** and **compatible with current Hermes**:
     6|
     7|- capture workflow evidence from real Hermes sessions
     8|- persist it across CLI/gateway sessions
     9|- expose slash commands and a CLI surface for inspection/export
    10|- provide a plugin skill for converting captured workflows into polished `SKILL.md` files
    11|- provide a phase-2 proposal handoff that prepares agent-facing packets and draft scaffolds
    12|
    13|## Why this exists
    14|
    15|The original `hermes-skill-factory` concept is strong, but its implementation assumes a plugin API that does not match current Hermes conventions. Hermes today supports plugins as:
    16|
    17|- `plugin.yaml`
    18|- `__init__.py` with `register(ctx)`
    19|- plugin hooks (`pre_tool_call`, `post_tool_call`, `on_session_finalize`, ...)
    20|- plugin slash commands via `ctx.register_command(...)`
    21|- plugin CLI subcommands via `ctx.register_cli_command(...)`
    22|- plugin-provided namespaced skills via `ctx.register_skill(...)`
    23|
    24|This repo uses those real extension points.
    25|
    26|## What this repo does
    27|
    28|### 1. Passive workflow capture
    29|The plugin records:
    30|- tool calls
    31|- session boundary events
    32|- stable metadata visible to current Hermes plugin hooks
    33|
    34|State is written to:
    35|- `~/.hermes/plugins/skill_factory_v1/state/sessions/<session_id>.jsonl`
    36|- `~/.hermes/plugins/skill_factory_v1/state/index.json`
    37|
    38|### 2. Export captured sessions
    39|The plugin can export a concise markdown workflow summary from hook-visible evidence.
    40|
    41|### 3. Phase-2 proposal generation
    42|The plugin can turn a captured session into:
    43|- an **agent-facing proposal packet** with an exact prompt for Hermes
    44|- a **draft `SKILL.md` scaffold** for refinement
    45|
    46|This keeps the system honest: deterministic capture first, agent-assisted polishing second.
    47|
    48|### 4. In-session slash commands
    49|- `/skillfactory-status`
    50|- `/skillfactory-last`
    51|- `/skillfactory-export [session_id]`
    52|- `/skillfactory-propose [session_id] [skill_name]`
    53|
    54|### 5. Operator CLI
    55|- `hermes skill-factory-v1 status [--session-id SID]`
    56|- `hermes skill-factory-v1 export [--session-id SID]`
    57|- `hermes skill-factory-v1 propose [--session-id SID] [--skill-name NAME]`
    58|- `hermes skill-factory-v1 recent [--limit N]`
    59|
    60|### 6. Plugin-provided helper skill
    61|The plugin registers a namespaced skill:
    62|- `skill_factory_v1:workflow-to-skill`
    63|
    64|Load it explicitly when you want Hermes to convert an exported workflow or proposal packet into a polished reusable skill.
    65|
    66|## Why it stops here
    67|A truly automatic “watch silently and generate perfect skill + implementation” flow is still not realistic without either:
    68|- much deeper session introspection APIs
    69|- a privileged agent-turn injection path for gateway sessions
    70|- or a first-class plugin-controlled LLM orchestration path with tool access
    71|
    72|So this repo solves the **deterministic capture + explicit handoff** problem first.
    73|
    74|## Repo layout
    75|
    76|```text
    77|hermes-skill-factory-native/
    78|├── .gitignore
    79|├── LICENSE
    80|├── README.md
    81|├── install.sh
    82|├── plugin/
    83|│   └── skill_factory_v1/
    84|│       ├── __init__.py
    85|│       ├── cli.py
    86|│       ├── plugin.yaml
    87|│       ├── state.py
    88|│       └── skills/
    89|│           └── workflow-to-skill/
    90|│               └── SKILL.md
    91|├── skills/
    92|│   └── workflow-to-skill/
    93|│       └── SKILL.md
    94|└── tests/
    95|    ├── test_plugin_registration.py
    96|    └── test_state.py
    97|```
    98|
    99|## Installation
   100|
   101|```bash
   102|bash install.sh
   103|hermes plugins enable skill_factory_v1
   104|hermes gateway restart
   105|```
   106|
   107|## Usage
   108|
   109|### In a Hermes session
   110|```text
   111|/skillfactory-status
   112|/skillfactory-last
   113|/skillfactory-export
   114|/skillfactory-propose
   115|```
   116|
   117|### In the terminal
   118|```bash
   119|hermes skill-factory-v1 recent --limit 5
   120|hermes skill-factory-v1 status
   121|hermes skill-factory-v1 export --session-id <sid>
   122|hermes skill-factory-v1 propose --session-id <sid> --skill-name <name>
   123|```
   124|
   125|### Converting a capture into a polished skill
   126|1. Run `/skillfactory-export` or `/skillfactory-propose`
   127|2. Copy the exported markdown path or proposal packet path
   128|3. Ask Hermes to load `skill_factory_v1:workflow-to-skill`
   129|4. Ask Hermes to turn that artifact into a reusable skill via `skill_manage`
   130|
   131|## Public repo handoff

This repo is prepared to be shared as a public artifact.

Included handoff materials:
- `CONTRIBUTING.md` — contributor expectations and scope boundaries
- `examples/example-export.md` — synthetic workflow export
- `examples/example-proposal.md` — synthetic proposal packet
- `examples/example-draft.SKILL.md` — synthetic draft skill scaffold
- `examples/README.md` — notes on how the examples were produced

## Honest limitations
   132|- Does not auto-generate full plugin implementations from workflows
   133|- Does not auto-run an LLM proposal at session end
   134|- Does not inspect raw full conversation history directly; it captures hook-visible events and summarizes them
   135|- Proposal generation is scaffold-first, then agent-assisted refinement
   136|
   137|Those are deliberate scope cuts to keep the repo correct and maintainable.
   138|