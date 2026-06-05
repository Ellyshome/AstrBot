# 02-总体架构-插件壳加Core内核

## 1. 总体结构

```text
IM 平台
  ↓
AstrBot IM 接入
  ↓
AstrBot Plugin Shell: team_brain_agent
  ↓
StandardMessage
  ↓
TeamBrain Core
  ↓
PostgreSQL + pgvector
  ↓
ReplyMessage
  ↓
AstrBot Plugin Shell
  ↓
IM 回复
```

---

## 2. AstrBot Plugin Shell 定位

Plugin Shell 只负责：

```text
接收 AstrBot 消息事件
转换为 StandardMessage
调用 TeamBrain Core
发送 ReplyMessage
插件生命周期管理
加载配置
```

禁止：

```text
业务规则
SQL
知识库检索
Prompt
LLM 决策
任务状态流转
```

---

## 3. TeamBrain Core 定位

TeamBrain Core 是业务系统内核。

负责：

```text
分域接管
消息入库
用户映射
项目识别
Intent 识别
Application 编排
Service 调用
知识库检索
业务对象创建
回复生成
```

TeamBrain Core 不依赖 AstrBot 原始对象，只依赖标准协议：

```text
StandardMessage
RouteDecision
ReplyMessage
HandlerResult
```

---

## 4. 运行形态

MVP 阶段：

```text
TeamBrain Core 以内嵌 Python 包形式运行在 AstrBot 插件目录内
```

未来阶段：

```text
TeamBrain Core 可迁移为独立 HTTP / Worker 服务
AstrBot Plugin Shell 改为 IM Gateway Adapter
```

---

## 5. 核心链路

```text
main.py
→ AstrBotInboundAdapter.to_standard_message()
→ TeamBrainCore.handle_message()
→ DomainTakeoverService.decide()
→ MessageApplication.process()
→ RouterAgent.route()
→ Handler / QueryApplication
→ ReplyMessage
→ AstrBotOutboundSender.send()
```

---

## 6. 层级划分

```text
adapters：外部系统适配，含 AstrBot 入站/出站
application：流程编排、事务边界、调用 Service
services：业务服务，处理核心业务规则
domain：领域模型、状态、值对象
repositories：数据库读写抽象
infrastructure：数据库、LLM、Embedding、文件存储、解析器
prompts：Prompt 模板
migrations：数据库迁移
```

---

## 7. 后续独立服务化原则

未来拆出独立服务时，优先保持以下目录不变：

```text
teambrain_core/application
teambrain_core/domain
teambrain_core/services
teambrain_core/repositories
teambrain_core/infrastructure
teambrain_core/prompts
```

只替换：

```text
adapters/astrbot
```

或新增：

```text
adapters/http
adapters/feishu
adapters/wecom
```
