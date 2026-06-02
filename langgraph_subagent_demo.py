"""A tiny LangGraph demo: a main agent calls sub agents.

Run with:
    python langgraph_subagent_demo.py
"""

import ast
import operator
import re
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class SubAgentState(TypedDict):
    task: str
    result: str


class MainState(TypedDict):
    user_input: str
    route: Literal["research", "math"]
    sub_result: str
    final_answer: str


_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_calculate(expression: str) -> float | int:
    """Calculate a small arithmetic expression without using eval()."""
    tree = ast.parse(expression, mode="eval")

    def visit(node: ast.AST) -> float | int:
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPERATORS:
            return _ALLOWED_OPERATORS[type(node.op)](visit(node.left), visit(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPERATORS:
            return _ALLOWED_OPERATORS[type(node.op)](visit(node.operand))
        raise ValueError("only numbers and + - * / operators are supported")

    return visit(tree)


def research_agent(state: SubAgentState) -> dict[str, str]:
    task = state["task"]
    return {
        "result": (
            "ResearchAgent: 已整理任务背景、关键概念和结论。"
            f"针对「{task}」，子 agent 建议先明确职责边界，"
            "再把可独立处理的任务交给专门节点。"
        )
    }


def math_agent(state: SubAgentState) -> dict[str, str]:
    task = state["task"]
    match = re.search(r"[\d\s+\-*/().]+", task)
    if not match:
        return {"result": "MathAgent: 没有找到可计算的表达式。"}

    expression = match.group().strip()
    try:
        value = _safe_calculate(expression)
    except Exception as exc:
        return {"result": f"MathAgent: 表达式「{expression}」无法计算：{exc}"}

    return {"result": f"MathAgent: {expression} = {value}"}


def build_research_graph():
    builder = StateGraph(SubAgentState)
    builder.add_node("research_agent", research_agent)
    builder.add_edge(START, "research_agent")
    builder.add_edge("research_agent", END)
    return builder.compile()


def build_math_graph():
    builder = StateGraph(SubAgentState)
    builder.add_node("math_agent", math_agent)
    builder.add_edge(START, "math_agent")
    builder.add_edge("math_agent", END)
    return builder.compile()


research_graph = build_research_graph()
math_graph = build_math_graph()


def route_task(state: MainState) -> dict[str, str]:
    text = state["user_input"]
    math_keywords = ("计算", "加", "减", "乘", "除", "+", "-", "*", "/")
    route = "math" if any(keyword in text for keyword in math_keywords) else "research"
    return {"route": route}


def select_subagent(state: MainState) -> str:
    return state["route"]


def call_research_subagent(state: MainState) -> dict[str, str]:
    result = research_graph.invoke({"task": state["user_input"]})
    return {"sub_result": result["result"]}


def call_math_subagent(state: MainState) -> dict[str, str]:
    result = math_graph.invoke({"task": state["user_input"]})
    return {"sub_result": result["result"]}


def summarize(state: MainState) -> dict[str, str]:
    return {
        "final_answer": (
            f"MainAgent: 已将任务路由给 {state['route']} 子 agent。\n"
            f"子 agent 返回：{state['sub_result']}\n"
            "MainAgent: 我再基于这个结果组织最终回复。"
        )
    }


def build_main_graph():
    builder = StateGraph(MainState)
    builder.add_node("route_task", route_task)
    builder.add_node("call_research_subagent", call_research_subagent)
    builder.add_node("call_math_subagent", call_math_subagent)
    builder.add_node("summarize", summarize)

    builder.add_edge(START, "route_task")
    builder.add_conditional_edges(
        "route_task",
        select_subagent,
        {
            "research": "call_research_subagent",
            "math": "call_math_subagent",
        },
    )
    builder.add_edge("call_research_subagent", "summarize")
    builder.add_edge("call_math_subagent", "summarize")
    builder.add_edge("summarize", END)
    return builder.compile()


def run_demo(user_input: str) -> None:
    graph = build_main_graph()
    result = graph.invoke({"user_input": user_input})

    print(f"User: {user_input}")
    print(f"MainAgent route: {result['route']}")
    print(f"SubAgent result: {result['sub_result']}")
    print(f"Final:\n{result['final_answer']}")
    print("-" * 60)


if __name__ == "__main__":
    main_graph = build_main_graph()
    print(main_graph.get_graph().draw_mermaid())
    print("=" * 60)

    run_demo("请调研一下 LangGraph 中子 agent 的作用")
    run_demo("请计算 2 + 3 * 4")
