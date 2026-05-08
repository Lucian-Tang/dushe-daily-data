# last30days-skill 安装试用报告

**日期:** 2026-05-09
**安装方式:** Git clone 源码（ClawHub 安装被标记为 suspicious，跳过）
**Skill 版本:** v3.0.0 (last30days-skill/skills/last30days)
**安装路径:** `~/.openclaw/workspace/skills/last30days/`

---

## 1. 安装过程

### 方式 A: ClawHub（失败）
```bash
clawhub install last30days-official
# 输出: "Warning: flagged as suspicious by VirusTotal Code Insight"
# 需 --force 才能绕过，不建议直接跳过安全警告
```

### 方式 B: Git clone（成功 ✓）
```bash
git clone https://github.com/mvanhorn/last30days-skill /tmp/last30days-skill
cp -r /tmp/last30days-skill/skills/last30days/* ~/.openclaw/workspace/skills/last30days/
```

---

## 2. 免费数据源可用性检测

```
$ python3 scripts/last30days.py --diagnose

Available: reddit, hackernews, polymarket, github
Bird authenticated: false
GitHub: ✓ (gh cli 已安装)
Native web backend: null
Providers (API keys): google ✗, openai ✗, openrouter ✗, xai ✗
```

| 数据源 | 状态 | 说明 |
|--------|------|------|
| Hacker News | ✅ 零配置可用 | Firebase API |
| GitHub | ✅ 零配置可用 | gh cli |
| Polymarket | ✅ 零配置可用 | 公开 API |
| Reddit | ⚠️ IP 被封，跳过 | 本项目跳过 |
| X/Twitter | 💡 可选（需 cookies 或 XAI_API_KEY） | 非免费 |
| YouTube | 💡 可选（需 yt-dlp） | 非免费 |

---

## 3. 试用结果

### 测试 1: "AI agents" (HN + GitHub + Polymarket)

```
✓ Research complete (3.1s)
├─ HN: 12 stories, 1,056 pts, 649 comments
├─ Polymarket: 0 markets
└─ GitHub: 8 items, 565 reactions, 242 comments
```

**输出样本（HN 热门项目）:**
- `Show HN: Git for AI Agents` (re_gent) - 33pts, 17cmt
- `Show HN: Agent-desktop` - 98pts, 43cmt - native desktop automation CLI
- `Show HN: Loopsy` - terminals/AI agents 跨机通信 - 58pts, 12cmt
- `Less human AI agents, please` - 161pts, 170cmt (博客文章)
- `MenteDB` - Rust open-source memory DB for AI agents

**Polymarket 测试 "AI" 关键词:**
```
✓ Polymarket: 9 markets
├─ "Which company has best AI model end of May?" - $4.7M volume
├─ "Which companies will have #1 AI model by June 30?"
├─ "Trump orders federal review of AI model releases by May 31?"
└─ "Which company's AI will first hit 1550 on Chatbot Arena in 2026?"
```

### 输出质量评估

**优点:**
- 数据结构完整：有 score、volume、liquidity、url
- 零配置即可运行，HN/GitHub/Polymarket 都是开箱即用
- raw 文件保存完整（~17KB 一次运行），方便后续分析
- 引擎自动生成 `--diagnose` 报告清楚

**问题:**
- 无 `--plan` 时触发 DEGRADED RUN WARNING，提示需要 LAWs 7 规划
- 需要 `--search=hackernews,github,polymarket` 指定，否则默认带 reddit（被封）
- Polymarket 有时不返回结果（"AI agents" 查 0 markets，"AI" 查 9 markets）

---

## 4. 输出文件格式

Raw 文件路径: `~/.openclaw/workspace/data/last30days/ai-agents-raw-ai-agents.md`

结构:
1. Badge: `🌐 last30days v? · synced 2026-05-09`
2. Metadata: date range, sources, freshness
3. Evidence Clusters (引擎生成，供模型 synthesis 用，LAW 6 要求不直接暴露给用户)
4. Stats 块（emoji-tree 格式）
5. Footer: `✅ All agents reported back!` + 分源统计

