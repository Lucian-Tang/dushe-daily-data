# 「品味挑战」小程序 MVP 技术方案

**作者：** Stephen（研发）
**日期：** 2026-05-09
**版本：** v1.0

---

## 1. 小程序架构设计

### 1.1 页面路由

采用微信小程序原生路由，共 8 个页面：

```
pages/
├── index          # 首页（今日挑战入口 + 快捷开始）
├── challenge      # 挑战答题页（核心玩法）
├── result         # 答题结果页（正确率 + 解析 + 分享卡片）
├── rank           # 排行榜页（周榜 + 好友榜 + 分类榜）
├── profile        # 个人主页（段位 + 标签 + 成就徽章）
├── pk             # 好友 PK 准备/匹配页
├── pk-result      # PK 结果页
└── categories     # 练习场分类选题页
```

**路由参数设计：**

| 页面 | 路由 | 参数 | 说明 |
|------|------|------|------|
| challenge | `/pages/challenge/main` | `category`, `count`, `mode` | mode= daily/practice/pk |
| result | `/pages/result/main` | `sessionId`, `score`, `correct`, `total` | sessionId 关联本次答题记录 |
| rank | `/pages/rank/main` | `type` | type= weekly/friends/category |
| pk | `/pages/pk/main` | `pkId` | pkId 为云函数生成的匹配 ID |

### 1.2 组件树

```
App
├── TabBar（固定底部 4 tab）
│   ├── 首页（index）
│   ├── 练习场（categories）
│   ├── 排行榜（rank）
│   └── 我的（profile）
│
└── 页面级组件（各 page 独立）
    ├── ChallengePage
    │   ├── QuestionCard          # 题目卡片（含 AB 对比 UI）
    │   ├── OptionButton (×2/3)   # 选项按钮
    │   ├── ProgressBar           # 进度条（当前题数/总题数）
    │   ├── TimerBar              # 倒计时条（可选）
    │   └── AnalysisPanel          # 答题后解析浮层
    │
    ├── ResultPage
    │   ├── ScoreCircle           # 环形得分展示
    │   ├── RankCard              # 击败百分比 + 段位展示
    │   ├── ShareCardCanvas       # 分享卡片 Canvas 渲染区
    │   └── ActionBar             # 分享/再来一局/邀请好友
    │
    ├── ProfilePage
    │   ├── RankBadge             # 段位徽章大图
    │   ├── TasteRadarChart       # 品味雷达图（多维度）
    │   ├── AchievementGrid       # 成就徽章列表
    │   └── HistoryList           # 历史挑战记录
    │
    └── PKPage
        ├── OpponentCard          # 对手信息卡
        ├── PKScoreBoard          # 实时比分（双方选项对比）
        └── PKResultCard          # PK 结局展示
```

### 1.3 数据流

**全局状态管理（小程序 globalData + 封装 store）：**

```
globalData
├── user
│   ├── openId          # 微信 openId（云开发获取）
│   ├── nickname        # 微信昵称
│   ├── avatarUrl       # 头像
│   ├── rank            # 当前段位
│   ├── score           # 当前积分
│   ├── streakDays      # 连胜天数
│   └── tasteProfile    # 品味雷达维度数据
│
├── session
│   ├── currentChallenge   # 当前挑战 sessionId
│   ├── answers           # 当前答题记录 [{qId, answer, correct, time}]
│   └── startTime         # 挑战开始时间
│
└── kv
    ├── dailyQuestions      # 今日挑战题目（缓存）
    ├── questionCache       # 已加载题目详情
    └── lastSyncTime        # 上次题库同步时间
```

**页面间数据传递：**
- 同城页面跳转：URL query params + globalData
- 云开发数据库：关键用户数据（积分/段位/成就）持久化到云 DB
- 分享参数：scene 短链（解析后跳转指定页面+参数）

---

## 2. 题库数据格式设计

### 2.1 JSON Schema（题目主文件）

题库托管在 GitHub Pages，每个分类一个 JSON 文件：

