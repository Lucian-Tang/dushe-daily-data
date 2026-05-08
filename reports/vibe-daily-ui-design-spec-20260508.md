# 毒舌日报 · 重构 Phase 1 交付物

> 任务编号：ui-design-spec-001 + content-sources-spec-001
> 日期：2026-05-08
> 执行人：Thomas

---

## 交付 A：视觉设计规范（Vibe Daily UI Design Spec）

### A1. 配色方案

主调：**暗色系**，背景深邃，强调色紫橙渐变，营造「科技感 + 人文感」的张力。

#### 完整色板

| 角色 | 色值 | 说明 |
|------|------|------|
| **背景-深** | `#0d0d1a` | 页面最底层背景 |
| **背景-卡片** | `#1a1a2e` | 卡片默认背景 |
| **背景-悬浮** | `#22223a` | 卡片 hover / 浮层背景 |
| **背景-输入框** | `#141428` | 输入框/搜索框底色 |
| **主色-紫** | `#7c3aed` | 渐变起点，主要 CTA |
| **主色-橙** | `#f97316` | 渐变终点，热度/强调 |
| **紫橙渐变** | `linear-gradient(135deg, #7c3aed 0%, #f97316 100%)` | 按钮/标签/热条填充 |
| **文字-主** | `#f1f5f9` | 标题、主要阅读文字 |
| **文字-次** | `#94a3b8` | 次要说明、时间戳 |
| **文字-弱** | `#475569` | 占位符、disabled |
| **文字-反转** | `#0d0d1a` | 渐变按钮上的文字 |
| **边框-默认** | `#2d2d4a` | 卡片默认边框 |
| **边框-强调** | `#7c3aed` | 聚焦/选中态边框 |
| **状态-成功** | `#22c55e` | 上线/正向标记 |
| **状态-警告** | `#eab308` | 待审核/中风险 |
| **状态-危险** | `#ef4444` | 负面/下架标记 |
| **状态-信息** | `#38bdf8` | 资讯类标签 |

#### 渐变应用规范
- **热条填充**：从左到右渐变，宽度按热度值 `0–100` 动态缩放
- **标签背景**：`gradient-label` 类使用紫橙渐变 + 0.15 透明度
- **按钮主 CTA**：`linear-gradient(135deg, #7c3aed, #f97316)`，配合 `box-shadow: 0 4px 20px rgba(124, 58, 237, 0.4)`

---

### A2. 字体层级

| 元素 | 字号 | 字重 | 行高 | letter-spacing | 说明 |
|------|------|------|------|----------------|------|
| **H1（日报标题）** | 28px | 700 | 1.2 | -0.02em | 频道切换后的日报大标题 |
| **H2（文章标题）** | 18px | 600 | 1.4 | -0.01em | 列表中文章主标题 |
| **H3（分段小标题）** | 15px | 600 | 1.4 | 0 | 内文分段 |
| **正文（摘要）** | 14px | 400 | 1.6 | 0 | 文章摘要/描述文字 |
| **金句（Pull-quote）** | 16px | 500 | 1.5 | -0.01em | 斜体风格，底部加紫橙装饰线 |
| **标签（Tag）** | 11px | 600 | 1 | 0.05em | 全大写，字母间距宽松 |
| **时间戳** | 12px | 400 | 1 | 0 | 次要信息，灰色 |
| **热度数值** | 14px | 700 | 1 | 0 | 热度数字，独立展示 |

**字体族：**
```css
font-family: 'Inter', 'Noto Sans SC', -apple-system, sans-serif;
```
金句可用 `'Georgia', serif` 增加人文气质。

---

### A3. 间距系统

基于 **4px 基准网格**。

