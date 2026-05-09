# xiaohongshu-cli Pilot Report — social-news-daily Integration

**日期**: 2026-05-09
**工程师**: Stephen
**背景**: 已在 `reports/xiaohongshu-cli-evaluation-20260509.md` 评分 4/4，本次试点验证 VPS 环境实际可用性。

---

## 1. 安装验证

| 步骤 | 结果 | 说明 |
|------|------|------|
| `uv tool install` | ❌ 不可用 | VPS 无 `uv` |
| `pip3 install` 系统级 | ❌ PEP 668 限制 | `--break-system-packages` 有风险 |
| `python3 -m venv` + pip | ✅ 成功 | 虚拟环境方案可用 |
| 依赖安装 | ✅ 成功 | camoufox/playwright 等全部装完 |

**推荐安装命令**:
```bash
python3 -m venv /root/.openclaw/workspace/venv-xhs
/root/.openclaw/workspace/venv-xhs/bin/pip install xiaohongshu-cli
# 执行时用 /root/.openclaw/workspace/venv-xhs/bin/xhs
```

---

## 2. CLI 功能验证

| 命令 | 结果 | 说明 |
|------|------|------|
| `xhs --help` | ✅ | 完整命令列表 |
| `xhs search "AI"` | ❌ 无 Cookie | `not_authenticated: No 'a1' cookie found` |
| `xhs hot -c food` | ❌ 无 Cookie | 同上 |
| `xhs feed` | ❌ 无 Cookie | 同上 |
| `xhs status` | ❌ 无 Cookie | 返回 `ok: false` + 错误信息 |
| `xhs login --qrcode` | ⚠️ HTTP 流程可启动 | 纯 Python 生成 QR URL，但无法完成扫码（需人工） |

---

## 3. Cookie 提取验证（核心问题）

### 3.1 浏览器 Cookie 自动提取

| 测试 | 结果 | 说明 |
|------|------|------|
| `browser-cookie3` 模块加载 | ✅ 装上了 | 但 VPS 无浏览器 |
| 系统 Chromium/Chrome | ❌ 不存在 | `dpkg` 无相关包 |
| 其他浏览器 | ❌ 不存在 | 无任何图形浏览器 |

**结论**: VPS 环境无法自动从浏览器提取 Cookie，这是主要障碍。

### 3.2 QR 码登录

`xhs login --qrcode` 有两种后端：

1. **Browser-assisted** (首选): 用 Camoufox 浏览器模拟真实扫码 → ❌ 不可用（无浏览器）
2. **Pure HTTP** (兜底): 用 `httpx` 直接调 QR API，QR 内容输出到终端 → ✅ 技术上可启动

HTTP QR 流程测试（成功）:
```
a1=d9dc050d57abbd3c6430..., webid=594d448d9f62e361a6b50daed7dbbda8
QR created: 49881778257732806 https://www.xiaohongshu.com/mobile/login?qrId=49881778257732806...
```

**瓶颈**: 扫码需要人工用小红书 App 扫描，VPS 无法自动化完成。

### 3.3 Cookie 结构（用于手动配置）

Cookie 文件在 `~/.xiaohongshu-cli/cookies.json`，格式：
```json
{
  "a1": "52-char-hex-device-id",
  "webId": "32-char-hex",
  "web_session": "session-token",
  "web_session_sec": "secure-session-token",
  "saved_at": 1778257747.5
}
```

**TTL**: 7 天，过期后 `xhs` 自动尝试从浏览器刷新（但这在 VPS 上也会失败）。

---

## 4. 集成方案分析

### 方案 A: 手动 Cookie 预配置（可行，推荐）

1. 在有浏览器的本地机器上运行 `xhs login`（或 `xhs login --qrcode` 扫码）
2. 复制 `~/.xiaohongshu-cli/cookies.json` 到 VPS 的相同路径
3. 脚本直接用 `xhs search/hot/feed --json` 读数据
4. 每 6 天重新手动刷新

**优点**: 最简单，绕开所有认证技术障碍
**缺点**: 需要人工定期维护，Cookie 过期有窗口期

### 方案 B: 改造 CLI 直接注入 Cookie（技术可行）

通过 Python 代码直接调用 `XhsClient`，注入 Cookie：
```python
from xhs_cli.client import XhsClient
cookies = {"a1": "...", "webId": "...", "web_session": "...", "web_session_sec": "..."}
with XhsClient(cookies) as client:
    result = client.search_notes("AI", sort="popular")
```
→ 绕过 CLI 的 `browser-cookie3` 自动提取逻辑，直接用已有的 Cookie。

### 方案 C: 模拟完整 HTTP QR 登录（不可行）

