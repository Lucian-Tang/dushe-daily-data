# 📡 行业热点日报 · 信源方案

> **制定人：** Thomas（产品经理）  
> **版本：** v1.0  
> **日期：** 2026-05-07  
> **覆盖赛道：** 自动驾驶 🤖 | 机器人 🦾 | AI 🧠

---

## 一、方案概述

为"行业热点日报"规划信源矩阵，核心原则：
- **质量优先**：优先选择一手来源、权威媒体、行业核心玩家官方渠道
- **多语言覆盖**：中英文各覆盖，避免单一信息茧房
- **可操作性**：RSS/API优先，减少手工维护成本
- **噪声控制**：单赛道不超过5个信源，避免信息过载

---

## 二、信源详细方案

---

### 🚗 自动驾驶

| # | 信源名称 | 类型 | URL / Feed | 更新频率 | 语言 | 权威度 |
|---|---------|------|------------|---------|------|--------|
| 1 | Waymo Blog | Blog (RSS) | https://waymo.com/blog/feed/ | 每周1-3篇 | 英 | A |
| 2 | The Verge - Transportation | RSS | https://www.theverge.com/rss/transportation/index.xml | 每日 | 英 | A |
| 3 | 机器之心 - 自动驾驶频道 | Web / RSS | https://www.jiqizhixin.com/section/auto | 每日 | 中 | A |
| 4 | Hacker News - "autonomous driving" | Search (RSS viahnrss) | https://hnrss.org/newest?q=autonomous+driving | 每日 | 英 | B |
| 5 | arXiv (cs.RO) - Autonomous Vehicles | arXiv RSS | https://arxiv.org/rss/cs.RO | 每日 | 英 | A |

**信源说明：**
- **Waymo Blog**：官方一手动态，技术路线、商业化进展，L4头部玩家的核心信息披露源
- **The Verge - Transportation**：科技媒体中自动驾驶报道最成体系的渠道，兼具深度和时效性
- **机器之心**：中文圈技术含量最高的科技媒体，过滤噪声能力强，适合快速获取中文行业动态
- **HN Autonomous Driving**：社区筛选机制，高热度帖子往往代表行业关注焦点，适合捕捉拐点性讨论
- **arXiv cs.RO**：学术前沿的风向标，适合捕捉技术范式转移的早期信号

**观点性判断示例：**
> "Waymo近期密集发布城区无图自动驾驶视频，标志着纯视觉+实时地图路线已完全进入产品化阶段，其他依赖高精地图的玩家面临更大时间压力。"

---

### 🤖 机器人

| # | 信源名称 | 类型 | URL / Feed | 更新频率 | 语言 | 权威度 |
|---|---------|------|------------|---------|------|--------|
| 1 | IEEE Spectrum Robotics | RSS | https://spectrum.ieee.org/robotics/rss | 每周3-5篇 | 英 | A |
| 2 | Boston Dynamics Blog | Blog (RSS) | https://www.bostondynamics.com/blog/rss.xml | 每月1-2篇 | 英 | A |
| 3 | Figure AI 新闻 | Blog / Twitter | https://www.figureai.com/news (无RSS，Twitter替代) | 不定期 | 英 | A |
| 4 | 机器之心 - 机器人频道 | Web / RSS | https://www.jiqizhixin.com/section/robotics | 每日 | 中 | A |
| 5 | arXiv (cs.RO) - Robotics | arXiv RSS | https://arxiv.org/rss/cs.RO | 每日 | 英 | A |

**信源说明：**
- **IEEE Spectrum Robotics**：行业顶级媒体，覆盖工业、人形、服务机器人全赛道，文章经过同行评审，权威性最高
- **Boston Dynamics Blog**：人形机器人商业化最成熟玩家，Atlas电动化转型后技术路线值得重点跟踪
- **Figure AI**：人形机器人赛道最新进展，融资规模和技术迭代速度均处于行业领先地位
- **机器之心机器人频道**：中文人形机器人热潮下，宇树、星动纪元等国内玩家动态的主要聚合地
- **arXiv cs.RO**：机器人领域核心学术论文预印本，尤其关注 Manipulation、Locomotion、VLN 等子方向的新工作

**观点性判断示例：**
> "Boston Dynamics宣布Atlas全面电动化并推进商业化，标志着双足人形机器人从实验室阶段正式进入产品落地竞争，倒逼国内宇树等人形玩家加速商业化验证。"

