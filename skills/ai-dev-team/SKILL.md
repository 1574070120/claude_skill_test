---
name: ai-dev-team
description: 为 Claude 组建一个面向单项目或多项目的 AI 开发团队，用于需求拆解、并行研发、代码审查、测试验证和团队协作。用户提到“创建 AI 开发小队”“创建开发团队”“ai-dev-team”“组建研发团队”等时触发。
---

# AI 开发小队

为当前项目或用户明确指定的项目创建一个可执行的研发团队。默认以最小可用团队启动，只有在存在明确并行收益时才扩编。

## 适用场景

- 用户明确希望“组队”“创建团队”“并行分工”
- 任务足够大，适合拆成产品、设计、研发、测试或评审
- 需要长期跟踪任务状态、收发 teammate 消息、管理多个子任务

## 不适用场景

- 单文件小改动、一次性问答、纯咨询
- 当前会话自己直接做更快，不值得拉团队
- 没有明确项目边界，且当前工作区里有大量无关仓库

## 核心原则

### 1. 先收敛范围，再建团

- 默认只围绕当前 `cwd` 或用户点名的项目路径建团
- 只有用户明确要求“多项目并行”或需求天然跨多个 repo 时，才创建多个 team
- 不要扫描整个 Home 目录，也不要把当前目录下所有 sibling repo 自动纳入团队

### 2. 以最小可用团队启动

默认只建 2 到 4 个角色：

- `developer`
- `reviewer` 或 `tester`
- `product-manager`，仅在需求未收敛时加入
- `designer`，仅在界面/交互设计明确重要时加入

只有出现明确的并行切分点，才增加 `frontend-dev`、`backend-dev` 或多个同类开发角色。

### 3. 实用隔离，不做绝对承诺

- 通过独立 `team_name`、明确 `cwd`、限制读取路径、禁止跨项目路径来实现操作隔离
- 不要宣称“绝对安全隔离”或“完全不可能串话”
- 多项目时，每个 team 只负责一个明确边界的项目或 repo

### 4. 任务必须可执行

每个任务都应至少包含：

- `subject`
- 清晰的目标和完成定义
- 涉及的文件或目录
- 验收标准
- 若存在依赖，说明阻塞条件

每个 agent 同时只推进一个主任务。大任务先拆成能汇报的小里程碑。

## 当前环境中的工具差异

Claude 不同版本里，拉起 teammate 的工具名可能不同：

- 旧版常见：`Agent`
- 新版常见：`Task`，但它在这里承担的是“后台 teammate spawn”而不是任务列表

团队协作中常见的工具包括：

- `TeamCreate`
- `TaskCreate`
- `TaskUpdate`
- `TaskList`
- `SendMessage`
- `Glob`

先使用当前会话里真实可用的工具名。不要把 teammate spawn 的工具名写死在流程里。

如果你需要：

- 可直接复用的角色启动提示词，见 `references/role-prompts.md`
- 当前环境里常见的 Team/Task/SendMessage 负载形态，见 `references/tool-shapes.md`
- 多项目模式下的建团与协作策略，见 `references/multi-project-mode.md`
- 根据项目路径自动生成建议 team 拓扑和 starter tasks，可运行 `scripts/suggest_team_setup.py`
- 根据角色、项目名、路径渲染 teammate 启动 prompt，可运行 `scripts/render_role_prompt.py`
- 根据项目路径直接生成整套团队协作 JSON 示例，可运行 `scripts/generate_team_examples.py`

## 标准流程

### 1. 确定项目边界

- 优先使用用户给的路径或当前 `cwd`
- 如需探测项目，使用 `Glob` 查找 `README.md`、`package.json`、`go.mod`、`pom.xml`、`pyproject.toml`、`Cargo.toml`
- 如果当前目录下存在多个 repo，先判断它们是否属于同一产品；不是就不要自动全部建团
- 如果需要快速得到角色建议，可运行 `python3 scripts/suggest_team_setup.py <project_path>`

### 2. 选择团队拓扑

默认精简版：

- `developer`
- `reviewer` 或 `tester`

需要需求收敛时增加：

- `product-manager`

需要界面方案时增加：

- `designer`

需要前后端并行时增加：

- `frontend-dev`
- `backend-dev`

除非存在真实的多分支整合工作，不要默认创建 `merge-engineer`。

如果是跨多个 repo 的工作，先阅读 `references/multi-project-mode.md`，再决定是单 team 协调还是多 team 并行。

### 3. 创建团队

团队名使用项目目录名的 slug 加 `-team` 后缀。

示例：

```json
{
  "team_name": "env-manager-team",
  "description": "env_manager 项目的 AI 研发团队，负责需求分析、研发、评审和测试"
}
```

如果是多项目模式，每个项目一个 `team_name`，不要把完全无关的项目塞进同一个 team。

### 4. 拉起 teammates

使用当前环境提供的 teammate spawn 工具，核心参数保持一致：

- `name`
- `prompt`
- `team_name`
- `subagent_type`
- `run_in_background`

常见示例字段如下：

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

