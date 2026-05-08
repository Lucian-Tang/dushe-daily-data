# 早报配图质量改善指南 v1.0
> Thomas 内容策划部分 | 复盘日期：2026-05-02

---

## 一、现状问题分析

### 1.1 首期封面图问题（morning-news-gen-cover-003）

基于实际输出观察到的典型问题：

| 问题 | 描述 | 严重程度 |
|------|------|---------|
| 文字可读性差 | 深色背景+浅色文字，平台压缩后更模糊 | 🔴 高 |
| 关键词不突出 | 封面缺少本期核心主题词 | 🔴 高 |
| 风格过于抽象 | 与科技新闻调性有偏差 | 🟡 中 |
| 尺寸适配问题 | 不同平台要求的裁剪比例不同 | 🟡 中 |
| 无品牌标识 | 缺少统一视觉识别 | 🟡 中 |

---

## 二、配图风格规范

### 2.1 色彩体系

**主色调（三选一）**

| 风格 | 主色 | 辅色 | 适用场景 |
|------|------|------|---------|
| 科技蓝 | #1A73E8 | #4285F4 / #34A853 | 通用科技新闻 |
| 暗夜紫 | #6C5CE7 | #A29BFE / #2D3436 | AI/编程相关 |
| 深空灰 | #2D3436 | #636E72 / #00B894 | 安全/基础设施 |

**背景规范**
- ✅ 渐变背景（从深到浅或对角线渐变）
- ✅ 深色背景 #1a1a2e 或 #16213e
- ❌ 纯白/纯黑背景
- ❌ 过于复杂的纹理

**文字颜色**
- 主标题：白色 #FFFFFF
- 副标题/标签：浅灰 #E0E0E0 或亮蓝 #64B5F6
- 数字：高亮黄 #FFD93D 或亮绿 #00E676

### 2.2 构图原则

**三分法**
- 视觉焦点放在画面1/3处（非正中心）
- 留白比例30%左右，不拥挤

**元素层次（从底到高）**
```
Layer 1: 渐变背景（最底层）
Layer 2: 抽象装饰元素（网格/线条/粒子）
Layer 3: 数据可视化元素（图表/图标）
Layer 4: 文字层（标题/标签，最高）
```

**常见构图禁忌**
- ❌ 文字贴近边缘（至少留8%边距）
- ❌ 多个视觉焦点（只能有一个核心）
- ❌ 与内容无关的装饰元素

### 2.3 字体规范

| 用途 | 字体 | 大小建议 |
|------|------|---------|
| 封面大标题 | Arial Bold / Source Han Sans Bold | 占画面高度15-20% |
| 副标题/日期 | Arial / Source Han Sans | 占画面高度8-10% |
| 标签/角标 | Roboto Mono | 占画面高度5-6% |

---

## 三、提示词优化建议

### 3.1 现有提示词问题

**原提示词：**
```
A modern tech news cover image, dark navy background with gradient,
stylized data visualization elements, bold headline text placeholder,
professional and clean design, 16:9 aspect ratio, no photographs
```

**问题诊断：**
- 过于泛化，缺少本期具体主题
- 没有指定颜色精确值
- 没有强调文字可读性
- 没有给出构图参考
- 缺少品牌元素要求

### 3.2 优化后的提示词模板

**标准版封面图：**
```
A modern tech news cover image for [本期主题],
dark navy gradient background (#1a1a2e to #16213e),
data visualization elements (abstract nodes and connection lines),
bold headline text placeholder at top,
[本期关键词] concept icon in center,
professional typography, white main title text,
date badge in corner, subtle brand logo,
16:9 aspect ratio, no photographs, clean modern tech aesthetic,
8K quality, high contrast for text readability
```

**分平台适配版：**

*微信公众号：*
```
Tech news cover, WeChat article style, 900x383px aspect ratio,
dark blue gradient background, clean modern design,
professional headline typography, subtle tech pattern overlay,
no photographs, high contrast text on dark background
```

