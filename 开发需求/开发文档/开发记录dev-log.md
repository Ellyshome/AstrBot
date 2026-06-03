

5.19 克隆项目，植入dev开发模式
---

## AstrBot 技术栈全景

### 语言与运行时

- **Python >= 3.12**，异步架构（asyncio）
- 前端：**Vue 3 + TypeScript + Vite**

---

### 后端核心框架

| 层面 | 技术 | 用途 |
|------|------|------|
| Web 框架 | **Quart**（async Flask）+ Hypercorn | Dashboard API 服务 |
| HTTP 客户端 | **aiohttp** / **httpx[socks]** | 异步请求、代理支持 |
| CLI | **Click** | `astrbot init/run/plug/conf` 命令 |
| ORM | **SQLAlchemy 2.0[asyncio]** + **SQLModel** | 数据库模型 |
| 数据库 | **SQLite**（aiosqlite） | 本地存储，`data/data_v4.db` |
| 向量数据库 | **FAISS (faiss-cpu)** | RAG 向量检索 |
| 数据校验 | **Pydantic v2** | Schema 校验 |
| 日志 | **Loguru** | 结构化日志 |
| 认证 | **PyJWT** + PBKDF2 | JWT Token + 密码哈希 |
| 定时任务 | **APScheduler** | Cron 调度 |
| 文件锁 | **filelock** | 防多实例启动 |
| 热重载 | **watchfiles** | 插件开发自动重载 |

---

### IM 平台适配（18 个）

QQ (OneBot/Official)、Telegram、Discord、Slack、飞书/Lark、钉钉、企业微信、微信（个人/公众号）、KOOK、LINE、Mattermost、Misskey、Satori、WebChat

SDK 对应：`aiocqhttp`, `python-telegram-bot`, `py-cord`, `slack-sdk`, `lark-oapi`, `dingtalk-stream`, `wechatpy` 等

---

### LLM Provider 适配（40+）

| 类型 | Provider |
|------|----------|
| Chat Completion | OpenAI、Anthropic Claude、Google Gemini、Groq、OpenRouter、AIHubMix、智谱 GLM、xAI、Kimi Code、LongCat、DashScope (Qwen)、Mimo |
| Embedding | OpenAI、Ollama、Gemini、NVIDIA |
| Rerank | 百炼、Xinference、vLLM、NVIDIA |
| TTS | OpenAI TTS、Edge TTS、Azure TTS、DashScope、FishAudio、Gemini、火山引擎、MiniMax、Mimo、GSVI、Genie |
| STT | Whisper API/Self-hosted、SenseVoice、Xinference、Mimo |

---

### AI / Agent 系统

| 组件 | 路径 | 说明 |
|------|------|------|
| 主 Agent | `astrbot/core/astr_main_agent.py` | 58K 行，核心 LLM 交互 + 工具调用循环 |
| Agent 框架 | `astrbot/core/agent/` | 泛型 Agent 模型 + 多种 Runner |
| 内置 Runner | `astrbot/core/agent/runners/tool_loop_agent_runner.py` | 本地 tool-calling 循环 |
| 第三方 Runner | `astrbot/core/agent/runners/coze/`、`dify/`、`dashscope/`、`deerflow/` | Coze / Dify / DashScope / DeerFlow 集成 |
| MCP Client | `astrbot/core/agent/mcp_client.py` | 支持 SSE / Streamable HTTP / Stdio 三种传输，含安全沙箱校验 |
| Sub-Agent | `astrbot/core/subagent_orchestrator.py` | 子 Agent 编排调度 |

---

### RAG / 知识库

- **文档解析**：PDF（pypdf）、EPUB、URL、纯文本、MarkItDown（docx/xlsx）
- **分块**：递归字符分块（中英双语分隔符）、固定大小分块
- **检索**：混合检索 = FAISS 向量检索 + BM25 稀疏检索（rank-bm25 + jieba 分词）
- **融合**：Reciprocal Rank Fusion (RRF) 合并稠密/稀疏结果
- **Rerank**：支持百炼 / Xinference / vLLM / NVIDIA 重排序

