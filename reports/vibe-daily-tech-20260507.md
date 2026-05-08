# 毒舌日报小程序 · 技术方案设计
> 工程师：Stephen | 日期：2026-05-07 | 状态：初稿

---

## 1. 项目背景 & 目标

- **MVP 周期**：2-3 天
- **核心价值**：用户可查看三份 AI 日报（行业/开发者/社会新闻）+ AI 毒舌点评 + 分享卡片
- **数据现状**：Cron 每日产出 3 个 JSON 文件到 `/root/.openclaw/workspace/data/`
  - `raw_articles_YYYYMMDD.json` → 行业日报
  - `raw_dev_YYYYMMDD.json` → 开发者日报
  - `raw_social_YYYYMMDD.json` → 社会新闻日报

---

## 2. 整体架构

```
┌──────────────────────────────────────────────────────────────┐
│                      微信小程序（原生）                        │
│  pages/index  ·  pages/detail  ·  pages/share                │
└──────────────┬───────────────────────┬───────────────────────┘
               │ HTTPS GET              │ AI 请求（DeepSeek V4 Pro）
               ▼                        ▼
   ┌─────────────────────┐   ┌──────────────────────────┐
   │   静态 JSON 托管      │   │   OpenClaw AI 网关        │
   │  （GitHub Pages /    │   │  /v1/chat/completions    │
   │   Cloudflare Pages） │   │                          │
   └──────────┬──────────┘   └────────────┬─────────────┘
              │                          │
              │ Cron 推送                 │ AI 生成毒舌点评
              ▼                          │
   ┌─────────────────────┐               │
   │ /workspace/data/   │               │
   │ raw_*.json         │◄──────────────┘
   └─────────────────────┘
```

### 数据流向详解

```
Cron (定时) → raw_*.json → GitHub Actions / 脚本 → GitHub Pages (静态托管)
                                      ↓
                              小程序wx.request() → JSON URL
                                      ↓
                              AI 毒舌点评（按需调用 DeepSeek V4 Pro）
                                      ↓
                              Canvas 分享卡片渲染
```

---

## 3. 后端方案选择

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| **GitHub Pages 静态托管** | 免费、CDN 加速、CI/CD 自动推送 | 公开数据（适合日报场景） | ⭐⭐⭐⭐⭐ |
| Cloudflare Pages | 免费、CDN、自动部署 | 多一层配置 | ⭐⭐⭐⭐ |
| Supabase | 实时数据、API 层 | 超出 MVP 需求，成本 | ⭐⭐⭐ |
| 自建 Node.js API | 完全可控 | 需要服务器、申请域名 | ⭐⭐ |
| 微信云开发 | 可免鉴权 | 配额有限，生态封闭 | ⭐⭐ |

### 推荐方案：GitHub Pages 静态托管 + GitHub Actions 自动同步

**理由**：日报数据天然适合静态资源，零成本，无服务器运维负担，且 CI/CD 一旦搭好，每日自动更新。

**流程**：
1. 服务器上每日 Cron 执行后，通过 `rsync` 或 `git push` 更新到 GitHub 私有仓库
2. GitHub Actions 检测到 push → 构建 → 发布到 `gh-pages` 分支
3. 小程序通过 `https://<username>.github.io/<repo>/raw_articles_20260507.json` 访问

---

## 4. 小程序技术选型

### 框架选择：**微信小程序原生**

| 考量 | 结论 |
|------|------|
| MVP 速度 | 原生最直接，无额外学习/编译成本 |
| 包体积 | 原生最小（<2MB），Taro/uni-app 有额外运行时 |
| Canvas 兼容性 | 原生 Canvas API 最稳定 |
| 团队经验 | Boss 强调"优先原生，快速" |

### UI 组件库

| 库 | 场景 | 说明 |
|----|------|------|
| **Vant Weapp** | 列表/宫格/弹窗 | 有赞出品，组件丰富，稳定 |
| **ColorUI** | 装饰性样式 | 色彩鲜活，适合毒舌风格 |
| WeUI | 表单/基础组件 | 微信官方，与小程序体验一致 |

