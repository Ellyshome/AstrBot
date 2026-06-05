# 06-Agent架构设计.md

> 团队大脑 Agent 系统
>
> 文档版本：V1.0
>
> 最后更新：2026-06
>
> 状态：架构基线文档

---

# 1. 文档目标

本文档定义团队大脑系统中的 Agent 架构。

主要解决：

* Agent职责划分
* Agent协作机制
* Agent与业务关系
* Agent与工作流关系
* Agent与知识库关系

---

# 2. 设计原则

系统采用：

```text
Event Driven Agent
```

架构。

即：

```text
事件驱动Agent
```

而非：

```text
聊天驱动Agent
```

---

# 3. Agent定位

Agent不是虚拟员工。

Agent本质上是：

```text
业务处理器
```

---

例如：

上传施工图。

Agent不会思考人生。

而是：

```text
识别事件

生成任务

通知相关人员

更新知识库
```

---

# 4. Agent总体架构

```text
                用户

                  │

                  ▼

            Router Agent

                  │

      ┌───────────┼───────────┐

      ▼           ▼           ▼

 Business     Archive      Query

  Agent        Agent       Agent

      │           │           │

      └───────────┼───────────┘

                  ▼

            Manager Agent
```

---

# 5. Agent分类

系统定义五类核心Agent。

```text
Router Agent

Business Agent

Archive Agent

Query Agent

Manager Agent
```

---

# 6. Router Agent

## 定位

系统入口。

---

职责：

```text
识别用户意图

识别事件类型

选择处理Agent
```

---

例如：

用户说：

```text
施工图已经上传
```

---

Router识别：

```text
FileEvent

drawing_upload
```

---

转发：

```text
Design Agent
```

---

# 7. Business Agent

## 定位

业务处理中心。

---

职责：

```text
处理业务事件

执行业务规则

创建任务

更新业务状态
```

---

Business Agent是一个集合。

---

# 8. Design Agent

负责：

```text
设计管理
```

---

处理：

```text
设计任务

图纸审核

设计变更

设计问题
```

---

# 9. Construction Agent

负责：

```text
施工管理
```

---

处理：

```text
材料进场

验收

整改

质量问题
```

---

# 10. Cost Agent

负责：

```text
成本管理
```

---

处理：

```text
付款申请

签证变更

成本统计
```

---

# 11. Approval Agent

负责：

```text
审批流程
```

---

处理：

```text
报建

付款

变更审批
```

---

# 12. Meeting Agent

负责：

```text
会议管理
```

---

处理：

```text
会议纪要

任务提取

责任分配
```

---

# 13. Archive Agent

## 定位

知识沉淀中心。

---

职责：

```text
归档资料

生成知识

沉淀案例

形成标准
```

---

例如：

项目完成。

---

Archive Agent：

```text
整理经验

生成案例

更新知识库
```

---

# 14. Query Agent

## 定位

统一查询入口。

---

职责：

```text
查询项目

查询任务

查询文件

查询知识
```

---

数据来源：

```text
PostgreSQL

Neo4j

Vector DB
```

---

统一返回结果。

---

# 15. Manager Agent

## 定位

Agent调度中心。

---

职责：

```text
监控Agent

统计Agent

处理异常
```

---

不参与具体业务。

---

# 16. Agent运行模式

系统采用：

```text
事件触发
```

模式。

---

不是：

```text
Agent主动聊天
```

模式。

---

例如：

```text
材料进场
```

触发：

```text
Construction Agent
```

---

例如：

```text
上传图纸
```

触发：

```text
Design Agent
```

---

# 17. Agent生命周期

```text
Receive Event

↓

Understand

↓

Plan

↓

Execute

↓

Record

↓

Finish
```

---

# 18. Agent标准输入

统一输入格式：

```yaml
event:
user:
project:
context:
attachments:
```

---

示例：

```yaml
event:
    drawing_upload

user:
    张三

project:
    未来城项目
```

---

# 19. Agent标准输出

统一输出：

```yaml
status:
tasks:
events:
knowledge:
messages:
```

---

例如：

```yaml
status:
    success

tasks:
    3

messages:
    图纸审核任务已创建
```

---

# 20. Agent与权限模型

Agent无独立权限。

---

原则：

```text
继承用户权限
```

---

例如：

张三可查看项目A。

Agent代张三执行：

允许。

---

张三无权限查看项目B。

Agent：

禁止访问。

````

---

# 21. Agent与知识图谱

Agent不直接推理全部数据。

---

Agent通过图谱导航。

---

例如：

查询：

```text
与施工图有关的全部问题
````

---

Agent执行：

```text
Project

↓

Event

↓

File

↓

Task

↓

Risk
```

遍历。

---

# 22. Agent与向量库

向量库只负责：

```text
找相似内容
```

---

例如：

```text
类似案例

类似问题

类似会议
```

---

最终决策仍由Agent完成。

---

# 23. Agent审计机制

所有Agent行为必须记录。

---

记录：

```yaml
agent:
user:
event:
action:
result:
time:
```

---

形成：

```text
Agent Log
```

---

# 24. Agent失败处理

统一机制：

```text
Retry

↓

Escalate

↓

Human
```

---

即：

重试

↓

升级

↓

人工处理

````

---

# 25. Agent扩展规范

新增Agent必须满足：

---

## 单一职责

例如：

```text
Design Agent
````

---

不要同时负责：

```text
设计

成本

审批
```

---

## 事件驱动

必须存在：

```text
event_type
```

触发。

---

## 可审计

必须生成：

```text
log
```

记录。

---

# 26. 推荐Agent体系

V1阶段：

```text
Router Agent

Meeting Agent

Design Agent

Construction Agent

Archive Agent

Query Agent
```

---

V2阶段：

```text
Approval Agent

Cost Agent

Risk Agent

Knowledge Agent
```

---

V3阶段：

```text
Process Agent

Planning Agent

Decision Agent
```

---

# 27. Agent与Workflow关系

重要原则：

```text
Workflow管理流程

Agent处理节点
```

---

即：

```text
Workflow
```

决定：

```text
下一步去哪
```

---

```text
Agent
```

决定：

```text
这一步怎么做
```

---

# 28. Agent与状态机关系

状态机负责：

```text
允许哪些状态变化
```

---

Agent负责：

```text
执行状态变化
```

---

例如：

```text
审核通过
```

---

状态机允许：

```text
reviewing

↓

approved
```

---

Agent执行：

```text
update_status()
```

---

# 29. 系统运行全景

```text
聊天消息

↓

Event

↓

Router Agent

↓

Business Agent

↓

Task/Event

↓

Workflow

↓

Knowledge

↓

Archive Agent

↓

企业大脑
```

---

# 30. 设计结论

团队大脑采用：

```text
Event Driven Agent
```

架构。

Agent本质不是聊天机器人。

而是：

```text
业务处理器
```

系统核心链路：

```text
Entity

↓

Event

↓

Agent

↓

Workflow

↓

Knowledge
```

最终形成：

```text
事件驱动

Agent执行

知识沉淀

持续演化
```

的企业数字大脑体系。
