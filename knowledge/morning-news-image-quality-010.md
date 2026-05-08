# 早报封面图最佳实践指南 — morning-news-image-quality-010

> 分析本期封面图质量问题，参考科技媒体/技术公众号优秀案例，输出配图规范
> 版本：v1.0 | 日期：2026-05-02 | 负责人：Stephen + Thomas

---

## 一、本期封面图质量复盘

### 问题1：Prompt描述模糊

**问题描述：**
本期封面图生成时使用的prompt偏模糊，仅包含「dark theme, futuristic」等宽泛词汇，缺乏具体场景描述。

**影响：**
- 生成结果风格随机，有时过于抽象，有时过于具体
- 与选题内容的关联性不稳定

**改进方向：**
- prompt中应包含选题的具体视觉元素关键词
- 示例：选题「USB-C检测工具」→ prompt中应有「cable, connector, port, device」等具体视觉词

### 问题2：风格不一致

**问题描述：**
不同选题的封面图风格差异较大（有时赛博朋克，有时极简），与公众号整体视觉形象不统一。

**改进方向：**
建立固定的风格模板（见第三章），所有封面图遵循同一风格体系

### 问题3：文字处理问题

**问题描述：**
- 部分图片中英文字符渲染异常（乱码/缺失）
- 标题文字在微信预览缩略图中太小，不可辨

**改进方向：**
- 避免在prompt中直接描述文字效果，图片不包含可读文字
- 指定图片布局时注明「text should be readable in small thumbnail」

### 问题4：比例不规范

**问题描述：**
生成的图片偶尔出现非1200×630比例，在微信公众号封面位置会被裁剪。

**改进方向：**
使用 `size: "1024x537"` 或 `aspectRatio: "16:9"` 参数明确指定比例

---

## 二、科技媒体/技术公众号优秀配图案例分析

### 参考案例1：The Verge

**特点：**
- 大量使用高饱和度摄影图（非插画）
- 标题字体粗大、纯色背景
- 科技感强但不花哨

**可借鉴：**
- 摄影图 > 插画图（真实性感更强）
- 纯色或浅色背景 + 大字标题

### 参考案例2：Ars Technica

**特点：**
- 深色/暗色调为主
- 技术细节图（如芯片、电路板）常见
- 文字覆盖层清晰

**可借鉴：**
- 深色科技风适合技术选题
- 技术细节图（如芯片近景、设备特写）有专业感

### 参考案例3：36氪

**特点：**
- 封面图多为信息图（数据可视化风格）
- 颜色鲜艳，视觉冲击力强
- 图表化表达数据趋势

**可借鉴：**
- 数据类选题可用信息图风格
- 橙红/蓝紫渐变配色有活力

### 参考案例4：量子位

**特点：**
- AI/技术选题多用抽象插画
- 蓝色调为主，科技感统一
- 人物插画 + 科技元素组合

**可借鉴：**
- AI类选题适用抽象插画风格
- 建立蓝色调主视觉体系

### 参考案例5：少数派

**特点：**
- 扁平插画为主，颜色活泼
- 文字与图片融合度高
- 适合年轻受众

**可借鉴：**
- 工具类选题适合扁平插画
- 可爱/活泼风格适合科普内容

---

## 三、封面图最佳实践规范

### 3.1 图片规格

| 参数 | 标准值 | 说明 |
|------|--------|------|
| 尺寸 | 1200×630px | 微信公众号封面图标准比例 |
| 最小分辨率 | 1024×537px | 低于此质量不过审 |
| 格式 | PNG/JPG | PNG优先，质量更高 |
| 宽高比 | 16:9 | 固定比例 |

### 3.2 视觉风格规范

**建立统一的「早报视觉体系」：**

