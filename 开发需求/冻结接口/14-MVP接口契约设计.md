# 14-MVP接口契约设计

## 1. 统一消息对象（StandardMessage）

所有IM渠道（QQ、企业微信、飞书等）进入系统后，统一转换为 StandardMessage。

```python
class StandardMessage:
    message_id: str
    platform: str
    sender_id: str
    sender_name: str
    group_id: str | None
    group_name: str | None
    content: str
    attachments: list
    timestamp: datetime
```

示例：

```json
{
  "message_id":"msg_001",
  "platform":"qq",
  "sender_id":"12345",
  "sender_name":"张三",
  "group_id":"g001",
  "group_name":"未来城项目群",
  "content":"记录一下，今天完成了样板段放线。",
  "attachments":[],
  "timestamp":"2026-06-01T10:30:00"
}
```

---

# 2. Router Agent

职责：

判断消息类型，并路由到对应处理器。

输入：

```python
StandardMessage
```

输出：

```python
RouteDecision
```

```python
class RouteDecision:
    takeover: bool
    intent: str
    confidence: float
    handler: str
```

示例：

```json
{
  "takeover": true,
  "intent": "event_record",
  "confidence": 0.95,
  "handler": "event_handler"
}
```

---

# 3. Event Handler

输入：

```python
EventCommand
```

```python
class EventCommand:
    project_id:int
    content:str
    creator_id:int
```

输出：

```python
class HandlerResult:
    success:bool
    object_id:int
    reply:str
```

示例：

```json
{
  "success":true,
  "object_id":101,
  "reply":"事件已记录"
}
```

---

# 4. Task Handler

输入：

```python
class TaskCommand:
    project_id:int
    title:str
    description:str
    assignee_id:int|None
    creator_id:int
```

输出：

```python
{
  "success":true,
  "object_id":201,
  "reply":"任务已创建"
}
```

---

# 5. Meeting Handler

输入：

```python
class MeetingCommand:
    project_id:int
    title:str
    summary:str
    attendees:list
```

输出：

```python
{
  "success":true,
  "object_id":301,
  "reply":"会议纪要已归档"
}
```

---

# 6. File Handler

输入：

```python
class FileCommand:
    project_id:int
    file_path:str
    file_name:str
    uploader_id:int
```

输出：

```python
{
  "success":true,
  "object_id":401,
  "reply":"文件已归档"
}
```

---

# 7. Query Agent

输入：

```python
class QueryCommand:
    query:str
    project_id:int|None
```

输出：

```python
class QueryResult:
    answer:str
    references:list
```

示例：

```json
{
  "answer":"未来城项目共有12项未关闭任务",
  "references":[
      {
        "type":"task",
        "id":12
      }
  ]
}
```

---

# 8. LLM统一输出格式

所有结构化提取必须返回JSON。

禁止返回自然语言描述。

标准格式：

```json
{
  "intent":"task_record",
  "project":"未来城",
  "data":{
      ...
  }
}
```

解析失败：

```json
{
  "intent":"unknown",
  "reason":"extract_failed"
}
```
