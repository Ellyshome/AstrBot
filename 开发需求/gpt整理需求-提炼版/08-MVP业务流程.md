# 08-MVP业务流程

## 1. 流程范围

MVP 阶段只实现固定流程，不实现完整 Workflow Engine。

流程包括：

```text
普通消息入库
事件录入
文件上传
会议记录
任务创建
简单查询
异常处理
```

---

## 2. 通用前置流程

所有 IM 消息进入系统后，统一执行：

```text
接收 AstrBot 消息
→ 标准化消息
→ 生成 event_id
→ 查找或创建 conversation
→ 查找 user_im_binding
→ 写入 messages
→ 写入 events(im_message_received)
→ Router Agent 判断 intent
```

---

## 3. 普通消息流程

触发：

```text
intent = chat
```

流程：

```text
消息已入库
→ 不创建业务数据
→ 群聊默认不回复
→ 单聊可回复“已收到”
```

---

## 4. 事件录入流程

触发：

```text
intent = event_record
```

流程：

```text
检查用户是否绑定
→ 尝试识别项目
→ 生成事件标题
→ 写入 events(business_event_recorded)
→ 回复事件编号
```

未绑定用户：

```text
消息保留
→ 不写正式业务事件
→ 回复绑定提示
```

---

## 5. 文件上传流程

触发：

```text
intent = file_upload 或消息包含附件
```

流程：

```text
消息已入库
→ 提取附件元数据
→ 写入 files
→ 可选转存 MinIO
→ 可选生成 document_chunks
→ 写入 events(file_uploaded)
→ 回复文件编号
```

---

## 6. 会议记录流程

触发：

```text
intent = meeting_record
```

流程：

```text
消息已入库
→ 生成会议标题
→ 保存会议摘要
→ 关联项目 / 文件 / 消息
→ 写入 meetings
→ 写入 events(meeting_recorded)
→ 可选抽取 tasks
→ 回复会议编号
```

---

## 7. 任务创建流程

触发：

```text
intent = task_record
```

流程：

```text
消息已入库
→ 抽取任务标题
→ 抽取责任人文本
→ 抽取截止时间文本
→ 尝试匹配 owner_id
→ 写入 tasks
→ 写入 events(task_created)
→ 回复任务编号
```

---

## 8. 查询流程

触发：

```text
intent = query
```

流程：

```text
消息已入库
→ 写入 events(query_requested)
→ 判断查询类型
→ 判断是否需要公司制度、规章、既定流程依据
→ 如需要，优先检索公司制度与业务流程知识包
→ 再查询 PostgreSQL 结构化业务数据
→ 可选查询项目文件或普通 document_chunks
→ 生成回复
→ 回复 IM
```

MVP 查询类型：

```text
未完成任务
最近文件
最近会议
最近事件
公司制度、规章、既定业务流程问答
```

---

## 9. 异常处理流程

任何流程异常：

```text
捕获异常
→ 写日志
→ 写 events(system_error)
→ 回复简短失败提示
→ 不影响 AstrBot 主流程
```

原则：

```text
消息先留痕
业务可失败
失败可追踪
```

---

## 10. 回复入库流程

所有 Agent 回复也要写入 messages：

```text
生成回复文本
→ 调用 AstrBot 发送
→ 写入 messages(direction=agent_to_user)
```

---

## 11. 后续流程升级

当以上固定流程稳定后，再抽象为：

```text
Workflow Definition
LangGraph Runtime
State Machine
```

MVP 不强制实现。