# 15-schema.sql

## users

```sql
CREATE TABLE users(
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100),
    created_at TIMESTAMP
);
```

---

## user_im_bindings

```sql
CREATE TABLE user_im_bindings(
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT,
    platform VARCHAR(50),
    platform_uid VARCHAR(200)
);
```

---

## projects

```sql
CREATE TABLE projects(
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(100),
    name VARCHAR(200),
    status VARCHAR(50),
    created_at TIMESTAMP
);
```

---

## project_members

```sql
CREATE TABLE project_members(
    id BIGSERIAL PRIMARY KEY,
    project_id BIGINT,
    user_id BIGINT,
    role VARCHAR(50)
);
```

---

## messages

```sql
CREATE TABLE messages(
    id BIGSERIAL PRIMARY KEY,
    message_uid VARCHAR(200),
    project_id BIGINT,
    sender_id BIGINT,
    content TEXT,
    raw_json JSONB,
    created_at TIMESTAMP
);
```

---

## events

```sql
CREATE TABLE events(
    id BIGSERIAL PRIMARY KEY,
    project_id BIGINT,
    creator_id BIGINT,
    content TEXT,
    source_message_id BIGINT,
    created_at TIMESTAMP
);
```

---

## tasks

```sql
CREATE TABLE tasks(
    id BIGSERIAL PRIMARY KEY,
    project_id BIGINT,
    title VARCHAR(500),
    description TEXT,
    assignee_id BIGINT,
    status VARCHAR(50),
    due_date DATE,
    source_message_id BIGINT,
    created_at TIMESTAMP
);
```

---

## meetings

```sql
CREATE TABLE meetings(
    id BIGSERIAL PRIMARY KEY,
    project_id BIGINT,
    title VARCHAR(500),
    summary TEXT,
    source_message_id BIGINT,
    created_at TIMESTAMP
);
```

---

## files

```sql
CREATE TABLE files(
    id BIGSERIAL PRIMARY KEY,
    project_id BIGINT,
    file_name VARCHAR(500),
    file_path TEXT,
    file_type VARCHAR(50),
    uploader_id BIGINT,
    created_at TIMESTAMP
);
```

---

## knowledge_packages

```sql
CREATE TABLE knowledge_packages(
    id BIGSERIAL PRIMARY KEY,
    project_id BIGINT,
    title VARCHAR(500),
    description TEXT,
    created_at TIMESTAMP
);
```

---

## documents

```sql
CREATE TABLE documents(
    id BIGSERIAL PRIMARY KEY,
    package_id BIGINT,
    file_id BIGINT,
    title VARCHAR(500),
    content TEXT,
    created_at TIMESTAMP
);
```

---

## document_chunks

```sql
CREATE TABLE document_chunks(
    id BIGSERIAL PRIMARY KEY,
    document_id BIGINT,
    chunk_index INT,
    chunk_text TEXT,
    embedding_id VARCHAR(200)
);
```

---

# MVP阶段禁止新增表

除以下情况外不得新增：

1. 核心业务实体
2. 权限控制
3. 审计日志

其他需求统一使用JSONB扩展字段。
