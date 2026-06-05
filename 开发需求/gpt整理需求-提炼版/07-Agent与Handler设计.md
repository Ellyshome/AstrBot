# 07-Agent与Handler设计

## 1. 设计原则

MVP 阶段不拆大量 Agent。

采用：

```text
少量 Agent + 多个 Handler + Service
```

这样既能保持架构清晰，又避免过早复杂化。

---

## 2. MVP 组件分工

```text
Router Agent
Query Agent
Event Handler
File Handler
Meeting Handler
Task Handler
Archive Service
Domain Service
Repository
```

---

## 3. Router Agent

职责：

```text
接收标准消息
判断是否属于团队大脑业务域
判断 intent
选择 Handler 或 Query Agent
生成处理结果
返回接管 / 放行结果
```

不负责：

```text
写数据库
解析文件正文
直接调用 AstrBot
执行复杂业务规则
替换 AstrBot 主 Agent
处理非团队大脑业务域消息
```

MVP intent：

```text
chat
event_record
file_upload
meeting_record
task_record
query
unknown
```

---

## 4. Query Agent

职责：

```text
处理查询类消息
查询任务、文件、会议、事件
组织回答文本
```

MVP 查询范围：

```text
未完成任务
最近文件
最近会议
最近事件
查询公司制度、规章、既定业务流程知识包
```

制度流程知识包检索属于 MVP 必做；普通项目文件的 RAG 查询可作为增强能力。

---

## 5. Event Handler

处理事件录入。

输入：

```text
标准消息
用户信息
项目上下文
```

输出：

```text
events 记录
回复文本
```

---

## 6. File Handler

处理文件上传。

职责：

```text
保存文件元数据
关联 message_id / event_id
可选转存 MinIO
可选生成 document_chunks
```

---

## 7. Meeting Handler

处理会议记录。

职责：

```text
创建 meetings
保存会议摘要
关联文件
可选抽取任务
```

MVP 允许先只保存会议文本，不强制任务抽取。

---

## 8. Task Handler

处理任务创建。

职责：

```text
抽取任务标题
抽取责任人文本
抽取截止时间文本
创建 tasks
```

责任人无法匹配时写入 `owner_text`。

---

## 9. Archive Service

MVP 中 Archive 不作为 Agent，先作为 Service。

职责：

```text
统一归档消息
归档文件元数据
归档事件
维护关联关系
```

后续可升级为 Archive Agent。

---

## 10. Service 层

Service 层负责业务规则。

示例：

```text
MessageService
FileService
MeetingService
TaskService
EventService
UserService
ProjectService
```

---

## 11. Repository 层

Repository 只负责数据库操作。

示例：

```text
MessageRepository
TaskRepository
FileRepository
MeetingRepository
EventRepository
```

禁止在 Agent 或 Handler 中直接拼 SQL。

---

## 12. 后续升级路径

```text
Handler 稳定
→ 抽象业务流程
→ 引入 LangGraph
→ 升级为专项 Agent
```

例如：

```text
Meeting Handler → Meeting Agent
Task Handler → Planning Agent
File Handler → Archive Agent
```

---

## 13. 审计要求

所有 Agent / Handler 关键动作写入日志或 events：

```text
intent_detected
handler_started
handler_completed
handler_failed
```

---

## 14. 禁止事项

1. 禁止团队大脑 Agent 夺舍 AstrBot 主 Agent。
2. 禁止 MVP 阶段将 AstrBot 全局降级为纯 IM Gateway。
3. 禁止 Router Agent 直接写业务表。
4. 禁止 Handler 直接依赖 AstrBot 原始对象。
5. 禁止 Agent 绕过用户权限。
6. 禁止 MVP 一开始拆出大量专项 Agent。