---

### 消息处理 Pipeline（9 阶段）

```
WakingCheck → WhitelistCheck → SessionStatusCheck → RateLimit
→ ContentSafety → PreProcess → Process → ResultDecorate → Respond
```

Process 阶段包含两个子阶段：**StarRequest**（插件处理）和 **AgentRequest**（LLM Agent 处理）

---

### 插件系统（Star）

- 基类：`astrbot/core/star/base.py` — 所有插件继承 `Star`
- 注册装饰器：`@register_star`, `@command`, `@regex`, `@llm_tool`, `@agent` 等
- 过滤器：命令匹配、正则、消息类型、平台类型、权限
- 生命周期钩子：`on_astrbot_loaded`, `on_platform_loaded`, `on_plugin_loaded/unloaded/error` 等
- 插件市场：集成 **Shipyard** SDK，支持在线安装/更新
- 插件页面：插件可注册自己的 Web UI 页面，通过 iframe + postMessage 桥接

---

### 内置工具（LLM Function Calling）

| 工具 | 说明 |
|------|------|
| `astr_kb_search` | 知识库 RAG 查询 |
| `web_search_*` | 多引擎网页搜索（百度/Tavily/Bocha/Brave/Firecrawl） |
| `send_message_to_user` | 主动发消息 |
| `future_task` | 定时/周期任务 |
| Computer Use | 文件读写编辑、Shell 执行、Python 执行、CUA 截图/鼠标/键盘 |
| Shipyard Neo | 浏览器自动化、Skill 创建/发布/回滚 |

---

### 前端（Dashboard）

- **Vue 3** + **Vuetify 3**（Material Design 组件库）
- **Pinia** 状态管理 + **Vue Router** 路由
- **vue-i18n** 国际化
- **Monaco Editor** 代码编辑器
- **TipTap** 富文本编辑
- **Mermaid** 图表渲染
- **ApexCharts** 数据可视化
- **Shiki** 语法高亮
- **KaTeX** 数学公式

---

### 基础设施与部署

| 项目 | 技术 |
|------|------|
| 构建系统 | **Hatchling**（含自定义 Vue 构建钩子） |
| 包管理 | **uv** |
| 容器化 | Docker（python:3.12-slim）、Dev Container |
| 音频处理 | pydub + silk-python（QQ SILK 编码） |
| 代理支持 | httpx SOCKS / python-socks / PySocks |
| 进程管理 | psutil、aiodocker |
| SSL | certifi CA 证书包 + aiohttp SSL 上下文补丁 |

---

### 整体架构

```
CLI (Click) ──→ CoreLifecycle
                      │
                      ├── PlatformManager ──→ 18 平台适配器
                      │         │ AstrMessageEvent
                      ├── PipelineScheduler (9 阶段流水线)
                      │         ├── StarRequestSubStage (插件处理)
                      │         └── AgentRequestSubStage
                      │               ├── Internal (tool-loop)
                      │               └── Third-Party (Coze/Dify/DeerFlow/DashScope)
                      ├── ProviderManager ──→ 40+ Provider (Chat/Embed/TTS/STT/Rerank)
                      ├── PluginManager (Star 系统)
                      ├── KnowledgeBaseManager (RAG: FAISS + BM25 + Rerank)
                      ├── SQLiteDatabase (SQLModel + SQLAlchemy async)
                      ├── CronJobManager (APScheduler)
                      ├── SubAgentOrchestrator
                      └── Dashboard (Quart + Vue SPA, 端口 6185)
```

---

## Agent 间通信机制

AstrBot **没有使用**事件总线或消息队列进行 Agent 间通信，而是采用 **Handoff（移交）模式**：子 Agent 以 Function Tool 的形式暴露给主 Agent，主 LLM 通过 tool-call 决定何时移交任务。

