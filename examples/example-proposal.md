# Skill Factory Proposal Packet — demo-session-001

## Intent
This packet is meant for an LLM agent session, not as a final skill by itself.
Use it to create or refine a reusable `SKILL.md` with human review.

## Candidate Skill
- Suggested name: `demo-workflow-capture`
- Dominant tools: read_file, search_files, write_file
- Source export: `/tmp/tmp2orcozox/state/exports/demo-session-001.md`

## Agent Prompt
```text
Load `skill_factory_v1:workflow-to-skill`. Read `/tmp/tmp2orcozox/state/exports/demo-session-001.md`. Convert it into a polished reusable Hermes skill named `demo-workflow-capture`. Use only facts present in the export. If a field is missing, mark it as verification required instead of guessing. Return: (1) a proposed skill outline, (2) the final SKILL.md content, and (3) any supporting references/templates worth splitting out.
```

## Observed Tool Pattern
- `read_file` × 2
- `search_files` × 2
- `write_file` × 2

## Review Checklist
- [ ] Skill name matches the actual repeated workflow
- [ ] No inferred steps were added without evidence
- [ ] Pitfalls and verification steps were included
- [ ] Any unresolved facts are marked 'verification required'
