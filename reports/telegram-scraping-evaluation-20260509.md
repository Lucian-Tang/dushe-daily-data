# Telegram 消息采集方案评估

> 评估人：Stephen  
> 日期：2026-05-09  
> 背景：Boss 想自动采集 Telegram 频道/群组内容（技术新闻、创业灵感），无需手动转发

---

## 一、方案对比

### 方案 A：MTProto API（Telethon / Pyrogram）

| 维度 | 评分 | 说明 |
|------|------|------|
| 实现难度 | ★★★☆☆ | 中等。需注册 my.telegram.org 获取 api_id/api_hash，Python 写 Client 脚本，熟悉 asyncio。库生态成熟（Telethon 文档较好）。 |
| 功能完整性 | ★★★★★ | 最强。能读频道/群组/私聊消息，获取任意公开内容，支持消息过滤、关键词监听、长期运行。 |
| 稳定性 | ★★★☆☆ | 依赖 Telegram 官方服务器。MTProto 协议相对稳定，但官方可能调整 API 版本导致偶发兼容性问题。 |
| 反风控 | ★★☆☆☆ | 风险最高。使用真实用户身份爬取，高频访问容易被判定为机器人，IP + 行为双重检测。曾有批量封号案例。 |
| 合规性 | ★★★★☆ | 技术上不违规，但需遵守 Telegram ToS（不得用于大规模数据挖掘）。频道主可能开启隐私保护导致拉取失败。 |
| 维护成本 | ★★☆☆☆ | api_id/api_hash 泄露风险高；若 Telegram 变更协议或 API 版本需及时更新库。 |

**关键风险：** `api_id/api_hash` 是你在 my.telegram.org 注册应用时获得的凭证，等同于你的"身份证"。如果泄露，攻击者可以：
- 以你的身份发消息、加群
- 消耗你的 API 请求配额（有限额，超量收费）
- 导致账号被封

**建议：** 若决定使用，凭证必须存环境变量，绝不写入代码或日志。

---

### 方案 B：Telegram Bot API

| 维度 | 评分 | 说明 |
|------|------|------|
| 实现难度 | ★☆☆☆☆ | 最低。创建 Bot 简单（@BotFather），HTTP API 调用，无须注册开发者账号。 |
| 功能完整性 | ★★☆☆☆ | 受限极大。**Bot 无法主动读取群/频道消息**，只能响应被 @ 提及的消息，或通过 Webhook 接收转发给它的消息。 |
| 稳定性 | ★★★★★ | 最稳定。官方 Bot API 是最被支持的接口，不会因协议变更而失效。 |
| 反风控 | ★★★★★ | 无风险。Bot 是官方认可的合法接口。 |
| 合规性 | ★★★★★ | 完全合规。 |
| 维护成本 | ★★★★★ | 极低。 |

**结论：Bot 方案本身不能实现"自动采集频道内容"的需求**。它只适合"用户在群里 @ 你的 Bot，Bot 把消息转发给另一个群"这类场景（本质上还是手动触发）。

> **如果你想绕过这个限制：** 可以把 Bot 添加到频道做 Admin，它能获取频道消息。但这需要频道主授权，不适合采集他人频道。

---

### 方案 C：RSS 桥接（RSSHub / tgRSS）

| 维度 | 评分 | 说明 |
|------|------|------|
| 实现难度 | ★★☆☆☆ | 低。你们已有 RSSHub 部署（`/root/.openclaw/workspace/rsshub`），可扩展 Telegram 路由。 |
| 功能完整性 | ★★★☆☆ | 中等。RSSHub 的 Telegram 路由可将 Telegram 频道转为 RSS feed。但频道需开启"透过链接邀请"且允许 RSS 抓取。部分频道禁止 RSS 抓取。 |
| 稳定性 | ★★★☆☆ | 依赖频道是否允许 RSS。部分频道随时可能关闭，导致 feed 失效。RSSHub 本身维护良好。 |
| 反风控 | ★★★★☆ | 低风险。RSS 是标准协议，频道主无法直接区分是 RSS 抓取还是正常访问。 |
| 合规性 | ★★★★☆ | 符合 RSS 协议规范，不爬协议外内容。 |
| 维护成本 | ★★★☆☆ | 中等。RSSHub 需保持运行，路由配置需针对频道维护。 |