*X/Twitter：*
```
Twitter card cover image, 1600x900px,
dark theme with blue accent (#1A73E8),
minimalist tech aesthetic, bold title text area,
social media friendly, modern clean design, 16:9 ratio
```

*知乎：*
```
Zhihu article cover, 840x460px aspect ratio,
tech blue gradient (#1A73E8 to #4285F4),
knowledge-style design, subtle graph/chart elements,
clean sans-serif typography, professional appearance, 16:9
```

### 3.3 内容辅助图提示词

**信息图风格：**
```
Minimalist infographic, dark theme palette,
single concept visualization,
data visualization with clean lines,
no text required, modern tech aesthetic,
professional appearance, suitable for article body
```

**对比图风格：**
```
Side-by-side comparison visual, dark theme,
two concept contrast layout,
clean modern design, tech aesthetic,
professional typography, 16:9 ratio
```

---

## 四、各平台配图规格对照表

### 4.1 综合规格表

| 平台/用途 | 尺寸(px) | 比例 | 文件大小 | 格式 |
|----------|---------|------|---------|------|
| 通用封面 | 1200×630 | 1.91:1 | ≤5MB | PNG/JPG |
| 微信公众号封面 | 900×383 | 2.35:1 | ≤2MB | JPG |
| 微信公众号次图 | 800×450 | 16:9 | ≤2MB | JPG |
| 知乎封面 | 840×460 | 16:9 | ≤5MB | PNG/JPG |
| X/Twitter卡片 | 1600×900 | 16:9 | ≤5MB | PNG/JPG |
| X/Twitter推文图 | 1200×675 | 16:9 | ≤5MB | PNG/JPG |
| RSS/OG Image | 1200×630 | 1.91:1 | ≤5MB | PNG/JPG |
| 微博卡片 | 800×800 | 1:1 | ≤5MB | PNG/JPG |
| LinkedIn | 1200×627 | 1.91:1 | ≤5MB | PNG/JPG |

### 4.2 输出建议

**实际工作流：**
1. 先生成通用版 1200×630px（最高质量）
2. 再用同一张图针对不同平台裁剪适配
3. 重要平台（公众号/X/知乎）单独微调

**分辨率选择：**
- 首选用 2K (2048×1080) 或 4K (3840×2160) 生成
- 平台压缩后降质严重，高分辨率留有余地

---

## 五、优秀配图案例参考

### 5.1 值得参考的配图风格

**科技媒体风格（对标）**
- The Verge：简洁扁平，大字体主标题，低饱和度背景
- TechCrunch：动感强，高对比，橙/蓝色调
- Ars Technica：学术感，暗色系，数据图表融入

**技术公众号风格（中文）**
- 极客公园：清新明亮，图标化元素多
- 差评：黑色幽默风格，配图有态度
- 爱范儿：极简，留白多，高级感

### 5.2 AI生成图片风格推荐关键词

```
✅ 推荐加入的词：
- "8K quality"
- "high contrast"
- "professional typography"
- "clean modern design"
- "data visualization elements"
- "no photographs"
- "dark theme"
- "blue accent color"

❌ 避免使用的词：
- "realistic"（容易产生照片，风格偏离）
- "cartoon"（过于幼稚）
- "vintage"（风格不搭）
- "busy background"（杂乱）
```

---

## 六、检查清单

### 封面图生成后自检

- [ ] 文字在深色背景下清晰可读
- [ ] 本期核心关键词在图中体现
- [ ] 比例符合目标平台要求
- [ ] 无版权/商标问题
- [ ] 整体风格与科技新闻调性一致
- [ ] 日期和品牌标识已添加
- [ ] 不同平台尺寸已适配

---

## 七、迭代记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| v0.1 | 2026-05-02 | 初稿完成，基于首期封面图问题分析 |
| v1.0 | 2026-05-02 | 提示词优化，规格表完善，案例参考补充 |

---

*Thomas 内容策划部分完成。配图技术实现（提示词执行/图片生成）由 Stephen 负责。*