**推荐组合**：Vant Weapp（主要） + ColorUI（装饰色彩/渐变）

### 状态管理

- **Reactivity**：`const app = getApp()` 全局单例，无需引入 MobX/Pinia
- 页面间数据：通过 `wx.navigateTo({ url, success })` 携带参数，或全局 `app.globalData`
- 简单场景直接用 `this.setData()`

### Canvas 分享海报方案

- 使用**原生 Canvas 2D API**（非 `canvas` 组件的旧版接口）
- 绘制内容：日期标签 + 日报标题 + AI 毒舌金句 + 小程序码（通过 `wxacode.getUnlimited` 获取）
- 导出：`canvasToTempFilePath` → `wx.showShareImage` / 分享时自动使用

---

## 5. 数据模型

### JSON 文件结构（每份日报）

```json
{
  "date": "2026-05-07",
  "category": "articles",
  "title": "行业日报",
  "items": [
    {
      "title": "Tesla hits Musk's threshold...",
      "url": "https://...",
      "source": "The Verge",
      "published": "2026-05-04T10:28:01-04:00",
      "content": "...",
      "summary": "Tesla 里程达标，马斯克设的 flag 又立住了...",
      "heat_score": 95
    }
  ]
}
```

### AI 毒舌点评结构（生成后追加或独立文件）

```json
{
  "date": "2026-05-07",
  "category": "articles",
  "toxic_comment": "今天的科技圈依然充满戏剧性，Tesla 又在里程表上刷存在感了...",
  "emotion_radar": {
    "angry": 20,
    "sarcastic": 65,
    "sad": 10,
    "funny": 45,
    "neutral": 15
  }
}
```

---

## 6. AI 毒舌点评 · Prompt 设计

```
你是「毒舌日报」的 AI 评论员，负责对新闻进行犀利毒舌点评。

风格要求：
- 毒舌但有信息量，不纯骂人
- 带点讽刺幽默感
- 一句话点评，不超过 50 字
- 中文输出

请输出 JSON 格式：
{
  "toxic_comment": "...",
  "emotion_radar": {
    "angry": 0-100,
    "sarcastic": 0-100,
    "sad": 0-100,
    "funny": 0-100,
    "neutral": 0-100
  }
}

以下是要点评的新闻：
<每条新闻的 title + content>
```

> **注意**：emotion_radar 五个维度之和不做归一化，展示时按比例换算。

---

## 7. MVP 开发计划

### Day 1：脚手架 + 首页 + 数据拉取

| 任务 | 时长 | 说明 |
|------|------|------|
| 微信小程序注册 + 开发工具安装 | 30min | 需主体认证 |
| 项目初始化（app.json 路由） | 15min | 3个 tab：日报列表/我的/关于 |
| Vant Weapp 引入 | 15min | npm 方式 |
| 静态托管搭建（GitHub Pages） | 1h | GitHub 仓库 + Actions |
| 数据推送脚本编写 | 1h | 现有 Cron → GitHub sync |
| 日报列表页（首页） | 1.5h | 三类日报 tab 切换 |
| 数据拉取 + 渲染 | 1h | wx.request + setData |

**Day 1 产出**：可看到三份日报列表，首页骨架完成 ✅

### Day 2：详情页 + 毒舌点评 + 情绪雷达

| 任务 | 时长 | 说明 |
|------|------|------|
| 日报详情页 | 1.5h | 列表页 → 详情，图文排版 |
| AI 毒舌点评接入 | 1h | DeepSeek V4 Pro 调用（先硬编码测试数据） |
| 情绪雷达可视化 | 1h | Canvas 绘制五维雷达图 |
| 分享卡片 Canvas 绘制 | 2h | 核心功能：导出带小程序码的图片 |
| 小程序码生成（wxacode.getUnlimited） | 1h | 需已发布小程序或体验版 |

