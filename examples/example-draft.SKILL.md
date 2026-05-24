---
name: demo-workflow-capture
description: "Use when this captured workflow recurs and should become a reusable Hermes skill. Facts not present in the export must remain verification required."
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [read_file, search_files, write_file]
    related_skills: [read_file, search_files, write_file]
---

# demo-workflow-capture

## Overview
Draft scaffold generated from `/tmp/tmp2orcozox/state/exports/demo-session-001.md`.
Refine this with the `skill_factory_v1:workflow-to-skill` helper skill before publishing.

## When to Use
- Use when this workflow repeats often enough to justify a reusable skill.
- If any critical step is not evidenced in the export, mark it as verification required.

## Workflow Evidence
- Source export: `/tmp/tmp2orcozox/state/exports/demo-session-001.md`
- Dominant observed tools: read_file, search_files, write_file

## Draft Procedure
1. Review the source export carefully.
2. Extract only repeated, evidenced steps.
3. Split pitfalls and verification into their own sections.
4. Replace any uncertain detail with 'verification required'.

## Common Pitfalls
1. Inferring intent or missing steps from tool names alone.
2. Publishing the scaffold without human/agent refinement.

## Verification Checklist
- [ ] Every procedure step is grounded in the export
- [ ] Missing facts are marked verification required
- [ ] Tool-specific commands and pitfalls were refined