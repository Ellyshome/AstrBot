from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages


class CalculatorState(TypedDict):
    input: float
    operation: str
    result: float


def add(state: CalculatorState):
    return {"result": state["input"] + 10}


def multiply(state: CalculatorState):
    return {"result": state["input"] * 2}


def subtract(state: CalculatorState):
    return {"result": state["input"] - 5}


def calculator_condition(state: CalculatorState):
    if state["operation"] == "add":
        return "add"
    elif state["operation"] == "multiply":
        return "multiply"
    else:
        return "subtract"


calculator_builder = StateGraph(CalculatorState)
calculator_builder.add_node("add", add)
calculator_builder.add_node("multiply", multiply)
calculator_builder.add_node("subtract", subtract)
calculator_builder.set_entry_point(START)
calculator_builder.add_conditional_edges(
    START,
    calculator_condition,
    {
        "add": "add",
        "multiply": "multiply",
        "subtract": "subtract",
    },
)
calculator_builder.add_edge("add", END)
calculator_builder.add_edge("multiply", END)
calculator_builder.add_edge("subtract", END)
calculator_graph = calculator_builder.compile()


class MainState(TypedDict):
    messages: Annotated[list, add_messages]
    input_value: float
    final_output: str


def call_calculator(state: MainState):
    calc_result = calculator_graph.invoke({
        "input": state["input_value"],
        "operation": "multiply"
    })
    return {
        "messages": [{"role": "system", "content": f"计算结果: {calc_result['result']}"}],
        "final_output": f"最终结果: {calc_result['result']}"
    }


def format_output(state: MainState):
    return {
        "messages": [{"role": "assistant", "content": state["final_output"]}]
    }


main_builder = StateGraph(MainState)
main_builder.add_node("call_calculator", call_calculator)
main_builder.add_node("format_output", format_output)
main_builder.set_entry_point("call_calculator")
main_builder.add_edge("call_calculator", "format_output")
main_builder.add_edge("format_output", END)
main_graph = main_builder.compile()


print("=== 子图结构 ===")
print(calculator_graph.get_graph().draw_mermaid())

print("\n=== 主图结构 ===")
print(main_graph.get_graph().draw_mermaid())

print("\n=== 测试子图直接调用 ===")
result1 = calculator_graph.invoke({"input": 5, "operation": "add"})
print(f"add: {result1}")

result2 = calculator_graph.invoke({"input": 5, "operation": "multiply"})
print(f"multiply: {result2}")

result3 = calculator_graph.invoke({"input": 5, "operation": "subtract"})
print(f"subtract: {result3}")

print("\n=== 测试主图调用子图 ===")
main_result = main_graph.invoke({
    "messages": [{"role": "user", "content": "计算一下"}],
    "input_value": 20
})
print(f"主图结果: {main_result}")
