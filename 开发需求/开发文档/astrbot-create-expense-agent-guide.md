# AstrBot 创建"报销"子 Agent 完整指南

AstrBot 支持两种方式创建子 Agent：
1. **纯配置方式**：在 `cmd_config.json` 的 `subagent_orchestrator.agents` 中添加条目，无需写代码
2. **Star 插件方式**：用 `@register_agent` 装饰器创建带自定义工具的插件

"报销"场景需要：查询报销政策、提交报销单、查询报销进度。纯配置方式只能复用已有工具，如果要有专门的"提交报销"工具则需要插件方式。

---

## 方案一：纯配置方式（最简单）

无需写代码，直接在配置中添加子 Agent 定义。

### 步骤

1. **开启主开关**：在 `cmd_config.json` 中设置 `subagent_orchestrator.main_enable = true`

2. **添加子 Agent 条目**：

```json
{
  "subagent_orchestrator": {
    "main_enable": true,
    "router_system_prompt": "你是任务路由助手...",
    "agents": [
      {
        "name": "报销助手",
        "enabled": true,
        "system_prompt": "你是公司报销助手。你了解公司的报销政策和流程。请用中文回复用户的报销相关问题...",
        "public_description": "处理报销相关的咨询，包括报销政策、流程、材料等",
        "tools": ["astr_kb_search", "send_message_to_user"],
        "provider_id": null
      }
    ]
  }
}
```

3. **如果使用知识库**：可通过 WebUI 上传报销政策文档到知识库，子 Agent 通过 `astr_kb_search` 工具查询。

### 关键配置字段

| 字段 | 说明 |
|------|------|
| `name` | 生成 `transfer_to_报销助手` 工具 |
| `system_prompt` | 子 Agent 的行为指令（角色、规则、约束） |
| `public_description` | 主 Agent 看到的工具描述，决定何时路由到此子 Agent |
| `tools` | 子 Agent 可用的工具名列表；`null` = 全部工具 |
| `persona_id` | 可选，绑定已有 Persona 到此子 Agent |
| `provider_id` | 可选，为子 Agent 指定不同的 LLM 模型 |

### 优点 / 缺点

- **优点**：零代码，WebUI 可配置，即时生效
- **缺点**：能用的工具只有已有工具，无法添加自定义报销提交逻辑

---

## 方案二：Star 插件方式（带自定义工具）

当需要"提交报销"这类要写入数据库/调 API 的操作时，需要用插件创建自定义工具。

### 目录结构

```
data/plugins/expense_agent/
├── metadata.yaml         # 插件元信息
├── requirements.txt      # 可选：第三方依赖
└── main.py               # 插件主文件
```

### Step 1: 创建 `metadata.yaml`

```yaml
name: expense_agent
desc: 报销助手插件，提供报销咨询和提交功能
author: your-name
version: 0.1.0
support_platforms: []
```

### Step 2: 创建 `main.py` — 定义插件类和子 Agent

文件结构如下：

```python
from astrbot.api.event import AstrMessageEvent
from astrbot.api.star import Star, Context, register_agent
from astrbot.core import logger
import json
import os

# ---- 1. 子 Agent 定义 ----

@register_agent(
    name="报销助手",
    instruction=(
        "你是公司的报销助手，帮助员工处理报销相关事务。\n\n"
        "## 你的能力\n"
        "- 回答报销政策、流程、材料等常见问题\n"
        "- 帮助员工提交报销申请\n"
        "- 查询报销进度\n\n"
        "## 规则\n"
        "- 始终使用中文回复\n"
        "- 提交报销前必须确认金额和事由\n"
        "- 单笔金额超过 5000 元时提醒需要额外审批\n"
    ),
)
async def expense_agent(event: AstrMessageEvent):
    pass  # 占位函数，主要配置在装饰器参数中
```

### Step 3: 注册自定义工具

在 `@register_agent` 返回的对象上注册专用工具：