---

### 核心通信组件

| 组件 | 路径 | 职责 |
|------|------|------|
| `HandoffTool` | `astrbot/core/agent/handoff.py` | 子 Agent 的工具封装，名称为 `transfer_to_<agent_name>` |
| `SubAgentOrchestrator` | `astrbot/core/subagent_orchestrator.py` | 从配置加载子 Agent 定义，创建 HandoffTool 实例 |
| `FunctionToolExecutor` | `astrbot/core/astr_agent_tool_exec.py` | 工具执行调度器，识别 HandoffTool 并路由到 handoff 逻辑 |
| `ToolLoopAgentRunner` | `astrbot/core/agent/runners/tool_loop_agent_runner.py` | Agent 执行引擎，独立的 tool-calling 循环 |
| `MainAgentHooks` | `astrbot/core/astr_agent_hooks.py` | 桥接 Agent 生命周期事件到插件系统 |

---

### HandoffTool：通信契约

每个子 Agent 被包装为一个名为 `transfer_to_<agent_name>` 的 LLM 可调用工具，参数定义了通信协议：

```json
{
  "type": "object",
  "properties": {
    "input": {"type": "string", "description": "移交给子 Agent 的任务文本"},
    "image_urls": {"type": "array", "items": {"type": "string"}, "description": "转发给子 Agent 的图片"},
    "background_task": {"type": "boolean", "description": "是否异步执行"}
  }
}
```

---

### 同步 Handoff（阻塞式）

最核心的通信路径，主 Agent 阻塞等待子 Agent 完成：

```
主 Agent LLM
    │ 决定调用 transfer_to_xxx(input="...", image_urls=[...])
    ▼
FunctionToolExecutor.execute()
    │ 识别 HandoffTool → _execute_handoff()
    ▼
_execute_handoff()
    │ 1. 提取 input 作为子 Agent 的 prompt
    │ 2. 从 Agent.tools 解析子 Agent 的工具集（字符串名 → FunctionTool 对象）
    │ 3. 解析 LLM Provider（tool.provider_id 或默认）
    │ 4. 准备 begin_dialogs 作为初始上下文
    ▼
ctx.tool_loop_agent()
    │ 创建新的 ToolLoopAgentRunner 实例
    │ 子 Agent 拥有独立的上下文和工具循环
    ▼
子 Agent 运行（可多次调用工具）
    │
    ▼ 返回 LLMResponse.completion_text
包装为 CallToolResult
    │
    ▼ 作为 tool role 消息追加到主 Agent 上下文
主 Agent LLM 继续推理
```

**关键特征**：
- 子 Agent 的最终文本输出 = 工具调用结果，被注入回主 Agent 的 LLM 上下文
- 子 Agent 工具集构建时**过滤掉 HandoffTool**，防止递归移交
- 子 Agent 可拥有独立的 LLM Provider 和 Persona

---

### 异步 Handoff（后台式）

当 `background_task=True` 时，主 Agent 不阻塞：

```
主 Agent LLM
    │ 调用 transfer_to_xxx(input="...", background_task=True)
    ▼
_execute_handoff_background()
    │ 1. 立即返回 CallToolResult（含 task_id），主 Agent 可继续
    │ 2. 在独立 asyncio.Task 中运行子 Agent
    ▼
子 Agent 完成
    │
    ▼
_wake_main_agent_for_background_result()
    │ 1. 创建 CronMessageEvent（合成事件）携带后台结果
    │ 2. 构建新的主 Agent 实例，结果注入 system prompt
    │ 3. 新主 Agent 拥有 send_message_to_user 工具
    │ 4. 新主 Agent 运行完毕，将结果发送给用户
```

**关键特征**：
- 这是项目中**唯一的异步 Agent 间通信路径**
- 后台结果通过**合成事件**重新唤醒主 Agent，不是回调
- 新主 Agent 是全新实例，不共享原始上下文

---

### 第三方 Agent 集成

