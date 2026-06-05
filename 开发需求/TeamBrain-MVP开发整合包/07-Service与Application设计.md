# 07-Service与Application设计

## 1. 层级定位

```text
Application层：流程编排、事务边界、调用Service
Service层：业务规则、状态流转、跨实体协调
Repository层：数据库读写抽象
```

禁止：

```text
Application 直接写 SQL
Service 直接依赖 AstrBot 对象
Repository 包含业务规则
```

---

## 2. Application 层

### MessageApplication

职责：

```text
接管消息入库
调用 DomainTakeoverService
调用 RouterAgent
分发到 Handler
生成回复
```

接口：

```python
async def handle_message(self, msg: StandardMessage) -> ReplyMessage | None: ...
```

### TaskApplication

职责：

```text
任务创建编排
保存消息 → 创建任务 → 记录事件 → 返回结果
```

### EventApplication

职责：

```text
事件记录编排
```

### MeetingApplication

职责：

```text
会议记录编排
```

### FileApplication

职责：

```text
文件归档编排
```

### QueryApplication

职责：

```text
查询编排
判断是否需要公司制度依据
调用 KnowledgeService 优先检索
调用结构化数据查询
聚合结果
```

### KnowledgeApplication

职责：

```text
知识包管理
文档导入
文件解析调度
切片与向量化调度
```

---

## 3. Service 层

### DomainTakeoverService

职责：

```text
根据会话模式、@状态、业务关键词、项目群配置
判断是否接管当前消息
```

接口：

```python
def decide(self, msg: StandardMessage, conversation: Conversation) -> RouteDecision: ...
```

输出 `RouteDecision`，含：

```text
takeover / mode / intent / handler / should_reply / reason
```

### UserBindingService

职责：

```text
IM 用户映射为系统用户
未绑定用户标记
```

接口：

```python
def resolve_user(self, platform: str, im_user_id: str) -> User | None: ...
```

### ProjectService

职责：

```text
项目识别
项目查询
项目成员管理
```

接口：

```python
def resolve_project(self, msg: StandardMessage, user_id: str) -> Project | None: ...
def list_projects(self) -> list[Project]: ...
```

### MessageService

职责：

```text
消息留痕
消息查询
消息追溯
```

接口：

```python
def save(self, msg: StandardMessage, ...) -> Message: ...
def get_by_event_id(self, event_id: str) -> Message: ...
```

### TaskService

职责：

```text
任务创建
任务分配
任务关闭
任务查询
```

任务状态：

```text
todo → in_progress → completed → closed / cancelled
```

### EventService

职责：

```text
事件记录
事件查询
```

### MeetingService

职责：

```text
会议归档
会议查询
```

### FileService

职责：

```text
文件元数据管理
文件存储调度
```

### QueryService

职责：

```text
统一查询入口
调用 KnowledgeService.search() + 结构化查询
聚合结果生成回答
```

### KnowledgeService

职责：

```text
知识包 CRUD
文档导入
检索
```

接口：

```python
def search(self, query: str, package_id: UUID | None = None, top_k: int = 8) -> list[SearchResult]: ...
```

### EmbeddingService

职责：

```text
文本切片
Embedding 生成
向量写入
```

使用 BGE-M3。

切片参数：

```text
chunk_size: 600
overlap: 120
```

### StorageService

职责：

```text
文件存储
文件读取
```

禁止业务层直接访问文件路径。
