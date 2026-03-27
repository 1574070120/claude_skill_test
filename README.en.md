# Claude Skill Test

English README for repository users. For the Chinese version, see [README.md](README.md).

This repository packages reusable Claude / Agent skills for practical project work.

Currently published:

- `skills/ai-dev-team`

## What `ai-dev-team` Does

`ai-dev-team` helps Claude coordinate a practical AI development team for one project or a small set of related projects. It covers:

- requirement breakdown
- parallel implementation
- code review
- testing and validation
- teammate messaging
- multi-project coordination

This package is intentionally pragmatic:

- it does not scan your whole workspace by default
- it starts with the smallest useful team
- it supports both `Agent` and `Task` teammate spawn shapes
- it includes prompt templates, tool payload references, and helper scripts

## Repository Layout

```text
.
├── README.md
├── README.en.md
├── docs/
│   ├── ai-dev-team-usage.en.md
│   └── ai-dev-team-usage.md
└── skills/
    └── ai-dev-team/
        ├── SKILL.md
        ├── agents/
        │   └── openai.yaml
        ├── references/
        │   ├── multi-project-mode.md
        │   ├── role-prompts.md
        │   └── tool-shapes.md
        └── scripts/
            ├── generate_team_examples.py
            ├── render_role_prompt.py
            └── suggest_team_setup.py
```

## Quick Start

1. Copy or symlink the skill into your local Claude skill directory:

```bash
mkdir -p ~/.agents/skills
ln -s "$(pwd)/skills/ai-dev-team" ~/.agents/skills/ai-dev-team
```

2. Validate the skill structure:

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py ~/.agents/skills/ai-dev-team
```

3. Trigger it in Claude with prompts such as:

- `create an AI dev team`
- `create a development team`
- `ai-dev-team`

4. Generate a suggested team topology:

```bash
python3 skills/ai-dev-team/scripts/suggest_team_setup.py /path/to/project
```

5. Render a teammate startup prompt:

```bash
python3 skills/ai-dev-team/scripts/render_role_prompt.py \
  --role developer \
  --project-name env_manager \
  --project-path /path/to/project
```

6. Generate workflow examples as JSON:

```bash
python3 skills/ai-dev-team/scripts/generate_team_examples.py \
  --project-path /path/to/project
```

7. Write workflow examples to a file:

```bash
python3 skills/ai-dev-team/scripts/generate_team_examples.py \
  --project-path /path/to/project \
  --output ./examples/team-workflow.json
```

8. Generate a Markdown handoff artifact:

```bash
python3 skills/ai-dev-team/scripts/generate_team_examples.py \
  --project-path /path/to/project \
  --format markdown \
  --output ./examples/team-workflow.md
```

## Documentation

Detailed installation, usage flow, and script references:

- [docs/ai-dev-team-usage.en.md](docs/ai-dev-team-usage.en.md)
- [docs/ai-dev-team-usage.md](docs/ai-dev-team-usage.md)

## When This Skill Fits

Use it when:

- the work is large enough to split across roles
- you want Claude to act as a team lead instead of a single worker
- you need structured teammate coordination over multiple tasks

Avoid it when:

- the task is a tiny one-file change
- a single assistant can do the work faster
- project boundaries are unclear
