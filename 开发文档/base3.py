"""LangGraph 教程: 添加记忆功能的聊天机器人

本示例展示了如何使用 LangGraph 的检查点功能为聊天机器人添加记忆功能，
使其能够记住对话历史并在多轮对话中保持上下文。
"""

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

import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

# 定义状态类型，使用 add_messages 注解来自动合并消息列表
class State(TypedDict):
    messages: Annotated[list, add_messages]  # 消息列表将使用 add_messages reducer 自动合并


# 初始化 DeepSeek 聊天模型
llm = init_chat_model(
    "deepseek-chat",  # 使用DeepSeek模型
    api_key=os.environ.get("DEEPSEEK_API_KEY")  # 从环境变量中获取API密钥
)

# 创建状态图构建器
graph_builder = StateGraph(State)

# 初始化Tavily搜索工具
print("\n初始化Tavily搜索工具...")
tool = TavilySearch(max_results=2)  # 设置最多返回2个搜索结果
tools = [tool]

# 将工具绑定到LLM
llm_with_tools = llm.bind_tools(tools)

# 定义聊天机器人节点函数
def chatbot(state: State):
    """LLM节点函数，处理用户输入并生成响应"""
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# 添加聊天机器人节点
graph_builder.add_node("chatbot", chatbot)

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

print("\n构建图并添加记忆功能...")

# 创建内存保存器
print("\n创建 MemorySaver 实例作为检查点保存器...")
memory = MemorySaver()  # 在内存中保存状态，适用于开发和测试

# 使用内存保存器编译图
print("使用检查点保存器编译图...")
graph = graph_builder.compile(checkpointer=memory)  # 将内存保存器传递给图

# 打印图结构
print("\n图结构如下：")
print(graph.get_graph().draw_mermaid())

# 定义对话线程ID
print("\n设置对话线程 ID = '1'...")
config = {"configurable": {"thread_id": "1"}}  # 使用线程ID来标识和区分不同的对话

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

