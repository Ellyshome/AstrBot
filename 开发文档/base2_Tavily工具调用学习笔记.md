# base2.py 学习笔记：LangGraph 工具调用与条件边

对应代码文件：[base2.py](base2.py)

## 一、整体作用

[base2.py](base2.py) 在 [base1.py](base1.py) 的基础上增加了“工具调用”能力：

1. 使用 `init_chat_model()` 初始化 DeepSeek 聊天模型；
2. 使用 `TavilySearch` 创建搜索工具；
3. 通过 `llm.bind_tools(tools)` 把工具绑定到模型；
4. 使用 `StateGraph` 构建图；
5. 添加 `chatbot` 节点负责调用带工具能力的模型；
6. 添加 `ToolNode` 节点负责真正执行工具；
7. 使用 `tools_condition` 判断模型是否需要调用工具；
8. 工具执行结束后，再回到 `chatbot` 节点生成最终回答。

核心流程可以理解为：

```text
用户输入
  ↓
chatbot 节点调用 llm_with_tools
  ↓
模型判断是否需要工具
  ├─ 不需要工具 → 直接结束
  └─ 需要工具 → 进入 tools 节点执行 TavilySearch
                      ↓
                  回到 chatbot
                      ↓
                  模型基于工具结果生成最终回答
```

---

## 二、关键导入

