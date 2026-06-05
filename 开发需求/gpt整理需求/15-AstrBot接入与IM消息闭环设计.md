# 15-AstrBot接入与IM消息闭环设计

> 团队大脑 Agent 系统  
> 文档版本：V1.0  
> 最后更新：2026-06  
> 状态：MVP落地设计文档

---

# 1. 文档目标

本文档用于补齐 MVP 阶段最关键的入口设计：

```text
AstrBot / IM 消息
→ 团队大脑模块
→ 消息入库
→ 意图识别
→ 业务处理
→ IM 回复
```

本阶段目标不是完整实现企业数字大脑，而是先跑通一个稳定的 IM 使用闭环。

---

# 2. MVP入口原则

第一阶段以 IM 为主要入口。

原因：

1. 用户不需要学习新系统。
2. 可以复用 AstrBot 的 QQ / 企业微信等多 IM 接入能力。
3. 消息天然包含业务上下文。
4. 适合从轻量录入、查询、提醒开始。

第一阶段暂不强依赖完整 Web 平台。

---

# 3. 总体链路

```text
用户在 IM 发送消息
        ↓
AstrBot 接收消息
        ↓
团队大脑插件入口
        ↓
IM 消息标准化
        ↓
生成 event_id
        ↓
写入 messages / conversations
        ↓
Router Agent 判断意图
        ↓
分派到对应处理器
        ↓
写入 events / files / meetings / tasks
        ↓
生成回复内容
        ↓
通过 AstrBot 回发 IM
```

---

# 4. AstrBot 插件定位

AstrBot 插件只作为接入层，不承载复杂业务逻辑。

插件职责：

```text
接收消息
标准化消息
调用团队大脑入口函数
发送回复
记录异常
```

插件不负责：

```text
复杂意图识别
业务规则判断
权限决策
数据库业务写入
知识库问答生成
```

---

# 5. 建议代码入口

建议在项目中建立独立插件模块：

```text
integrations/astrbot/
  plugin.py
  adapter.py
  sender.py
  user_mapper.py
```

职责：

| 文件 | 职责 |
|---|---|
| plugin.py | AstrBot 插件入口，接收消息事件 |
| adapter.py | 将 AstrBot 原始消息转为系统标准消息 |
| sender.py | 封装消息回复能力 |
| user_mapper.py | IM 用户 ID 与系统用户映射 |

---

# 6. 标准 IM 消息结构

所有来自 AstrBot 的消息统一转换为以下结构：

```json
{
  "event_id": "EV-20260605-000001",
  "source": "astrbot",
  "im_platform": "qq",
  "conversation_type": "group",
  "conversation_id": "group_123456",
  "group_id": "group_123456",
  "sender_im_id": "qq_10001",
  "sender_name": "张三",
  "receiver_im_id": null,
  "message_type": "text",
  "content": "记录一下，今天1号楼地下室防水验收完成",
  "attachments": [],
  "raw_payload": {},
  "received_at": "2026-06-05T10:00:00"
}
```

---

# 7. event_id 规则

每条进入系统的 IM 消息必须生成 `event_id`。

建议格式：

```text
EV-YYYYMMDD-000001
```

用途：

1. 关联原始消息。
2. 关联业务事件。
3. 关联文件。
4. 关联任务。
5. 支持日志追踪。

---

# 8. 用户映射

AstrBot 中的 IM 用户不是系统用户。

需要建立映射关系：

```text
im_platform + im_user_id
→ user_id
```

MVP 阶段处理策略：

| 情况 | 处理 |
|---|---|
| 已映射用户 | 正常处理 |
| 未映射用户 | 允许记录消息，但业务写入需提示绑定用户 |
| 群聊用户 | 先根据 sender_im_id 映射 |
| Agent 自己发送 | 标记为 system / agent |

建议后续增加表：

```text
user_im_binding
```

字段：

```text
id
user_id
im_platform
im_user_id
im_display_name
status
created_at
```

---

# 9. 会话与消息入库

第一阶段建议使用两层记录：

```text
conversation
message
```

如果为了快速启动，也可以先只使用 `messages` 表。

## 9.1 conversation

表示一个群聊或单聊会话。

核心字段：

```text
id
im_platform
conversation_type
conversation_id
group_id
title
project_id
created_at
updated_at
```

## 9.2 message

表示一条具体消息。

核心字段：

```text
id
event_id
conversation_id
sender_id
sender_im_id
message_type
content
attachments
raw_payload
direction
created_at
```

---

# 10. 意图识别范围

MVP 阶段只识别 5 类意图：

