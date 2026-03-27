# Claude Skill Test

这个仓库用于存放和发布可复用的 Claude / Agent 技能包。

当前已整理并发布的技能：

- `skills/ai-dev-team`

## `ai-dev-team` 是什么

`ai-dev-team` 用于为单项目或多项目工作流组建一个可执行的 AI 开发团队，覆盖：

- 需求拆解
- 并行研发
- 代码评审
- 测试验证
- teammate 消息协作
- 多项目协调

这个版本已经按“可发布、可复用、可落地”的方向整理过，重点解决了以下问题：

- 不再默认扫描整个工作区乱建团
- 默认采用最小可用团队，而不是一上来堆很多角色
- 明确兼容不同 Claude 版本下 `Agent` / `Task` 两种 teammate spawn 形态
- 补齐多项目协作策略、角色 prompt 模板和辅助脚本

## 仓库结构

```text
.
├── README.md
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

## 快速开始

1. 将 `skills/ai-dev-team` 复制到你的 Claude skill 目录，例如 `~/.agents/skills/ai-dev-team`。
2. 验证 skill frontmatter：

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py ~/.agents/skills/ai-dev-team
```

3. 在 Claude 中通过如下表达触发：

- “创建 AI 开发小队”
- “创建开发团队”
- “ai-dev-team”
- “组建研发团队”

4. 如果想先得到推荐的团队拓扑，可以运行：

```bash
python3 skills/ai-dev-team/scripts/suggest_team_setup.py /path/to/project
```

5. 如果想直接生成整套团队协作 JSON 示例，可以运行：

```bash
python3 skills/ai-dev-team/scripts/generate_team_examples.py --project-path /path/to/project
```

## 文档

详细安装方式、调用步骤、脚本说明、单项目 / 多项目示例见：

- [docs/ai-dev-team-usage.md](docs/ai-dev-team-usage.md)
- [docs/ai-dev-team-usage.en.md](docs/ai-dev-team-usage.en.md)

## 适用人群

这个 skill 适合：

- 需要把一个较大任务拆成多角色并行推进的个人开发者
- 想把 team lead / developer / reviewer / tester 协作模式沉淀成固定套路的人
- 想在 Claude Team 工具存在版本差异时仍然稳定落地的人

不适合：

- 单文件小改动
- 一次性简单问答
- 没有清晰项目边界、但想让 skill 自动接管整个工作区的场景
