#!/usr/bin/env python3
"""
Generate example JSON payloads for ai-dev-team workflows.

Usage:
    python3 scripts/generate_team_examples.py --project-path /abs/path
    python3 scripts/generate_team_examples.py --project-path /abs/path --roles developer reviewer
    python3 scripts/generate_team_examples.py --project-path /abs/path --output ./examples/team.json
    python3 scripts/generate_team_examples.py --project-path /abs/path --format markdown --output ./examples/team.md
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from render_role_prompt import TEMPLATES, render_prompt
from suggest_team_setup import build_team_spec, starter_tasks as suggest_starter_tasks


def teammate_payloads(
    roles: list[str], project_name: str, project_path: str, team_name: str
) -> dict[str, list[dict[str, Any]]]:
    agent_tool = []
    task_tool = []
    for role in roles:
        prompt = render_prompt(role, project_name, project_path)
        common = {
            "name": role,
            "description": f"{role} role for {project_name}",
            "prompt": prompt,
            "subagent_type": "general-purpose",
            "team_name": team_name,
            "run_in_background": True,
        }
        agent_tool.append({"tool": "Agent", "input": common})
        task_tool.append({"tool": "Task", "input": common})
    return {
        "spawn_with_agent_tool": agent_tool,
        "spawn_with_task_tool": task_tool,
    }


def task_create_examples(starter_tasks: list[dict[str, str]]) -> list[dict[str, Any]]:
    return [{"tool": "TaskCreate", "input": task} for task in starter_tasks]


def message_examples(team_name: str, primary_role: str) -> dict[str, dict[str, Any]]:
    return {
        "ready_report": {
            "tool": "SendMessage",
            "input": {
                "type": "message",
                "recipient": "team-lead",
                "summary": f"{primary_role} ready",
                "content": (
                    f"{primary_role} 已就绪。已阅读 README、依赖清单和关键目录，"
                    "可以开始接收任务。"
                ),
            },
        },
        "task_assignment": {
            "tool": "SendMessage",
            "input": {
                "type": "message",
                "recipient": primary_role,
                "summary": "Task #1 assignment",
                "content": (
                    "这是 Task #1。\n\n"
                    "主题：Read and map the codebase\n"
                    "目标：理解项目结构、入口、关键模块和测试方式\n"
                    "完成后请用 TaskUpdate 更新状态，并通过 SendMessage 回复 team-lead。"
                ),
            },
        },
        "shutdown_request": {
            "tool": "SendMessage",
            "input": {
                "type": "shutdown_request",
                "recipient": primary_role,
                "reason": f"{team_name} 当前批次任务已完成，请停止接收新任务",
            },
        },
    }


def dump_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def render_markdown(output: dict[str, Any]) -> str:
    sections = [
        "# ai-dev-team Workflow Examples",
        "",
        f"- Project: `{output['project_name']}`",
        f"- Project Path: `{output['project_path']}`",
        f"- Team Name: `{output['team_name']}`",
        f"- Roles: `{', '.join(output['roles'])}`",
        "",
        "## TeamCreate",
        "",
        "```json",
        dump_json(output["team_create"]),
        "```",
        "",
        "## Spawn Teammates with Agent",
        "",
        "```json",
        dump_json(output["teammates"]["spawn_with_agent_tool"]),
        "```",
        "",
        "## Spawn Teammates with Task",
        "",
        "```json",
        dump_json(output["teammates"]["spawn_with_task_tool"]),
        "```",
        "",
        "## Starter Tasks",
        "",
        "```json",
        dump_json(output["starter_tasks"]),
        "```",
        "",
        "## Messages",
        "",
        "```json",
        dump_json(output["messages"]),
        "```",
        "",
    ]
    return "\n".join(sections)


def infer_format(explicit_format: str | None, output_path: str | None) -> str:
    if explicit_format in {"json", "markdown"}:
        return explicit_format
    if explicit_format == "md":
        return "markdown"
    if output_path:
        suffix = Path(output_path).suffix.lower()
        if suffix in {".md", ".markdown"}:
            return "markdown"
    return "json"


def render_output(output: dict[str, Any], output_format: str) -> str:
    if output_format == "markdown":
        return render_markdown(output)
    return dump_json(output)


def write_output(content: str, output_path: str | None) -> None:
    if not output_path:
        sys.stdout.write(content + ("\n" if not content.endswith("\n") else ""))
        return

    destination = Path(output_path).expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content + ("\n" if not content.endswith("\n") else ""))
    sys.stdout.write(f"Wrote {destination}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate ai-dev-team example payloads.")
    parser.add_argument("--project-path", required=True, help="Absolute project directory")
    parser.add_argument("--project-name", help="Override project name")
    parser.add_argument("--team-name", help="Override team name")
    parser.add_argument(
        "--output",
        help="Optional output file path. If omitted, prints to stdout.",
    )
    parser.add_argument(
        "--format",
        choices=["json", "markdown", "md"],
        help="Optional output format. Defaults to json, or infers markdown from .md output files.",
    )
    parser.add_argument(
        "--roles",
        nargs="+",
        choices=sorted(TEMPLATES.keys()),
        help="Optional explicit role list. Defaults to suggested roles for the project.",
    )
    args = parser.parse_args()

    project_dir = Path(args.project_path).expanduser().resolve()
    if not project_dir.exists() or not project_dir.is_dir():
        raise SystemExit(f"Project path not found or not a directory: {args.project_path}")

    project_path = str(project_dir)
    spec = build_team_spec(project_dir)
    project_name = args.project_name or spec["project_name"]
    team_name = args.team_name or spec["team_name"]
    roles = args.roles or [role["name"] for role in spec["roles"]]
    starter_task_roles = [{"name": role, "reason": "explicitly selected"} for role in roles]
    starter_tasks = (
        suggest_starter_tasks({"project_name": project_name}, starter_task_roles)
        if args.roles
        else spec["starter_tasks"]
    )

    output = {
        "project_name": project_name,
        "project_path": project_path,
        "team_name": team_name,
        "roles": roles,
        "team_create": {
            "tool": "TeamCreate",
            "input": {
                "team_name": team_name,
                "description": f"{project_name} project AI development team",
            },
        },
        "teammates": teammate_payloads(roles, project_name, project_path, team_name),
        "starter_tasks": task_create_examples(starter_tasks),
        "messages": message_examples(team_name, roles[0]),
    }

    output_format = infer_format(args.format, args.output)
    write_output(render_output(output, output_format), args.output)


if __name__ == "__main__":
    main()