| 用途 | 数值 |
|------|------|
| 页面左右边距（移动端） | 16px |
| 页面左右边距（桌面端） | 24px |
| **卡片内边距** | 16px |
| **列表项间距**（卡片之间） | 12px |
| 频道 Tab 间距 | 8px |
| 标签内间距 | 6px 10px |
| 区块之间（大区隔） | 32px |
| 标题与内容间距 | 8px |
| 热条高度 | 4px |

---

### A4. 动效曲线

| 动效场景 | 时长 | 缓动函数 | 说明 |
|----------|------|----------|------|
| **卡片入场（列表加载）** | 400ms | `cubic-bezier(0.16, 1, 0.3, 1)`（出场感强） | 依次入场，间隔 60ms |
| **卡片 hover 抬升** | 200ms | `cubic-bezier(0.4, 0, 0.2, 1)` | translateY(-2px) + 阴影增强 |
| **卡片点击反馈** | 100ms | `ease-out` | scale(0.98) |
| **热度条动画** | 800ms | `cubic-bezier(0.25, 0.46, 0.45, 0.94)` | 从 0 增长到目标值 |
| **热度条 hover 脉冲** | 1.5s | `ease-in-out` | 无限循环 opacity 0.7→1 |
| **频道 Tab 切换** | 250ms | `cubic-bezier(0.4, 0, 0.2, 1)` | 下划线滑动 |
| **吸底操作栏出现** | 300ms | `cubic-bezier(0.16, 1, 0.3, 1)` | 从底部滑入 |
| **模态框/浮层** | 250ms | `cubic-bezier(0.16, 1, 0.3, 1)` | scale 0.95→1 + opacity |
| **骨架屏 shimmer** | 1.5s | `ease-in-out` | 渐变位移动画 |

---

### A5. 组件状态

#### 卡片（Article Card）

| 状态 | 背景 | 边框 | 阴影 | 变换 |
|------|------|------|------|------|
| **Normal** | `#1a1a2e` | 1px `#2d2d4a` | `0 2px 8px rgba(0,0,0,0.3)` | — |
| **Hover** | `#22223a` | 1px `#7c3aed` | `0 8px 24px rgba(124,58,237,0.2)` | translateY(-2px) |
| **Active（点击中）** | `#1a1a2e` | 1px `#f97316` | `0 2px 8px rgba(0,0,0,0.3)` | scale(0.98) |
| **Disabled** | `#1a1a2e` | 1px `#1e1e32` | none | opacity: 0.5, cursor: not-allowed |

#### 按钮（Button）

| 状态 | 背景 | 文字色 | 阴影 |
|------|------|--------|------|
| **Normal** | 渐变紫→橙 | `#ffffff` | `0 4px 20px rgba(124,58,237,0.4)` |
| **Hover** | 渐变 +10% 亮度 | `#ffffff` | `0 6px 28px rgba(124,58,237,0.6)` |
| **Active** | 渐变 -10% 亮度 | `#ffffff` | `0 2px 12px rgba(249,115,22,0.4)` |
| **Disabled** | `#2d2d4a` | `#475569` | none |

#### 标签（Tag）

| 状态 | 背景 | 文字色 | 边框 |
|------|------|--------|------|
| **Normal** | `rgba(124,58,237,0.15)` | `#a78bfa` | 1px `rgba(124,58,237,0.3)` |
| **Hover** | `rgba(124,58,237,0.25)` | `#c4b5fd` | 1px `rgba(124,58,237,0.5)` |
| **Active（选中）** | 渐变紫→橙 | `#ffffff` | none |
| **Disabled** | `rgba(71,85,105,0.15)` | `#475569` | 1px `rgba(71,85,105,0.2)` |

#### 输入框（Search/Input）

| 状态 | 背景 | 边框 | 文字色 |
|------|------|------|--------|
| **Normal** | `#141428` | 1px `#2d2d4a` | `#f1f5f9` |
| **Focus** | `#141428` | 1px `#7c3aed` + 外发光 | `#f1f5f9` |
| **Filled** | `#141428` | 1px `#2d2d4a` | `#f1f5f9` |
| **Error** | `#141428` | 1px `#ef4444` | `#f1f5f9` |

