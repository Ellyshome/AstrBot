# 06-MVP数据库设计

## 1. 设计目标

MVP 数据库用于支撑 IM 入口下的最小闭环：

```text
消息入库
用户映射
项目关联
文件记录
会议记录
任务创建
事件追踪
简单查询
```

第一阶段使用 PostgreSQL 作为唯一事实源。

---

## 2. 必建表

MVP 必建表：

```text
users
roles
user_roles
projects
project_members
user_im_bindings
conversations
messages
files
knowledge_packages
document_chunks
meetings
tasks
events
```

`document_chunks` 对普通项目文件可延后；对公司制度、规章、既定业务流程知识包应作为 MVP 必做，用于支持优先检索。

---

## 3. users

系统用户表。

核心字段：

```text
id UUID PK
username varchar
real_name varchar
email varchar
phone varchar
status varchar
created_at timestamp
updated_at timestamp
```

状态：

```text
active
inactive
```

---

## 4. roles / user_roles

MVP 只做三类角色：

```text
admin
member
guest
```

完整 RBAC 后置。

---

## 5. projects

项目表。

核心字段：

```text
id UUID PK
code varchar
name varchar
description text
status varchar
start_date date
end_date date
created_by UUID
created_at timestamp
updated_at timestamp
```

状态：

```text
planning
active
closed
```

---

## 6. project_members

项目成员关系表。

核心字段：

```text
id UUID PK
project_id UUID
user_id UUID
role_in_project varchar
created_at timestamp
```

MVP 用于判断用户是否属于项目。

---

## 7. user_im_bindings

IM 用户绑定表。

核心字段：

```text
id UUID PK
user_id UUID
im_platform varchar
im_user_id varchar
im_display_name varchar
status varchar
created_at timestamp
updated_at timestamp
```

唯一约束：

```text
im_platform + im_user_id
```

作用：

```text
将 AstrBot 消息发送人映射为系统 users.id
```

---

## 8. conversations

IM 会话表。

核心字段：

```text
id UUID PK
im_platform varchar
conversation_type varchar
conversation_id varchar
group_id varchar
title varchar
project_id UUID nullable
created_at timestamp
updated_at timestamp
```

`conversation_type`：

```text
group
private
```

---

## 9. messages

IM 消息表。所有 IM 消息必须先写入此表。

核心字段：

```text
id UUID PK
event_id varchar unique
conversation_id UUID
sender_user_id UUID nullable
sender_im_id varchar
sender_name varchar
message_type varchar
direction varchar
content text
attachments jsonb
raw_payload jsonb
intent varchar nullable
status varchar
created_at timestamp
```

`direction`：

```text
user_to_agent
agent_to_user
system
```

`status`：

```text
received
processed
failed
ignored
```

---

## 10. files

文件元数据表。

核心字段：

```text
id UUID PK
file_no varchar unique
project_id UUID nullable
message_id UUID nullable
filename varchar
file_type varchar
bucket varchar nullable
object_key varchar nullable
storage_path text
file_size bigint
uploaded_by UUID nullable
uploaded_at timestamp
parse_status varchar
created_at timestamp
```

`parse_status`：

```text
pending
parsed
failed
skipped
```

---

## 11. knowledge_packages

知识包表，用于维护公司规章制度、既定业务流程、标准模板等资料集合。

MVP 至少需要一个默认知识包：

```text
公司制度与业务流程知识包
```

核心字段：

```text
id UUID PK
package_code varchar unique
name varchar
description text
package_type varchar
status varchar
priority int
created_by UUID nullable
created_at timestamp
updated_at timestamp
```

`package_type` 建议：

```text
company_policy
business_process
project_knowledge
general_document
```

`status` 建议：

```text
active
inactive
archived
```

`priority` 用于检索优先级。公司制度和既定流程知识包默认优先级最高。

---

## 12. document_chunks

文档切片表，用于简单 RAG。

核心字段：

```text
id UUID PK
file_id UUID
knowledge_package_id UUID nullable
chunk_index int
content text
embedding vector nullable
metadata jsonb nullable
created_at timestamp
```

MVP 如不启用 pgvector，可先不写 embedding。

公司制度、规章、既定业务流程类文件解析后，应写入 `document_chunks` 并关联 `knowledge_package_id`。

---

## 13. meetings

会议记录表。

核心字段：

```text
id UUID PK
meeting_no varchar unique
project_id UUID nullable
title varchar
meeting_date timestamp nullable
summary text
file_id UUID nullable
source_message_id UUID nullable
created_by UUID nullable
created_at timestamp
```

---

## 14. tasks

任务表。

核心字段：

```text
id UUID PK
task_no varchar unique
project_id UUID nullable
meeting_id UUID nullable
source_message_id UUID nullable
title varchar
description text
owner_id UUID nullable
owner_text varchar nullable
status varchar
due_date timestamp nullable
due_text varchar nullable
created_by UUID nullable
created_at timestamp
updated_at timestamp
```

`owner_text` 用于责任人尚未匹配系统用户时保存原始文本。

状态：

```text
todo
in_progress
completed
closed
cancelled
```

---

## 15. events

事件追踪表。

MVP 中 `events` 统一承载轻量事件记录。

核心字段：

```text
id UUID PK
event_no varchar unique nullable
event_type varchar
entity_type varchar nullable
entity_id UUID nullable
project_id UUID nullable
user_id UUID nullable
message_id UUID nullable
payload jsonb
status varchar
created_at timestamp
```

MVP 事件类型：

```text
im_message_received
business_event_recorded
file_uploaded
meeting_recorded
task_created
query_requested
system_error
```

---

## 16. 入库顺序

所有 IM 消息：

```text
conversations
→ messages
→ events(im_message_received)
```

触发业务后：

```text
files / meetings / tasks / events
→ Agent 回复 messages
```

制度流程文件入库后：

```text
files
→ knowledge_packages
→ document_chunks
→ 查询时优先检索对应知识包
```

---

## 17. MVP 后续拆分

如果 events 表过大，后续可拆分：

```text
business_events
audit_events
integration_events
system_events
```

MVP 不拆，降低复杂度。