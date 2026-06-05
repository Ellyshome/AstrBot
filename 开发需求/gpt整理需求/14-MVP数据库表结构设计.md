# 14-MVP数据库表结构设计.md

> 团队大脑 Agent 系统
>
> 文档版本：V1.0
>
> 最后更新：2026-06
>
> 状态：开发实施文档

---

# 1. 文档目标

定义MVP阶段数据库设计。

用于指导：

* PostgreSQL建库
* SQLAlchemy建模
* Alembic迁移
* Repository实现
* API开发

---

# 2. MVP设计原则

MVP仅保留：

```text
用户
项目
文件
会议
任务
文档切片
```

---

暂不建设：

```text
知识图谱
知识演化
标准库
Agent协同
```

---

# 3. 数据库总体结构

```text
users

roles

projects

project_members

files

document_chunks

meetings

tasks

events
```

---

# 4. users

用户表

---

字段：

| 字段         | 类型           |
| ---------- | ------------ |
| id         | UUID         |
| username   | varchar(100) |
| real_name  | varchar(100) |
| email      | varchar(200) |
| phone      | varchar(50)  |
| status     | varchar(20)  |
| created_at | timestamp    |
| updated_at | timestamp    |

---

SQLAlchemy：

```python
class User(Base):
    id: UUID
    username: str
    real_name: str
    email: str
```

---

# 5. roles

角色表

---

字段：

| 字段          | 类型           |
| ----------- | ------------ |
| id          | UUID         |
| name        | varchar(100) |
| description | text         |

---

示例：

```text
admin

manager

member

guest
```

---

# 6. user_roles

用户角色关系表

---

字段：

| 字段      | 类型   |
| ------- | ---- |
| user_id | UUID |
| role_id | UUID |

---

多对多。

---

# 7. projects

项目表

---

字段：

| 字段          | 类型           |
| ----------- | ------------ |
| id          | UUID         |
| code        | varchar(50)  |
| name        | varchar(255) |
| description | text         |
| status      | varchar(50)  |
| start_date  | date         |
| end_date    | date         |
| created_by  | UUID         |
| created_at  | timestamp    |

---

状态：

```text
planning

active

closed
```

---

# 8. project_members

项目成员

---

字段：

| 字段              | 类型           |
| --------------- | ------------ |
| id              | UUID         |
| project_id      | UUID         |
| user_id         | UUID         |
| role_in_project | varchar(100) |

---

示例：

```text
项目经理

设计经理

工程经理
```

---

# 9. files

文件表

---

注意：

```text
只存元数据
```

---

实际文件：

```text
MinIO
```

---

字段：

| 字段          | 类型           |
| ----------- | ------------ |
| id          | UUID         |
| project_id  | UUID         |
| filename    | varchar(500) |
| file_type   | varchar(50)  |
| bucket      | varchar(100) |
| object_key  | varchar(500) |
| file_size   | bigint       |
| uploaded_by | UUID         |
| uploaded_at | timestamp    |

---

# 10. 文件分类

建议：

```text
drawing

meeting

contract

report

image

other
```

---

# 11. document_chunks

文档切片

---

RAG核心表。

---

字段：

| 字段          | 类型        |
| ----------- | --------- |
| id          | UUID      |
| file_id     | UUID      |
| chunk_index | int       |
| content     | text      |
| embedding   | vector    |
| created_at  | timestamp |

---

# 12. pgvector

Embedding字段：

```sql
vector(1024)
```

或：

```sql
vector(1536)
```

取决于Embedding模型。

---

# 13. meetings

会议表

---

字段：

| 字段           | 类型           |
| ------------ | ------------ |
| id           | UUID         |
| project_id   | UUID         |
| title        | varchar(500) |
| meeting_date | timestamp    |
| summary      | text         |
| file_id      | UUID         |
| created_by   | UUID         |
| created_at   | timestamp    |

---

# 14. 会议纪要来源

来源：

```text
Word

Markdown

录音转文字
```