**已知限制：** 并非所有 Telegram 频道都支持 RSS——只有开启了"内容分享"权限的公开频道才能被 RSSHub 抓取。

---

## 二、VPS 可行性分析

### 当前 VPS 信息

```
IP: 170.106.75.214
地区: US（美国）
VPS: VM-0-14-ubuntu
```

### Telegram 连接风险评估

**好消息：**
- Telegram 在美国有多个数据中心，US IP 直连延迟较低
- US IP 对 Telegram 来说属于"正常地区"，不会被默认屏蔽

**风险点：**
- 之前 Reddit 被封，说明该 IP 段可能已被国内防火墙标记。若 Telegram 也封锁该 IP，则所有方案都无法工作
- 验证方式：在这台 VPS 上实际执行 `curl -s https://telegram.org` 或 `nc -zv telegram.org 443`，观察是否能连通

### 建议验证步骤（登录 VPS 后执行）

```bash
# 1. 检测 Telegram 域名是否可解析
nslookup telegram.org

# 2. 检测 443 端口是否可达
nc -zv telegram.org 443

# 3. 若上面失败，尝试 Telegram 的备用域名
nc -zv web.telegram.org 443

# 4. 若 MTProto 方案，测试 DC (数据中心) 连通性
nc -zv 149.154.167.220 443  # TG DC1
```

### VPS 连通性验证结果（实测）

```
DNS 解析: telegram.org → 149.154.167.99 ✓
443 端口: OPEN ✓（耗时 <1s）
```

**结论：VPS 可以直连 Telegram，三种方案在网络层面均可行。**

但需注意：这是单次检测结果，Telegram 在不同时间可能会切换到不同 IP 段（如 149.154.167.x 或 91.108.x.x），建议在业务高峰时段复测 2-3 次确认稳定性。

**若端口被封：**
- MTProto API 走 443/UDP 和 443/TCP，基本无法翻墙
- Bot API 走 HTTPS（标准 443），理论上可以通过 HTTP 代理绕行，但需要额外配置

---

## 三、推荐方案

### 首选：RSSHub Telegram 路由（方案 C）

**理由：**
1. 你们已经有 RSSHub 基础设施，改动最小
2. 无需申请任何凭证
3. 对频道主合规，风险最低
4. 可以和现有的 RSS 采集流程整合（sources.yaml → 行业日报）

**限制：** 只能采集**允许 RSS 的公开频道**，无法抓取私人群组/受限频道。

### 备选：Telethon MTProto（方案 A）