| intent | 说明 | 示例 |
|---|---|---|
| chat | 普通消息，仅记录 | 大家下午开会 |
| event_record | 事件录入 | 记录一下，防水验收完成 |
| file_upload | 文件上传 | 上传一份会议纪要 |
| task_record | 任务/计划录入 | 张三下周五前完成整改 |
| query | 查询问答 | 查一下未来城有哪些未完成任务 |

暂不实现复杂审批、复杂工作流和多 Agent 协同。

---

# 11. 路由规则

MVP 阶段可先采用关键词规则 + LLM 辅助。

优先级：

```text
文件/附件 > 明确查询 > 明确任务 > 明确记录 > 普通消息
```

关键词示例：

| 关键词 | intent |
|---|---|
| 查一下 / 查询 / 有没有 / 哪些 | query |
| 任务 / 截止 / 负责 / 完成时间 | task_record |
| 记录一下 / 上报 / 录入 / 完成 / 验收 | event_record |
| 上传 / 文件 / 图纸 / 纪要 | file_upload |

---

# 12. 业务处理闭环

## 12.1 普通消息

```text
标准化
→ 生成 event_id
→ 消息入库
→ 不触发业务事件
→ 可配置是否回复
```

## 12.2 事件录入

```text
标准化
→ 消息入库
→ 识别 event_record
→ 创建 events 记录
→ 回复事件编号
```

## 12.3 文件上传

```text
标准化
→ 消息入库
→ 附件暂存
→ 写入 files
→ 后续解析文档切片
→ 回复文件编号
```

## 12.4 任务录入

```text
标准化
→ 消息入库
→ 抽取任务标题、责任人、截止时间
→ 写入 tasks
→ 回复任务编号
```

## 12.5 查询问答

```text
标准化
→ 消息入库
→ 判断查询范围
→ 检索 PostgreSQL / document_chunks
→ 生成回答
→ 回复 IM
```

---

# 13. 回复策略

MVP 阶段需要避免群聊刷屏。

建议：

| 场景 | 回复策略 |
|---|---|
| 单聊普通消息 | 可回复 |
| 群聊普通消息 | 默认不回复 |
| 群聊中 @Agent | 回复 |
| 事件录入成功 | 回复 |
| 任务创建成功 | 回复 |
| 文件上传成功 | 回复 |
| 查询问答 | 回复 |
| 处理失败 | 回复简短错误 |

---

# 14. 回复格式示例

事件录入成功：

```text
已记录该事件。
事件编号：EVT-20260605-000001
类型：施工/验收
```

任务创建成功：

```text
已创建任务。
任务编号：TASK-20260605-000001
责任人：张三
截止时间：2026-06-12
```

文件上传成功：

```text
文件已归档。
文件编号：FILE-20260605-000001
文件名：项目会议纪要.docx
```

未知用户：

```text
已收到消息，但尚未识别您的系统身份。请联系管理员绑定账号后再进行业务录入。
```

---

# 15. MVP 数据写入顺序

一条事件录入消息的写入顺序：

```text
1. 生成 event_id
2. 写入 messages
3. 写入 events，event_type = im_message_received
4. 识别意图 event_record
5. 写入 events，event_type = business_event_recorded
6. 写入 Agent 回复 messages
```

如果触发任务：

```text
额外写入 tasks
```

如果包含文件：

```text
额外写入 files / document_chunks
```

---

# 16. 异常处理

异常分为三类：

| 类型 | 处理 |
|---|---|
| 消息解析失败 | 记录原始 payload，回复用户稍后处理 |
| 数据库写入失败 | 记录日志，回复系统异常 |
| 业务识别失败 | 作为普通消息入库，不中断流程 |

原则：

```text
消息尽量先入库
业务失败不影响消息留痕
```

---

# 17. MVP 完成标准

满足以下条件即认为 AstrBot 接入闭环完成：

1. AstrBot 能将 QQ/IM 消息传入团队大脑模块。
2. 系统能生成 `event_id`。
3. 原始消息能写入数据库。
4. 系统能区分普通消息、事件录入、任务录入、文件上传、查询。
5. 事件录入能写入 `events`。
6. 任务录入能写入 `tasks`。
7. 文件上传能写入 `files`。
8. 查询能返回基础结果。
9. Agent 回复能通过 AstrBot 发回 IM。
10. 失败场景有日志和用户提示。

---

# 18. 后续扩展

MVP 跑通后再扩展：

1. 多轮补全。
2. 用户账号自助绑定。
3. 群聊自动识别项目。
4. 文件自动解析与向量化。
5. 计划任务定时提醒。
6. 复杂权限校验。
7. LangGraph 工作流。
8. 多 Agent 协同。