---

统一进入：

```text
meetings
```

---

# 15. tasks

任务表

---

MVP核心表。

---

字段：

| 字段          | 类型           |
| ----------- | ------------ |
| id          | UUID         |
| project_id  | UUID         |
| meeting_id  | UUID         |
| title       | varchar(500) |
| description | text         |
| owner_id    | UUID         |
| status      | varchar(50)  |
| due_date    | timestamp    |
| created_at  | timestamp    |

---

# 16. Task状态

```text
todo

in_progress

completed

closed
```

---

# 17. Meeting→Task

关系：

```text
Meeting

↓

Task
```

---

支持：

```text
会议纪要自动抽取任务
```

---

# 18. events

事件表

---

用于：

```text
审计

追踪

回放
```

---

字段：

| 字段          | 类型           |
| ----------- | ------------ |
| id          | UUID         |
| event_type  | varchar(100) |
| entity_type | varchar(100) |
| entity_id   | UUID         |
| payload     | jsonb        |
| created_at  | timestamp    |

---

# 19. event_type

示例：

```text
file_uploaded

meeting_created

task_created

task_completed
```

---

# 20. 索引设计

users：

```sql
idx_user_username
```

---

projects：

```sql
idx_project_name
```

---

files：

```sql
idx_file_project
```

---

tasks：

```sql
idx_task_owner
```

---

# 21. pgvector索引

使用：

```sql
ivfflat
```

---

示例：

```sql
CREATE INDEX idx_chunk_embedding
ON document_chunks
USING ivfflat (embedding vector_cosine_ops);
```

---

# 22. 外键关系

```text
Project

├── File

├── Meeting

└── Task
```

---

# 23. 文件关系

```text
File

↓

DocumentChunk
```

---

1:N

---

# 24. 会议关系

```text
Meeting

↓

Task
```

---

1:N

---

# 25. 用户关系

```text
User

↓

Task
```

---

1:N

---

# 26. MVP ER图

```text
User

│

├── ProjectMember

│       │

│       ▼

│    Project

│       │

├───────┼───────┐

│       │       │

▼       ▼       ▼

File  Meeting  Task

│

▼

DocumentChunk
```

---

# 27. MVP Repository

每张表对应：

```text
repository.py
```

---

例如：

```python
UserRepository

ProjectRepository

FileRepository

TaskRepository
```

---

# 28. MVP Service

业务逻辑层：

```python
ProjectService

MeetingService

TaskService
```

---

# 29. MVP API

第一批接口：

```text
POST /projects

GET /projects

POST /files

POST /meetings

POST /tasks
```

---

# 30. MVP Query Agent

问答流程：

```text
Question

↓

Embedding

↓

document_chunks

↓

TopK

↓

LLM
```

---

# 31. MVP权限

只做：

```text
Admin

Member
```

两级即可。

---

# 32. MVP审计

记录：

```text
创建

修改

删除
```

---

写入：

```text
events
```

---

# 33. MVP迁移管理

统一：

```text
Alembic
```

---

禁止：

```text
手工改库
```

---

# 34. MVP数据库规模

预计：

```text
100用户

100项目

10万Chunk
```

---

PostgreSQL足够。

---

# 35. MVP开发顺序

第一周：

```text
users

projects
```

---

第二周：

```text
files

document_chunks
```

---

第三周：

```text
meetings

tasks
```

---

第四周：

```text
query agent
```

---

# 36. MVP完成标志

完成：

```text
上传文件

自动切片

向量化

问答

会议抽取任务

任务追踪
```

即可上线试运行。

---

# 37. 设计结论

MVP阶段仅建设：

```text
User

Project

File

Meeting

Task

DocumentChunk

Event
```

七个核心实体。

以：

```text
PostgreSQL
+
pgvector
+
MinIO
```

为核心基础设施。

优先完成：

```text
文件沉淀

会议沉淀

任务闭环

知识检索
```

确保系统在最短时间内具备真实业务价值。
