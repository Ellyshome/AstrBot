# 03-RBAC权限模型.md

> 团队大脑 Agent 系统
>
> 文档版本：V1.0
>
> 最后更新：2026-06
>
> 状态：架构基线文档

---

# 1. 文档目标

本文档用于定义系统权限模型。

主要解决：

* 谁可以查看数据
* 谁可以修改数据
* 谁可以审批数据
* Agent是否有执行权限
* 跨项目权限如何控制

---

# 2. 设计原则

系统采用：

```text
RBAC + Project Scope + Agent Delegation
```

即：

```text
角色权限控制

+
项目范围控制

+
Agent代理控制
```

---

# 3. 为什么不能只用传统RBAC

传统RBAC：

```text
用户
 ↓
角色
 ↓
权限
```

例如：

```text
张三
 ↓
设计经理
 ↓
查看图纸
```

看似简单。

但项目制企业并不适用。

---

# 4. 项目制企业的特点

同一个人：

在不同项目中角色不同。

例如：

```text
张三
```

项目A：

```text
项目负责人
```

项目B：

```text
普通成员
```

项目C：

```text
无权限
```

因此必须引入：

```text
Project Role
```

---

# 5. 权限架构

整体模型：

```text
User

├─ Organization Role
│
├─ Project Role
│
└─ Agent Delegation
```

---

# 6. 权限组成

系统权限由三部分决定：

```text
最终权限

=

组织权限

+

项目权限

+

代理权限
```

---

# 7. 用户(User)

用户是权限主体。

---

核心属性：

```yaml
id:
name:
department:
status:
```

---

# 8. 组织角色(Organization Role)

表示员工在企业中的职位。

---

典型角色：

```text
系统管理员

总经理

设计总监

设计经理

工程经理

成本经理

普通员工
```

---

组织角色决定：

```text
能访问哪些模块
```

例如：

设计经理：

```text
查看设计资料

创建设计任务

查看项目进展
```

---

# 9. 项目角色(Project Role)

表示用户在某个项目中的身份。

---

典型角色：

```text
项目负责人

专业负责人

项目成员

观察者

外部单位
```

---

项目角色决定：

```text
能访问哪些项目数据
```

---

# 10. Agent代理角色

新增概念。

---

Agent不是用户。

但Agent可能代表用户执行动作。

因此定义：

```text
Delegated Role
```

---

例如：

会议Agent：

允许：

```text
创建会议纪要

整理任务

发送通知
```

---

禁止：

```text
审批付款

删除合同

关闭项目
```

---

# 11. 权限对象(Resource)

权限控制对象统一称：

```text
Resource
```

---

包括：

```text
Project

Task

Event

File

Workflow

Knowledge
```

---

# 12. 权限动作(Action)

统一动作定义：

```text
create

read

update

delete

approve

execute

assign
```

---

解释：

| 动作      | 说明 |
| ------- | -- |
| create  | 创建 |
| read    | 查看 |
| update  | 修改 |
| delete  | 删除 |
| approve | 审批 |
| execute | 执行 |
| assign  | 分派 |

---

# 13. 权限表达方式

采用：

```text
Resource:Action
```

格式。

例如：

```text
project:read

project:update

task:create

task:assign

file:read

file:upload
```

---

# 14. 权限层级

系统权限分四级。

---

## Level 1

公开

```text
Public
```

---

所有登录用户可访问。

---

## Level 2

项目级

```text
Project
```

---

仅项目成员可访问。

---

## Level 3

部门级

```text
Department
```

---

仅部门成员可访问。

---

## Level 4

系统级

```text
System
```

---

仅管理员可访问。

---

# 15. 文件权限模型

文件权限最复杂。

---

文件继承项目权限。

例如：

```text
未来城项目

↓

施工图
```

默认：

```text
项目成员可查看
```

---

特殊文件：

```text
合同

付款资料
```

允许额外限制。

---

# 16. Event权限模型

原则：

```text
事件跟随项目
```

---

例如：

```text
项目A事件
```

只能由：

```text
项目A成员
```

查看。

---

# 17. Task权限模型

任务具有：

```text
负责人

参与人

创建人
```

三种关系。

---

默认：

负责人：

```text
可修改
```

---

参与人：

```text
可查看
```

---

创建人：

```text
可跟踪
```

---

# 18. 知识库权限模型

知识库分级。

---

公开知识：

```text
企业制度

设计标准
```

---

项目知识：

```text
项目案例

经验总结
```

---

受限知识：

```text
合同

商业机密
```

---

# 19. Agent权限模型

Agent不拥有权限。

---

原则：

```text
Agent只能继承用户权限
```

---

例如：

张三可查看项目A。

Agent代张三执行：

允许。

---

张三无权限查看项目B。

Agent代张三执行：

禁止。

---

# 20. Agent执行审计

所有Agent动作必须记录。

---

记录：

```yaml
user:
agent:
resource:
action:
time:
result:
```

---

示例：

```yaml
user: 张三

agent: MeetingAgent

action: create_task

time: 2026-06-01
```

---

# 21. 特权操作

以下操作必须人工确认：

```text
删除项目

删除文件

关闭项目

审批付款

合同归档

权限变更
```

---

禁止Agent自动执行。

---

# 22. 权限继承规则

项目成员自动继承：

```text
项目

↓

任务

↓

事件

↓

文件
```

权限。

---

即：

```text
Project

↓

Task

↓

Event

↓

File
```

---

逐层继承。

---

# 23. 权限冲突处理

原则：

```text
拒绝优先
```

例如：

组织角色允许。

项目角色禁止。

最终：

```text
禁止
```

---

# 24. Neo4j权限关系

推荐建模：

```text
(User)

↓

HAS_ROLE

↓

(Role)

↓

CAN

↓

(Resource)
```

---

项目关系：

```text
(User)

↓

MEMBER_OF

↓

(Project)
```

---

# 25. PostgreSQL表建议

```text
user

role

permission

user_role

project_member

agent_delegation

audit_log
```

---

# 26. 设计结论

系统采用：

```text
RBAC

+

Project Scope

+

Agent Delegation
```

三层权限模型。

实现目标：

1. 企业组织权限控制
2. 项目权限隔离
3. Agent安全代理执行
4. 全过程审计追踪

保证团队大脑在多人协作环境下可安全运行。