第三方 Agent 是内部 Agent 的**替代方案**，不参与 Handoff 体系，在 Pipeline 层做路由选择：

```
AgentRequestSubStage
    │
    ├── agent_runner_type == "local"
    │       └── InternalAgentSubStage（支持 Handoff）
    │
    └── agent_runner_type != "local"
            └── ThirdPartyAgentSubStage
                    ├── Coze Runner ── HTTP API + SSE 流
                    ├── Dify Runner ── HTTP API（chat/agent/workflow 模式）
                    ├── DashScope Runner ── 阿里云 SDK + 同步生成器
                    └── DeerFlow Runner ── LangGraph HTTP API + 事件流
```

| Runner | 通信协议 | 会话管理 |
|--------|---------|---------|
| Coze | HTTP API，SSE 流式响应 | 持久化 conversation_id |
| Dify | HTTP API，支持流/非流 | 持久化 conversation_id + session variables |
| DashScope | 阿里云 Application SDK，线程中消费同步生成器 | session_id 多轮对话 |
| DeerFlow | LangGraph HTTP API，values/messages-tuple/custom 事件流 | thread_id，内部支持子 Agent |

所有第三方 Runner 遵循统一的 `BaseAgentRunner` 接口，返回相同格式的 `AgentResponse`。

---

### MCP 的通信角色

MCP 提供**工具级**通信，不是 Agent 级：

```
Agent LLM
    │ 调用 MCP 工具（如 mcp__filesystem__read_file）
    ▼
MCPTool.call()
    │ 委托给 MCPClient
    ▼
MCPClient
    │ 通过 SSE / Streamable HTTP / Stdio 传输
    ▼
外部 MCP Server
    │ 执行工具，返回结果
    ▼
CallToolResult 返回给 Agent
```

MCP 工具与本地 FunctionTool 被统一对待，Agent Runner 不区分二者。

---

### 插件注册 Agent

插件通过 `@register_agent` 装饰器注册子 Agent，自动创建 HandoffTool：

```python
@register_agent(name="translator", instruction="你是翻译专家", tools=["web_search"])
async def translator_agent(...):
    ...
```

等价于：创建 `Agent(name="translator", ...)` → 包装为 `HandoffTool(name="transfer_to_translator")` → 注册到主 Agent 工具集。

通过 `RegisteringAgent.llm_tool()` 注册的工具**仅在该子 Agent 运行时可用**。

---

### Hooks：Agent 到插件的单向通知

`MainAgentHooks` 将 Agent 生命周期事件桥接到插件系统（同步阻塞）：

| Hook | 触发事件 | 方向 |
|------|---------|------|
| `on_agent_begin` | `OnAgentBeginEvent` | Agent → 插件 |
| `on_agent_done` | `OnAgentDoneEvent` | Agent → 插件 |
| `on_tool_start` | `OnUsingLLMToolEvent` | Agent → 插件 |
| `on_tool_end` | `OnLLMToolRespondEvent` | Agent → 插件 |

这是唯一具有"事件"特征的通信，但它是**单向且同步**的，不是 Agent 间通信。

---

### 通信模式总结

| 模式 | 机制 | 同步/异步 | 适用场景 |
|------|------|----------|---------|
| 同步 Handoff | `transfer_to_xxx` tool-call → 新 ToolLoopAgentRunner | 同步阻塞 | 子任务需要立即结果 |
| 异步 Handoff | `background_task=True` → asyncio.Task → CronMessageEvent 唤醒 | 异步非阻塞 | 长时间后台任务 |
| 第三方 Agent | HTTP API 调用外部服务 | 同步（流式） | 使用 Coze/Dify/DeerFlow 等平台 |
| MCP 工具调用 | MCPClient → 外部 MCP Server | 同步阻塞 | 调用外部工具服务 |
| 插件 Hooks | MainAgentHooks → 插件事件处理器 | 同步阻塞 | Agent 生命周期通知 |

---