纯 HTTP QR 登录理论上可以自动化：
1. 调用 `/api/sns/web/v1/login/qrcode/create` 获取 QR
2. 调用 `/api/sns/web/v1/login/qrcode/status` 查询扫码状态

但状态查询需要**人工用小红书 App 扫描**，无法在无人值守的 VPS 上完成。

---

## 5. 推荐集成路径

```
social-news-daily 接入小红书（只读采集）
├── Phase 1: 手动 Cookie 方式（立即可做）
│   ├── 在本地机器登录 xhs，导出 cookies.json
│   ├── 上传至 VPS 路径 ~/.xiaohongshu-cli/cookies.json
│   └── 写 cron/scripts/xiaohongshu_signals.py 调用 xhs CLI
│
└── Phase 2: 7 天 Cookie 刷新机制（需人工介入）
    ├── 设置日历提醒：每 6 天重新导出 Cookie
    └── 或在飞书机器人加一个"刷新小红书 Cookie"指令
```

**Cookie 刷新频率**: 每 6 天（TTL 7 天，提前 1 天刷新）

---

## 6. 集成脚本设计

`cron/scripts/xiaohongshu_signals.py`:

- 调用 `/root/.openclaw/workspace/venv-xhs/bin/xhs search/hot/feed --json`
- 解析 YAML/JSON 输出（`xhs` 在非 TTY 时默认输出 YAML，`--json` 显式指定）
- 过滤关键词（AI/创业/工具/开源等）
- 评分（engagement + recency + keyword match）
- 写入 `data/opportunities/xiaohongshu/{YYYY-MM}.json`
- 写入 Feishu Bitable

**输出字段映射**:
| XHS 字段 | 输出字段 |
|---------|---------|
| `note.display_title` | `title` |
| `note.interact_info.liked_count` | `engagement` |
| `note.image_list[0].urlDefault` | `image_url` |
| `note.user.nickname` | `author` |
| `note.note_id` | `note_id` |
| `note.url` | `url` |

---

## 7. cron 注册参数

待 Cookie 手动配置好后，可用以下参数注册 cron：

```bash
# 每天 09:00 / 15:00 采集小红书信号
0 9,15 * * * /root/.openclaw/workspace/cron/scripts/xiaohongshu_signals.py >> /root/.openclaw/workspace/logs/xiaohongshu-cron.log 2>&1

# 环境
XHS_BINARY=/root/.openclaw/workspace/venv-xhs/bin/xhs
XHS_DATA_DIR=/root/.openclaw/workspace/data/opportunities/xiaohongshu
```

---

## 8. 风险记录

| 风险 | 等级 | 说明 |
|------|------|------|
| Cookie 过期无法自动刷新 | 🔴 高 | VPS 无浏览器，需人工介入 |
| XHS API 签名变更 | 🔴 高 | 签名算法变 → 全量失效 |
| IP 被封 | 🟡 中 | 高频采集触发封禁，需控制频率 |
| 法律风险 | 🟡 中 | 逆向 API，灰色地带（见评估报告 7.3） |
| QR 登录无法自动化 | 🟡 中 | 扫码必须人工，无法无人值守 |

---

## 9. 下一步行动

- [ ] **Lucian 手动操作**: 在有浏览器的设备上运行 `xhs login`，将 `~/.xiaohongshu-cli/cookies.json` 内容发给我，我写入 VPS
- [ ] Cookie 写入后，运行一次 `xhs status` 验证
- [ ] 确认后写完整 `xiaohongshu_signals.py`
- [ ] 注册 cron job

---

## 附录：cron 注册参数

```bash
# ---- Cron 注册命令 ----
# 环境变量
export XHS_BINARY=/root/.openclaw/workspace/venv-xhs/bin/xhs
export XHS_KEYWORDS="AI,LLM,大模型,创业,工具,开源,SaaS"
export XHS_DATA_DIR=/root/.openclaw/workspace/data/opportunities/xiaohongshu

# 每天 09:00 和 15:00 采集
0 9,15 * * * /root/.openclaw/workspace/cron/scripts/xiaohongshu_signals.py >> /root/.openclaw/workspace/logs/xiaohongshu-cron.log 2>&1

# 独立测试（无需 cron）
XHS_BINARY=/root/.openclaw/workspace/venv-xhs/bin/xhs python3 /root/.openclaw/workspace/cron/scripts/xiaohongshu_signals.py
```

**Cookie 刷新提醒**: 每 6 天需要重新从浏览器导出 Cookie 并更新 `~/.xiaohongshu-cli/cookies.json`。
设置日历提醒提前 1 天触发。

---

*Stephen | 2026-05-09*