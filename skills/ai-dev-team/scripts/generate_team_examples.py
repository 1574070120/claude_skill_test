#!/usr/bin/env python3
"""
Generate example JSON payloads for ai-dev-team workflows.

Usage:
    python3 scripts/generate_team_examples.py --project-path /abs/path
    python3 scripts/generate_team_examples.py --project-path /abs/path --roles developer reviewer
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate ai-dev-team example payloads.")
    parser.add_argument("--project-path", required=True, help="Absolute project directory")
    parser.add_argument("--project-name", help="Override project name")
    parser.add_argument("--team-name", help="Override team name")
    parser.add_argument(
        "--roles",
        nargs="*",
        choices=sorted(TEMPLATES.keys()),
        help="Optional explicit role list. Defaults to suggested roles for the project.",
    )
    args = parser.parse_args()

    project_path = str(Path(args.project_path).expanduser().resolve())
    spec = build_team_spec(Path(project_path))
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

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
