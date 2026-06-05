# 23-Agent设计.md

# 一、Agent设计原则

MVP采用：

```text
单Agent路由模式
```

不采用：

```text
多Agent协作
```

---

# 二、Agent架构

```text
Message

↓

RouterAgent

↓

Intent

↓

Application Service

↓

Result
```

---

# 三、RouterAgent

唯一Agent。

职责：

```text
意图识别

项目识别

参数提取

路由
```

输出：

```json
{
  "intent":"task_record",
  "project":"未来城",
  "data":{}
}
```

---

# 四、Intent类型

```text
task_record

event_record

meeting_record

file_record

query

chat
```

---

# 五、TaskAgent（逻辑模块）

职责：

```text
任务提取
```

输出：

```json
{
  "title":"",
  "assignee":"",
  "due_date":""
}
```

---

# 六、MeetingAgent（逻辑模块）

职责：

```text
会议解析
```

输出：

```json
{
  "title":"",
  "summary":""
}
```

---

# 七、KnowledgeAgent（逻辑模块）

职责：

```text
RAG查询
```

流程：

```text
问题

↓

检索

↓

上下文

↓

LLM回答
```

---

# 八、Prompt管理

所有Prompt必须独立文件。

目录：

```text
prompts/

router.txt

task_extract.txt

meeting_extract.txt

query.txt
```

禁止Prompt硬编码。

---

# 九、Agent状态原则

MVP：

```text
无状态
```

设计。

所有状态保存数据库。

禁止：

```text
Agent内存状态
```

---

# 十、V2规划

未来允许：

```text
Planner Agent

Knowledge Agent

Task Agent

Workflow Agent
```

协作。

但MVP不实现。
