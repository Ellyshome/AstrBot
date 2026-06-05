# 12-开发路线图与MVP实施计划.md

> 团队大脑 Agent 系统
>
> 文档版本：V1.0
>
> 最后更新：2026-06
>
> 状态：实施规划文档

---

# 1. 文档目标

定义系统开发路线图。

明确：

* MVP范围
* 优先级排序
* 实施阶段
* 人员配置
* 技术策略
* 风险控制

确保项目：

```text
快速上线
快速验证
快速迭代
```

避免：

```text
长期设计
长期开发
始终无法落地
```

---

# 2. 项目最终目标

构建：

```text
企业数字大脑
```

实现：

```text
文件管理

知识沉淀

经验传承

流程协同

Agent辅助决策
```

最终形成：

```text
组织级长期记忆系统
```

---

# 3. 开发原则

原则一：

```text
先可用
后完善
```

---

原则二：

```text
先人工
后自动
```

---

原则三：

```text
先业务闭环
后智能闭环
```

---

原则四：

```text
先沉淀事实
后沉淀知识
```

---

原则五：

```text
先MVP
后平台化
```

---

# 4. 三阶段路线图

系统建设分为：

```text
Phase 1
MVP

↓

Phase 2
Pilot

↓

Phase 3
Enterprise
```

---

# 5. Phase 1：MVP

目标：

```text
证明系统有价值
```

时间：

```text
8~12周
```

---

# 6. MVP成功标准

满足以下条件：

```text
团队愿意每天使用

资料持续上传

会议持续记录

知识持续积累
```

即视为成功。

---

# 7. MVP核心能力

仅保留：

```text
用户

项目

文件

会议

任务

Agent问答
```

---

# 8. MVP必须实现

模块：

```text
RBAC

Project

File

Meeting

Task

Knowledge Base

Query Agent
```

---

# 9. MVP暂不实现

以下全部延后：

```text
流程引擎

图谱推理

标准生成

复杂Agent协同

自动决策

ERP集成

BIM集成
```

---

# 10. MVP架构

```text
FastAPI

↓

PostgreSQL

↓

MinIO

↓

Redis

↓

LLM
```

---

# 11. MVP知识库

仅实现：

```text
Document

↓

Chunk

↓

Embedding

↓

RAG
```

---

不实现：

```text
Knowledge

Case

Standard
```

自动演化。

---

# 12. MVP Agent

仅保留：

```text
Query Agent
```

---

职责：

```text
文档问答

会议问答

项目问答
```

---

# 13. MVP会议系统

支持：

```text
上传会议纪要
```

---

自动抽取：

```text
责任人

任务

时间
```

---

生成：

```text
Task
```

记录。

---

# 14. MVP文件系统

支持：

```text
上传

分类

版本管理

检索
```

---

# 15. MVP任务系统

支持：

```text
创建

分派

完成

关闭
```

---

即可。

---

# 16. MVP数据库

仅使用：

```text
PostgreSQL
```

---

# 17. MVP向量库

推荐：

```text
pgvector
```

---

原因：

```text
无需独立部署
```

---

# 18. MVP图谱

不建设。

---

原因：

```text
收益低

维护高
```

---

# 19. MVP事件总线

仅采用：

```text
Redis Streams
```

---

# 20. MVP部署

单机部署：

```text
Docker Compose
```

---

服务：

```text
api

worker

postgres

redis

minio
```

---

# 21. MVP团队配置

推荐：

```text
1架构

2后端

1前端

1业务专家
```

---

总计：

```text
4~5人
```

---

# 22. MVP第1个月

目标：

```text
完成基础平台
```

---

完成：

```text
用户

权限

项目

文件
```

模块。

---

# 23. MVP第2个月

完成：

```text
会议

任务

知识库
```

模块。

---

# 24. MVP第3个月

完成：

```text
Agent问答

测试

上线
```

---

# 25. MVP验收标准

能够回答：

```text
某项目有哪些问题？

某会议安排了什么任务？

某图纸讨论过什么？

某材料出现过哪些风险？
```

---

即可上线。

---

# 26. Phase 2：Pilot

目标：

```text
部门级试运行
```

时间：

```text
3~6个月
```

---

# 27. Pilot新增能力

新增：

```text
Workflow

State Machine

Knowledge Graph

Event Bus
```

---

# 28. Pilot新增Agent

增加：

```text
Meeting Agent

Archive Agent

Design Agent
```

---

# 29. Pilot新增知识模型

新增：

```text
Fact

Case

Knowledge
```

---

# 30. Pilot新增图谱

引入：

```text
Neo4j
```

---

构建：

```text
项目图谱

任务图谱

知识图谱
```

---

# 31. Pilot新增工作流

实现：

```text
设计评审流程

会议闭环流程

问题整改流程
```

---

# 32. Pilot成功标准

达到：

```text
部门级使用

每周活跃

持续产生知识
```

---

# 33. Phase 3：Enterprise

目标：

```text
企业级数字大脑
```

---

# 34. Enterprise新增能力

新增：

```text
多Agent协同

企业标准生成

知识演化

组织记忆
```

---

# 35. Enterprise新增系统集成

接入：

```text
OA

ERP

CAD

BIM

企业微信
```

---

# 36. Enterprise新增知识层

形成：

```text
Document

↓

Fact

↓

Knowledge

↓

Case

↓

Standard
```

---

# 37. Enterprise新增Agent

新增：

```text
Construction Agent

Cost Agent

Risk Agent

Decision Agent
```

---

# 38. Enterprise新增搜索

实现：

```text
向量搜索

图谱搜索

混合搜索
```

---

# 39. Enterprise成功标准

达到：

```text
企业知识统一入口
```

---

并实现：

```text
经验传承

标准沉淀

组织学习
```

---

# 40. 功能优先级矩阵

P0：

```text
用户

项目

文件

会议

任务

问答
```

---

P1：

```text
Workflow

State Machine

Knowledge
```

---

P2：

```text
Graph

Agent协同

企业标准
```

---

P3：

```text
自动决策

预测分析

数字员工
```

---

# 41. 技术优先级矩阵

V1：

```text
FastAPI

PostgreSQL

Redis

MinIO

pgvector
```

---

V2：

```text
Neo4j

LangGraph
```

---

V3：

```text
Kafka

GraphRAG

Agent Cluster
```

---

# 42. 风险控制原则

禁止：

```text
先做复杂图谱
```

---

禁止：

```text
先做多Agent
```

---

禁止：

```text
先做自动决策
```

---

# 43. MVP核心原则

第一原则：

```text
先把资料存进去
```

---

第二原则：

```text
先把资料找出来
```

---

第三原则：

```text
先把会议记下来
```

---

第四原则：

```text
先把任务追起来
```

---

第五原则：

```text
先让大家愿意使用
```

---

# 44. 预算预估

MVP阶段：

```text
4~5人

2~3个月
```

---

Pilot阶段：

```text
6~8人

3~6个月
```

---

Enterprise阶段：

```text
10+人
```

---

# 45. 最终路线图

```text
MVP（3个月）

文件管理
会议管理
任务管理
RAG问答

↓

Pilot（6个月）

Workflow
Graph
Knowledge

↓

Enterprise（12个月+）

Agent协同
组织记忆
企业标准
数字大脑
```

---

# 46. 设计结论

团队大脑项目采用：

```text
MVP

↓

Pilot

↓

Enterprise
```

渐进式建设路线。

首个版本聚焦：

```text
项目

文件

会议

任务

知识检索
```

确保：

```text
8~12周上线

真实团队使用

持续沉淀知识
```

在此基础上逐步演化为：

```text
企业级数字大脑平台
```