---

### 🧠 AI

| # | 信源名称 | 类型 | URL / Feed | 更新频率 | 语言 | 权威度 |
|---|---------|------|------------|---------|------|--------|
| 1 | Anthropic Research Blog | Blog (RSS) | https://www.anthropic.com/news/rss | 每月2-4篇 | 英 | A |
| 2 | OpenAI Blog | Blog (RSS) | https://openai.com/blog/rss/ | 每周1-3篇 | 英 | A |
| 3 | 量子位 - AI频道 | Web / RSS | https://www.qbitai.com/ | 每日 | 中 | A |
| 4 | Hacker News - AI Tag | Search (RSS) | https://hnrss.org/newest?tags=ai | 每日 | 英 | B |
| 5 | arXiv (cs.AI / cs.LG) | arXiv RSS | https://arxiv.org/rss/cs.AI + https://arxiv.org/rss/cs.LG | 每日 | 英 | A |

**信源说明：**
- **Anthropic Research Blog**：Claude模型背后核心技术思路、RLHF、Constitutional AI等方法论的一手披露，适合深度理解AI能力边界
- **OpenAI Blog**：GPT系列、文生视频、Agent方向的产品和研究动态，行业事实标准的风向标
- **量子位AI频道**：国内AI创业投资动态最全的中文信源，适合跟踪国内大模型竞争格局
- **HN AI Tag**：社区热度筛选，适合捕捉开源社区反应、论文复现讨论等非官方信号
- **arXiv cs.AI/cs.LG**：基础研究最新进展，适合识别哪些技术方向正在从学术向产业迁移

**观点性判断示例：**
> "OpenAI近期密集发布Agent相关研究，结合Anthropic对Claude Tool Use能力的披露，2026年下半年有望成为Agent从Demo走向真实工作流落地的拐点。"

---

## 三、信源总览矩阵

| 赛道 | 信源数 | 语言比例 | 更新频率覆盖 |
|------|--------|---------|------------|
| 🚗 自动驾驶 | 5 | 英文4 : 中文1 | 日频3 / 周频2 |
| 🤖 机器人 | 5 | 英文4 : 中文1 | 日频2 / 周频2 / 不定期1 |
| 🧠 AI | 5 | 英文3 : 中文2 | 日频3 / 周频2 |
| **合计** | **15** | **英11 : 中4** | — |

---

## 四、日报模板

```markdown
# 🤖 行业热点日报 YYYY-MM-DD

> 本日编辑：Thomas｜信源覆盖：自动驾驶🤖/机器人🦾/AI🧠

---

## 🚗 自动驾驶（2-3条）

- **[标题](链接)**
  一句话摘要 + **分析观点**：……

- **[标题](链接)**
  一句话摘要 + **分析观点**：……

---

## 🤖 机器人（2-3条）

- **[标题](链接)**
  一句话摘要 + **分析观点**：……

- **[标题](链接)**
  一句话摘要 + **分析观点**：……

---

## 🧠 AI（2-3条）

- **[标题](链接)**
  一句话摘要 + **分析观点**：……

- **[标题](链接)**
  一句话摘要 + **分析观点**：……

---

## 📄 今日值得关注的论文（2-3篇）

- **[论文标题](arXiv链接)** — arXiv cs.XX
  一句话摘要 + **为什么值得关注**：……

---

> 📌 今日编辑备注（如有）
```

---

## 五、执行建议

### 优先级排序（建议日报制作顺序）
1. **必读**：Waymo Blog / Boston Dynamics / Anthropic / OpenAI → 核心玩家官方动态
2. **推荐**：IEEE Spectrum / The Verge / 机器之心 → 媒体二次加工，信息密度高
3. **补充**：HN / arXiv → 社区热度和学术前沿，作为观点佐证

### 工具建议
- **RSS聚合**：`Miniflux` 或 `Inoreader` 统一管理所有RSS信源
- **arXiv监控**：使用 `arxiv-sanity` 或自定义关键词过滤
- **自动化**：可选 `Zapier` / `Make` 将RSS更新推送到飞书群

### 信源迭代原则
- 每季度审视信源有效性，删除低频、低权威来源
- 跟踪新玩家（如鉴智机器人、Physical Intelligence）动态，适时纳入
- 日报读者反馈中标注"已读无感"的信源优先替换

---

*本方案为初版，后续根据实际执行反馈迭代优化。*