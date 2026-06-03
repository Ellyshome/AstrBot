# AstrBot 多 Agent 架构解析

AstrBot 的多 Agent 架构是一个**基于 Handoff（交接/委托）模式的层级式多 Agent 系统**，核心思想是"主 Agent 通过工具调用来把子任务委托给子 Agent"。整体架构分为以下几层：

## 1. Agent 定义层

**[agent.py](AstrBot/astrbot/core/agent/agent.py)** 定义了 Agent 的本质——一个简单的数据类：

```python
Agent(name, instructions, tools, run_hooks, begin_dialogs)
```

每个 Agent 只是一个"名字 + 系统指令 + 工具集"的模板/描述符，不包含运行时状态。这是理解整个架构的关键——**Agent 是声明式的配置，而不是运行实例**。

## 2. Handoff 机制（多 Agent 核心）

**[handoff.py](AstrBot/astrbot/core/agent/handoff.py)** 是整个多 Agent 架构的基石。`HandoffTool` 继承自 `FunctionTool`，它会自动生成名为 `transfer_to_{agent_name}` 的 Function Calling 工具：

- 主 Agent 的 LLM 看到这个工具后，会像调用普通工具一样调用它
- 参数包含 `input`（委托的任务描述）、`image_urls`（多模态输入）、`background_task`（是否后台执行）
- 每个 HandoffTool 都持有对目标子 Agent 的引用

## 3. 子 Agent 编排器

**[subagent_orchestrator.py](AstrBot/astrbot/core/subagent_orchestrator.py)** 从配置文件读取子 Agent 定义并创建对应的 HandoffTool：

```
配置 (YAML/JSON)
  → SubAgentOrchestrator.reload_from_config()
    → Agent(name, instructions, tools, persona)
      → HandoffTool(agent, description)
        → 注册到主 Agent 的 toolset
```

每个子 Agent 可以配置：

| 配置项 | 说明 |
|--------|------|
| **独立的人格 (persona_id)** | 绑定到特定人格的 system prompt |
| **独立的工具集 (tools)** | 指定该子 Agent 能使用哪些工具，`null` 表示全部 |
| **独立的 LLM Provider (provider_id)** | 可以为子 Agent 指定不同的模型 |
| **公开描述 (public_description)** | 主 Agent 看到的工具描述 |

## 4. 子 Agent 执行层

当主 Agent 的 LLM 调用 `transfer_to_X` 时，**[astr_agent_tool_exec.py](AstrBot/astrbot/core/agent/tool_exec.py)** 的 `_execute_handoff()` 负责：

1. 构建子 Agent 的 toolset（从全局工具 + 运行时工具中筛选）
2. 调用 `ctx.tool_loop_agent()` —— 这实际上启动了一个**全新的、独立的 Agent Loop**
3. 子 Agent 有自己的 context、自己的 LLM 调用循环、自己的工具执行
4. 子 Agent 的执行结果作为 `CallToolResult` 返回给主 Agent，内容为子 Agent 的 `completion_text`

支持两种模式：
- **同步模式**：主 Agent 等待子 Agent 完成后再继续
- **后台模式**（`background_task=true`）：子 Agent 异步执行，完成后通过 `CronMessageEvent` 唤醒主 Agent

## 5. Agent Runner 层

Agent 的实际运行由 Runner 驱动，核心文件在 `core/agent/runners/` 目录下：

```
BaseAgentRunner (抽象接口)
  ├── ToolLoopAgentRunner (标准 LLM Agent Loop)
  ├── CozeAgentRunner (对接扣子平台)
  ├── DifyAgentRunner (对接 Dify 平台)
  ├── DashScopeAgentRunner (对接阿里百炼)
  └── DeerFlowAgentRunner (对接 DeerFlow)
```

**[ToolLoopAgentRunner](AstrBot/astrbot/core/agent/runners/tool_loop_agent_runner.py)** 实现了标准的 ReAct Agent 循环：

