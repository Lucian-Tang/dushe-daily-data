# 产品机会深度调研报告 | 2026-06-01

调研时间：2026-06-01 | 调研员：Thomas

---

## 机会一：NODUS HN Radar — HN 爆炸帖追踪

| 维度 | 详情 |
|------|------|
| **产品** | NODUS HN Radar — Chrome 扩展 |
| **网站** | nodus-ai.app/hn-radar |
| **作者** | mmcarvalhodev（同 NODUS 作者） |
| **License** | MIT 开源 |
| **定价** | 免费，无需注册 |
| **平台** | Chrome + Firefox（280KB 轻量） |

### 核心能力
- 在 HN 页面之上叠加了一层 Lens 阅读层（沉浸式阅读视图）
- **Velocity & Delta**：用速度分数标记帖子爬升速度，区分"持续走热" vs "突然爆火"
- **雷达面板**：实时追踪 HN 上的火花，监控帖子 velocity 变化
- **OP 在线徽章**：帖子作者正在线上讨论时可见
- **评论战争预警**：当帖子的评论数量激增且回复迅速时触发
- **内联预览 + 翻译**：不跳转预览链接内容，内置翻译
- **域静音 + 观察列表**：屏蔽特定域名，自定义追踪关键词

### 底层逻辑
HN Radar 是 NODUS 生态的一部分——NODUS 本身是一个跨平台 AI 对话捕捉浏览器扩展（支持 ChatGPT/Claude/Gemini/Perplexity/Copilot/Grok/DeepSeek 7 大平台），核心解决"AI 对话结束就消失"的问题。HN Radar 可视为 NODUS 生态在 HN 场景的专精分支。

### 对 Luxmind 的启示
HN Radar 解决的是「信息过剩下的信号过滤」问题——HN 每天 1000+ 帖子，谁能帮用户找出真正值得看的？这和有数Feed的核心命题高度一致。差异化在于：HN Radar 是 local-first 无服务器架构，用户数据全在本地，这是一把双刃剑——隐私强但缺少社交/协作能力。

### 可行性判断
- ✅ HN Radar 本身已是成熟产品，直接使用即可
- ✅ 有数Feed若做 HN 信息源，可借鉴其雷达/velocity 机制
- ⚠️ HN Radar 的 velocity 算法是核心壁垒，但可以用简单的 rate-of-change 替代
- ⚠️ 如果只是集成 HN 数据源到有数Feed，技术难度不高

---

## 机会二：Angel Match 4.0 — 12.5万+ 天使/VC 数据库

| 维度 | 详情 |
|------|------|
| **产品** | Angel Match 4.0 |
| **网站** | angelmatch.io（Cloudflare 保护） |
| **数据库** | 声称 125,000+ 天使投资人/VC |
| **首次发布** | 2019 年（当时 50,000 投资人） |
| **定位** | 创始人寻找投资人匹配平台 |

### 产品分析
Angel Match 是一个风投匹配平台，帮助创业者和投资人进行双向匹配。第一版 2019 年在 HN 发布时主打 5 万个天使/VC 投资人对接，创始人可以按行业、阶段、地域等维度筛选投资人，并直接查看对接可能性评分。

### 4.0 版本的差异化
已知信息有限（网站被 Cloudflare 保护），但从名称 "4.0" 推断：
- 数据库规模从 50k → 125k+（扩大 2.5x）
- 应增强了 AI 匹配算法
- 可能加入了 pitch deck 评估/评分功能
- 可能包含投资人活跃度分析（哪些投资人最近在出手）

### 对 Luxmind 的启示
创始人对投资人匹配有真实痛点——Crunchbase 数据全但搜索体验差、Angellist 已转型、Pitchbook 太贵（$10k+/年）。Luxmind 若做类似方向，可考虑：
1. **轻量版**：整合中国天使/VC 数据库，聚焦国内场景
2. **差异化**：加 AI 评分（投资人的行业匹配度 + 活跃度 + 历史偏好）
3. **模式**：数据库免费 + 深度分析报告付费

### 可行性判断
- ⚠️ 数据获取是最大壁垒——投资人数据库需要持续维护和验证
- ⚠️ 海外市场已有 Crunchbase/Pitchbook/LinkedIn 等强竞争对手
- ⚠️ 国内市场 VC 数据库已有 IT 桔子/36氪创投等
- ✅ 如果专注超级垂类（如 AI 赛道独家投资人数据库），有空间

---

## 机会三：RabbitTravel — 智能旅行规划

### 调研结果
经过多个渠道（域名查询、HN Algolia 搜索、GitHub 搜索、Product Hunt 搜索）交叉验证，**RabbitTravel（rabbittravel.app）目前不是一个活跃的产品**：

- 域名 rabbittravel.app 无法解析（DNS A 记录不存在）
- HN Algolia 搜索无相关记录
- GitHub 上仅有一个无关项目（Rabbit.AI.Travel，葡萄牙语的学校项目，1 commit）
- Product Hunt 上未找到匹配产品

### 可能性分析
1. **产品尚未发布**：域名持有中但 MVP 尚未上线
2. **已改名/迭代**：可能换了产品名，比如 Rabittravel 这种拼写变体
3. **内部代号**：可能是某团队的内部项目名称

