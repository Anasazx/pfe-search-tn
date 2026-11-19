# pfe-search-tn

PFE (projet de fin d'études) internship search automation for Tunisian students.
Free Python core (`python -m pfe …`); Claude Code slash commands in `.claude/commands/` add AI writing on top.

## Layout
- `pfe/sources/`: one module per job board, each exposing `fetch()`. The offer schema is documented in `pfe/sources/__init__.py`.
- `pfe/rules.py`: extracts company application rules (emails, max subjects, reference, subject format, documents, deadline).
- `pfe/rank.py`: scoring (skills 65, level 20, domain 10, location 5). `pfe/skills.py` holds the skill → regex catalog.
- `pfe/drafts.py`: template email and `.eml` writer. `pfe/tracker.py`: `data/applications.json`.
- `pfe/cli.py`: all commands. `docs/email-guide.md`: rules for every AI-written email.

## Private data (gitignored, never commit)
`me/` (profile + CV), `data/` (offers, applications), `output/` (reports, drafts).

## Working rules
- Never invent CV facts in emails or profiles. Only use `me/` and what the student says.
- Never send email on the student's behalf. Produce `.eml` drafts; the student sends.
- Respect each company's rules from `python -m pfe show <id>` (max subjects, subject format).
- Keep the core free of AI/API dependencies: anything needing an LLM belongs in a slash command.
- Tests: `python -m unittest discover tests`. Add a test when fixing a rules/ranking parsing bug.