```
https://luxmind.github.io/taste-challenge/questions/v1/
├── index.json              # 题库索引（含版本号 + 各分类 MD5）
├── ai-images.json          # AI 图识别题
├── prompts.json            # Prompt 品味题
├── design.json             # 设计审美题
├── writing.json            # 文案标题题
└── metadata.json           # 题库统计元信息
```

### 2.2 题目 JSON 结构

```json
{
  "version": "1.0.0",
  "lastUpdated": "2026-05-09T00:00:00Z",
  "totalCount": 200,
  "categories": ["ai-images", "prompts", "design", "writing"],
  "questions": [
    {
      "id": "ai-img-001",
      "category": "ai-images",
      "type": "choice-binary",
      "difficulty": 2,
      "tags": ["photography", "portrait", "realism"],
      "tasteDimension": "visual",
      "content": {
        "description": "以下哪张图片是 AI 生成的？",
        "media": [
          { "type": "image", "url": "https://cdn.luxmind.com/qs/ai-img-001-a.jpg", "aspectRatio": "4:3" },
          { "type": "image", "url": "https://cdn.luxmind.com/qs/ai-img-001-b.jpg", "aspectRatio": "4:3" }
        ],
        "options": [
          { "id": "A", "label": "左图", "targetMediaIndex": 0 },
          { "id": "B", "label": "右图", "targetMediaIndex": 1 }
        ],
        "correctAnswer": "B",
        "explanation": "右图在皮肤纹理和眼神光线方面存在不自然的细节，这是当前主流 AI 生成图的典型特征。AI 生成的皮肤通常过于光滑，瞳孔光源与环境光不一致。",
        "learningPoint": "学会识别 AI 生成图像的细微瑕疵：皮肤纹理、眼神光、背景一致性。",
        "distractorExplanations": {
          "A": "左图是真实摄影作品，光影自然，色调有真实的胶片感。"
        }
      },
      "scoring": {
        "baseScore": 10,
        "timeBonus": 3,
        "streakBonus": 2
      }
    },
    {
      "id": "prompt-042",
      "category": "prompts",
      "type": "choice-binary",
      "difficulty": 3,
      "tags": ["landscape", "midjourney", "cinematic"],
      "tasteDimension": "prompt",
      "content": {
        "description": "以下两个 Midjourney Prompt，哪个生成效果更好？",
        "media": [
          {
            "type": "prompt-text",
            "text": "a beautiful landscape, mountains, sunset, golden hour, epic, dramatic",
            "modelHint": "v6.1"
          },
          {
            "type": "prompt-text",
            "text": "dramatic mountain landscape at golden hour, ancient peaks draped in mist, volumetric god rays piercing through clouds, cinematic wide-angle shot, anamorphic lens flare, 8K resolution, National Geographic photography --ar 16:9 --stylize 200",
            "modelHint": "v6.1"
          }
        ],
        "options": [
          { "id": "A", "label": "Prompt A（简洁版）" },
          { "id": "B", "label": "Prompt B（详细版）" }
        ],
        "correctAnswer": "B",
        "explanation": "详细的 Prompt 包含更多控制性指令（镜头语言、光线描述、风格参数），输出质量更稳定、可控性更强。",
        "learningPoint": "好的 Prompt = 具体描述 + 风格词 + 技术参数。不要只依赖抽象形容词。"
      },
      "scoring": {
        "baseScore": 15,
        "timeBonus": 3,
        "streakBonus": 2
      }
    },
    {
      "id": "design-015",
      "category": "design",
      "type": "choice-ternary",
      "difficulty": 3,
      "tags": ["poster", "typography", "commercial"],
      "tasteDimension": "visual",
      "content": {
        "description": "以下三张营销海报，哪张点击率最高？（仅从视觉设计角度判断）",
        "media": [
          { "type": "image", "url": "https://cdn.luxmind.com/qs/design-015-a.jpg", "aspectRatio": "3:4" },
          { "type": "image", "url": "https://cdn.luxmind.com/qs/design-015-b.jpg", "aspectRatio": "3:4" },
          { "type": "image", "url": "https://cdn.luxmind.com/qs/design-015-c.jpg", "aspectRatio": "3:4" }
        ],
        "options": [
          { "id": "A", "label": "海报 A" },
          { "id": "B", "label": "海报 B" },
          { "id": "C", "label": "海报 C" }
        ],
        "correctAnswer": "C",
        "explanation": "海报 C 在视觉层级、信息 hierarchy 和 CTA 设计上更优：主标题大而醒目，副标题清晰，行动号召按钮对比度强。",
        "learningPoint": "商业设计评估维度：信息层级 → 可读性 → CTA 醒目度 → 整体调性一致。",
        "distractorExplanations": {
          "A": "海报 A 排版过于拥挤，视觉焦点不明确。",
          "B": "海报 B 色调偏暗，在信息流中容易被忽略。"
        }
      },
      "scoring": {
        "baseScore": 15,
        "timeBonus": 3,
        "streakBonus": 2
      }
    }
  ]
}
```