- **状态机**: `IDLE → RUNNING → DONE/ERROR`
- **每步流程**: LLM 推理 → 提取 tool_call → 执行工具 → 将结果反馈给 LLM → 继续或完成
- **高级特性**: 流式输出、工具重复调用检测、上下文压缩、Provider 回退（fallback）、skills_like 轻量 tool schema 模式

## 6. Pipeline 消息处理管道

消息处理通过一个**洋葱模型的管道**进行，定义在 `core/pipeline/` 中：

```
用户消息
  │
  ▼
WakingCheck (检查唤醒词)
  │
  ▼
WhitelistCheck (黑白名单检查)
  │
  ▼
SessionStatusCheck (会话状态检查)
  │
  ▼
RateLimit (频率限制)
  │
  ▼
ContentSafety (内容安全)
  │
  ▼
PreProcess (预处理 / Stars 插件拦截)
  │
  ▼
ProcessStage (Stars 插件处理 或 LLM Agent 调用)
  │
  ▼
ResultDecorate (结果装饰：T2I、语音转换等)
  │
  ▼
Respond (发送回复)
```

每个阶段都可以：
- **阻断事件传播** (`event.stop_event()`)，后续阶段不再执行
- **使用异步生成器** 实现洋葱模型：前置处理 → yield → 后续阶段执行 → 后置处理

## 7. Stars 插件系统

位于 `core/star/` 目录：

- 每个插件继承 `Star` 基类
- 通过 `@filter.event_message_type()` 等装饰器注册事件处理器
- 插件可以注册两类扩展：
  - **事件处理器 (StarHandler)**：拦截管道中的消息事件
  - **LLM 工具 (FunctionTool)**：扩展 Agent 的能力边界
- 插件管理器 (`star_manager.py`) 负责插件的加载、卸载、热重载、依赖安装

## 8. 平台抽象层

位于 `core/platform/` 目录：

统一的 `AstrMessageEvent` 抽象屏蔽了不同聊天平台的差异，支持的平台包括 QQ（Napcat/Lagrange）、微信（企业微信 AI Bot）、WebChat 等。

## 9. Provider 抽象层

位于 `core/provider/` 目录：

- 统一的 `Provider` 接口屏蔽不同 LLM 服务商的差异
- 支持 Chat / STT / TTS / Embedding / Rerank 多种能力类型
- 内置 Provider 回退（fallback）和空输出重试机制

---

## 完整请求流程图

```
用户消息
  │
  ▼
Platform Adapter (QQ/微信/WebChat...)
  │
  ▼
Pipeline 管道 (洋葱模型)
  ├── WakingCheck (检查唤醒词)
  ├── WhitelistCheck (黑白名单)
  ├── SessionStatusCheck (会话状态)
  ├── RateLimit (频率限制)
  ├── ContentSafety (内容安全)
  ├── PreProcess (预处理 / Stars 拦截)
  │
  ├── ProcessStage ────────────────────────────────┐
  │   │                                            │
  │   ├── Stars 插件处理 (可拦截事件)                │
  │   │                                            │
  │   └── build_main_agent()                       │
  │       ├── _select_provider() 选择 LLM           │
  │       ├── _ensure_persona_and_skills()          │
  │       │   ├── 注入人格 (Persona)                │
  │       │   ├── 注入技能 (Skills)                 │
  │       │   ├── 构建工具集 (含 HandoffTool)       │
  │       │   └── 子 Agent 编排（去重、路由提示）    │
  │       ├── _apply_kb() 注入知识库                │
  │       ├── _apply_web_search_tools() 网络搜索    │
  │       ├── _apply_local_env_tools() 本地工具     │
  │       └── AgentRunner.reset() 初始化            │
  │           │                                    │
  │           ▼                                    │
  │       ToolLoopAgentRunner                      │
  │       (ReAct Agent Loop)                       │
  │           │                                    │
  │           ├── LLM 推理                          │
  │           │   ├── 流式输出 (streaming)          │
  │           │   ├── Provider 回退 (fallback)      │
  │           │   └── 空输出重试                    │
  │           │                                    │
  │           ├── 调用普通工具 ──────────────────► 返回结果
  │           │   ├── 函数过滤（仅传有效参数）       │
  │           │   ├── 超时控制                      │
  │           │   ├── 重复调用检测                  │
  │           │   └── 大结果溢出到文件              │
  │           │                                    │
  │           └── 调用 transfer_to_X ────────────► │
  │               │                                │
  │               ▼                                │
  │           FunctionToolExecutor                 │
  │               │                                │
  │               ├── _execute_handoff() ─────────┐ │
  │               │   ├── 构建子 Agent toolset    │ │
  │               │   ├── 选择 Provider           │ │
  │               │   │   (可用不同模型)           │ │
  │               │   ├── 启动新的 LLM Agent Loop │ │
  │               │   ├── 子 Agent 独立执行       │ │
  │               │   └── 返回 completion_text ──┘ │
  │               │                                │
  │               └── _execute_handoff_background() │
  │                   ├── 异步执行子 Agent          │
  │                   └── CronEvent 唤醒主 Agent    │
  │                                                │
  ├── ResultDecorate (T2I / 语音转换等)             │
  └── Respond (发送回复给用户)                       │
```

