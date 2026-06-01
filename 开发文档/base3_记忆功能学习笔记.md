# base3.py 学习笔记：LangGraph 记忆功能与 Checkpointer

对应代码文件：[base3.py](base3.py)

## 一、整体作用

[base3.py](base3.py) 在工具调用 Agent 的基础上，进一步加入了 LangGraph 的记忆能力。

它主要演示：

1. 使用 `init_chat_model()` 初始化 DeepSeek 模型；
2. 使用 `TavilySearch` 作为搜索工具；
3. 使用 `llm.bind_tools(tools)` 让模型具备工具调用能力；
4. 使用 `StateGraph` 构建带工具节点的 LangGraph 图；
5. 使用 `MemorySaver` 作为检查点保存器；
6. 编译图时传入 `checkpointer=memory`；
7. 通过 `thread_id` 区分不同对话线程；
8. 验证同一线程能够记住历史，不同线程之间互相隔离。

核心流程可以概括为：

```text
用户输入 + thread_id
  ↓
LangGraph 根据 thread_id 加载历史状态
  ↓
chatbot 节点调用带工具能力的 LLM
  ↓
必要时进入 tools 节点执行工具
  ↓
回到 chatbot 生成回答
  ↓
LangGraph 把新状态保存到该 thread_id 对应的检查点
```

---

## 二、文件开头说明

