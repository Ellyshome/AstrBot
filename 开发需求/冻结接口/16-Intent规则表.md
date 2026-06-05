# 16-Intent规则表

## Intent分类

| Intent         | 说明   |
| -------------- | ---- |
| task_record    | 创建任务 |
| event_record   | 记录事件 |
| meeting_record | 会议纪要 |
| file_record    | 文件归档 |
| query          | 查询   |
| chat           | 普通聊天 |

---

# 优先级

```text
meeting_record
> task_record
> event_record
> file_record
> query
> chat
```

---

# task_record规则

触发关键词：

```text
负责
跟进
完成
整改
处理
落实
提交
安排
```

示例：

```text
王五负责入口整改
```

结果：

```json
{
  "intent":"task_record"
}
```

---

# event_record规则

触发关键词：

```text
记录一下
今天完成
现场情况
巡检发现
```

示例：

```text
记录一下，今天完成样板段放线
```

结果：

```json
{
  "intent":"event_record"
}
```

---

# meeting_record规则

触发关键词：

```text
会议纪要
会议记录
例会
专题会
评审会
```

示例：

```text
会议纪要：
...
```

结果：

```json
{
  "intent":"meeting_record"
}
```

---

# file_record规则

触发条件：

```text
上传文件
发送附件
上传图纸
上传照片
```

结果：

```json
{
  "intent":"file_record"
}
```

---

# query规则

触发关键词：

```text
查询
统计
多少
哪些
帮我查
帮我找
```

示例：

```text
未来城项目还有多少未完成任务
```

结果：

```json
{
  "intent":"query"
}
```

---

# chat规则

以上均不满足。

统一归类：

```json
{
  "intent":"chat"
}
```

---

# 项目识别规则（MVP）

第一优先：

消息中明确出现项目名称

```text
未来城
凤凰城
云栖府
```

直接匹配。

---

第二优先：

群绑定项目

```text
未来城项目群
→
未来城项目
```

---

第三优先：

用户最近活跃项目

最近7天交互最多项目。

---

第四优先：

无法识别

返回：

```json
{
  "project_id":null,
  "need_confirm":true
}
```

向用户询问项目归属。