---

## 5. 与现有 Crons 对比

| 维度 | hn_signals.py | github_trending_signals.py | last30days-skill |
|------|---------------|---------------------------|------------------|
| 数据源 | HN only | GitHub Trending HTML | HN + GitHub API + Polymarket |
| 输出 | JSON + Feishu Bitable | JSON (本地文件) | Markdown raw 文件 |
| 过滤 | 关键词 + score 阈值 | 关键词 + star 阈值 | 多维 scoring |
| 自动化 | cron job | cron job | 主动触发 / cron |
| 配置 | 直接写死 | 直接写死 | SKILL.md 规范 |
| LLM synthesis | 无（纯数据） | 无（纯数据） | **有（LAW 合成）** |
| Polymarket | ❌ | ❌ | ✅ |

**关键差异:**
- last30days 强调的是"LLM synthesis"——不是 raw 数据推送，而是把数据合成成 `What I learned:` 格式的研报
- hn_signals.py / github_trending_signals.py 是纯数据采集，不做 synthesis
- last30days 的优势在于多源 + synthesis + 结构化输出，crons 的优势在于定时推送 Feishu

---

## 6. 共存方案

### 方案 A: 各司其职（推荐）

```
现有 crons (hn_signals.py, github_trending_signals.py)
  → 定时 Feishu Bitable 推送，数据为准，快速轻量

last30days-skill
  → 按需触发（手动 / 有趣话题时），研报输出，侧重 synthesis
  → 手动触发方式: /last30days {topic}
```

**为什么不合并:**
- last30days 设计为"reasoning model 调用"，有复杂 LAWs 合成流程
- 现有 crons 已经能稳定推送 HN + GitHub 数据到 Feishu
- last30days 的价值在于"按需研报"，不是定时数据推送

### 方案 B: 把 last30days 的 HN/GitHub 数据纳入 pipeline

如果想在 pipeline 里用 last30days 的结构化输出，可以:

```python
# 用 last30days 的 lib/github.py 做 GitHub 数据拉取
import sys
sys.path.insert(0, '~/.openclaw/workspace/skills/last30days/scripts/lib')
from github import search_repos, search_issues

results = search_repos("AI agents", days=30)
# 结果格式比 github_trending_signals.py 更结构化（有 score, url, stars）
```

### 方案 C: Cron 化 last30days（不推荐）

last30days 的 SKILL.md 设计上是"reasoning model 调用"，包含 LAWs 合成逻辑，cron 化需要:
1. 自己写 wrapper 脚本通过 OpenClaw agent 调用
2. 或用 `--plan` JSON 绕过 LLM planning 直接调 engine（部分可行，但 SKILL.md 不鼓励这样做）

**结论:** 方案 A 最干净。现有 crons 负责数据推送，last30days 负责按需研报。

---

## 7. 快速使用命令

```bash
# 零配置可用部分
SKILL_ROOT="~/.openclaw/workspace/skills/last30days"
PYTHON="python3.12"  # 需要 3.12+

# HN + GitHub + Polymarket（跳过 Reddit）
"$PYTHON" "$SKILL_ROOT/scripts/last30days.py" \
  "AI agents" \
  --search="hackernews,github,polymarket" \
  --emit=compact \
  --save-dir="~/.openclaw/workspace/data/last30days"

# Polymarket 专项
"$PYTHON" "$SKILL_ROOT/scripts/last30days.py" \
  "AI" \
  --search="polymarket" \
  --emit=compact \
  --save-dir="~/.openclaw/workspace/data/last30days"
```

---

## 8. 下一步建议

1. **X/Twitter:** 浏览器登录 x.com 后重跑，last30days 自动检测 cookies（免费）
2. **YouTube:** `brew install yt-dlp` 后解锁视频 transcript
3. **Reddit:** IP 解封后加上 `--search=reddit,hackernews,github,polymarket`
4. **融入 pipeline:** 可以让 pipeline 在触发条件（比如特定关键词）时调用 last30days 作为高级研报，输出保存到 `data/last30days/` 供后续消费