**前提条件：**
- 在 [my.telegram.org](https://my.telegram.org) 注册应用获取 `api_id` + `api_hash`
- 将凭证写入 `~/.bashrc` 或 `.env`，绝不硬编码

**适合场景：** 需要采集**不支持 RSS** 的频道内容，且愿意承担风控成本。

**Bot 方案（方案 B）** 不推荐用于自动采集——它无法满足核心需求。

---

## 四、PoC 脚本

### PoC 1: RSSHub Telegram 路由（已有基础，快速上线）

RSSHub 内置了 Telegram 频道 RSS 路由，使用方式：

```
https://rsshub.example.com/telegram/channel/{channel_username}
```

例如：
```
https://rsshub.example.com/telegram/channel/TelegramTips
```

**在你们现有架构下整合：**

```python
# scripts/fetch_telegram_rss.py
# 在现有日报流程中加入 Telegram RSS 信源

import feedparser
import httpx

TELEGRAM_RSS_CHANNELS = [
    "AI、科技、创业相关的公开频道 username（不含 @）",
]

def fetch_telegram_channel(channel_username: str) -> list[dict]:
    """通过 RSSHub 抓取 Telegram 频道内容"""
    rsshub_base = "http://localhost:1200"  # RSSHub 监听端口
    url = f"{rsshub_base}/telegram/channel/{channel_username}"
    feed = feedparser.parse(url)
    return [
        {
            "source": f"Telegram/{channel_username}",
            "title": entry.title,
            "url": entry.link,
            "summary": entry.get("summary", ""),
            "published": entry.get("published", ""),
        }
        for entry in feed.entries
    ]

def main():
    all_items = []
    for ch in TELEGRAM_RSS_CHANNELS:
        all_items.extend(fetch_telegram_channel(ch))
    print(f"Fetched {len(all_items)} items from Telegram channels")
    # 后续接入现有日报流程...
```

**启动 RSSHub（已在 `/root/.openclaw/workspace/rsshub`）：**

```bash
cd /root/.openclaw/workspace/rsshub
# npm install（已有 node_modules）
node ./node_modules/.bin/rsshub &
# 默认监听 localhost:1200
```

---

### PoC 2: Telethon MTProto（需要 api_id/api_hash）

```python
# scripts/telegram_scraper_telethon.py
# 依赖: pip install telethon python-dotenv httpx

import os
import asyncio
from datetime import datetime, timedelta
from telethon import TelegramClient
from telethon.tl.types import InputPeerChannel

# ============ 凭证管理（敏感）============
# 绝对禁止硬编码！从环境变量读取
API_ID = int(os.environ["TG_API_ID"])
API_HASH = os.environ["TG_API_HASH"]
SESSION_NAME = os.environ.get("TG_SESSION_NAME", "telegram_scraper")

# 监控的频道 username 列表（不含 @）
CHANNELS_TO_MONITOR = [
    "some_tech_channel",
    "startup_ideas_channel",
]


async def fetch_channel_messages(client: TelegramClient, channel_username: str, days_back: int = 7):
    """获取频道最近 N 天的消息"""
    try:
        entity = await client.get_entity(channel_username)
        messages = await client.get_messages(
            entity,
            limit=100,
            offset_date=datetime.now() - timedelta(days=days_back),
        )
        return [
            {
                "channel": channel_username,
                "date": msg.date.isoformat(),
                "text": msg.text or "",
                "views": msg.views,
            }
            for msg in messages if msg.text
        ]
    except Exception as e:
        print(f"[ERROR] Failed to fetch {channel_username}: {e}")
        return []


async def main():
    async with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
        all_items = []
        for ch in CHANNELS_TO_MONITOR:
            items = await fetch_channel_messages(client, ch)
            all_items.extend(items)
            print(f"Fetched {len(items)} from @{ch}")

        print(f"Total: {len(all_items)} items")
        # 后续接入现有日报流程...


if __name__ == "__main__":
    asyncio.run(main())
```

**环境变量配置：**
```bash
# 写入 ~/.bashrc 或 ~/.profile，绝不写入代码！
export TG_API_ID="12345678"
export TG_API_HASH="your_api_hash_here"
export TG_SESSION_NAME="lucian_telegram"
```

---

## 五、安全提醒

### MTProto api_id / api_hash 是高敏感凭证

```
风险场景：
1. 硬编码到 Git 仓库 → 泄露 → 攻击者以你的身份操作 Telegram
2. 写入日志文件 → 泄露
3. 通过不安全的网络传输 → 被中间人截获
```

**安全最佳实践：**
- [ ] 凭证只存在于环境变量或加密的 `.env` 文件
- [ ] `.env` 加入 `.gitignore`
- [ ] 定期轮换（在 my.telegram.org 注销旧应用，重建新应用）
- [ ] 不要在多台机器共用同一组凭证
- [ ] 为该应用设置最低权限（在 my.telegram.org 可配置）

### RSSHub Telegram 路由的隐私说明

RSSHub 抓取 Telegram 频道时，Telegram 服务器会记录请求来自你的 VPS IP。这是正常行为，但：
- 频道主可以通过 Telegram 后台看到有人通过 RSS 订阅了他们的内容
- 部分频道主会因此关闭 RSS 功能

---

## 六、行动建议

| 优先级 | 动作 | 状态 |
|--------|------|------|
| P0 | 在 VPS 上测试 Telegram 连通性 | 待验证 |
| P1 | 部署 RSSHub Telegram 路由，配置监控频道列表 | 待实施 |
| P2 | 若 RSSHub 覆盖不够，评估 Telethon 方案并注册 my.telegram.org | 视情况 |
| P3 | 将 Telegram 内容整合进现有 sources.yaml 日报流程 | 后续迭代 |

---

## 附录：验证命令速查

```bash
# VPS 上检测 Telegram 连通性
nslookup telegram.org
nc -zv telegram.org 443
curl -sI https://telegram.org

# 查看 RSSHub 路由是否支持 Telegram
curl "http://localhost:1200/telegram/channel/test" 2>&1 | head -20

# 检查 RSSHub 进程是否在运行
ps aux | grep rsshub
```