---

## 交付 B：新频道信源规格（Content Sources Spec）

### B1. 统一 Article Schema

所有信源最终归一化为以下结构：

```json
{
  "id": "string (md5/url+title 哈希，保证唯一性)",
  "title": "string (必填，最多 120 字符)",
  "summary": "string (选填，最多 300 字符，由 AI 从正文摘要或直接使用描述字段)",
  "content": "string (正文原文或完整描述，最多 5000 字符)",
  "url": "string (原始链接，必填)",
  "source": "string (来源站点名，如 'TechCrunch')",
  "sourceType": "free_api | rss | scrape | paid",
  "author": "string (作者名，选填)",
  "publishedAt": "ISO 8601 datetime",
  "tags": ["string"] (自动打标或从元数据提取，1–5 个)",
  "channel": "startup | ai | design",
  "heat": 0-100 (计算得出，见热度算法),
  "language": "zh | en",
  "createdAt": "ISO 8601 datetime"
}
```

---

### B2. 频道①：Startup（创业/科技）

#### 候选信源

| # | 信源名称 | 获取方式 | 说明 |
|---|----------|----------|------|
| S1 | **TechCrunch** | RSS | `https://techcrunch.com/feed/` |
| S2 | **Product Hunt** | 免费 API（需 key） | PH API v1，每日热门产品 |
| S3 | **Hacker News** | RSS | `https://hnrss.org/frontpage` |
| S4 | **Product Hunt Launch Feed** | RSS | `https://www.producthunt.com/feed` |
| S5 | **小众软件/异次元** | web_fetch 爬虫 | 中文，垂直工具类 |

#### 字段映射

**S1 TechCrunch RSS → Article**
```json
{
  "title": "item.title",
  "summary": "item.description (strip HTML, truncate 300)",
  "url": "item.link",
  "source": "TechCrunch",
  "sourceType": "rss",
  "author": "item.author | item['dc:creator']",
  "publishedAt": "item.pubDate → ISO 8601",
  "tags": ["startup"],
  "language": "en"
}
```

**S2 Product Hunt API → Article**
```json
{
  "title": "post.name",
  "summary": "post.tagline",
  "content": "post.description",
  "url": "post.redirect_url",
  "source": "Product Hunt",
  "sourceType": "free_api",
  "author": "post.maker_string",
  "publishedAt": "post.created_at",
  "tags": "post.topics[]",
  "language": "en"
}
```

**S3 Hacker News RSS → Article**
```json
{
  "title": "item.title",
  "summary": "item.description (strip HTML)",
  "url": "item.link",
  "source": "Hacker News",
  "sourceType": "rss",
  "author": "item.author",
  "publishedAt": "item.pubDate → ISO 8601",
  "tags": ["tech", "startup"],
  "language": "en"
}
```

---

### B3. 频道②：AI（人工智能）

#### 候选信源

| # | 信源名称 | 获取方式 | 说明 |
|---|----------|----------|------|
| A1 | **Hugging Face Blog** | RSS | `https://huggingface.co/blog/feed.xml` |
| A2 | **DeepMind Blog** | web_fetch 爬虫 | 页面结构稳定 |
| A3 | **The Rundown AI** | RSS / web_fetch | AI 新闻汇总，质量高 |
| A4 | **Verse AI 资讯** | RSS | 中文 AI 媒体 |
| A5 | **ArXiv cs.AI** | RSS | 学术前沿，每日取最新 20 篇 |
| A6 | **Future Tools** | web_fetch | AI 工具库，每日热门工具 |

#### 字段映射