```python
# ---- 2. 自定义工具 ----

@expense_agent.llm_tool(name="submit_expense")
async def submit_expense(
    event: AstrMessageEvent,
    amount: float,
    category: str,
    description: str,
    date: str = ""
):
    """提交一条新的报销申请。

    Args:
        amount(number): 报销金额（人民币元）
        category(string): 费用类别，如 差旅、办公用品、招待、其他
        description(string): 费用说明
        date(string): 费用发生日期，格式 YYYY-MM-DD，不填默认为今天
    """
    # TODO: 接入实际的报销系统 API
    expense_data = {
        "amount": amount,
        "category": category,
        "description": description,
        "date": date,
        "user_id": event.message_obj.sender.user_id,
        "status": "已提交",
    }
    logger.info(f"新报销申请: {expense_data}")
    return f"报销申请已提交成功！金额: ¥{amount}, 类别: {category}, 说明: {description}。请保留原始票据等待审核。"


@expense_agent.llm_tool(name="query_expense_policy")
async def query_expense_policy(event: AstrMessageEvent, question: str):
    """查询公司报销政策和规定。

    用于回答各类报销政策问题，如差旅标准、可报销类目、审批流程等。

    Args:
        question(string): 要查询的政策问题
    """
    # TODO: 接入公司政策知识库或 API
    policies = {
        "差旅": "出差住宿不超过 ¥400/晚，交通可报销高铁二等座或经济舱机票。餐补 ¥100/天。",
        "办公": "办公用品单件不超过 ¥500 无需审批，超过需部门主管签字。",
        "招待": "招待费需提前申请，人均不超过 ¥200。需提供参与者名单。",
    }
    for keyword, policy in policies.items():
        if keyword in question:
            return f"关于「{keyword}」的公司政策：{policy}"
    return "未找到相关政策，建议咨询财务部门获取最新政策。"


@expense_agent.llm_tool(name="check_expense_status")
async def check_expense_status(event: AstrMessageEvent):
    """查询当前用户的报销申请状态。"""
    # TODO: 从数据库查询实际状态
    return (
        "你的最近报销记录：\n"
        "1. 2024-03-15 差旅费 ¥3200 — 已审核通过\n"
        "2. 2024-03-10 办公用品 ¥150 — 待审核\n"
    )
```

### Step 4: 定义 Star 插件类（对外入口）

```python
# ---- 3. 插件主体 ----

class Main(Star):
    def __init__(self, context: Context) -> None:
        self.context = context

    async def initialize(self) -> None:
        logger.info("报销助手插件已加载")
```

### 工具装饰器规范

`@register_agent.llm_tool()` 通过解析函数 docstring 自动生成 JSON Schema：

- **函数名** → 工具名
- **`Args:` 部分** → parameter 定义（参数名、类型、描述）
- **docstring 第一行** → 工具描述
- **参数类型映射**：`int`→`integer`，`float`→`number`，`str`→`string`，`bool`→`boolean`

### 触发流程

```
用户: "帮我报销一笔500元的办公用品"
  ↓
Pipeline → ProcessStage → build_main_agent()
  ↓
主 Agent (LLM) 看到工具: transfer_to_报销助手
  ↓
主 Agent 调用 transfer_to_报销助手(input="用户要报销500元办公用品")
  ↓
FunctionToolExecutor._execute_handoff()
  ↓
子 Agent (报销助手) 的 LLM 看到一个系统指令 + 两个工具:
  - submit_expense
  - check_expense_status
  ↓
子 Agent 调用 submit_expense(amount=500, category="办公", description="...")
  ↓
工具返回结果 → 子 Agent 整理回复 → 返回给主 Agent → 回复用户
```

---

## 两个方案对比

| 维度 | 方案一：纯配置 | 方案二：Star 插件 |
|------|--------------|------------------|
| 需要写代码 | 否 | 是 |
| 自定义工具 | 不可 | 可以（`@llm_tool`） |
| 配置方式 | WebUI / JSON | metadata.yaml + 代码 |
| 接入外部系统 | 否 | 可以（调 API、写 DB） |
| 部署方式 | 即时生效 | 需要安装/重载插件 |
| 适用场景 | 纯咨询类（用已有工具） | 需提交/查询等操作 |

---

## 涉及的源文件

| 文件 | 用途 |
|------|------|
| `AstrBot/astrbot/core/config/default.py:197-206` | subagent_orchestrator 配置 schema |
| `AstrBot/astrbot/core/subagent_orchestrator.py` | 子 Agent 编排器 |
| `AstrBot/astrbot/core/star/register/star_handler.py:580` | `@register_llm_tool` 装饰器 |
| `AstrBot/astrbot/core/star/register/star_handler.py:691` | `@register_agent` 装饰器 |
| `AstrBot/astrbot/core/agent/handoff.py` | HandoffTool 实现 |
| `AstrBot/astrbot/core/agent/agent.py` | Agent 数据类 |
| `AstrBot/astrbot/core/astr_main_agent.py:494-554` | 子 Agent 集成到主 Agent 的逻辑 |
| `AstrBot/astrbot/dashboard/routes/subagent.py` | 子 Agent 配置 API |

---

## 验证方式

1. **方案一**：在 WebUI 配置页面添加子 Agent → 发送报销相关问题 → 观察主 Agent 是否调用 `transfer_to_报销助手`
2. **方案二**：安装插件后重载 → 同样发送报销问题 → 验证子 Agent 是否调用自定义工具（如 `submit_expense`）
3. 查看日志确认 Handoff 执行路径：`Agent 使用工具: transfer_to_报销助手` → `Agent 使用工具: submit_expense`

---

## 推荐路径

先用**方案一**快速验证路由效果，如果只是报销政策咨询（配合知识库）就足够了。

如果需要接入实际报销系统（写入数据库/调 API），则在方案一基础上追加**方案二**的自定义工具注册部分。
