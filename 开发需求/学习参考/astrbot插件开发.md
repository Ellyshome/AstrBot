
# AstrBot 透明代理插件方案

## 插件功能设计

| 功能 | 实现方式 |
|------|---------|
| **上行（IM → 你的服务）** | 监听所有消息，通过 Webhook POST 到你的服务 |
| **下行（你的服务 → IM）** | 插件提供 HTTP API，接收你的请求并发到 IM |
| **双向透传** | 保持原始消息结构 |

---

## 完整插件代码

创建文件：`data/extensions/astrbot_transparent_plugin/__init__.py`

```python
import asyncio
import json
from typing import Any

import aiohttp
from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, MessageChain
from astrbot.api.platform import AstrBotMessage, MessageType
from astrbot.api.star import Star, register
from astrbot.core.star.register import register_web_api
from quart import request, jsonify


class TransparentProxyPlugin(Star):
    """AstrBot 透明代理插件 - 上下行消息透传"""
    
    def __init__(self):
        super().__init__()
        
        # 配置
        self.webhook_url = "http://your-service:port/webhook/message"  # 你的接收地址
        self.api_path = "/transparent-proxy/send"  # 下行 API 路径
        
        # HTTP Session
        self._session: aiohttp.ClientSession | None = None
    
    async def _get_session(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def _forward_to_webhook(self, message: AstrBotMessage):
        """上行：转发 IM 消息到你的服务"""
        
        try:
            session = await self._get_session()
            
            # 构建透传数据
            payload = {
                "type": "message",
                "direction": "up",  # 上行：IM -&gt; 你的服务
                "platform": message.platform_name,
                "message_id": message.message_id,
                "timestamp": message.timestamp,
                "sender": {
                    "id": message.sender.user_id,
                    "name": message.sender.user_name,
                    "role": str(message.sender.role)
                },
                "session": {
                    "is_group": message.is_group(),
                    "group_id": message.group_id,
                    "umo": str(message.session)  # 关键：UMO 用于下行回复
                },
                "message_str": message.message_str,
                "message_obj": message.to_dict() if hasattr(message, "to_dict") else None,
                "raw_message": message.raw_message
            }
            
            # 异步发送，不阻塞 AstrBot 处理
            async with session.post(
                self.webhook_url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ):
                pass
                
        except Exception as e:
            logger.warning(f"[透传插件] 上行转发失败: {e}")
    
    @register()
    async def on_message(self, event: AstrMessageEvent):
        """监听所有消息"""
        
        try:
            # 转发给你的服务
            asyncio.create_task(self._forward_to_webhook(event.message_obj))
        except Exception as e:
            logger.error(f"[透传插件] 处理消息失败: {e}")
        
        # 继续让 AstrBot 处理（可选，如果不需要 AstrBot 自己回复，可以返回 event.stop()）
        return event.continue_()
    
    @register_web_api("/transparent-proxy/send", methods=["POST"])
    async def api_send_message(self):
        """下行 API：你的服务调用这个接口发消息到 IM"""
        
        try:
            data = await request.get_json()
            
            # 必填字段
            umo = data.get("umo")
            if not umo:
                return jsonify({
                    "success": False,
                    "error": "缺少 umo 参数（Unified Message Object）"
                }), 400
            
            message_content = data.get("message")
            if not message_content:
                return jsonify({
                    "success": False,
                    "error": "缺少 message 参数"
                }), 400
            
            # 解析 UMO 获取 Session
            from astrbot.core.platform.astr_message_event import MessageSesion
            session = MessageSesion.from_str(umo)
            
            # 构建消息链
            chain = MessageChain()
            if isinstance(message_content, str):
                from astrbot.api.message_components import Plain
                chain.append(Plain(message_content))
            else:
                # 支持消息段数组格式
                # TODO: 完善消息段解析
                pass
            
            # 获取平台适配器并发送
            platform = self.get_context().platform_manager.get_platform_by_name(session.platform_name)
            if not platform:
                return jsonify({
                    "success": False,
                    "error": f"找不到平台适配器: {session.platform_name}"
                }), 404
            
            await platform.send_by_session(session, chain)
            
            return jsonify({
                "success": True,
                "umo": umo
            })
            
        except Exception as e:
            logger.error(f"[透传插件] 下行发送失败: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @register_web_api("/transparent-proxy/status", methods=["GET"])
    async def api_status(self):
        """健康检查 API"""
        return jsonify({
            "status": "ok",
            "plugin": "transparent-proxy"
        })
    
    async def terminate(self):
        if self._session and not self._session.closed:
            await self._session.close()
```

