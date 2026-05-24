---
name: workflow-to-skill
description: Use when you have a Hermes Skill Automation workflow export and want to convert it into a polished reusable Hermes skill.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [skills, workflow-capture, hermes, authoring]
    related_skills: [hermes-agent, hermes-agent-skill-authoring, writing-plans]
---

# Workflow To Skill

## Overview

Use this skill after Hermes Skill Automation exports a deterministic workflow summary from a real Hermes session. The export is evidence, not the final skill. Your job is to turn that evidence into a clean, reusable `SKILL.md` that captures triggers, ordered steps, pitfalls, and verification checks.

The core rule: **do not pretend the export contains more than it does**. If a step or rationale is missing, mark it explicitly as needing confirmation or infer only the minimum necessary to make the skill usable.

## When to Use

Use this skill when:
- you have a markdown export produced by `/skillfactory-export`
- a user says "save this workflow as a skill"
- you want to turn repeated tool usage into procedural memory

Do not use this skill when:
- the captured session is too small or too noisy to generalize
- the workflow was clearly one-off
- an existing skill already covers the workflow better than a new one would

## Workflow

### Phase 1: Read the evidence

1. Read the exported markdown file.
2. Identify:
   - the likely workflow goal
   - the most repeated tools
   - the rough order of operations
   - any missing steps or ambiguities
3. Decide whether the workflow is worth capturing as:
   - a new skill, or
   - an edit to an existing skill

### Phase 2: Normalize into a reusable workflow

Transform the export into:
- a clear trigger sentence beginning with "Use when ..."
- a concise description of the goal
- ordered phases and steps
- a short pitfalls section
- a verification checklist

Do not blindly copy raw event timelines into the final skill.

### Phase 3: Write the skill

When creating a user-local skill, prefer `skill_manage(action='create')` with:
- a kebab-case name
- concise but concrete frontmatter
- a body that explains both **what** to do and **why**

Minimum structure:
- `# Title`
- `## Overview`
- `## When to Use`
- `## Workflow`
- `## Common Pitfalls`
- `## Verification Checklist`

## Common Pitfalls

1. **Overfitting to one session**
   - Remove incidental details that are not part of the reusable workflow.

2. **Inventing hidden reasoning**
   - If the export only shows tool calls, do not claim exact human reasoning unless it was explicit.

3. **Capturing noise instead of procedure**
   - Repeated `read_file` calls may just be exploration; the skill should encode the actual method.

4. **Creating a new skill when a patch is better**
   - Check whether an existing skill should simply be improved.

## Verification Checklist

- [ ] The workflow has a clear trigger condition
- [ ] The skill goal is obvious from the title and description
- [ ] Steps are ordered and actionable
- [ ] Any inferred details are minimal and clearly justified
- [ ] Pitfalls and verification are included
- [ ] The resulting skill would help on a future session, not just document the past one
