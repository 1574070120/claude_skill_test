#!/usr/bin/env python3
"""
Suggest an AI team topology and starter tasks for one or more project paths.

Usage:
    python3 scripts/suggest_team_setup.py /path/to/project
    python3 scripts/suggest_team_setup.py --mode multi /path/a /path/b
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "project"


def team_name_for(project_name: str) -> str:
    slug = slugify(project_name)
    return slug if slug.endswith("-team") else f"{slug}-team"


def has_any(path: Path, names: list[str]) -> bool:
    return any((path / name).exists() for name in names)


def safe_read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def package_json_signals(path: Path) -> dict[str, bool]:
    pkg = path / "package.json"
    if not pkg.exists():
        return {}
    data = safe_read_json(pkg)
    deps: dict[str, Any] = {}
    deps.update(data.get("dependencies") or {})
    deps.update(data.get("devDependencies") or {})
    keys = set(deps.keys())
    return {
        "react": "react" in keys or "next" in keys,
        "vue": "vue" in keys or "nuxt" in keys,
        "angular": "@angular/core" in keys,
        "node_backend": any(
            key in keys for key in ["express", "koa", "fastify", "nestjs", "@nestjs/core"]
        ),
        "ui_heavy": any(
            key in keys
            for key in ["react", "next", "vue", "nuxt", "@angular/core", "svelte", "solid-js"]
        ),
    }


def detect_project(path: Path) -> dict[str, Any]:
    pkg_signals = package_json_signals(path)
    markers = {
        "package_json": (path / "package.json").exists(),
        "go_mod": (path / "go.mod").exists(),
        "pom_xml": (path / "pom.xml").exists(),
        "pyproject": (path / "pyproject.toml").exists(),
        "requirements": has_any(path, ["requirements.txt", "requirements-dev.txt"]),
        "cargo": (path / "Cargo.toml").exists(),
        "flutter": (path / "pubspec.yaml").exists(),
        "swift": has_any(path, ["Package.swift"]) or bool(list(path.glob("*.xcodeproj"))),
    }

    project_type = []
    if markers["go_mod"]:
        project_type.append("go")
    if markers["pom_xml"]:
        project_type.append("java")
    if markers["pyproject"] or markers["requirements"]:
        project_type.append("python")
    if markers["cargo"]:
        project_type.append("rust")
    if markers["flutter"]:
        project_type.append("flutter")
    if markers["swift"]:
        project_type.append("swift")
    if markers["package_json"]:
        project_type.append("node")

    frontend = bool(
        pkg_signals.get("react")
        or pkg_signals.get("vue")
        or pkg_signals.get("angular")
        or markers["flutter"]
        or markers["swift"]
    )
    backend = bool(
        markers["go_mod"]
        or markers["pom_xml"]
        or markers["pyproject"]
        or markers["requirements"]
        or pkg_signals.get("node_backend")
    )
    ui_heavy = bool(pkg_signals.get("ui_heavy") or markers["flutter"] or markers["swift"])

    return {
        "path": str(path.resolve()),
        "project_name": path.name,
        "team_name": team_name_for(path.name),
        "markers": markers,
        "signals": pkg_signals,
        "project_type": project_type or ["unknown"],
        "frontend": frontend,
        "backend": backend,
        "ui_heavy": ui_heavy,
    }


def choose_roles(info: dict[str, Any]) -> list[dict[str, str]]:
    roles: list[dict[str, str]] = []
    if info["frontend"] and info["backend"]:
        roles.extend(
            [
                {"name": "frontend-dev", "reason": "UI and client-side delivery"},
                {"name": "backend-dev", "reason": "API and service delivery"},
                {"name": "tester", "reason": "Cross-boundary verification"},
            ]
        )
    elif info["frontend"]:
        roles.extend(
            [
                {"name": "frontend-dev", "reason": "Primary implementation role"},
                {"name": "reviewer", "reason": "Independent review and regression check"},
            ]
        )
    elif info["backend"]:
        roles.extend(
            [
                {"name": "backend-dev", "reason": "Primary implementation role"},
                {"name": "reviewer", "reason": "Independent review and risk check"},
            ]
        )
    else:
        roles.extend(
            [
                {"name": "developer", "reason": "General implementation role"},
                {"name": "reviewer", "reason": "Independent review"},
            ]
        )

    if info["ui_heavy"]:
        roles.append({"name": "designer", "reason": "UI and interaction guidance"})
    return roles


def starter_tasks(info: dict[str, Any], roles: list[dict[str, str]]) -> list[dict[str, str]]:
    tasks = [
        {
            "subject": "Read and map the codebase",
            "description": (
                f"Read README, dependency files, entrypoints, and key directories in {info['project_name']}. "
                "Summarize architecture, major flows, and obvious risks."
            ),
            "activeForm": "Reading and mapping the codebase",
        }
    ]

    role_names = {role["name"] for role in roles}
    if "product-manager" in role_names:
        tasks.append(
            {
                "subject": "Draft task breakdown and acceptance criteria",
                "description": "Turn the user goal into executable tasks with scope, acceptance criteria, and sequencing.",
                "activeForm": "Drafting task breakdown",
            }
        )
    if "frontend-dev" in role_names:
        tasks.append(
            {
                "subject": "Audit frontend entrypoints and state",
                "description": "Inspect pages, routes, components, and state management. Identify the smallest safe frontend slice to implement first.",
                "activeForm": "Auditing frontend entrypoints",
            }
        )
    if "backend-dev" in role_names:
        tasks.append(
            {
                "subject": "Audit backend entrypoints and API surface",
                "description": "Inspect service entrypoints, modules, handlers, and tests. Identify the smallest safe backend slice to implement first.",
                "activeForm": "Auditing backend entrypoints",
            }
        )
    if "reviewer" in role_names:
        tasks.append(
            {
                "subject": "Prepare review checklist",
                "description": "List likely regression areas, missing tests, and code review focus points based on current project structure.",
                "activeForm": "Preparing review checklist",
            }
        )
    if "tester" in role_names:
        tasks.append(
            {
                "subject": "Map validation paths",
                "description": "Identify existing test framework, executable test commands, and highest-risk manual verification paths.",
                "activeForm": "Mapping validation paths",
            }
        )
    if "designer" in role_names:
        tasks.append(
            {
                "subject": "Review UI structure and design constraints",
                "description": "Inspect existing UI surfaces, design system usage, and interaction hotspots before proposing changes.",
                "activeForm": "Reviewing UI structure",
            }
        )
    return tasks


def build_team_spec(path: Path) -> dict[str, Any]:
    info = detect_project(path)
    roles = choose_roles(info)
    return {
        "project_name": info["project_name"],
        "project_path": info["path"],
        "team_name": info["team_name"],
        "project_type": info["project_type"],
        "frontend": info["frontend"],
        "backend": info["backend"],
        "ui_heavy": info["ui_heavy"],
        "roles": roles,
        "starter_tasks": starter_tasks(info, roles),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Suggest team topology and starter tasks.")
    parser.add_argument(
        "--mode",
        choices=["single", "multi"],
        default="single",
        help="Whether to treat the provided paths as one active project or multiple coordinated projects.",
    )
    parser.add_argument("project_paths", nargs="+", help="One or more project directories")
    args = parser.parse_args()

    specs = []
    for raw_path in args.project_paths:
        path = Path(raw_path).expanduser().resolve()
        if not path.exists() or not path.is_dir():
            raise SystemExit(f"Project path not found or not a directory: {raw_path}")
        specs.append(build_team_spec(path))

    output: dict[str, Any] = {"mode": args.mode, "teams": specs}
    if args.mode == "multi":
        output["coordination_notes"] = [
            "Create at most 2-3 active teams unless the user explicitly asks for more parallelism.",
            "Route cross-team dependencies through team lead messages.",
            "Keep shared-library work isolated from app-specific work.",
        ]

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
