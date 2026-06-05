# base4.py 学习笔记：LangGraph 子图调用

对应代码文件：[base4.py](base4.py)

## 一、整体作用

base4.py 演示了 LangGraph 中**子图调用**的核心概念：

1. 创建一个不包含 LLM 的子图（计算器）
2. 创建主图，在主图中调用子图
3. 展示子图如何作为模块协助工作

核心流程：

```text
主图
  ↓
调用子图
  ↓
子图执行计算
  ↓
返回结果给主图
  ↓
主图继续处理
```

---

## 二、关键导入

相关代码：[base4.py:1-5](base4.py#L1-L5)

```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
```

### 重点模块

| 模块 | 作用 |
|---|---|
| `StateGraph` | 构建状态图 |
| `START`, `END` | 图的起点和终点 |
| `add_messages` | 合并消息列表 |

---

## 三、子图：计算器（不含 LLM）

### 1. 子图状态定义

相关代码：[base4.py:8-12](base4.py#L8-L12)

```python
class CalculatorState(TypedDict):
    input: float
    operation: str
    result: float
```

子图有三个字段：
- `input`: 输入数值
- `operation`: 操作类型（add/multiply/subtract）
- `result`: 计算结果

### 2. 子图节点函数

相关代码：[base4.py:15-23](base4.py#L15-L23)

```python
def add(state: CalculatorState):
    return {"result": state["input"] + 10}


def multiply(state: CalculatorState):
    return {"result": state["input"] * 2}


def subtract(state: CalculatorState):
    return {"result": state["input"] - 5}
```

三个简单的数学运算节点。

### 3. 子图条件判断

相关代码：[base4.py:26-34](base4.py#L26-L34)

```python
def calculator_condition(state: CalculatorState):
    if state["operation"] == "add":
        return "add"
    elif state["operation"] == "multiply":
        return "multiply"
    else:
        return "subtract"
```

根据 `operation` 字段决定走哪个计算节点。

### 4. 构建子图

相关代码：[base4.py:37-49](base4.py#L37-L49)

```python
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
```

这就是完整的子图构建过程。

---

## 四、主图

### 1. 主图状态定义

相关代码：[base4.py:52-56](base4.py#L52-L56)

```python
class MainState(TypedDict):
    messages: Annotated[list, add_messages]
    input_value: float
    final_output: str
```

主图有三个字段：
- `messages`: 消息列表
- `input_value`: 传给子图的输入值
- `final_output`: 最终输出

### 2. 调用子图的节点

相关代码：[base4.py:59-67](base4.py#L59-L67)

```python
def call_calculator(state: MainState):
    calc_result = calculator_graph.invoke({
        "input": state["input_value"],
        "operation": "multiply"
    })
    return {
        "messages": [{"role": "system", "content": f"计算结果: {calc_result['result']}"}],
        "final_output": f"最终结果: {calc_result['result']}"
    }
```

**关键：调用子图就像调用普通函数一样**，使用 `calculator_graph.invoke()`。

### 3. 格式化输出节点

相关代码：[base4.py:70-74](base4.py#L70-L74)

```python
def format_output(state: MainState):
    return {
        "messages": [{"role": "assistant", "content": state["final_output"]}]
    }
```

### 4. 构建主图

相关代码：[base4.py:77-83](base4.py#L77-L83)

```python
main_builder = StateGraph(MainState)
main_builder.add_node("call_calculator", call_calculator)
main_builder.add_node("format_output", format_output)
main_builder.set_entry_point("call_calculator")
main_builder.add_edge("call_calculator", "format_output")
main_builder.add_edge("format_output", END)
main_graph = main_builder.compile()
```

---

## 五、测试子图直接调用

相关代码：[base4.py:91-100](base4.py#L91-L100)

```python
print("\n=== 测试子图直接调用 ===")
result1 = calculator_graph.invoke({"input": 5, "operation": "add"})
print(f"add: {result1}")

result2 = calculator_graph.invoke({"input": 5, "operation": "multiply"})
print(f"multiply: {result2}")

result3 = calculator_graph.invoke({"input": 5, "operation": "subtract"})
print(f"subtract: {result3}")
```

子图可以独立运行，就像普通函数一样。

---

## 六、测试主图调用子图

相关代码：[base4.py:102-109](base4.py#L102-L109)

```python
print("\n=== 测试主图调用子图 ===")
main_result = main_graph.invoke({
    "messages": [{"role": "user", "content": "计算一下"}],
    "input_value": 20
})
print(f"主图结果: {main_result}")
```

主图在运行过程中会调用子图，然后继续自己的流程。

---

## 七、子图调用的核心要点

### 1. 子图也是图

子图本身就是一个完整的 `StateGraph`，需要：
- 定义状态
- 添加节点
- 添加边
- 编译

### 2. 调用方式

```python
subgraph_result = subgraph.invoke(subgraph_input)
```

就像调用普通函数一样简单。

### 3. 状态传递

- 主图状态 → 手动构造子图输入
- 子图输出 → 手动解析，更新主图状态

没有自动的状态传递，你需要显式处理。

### 4. 子图可以不包含 LLM

子图可以是纯逻辑处理、工具调用等，不需要 LLM。

---

## 八、为什么要用子图？

| 优势 | 说明 |
|---|---|
| 模块化 | 把复杂逻辑拆成小模块 |
| 复用 | 同一个子图可以在多个地方调用 |
| 测试 | 子图可以独立测试 |
| 团队协作 | 不同人负责不同子图 |

---

## 九、建议延伸学习

### 1. 子图与父图状态共享

可以尝试让子图直接读写父图的状态（需要使用 `checkpointer` 或更复杂的设计）。

### 2. 嵌套子图

子图里面还可以有子图，形成多层嵌套。

### 3. 子图作为工具

把子图包装成 LangChain 工具，供 LLM 调用。
