# Phase 3 配图方案（补）

**负责人：** Stephen  
**完成时间：** 2026-04-30 08:30（预计）  
**需求确认：** 小红书平台，静态图，关键词自动匹配

---

## 一、技术方案：Unsplash API

**为什么选 Unsplash：**
- 免费额度充足（1000次/小时）
- 高质量摄影图片，适合小红书风格
- 有明确版权授权（可商用）

## 二、核心流程

```
选题关键词 → Unsplash搜索 → 下载图片 → 裁剪适配小红书尺寸 → 输出文件
```

**图片尺寸：** 小红书推荐 3:4 竖版（1080×1440 或 720×960）

## 三、关键词映射表

| 糗事类型 | 搜索关键词 |
|----------|-----------|
| AI fail | technology error, robot fail, computer glitch |
| AI mistake | wrong answer, confused, mistake |
| hilarious | funny fail, laughing, comedy |
| AI disaster | broken computer, system crash |

## 四、脚本结构

```
scripts/
├── image_fetcher.py      # Unsplash API 获取图片
├── image_cropper.py      # 裁剪为3:4
└── image_pipeline.sh     # 串联流程
```

## 五、API 准备

需要配置：
- Unsplash API Access Key（免费注册）
- 存储在环境变量或 config.json

## 六、Phase 5 串联

输入：选题 JSON（含 title/keywords）  
输出：裁剪好的图片文件路径 → 传给文案生成环节

---