更完整的角色提示词模板见 `references/role-prompts.md`。
如果你想直接生成 prompt 文本，可运行 `python3 scripts/render_role_prompt.py --role developer --project-name <name> --project-path <path>`。
如果你想快速拿到 `TeamCreate`、teammate spawn、`TaskCreate`、`SendMessage`、`shutdown_request` 的整套示例，可运行 `python3 scripts/generate_team_examples.py --project-path <path>`。

### 5. 先熟悉项目，再接任务

每个 teammate 的启动提示词里都要包含：

- 角色名和职责
- 项目路径
- 只允许关注当前项目
- 先用只读方式熟悉代码结构
- 熟悉完成后用 `SendMessage` 向 `team-lead` 报告就绪

推荐的开场提示词结构：

```text
你是 {role}。

当前项目：{project_name}
工作目录：{project_path}

你的职责：
- ...
- ...

规则：
- 只阅读和处理当前项目目录内的文件
- 不要主动跨项目搜索
- 先熟悉 README、依赖清单、关键目录
- 熟悉后通过 SendMessage 向 team-lead 回复“已就绪 + 你看到的关键结构”
```

### 6. 创建任务并分配

用 `TaskCreate` 建立可跟踪任务，优先拆成小而完整的任务。

示例：

```json
{
  "subject": "实现用户认证模块",
  "description": "在 auth/ 相关目录中实现登录、鉴权中间件和基础单元测试。验收标准：登录成功、鉴权失败处理正确、测试通过。",
  "activeForm": "实现用户认证模块"
}
```

分配原则：

- 同一个 agent 一次只处理一个主任务
- 如果任务系统支持依赖字段，再使用依赖；如果不支持，就把依赖写进任务描述并由 team lead 顺序调度
- 任务描述里尽量写清楚文件路径、验证方式、交付物

### 7. 用 `SendMessage` 做精确协作

消息应短、准、带上下文。优先包含：

- 当前任务编号
- 结论或请求
- 阻塞点
- 下一步建议

推荐格式：

```json
{
  "type": "message",
  "recipient": "developer",
  "summary": "Task #3 ready for review",
  "content": "Task #3 已完成。涉及文件：src/auth/*。请重点检查 token 刷新逻辑和错误码处理。"
}
```

如果需要完整示例，包括 `TeamCreate`、teammate spawn、`TaskCreate`、`SendMessage`、`shutdown_request`，见 `references/tool-shapes.md`。

### 8. Team lead 的职责

team lead 负责：

- 控制团队规模，避免过度拉人
- 定期调用 `TaskList` 查看状态
- 处理阻塞和重新分配
- 向用户汇报真实进度，而不是空泛口号
- 决定哪些任务继续并行，哪些改为串行

给用户的状态汇报应该至少包含：

- 当前 team 名称
- 活跃成员
- 进行中的任务
- 阻塞点
- 下一步

### 9. 长任务的状态记录

如果任务跨多个阶段或多轮对话，优先维护项目内已有的计划文件；如果没有，再考虑新增轻量状态文件。

推荐：

- 沿用项目已有的 `IMPLEMENTATION_PLAN.md`
- 只记录关键决策、当前状态、阻塞点、下一步

不推荐：

- 为每个 agent 大量创建 `memory/` 笔记
- 频繁写“长期记忆”类文件但无人使用
- 把上下文管理复杂化

### 10. 收尾与下线

完成后先收集每个 agent 的最终结果：

- 做了什么
- 改了哪些文件
- 测试或验证是否完成
- 还有哪些风险

然后再发送关闭消息。常见形式：

```json
{
  "type": "shutdown_request",
  "reason": "当前批次任务已完成，请停止接收新任务"
}
```

如果当前环境支持 `TeamDelete`，在确认所有成员完成后再清理团队；如果没有，就让成员停留在空闲状态，不再派发任务。

## 角色建议

### `product-manager`

适合：

- 需求还模糊
- 需要拆解 backlog
- 需要先明确优先级和验收标准

不适合直接承担编码任务。

### `developer`

适合：

- 单仓库主力开发
- 小到中等规模编码任务
- 在没有明确前后端分界时的一体化推进

### `frontend-dev`

适合：

- UI 改造
- 前端状态管理
- 组件重构
- 交互实现

### `backend-dev`

适合：

- API
- 数据库
- 服务逻辑
- 任务调度

### `reviewer`

适合：

- 独立代码评审
- 风险识别
- 回归风险检查

原则上不参与主实现。

### `tester`

适合：

- 测试方案设计
- 测试补充
- 手工验证
- 自动化回归

## 反模式

- 一上来就为整个工作区每个 repo 建一个 team
- 在没有并行收益时创建 6 个以上角色
- 把“团队已就绪”当成结果，迟迟不进入实际任务
- 任务描述只有一句“修一下”“看一下”
- 默认让 agent 直接合并主分支
- 默认授予生产环境、破坏性 git 或跨项目写权限
- 把不存在或版本不稳定的工具参数写死

## 最终输出模板

```text
AI 开发小队已建立

项目：{project_name}
团队：{team_name}
工作目录：{project_path}

成员：
- {role_1}: {responsibility}
- {role_2}: {responsibility}

当前任务：
- #{id} {subject} - {status}

阻塞点：
- {blocker_or_none}

下一步：
- {next_step}
```
