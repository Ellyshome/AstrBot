# 21-Service设计.md

# 一、Service层定位

Service层是系统业务核心。

负责：

```text
业务规则
状态流转
事务控制
跨实体协调
```

禁止：

```text
SQL
AstrBot调用
HTTP请求
```

---

# 二、ProjectService

职责：

```text
项目识别
项目归属
项目查询
项目成员管理
```

接口：

```python
resolve_project()

find_project()

list_projects()

get_project()
```

项目识别优先级：

```text
消息明确项目名

↓

群绑定项目

↓

最近活跃项目

↓

人工确认
```

---

# 三、MessageService

职责：

```text
消息留存
消息追溯
消息关联
```

接口：

```python
save_message()

get_message()

trace_source()
```

说明：

所有业务对象必须可追溯到原始消息。

---

# 四、EventService

职责：

```text
事件记录
事件查询
事件统计
```

接口：

```python
create_event()

list_events()

get_event()
```

---

# 五、TaskService

职责：

```text
任务创建
任务分配
任务关闭
任务查询
```

接口：

```python
create_task()

assign_task()

close_task()

list_tasks()
```

任务状态：

```text
TODO

IN_PROGRESS

DONE

CANCELLED
```

---

# 六、MeetingService

职责：

```text
会议归档
会议检索
会议摘要
```

接口：

```python
create_meeting()

list_meetings()

get_meeting()
```

---

# 七、KnowledgeService

职责：

```text
知识包管理
文档导入
向量检索
知识问答
```

接口：

```python
create_package()

import_document()

search()

ask()
```

---

# 八、QueryService

统一查询入口。

负责：

```text
自然语言查询
查询路由
结果聚合
```

接口：

```python
query()
```

调用：

```text
TaskService

EventService

MeetingService

KnowledgeService
```

---

# 九、EmbeddingService

职责：

```text
文本切片

Embedding生成

向量写入
```

接口：

```python
chunk()

embed()

store_vector()
```

使用：

```text
BGE-M3
```

统一封装。

---

# 十、StorageService

职责：

```text
文件存储

文件读取

文件归档
```

接口：

```python
save()

load()

delete()
```

禁止业务层直接访问文件路径。