### 2.3 题目类型枚举

| type | 说明 | 选项数 |
|------|------|--------|
| `choice-binary` | 二选一（哪张是 AI 生成的/哪个 Prompt 更好） | 2 |
| `choice-ternary` | 三选一（哪张海报点击率最高） | 3 |
| `ranking` | 排序题（5 张图按审美排序） | 5 |
| `prompt-optimize` | Prompt 优化挑战（用户输入，AI 评分） | — |

### 2.4 题库索引文件（index.json）

```json
{
  "version": "1.2.0",
  "baseUrl": "https://luxmind.github.io/taste-challenge/questions/v1/",
  "lastSync": "2026-05-09T00:00:00Z",
  "categories": [
    {
      "name": "ai-images",
      "displayName": "AI 鉴定师",
      "file": "ai-images.json",
      "count": 80,
      "md5": "a3f5c8d2e1b4...",
      "difficultyDistribution": { "easy": 30, "medium": 35, "hard": 15 }
    },
    {
      "name": "prompts",
      "displayName": "Prompt 大师",
      "file": "prompts.json",
      "count": 50,
      "md5": "b7c9d1e3f2a5..."
    },
    {
      "name": "design",
      "displayName": "设计审美",
      "file": "design.json",
      "count": 40,
      "md5": "c8d2e4f1a3b6..."
    },
    {
      "name": "writing",
      "displayName": "文案高手",
      "file": "writing.json",
      "count": 30,
      "md5": "d9e3f5a2b1c7..."
    }
  ]
}
```

---

## 3. 评分算法（段位计算逻辑）

### 3.1 积分体系

每次挑战根据以下维度计算得分：

```
总得分 = Σ( baseScore_i + timeBonus_i + streakBonus_i + difficultyBonus_i )

其中：
- baseScore_i：题目基础分（10/15/20，根据难度）
- timeBonus_i：答题速度奖励（<5s → +3分，5-15s → +1分）
- streakBonus_i：连胜奖励（连续答对 ≥3 题时额外 +2 分/题）
- difficultyBonus_i：高难度题答对额外 +5 分
```

### 3.2 段位计算

段位根据**累计积分**计算，每个赛季（季度）重置：

| 段位 | 名称 | 分数区间 | 徽章 | 升级条件 |
|------|------|----------|------|----------|
| 青铜 | 观察者 | 0 – 499 | 🥉 | — |
| 白银 | 鉴赏者 | 500 – 1499 | 🥈 | 500 分 |
| 黄金 | 品鉴师 | 1500 – 3499 | 🥇 | 1500 分 |
| 铂金 | 审美家 | 3500 – 6999 | 💎 | 3500 分 |
| 钻石 | 品味大师 | 7000 – 14999 | 💠 | 7000 分 |
| 星耀 | 美学权威 | 15000+ | ⭐ | 15000 分 |

**段位保护规则：**
- 段位只升不降（季度重置前）
- 每赛季提供 1 次「保级保护」（触发条件：段位已达白银且本季度挑战≥10次）

### 3.3 周榜积分

