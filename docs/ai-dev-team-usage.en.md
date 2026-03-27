# AI Dev Team Usage Guide

This document is the English usage guide for the `ai-dev-team` skill package.

## Goal

`ai-dev-team` is designed to help Claude act as a practical team lead for a real software project. The goal is not to create more agents for the sake of it. The goal is to:

- start the smallest useful team
- split work into executable tasks
- coordinate implementation, review, and validation
- keep cross-role communication structured
- avoid uncontrolled multi-repo sprawl

## What the Skill Includes

The published package contains:

- `SKILL.md`: the core workflow and invocation rules
- `references/role-prompts.md`: reusable teammate prompt templates
- `references/tool-shapes.md`: example payload shapes for team tools
- `references/multi-project-mode.md`: rules for multi-repo coordination
- `scripts/render_role_prompt.py`: render a role-specific startup prompt
- `scripts/suggest_team_setup.py`: suggest a team topology and starter tasks
- `scripts/generate_team_examples.py`: generate example JSON payloads for team workflows

## Installation

Assuming you cloned this repository already:

### Option A: Copy

```bash
mkdir -p ~/.agents/skills
cp -R skills/ai-dev-team ~/.agents/skills/ai-dev-team
```

### Option B: Symlink

```bash
mkdir -p ~/.agents/skills
ln -s "$(pwd)/skills/ai-dev-team" ~/.agents/skills/ai-dev-team
```

### Validate

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py ~/.agents/skills/ai-dev-team
```

Expected output:

```text
Skill is valid!
```

## When to Use It

Use this skill when:

- the user explicitly asks to create a team
- the work is large enough to split across implementation, review, and testing
- you want Claude to coordinate teammate progress over multiple tasks

Do not use it when:

- the task is a small one-file edit
- a single assistant can do the work faster
- project boundaries are unclear and you are tempted to auto-scan everything

## Core Rules

The skill enforces a few important constraints:

- default to the current `cwd` or an explicitly named project path
- start with a minimal team instead of many roles
- only enter multi-project mode when the user clearly needs it
- keep tasks concrete, scoped, and verifiable

## Single-Project Workflow

### 1. Suggest a team topology

Run:

```bash
python3 skills/ai-dev-team/scripts/suggest_team_setup.py /path/to/project
```

This returns:

- a suggested `team_name`
- recommended roles
- starter tasks

### 2. Render teammate prompts

Example:

```bash
python3 skills/ai-dev-team/scripts/render_role_prompt.py \
  --role developer \
  --project-name env_manager \
  --project-path /Users/liliguo/IdeaProjects/env_manager
```

The output is ready to use as the `prompt` field when spawning a teammate.

### 3. Generate workflow examples

Example:

```bash
python3 skills/ai-dev-team/scripts/generate_team_examples.py \
  --project-path /Users/liliguo/IdeaProjects/create_data_util
```

This returns example payloads for:

- `TeamCreate`
- teammate spawn using `Agent`
- teammate spawn using `Task`
- `TaskCreate`
- `SendMessage`
- `shutdown_request`

Use it when you want a quick scaffold instead of writing JSON by hand.

To write the result to a file:

```bash
python3 skills/ai-dev-team/scripts/generate_team_examples.py \
  --project-path /Users/liliguo/IdeaProjects/create_data_util \
  --output ./examples/create-data-util-team.json
```

To generate a Markdown handoff document instead:

```bash
python3 skills/ai-dev-team/scripts/generate_team_examples.py \
  --project-path /Users/liliguo/IdeaProjects/create_data_util \
  --format markdown \
  --output ./examples/create-data-util-team.md
```

### 4. Create the team

Typical shape:

```json
{
  "team_name": "env-manager-team",
  "description": "env_manager project AI development team"
}
```

### 5. Spawn teammates

Claude environments may differ. Older sessions often use `Agent`. Newer sessions may use `Task` for teammate spawning. The important fields stay mostly the same:

- `name`
- `prompt`
- `team_name`
- `subagent_type`
- `run_in_background`

### 6. Let teammates read first

Each teammate should:

- read the README
- read dependency files
- inspect key directories
- report readiness via `SendMessage`

### 7. Create real tasks

Good task payloads contain:

- a clear subject
- a concrete scope
- acceptance criteria
- dependencies or blockers
- a verification path

Bad example:

```text
fix login
```

Good example:

```json
{
  "subject": "Implement authentication module",
  "description": "Implement login flow, auth middleware, and baseline tests in auth/ related directories. Acceptance criteria: login succeeds, auth failures are handled, tests pass.",
  "activeForm": "Implementing authentication module"
}
```

### 8. Coordinate with short messages

Use `SendMessage` to send short, contextual, action-oriented messages.

Example:

```json
{
  "type": "message",
  "recipient": "developer",
  "summary": "Task #3 ready for review",
  "content": "Task #3 is complete. Files touched: src/auth/*. Please focus on token refresh logic and error handling."
}
```

### 9. Close the loop

Before shutdown, collect from each teammate:

- what changed
- what was validated
- what risks remain

Then send a shutdown request.

## Multi-Project Workflow

Only use multi-project mode when:

- the user explicitly wants multiple repositories in parallel
- one change clearly spans frontend, backend, or shared-library repos
- the product is intentionally split across repos

Suggested helper command:

```bash
python3 skills/ai-dev-team/scripts/suggest_team_setup.py --mode multi /path/a /path/b
```

This returns:

- one team suggestion per project
- recommended roles
- starter tasks
- coordination notes

For deeper rules, read:

- `skills/ai-dev-team/references/multi-project-mode.md`

## Helper Scripts

### `render_role_prompt.py`

Use it when you already know the role and just want a ready-to-paste teammate prompt.

### `suggest_team_setup.py`

Use it when you want a lightweight inference of team topology from the project path.

### `generate_team_examples.py`

Use it when you want ready-made team workflow examples.

Notes:

- default output is pretty JSON to stdout
- `--output` writes the result to a file
- `--format markdown` renders a shareable Markdown artifact
- if `--output` ends with `.md`, Markdown is inferred automatically unless `--format` is set explicitly

## Common Mistakes

### Starting too many roles

Problem:

- coordination cost exceeds execution value

Fix:

- start with `developer + reviewer/tester`

### Creating teams without boundaries

Problem:

- teammates drift into unrelated repos

Fix:

- explicitly scope the project path first

### Writing vague tasks

Problem:

- teammates produce unstable or inconsistent results

Fix:

- define goal, scope, acceptance criteria, and verification

### Letting cross-team dependencies float

Problem:

- the user loses track of real blockers

Fix:

- route all cross-team dependencies through the team lead

## Maintenance

When you update this skill package later, use this order:

1. update `SKILL.md`
2. update `references/`
3. update `scripts/`
4. update repository docs

That keeps the published package and its documentation aligned.