**Day 2 产出**：完整浏览流程 + 分享卡片 ✅

### Day 3：测试 + 体验版 + 上线

| 任务 | 时长 | 说明 |
|------|------|------|
| 真机测试（网络/机型兼容） | 1.5h | 务必真机，模拟器 Canvas 表现不同 |
| 微信审核材料准备 | 1h | 截图+说明+隐私协议 |
| 提交审核 | 30min | |
| 备案/域名（如需） | 1h | 小程序需 HTTPS 域名 |
| 上线 + 监控 | 30min | 数据拉取成功率 |

**Day 3 产出**：小程序上线可用 🔥

---

## 8. 目录结构

```
toxic-daily/
├── miniprogram/                     # 小程序源码
│   ├── app.js                       # 应用入口
│   ├── app.json                     # 全局配置
│   ├── app.wxss                     # 全局样式
│   ├── components/                  # 组件
│   │   ├── daily-card/              # 日报卡片组件
│   │   ├── toxic-comment/           # 毒舌点评组件
│   │   └── emotion-radar/           # 情绪雷达组件（Canvas）
│   └── pages/
│       ├── index/                   # 首页：日报列表
│       │   ├── index.js
│       │   ├── index.wxml
│       │   └── index.wxss
│       ├── detail/                  # 日报详情
│       │   ├── detail.js
│       │   ├── detail.wxml
│       │   └── detail.wxss
│       ├── share/                   # 分享海报页（无 tab）
│       │   ├── share.js
│       │   ├── share.wxml
│       │   └── share.wxss
│       └── about/                   # 关于页（无 tab）
│           └── about.js
├── server/                          # 后端同步脚本
│   ├── sync-to-github.js            # JSON → GitHub 同步
│   └── package.json
└── README.md
```

---

## 9. 关键页面框架

### app.json（路由配置）

```json
{
  "pages": [
    "pages/index/index",
    "pages/detail/detail",
    "pages/share/share",
    "pages/about/about"
  ],
  "tabBar": {
    "list": [
      { "pagePath": "pages/index/index", "text": "日报", "iconPath": "...", "selectedIconPath": "..." },
      { "pagePath": "pages/about/about", "text": "关于", "iconPath": "...", "selectedIconPath": "..." }
    ]
  }
}
```

### 数据拉取（index.js 摘要）

```javascript
// 拉取日报数据
async function loadDaily(category = 'articles') {
  const date = formatDate(new Date())  // YYYYMMDD
  const url = `https://<username>.github.io/toxic-daily/raw_${category}_${date}.json`
  const res = await wx.request({ url })
  return res.data
}

