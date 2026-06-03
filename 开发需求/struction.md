# AstrBot 核心模块项目结构文档
## 项目简介
AstrBot 是一款高度可扩展的开源AI聊天机器人框架，支持多消息平台接入、多LLM厂商适配、插件扩展、工具调用、知识库、子代理编排等丰富能力，专注于私有化部署场景和二次开发需求。

## 快速导航
- [WebUI后台模块](#dashboard-webui后台服务模块)
- [核心业务模块](#core-系统核心业务逻辑模块)
  - [通用工具集](#coreutils-核心通用工具集目录)
  - [内置工具集](#coretools-内置工具集目录)
  - [Star插件体系](#corestar-star插件体系核心模块)
  - [技能体系](#coreskills-技能体系模块)
  - [第三方服务适配](#coreprovider-第三方服务提供商适配模块)
  - [系统配置模块](#coreconfig-系统配置模块)
  - [本地计算机操作模块](#corecomputer-本地计算机操作能力模块)
- [整体架构说明](#整体架构设计)
- [核心特性与模块映射](#核心特性与模块映射关系)
- [模块调用关系](#模块调用关系说明)

---

## 项目结构
astrbot/
├── __init__.py # Python包初始化文件
├── utils/ # 通用工具模块
│   ├── __init__.py
│   └── http_ssl_common.py # HTTP SSL证书通用配置工具
├── dashboard/ # WebUI后台服务模块
│   ├── utils.py # 后台通用工具函数
│   ├── server.py # Web服务启动主入口
│   ├── plugin_page_bridge.js # 插件页前后端桥接脚本
│   ├── plugin_page_auth.py # 插件页权限验证逻辑
│   ├── password_state.py # 登录密码状态管理器
│   └── routes/ # 所有API路由实现目录
│       ├── __init__.py
│       ├── auth.py # 身份验证API
│       ├── config.py # 系统配置管理API
│       ├── chat.py # 聊天核心API
│       ├── conversation.py # 对话记录管理API
│       ├── file.py # 文件操作API
│       ├── knowledge_base.py # 知识库管理API
│       ├── log.py # 日志查询API
│       ├── plugin.py # 插件管理API
│       ├── platform.py # 消息平台适配器管理API
│       ├── persona.py # 角色设定管理API
│       ├── cron.py # 定时任务管理API
│       ├── skills.py # 技能管理API
│       ├── subagent.py # 子代理编排API
│       ├── t2i.py # 文本转图片API
│       ├── update.py # 系统更新相关API
│       ├── open_api.py # 对外开放API
│       └── api_key.py # API密钥管理API
└── core/ # 系统核心业务逻辑模块
    ├── __init__.py
    ├── core_lifecycle.py # 核心生命周期管理器（启动/停止/重载）
    ├── conversation_mgr.py # 全局对话会话管理器
    ├── updator.py # 系统更新核心逻辑
    ├── zip_updator.py # ZIP格式包更新器
    ├── umop_config_router.py # 配置变更路由分发器
    ├── subagent_orchestrator.py # 多子代理任务编排器
    ├── sentinels.py # 系统运行状态哨兵监控模块
    ├── utils/ # 核心通用工具集目录
    │   ├── path_util.py # 系统路径处理工具
    │   ├── command_parser.py # 用户命令解析器
    │   ├── pip_installer.py # Python依赖自动安装器
    │   ├── network_utils.py # 网络请求工具
    │   ├── datetime_utils.py # 日期时间处理工具
    │   ├── error_redaction.py # 错误信息敏感内容脱敏工具
    │   ├── history_saver.py # 对话历史持久化工具
    │   ├── media_utils.py # 音视频/图片处理工具
    │   ├── metrics.py # 系统运行指标统计工具
    │   ├── plugin_kv_store.py # 插件专属KV存储工具
    │   ├── t2i/ # 文本转图片渲染子模块
    │   │   ├── renderer.py # 渲染核心
    │   │   ├── template_manager.py # 渲染模板管理器
    │   │   ├── local_strategy.py # 本地渲染策略
    │   │   └── network_strategy.py # 网络渲染策略
    │   └── quoted_message/ # 引用消息解析子模块
    │       ├── extractor.py # 引用内容提取器
    │       ├── image_resolver.py # 引用图片解析器
    │       └── onebot_client.py # OneBot协议引用消息客户端
    ├── tools/ # 内置工具集目录
    │   ├── web_search_tools.py # 网页搜索工具
    │   ├── knowledge_base_tools.py # 知识库操作工具
    │   ├── message_tools.py # 消息处理工具
    │   ├── cron_tools.py # 定时任务操作工具
    │   ├── registry.py # 工具注册中心
    │   └── computer_tools/ # 计算机操作工具集
    │       ├── shell.py # Shell命令执行工具
    │       ├── python.py # Python代码执行工具
    │       ├── fs.py # 文件系统操作工具
    │       └── browser.py # 浏览器操作工具
    ├── star/ # Star插件体系核心模块
    │   ├── README.md # Star插件开发文档
    │   ├── base.py # Star插件基类
    │   ├── config.py # Star配置管理器
    │   ├── context.py # Star运行上下文
    │   ├── star_manager.py # Star插件全局管理器
    │   ├── session_plugin_manager.py # 会话级插件管理器
    │   ├── session_llm_manager.py # 会话级LLM管理器
    │   ├── command_management.py # 自定义命令管理器
    │   ├── filter/ # 消息过滤器集合
    │   │   ├── command.py # 命令过滤器
    │   │   ├── permission.py # 权限过滤器
    │   │   ├── regex.py # 正则过滤器
    │   │   └── platform_adapter_type.py # 平台类型过滤器
    │   └── register/ # Star组件注册器
    ├── skills/ # 技能体系模块
    │   ├── skill_manager.py # 技能全局管理器
    │   └── neo_skill_sync.py # Neo技能仓库同步器
    ├── provider/ # 第三方服务提供商适配模块
    │   ├── provider.py # 所有提供商基类
    │   ├── register.py # 提供商注册中心
    │   └── sources/ # 各厂商实现目录
    │       ├── openai_source.py # OpenAI LLM适配
    │       ├── gemini_source.py # Google Gemini LLM适配
    │       ├── anthropic_source.py # Claude LLM适配
    │       ├── zhipu_source.py # 智谱清言LLM适配
    │       ├── groq_source.py # Groq LLM适配
    │       ├── edge_tts_source.py # 微软Edge TTS适配
    │       ├── openai_tts_api_source.py # OpenAI TTS适配
    │       ├── whisper_api_source.py # Whisper语音转文字适配
    │       └── openai_embedding_source.py # OpenAI向量嵌入适配
    ├── config/ # 系统配置模块
    │   ├── astrbot_config.py # 核心配置类
    │   ├── default.py # 系统默认配置
    │   └── i18n_utils.py # 国际化工具
    └── computer/ # 本地计算机操作能力模块
        ├── computer_client.py # 计算机操作统一客户端
        ├── olayer/ # 操作抽象层
        │   ├── shell.py # Shell操作抽象层
        │   ├── filesystem.py # 文件系统操作抽象层
        │   ├── browser.py # 浏览器操作抽象层
        │   └── python.py # Python代码执行抽象层
        └── booters/ # 运行环境启动器
            ├── local.py # 本地环境启动器
            ├── shipyard.py # Shipyard容器环境启动器
            ├── shell_background.py # 后台Shell启动器
            └── base.py # 启动器基类

---

## 整体架构设计
AstrBot 采用经典的四层分层架构，严格遵循单一职责原则：
1. **接入层** (`dashboard/`)：负责所有外部请求接入，包括WebUI交互、API调用、第三方平台消息推送，是系统对外的唯一入口
2. **业务编排层** (`core/star/`/`core/subagent_orchestrator.py`)：负责核心业务逻辑编排，包括消息路由、插件执行、多代理协作、任务调度，是系统的大脑
3. **能力支撑层** (`core/provider/`/`core/tools/`/`core/computer/`)：封装所有底层能力，包括LLM调用、工具执行、本地操作、知识库查询，是系统的能力底座
4. **通用基础层** (`core/utils/`/`utils/`/`core/config/`)：提供所有通用工具、配置管理、常量定义，供上层所有模块调用

---
## 核心特性与模块映射关系
| 核心特性 | 对应负责模块 | 说明 |
|---------|-------------|------|
| 多平台消息接入 | `dashboard/routes/platform.py` + `core/star/filter/platform_adapter_type.py` | 支持OneBot v11/v12、微信、QQ、Discord等多平台适配器 |
| 多LLM厂商适配 | `core/provider/` | 支持OpenAI、Gemini、Claude、智谱、通义千问等20+厂商LLM/embedding/TTS/STT服务 |
| 插件扩展能力 | `core/star/` | 支持自定义Star插件，可扩展消息处理逻辑、自定义命令、事件监听 |
| 工具调用能力 | `core/tools/` | 内置网页搜索、文件操作、Shell执行、代码运行、浏览器操作等10+内置工具 |
| 知识库能力 | `core/tools/knowledge_base_tools.py` + `dashboard/routes/knowledge_base.py` | 支持本地文件知识库、向量检索、文档问答 |
| 多代理编排 | `core/subagent_orchestrator.py` + `dashboard/routes/subagent.py` | 支持多个子代理分工协作，处理复杂任务 |
| 定时任务 | `core/tools/cron_tools.py` + `dashboard/routes/cron.py` | 支持自定义定时触发任务，定期推送消息、执行操作 |
| 文本转图片渲染 | `core/utils/t2i/` + `dashboard/routes/t2i.py` | 支持代码块、Markdown内容转美观图片输出 |
| Web管理后台 | `dashboard/` | 提供可视化配置、对话管理、插件管理、日志查看等能力 |

---
## 模块调用关系说明
### 标准消息处理流程：
1. 消息入口：用户消息从消息平台适配器/`dashboard/routes/chat.py` 进入系统
2. 路由分发：`core/star/star_manager.py` 接收消息，经过`core/star/filter/` 过滤器链匹配
3. 业务处理：匹配到的Star插件/核心响应逻辑执行，根据需要调用`core/tools/` 工具或`core/provider/` LLM服务
4. 结果返回：处理结果经 `dashboard/` 返回给用户端，同时`core/utils/history_saver.py` 持久化对话历史

### 通用调用规则：
- 上层模块可以调用下层模块，禁止反向调用（比如dashboard可以调用core的任何模块，core的模块不能调用dashboard的接口）
- 同层级模块之间可以互相调用（比如star模块可以调用provider、tools模块）
- 所有模块都可以调用utils层的通用工具函数，禁止utils层调用任何上层业务模块