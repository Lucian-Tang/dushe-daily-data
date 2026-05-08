# 技能评估报告：mvanhorn/last30days-skill

**评估人：** Stephen（研发工程师）  
**评估日期：** 2026-05-09  
**仓库：** https://github.com/mvanhorn/last30days-skill

---

## 一、功能概述

`last30days` 是一个 AI Agent 驱动的社交舆情研究引擎，核心思路是：以 Reddit、X、YouTube、Hacker News、Polymarket、GitHub 等平台的真实用户参与度（ upvotes、likes、预测赔率）作为排序信号，而非 Google式的 SEO 权重。

用户输入一个主题，引擎自动：
1. **智能解析实体**：识别主题相关的人物、公司、GitHub 账号、subreddit、X handles（v3 新增 Python pre-research brain）
2. **并行搜索**多个平台，采集最近 30 天的内容
3. **聚类去重**：同一事件在 Reddit/X/YouTube 上出现，合并为一条
4. **评分排序**：相关性 × 时效性 × 参与度（humor judge 额外评估幽默/传播性）
5. **合成简报**：输出 Markdown/HTML 格式的综合报告（含引用来源）

**支持平台（按配置难度分）：**

| 平台 | 状态 | 所需配置 |
|------|------|---------|
| Reddit（含评论） | 开箱即用 | 无（免费公共 JSON） |
| Hacker News | 开箱即用 | 无 |
| Polymarket | 开箱即用 | 无 |
| GitHub | 开箱即用 | 无 |
| X / Twitter | 需登录 | 免费，需浏览器 session |
| YouTube | 需 yt-dlp | 免费 |
| Bluesky | 需 App Password | 免费 |
| TikTok / Instagram / Threads / Pinterest | 需 ScrapeCreators API Key | 10,000 次免费调用 |
| Perplexity Sonar | 需 OpenRouter Key | 按量付费 |
| Web 搜索 | 需 Brave Search Key | 2,000 次/月免费 |

---

## 二、技术实现分析

### 2.1 技术栈

- **语言：** Python 3.12+
- **核心依赖（pyproject.toml）：**
  - `requests >= 2.32, < 3`
  - `yt-dlp`（YouTube 转录）
  - Node.js vendored Bird client（X 搜索）
- **测试覆盖：** 1,012 个测试用例
- **MIT 协议，无追踪，无分析上报**

### 2.2 架构（从 SPEC.md 分析）

```
last30days.py (编排器)
├── env.py         - API Key 加载
├── dates.py       - 30天窗口 + 置信度
├── cache.py       - 24h TTL 缓存
├── http.py        - stdlib HTTP client（重试逻辑）
├── models.py      - OpenAI/xAI 模型自动选择
├── openai_reddit.py  - Reddit via OpenAI Responses API
├── xai_x.py       - X via xAI Responses API
├── hackernews.py  - HN via Algolia API（免费）
├── polymarket.py  - Polymarket via Gamma API（免费）
├── normalize.py   - 统一数据schema
├── score.py       - 评分（相关性+时效性+参与度）
├── dedupe.py      - 近似重复检测
└── render.py      - Markdown/HTML 输出
```

### 2.3 输出文件

所有输出写入 `~/.local/share/last30days/out/`：
- `report.md` / `report.json` - 综合报告
- `last30days.context.md` - 可注入到其他 skill 的上下文片段
- `raw_*.json` - 各平台原始数据

### 2.4 OpenClaw 集成方式

- **安装命令：** `clawhub install last30days-official`
- **skill 本体：** 遵循 OpenClaw skill 规范，SKILL.md 定义 prompt 模板和工具白名单
- **允许工具：** `Bash, Read, Write, AskUserQuestion, WebSearch`
- **Python 引擎**运行在 `skills/last30days/scripts/last30days.py`

---

## 三、对我们团队的价值评估

### 3.1 能否用于日报系统？

**可以，但需分场景评估。**

| 维度 | 评估 |
|------|------|
| **数据源覆盖** | 覆盖主流社交平台（Reddit、X、HN、Polymarket、GitHub），对于舆情/竞品/技术趋势类日报非常实用 |
| **输出格式** | 支持 Markdown/HTML 输出，可嵌入飞书文档；也有 JSON 输出，利于程序化处理 |
| **时效性** | 严格 30 天窗口，符合日报需求 |
| **自动化友好度** | CLI 驱动，`python3 last30days.py <topic> --emit=md` 即可获取报告，可 cron 化 |
| **与我们现有系统对比** | 我们若已有数据采集管道，此工具可作为"增强层"，但不能替代结构化数据采集 |

**结论：** 更适合作为**技术趋势/竞品舆情研究**工具，而非企业级日报数据源。例如：调研竞品最近一个月的社区反馈、技术选型的社区共识、关键人物动态。

### 3.2 能否增强数据采集管道？

**可以，主要体现在以下方面：**

