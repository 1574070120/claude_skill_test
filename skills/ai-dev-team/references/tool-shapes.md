# Tool Shapes

下面是当前环境中常见的团队协作工具负载形态。它们来自本地已存在会话的实际调用样式，适合在不确定参数名时作为参考。

## `TeamCreate`

```json
{
  "team_name": "env-manager-team",
  "description": "env_manager 项目的 AI 研发团队，负责需求分析、研发、评审和测试"
}
```

有些版本还会带：

```json
{
  "team_name": "ads-manager-team",
  "description": "Full-stack team for ads-manager project",
  "agent_type": "team-lead"
}
```

## teammate spawn

不同版本里常见两种工具名：

- `Agent`
- `Task`

它们都可能承担“创建后台 teammate”的作用。

### 形态 A：`Agent`

```json
{
  "description": "Backend Developer agent",
  "prompt": "你是当前项目的后端研发……",
  "subagent_type": "general-purpose",
  "run_in_background": true,
  "name": "backend-dev",
  "team_name": "quirky-hugging-firefly"
}
```

### 形态 B：`Task`

```json
{
  "description": "研发工程师角色",
  "prompt": "你是团队的研发工程师（developer）……",
  "name": "developer",
  "subagent_type": "general-purpose",
  "team_name": "env-manager-team",
  "run_in_background": true
}
```

实操建议：

- 先看当前会话工具列表或最近示例，确认用 `Agent` 还是 `Task`
- 参数名尽量保持 `name` / `prompt` / `team_name` / `subagent_type` / `run_in_background`

## `TaskCreate`

```json
{
  "subject": "实现用户认证模块",
  "description": "在 auth/ 相关目录中实现登录、鉴权中间件和基础单元测试。验收标准：登录成功、鉴权失败处理正确、测试通过。",
  "activeForm": "实现用户认证模块"
}
```

写法建议：

- `subject`：短标题
- `description`：目标、范围、验收标准、依赖、验证方式
- `activeForm`：进行时描述，便于状态展示

## `TaskUpdate`

```json
{
  "taskId": "13",
  "status": "completed"
}
```

也常见：

```json
{
  "taskId": "6",
  "status": "in_progress",
  "owner": "tester",
  "activeForm": "Reviewing data sync code for bugs and risks"
}
```

## `TaskList`

通常不需要参数：

```json
{}
```

用于：

- 看还有哪些任务未开始
- 判断某个 teammate 完成后是否解锁了后续任务

## `SendMessage`

### 普通协作消息

```json
{
  "type": "message",
  "recipient": "developer",
  "summary": "Task #3 ready for review",
  "content": "Task #3 已完成。涉及文件：src/auth/*。请重点检查 token 刷新逻辑和错误码处理。"
}
```

### 发给 team-lead 的完成汇报

```json
{
  "type": "message",
  "recipient": "team-lead",
  "summary": "Task #6 completed",
  "content": "Task #6 已完成。修改文件：... 验证结果：... 剩余风险：..."
}
```

### 关闭请求响应

```json
{
  "type": "shutdown_response",
  "request_id": "shutdown-1771494835717@tester",
  "approve": true,
  "content": "All testing analysis tasks completed. Shutting down."
}
```

## teammate mailbox 中常见消息包装

### 角色初始化

```xml
<teammate-message teammate_id="team-lead" summary="研发工程师角色">
你是团队的研发工程师（developer）……
</teammate-message>
```

### 任务分配

```xml
<teammate-message teammate_id="team-lead">
{"type":"task_assignment","taskId":"6","subject":"设计师审查项目 UI/UX","description":"……","assignedBy":"team-lead"}
</teammate-message>
```

实操建议：

- 发消息时把任务号放前面
- 摘要字段尽量短
- 内容里同时写结论、证据和下一步

## `shutdown_request`

常见消息体：

```json
{
  "type": "shutdown_request",
  "reason": "当前批次任务已完成，请停止接收新任务"
}
```

如果环境支持 `TeamDelete`，等成员确认后再清理团队；如果没有，停止派发即可。