周榜单独统计本周积分：

```javascript
// 每周一 00:00 GMT+8 重置
weeklyScore = Σ(每日挑战得分 × 周倍数)
周倍数 = 第1天×1.0, 第2天×1.1, 第3天×1.2, ..., 第7天×1.6
```

### 3.4 击败百分比算法

```
击败比例 = (分数高于我的用户数 + 分数等于我的用户数 × 0.5) / 总用户数 × 100%
```

用户挑战结果页显示「击败了 XX% 的用户」，数据来源为云数据库聚合查询。

---

## 4. 分享卡片生成方案

### 4.1 方案选型：Canvas 前端绘制

**选型理由：**
- 避免后端渲染服务，降低成本和延迟
- 小程序 Canvas API 完善，支持离屏绘制
- 卡片生成后可本地保存或直接调起分享

### 4.2 卡片模板类型

**模板 A：挑战结果卡（基础卡）**
```
┌─────────────────────────────────┐
│  [背景渐变 + 品牌色]             │
│                                 │
│  [用户头像] [昵称] 品味段位       │
│  🔥 连胜 7 天                   │
│                                 │
│  本次得分：85/100               │
│  击败了 72% 的用户               │
│                                 │
│  [段位大徽章]                   │
│                                 │
│  [小程序码]                     │
└─────────────────────────────────┘
```

**模板 B：段位晋升卡**
```
┌─────────────────────────────────┐
│  🎉 段位升级！                   │
│                                 │
│  [旧段位图标] → [新段位图标]     │
│  青铜 → 白银                     │
│                                 │
│  你已超越 80% 的用户             │
│                                 │
│  [继续挑战按钮引导]              │
└─────────────────────────────────┘
```

**模板 C：PK 胜利卡**
```
┌─────────────────────────────────┐
│  🏆 PK 胜利                     │
│                                 │
│  [我]  3  :  2  [对手昵称]       │
│                                 │
│  我的段位：💎 铂金               │
│  额外 +100 XP                   │
│                                 │
│  [再战一局] [邀请观战]           │
└─────────────────────────────────┘
```

### 4.3 Canvas 绘制实现架构

```javascript
// 分享卡片生成器类
class ShareCardGenerator {
  constructor(template, userData, resultData) {
    this.template = template  // 模板配置
    this.userData = userData // 用户数据（昵称/头像/段位）
    this.resultData = resultData // 挑战结果数据
  }

  // 模板配置示例（模板 A）
  static TEMPLATE_A = {
    width: 430,
    height: 600,
    background: { type: 'gradient', colors: ['#667eea', '#764ba2'] },
    elements: [
      { type: 'avatar', x: 30, y: 30, size: 60, borderRadius: 30 },
      { type: 'nickname', x: 100, y: 40, fontSize: 28, color: '#fff' },
      { type: 'rankBadge', x: 30, y: 520, width: 100, height: 100 },
      { type: 'qrcode', x: 330, y: 480, width: 80, height: 80 },
      // ...
    ]
  }

  async generate() {
    const ctx = wx.createCanvasContext('shareCanvas')
    // 1. 绘制背景
    // 2. 绘制用户信息
    // 3. 绘制结果数据
    // 4. 绘制段位徽章
    // 5. 绘制小程序码
    ctx.draw()
    // 导出为图片
    return await this.exportImage()
  }
}
```

### 4.4 徽章图片资源

段位徽章图片存储在 CDN，随模板硬编码路径：

```
https://cdn.luxmind.com/taste-challenge/badges/
├── bronze.png      # 120×120px
├── silver.png
├── gold.png
├── platinum.png
├── diamond.png
└── star.png
```

### 4.5 小程序码生成

通过微信云调用 `wxacode.get` 接口生成参数小程序码，scene 参数包含挑战 ID 和分享者 openId。

---

## 5. 微信云开发需求清单

### 5.1 云函数列表

