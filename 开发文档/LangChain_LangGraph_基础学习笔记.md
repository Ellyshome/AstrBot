# LangChain + LangGraph 基础学习笔记

对应代码文件：[base1.py](base1.py)

## 一、整体代码作用

当前代码实现了一个最小可运行的命令行聊天机器人：

1. 使用 `dotenv` 加载 `.env` 中的环境变量；
2. 使用 LangChain 的 `init_chat_model()` 初始化大语言模型；
3. 使用 LangGraph 的 `StateGraph` 构建一个简单状态图；
4. 定义一个 `chatbot` 节点，接收用户消息并调用模型生成回复；
5. 使用 `graph.stream()` 以流式事件的方式执行图；
6. 通过 `while True` 实现命令行循环对话。

核心流程可以概括为：

```text
用户输入
  ↓
构造 messages 状态
  ↓
进入 LangGraph 图
  ↓
执行 chatbot 节点
  ↓
调用 llm.invoke()
  ↓
返回 AI 回复
  ↓
打印 Assistant 输出
```

---

## 二、环境变量加载

相关代码：[base1.py:9-13](base1.py#L9-L13)

```python
import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()
```

### 作用

`load_dotenv()` 会读取项目中的 `.env` 文件，并把里面的配置加载到当前 Python 进程的环境变量中。

例如 `.env` 中可以写：

```env
DEEPSEEK_API_KEY=你的_api_key
```

之后代码中就可以通过：

```python
os.environ.get("DEEPSEEK_API_KEY")
```

读取这个值。

### 注意点

不要把 `.env` 文件提交到公开仓库，因为里面通常包含 API Key、数据库密码等敏感信息。

---

## 三、`init_chat_model`：初始化聊天模型

相关代码：[base1.py:3](base1.py#L3)、[base1.py:18-21](base1.py#L18-L21)

```python
from langchain.chat_models import init_chat_model

llm = init_chat_model(
    "deepseek-chat",  # 使用DeepSeek模型
    api_key=os.environ.get("DEEPSEEK_API_KEY")
)
```

### 1. `init_chat_model` 是什么？

`init_chat_model()` 是 LangChain 提供的一个统一初始化聊天模型的方法。

它的作用是：用统一的接口初始化不同厂商的大模型，例如 OpenAI、Anthropic、DeepSeek、Google、通义千问等。

传统方式中，不同模型可能需要导入不同类，例如：

```python
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
```

而 `init_chat_model()` 尝试提供一个更统一的入口。

### 2. 当前代码中的含义

```python
llm = init_chat_model(
    "deepseek-chat",
    api_key=os.environ.get("DEEPSEEK_API_KEY")
)
```

表示初始化一个名为 `"deepseek-chat"` 的聊天模型，并使用环境变量中的 `DEEPSEEK_API_KEY` 作为 API Key。

初始化完成后，`llm` 就是一个可以被调用的聊天模型对象。

### 3. 常见调用方式

当前代码使用的是：

```python
llm.invoke(state["messages"])
```

相关代码：[base1.py:24-25](base1.py#L24-L25)

```python
def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}
```

`invoke()` 是 LangChain 中非常核心的调用方法，用来同步调用模型。

---

## 四、`llm.invoke()`：调用模型

### 1. 基本含义

```python
llm.invoke(input)
```

表示给模型传入输入，然后等待模型返回完整结果。

在当前代码中：

```python
llm.invoke(state["messages"])
```

这里传入的是一组聊天消息，也就是 `state["messages"]`。

### 2. `state["messages"]` 是什么？

它来自图状态中的 `messages` 字段。

在用户输入时，代码会传入：

```python
{"messages": [{"role": "user", "content": user_input}]}
```

相关代码：[base1.py:34-35](base1.py#L34-L35)

```python
for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
```

也就是说，每次用户输入都会变成类似下面的结构：

```python
{
    "messages": [
        {
            "role": "user",
            "content": "你好"
        }
    ]
}
```

模型接收到这组消息后，会返回一条 AI 消息。

### 3. 为什么返回值要包成列表？

当前代码中：

```python
return {"messages": [llm.invoke(state["messages"])]}
```

注意这里不是：

```python
return {"messages": llm.invoke(state["messages"])}
```

而是：

```python
return {"messages": [llm.invoke(...)]}
```

这是因为 `messages` 字段本身表示的是“消息列表”。

`llm.invoke()` 返回的是单条 AI 消息对象，例如：

```python
AIMessage(content="你好，我是助手")
```

为了把它合并进 `messages` 列表，需要写成：

```python
[AIMessage(...)]
```

也就是“包含一条 AI 消息的列表”。

---

## 五、`State`：定义图的状态结构

相关代码：[base1.py:1](base1.py#L1)、[base1.py:4](base1.py#L4)、[base1.py:15-16](base1.py#L15-L16)

```python
from typing import Annotated
from typing_extensions import TypedDict

class State(TypedDict):
    messages: Annotated[list, add_messages]
```

### 1. `TypedDict` 是什么？

`TypedDict` 用来声明字典结构的类型。

这里定义了一个状态类型 `State`：

```python
class State(TypedDict):
    messages: Annotated[list, add_messages]
```

意思是：这个状态是一个字典，其中必须包含一个字段：

```python
messages
```

它的类型是：

```python
list
```

也就是消息列表。

### 2. 为什么 LangGraph 需要 State？

LangGraph 是围绕“状态图”运行的。

图中的每个节点都接收一个状态，然后返回对状态的更新。

当前代码中，状态长这样：

```python
{
    "messages": [...]
}
```

`chatbot` 节点接收这个状态：

```python
def chatbot(state: State):
```

然后返回新的状态更新：

```python
return {"messages": [llm.invoke(state["messages"])]}
```

LangGraph 会把这个返回结果合并回原状态。

---

## 六、`Annotated[list, add_messages]` 的含义

相关代码：[base1.py:7](base1.py#L7)、[base1.py:15-16](base1.py#L15-L16)

```python
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]
```

这是当前代码中最关键、也最容易忽略的部分。

### 1. `Annotated` 是什么？

`Annotated` 是 Python 类型系统中的一个工具，用来给类型附加额外信息。

普通写法：

```python
messages: list
```

只表示 `messages` 是一个列表。

而：

```python
messages: Annotated[list, add_messages]
```

表示：

```text
messages 是一个 list，并且它有一个特殊的合并规则 add_messages
```

### 2. `add_messages` 是什么？

`add_messages` 是 LangGraph 提供的消息合并函数。

它告诉 LangGraph：

> 当某个节点返回新的 `messages` 时，不要直接覆盖旧的 `messages`，而是把新消息追加到旧消息后面。

例如初始状态是：

```python
{
    "messages": [
        {"role": "user", "content": "你好"}
    ]
}
```

`chatbot` 节点返回：

```python
{
    "messages": [
        AIMessage(content="你好，有什么可以帮你？")
    ]
}
```

如果没有 `add_messages`，新返回的 `messages` 可能会覆盖旧的 `messages`。

如果有 `add_messages`，合并后会变成：

```python
{
    "messages": [
        {"role": "user", "content": "你好"},
        AIMessage(content="你好，有什么可以帮你？")
    ]
}
```

这样就保留了完整的对话历史。

### 3. `add_messages` 的重要性

在聊天机器人中，消息历史非常重要。

如果没有历史，模型每轮只能看到当前用户输入，无法进行上下文对话。

例如：

```text
User: 我叫小明
Assistant: 你好小明
User: 我叫什么？
```

如果保留历史，模型能回答：

```text
你叫小明。
```

如果不保留历史，模型可能不知道用户叫什么。

### 4. 当前代码的一个限制

当前代码每次调用 `stream_graph_updates()` 时传入的是：

```python
{"messages": [{"role": "user", "content": user_input}]}
```

也就是说，每轮输入都会单独创建一个新的图输入。

虽然 `add_messages` 可以在一次图运行过程中合并消息，但当前代码没有显式保存多轮对话状态。

所以当前代码可能并不能真正实现长期多轮记忆。

如果想保留多轮对话历史，通常需要：

1. 手动维护一个 `messages` 列表；
2. 使用 LangGraph 的 checkpointer；
3. 使用 thread/session 机制保存状态。

一个简单的手动维护方式类似：

```python
messages = []

def stream_graph_updates(user_input: str):
    global messages
    messages.append({"role": "user", "content": user_input})

    for event in graph.stream({"messages": messages}):
        for value in event.values():
            ai_message = value["messages"][-1]
            print("Assistant:", ai_message.content)
            messages.append(ai_message)
```

不过真实项目中更推荐使用 LangGraph 的持久化机制。

---

## 七、`StateGraph`：构建状态图

相关代码：[base1.py:6](base1.py#L6)、[base1.py:28-32](base1.py#L28-L32)

```python
from langgraph.graph import StateGraph, START

graph_builder = StateGraph(State)
# 添加节点和边
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph = graph_builder.compile()
```

### 1. `StateGraph` 是什么？

`StateGraph` 是 LangGraph 中用于构建状态流转图的核心类。

它可以把多个处理步骤组织成一个图。

每个节点可以理解为一个函数：

```text
输入状态 → 处理 → 返回状态更新
```

多个节点通过边连接起来，形成执行流程。

### 2. 当前图结构

当前代码的图非常简单：

```text
START → chatbot
```

也就是：

1. 从起点 `START` 开始；
2. 执行 `chatbot` 节点；
3. 节点调用大模型；
4. 返回 AI 回复；
5. 图执行结束。

### 3. `StateGraph(State)` 的含义

```python
graph_builder = StateGraph(State)
```

这里把前面定义的 `State` 类型传给了 `StateGraph`。

意思是：

> 这个图运行过程中维护的状态结构，就是 `State` 定义的结构。

当前的状态结构只有一个字段：

```python
messages
```

### 4. `add_node()`：添加节点

```python
graph_builder.add_node("chatbot", chatbot)
```

这行代码表示往图中添加一个名为 `"chatbot"` 的节点。

节点对应的处理函数是：

```python
chatbot
```

也就是：

```python
def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}
```

执行到这个节点时，LangGraph 会自动调用这个函数。

### 5. `add_edge()`：添加边

```python
graph_builder.add_edge(START, "chatbot")
```

这行代码表示添加一条边：

```text
START → chatbot
```

也就是说，图从起点开始后，第一个执行的节点是 `chatbot`。

### 6. `compile()`：编译图

```python
graph = graph_builder.compile()
```

在 LangGraph 中，`StateGraph` 只是一个图构建器。

调用 `compile()` 后，才会生成真正可以运行的图对象。

编译后的 `graph` 支持：

```python
graph.invoke(...)
graph.stream(...)
graph.batch(...)
```

等运行方式。

---

## 八、`graph.stream()`：流式执行图

相关代码：[base1.py:34-37](base1.py#L34-L37)

```python
def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)
```

### 1. `graph.stream()` 是什么？

`graph.stream()` 用于以流式方式执行图。

它会逐步返回图执行过程中的事件。

在当前这个简单图里，只有一个节点 `chatbot`，所以通常只会看到一次主要输出。

如果图中有多个节点，比如：

```text
START → classify → retrieve → generate
```

那么 `graph.stream()` 可以逐步拿到每个节点产生的结果。

### 2. `event` 是什么？

在 LangGraph 中，`graph.stream()` 每次产出的 `event` 通常是一个字典，结构可能类似：

```python
{
    "chatbot": {
        "messages": [
            AIMessage(content="你好，有什么可以帮你？")
        ]
    }
}
```

也就是说：

- key 是节点名；
- value 是该节点返回的状态更新。

当前代码中：

```python
for value in event.values():
```

就是不关心节点名，只取节点的返回值。

### 3. 为什么使用 `value["messages"][-1]`？

```python
print("Assistant:", value["messages"][-1].content)
```

`value["messages"]` 是消息列表。

`[-1]` 表示取最后一条消息。

因为 `chatbot` 节点刚刚生成的 AI 回复被追加到了消息列表末尾，所以最后一条就是助手回复。

`.content` 用来获取消息正文。

---

## 九、命令行循环

相关代码：[base1.py:40-49](base1.py#L40-L49)

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

### 作用

这部分实现了一个简单的命令行聊天循环。

用户可以不断输入内容：

```text
User: 你好
Assistant: 你好，有什么可以帮你？
User: 介绍一下 LangGraph
Assistant: ...
```

输入以下任意内容时退出：

```text
quit
exit
q
```

或者按下 `Ctrl + C`，触发 `KeyboardInterrupt`，也会退出。

---

## 十、当前代码的核心知识点总结

### 1. `init_chat_model`

用于初始化聊天模型。

```python
llm = init_chat_model("deepseek-chat", api_key=...)
```

可以理解为：

```text
创建一个可以对话的大模型对象
```

### 2. `llm.invoke()`

同步调用模型。

```python
llm.invoke(messages)
```

可以理解为：

```text
把消息列表发给模型，等待模型返回一条 AI 消息
```

### 3. `State`

定义 LangGraph 图中的状态结构。

```python
class State(TypedDict):
    messages: Annotated[list, add_messages]
```

可以理解为：

```text
这个图的状态里有一个 messages 字段，用来保存对话消息
```

### 4. `add_messages`

定义 `messages` 字段的合并规则。

```python
messages: Annotated[list, add_messages]
```

可以理解为：

```text
新的消息不要覆盖旧消息，而是追加到消息列表后面
```

### 5. `StateGraph`

构建一个状态图。

```python
graph_builder = StateGraph(State)
```

可以理解为：

```text
我要构建一个基于 State 状态流转的图
```

### 6. `add_node`

添加图节点。

```python
graph_builder.add_node("chatbot", chatbot)
```

可以理解为：

```text
图中有一个叫 chatbot 的步骤，它执行 chatbot 函数
```

### 7. `add_edge`

连接图节点。

```python
graph_builder.add_edge(START, "chatbot")
```

可以理解为：

```text
图从 START 开始后，进入 chatbot 节点
```

### 8. `compile`

编译图，使其可运行。

```python
graph = graph_builder.compile()
```

可以理解为：

```text
把图构建器变成真正可以执行的图对象
```

### 9. `graph.stream`

流式执行图。

```python
graph.stream(input_state)
```

可以理解为：

```text
运行图，并逐步拿到每个节点的输出
```

---

## 十一、`invoke`、`stream`、`batch` 的区别

LangChain 和 LangGraph 中经常会看到这些方法。

### 1. `invoke`

同步执行一次，返回最终结果。

```python
result = graph.invoke(input)
```

适合普通调用。

### 2. `stream`

流式执行，逐步返回中间结果或节点结果。

```python
for event in graph.stream(input):
    print(event)
```

适合：

- 观察图执行过程；
- 多节点工作流；
- 流式输出；
- 调试。

### 3. `batch`

批量执行多个输入。

```python
results = graph.batch([
    {"messages": [{"role": "user", "content": "你好"}]},
    {"messages": [{"role": "user", "content": "讲个笑话"}]},
])
```

适合一次处理多个请求。

---

## 十二、可以进一步学习的知识点

### 1. 多轮对话状态保存

当前代码每轮输入都是：

```python
{"messages": [{"role": "user", "content": user_input}]}
```

如果想让机器人真正记住前文，需要学习：

- 手动维护 `messages`；
- LangGraph checkpointer；
- thread/session 配置；
- memory saver；
- 持久化存储对话历史。

建议重点学习：

```text
LangGraph checkpointing
LangGraph MemorySaver
thread_id
```

### 2. 条件边 `add_conditional_edges`

当前图只有一条固定路径：

```text
START → chatbot
```

实际 Agent 通常会根据模型输出选择不同路径，例如：

```text
START → chatbot → 是否需要工具？
                    ├── 是 → tool_node → chatbot
                    └── 否 → END
```

可以进一步学习：

```python
graph_builder.add_conditional_edges(...)
```

它常用于构建 Agent、工具调用、流程分支。

### 3. `END` 结束节点

当前代码没有显式写 `END`，因为简单图可以自然结束。

更完整的 LangGraph 代码通常会引入：

```python
from langgraph.graph import END
```

然后添加：

```python
graph_builder.add_edge("chatbot", END)
```

图结构会更清晰：

```text
START → chatbot → END
```

### 4. 工具调用 Tool Calling

如果要让模型使用工具，比如：

- 搜索网页；
- 查询数据库；
- 调用 API；
- 执行计算；
- 读取文件；

就需要学习 LangChain/LangGraph 的工具调用机制。

相关概念：

```text
tool
bind_tools
ToolNode
tools_condition
```

### 5. 消息类型

当前代码中输入消息使用的是字典形式：

```python
{"role": "user", "content": user_input}
```

LangChain 也提供专门的消息类：

```python
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
```

例如：

```python
HumanMessage(content="你好")
AIMessage(content="你好，我是助手")
SystemMessage(content="你是一个专业助手")
```

建议后续学习这些消息类型，因为真实项目中会经常使用。

### 6. System Prompt

当前代码没有设置系统提示词。

如果想控制助手的角色、语气和行为，可以加入 system message：

```python
{
    "role": "system",
    "content": "你是一个专业、简洁、耐心的 Python 教学助手。"
}
```

多轮对话时通常会把 system message 放在消息列表最前面。

### 7. 异步调用

当前代码使用同步调用：

```python
llm.invoke(...)
```

后续可以学习异步调用：

```python
await llm.ainvoke(...)
```

以及异步流式调用：

```python
async for event in graph.astream(...):
    ...
```

适合 Web 服务、机器人、异步 API 后端等场景。

---

## 十三、建议掌握的最小心智模型

可以把当前代码理解成三个层次：

### 第一层：模型层

```python
llm = init_chat_model(...)
```

负责创建大模型。

### 第二层：节点层

```python
def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}
```

负责定义一个处理步骤：拿到当前消息，调用模型，返回模型回复。

### 第三层：图层

```python
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph = graph_builder.compile()
```

负责把处理步骤组织成流程。

---

## 十四、推荐改进版结构

如果只是学习，当前代码已经足够简单清晰。

如果想让结构更标准，可以考虑显式加入 `END`：

```python
from langgraph.graph import StateGraph, START, END

graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)
graph = graph_builder.compile()
```

图结构更明确：

```text
START → chatbot → END
```

---

## 十五、学习路线建议

建议按照下面顺序继续学习：

1. **LangChain 消息模型**
   - `HumanMessage`
   - `AIMessage`
   - `SystemMessage`

2. **LangChain 模型调用**
   - `invoke`
   - `stream`
   - `batch`
   - `ainvoke`
   - `astream`

3. **LangGraph 基础图**
   - `StateGraph`
   - `START`
   - `END`
   - `add_node`
   - `add_edge`
   - `compile`

4. **状态合并机制**
   - `Annotated`
   - `add_messages`
   - reducer 概念

5. **多轮对话记忆**
   - checkpointer
   - `MemorySaver`
   - `thread_id`

6. **Agent 工具调用**
   - `tool`
   - `ToolNode`
   - `tools_condition`
   - `bind_tools`

7. **复杂图流程**
   - 条件边
   - 循环边
   - 多节点协作
   - RAG 问答流程

---

## 十六、一句话总结

这份代码的核心是：

> 用 `init_chat_model` 创建聊天模型，用 `StateGraph` 搭建对话流程，用 `add_messages` 维护消息累积规则，然后通过 `graph.stream()` 执行图并输出模型回复。