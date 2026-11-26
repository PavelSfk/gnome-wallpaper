# Agent Guidelines for This Project

## 1. Context — read minimally and intentionally
Before every change:
1. `docs/ai-context.md` — current project state (brief and technical)
2. `docs/decisions.md` — only when the change affects the architecture
3. Code: locate it with `grep`, `ripgrep`, or symbol search instead of reading entire directories
4. Read only the file sections required for the task, not whole files unless necessary

Do not read:
- `README.md` as working context (it is documentation for people)
- `.env*`, `*.pem`, `secrets/`, keys, or credentials
- `node_modules/`, `dist/`, `build/`, lock files, or large binary files
- conversation history or assumptions when the state can be verified in files

## 2. Editing code
- Make focused diffs or patches at specific locations; do not rewrite entire files unnecessarily
- Do not paste repository file contents back into responses; the user can see them in the editor
- Priorities: simplicity > readability > stable architecture > compact context
- Keep logic separated, with one responsibility per module or function

## 3. Project memory — three files with distinct roles

**`docs/ai-context.md`** — the state *now*, not history.
What the project does / architecture / modules / what works / next step / what is not being done yet.
Keep it compact by replacing outdated information instead of appending.

**`docs/decisions.md`** — only decisions that change how the project is built.
Format: date / decision / reason / consequence.
Mark an old decision as `superseded by <date/link>` instead of deleting it.

**`docs/changelog.md`** — history of significant changes.
Format: what / why / effect. Exclude typo fixes and cosmetic changes.

Optionally use `docs/current-status.md` with three lines: works / does not work / next step. Use it when work spans multiple sessions.

## 4. When to update each file
Update `changelog.md` when a change affects more than one module, adds or removes a dependency, changes a contract or API, or is difficult to reverse.
Update `decisions.md` only when changing *how* something is built, not for an individual bug fix.
Update `ai-context.md` when the current state or architecture changes, not after every modification.

Minor fixes such as typos, formatting, or a small bug fix with no architectural impact **do not require** updates to these files.

Rule: do not duplicate information between files. If something is in `ai-context.md`, do not repeat it in `changelog.md`.

## 5. Response format — based on the size of the change
**Micro change** (typo or small fix): briefly state what changed and where.
**Functional or architectural change**: (1) what is changing and why, (2) specific diff/files, (3) a short note for `changelog.md` and, when architectural, `decisions.md`.

## 6. Primary goal
After 100 changes, a person or another agent should be able to quickly determine:
what is current / why decisions were made / what changed recently / what comes next —
without reading the entire repository history.
