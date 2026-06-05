# 01-MVP范围与阶段边界

## 1. MVP 目标

MVP 目标是让 TeamBrain 先在 AstrBot 基座内跑通最基本能力：

```text
IM 接入
分域接管
消息留痕
用户映射
项目识别
事件记录
任务创建
制度流程知识包问答
IM 回复
```

---

## 2. P0 必做范围

| 能力 | 说明 |
|---|---|
| AstrBot Plugin Shell | 作为消息接入与回复发送壳 |
| TeamBrain Core | 独立业务内核，不依赖 AstrBot 原始对象 |
| StandardMessage | 统一 IM 消息对象 |
| DomainTakeoverService | 判断观察 / 协作 / 托管模式下是否接管 |
| MessageService | 所有接管消息留痕 |
| UserBindingService | IM 用户映射为系统用户 |
| ProjectService | 简单项目识别 |
| RouterAgent | 单 Agent 路由，识别 intent |
| Handler | 事件、任务、文件、会议最小处理 |
| KnowledgeService | 公司制度与业务流程知识包检索 |
| ReplyMessage | 统一回复对象 |

---

## 3. P1 可做范围

```text
FastAPI 管理接口
知识包后台导入接口
文件解析增强
任务提醒定时扫描
更多查询类型
```

---

## 4. MVP 暂不做

```text
独立 TeamBrain 服务部署
完整 RBAC
复杂审批流
自动业务流生成
多 Agent 协作
LangGraph 工作流
Neo4j
GraphRAG
Kafka / MQ
复杂长期记忆
```

---

## 5. 分域接管原则

MVP 默认采用协作模式：

```text
命中 TeamBrain 业务域 → TeamBrain 接管
未命中 TeamBrain 业务域 → 放行给 AstrBot 原流程
```

三种模式：

| 模式 | 行为 | 用途 |
|---|---|---|
| 观察模式 | 只记录，不主动回复，不阻断 AstrBot | 新群试运行 |
| 协作模式 | 命中业务意图才接管 | MVP 默认 |
| 托管模式 | 指定会话中 TeamBrain 优先处理大多数消息 | 后期成熟后 |

---

## 6. Project 归属边界

正式项目业务对象原则上归属于 Project。

允许 `project_id` 为空的对象：

```text
原始消息
未识别项目的待处理消息
系统事件
公司级知识包
公司制度与业务流程文档
未绑定用户消息
```

后续可通过人工确认或自动识别补充项目归属。