| 云函数名 | 触发方式 | 职责 |
|---------|---------|------|
| `login` | 客户端调用 | 微信登录，生成/更新用户记录，返回 openId + 匿名 uid |
| `getUserProfile` | 客户端调用 | 获取当前用户积分/段位/成就数据 |
| `submitAnswer` | 客户端调用 | 提交单次答题结果，写入答题记录，更新积分和段位 |
| `getDailyQuestions` | 客户端调用 | 获取今日挑战题目列表（每日5题，从题库抽取） |
| `createPKRoom` | 客户端调用 | 创建 PK 房间，生成 roomId，返回给双方 |
| `joinPKRoom` | 客户端调用 | 加入已有 PK 房间，校验对方在线状态 |
| `syncPKAnswer` | 客户端调用（高频） | 同步 PK 双方答题状态，判定 PK 胜负 |
| `getWeeklyLeaderboard` | 客户端调用 | 获取周榜前100名（含分页） |
| `getFriendsLeaderboard` | 客户端调用 | 获取好友排行榜（微信关系链） |
| `getAchievementList` | 客户端调用 | 获取用户成就列表及解锁状态 |
| `claimAchievement` | 客户端调用 | 领取新解锁成就（触发写 DB + 通知） |
| `generateShareCard` | 云调用（内部） | 生成参数小程序码（调用微信 wxacode.getUnlimited） |
| `reportQuestion` | 客户端调用 | 用户举报疑似错误题目，写入反馈表 |

### 5.2 数据库集合设计

```
集合：users
{
  _id: ObjectId,
  openId: String (唯一索引),
  unionId: String,
  nickname: String,
  avatarUrl: String,
  totalScore: Number,
  weeklyScore: Number,
  rank: String,           // bronze/silver/gold/platinum/diamond/star
  streakDays: Number,
  lastChallengeDate: Date,
  tasteProfile: {
    visual: Number,       // 视觉品味分
    prompt: Number,       // Prompt 品味分
    design: Number,       // 设计品味分
    writing: Number       // 文案品味分
  },
  achievements: [String], // 已解锁成就 ID 列表
  pkStats: {
    total: Number,
    win: Number,
    lose: Number
  },
  createdAt: Date,
  updatedAt: Date
}

集合：challenge_sessions
{
  _id: ObjectId,
  sessionId: String (UUID, 唯一索引),
  openId: String (索引),
  category: String,
  mode: String,          // daily/practice/pk
  questions: [String],   // 题目 ID 数组
  answers: [
    { qId: String, userAnswer: String, correct: Boolean, timeMs: Number }
  ],
  totalScore: Number,
  correctCount: Number,
  totalCount: Number,
  rankBefore: String,
  rankAfter: String,
  createdAt: Date
}

集合：pk_rooms
{
  _id: ObjectId,
  roomId: String (唯一索引),
  openIdA: String,
  openIdB: String,
  questions: [String],
  currentQuestionIndex: Number,
  scores: { A: Number, B: Number },
  status: String,        // waiting/in_progress/finished
  winner: String,       // openId of winner
  createdAt: Date,
  updatedAt: Date,
  expireAt: Date         // 30分钟无操作自动过期
}

集合：achievements
{
  _id: ObjectId,
  achievementId: String (唯一索引),
  name: String,
  description: String,
  icon: String,
  condition: Object,     // 解锁条件配置
  reward: Number        // 解锁奖励 XP
}

集合：question_feedback
{
  _id: ObjectId,
  qId: String (索引),
  openId: String,
  type: String,          // wrong_answer/buggy_explanation_other
  content: String,
  createdAt: Date
}
```

### 5.3 安全与权限

- 所有云函数需验证 `wxcontext.OPENID`，禁止未授权访问
- `submitAnswer` 云函数需加并发锁（同一 sessionId 并发提交防护）
- `pk_rooms` expireAt 字段配合定时触发器清理过期房间
- 用户 openId 不可泄露给客户端（仅内部使用）

---

## 6. 性能考量

### 6.1 题库分片加载策略

**加载策略：懒加载 + 预加载结合**