---

## 你的服务端示例（Python + FastAPI）

你需要一个服务来接收上行消息和发送下行消息：

```python
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import httpx

app = FastAPI()

# AstrBot 的地址（Docker 内部用服务名）
ASTRBOT_URL = "http://astrbot:6185"


class DownstreamMessage(BaseModel):
    umo: str  # 从上行消息获取的 UMO
    message: str


@app.post("/webhook/message")
async def receive_upstream(request: Request):
    """接收 AstrBot 转发的 IM 消息"""
    data = await request.json()
    
    print(f"收到来自 {data['platform']} 的消息:")
    print(f"发送者: {data['sender']}")
    print(f"内容: {data['message_str']}")
    print(f"回复用的 UMO: {data['session']['umo']}")
    
    return {"status": "ok"}


@app.post("/send-message")
async def send_downstream(msg: DownstreamMessage):
    """通过 AstrBot 发送消息到 IM"""
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{ASTRBOT_URL}/api/plug/transparent-proxy/send",
                json={
                    "umo": msg.umo,
                    "message": msg.message
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## Docker Compose 集成

修改 `docker-compose-napcat.yml`，加入你的服务：

```yaml
services:
  napcat:
    # ... 原有配置 ...
    networks:
      - astrbot_network

  astrbot:
    # ... 原有配置 ...
    networks:
      - astrbot_network

  # 新增你的服务
  your-service:
    image: python:3.12-slim
    container_name: your-service
    restart: always
    volumes:
      - ./your-service-code:/app
    working_dir: /app
    command: bash -c "pip install fastapi uvicorn httpx &amp;&amp; python main.py"
    ports:
      - "8000:8000"  # 可选：如果需要从主机访问
    networks:
      - astrbot_network

networks:
  astrbot_network:
    driver: bridge
```

---

## 完整流程演示

### 1️⃣ 上行（用户 → QQ → NapCat → AstrBot → 你的服务）

```
用户 QQ: "你好"
    ↓
NapCat 收到
    ↓
OneBot WebSocket 发给 AstrBot
    ↓
透传插件 on_message 触发
    ↓
POST 到 http://your-service:8000/webhook/message
    ↓
你的服务收到：
{
    "type": "message",
    "direction": "up",
    "platform": "aiocqhttp",
    "session": {
        "umo": "aiocqhttp:GroupMessage:123456_7890123"
    },
    "message_str": "你好"
}
```

### 2️⃣ 下行（你的服务 → AstrBot → NapCat → QQ → 用户）

```
你的服务调用：
POST http://astrbot:6185/api/plug/transparent-proxy/send
{
    "umo": "aiocqhttp:GroupMessage:123456_7890123",
    "message": "我收到了！"
}
    ↓
透传插件 API 接收
    ↓
调用平台适配器发送
    ↓
AstrBot → NapCat → QQ
    ↓
用户收到回复
```

---

## 关键概念：UMO（Unified Message Object）

注意看 `umo` 字段，格式类似：
```
aiocqhttp:GroupMessage:123456_7890123
 平台名    消息类型    会话ID
```

**UMO 是双向通信的关键**：
- 上行时，AstrBot 把 UMO 给你
- 下行时，你用这个 UMO 告诉 AstrBot 往哪发

---

## 通信架构回顾

```
┌───────────────┐        WebSocket        ┌───────────────┐
│   NapCatQQ    │  (反向连接)  ──────────&gt; │    AstrBot    │
│  (QQ 客户端)  │                           │  (机器人框架) │
│               │                           │               │
│  - 连接 QQ    │                           │  - 接收消息   │
│  - OneBot V11 │                           │  - 处理消息   │
│  - 作为 Client│                           │  - 作为 Server│
└───────────────┘                           └───────────────┘
                                              │
                                              │ 插件
                                              ↓
                                    ┌───────────────┐
                                    │  你的服务    │
                                    │ (中间层业务) │
                                    └───────────────┘
```