---

## 架构特点总结

| 维度 | 设计 |
|------|------|
| **多 Agent 模式** | Handoff-based 层级委托，不是平等协作的 Multi-Agent |
| **Agent 定义** | 声明式数据类 (`Agent` dataclass)，不是运行时实例 |
| **子 Agent 隔离** | 独立的 LLM 调用、独立的上下文、独立的工具集 |
| **通信方式** | 主→子：Function Calling 参数；子→主：文本返回值 (CallToolResult) |
| **Provider** | 每个 Agent（包括子 Agent）可使用不同的 LLM 模型 |
| **工具分配** | 可精确控制每个子 Agent 的工具集，实现权限隔离 |
| **扩展性** | 子 Agent 配置在 `subagent_orchestrator` 中，支持 Persona 复用 |
| **并发** | 子 Agent 支持同步/后台两种模式，后台模式不阻塞主 Agent |
| **运行载体** | 支持内置 ToolLoop、Dify、扣子、阿里百炼、DeerFlow 等多种运行环境 |

## 关键源文件索引

| 文件 | 职责 |
|------|------|
| [agent.py](AstrBot/astrbot/core/agent/agent.py) | Agent 数据结构定义 |
| [handoff.py](AstrBot/astrbot/core/agent/handoff.py) | HandoffTool — 多 Agent 委托机制 |
| [subagent_orchestrator.py](AstrBot/astrbot/core/subagent_orchestrator.py) | 子 Agent 编排器，从配置创建 HandoffTool |
| [astr_main_agent.py](AstrBot/astrbot/core/astr_main_agent.py) | 主 Agent 构建入口 `build_main_agent()` |
| [astr_agent_tool_exec.py](AstrBot/astrbot/core/astr_agent_tool_exec.py) | Handoff 执行器 `_execute_handoff()` |
| [runners/tool_loop_agent_runner.py](AstrBot/astrbot/core/agent/runners/tool_loop_agent_runner.py) | 标准 ReAct Agent Loop 实现 |
| [runners/base.py](AstrBot/astrbot/core/agent/runners/base.py) | Agent Runner 抽象基类 |
| [pipeline/scheduler.py](AstrBot/astrbot/core/pipeline/scheduler.py) | Pipeline 调度器 |
| [star/star_manager.py](AstrBot/astrbot/core/star/star_manager.py) | 插件管理器 |
| [star/star.py](AstrBot/astrbot/core/star/star.py) | StarMetadata — 插件元数据 |
| [provider/manager.py](AstrBot/astrbot/core/provider/manager.py) | Provider 管理器 |
| [platform/sources/](AstrBot/astrbot/core/platform/sources/) | 各平台适配器实现 |