相关代码：[base2.py:1-10](base2.py#L1-L10)

```python
from typing import Annotated

from langchain.chat_models import init_chat_model
from langchain_tavily import TavilySearch
from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict

from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
```

### 重点模块

| 模块 | 作用 |
|---|---|
| `init_chat_model` | 初始化聊天模型 |
| `TavilySearch` | Tavily 搜索工具，用于联网搜索 |
| `StateGraph` | 构建 LangGraph 状态图 |
| `add_messages` | 合并消息列表，追加新消息而不是覆盖 |
| `ToolNode` | LangGraph 预置工具节点，负责执行工具调用 |
| `tools_condition` | 判断模型输出中是否包含工具调用 |

### 备注

[base2.py:5](base2.py#L5) 中导入了 `BaseMessage`：

```python
from langchain_core.messages import BaseMessage
```

但当前代码中没有实际使用它。后续如果要更严格地标注消息类型，可以把 `State` 写得更明确一些，例如：

```python
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
```

---

## 三、状态定义：`State` 与 `add_messages`

相关代码：[base2.py:18-19](base2.py#L18-L19)

```python
class State(TypedDict):
    messages: Annotated[list, add_messages]
```

这里定义了图运行时维护的状态结构。

`messages` 是消息列表，`add_messages` 是这个字段的 reducer，表示当节点返回新的消息时，不是覆盖旧消息，而是追加合并。

例如：

```python
旧状态 = {"messages": [HumanMessage(content="今天有什么新闻？")]}
节点返回 = {"messages": [AIMessage(content="我来搜索一下...")]}
合并后 = {"messages": [HumanMessage(...), AIMessage(...)]}
```

在带工具调用的 Agent 图中，消息历史通常会包含：

1. 用户消息；
2. AI 发出的工具调用请求；
3. 工具返回结果；
4. AI 基于工具结果生成的最终回复。

因此 `add_messages` 很重要。

---

## 四、创建状态图

相关代码：[base2.py:22](base2.py#L22)

```python
graph_builder = StateGraph(State)
```

`StateGraph(State)` 表示创建一个以 `State` 为状态结构的 LangGraph 图。

后续添加的每个节点都会接收这个状态，并返回部分状态更新。

---

## 五、初始化 LLM

相关代码：[base2.py:24-27](base2.py#L24-L27)

```python
llm = init_chat_model(
    "deepseek-chat",  # 使用DeepSeek模型
    api_key=os.environ.get("DEEPSEEK_API_KEY")
)
```

这部分与 base1 类似，用统一入口初始化 DeepSeek 聊天模型。

环境变量来自：

```python
load_dotenv()
os.environ.get("DEEPSEEK_API_KEY")
```

使用 `.env` 保存 API Key 是常见做法，但需要注意不要把 `.env` 提交到公开仓库。

---

## 六、初始化 Tavily 搜索工具

相关代码：[base2.py:29-31](base2.py#L29-L31)

```python
# 初始化Tavily搜索工具
tool = TavilySearch(max_results=2)
tools = [tool]
```

### 1. `TavilySearch` 是什么？

`TavilySearch` 是 LangChain 生态中的搜索工具，通常用于让 Agent 具备联网搜索能力。

它适合回答：

- 最新新闻；
- 当前价格；
- 实时资料；
- 需要外部信息的问题；
- 模型训练数据中没有的新信息。

### 2. `max_results=2` 的含义

```python
TavilySearch(max_results=2)
```

表示每次搜索最多返回 2 条结果。

这个参数可以控制搜索结果数量：

- 数量少：响应更快、上下文更短；
- 数量多：信息更充分，但 token 消耗更大，也可能引入噪声。

### 3. `tools = [tool]`

LangChain / LangGraph 的工具绑定通常接收工具列表，即使只有一个工具，也写成列表：

```python
tools = [tool]
```

后续会把这个列表传给：

```python
llm.bind_tools(tools)
ToolNode(tools=[tool])
```

---

## 七、`llm.bind_tools(tools)`：把工具能力交给模型

相关代码：[base2.py:33-34](base2.py#L33-L34)

```python
# 将工具绑定到LLM
llm_with_tools = llm.bind_tools(tools)
```

### 1. `bind_tools` 的作用

`bind_tools()` 会告诉模型：

> 你可以使用这些工具。如果用户问题需要外部能力，可以生成工具调用请求。

绑定后得到的 `llm_with_tools` 仍然是一个模型对象，但它具备了“选择工具”的能力。

### 2. 注意：模型不会在这里直接执行工具

`llm_with_tools.invoke(...)` 的职责是：

- 根据用户问题决定是否需要工具；
- 如果需要，生成 tool call；
- 如果不需要，直接生成普通回答。

真正执行工具的是后面的 `ToolNode`。

也就是说：

```text
bind_tools 让模型知道有哪些工具
ToolNode 负责实际运行这些工具
```

---

## 八、`chatbot` 节点

相关代码：[base2.py:36-37](base2.py#L36-L37)

```python
def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}
```

这个节点的作用是调用绑定工具后的模型。

它可能返回两类结果：

### 1. 普通 AI 回复

如果模型认为不需要调用工具，它会直接返回最终回答。

例如：

```text
User: 你好
Assistant: 你好！有什么可以帮你？
```

### 2. 带工具调用请求的 AIMessage

如果模型认为需要搜索，它可能返回一个包含 tool call 的 `AIMessage`。

此时并不代表工具已经执行，只是模型发出了“我要调用某个工具”的请求。

接下来图会通过 `tools_condition` 判断是否进入 `tools` 节点。

---

## 九、添加 `chatbot` 节点

相关代码：[base2.py:39-40](base2.py#L39-L40)

```python
# 添加聊天机器人节点
graph_builder.add_node("chatbot", chatbot)
```

这表示图中有一个名为 `chatbot` 的节点，对应的执行函数是 `chatbot()`。

图执行到该节点时，会把当前状态传入函数。

---

## 十、`ToolNode`：工具执行节点

相关代码：[base2.py:42-44](base2.py#L42-L44)

```python
# 添加工具节点
tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)
```

### 1. `ToolNode` 是什么？

`ToolNode` 是 LangGraph 提供的预置节点，专门用于执行工具调用。

它会读取上一条 AI 消息中的 tool calls，然后根据 tool call 的名称和参数调用对应工具。

### 2. 它在图中的位置

当前图中，`ToolNode` 被命名为：

```python
"tools"
```

也就是：

```python
graph_builder.add_node("tools", tool_node)
```

后续如果模型请求调用 Tavily 搜索，就会进入这个节点。

### 3. 工具结果也会进入 `messages`

工具执行结果通常会以工具消息的形式加入 `messages`，然后再回到 `chatbot` 节点，让模型基于搜索结果组织自然语言回答。

---

## 十一、`tools_condition`：判断是否需要工具

相关代码：[base2.py:46-50](base2.py#L46-L50)

```python
# 添加条件边
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
```

### 1. 条件边是什么？

普通边是固定流程，例如：

```python
graph_builder.add_edge("tools", "chatbot")
```

表示一定从 `tools` 走回 `chatbot`。

条件边则是根据状态动态选择下一步。

### 2. `tools_condition` 的作用

`tools_condition` 是 LangGraph 预置条件函数。

它会检查 `chatbot` 节点输出的最后一条 AI 消息：

- 如果包含工具调用请求，则路由到 `tools` 节点；
- 如果没有工具调用请求，则图结束。

因此它实现了 Agent 的核心判断：

```text
模型是否想用工具？
```

### 3. 简化理解

这段代码等价于让图拥有以下逻辑：

```python
if 最后一条AI消息里有tool_calls:
    next_node = "tools"
else:
    end
```

---

## 十二、工具调用后回到 `chatbot`

相关代码：[base2.py:51-52](base2.py#L51-L52)

```python
# 工具调用完成后，返回到聊天机器人节点
graph_builder.add_edge("tools", "chatbot")
```

工具执行完后不能直接结束，因为工具结果通常是结构化或原始信息，用户需要的是自然语言答案。

所以流程是：

```text
chatbot 生成工具调用请求
  ↓
tools 执行搜索
  ↓
chatbot 读取搜索结果并生成最终回答
```

这也是 ReAct / Tool Calling Agent 的典型结构。

---

## 十三、设置入口节点与编译图

相关代码：[base2.py:53-54](base2.py#L53-L54)

```python
graph_builder.set_entry_point("chatbot")
graph = graph_builder.compile()
```

### 1. `set_entry_point("chatbot")`

表示图从 `chatbot` 节点开始执行。

在 base1 中使用的是：

```python
graph_builder.add_edge(START, "chatbot")
```

这两种写法都可以表达入口，只是风格不同。

### 2. `compile()`

编译图，使图变成可运行对象。

编译后的 `graph` 可以调用：

```python
graph.invoke(...)
graph.stream(...)
graph.batch(...)
```

---

## 十四、打印图结构：`draw_mermaid()`

相关代码：[base2.py:56-57](base2.py#L56-L57)

```python
# 打印图结构
print(graph.get_graph().draw_mermaid())
```

这会输出 Mermaid 格式的图结构。

Mermaid 是一种文本化画图语法，可以用来展示流程图。

对于当前代码，图结构大致是：

```text
chatbot
  ├─ 如果需要工具 → tools → chatbot
  └─ 如果不需要工具 → END
```

这个功能很适合调试和学习 LangGraph，因为可以直观看到节点和边的连接方式。

---

## 十五、流式运行图

相关代码：[base2.py:59-62](base2.py#L59-L62)

```python
def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)
```

### 1. `graph.stream()` 的作用

`graph.stream()` 会逐步返回图执行过程中各节点的输出。

在当前图中，一个问题可能会产生多个事件：

1. `chatbot` 输出工具调用请求；
2. `tools` 输出工具执行结果；
3. `chatbot` 输出最终回答。

### 2. 当前打印方式的局限

当前代码简单地打印：

```python
value["messages"][-1].content
```

如果最后一条消息是工具调用请求或工具结果，打印内容可能为空、结构化，或者不太像最终回答。

学习时可以先打印完整事件观察：

```python
for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
    print(event)
```

这样能更清楚看到工具调用过程中消息如何变化。

---

## 十六、命令行循环

相关代码：[base2.py:64-73](base2.py#L64-L73)

```python
while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        stream_graph_updates(user_input)
    except KeyboardInterrupt:
        print("\nGoodbye!")
        break
```

这部分实现了交互式命令行聊天。

输入以下内容会退出：

```text
quit
exit
q
```

按 `Ctrl + C` 也会退出。

---

## 十七、当前代码相比 base1 的新增重点

| 对比项 | base1.py | base2.py |
|---|---|---|
| 模型初始化 | 有 | 有 |
| 状态图 | 简单单节点 | 多节点 Agent 图 |
| 工具调用 | 无 | 有 Tavily 搜索 |
| 条件边 | 无 | 有 `tools_condition` |
| 工具执行节点 | 无 | 有 `ToolNode` |
| 图结构 | `START → chatbot` | `chatbot → tools → chatbot`，或直接结束 |
| 外部信息能力 | 无 | 有联网搜索能力 |
| 记忆能力 | 无显式持久记忆 | 无显式持久记忆 |

---

## 十八、需要注意的问题

### 1. 当前代码没有长期记忆

虽然 `State` 中用了 `add_messages`，但每次用户输入时仍然传入新的：

```python
{"messages": [{"role": "user", "content": user_input}]}
```

没有使用 checkpointer 或外部变量保存多轮状态。

因此它主要演示的是工具调用，不是多轮记忆。

### 2. 工具搜索需要 Tavily API Key

`TavilySearch` 通常需要配置 Tavily 的 API Key，例如：

```env
TAVILY_API_KEY=你的_tavily_key
```

如果没有配置，工具调用可能失败。

### 3. 工具调用依赖模型能力

不是所有模型都完全支持工具调用格式。

如果模型不支持或适配不完整，可能出现：

- 模型不调用工具；
- 工具调用参数格式错误；
- `ToolNode` 无法执行；
- 返回结果不符合预期。

---

## 十九、建议延伸学习

### 1. Tool Calling 原理

重点理解：

```text
模型生成 tool call ≠ 工具已经执行
```

完整流程是：

```text
LLM 决定调用工具 → ToolNode 执行工具 → LLM 读取工具结果 → 生成最终回答
```

### 2. `ToolNode`

建议进一步学习：

- `ToolNode` 如何读取 `AIMessage.tool_calls`；
- 多工具时如何匹配工具名称；
- 工具异常如何处理；
- 工具返回值如何进入消息列表。

### 3. `tools_condition`

建议理解它如何判断下一步：

- 有工具调用 → 去 `tools`；
- 无工具调用 → 结束。

### 4. 自定义工具

可以尝试自己定义工具，例如：

```python
from langchain_core.tools import tool

@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b
```

然后加入工具列表：

```python
tools = [add]
llm_with_tools = llm.bind_tools(tools)
```

### 5. 多轮记忆

base2 没有持久记忆。可以继续学习 base3 中的：

```python
MemorySaver
checkpointer
thread_id
```

---

## 二十、一句话总结

[base2.py](base2.py) 的核心是：

> 在 LangGraph 中通过 `bind_tools`、`ToolNode` 和 `tools_condition` 构建一个具备 Tavily 搜索能力的工具调用 Agent，让模型可以根据问题自动决定是否搜索，并基于搜索结果生成回答。
