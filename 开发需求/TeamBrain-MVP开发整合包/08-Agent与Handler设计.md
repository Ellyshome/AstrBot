# 08-Agent与Handler设计

## 1. MVP 设计原则

MVP 采用单 Agent 路由模式：

```text
RouterAgent（唯一 Agent）
```

不采用多 Agent 协作。

Handler 作为 Router 的下游处理模块。

---

## 2. RouterAgent

RouterAgent 是 MVP 唯一 Agent。

职责：

```text
接收 StandardMessage
（已由 DomainTakeoverService 判断 takeover=true）
识别 intent
识别 project
提取参数
路由到对应 Handler 或 QueryApplication
```

不负责：

```text
分域接管判断（由 DomainTakeoverService 负责）
写数据库
拼 SQL
发 IM 回复
替换 AstrBot 主 Agent
```

输出：

```json
{
  "intent": "task_record",
  "project_id": "uuid",
  "project_name": "未来城",
  "data": {
    "title": "...",
    "assignee": "...",
    "due_date": "..."
  }
}
```

---

## 3. 完整调用链

```text
StandardMessage
→ DomainTakeoverService.decide()
    ├─ takeover=false → 放行 AstrBot 原流程
    └─ takeover=true
        → RouterAgent.route()
            → intent=query → QueryApplication
            → intent=task_record → TaskHandler
            → intent=event_record → EventHandler
            → intent=meeting_record → MeetingHandler
            → intent=file_record → FileHandler
            → intent=chat → 简单回复或静默
        → ReplyMessage
```

---

## 4. Handler（处理模块）

Handler 是普通业务处理模块，不是 Agent。

### TaskHandler

输入 RouterAgent 输出 → 解析任务 → 调用 TaskApplication

### EventHandler

输入 RouterAgent 输出 → 构造事件 → 调用 EventApplication

### MeetingHandler

输入 RouterAgent 输出 → 构造会议 → 调用 MeetingApplication

### FileHandler

输入 RouterAgent 输出 → 归档文件 → 调用 FileApplication

---

## 5. Prompt 管理

所有 LLM Prompt 独立文件，存放在：

```text
teambrain_core/prompts/
```

文件：

```text
router.txt
task_extract.txt
meeting_extract.txt
query.txt
```

禁止 Prompt 硬编码在代码中。

---

## 6. 无状态原则

RouterAgent 无状态。

所有状态保存在：

```text
messages
events
tasks
```

禁止 Agent 内存状态。

---

## 7. 禁止事项

1. 禁止 TeamBrain Agent 夺舍 AstrBot 主 Agent。
2. 禁止 MVP 把 AstrBot 全局降级为纯 IM Gateway。
3. 禁止 RouterAgent 直接写业务表。
4. 禁止 Handler 直接依赖 AstrBot 原始对象。
5. 禁止 Agent 绕过用户权限。
6. 禁止 MVP 一开始拆出大量专项 Agent。

---

## 8. V2 展望

后续可扩展：

```text
QueryAgent 升级为独立 Agent
TaskAgent
MeetingAgent
KnowledgeAgent
Planner Agent
Workflow Agent
```

但 MVP 不实现。