1. **社交舆情信号采集**：可将 Reddit/HN/Polymarket 的参与度数据标准化后入库
2. **实体解析增强**：v3 的 pre-research brain 能自动识别主题相关的人物/账号/社区，降低人工配置成本
3. **上下文注入接口**：其他 skill 可通过 `!python3 last30days.py "topic" --emit=context` 注入研究结果，为后续 agent 任务提供实时上下文
4. **竞争对比分析**：`--competitors` 参数自动发现竞品并并行研究，适合竞品监控管道

**局限：**
- 这是"研究"工具，非 ETL 工具；输出是自然语言合成，非结构化数据库记录
- 若要将结果落入我们的数据库，需要二次处理（解析 JSON/Markdown）
- API 成本：X/Twitter 需要 xAI API Key，TikTok 等需要 ScrapeCreators

---

## 四、安装风险评估

### 4.1 权限风险

| 项目 | 评估 | 风险等级 |
|------|------|---------|
| 文件写入 | 写入 `~/.local/share/last30days/out/` 和 `~/Documents/Last30Days/` | 低（用户态目录） |
| API Key 读取 | 读取 `~/.config/last30days/.env` 中的用户配置 | 低 |
| 网络访问 | 多个外部 API（Reddit、XAI、OpenRouter、Brave等） | 中 |
| 浏览器 session | X 搜索需要登录态 cookie | 中（隐私） |
| 代码执行 | skill 允许 `Bash` 工具，Python 引擎本地执行 | 中（第三方代码） |

### 4.2 依赖风险

- **Python 3.12+**：我们环境应满足
- **yt-dlp**：需 `pip install yt-dlp`，YouTube 功能必需
- **Node.js**：vendored Bird client for X，skill 内含
- **ScrapeCreators API**：TikTok/Instagram/Threads 必需，有免费额度（10,000次）
- **OpenRouter Key**：Perplexity 必需，按量付费

### 4.3 安全评估

- **MIT 协议**，代码开源，可审计
- **1,012 个测试**，质量有一定保障
- **无遥测上报**（README 明确声明）
- **主要风险点**：需配置多个第三方 API Key，若 Key 配置在 `.env` 中需控制文件权限（`chmod 600`）
- **第三方服务依赖**：长期可用性依赖 XAI、ScrapeCreators、OpenRouter 等第三方服务稳定性

---

## 五、建议

### 5.1 总体建议：**改后装**

### 5.2 理由

**不直接装的原因：**
1. 多个付费 API 依赖（xAI、ScrapeCreators、OpenRouter），我们尚未评估成本
2. TikTok/Instagram 等平台对我们团队研究场景价值有限（可能主要是中文/英文舆情场景）
3. skill 的核心能力（Reddit/HN/Polymarket/GitHub）已免费可用，但 X 搜索需要额外配置

**改后装的条件：**
1. **确认 API 成本**：先评估 xAI API 费用，若免费层级够用则保留
2. **明确使用场景**：限定用于技术趋势/竞品研究，而非日常信息摄入（避免 token 浪费）
3. **安全审查**：对 `last30days.py` 及其 lib 做一次快速代码审查（主要是网络调用和文件写入路径）
4. **配置管理**：API Key 通过统一密钥管理而非明文 `.env`

### 5.3 具体行动计划

```
第一步（1天）：
  - 试用：clawhub install last30days-official
  - 验证 Reddit/HN/Polymarket/GitHub 零配置能力
  - 测试输出格式是否满足我们日报需求

第二步（2天）：
  - 评估 xAI API 成本（注册 xAI 开发者账号，查看免费层级）
  - 若成本可接受，配置 X 搜索
  - 测试 --competitors 竞品对比功能

第三步（安全审查）：
  - 审查 skills/last30days/scripts/ 目录下的 Python 代码
  - 确认网络调用范围和数据存储路径
  - 如有必要，容器化运行

第四步（集成）：
  - 与现有日报系统/数据管道做集成 POC
  - 评估是否需要 JSON 解析层
```

### 5.4 替代方案

若评估后不安装，可参考其**设计思路**在我们的数据管道中实现类似能力：
- 用 Brave Search API 替代（免费层级 2,000 次/月）
- Reddit public JSON + Algolia HN API 免费提供参与度数据
- 自己实现 entity resolution + scoring 算法

---

## 六、总结

| 维度 | 评分（5分制） | 说明 |
|------|-------------|------|
| 功能完整性 | ⭐⭐⭐⭐⭐ | 覆盖平台最全，评分逻辑最成熟 |
| 技术质量 | ⭐⭐⭐⭐ | 1,012 测试，开源可审计，MIT |
| 团队实用性 | ⭐⭐⭐ | 零配置部分很有价值，但 API 依赖需评估 |
| 安全风险 | ⭐⭐⭐ | 中等，主要风险在第三方 API Key 和网络访问 |
| 安装优先级 | 中 | 建议先试用再决定 |

**一句话结论：** 这是目前见过的**最完整的社交舆情研究 skill**，设计思路清晰，工程实现扎实。零配置部分（Reddit/HN/Polymarket/GitHub）完全免费且开箱即用，建议**立即试用**；付费 API 部分根据实际使用量和场景评估后再决策。**不适合作为唯一数据源**，但作为日报系统/舆情管道的**增强层**很有价值。