**A5 ArXiv cs.AI RSS → Article**
```json
{
  "title": "item.title (remove 'cs.AI:' prefix)",
  "summary": "从 item.description 提取前 300 字",
  "url": "item.link",
  "source": "arXiv",
  "sourceType": "rss",
  "author": "item.author",
  "publishedAt": "item.pubDate → ISO 8601",
  "tags": ["AI", "research", "paper"],
  "language": "en"
}
```

**A3 The Rundown AI → Article**
```json
{
  "title": "article.title",
  "summary": "article.excerpt",
  "url": "article.url",
  "source": "The Rundown AI",
  "sourceType": "rss",
  "author": "article.author",
  "publishedAt": "article.published_at",
  "tags": ["AI", "news"],
  "language": "en"
}
```

---

### B4. 频道③：Design（设计/创意）

#### 候选信源

| # | 信源名称 | 获取方式 | 说明 |
|---|----------|----------|------|
| D1 | **Behance RSS** | RSS | `https://www.behance.net/feeds/projects` |
| D2 | **Dribbbles Popular** | RSS | `https://dribbble.com/shots/popular.rss` |
| D3 | **CSS Design Awards** | web_fetch 爬虫 | 精选网页设计 |
| D4 | **Designboom** | RSS | `https://www.designboom.com/feed/` |
| D5 | **优设/uisdc** | RSS | 中文设计媒体 |
| D6 | **Muzli by Medium** | RSS | `https://medium.com/feed/@Muzli` |

#### 字段映射

**D2 Dribbble RSS → Article**
```json
{
  "title": "entry.title",
  "summary": "entry.summary (strip HTML, 300字)",
  "url": "entry.link",
  "source": "Dribbble",
  "sourceType": "rss",
  "author": "entry.author",
  "publishedAt": "entry.published → ISO 8601",
  "tags": ["design", "ui", "illustration"],
  "language": "en"
}
```

**D5 优设 RSS → Article**
```json
{
  "title": "item.title",
  "summary": "item.description (strip HTML, 300字)",
  "url": "item.link",
  "source": "优设 UISDC",
  "sourceType": "rss",
  "author": "item.author",
  "publishedAt": "item.pubDate → ISO 8601",
  "tags": ["design", "ui", "ux"],
  "language": "zh"
}
```

---

### B5. 质量门槛

| 维度 | 门槛 |
|------|------|
| **最少字数** | title ≥ 5 字符；summary/content ≥ 20 字符 |
| **重复去重** | 以 `md5(url)` 为主键，去重窗口为 **72 小时**内；同一 title（忽略大小写/标点）出现视为重复，降分处理 |
| **时间过滤** | publishedAt 超过 **7 天**的条目默认不收录（AI 频道学术源放宽至 14 天） |
| **语言过滤** | 中英混排时，以内容中汉字占比是否 ≥ 30% 判断为中文内容 |
| **最低质量** | 无 title 或无 url 的条目直接丢弃 |
| **排序权重** | 热度分 = (阅读量因子 × 0.4) + (新鲜度因子 × 0.3) + (互动因子 × 0.3) |

---

### B6. 降级方案（Fallback）

当主信源不可用时，按以下顺序降级：

#### Startup 频道降级链
```
TechCrunch RSS (主)
  → Hacker News RSS (备1)
    → Product Hunt RSS (备2)
      → 小众软件/异次元爬虫 (备3)
```

#### AI 频道降级链
```
Hugging Face Blog RSS (主)
  → ArXiv cs.AI RSS (备1)
    → The Rundown AI RSS (备2)
      → Verses AI 资讯 RSS (备3)
```

#### Design 频道降级链
```
Dribbble Popular RSS (主)
  → Behance RSS (备1)
    → 优设 RSS (备2)
      → Designboom RSS (备3)
```

**降级触发条件：** 连续 2 次请求超时（>10s）或 HTTP 状态码 ≥ 500。
**降级恢复检测：** 每 30 分钟重试主信源一次，恢复后自动切回。

---

*文档版本：v1.0 | 下一阶段：Phase 2 技术实施评审*
