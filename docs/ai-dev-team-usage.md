# AI Dev Team Usage Guide

这份文档面向“实际使用这个 skill 的人”，不是 skill 内部实现说明。

## 1. 目标

`ai-dev-team` 的目标不是“把更多 agent 拉起来”，而是：

- 在适合并行协作时创建最小可用团队
- 把任务拆成可执行、可跟踪、可回收的工作单元
- 让 team lead 能稳定推进，而不是陷入消息噪音

## 2. 安装

假设你已经 clone 了本仓库。

### 方式 A：直接复制

```bash
mkdir -p ~/.agents/skills
cp -R skills/ai-dev-team ~/.agents/skills/ai-dev-team
```

### 方式 B：软链接

```bash
mkdir -p ~/.agents/skills
ln -s "$(pwd)/skills/ai-dev-team" ~/.agents/skills/ai-dev-team
```

### 校验

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py ~/.agents/skills/ai-dev-team
```

期望输出：

```text
Skill is valid!
```

## 3. 触发方式

当你在 Claude 中说以下任意类似表达时，应触发这个 skill：

- “创建 AI 开发小队”
- “创建开发团队”
- “ai-dev-team”
- “组建研发团队”

## 4. 核心原则

这个 skill 的几个关键约束：

- 默认只围绕当前 `cwd` 或用户明确指定项目建团
- 默认从最小团队开始，而不是一口气拉 6 个以上角色
- 没有明确并行收益时，优先直接做，不强行建团
- 多项目模式必须是用户明确需要，或需求天然跨多个 repo

## 5. 什么时候该用

推荐：

- 一个需求很大，适合拆成研发、评审、测试
- 你明确想让 Claude 做 team lead，而不是单 agent 硬推
- 你希望长期跟踪任务状态和 teammate 消息

不推荐：

- 改一个小 bug
- 只查一个问题
- 当前会话自己直接做更快

## 6. 单项目工作流

下面是一条建议流程。

### 第一步：先看项目边界

如果你不确定这个项目适合什么角色，先跑：

```bash
python3 skills/ai-dev-team/scripts/suggest_team_setup.py /path/to/project
```

输出会包含：

- `team_name`
- 建议角色
- starter tasks

### 第二步：如果需要，生成角色 prompt

例如生成 developer 启动提示词：

```bash
python3 skills/ai-dev-team/scripts/render_role_prompt.py \
  --role developer \
  --project-name env_manager \
  --project-path /Users/liliguo/IdeaProjects/env_manager
