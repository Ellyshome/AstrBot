langgraph 笔记
# 1.基本对话流 
```py
# 基本引入
import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()
```

```py
# 初始化 DeepSeek 聊天模型
from langchain.chat_models import init_chat_model
llm = init_chat_model(
    "deepseek-chat",  # 使用DeepSeek模型
    api_key=os.environ.get("DEEPSEEK_API_KEY")  # 从环境变量中获取API密钥
)

```

```py
# 配置状态机
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START
class State(TypedDict):
    messages: Annotated[list, add_messages]

# 创建图容器
graph_builder = StateGraph(State)
```

```py
# 配置基本聊天机器人
def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

# 添加节点和边
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph = graph_builder.compile()

# 流式调用 graph.stream 的封装函数
def stream_graph_updates(user_input: str):
    # 调用 graph.stream 逐事件获取执行结果
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        # 遍历事件中的结果，取出最新消息
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)

# 主交互循环
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
---

## 图容器StateGraph的.stream 函数介绍
```py
# 
graph.stream(
    inputs,           # 必传：图的初始状态（如用户消息）
    config=None,      # 可选：运行配置（线程ID、模型参数等）
    stream_mode="values"  # 可选：流式模式，默认 values
)
```
- inputs：字典格式，必须匹配你定义的 State 结构（如 {"messages": [...]}）
- config：用于控制运行时，如 {"configurable": {"thread_id": "1"}} 实现记忆
- stream_mode：
- values：输出完整状态（最常用）
- updates：只输出节点返回的增量更新
- debug：调试用，输出执行详情
- 返回值: 返回一个可迭代对象（generator），可以用 for event in graph.stream(...) 遍历每一步执行结果。

---
## 关于add_messages
```py
from langgraph.graph.message import add_messages
class State(TypedDict):
    messages: Annotated[list, add_messages]
```
- 是LangGraph 内置的消息合并器
- add_messages 把新消息追加到对话历史里，并且能按 ID 更新已有消息。
---

# 2.增加搜索功能
- 工具绑定（Tool Binding）：通过bind_tools方法将工具与LLM集成
- 预构建组件：使用ToolNode和tools_condition简化工具处理
- 条件边：根据状态动态决定执行流程
- 循环流程：创建包含循环的复杂工作流
## TavilySearch
- 是 LangChain 封装的 Tavily 搜索引擎工具，专门给 LLM/AI Agent 做实时联网搜索

```py
from langchain_tavily import TavilySearch

# 初始化Tavily搜索工具
tool = TavilySearch(max_results=2)
tools = [tool]

# 初始化Tavily搜索工具
tool = TavilySearch(max_results=2)
tools = [tool]

# 将工具绑定到LLM
llm_with_tools = llm.bind_tools(tools)

# 添加工具节点
tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)

# 添加条件边
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)

# 工具调用完成后，返回到聊天机器人节点
graph_builder.add_edge("tools", "chatbot")
graph_builder.set_entry_point("chatbot")
graph = graph_builder.compile()
```
## 添加条件边add_conditional_edges

```py
graph_builder.add_conditional_edges(
    source,         # （必填）条件边的出发节点名，如 "chatbot"。
    condition_fn,   # 条件函数：state → 下一步节点/标识，签名：def fn(state: State) -> str
    mapping=None    # 可选
)
```
- 条件边：和普通边 add_edge（固定 A→B）不同，它是动态分支—— 运行时根据「状态 + 条件函数」决定下一步走哪个节点，相当于 if-else 路由。
- tools_condition 是专用路由函数，专门判断：LLM 输出是否包含工具调用。
- `source`：条件边的出发节点名，例如 `"chatbot"`。
- `condition_fn`：条件函数，接收当前完整 `state`，返回下一步节点名、标识或 `"__end__"`。
  - 典型签名：`def fn(state: State) -> str`
- `mapping`：可选字典，用于把 `condition_fn` 的返回值映射成真实节点名。
  - 例如：`{"tools": "tool_node", "__end__": END}`
  - 省略时，函数返回值会直接当作目标节点名。

# 增加记忆功能