### 智能旅行规划赛道分析（即使 RabbitTravel 本身未上线，这个方向值得关注）

| 竞品 | 特点 | 价格 |
|------|------|------|
| Trip Planner AI | ChatGPT 插件 + Web 版，行程自动生成 | $9/mo |
| OutOfOffice | AI 旅行规划，支持协作 | $15/mo |
| Roam Around | 多语言 AI 行程生成 | 免费+付费 |
| Wonderplan | 从行程到预订一站式 | $5/行程 |
| Layla | WhatsApp 聊天式旅行助手 | 免费 |
| GuideGeek | WhatsApp/Instagram 聊天机器人 | 免费 |

### 对 Luxmind 的启示
AI 旅行规划是红海赛道，全球有至少 30+ 竞品。核心差异点：
- **多数竞品是做行程规划，不是做旅行决策**——"去哪里"比"怎么安排行程"更难
- **信息聚合 > 行程生成**：真正的痛点是碎片化的攻略信息太多（小红书/穷游/马蜂窝），需要一个 AI Agent 去消化这些信息
- **商业闭环**：预订抽佣还是订阅制？多数竞品靠预订 affiliate 活得不好

### 可行性判断
- ⚠️ 红海赛道，获客成本高
- ⚠️ 数据源整合复杂（酒店/航班/景点/攻略/用户评价）
- ⚠️ 国内有携程/去哪儿/飞猪，API 开放程度不确定
- ✅ 如果聚焦"行程推荐 × 朋友投票"社交场景，可能有差异化

---

## 机会四：AccountyCat — 真懂上下文的专注伴侣

| 维度 | 详情 |
|------|------|
| **产品** | AccountyCat |
| **网站** | accountycat.com |
| **GitHub** | github.com/strjonas/AccountyCat |
| **作者** | Nick Senger（strjonas / nicksenger） |
| **License** | MIT 开源 |
| **定价** | 免费（自带 OpenRouter key 可用） |
| **平台** | macOS 26+，Apple Silicon（Native Swift 应用） |
| **发布** | 刚刚在 Product Hunt 上线 |

### 核心创新：不是 Blocklist，而是语义理解
AccountyCat 的核心差异化在于**它不依赖黑名单**——传统专注工具（SelfControl/Cold Turkey/Freedom）只能阻止/允许特定域名，但同一个网站（Docs/Notion/ChatGPT）在写东西和刷页面时意义完全不同。

AccountyCat 的工作原理：
1. 驻留在菜单栏，每隔几分钟（或切换应用时）检查当前活跃应用和窗口标题
2. **有足够上下文就用文本判断**（如窗口标题是 "Google Doc - PRD draft v3"），不需要截图
3. **上下文不足时才截屏**（一次），用视觉模型判断你在做什么
4. 走神时弹出温和提醒（不锁屏幕，不阻止操作）
5. 误判时可以纠正，它会学习

### 模型与成本

| 等级 | 文本模型 | 视觉模型 | 预估月费 |
|------|----------|----------|----------|
| Economy | DeepSeek V4 Flash | Qwen 3.5 9B | ~$0.80-$1.50 |
| Default | DeepSeek V4 Flash | Qwen 3.6 35B | ~$1.50-$3.00 |
| Smartest | Kimi K2.6 | Kimi K2.6 | ~$3.00-$5.00 |

也支持全本地模式（llama.cpp，Qwen 系列模型），无需联网。

### 隐私架构
- 所有推断数据不经过 AccountyCat 服务器
- 截图是临时分析，分析完即丢弃
- 本地模式完全不联网
- 开源 + 显式权限说明

### 对 Luxmind 的启示
AccountyCat 证明了一个趋势：**AI 原生工具正在从"规则引擎"进化到"理解引擎"**。传统专注工具本质是防火墙逻辑（阻断→移除），AccountyCat 是教练逻辑（觉察→提醒→学习）。

这个思路可以迁移到：
- **代码开发辅助**：检测开发者是否真的在写代码 vs 刷 Reddit
- **阅读辅助**：检测用户是在精读文章还是快速滚动
- **会议辅助**：检测用户是否在发呆/做其他事

### 可行性判断
- ✅ 方向正确，AI 降低 context-awareness 的边际成本
- ✅ macOS 原生 + MIT 开源，可以直接 fork/二次开发
- ✅ 极低成本（$0.80/mo 起），说明推理成本不是瓶颈
- ⚠️ Screen Recording + Accessibility 权限是门槛（用户信任问题）
- ⚠️ 目前的用户群体偏极客，需要降低配置门槛

---

## 综合优先级排序

| 优先级 | 机会 | 理由 |
|--------|------|------|
| **P1** | AccountyCat | MIT 开源、方向对、成本低、可直接用或 fork |
| **P1** | NODUS HN Radar | 成熟产品、可直接集成、和有数Feed方向吻合 |
| **P2** | Angel Match 4.0 | 数据壁垒高，需要大量冷启动资源 |
| **P3** | RabbitTravel | 产品不存在或未上线，AI 旅行规划是红海 |

调研完成 | 共 4 个机会 | 如需深入某方向请告知