```

这个输出可以直接塞进 teammate spawn 的 `prompt` 字段。

### 第三步：创建 team

示例：

```json
{
  "team_name": "env-manager-team",
  "description": "env_manager 项目的 AI 研发团队，负责需求分析、研发、评审和测试"
}
```

### 第四步：拉起 teammate

注意：不同版本 Claude 里，拉起 teammate 的工具可能是：

- `Agent`
- `Task`

它们都可能承担“后台启动 teammate”的功能。

关键参数保持一致：

- `name`
- `prompt`
- `team_name`
- `subagent_type`
- `run_in_background`

示例：

```json
{
  "name": "developer",
  "description": "核心研发角色",
  "prompt": "你是当前项目的研发工程师……",
  "subagent_type": "general-purpose",
  "team_name": "env-manager-team",
  "run_in_background": true
}
```

### 第五步：先熟悉项目，再分派任务

每个 teammate 启动后应先：

- 阅读 README
- 阅读依赖清单
- 阅读核心目录和测试目录
- 用 `SendMessage` 回复 `team-lead`，汇报“已就绪 + 关键结构 + 适合承担什么任务”

### 第六步：创建任务

使用 `TaskCreate` 时，不要只写一句“修一下”。

建议写法：

```json
{
  "subject": "实现用户认证模块",
  "description": "在 auth/ 相关目录中实现登录、鉴权中间件和基础单元测试。验收标准：登录成功、鉴权失败处理正确、测试通过。",
  "activeForm": "实现用户认证模块"
}
```

一个好任务至少要包含：

- 目标
- 范围
- 验收标准
- 依赖 / 阻塞条件
- 验证方式

### 第七步：消息协作

推荐通过 `SendMessage` 发送短、准、带上下文的消息。

例如：

```json
{
  "type": "message",
  "recipient": "developer",
  "summary": "Task #3 ready for review",
  "content": "Task #3 已完成。涉及文件：src/auth/*。请重点检查 token 刷新逻辑和错误码处理。"
}
```

### 第八步：收尾

团队结束前，team lead 应先收集团队成员的最终结果：

- 改了哪些文件
- 做了哪些验证
- 剩余风险是什么

然后再发送：

```json
{
  "type": "shutdown_request",
  "reason": "当前批次任务已完成，请停止接收新任务"
}
```

## 7. 多项目工作流

多项目模式只在下面场景建议开启：

- 用户明确要求多个项目并行推进
- 一个需求天然横跨多个 repo
- 同一产品由多个独立 repo 组成

不要因为当前目录下碰巧有很多 repo，就全部拉起来。

### 推荐做法

1. 先决定是否真的需要多项目模式
2. 每个 repo 一个明确边界
3. 最多保持 2 到 3 个活跃 team
4. 跨 team 依赖必须通过 team lead 转发

更完整的策略见：

- `skills/ai-dev-team/references/multi-project-mode.md`

### 多项目辅助命令

```bash
python3 skills/ai-dev-team/scripts/suggest_team_setup.py --mode multi /path/a /path/b
```

会返回：

- 每个项目建议的 team
- 各自角色
- starter tasks
- coordination notes

## 8. Helper Scripts

### `suggest_team_setup.py`

用途：

- 识别项目的粗粒度技术栈信号
- 推导建议的 `team_name`
- 推荐角色组合
- 生成 starter tasks

示例：

```bash
python3 skills/ai-dev-team/scripts/suggest_team_setup.py /Users/liliguo/IdeaProjects/create_data_util
```

对于同时有前端和后端信号的项目，典型输出会偏向：

- `frontend-dev`
- `backend-dev`
- `tester`
- `designer`（如果 UI 比较重）

### `render_role_prompt.py`

用途：

- 根据角色、项目名、路径直接生成 teammate 启动 prompt

示例：

```bash
python3 skills/ai-dev-team/scripts/render_role_prompt.py \
  --role backend-dev \
  --project-name create_data_util \
  --project-path /Users/liliguo/IdeaProjects/create_data_util
```

适合拿来直接填 teammate spawn 的 `prompt` 字段。

## 9. 参考文件说明

### `references/role-prompts.md`

包含：

- 各角色的启动 prompt 模板
- 通用约束
- 任务分派消息模板

### `references/tool-shapes.md`

包含：

- `TeamCreate`
- `TaskCreate`
- `TaskUpdate`
- `TaskList`
- `SendMessage`
- `shutdown_request`
- `Agent` / `Task` 两种 teammate spawn 形态

用途：

- 当你忘了某个负载字段怎么组织时，直接对照这个文件

### `references/multi-project-mode.md`

包含：

- 多项目模式何时开启
- 单 team / 多 team 决策
- 共享库隔离
- 跨 team 消息格式
- 反模式

## 10. 常见错误

### 错误 1：一上来就建很多角色

问题：

- 协调成本大于产出

建议：

- 默认从 `developer + reviewer/tester` 开始

### 错误 2：没有项目边界就建团

问题：

- agent 会读到无关仓库
- 任务范围失控

建议：

- 明确当前 `cwd` 或用户指定路径

### 错误 3：任务描述太空

问题：

- teammate 很难稳定交付

建议：

- 明确目标、范围、验收标准、验证方式

### 错误 4：跨 team 依赖不经 team lead

问题：

- 信息不同步
- 用户看不到真实进度

建议：

- 所有跨 team 依赖都通过 team lead 消息显式转发

## 11. 维护建议

当你继续迭代这个 skill 时，建议按下面顺序：

1. 先更新 `SKILL.md` 的核心原则和流程
2. 再更新 `references/` 中的模板和负载示例
3. 如果脚本能力变化，再更新 `scripts/`
4. 最后同步更新本 README 和这份 usage 文档

这样可以避免“skill 已更新，但文档和脚本还是旧的”。
