# Multi-Project Mode

这个参考文件用于“确实需要跨多个 repo / 子项目协作”时的决策，不用于日常单项目开发。

## 何时开启多项目模式

只有满足下面至少一条时才建议开启：

- 用户明确要求多个项目并行推进
- 一个需求明确横跨前端 repo、后端 repo、共享库 repo
- 同一个产品由多个独立仓库组成，且存在明确交付关系

不要因为当前目录下碰巧有很多仓库，就自动进入多项目模式。

## 决策树

### 情况 A：单产品，多 repo

例子：

- `web-app`
- `backend-service`
- `shared-sdk`

建议：

- 可以为每个 repo 建一个 team
- 也可以只建一个 team，由 `frontend-dev` / `backend-dev` 按 repo 分工
- 如果 repo 之间改动强耦合但任务量不大，优先单 team，减少协调成本

### 情况 B：多个完全独立产品

建议：

- 不要自动同时建团
- 先让用户确认优先级
- 默认只对当前产品建团

### 情况 C：共享库 + 多个业务 repo

建议：

- 把共享库视为独立边界
- 共享库团队只处理公共接口、兼容性和版本约束
- 业务 repo 团队只消费共享库，不直接替共享库做未约定改动

## 团队数量上限

默认建议：

- 最多 2 到 3 个 team 同时活跃

原因：

- team 越多，消息编排和任务同步成本越高
- 大部分个人工作流里，超过 3 个并行 team 的收益很快下降

## 推荐拓扑

### 方案 1：单 team，多角色

适合：

- 单产品
- 多 repo 但改动量不大
- 主要问题是前后端配合，不是组织隔离

优点：

- 协调简单
- 更快进入执行

缺点：

- 角色消息更容易混在一起

### 方案 2：多 team，按 repo 划分

适合：

- repo 边界清楚
- 可以并行实现
- 每个 repo 都有足够工作量

优点：

- 边界清晰
- 更利于隔离风险

缺点：

- team lead 协调成本更高

## 启动顺序

多项目模式下，建议按下面顺序启动：

1. 先建立主协调 team 或确定主 team lead
2. 明确每个 repo 的路径、负责人角色、输出物
3. 先创建关键路径上的 team
4. 只在有真实并行任务时再启动其余 team

不要一次把所有 team 和所有成员全部拉起。

## 跨 team 协作规则

- 不允许 agent 直接假设另一个 team 会做什么
- 跨 team 依赖必须由 team lead 显式转发
- 所有跨 team 消息都要写明：
  - 来源 team
  - 目标 team
  - 依赖任务
  - 需要的输出
  - 截止条件

推荐消息格式：

```text
[from backend-team]
需要 frontend-team 确认 Task #12 的接口字段命名。
接口：POST /api/auth/login
待确认字段：rememberMe / remember_me
阻塞影响：前端表单提交联调
```

## 共享库变更规则

共享库 repo 常见风险：

- 接口破坏性改动
- 版本未同步
- 业务 repo 假设不一致

建议：

- 共享库任务必须写清楚兼容性要求
- 先完成接口设计或 reviewer 审查，再让业务 repo 接入
- team lead 汇总受影响的 repo 列表

## 任务依赖写法

在多项目模式下，任务描述里要显式写 repo 边界。

推荐：

```text
subject: "backend-service: 提供登录接口"
description: "在 backend-service 中实现 POST /api/auth/login。完成后通知 frontend-team 进行联调。"
```

不推荐：

```text
subject: "做登录"
description: "把登录搞定"
```

## 状态汇总建议

team lead 对用户汇报时，按 repo 或 team 汇总：

```text
当前活跃团队：
- web-app-team：前端表单与状态管理开发中
- backend-service-team：登录接口已完成，等待前端联调
- shared-sdk-team：暂未启动

当前阻塞：
- web-app-team 等待 backend-service-team 确认错误码格式
```

## 反模式

- 当前目录里有 5 个 repo，就 5 个全拉起来
- 为共享库和业务 repo 同时做未经审查的接口变更
- 跨 team 依赖只靠口头描述，不写进消息或任务
- team lead 不做汇总，让用户自己拼装进度