// 切换 tab 时调用
onTabItemTap({ index }) {
  const categories = ['articles', 'dev', 'social']
  this.setData({ activeCategory: categories[index] })
  loadDaily(categories[index]).then(data => this.setData({ dailyData: data }))
}
```

### Canvas 分享卡片（核心逻辑）

```javascript
// share.js
async function generateShareCard(dailyData, toxicComment) {
  const ctx = wx.createCanvasContext('shareCanvas')
  const W = 375, H = 550  // 朋友圈海报比例

  // 背景
  ctx.setFillStyle('#1a1a2e')
  ctx.fillRect(0, 0, W, H)

  // 顶部渐变色块
  const gradient = ctx.createLinearGradient(0, 0, W, 0)
  gradient.addColorStop(0, '#ff6b6b')
  gradient.addColorStop(1, '#ffa502')
  ctx.setFillStyle(gradient)
  ctx.fillRect(0, 0, W, 120)

  // 日期标签
  ctx.setFontSize(24)
  ctx.setFillStyle('#fff')
  ctx.fillText(dailyData.date, 20, 80)

  // 日报标题
  ctx.setFontSize(32)
  ctx.setFillStyle('#fff')
  ctx.fillText(dailyData.title, 20, 180)

  // 毒舌金句
  ctx.setFontSize(18)
  ctx.setFillStyle('#ff6b6b')
  ctx.fillText(toxicComment.toxic_comment.slice(0, 60) + '...', 20, 240)

  // 情绪雷达迷你图（Canvas 嵌套）
  // ... 雷达图绘制代码 ...

  // 小程序码（通过 wxacode.getUnlimited 换取）
  if (this.qrCodePath) {
    ctx.drawImage(this.qrCodePath, 130, 420, 115, 115)
  }

  ctx.draw()

  // 导出
  setTimeout(() => {
    wx.canvasToTempFilePath({
      canvasId: 'shareCanvas',
      success: res => this.setData({ shareImage: res.tempFilePath })
    })
  }, 300)
}
```

### 情绪雷达（Canvas 雷达图）

```javascript
// emotion_radar.js Component
drawRadar(emotions) {
  const ctx = this.ctx
  const cx = 75, cy = 75, r = 60
  const labels = ['愤怒', '讽刺', '悲伤', '有趣', '中性']
  const values = [emotions.angry, emotions.sarcastic, emotions.sad, emotions.funny, emotions.neutral]

  // 绘制五边形背景 + 数据填充
  // ... 5 边雷达图数学计算 ...
  // 外框线 + 渐变填充区域
}
```

---

## 10. 风险点 & 应对

### 风险 1：微信小程序审核被拒

| 常见拒绝原因 | 应对 |
|-------------|------|
| 隐私协议缺失 | 必须在小程序中补充隐私政策页面 |
| 内容涉及 AI 评论（需资质） | MVP 阶段声明"AI 点评仅供参考，不构成投资建议" |
| 诱导分享 | 分享卡片做成可选项，而非强制分享 |
| 类新闻/媒体资质 | 日报内容为客观摘录，非原创报道，问题不大 |

### 风险 2：AI 毒舌点评延迟

| 场景 | 应对 |
|------|------|
| DeepSeek 响应慢（>3s） | 前端显示 skeleton 加载态，后端预生成写入 JSON |
| API 调用失败 | 容灾：展示"暂无毒舌"，不阻塞阅读 |
| 冷启动（首个用户） | **预生成策略**：Cron 产出 JSON 时同步调用 AI，生成 `toxic_comment` 字段写入同一文件 |

> **推荐**：采用"预生成"方案——AI 点评在 Cron 阶段就生成完毕，小程序只拉 JSON，不实时调 AI。

### 风险 3：冷启动加载体验

| 优化手段 | 说明 |
|---------|------|
| 分页懒加载 | 列表一次只渲染 10 条 |
| 数据缓存 | `wx.setStorageSync('daily_cache', data)`，下次先展示缓存再刷新 |
| Skeleton 骨架屏 | Vant Weapp 支持 `<van-skeleton />` |
| 预拉取 | 小程序启动时静默请求当天数据 |
| 图片懒加载 | Vant `lazy-load` 属性 |

---

## 11. 后续扩展（上线后）

1. **用户收藏** → 微信云开发数据库 or 各自端本地存储
2. **推送订阅** → `wx.requestSubscribeMessage` 每日推送
3. **评论互动** → 接入腾讯云·移动解析或自建 API
4. **多语言** → 开发者日报可加中英双语

---

## 12. 快速启动清单

```bash
# 1. 注册小程序账号
# https://mp.weixin.qq.com/

# 2. 初始化项目
cd /root/.openclaw/workspace
npx wepy-cli init toxic-daily   # 或直接在微信开发者工具新建项目

# 3. 安装 Vant
cd toxic-daily/miniprogram
npm init -y
npm i vant-weapp -S --production

# 4. 搭建 GitHub Pages 静态托管（见 server/sync-to-github.js）

# 5. 配置域名（微信需 HTTPS）
# GitHub Pages 自带 HTTPS，无需额外配置

# 6. 开发/调试
# 微信开发者工具 → 导入项目 → 填 AppID → 开启"不校验合法域名"
```

---

*本方案聚焦 MVP 快速落地，架构预留扩展性。祝项目顺利上线！ 🚀*