```
首次启动：
  → 只加载 index.json（含 MD5 校验 + 题库索引）
  → 不加载任何题目内容

进入「今日挑战」：
  → 加载 category=random（按比例抽取）的完整题目文件
  → 5 道题目 JSON 大小约 50-100KB（GZIP 后 ~10-20KB）
  → 用户网络 < 1Mbps 时，感知延迟 < 1s

进入「练习场」分类页：
  → 按需加载对应分类 JSON（用户点击分类时触发）
  → 分类内题目支持分页（每页 20 题）

图片预加载（用户进入挑战页前）：
  → 同时发起所有题目图片请求（最多 6 张图）
  → 使用 wx.downloadFile 缓存到本地
  → 预加载完成前显示加载骨架屏
```

**CDN + 协议：**
- 题库 JSON：GitHub Pages（CDN 加速，GZIP）
- 图片资源：CDN 域名（https://cdn.luxmind.com），WebP 格式优先
- 地图/徽章等小图：Base64 内联或雪碧图

### 6.2 缓存策略

```javascript
// 本地缓存策略
const CACHE_STRATEGY = {
  // 题库索引：有效期 24 小时，变更检测靠 MD5
  indexJson: { key: 'question_index_v1', maxAge: 24 * 3600 * 1000 },

  // 题目内容：按分类缓存，MD5 校验更新
  questions: { key: 'qs_{category}_v{md5}', maxAge: 7 * 24 * 3600 * 1000 },

  // 用户积分/段位：实时性要求高，仅内存缓存，页面切出时写 DB
  userProfile: { key: 'user_profile', maxAge: 300 * 1000 }, // 5分钟

  // 今日挑战：每天 00:00 刷新
  dailyQuestions: { key: 'daily_qs_{date}', maxAge: 24 * 3600 * 1000 }
}
```

### 6.3 图片优化

| 优化项 | 方案 |
|--------|------|
| 格式 | 优先 WebP，降级 JPEG |
| 尺寸 | 服务端多档（thumbnail 320px / medium 640px / full 1080px）|
| 懒加载 | 视口外图片不加载（IntersectionObserver） |
| 占位 | 骨架屏/shimmer 占位 |
| 内存 | 小程序内存限制 200MB，图片解码缓存最多 20 张 |

### 6.4 列表虚拟滚动

排行榜等长列表使用 `recycle-view` 组件（微信小程序官方虚拟列表），仅渲染可视区域 DOM。

---

## 7. 项目文件结构