| 元素 | 规范 |
|------|------|
| 主色调 | 深色系背景（#1a1a2e 或 #0d1117），科技感强 |
| 辅助色 | 蓝紫渐变（#4f46e5 → #7c3aed） |
| 强调色 | 霓虹蓝（#06b6d4）、霓虹紫（#8b5cf6）用于文字高亮 |
| 视觉元素 | 电路图/芯片/数据流/代码/几何图形 |
| 文字 | 无可读文字（避免渲染问题）；如需标题效果，用Figma/PS后加 |

### 3.3 Prompt模板库

**A型：技术产品选题**
```
A sleek tech newsletter cover image, dark theme (#1a1a2e background), 
futuristic technology aesthetic, circuit board patterns and glowing data streams, 
neon blue (#06b6d4) and purple (#8b5cf6) accent lighting, modern minimal layout, 
no text, high contrast, 16:9 aspect ratio, photorealistic digital art style
```

**B型：AI/数据选题**
```
A sleek AI-themed newsletter cover, deep space dark background (#0d1117), 
floating neural network nodes with glowing connections, data visualization elements, 
cyan and violet gradient lighting, futuristic minimal design, no readable text, 
ultra high detail, 16:9 aspect ratio, cinematic lighting
```

**C型：开源/社区选题**
```
A sleek open source themed newsletter cover, dark background with geometric patterns, 
interconnected nodes representing community collaboration, code snippets subtly visible, 
electric blue (#3b82f6) and amber (#f59e0b) accent colors, modern flat design, 
no text overlay, 16:9 ratio, clean vector art style
```

**D型：工具/效率选题**
```
A sleek productivity tool newsletter cover, dark grey background (#1f2937), 
minimalist iconography, clean geometric shapes, subtle gradient glow, 
professional and clean aesthetic, no text, 16:9 aspect ratio, modern UI design style
```

### 3.4 生成后必检清单

- [ ] 尺寸 = 1200×630（或比例16:9）
- [ ] 无乱码/可读文字
- [ ] 视觉元素与选题相关
- [ ] 风格与早报视觉体系一致（深色科技风）
- [ ] 缩略图场景下文字/图形仍可辨
- [ ] 无水印/无版权问题

### 3.5 简化版兜底方案

当AI生成多次失败时，使用以下兜底方案：

```
纯色背景（#1a1a2e） + 居中几何图形（圆形/六边形）+ 简单渐变效果
工具：Canva / Figma手动快速制作
时间要求：<5分钟完成
```

---

## 四、Prompt优化指南

### 4.1 好的Prompt要素

1. **具体场景词**：比「tech」更具体，如「chip fabrication, neural network visualization」
2. **明确颜色值**：避免「bright colors」，改为「cyan #06b6d4 and violet #8b5cf6」
3. **比例约束**：注明「16:9 aspect ratio」
4. **排除项**：注明「no text, no watermark, no Chinese characters」
5. **质量词**：注明「ultra detailed, 8K, professional」

### 4.2 常见错误

| 错误 | 原因 | 修正 |
|------|------|------|
| 图片含乱码中文 | prompt中包含中文字符 | 去掉中文，只用英文描述 |
| 比例不对被裁剪 | 未指定16:9 | 加 `aspectRatio: "16:9"` |
| 风格不一致 | 未固定视觉体系 | 使用上面的模板库，不自由发挥 |
| 缩略图不可辨 | 视觉元素太细 | 加 `high contrast, bold shapes` |

---

## 五、持续优化机制

1. **每期封面图存档**：保存到 `daily-digest/output/covers/YYYYMMDD-cover.png`
2. **每周复盘**：Stephen/Thomas每周一会检视本周7张封面图质量
3. **Prompt迭代**：根据检视结果更新Prompt模板库
4. **.bad case记录**：记录质量差的prompt和原因，持续优化

---

## 六、双文档

| 文档 | 路径 |
|------|------|
| 飞书文档 | 创建飞书文档，链接填入bitable |
| 本地文件 | `/root/.openclaw/workspace/knowledge/morning-news-image-quality-010.md` |

---

*本指南 v1.0，每期执行后更新Prompt模板库和.bad case记录*