相关代码：[base3.py:1-5](base3.py#L1-L5)

```python
"""LangGraph 教程: 添加记忆功能的聊天机器人

本示例展示了如何使用 LangGraph 的检查点功能为聊天机器人添加记忆功能，
使其能够记住对话历史并在多轮对话中保持上下文。
"""
```

这段文档字符串已经说明了 base3 的主题：

> 使用 LangGraph 的检查点功能，为聊天机器人添加记忆。

这里的“记忆”不是模型本身永久学会了什么，而是 LangGraph 在运行图时保存了对话状态，下次用同一个 `thread_id` 调用时可以恢复之前的状态。

---

## 三、关键导入

相关代码：[base3.py:7-18](base3.py#L7-L18)

```python
from typing import Annotated

from langchain.chat_models import init_chat_model
from langchain_tavily import TavilySearch
from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict

# 导入 MemorySaver 用于实现记忆功能
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
```

### 重点模块

| 模块 | 作用 |
|---|---|
| `init_chat_model` | 初始化聊天模型 |
| `TavilySearch` | Tavily 搜索工具 |
| `MemorySaver` | 内存检查点保存器，用于保存图状态 |
| `StateGraph` | 构建状态图 |
| `add_messages` | 合并消息列表 |
| `ToolNode` | 执行工具调用的预置节点 |
| `tools_condition` | 判断是否需要进入工具节点 |

### 备注

[base3.py:11](base3.py#L11) 导入了 `BaseMessage`，但当前代码没有实际使用。

如果想让类型更明确，可以把状态写成：

```python
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
```

---

## 四、环境变量加载

相关代码：[base3.py:20-24](base3.py#L20-L24)

```python
import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()
```

这部分负责加载 `.env` 文件中的环境变量。

当前代码至少需要：

```env
DEEPSEEK_API_KEY=你的_deepseek_key
```

如果 Tavily 工具需要联网搜索，通常还需要：

```env
TAVILY_API_KEY=你的_tavily_key
```

---

## 五、状态定义：`State` 与消息合并

相关代码：[base3.py:26-28](base3.py#L26-L28)

```python
# 定义状态类型，使用 add_messages 注解来自动合并消息列表
class State(TypedDict):
    messages: Annotated[list, add_messages]  # 消息列表将使用 add_messages reducer 自动合并
```

`State` 定义了图的状态结构。

这里只有一个字段：

```python
messages
```

它保存对话消息列表。

`Annotated[list, add_messages]` 表示：

```text
messages 是一个列表，并且更新时使用 add_messages 规则追加合并
```

这对记忆功能很关键，因为如果消息每次都被覆盖，就无法保留对话历史。

---

## 六、初始化 DeepSeek 模型

相关代码：[base3.py:31-35](base3.py#L31-L35)

```python
# 初始化 DeepSeek 聊天模型
llm = init_chat_model(
    "deepseek-chat",  # 使用DeepSeek模型
    api_key=os.environ.get("DEEPSEEK_API_KEY")  # 从环境变量中获取API密钥
)
```

这部分创建聊天模型对象。

后面不会直接使用 `llm` 调用，而是先绑定工具：

```python
llm_with_tools = llm.bind_tools(tools)
```

---

## 七、创建状态图

相关代码：[base3.py:37-38](base3.py#L37-L38)

```python
# 创建状态图构建器
graph_builder = StateGraph(State)
```

`StateGraph(State)` 创建一个状态图构建器。

后续会往里面添加：

- `chatbot` 节点；
- `tools` 节点；
- 条件边；
- 普通边；
- 入口点。

---

## 八、初始化 Tavily 搜索工具

相关代码：[base3.py:40-43](base3.py#L40-L43)

```python
# 初始化Tavily搜索工具
print("\n初始化Tavily搜索工具...")
tool = TavilySearch(max_results=2)  # 设置最多返回2个搜索结果
tools = [tool]
```

`TavilySearch(max_results=2)` 表示创建一个 Tavily 搜索工具，每次最多返回 2 条搜索结果。

这个工具让模型可以查询实时外部信息。

但要注意：

- 搜索工具通常需要 `TAVILY_API_KEY`；
- 工具调用会消耗外部服务额度；
- 搜索结果需要模型进一步整理，不能直接等同于最终答案。

---

## 九、绑定工具到 LLM

相关代码：[base3.py:45-46](base3.py#L45-L46)

```python
# 将工具绑定到LLM
llm_with_tools = llm.bind_tools(tools)
```

`bind_tools()` 的作用是把工具描述提供给模型，让模型知道自己可以调用哪些工具。

注意职责区分：

```text
llm_with_tools：决定是否调用工具，并生成 tool call
ToolNode：真正执行工具
```

绑定工具后，模型在遇到需要实时信息的问题时，可以生成工具调用请求。

---

## 十、`chatbot` 节点

相关代码：[base3.py:48-51](base3.py#L48-L51)

```python
# 定义聊天机器人节点函数
def chatbot(state: State):
    """LLM节点函数，处理用户输入并生成响应"""
    return {"messages": [llm_with_tools.invoke(state["messages"])]}
```

这个节点负责调用带工具能力的模型。

它接收当前状态：

```python
state["messages"]
```

然后返回新的模型消息：

```python
{"messages": [AIMessage(...)]}
```

因为 `messages` 使用了 `add_messages`，所以这条新消息会被追加到历史消息中。

---

## 十一、添加节点

相关代码：[base3.py:53-58](base3.py#L53-L58)

```python
# 添加聊天机器人节点
graph_builder.add_node("chatbot", chatbot)

# 添加工具节点
tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)
```

当前图有两个节点：

| 节点名 | 作用 |
|---|---|
| `chatbot` | 调用带工具能力的 LLM |
| `tools` | 执行模型请求的工具调用 |

---

## 十二、添加条件边和普通边

相关代码：[base3.py:60-67](base3.py#L60-L67)

```python
# 添加条件边
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
# 工具调用完成后，返回到聊天机器人节点
graph_builder.add_edge("tools", "chatbot")
graph_builder.set_entry_point("chatbot")
```

### 1. 条件边

```python
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
```

表示从 `chatbot` 节点出来后，根据 `tools_condition` 判断下一步：

- 如果最后一条 AI 消息包含工具调用，则进入 `tools`；
- 如果没有工具调用，则结束。

### 2. 工具执行后返回模型

```python
graph_builder.add_edge("tools", "chatbot")
```

表示工具执行完成后回到 `chatbot`。

这样模型可以读取工具结果，并生成最终自然语言回答。

### 3. 设置入口点

```python
graph_builder.set_entry_point("chatbot")
```

表示图从 `chatbot` 节点开始执行。

---

## 十三、`MemorySaver`：内存检查点保存器

相关代码：[base3.py:69-77](base3.py#L69-L77)

```python
print("\n构建图并添加记忆功能...")

# 创建内存保存器
print("\n创建 MemorySaver 实例作为检查点保存器...")
memory = MemorySaver()  # 在内存中保存状态，适用于开发和测试

# 使用内存保存器编译图
print("使用检查点保存器编译图...")
graph = graph_builder.compile(checkpointer=memory)  # 将内存保存器传递给图
```

这是 base3 最核心的新增内容。

### 1. `MemorySaver` 是什么？

`MemorySaver` 是 LangGraph 提供的一个检查点保存器。

它会把图运行过程中的状态保存到内存中。

当你再次用相同的 `thread_id` 调用图时，LangGraph 可以恢复这个线程之前的状态。

### 2. `compile(checkpointer=memory)` 的作用

```python
graph = graph_builder.compile(checkpointer=memory)
```

这表示编译图时启用检查点机制。

没有传入 checkpointer 时，每次调用通常都是独立执行；传入 checkpointer 后，LangGraph 可以保存和恢复状态。

### 3. MemorySaver 的适用场景

`MemorySaver` 把数据保存在当前 Python 进程内存中，因此适合：

- 教程；
- 本地实验；
- 单进程调试；
- 临时会话。

不适合：

- 生产环境长期记忆；
- 服务重启后仍要保留历史；
- 多实例共享会话；
- 大规模用户会话管理。

生产环境更可能需要 SQLite、Postgres、Redis 等持久化 checkpointer。

---

## 十四、打印图结构

相关代码：[base3.py:79-81](base3.py#L79-L81)

```python
# 打印图结构
print("\n图结构如下：")
print(graph.get_graph().draw_mermaid())
```

`draw_mermaid()` 会输出 Mermaid 格式的图结构。

当前图大致是：

```text
chatbot
  ├─ 需要工具 → tools → chatbot
  └─ 不需要工具 → END
```

打印图结构有助于理解 LangGraph 的执行路线。

---

## 十五、`thread_id`：区分对话线程

相关代码：[base3.py:83-85](base3.py#L83-L85)

```python
# 定义对话线程ID
print("\n设置对话线程 ID = '1'...")
config = {"configurable": {"thread_id": "1"}}  # 使用线程ID来标识和区分不同的对话
```

### 1. `thread_id` 是什么？

`thread_id` 是 LangGraph 用来区分不同对话线程的标识。

可以理解为：

```text
thread_id = 某个会话的唯一 ID
```

同一个 `thread_id` 下的调用会共享历史状态。

不同 `thread_id` 之间相互隔离。

### 2. 为什么要放在 `configurable` 里面？

LangGraph 的运行配置通常通过 `config` 参数传入。

其中可配置项放在：

```python
{"configurable": {...}}
```

所以 thread_id 写成：

```python
{"configurable": {"thread_id": "1"}}
```

### 3. 一个实用类比

可以把 `thread_id` 理解为聊天软件中的会话 ID：

```text
用户 A 的会话：thread_id = "user-a-session"
用户 B 的会话：thread_id = "user-b-session"
```

只要每个用户或每个会话使用不同 `thread_id`，历史就不会混在一起。

---

## 十六、示例 1：第一次对话，写入记忆

相关代码：[base3.py:87-103](base3.py#L87-L103)

```python
# 示例 1: 第一次对话
print("\n示例 1: 第一次对话 - 用户介绍自己")
user_input = "Hi there! My name is Will."
print(f"\n用户输入: '{user_input}'")

# 注意: config 是 stream() 函数的第二个参数!
print("使用线程 ID '1' 调用图...")
events = graph.stream(
    {"messages": [{"role": "user", "content": user_input}]},
    config,  # 传递包含 thread_id 的配置
    stream_mode="values",
)

print("\n助理回应:")
for event in events:
    event["messages"][-1].pretty_print()  # 打印助理的回应
```

这一段使用 `thread_id = "1"` 发起第一次对话：

```text
Hi there! My name is Will.
```

因为编译图时启用了 checkpointer，所以这次对话结束后，消息历史会保存到线程 `1` 中。

---

## 十七、`graph.stream(input, config, stream_mode="values")`

相关代码：[base3.py:94-98](base3.py#L94-L98)

```python
events = graph.stream(
    {"messages": [{"role": "user", "content": user_input}]},
    config,
    stream_mode="values",
)
```

这里有三个重要参数。

### 1. 第一个参数：输入状态

```python
{"messages": [{"role": "user", "content": user_input}]}
```

表示本轮新增的用户消息。

### 2. 第二个参数：运行配置

```python
config
```

这里包含：

```python
{"configurable": {"thread_id": "1"}}
```

这个参数决定本次调用属于哪个对话线程。

### 3. `stream_mode="values"`

`stream_mode="values"` 表示流式输出每一步后的完整状态值。

因此循环中可以直接访问：

```python
event["messages"][-1]
```

而在 base2 中没有指定 `stream_mode="values"`，默认事件结构通常更偏向节点输出，例如：

```python
{"chatbot": {...}}
```

这也是 base3 的打印方式与 base2 不同的原因。

---

## 十八、`pretty_print()`

相关代码：[base3.py:101-102](base3.py#L101-L102)

```python
for event in events:
    event["messages"][-1].pretty_print()  # 打印助理的回应
```

`pretty_print()` 是 LangChain 消息对象提供的格式化打印方法。

相比：

```python
print(event["messages"][-1].content)
```

`pretty_print()` 通常能更清楚地显示消息类型和内容。

不过如果最后一条消息是工具调用或工具结果，它也可能打印出中间过程。因此学习时可以观察完整 `event` 来理解状态变化。

---

## 十九、示例 2：使用相同线程测试记忆

相关代码：[base3.py:104-119](base3.py#L104-L119)

```python
# 示例 2: 测试记忆功能
print("\n\n示例 2: 第二次对话 - 测试记忆功能")
user_input = "Remember my name?"
print(f"\n用户输入: '{user_input}'")

# 使用相同的线程ID再次调用图
print("使用相同的线程 ID '1' 再次调用图...")
events = graph.stream(
    {"messages": [{"role": "user", "content": user_input}]},
    config,  # 使用相同的配置，图将加载之前保存的状态
    stream_mode="values",
)

print("\n助理回应 (应该记得用户名字):")
for event in events:
    event["messages"][-1].pretty_print()
```

这次仍然使用同一个：

```python
thread_id = "1"
```

因此 LangGraph 会加载线程 `1` 之前保存的历史。

用户问：

```text
Remember my name?
```

模型应该能够根据历史回答用户名字是 Will。

这说明：

```text
同一个 thread_id 可以保留上下文
```

---

## 二十、示例 3：新线程测试隔离

相关代码：[base3.py:121-135](base3.py#L121-L135)

```python
# 示例 3: 新对话线程
print("\n\n示例 3: 新对话线程 - 测试线程隔离")
print("创建新的线程 ID = '2'...")

# 使用不同的线程ID
print("使用新的线程 ID '2' 调用图...")
events = graph.stream(
    {"messages": [{"role": "user", "content": user_input}]},
    {"configurable": {"thread_id": "2"}},  # 使用新的线程ID
    stream_mode="values",
)

print("\n助理回应 (不应该记得用户名字):")
for event in events:
    event["messages"][-1].pretty_print()
```

这里切换到了新的线程：

```python
{"configurable": {"thread_id": "2"}}
```

线程 `2` 之前没有收到过：

```text
My name is Will.
```

所以当用户问：

```text
Remember my name?
```

模型不应该知道用户名字。

这说明：

```text
不同 thread_id 之间状态隔离
```

---

## 二十一、示例 4：回到第一个线程验证持久性

相关代码：[base3.py:137-151](base3.py#L137-L151)

```python
# 示例 4: 返回第一个线程
print("\n\n示例 4: 返回第一个线程 - 验证记忆持久性")
print(f"\n用户输入: '{user_input}'")

# 再次使用第一个线程ID
print("再次使用线程 ID '1' 调用图...")
events = graph.stream(
    {"messages": [{"role": "user", "content": user_input}]},
    config,  # 使用原始线程ID
    stream_mode="values",
)

print("\n助理回应 (应该仍然记得用户名字):")
for event in events:
    event["messages"][-1].pretty_print()
```

这次又回到：

```python
thread_id = "1"
```

如果记忆功能正常，模型应该仍然能记得之前用户说过：

```text
My name is Will.
```

这验证了同一线程中的状态可以持续保留。

---

## 二十二、base3 相比 base2 的新增重点

| 对比项 | base2.py | base3.py |
|---|---|---|
| 工具调用 | 有 | 有 |
| Tavily 搜索 | 有 | 有 |
| `ToolNode` | 有 | 有 |
| `tools_condition` | 有 | 有 |
| 检查点保存器 | 无 | 有 `MemorySaver` |
| 编译图 | `compile()` | `compile(checkpointer=memory)` |
| 对话线程 | 无 | 有 `thread_id` |
| 多轮记忆 | 无显式记忆 | 有，同一线程可恢复历史 |
| 线程隔离 | 无 | 有，不同 `thread_id` 隔离 |
| 示例形式 | 命令行循环 | 固定四段演示 |

---

## 二十三、`MemorySaver`、`thread_id`、`add_messages` 的关系

这三个概念经常一起出现，但职责不同。

### 1. `add_messages`

负责“如何合并消息”：

```text
新消息追加到旧消息后面
```

### 2. `MemorySaver`

负责“把状态保存在哪里”：

```text
保存在当前 Python 进程内存中
```

### 3. `thread_id`

负责“保存到哪个会话”：

```text
thread_id = "1" 的历史和 thread_id = "2" 的历史分开保存
```

三者合起来才构成多轮记忆：

```text
add_messages 负责累积消息
MemorySaver 负责保存状态
thread_id 负责区分会话
```

---

## 二十四、重要心智模型

可以把 base3 的记忆机制理解为：

```text
每次调用 graph.stream 时：

1. 读取 config 中的 thread_id；
2. 根据 thread_id 查找之前保存的状态；
3. 把本轮新输入合并进 messages；
4. 执行图中的节点；
5. 把执行后的新状态保存回这个 thread_id；
6. 下次同 thread_id 调用时继续使用这份状态。
```

如果没有传 `thread_id`，或者每次传不同的 `thread_id`，就无法表现出同一个会话的记忆效果。

---

## 二十五、需要注意的问题

### 1. `MemorySaver` 不是永久存储

`MemorySaver` 保存在内存中。

程序一旦退出，记忆就会丢失。

如果需要长期保存，可以学习 LangGraph 的持久化 checkpointer，例如：

- SQLite checkpointer；
- Postgres checkpointer；
- Redis 或自定义存储；
- 业务数据库存储消息历史。

### 2. 记忆内容会越来越长

如果每轮对话都保存在 `messages` 中，历史会越来越长。

可能带来：

- token 成本升高；
- 响应变慢；
- 超过模型上下文窗口；
- 旧信息干扰新回答。

后续可以学习：

- 对话摘要；
- 滑动窗口记忆；
- 长期记忆和短期记忆分离；
- 向量数据库检索历史。

### 3. 线程 ID 应该由业务系统生成

示例中写死：

```python
thread_id = "1"
```

真实项目中通常应该用：

- 用户 ID；
- 会话 ID；
- 群聊 ID；
- 任务 ID；
- UUID。

例如：

```python
config = {"configurable": {"thread_id": f"user-{user_id}-session-{session_id}"}}
```

### 4. 工具调用和记忆是两个独立能力

base3 同时包含工具调用和记忆，但它们不是一回事。

```text
工具调用：让模型能访问外部工具
记忆功能：让图能保存并恢复状态
```

可以只使用工具不使用记忆，也可以只使用记忆不使用工具。

---

## 二十六、建议延伸学习

### 1. 持久化 Checkpointer

继续学习如何把 checkpointer 从内存换成持久化存储。

重点关注：

```text
SQLiteSaver
PostgresSaver
checkpointer
checkpoint namespace
```

### 2. 多用户会话设计

思考如何在真实应用中设计：

```text
user_id
session_id
thread_id
conversation_id
```

以及它们之间的关系。

### 3. 消息裁剪与摘要

当消息历史变长时，需要学习：

- 只保留最近 N 轮；
- 对旧消息做摘要；
- 把长期信息提取成结构化记忆；
- 结合 RAG 检索历史。

### 4. `stream_mode` 的不同模式

base3 使用：

```python
stream_mode="values"
```

可以继续了解其他模式，例如：

- 节点更新；
- 完整状态；
- token 流式输出；
- debug 模式。

### 5. 工具调用错误处理

真实项目中需要处理：

- 搜索工具超时；
- API Key 缺失；
- 工具参数错误；
- 工具返回空结果；
- 模型反复调用工具导致循环。

---

## 二十七、推荐实践改造

如果把 base3 改成交互式聊天，可以保留同一个 `config`：

```python
config = {"configurable": {"thread_id": "1"}}

while True:
    user_input = input("User: ")
    if user_input.lower() in ["quit", "exit", "q"]:
        break

    events = graph.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        config,
        stream_mode="values",
    )

    for event in events:
        event["messages"][-1].pretty_print()
```

这样就可以在命令行中体验同一线程的连续记忆。

---

## 二十八、一句话总结

[base3.py](base3.py) 的核心是：

> 在 LangGraph 工具调用 Agent 的基础上，通过 `MemorySaver` 和 `thread_id` 启用检查点机制，让同一个对话线程能够保存并恢复消息历史，从而实现多轮记忆与线程隔离。