```
/root/.openclaw/workspace/projects/taste-challenge/
├── miniprogram/                    # 微信小程序主项目
│   ├── app.js                      # 应用入口
│   ├── app.json                    # 应用配置（pages + tabBar）
│   ├── app.wxss                    # 全局样式
│   │
│   ├── pages/                      # 页面目录
│   │   ├── index/                  # 首页
│   │   │   ├── index.js
│   │   │   ├── index.wxml
│   │   │   ├── index.wxss
│   │   │   └── index.json
│   │   │
│   │   ├── challenge/              # 挑战答题页
│   │   │   ├── challenge.js
│   │   │   ├── challenge.wxml
│   │   │   ├── challenge.wxss
│   │   │   └── challenge.json
│   │   │
│   │   ├── result/                 # 结果页
│   │   │   ├── result.js
│   │   │   ├── result.wxml
│   │   │   ├── result.wxss
│   │   │   └── result.json
│   │   │
│   │   ├── categories/             # 练习场分类页
│   │   │   ├── categories.js
│   │   │   ├── categories.wxml
│   │   │   └── categories.wxss
│   │   │
│   │   ├── rank/                   # 排行榜页
│   │   │   ├── rank.js
│   │   │   ├── rank.wxml
│   │   │   └── rank.wxss
│   │   │
│   │   ├── profile/               # 个人主页
│   │   │   ├── profile.js
│   │   │   ├── profile.wxml
│   │   │   ├── profile.wxss
│   │   │   └── profile.json
│   │   │
│   │   ├── pk/                    # PK 匹配页
│   │   │   ├── pk.js
│   │   │   ├── pk.wxml
│   │   │   └── pk.wxss
│   │   │
│   │   └── pk-result/             # PK 结果页
│   │       ├── pk-result.js
│   │       ├── pk-result.wxml
│   │       └── pk-result.wxss
│   │
│   ├── components/                 # 业务组件库
│   │   ├── question-card/
│   │   ├── option-button/
│   │   ├── rank-badge/
│   │   ├── achievement-badge/
│   │   ├── share-card-canvas/
│   │   ├── progress-bar/
│   │   ├── taste-radar/
│   │   └── pk-scoreboard/
│   │
│   ├── lib/                       # 工具库
│   │   ├── request.js             # 云函数调用封装
│   │   ├── cache.js               # 缓存策略封装
│   │   ├── question-loader.js      # 题库加载器
│   │   ├── score-calculator.js     # 评分算法
│   │   ├── rank-updater.js        # 段位更新逻辑
│   │   ├── share-card.js          # 分享卡片生成器
│   │   └── utils.js               # 通用工具函数
│   │
│   ├── assets/                    # 静态资源
│   │   ├── images/
│   │   │   ├── badges/            # 段位徽章图片
│   │   │   ├── icons/             # UI 图标
│   │   │   └── backgrounds/      # 卡片背景图
│   │   ├── fonts/                # 字体文件（如有）
│   │   └── sounds/               # 音效（可选）
│   │
│   └── config/
│       ├── api.js                 # 云函数请求路径配置
│       └── constants.js           # 段位阈值、积分常量
│
├── cloudfunctions/               # 微信云开发云函数
│   ├── login/
│   │   └── index.js
│   ├── getUserProfile/
│   │   └── index.js
│   ├── submitAnswer/
│   │   └── index.js
│   ├── getDailyQuestions/
│   │   └── index.js
│   ├── createPKRoom/
│   │   └── index.js
│   ├── joinPKRoom/
│   │   └── index.js
│   ├── syncPKAnswer/
│   │   └── index.js
│   ├── getWeeklyLeaderboard/
│   │   └── index.js
│   ├── getFriendsLeaderboard/
│   │   └── index.js
│   ├── getAchievementList/
│   │   └── index.js
│   └── reportQuestion/
│       └── index.js
│
├── questions/                    # 题库源文件（GitHub Pages 同步源）
│   ├── v1/
│   │   ├── index.json
│   │   ├── ai-images.json
│   │   ├── prompts.json
│   │   ├── design.json
│   │   └── writing.json
│   └── README.md                  # 题库维护说明
│
├── scripts/                      # 运营维护脚本
│   ├── build-questions.js        # 题库打包脚本（生成单文件 + MD5）
│   └── sync-to-gh-pages.js       # 同步到 GitHub Pages
│
├── docs/                         # 开发文档
│   ├── api-spec.md               # 云函数 API 规格说明
│   ├── db-schema.md              # 数据库设计文档
│   └── component-guide.md        # 组件开发规范
│
├── project.config.json           # 小程序项目配置文件
├── README.md                     # 项目说明
└── package.json                  # npm 依赖（eslint/prettier/eslint-plugin-wxapp）
```

### 7.1 关键路径说明

| 路径 | 用途 |
|------|------|
| `miniprogram/pages/challenge/` | 核心答题流程，性能最关键 |
| `miniprogram/components/share-card-canvas/` | Canvas 绘制核心组件 |
| `cloudfunctions/submitAnswer/` | 最高频云函数，需做并发防护 |
| `questions/v1/` | 题库源文件，发布时同步到 GitHub Pages |
| `scripts/sync-to-gh-pages.js` | 题库发布流水线脚本 |

---

## 附录：技术债务与后续规划

1. **图片 CDN**：当前设计依赖 CDN，需提前确认 luxmind CDN 域名备案
2. **PK 实时性**：syncPKAnswer 高频调用考虑 WebSocket 或微信实时消息推送替代轮询
3. **题库运营**：需建立题目审核流程，避免错误答案影响用户体验
4. **企业版**：如后续启动 B2B，需新增管理后台云函数和数据导出功能