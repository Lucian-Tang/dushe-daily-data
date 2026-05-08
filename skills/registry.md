# Skills Registry

> 维护人：Lucia | 最后更新：2026-05-09

## 已安装技能（22 个）

### 飞书生态
| 技能 | 来源 | 用途 | 风险 | 评分 |
|------|------|------|------|------|
| feishu-sync | workspace | 飞书文档双轨同步 | 🔴高 | 4/5 |
| feishu-doc-write | workspace | 飞书文档创建/编辑 | 🔴高 | 4/5 |

### 搜索引擎
| 技能 | 来源 | 用途 | 风险 | 评分 |
|------|------|------|------|------|
| openclaw-tavily-search | ClawHub | Web 搜索（Tavily API） | 🟡中 | 4/5 |
| wechat-article-search | ClawHub | 微信公众号文章搜索 | 🟡中 | 3/5 |

### 浏览器/爬虫
| 技能 | 来源 | 用途 | 风险 | 评分 |
|------|------|------|------|------|
| agent-browser-clawdbot | workspace | Headless 浏览器自动化 | 🔴高 | 4/5 |
| scrapling-official | ClawHub | 高级反反爬（Cloudflare 绕过） | 🟢低 | 5/5 |
| web-tools-guide | workspace | Web 工具使用指南 | 🟢低 | 5/5 |

### 热榜/舆情
| 技能 | 来源 | 用途 | 风险 | 评分 |
|------|------|------|------|------|
| web-hot | workspace | 微博/知乎/B站/百度/头条热榜 | 🟢低 | 4/5 |
| cn-trends-aggregator | workspace | 中文+全球热榜聚合 | 🟢低 | 4/5 |
| baidu-hot-monitor | workspace | 百度热搜监控 | 🟢低 | 3/5 |
| douyin-hot | workspace | 抖音热榜 | 🟢低 | 3/5 |
| hot-news-aggregator | workspace | 国内外社会/科技/军事新闻 | 🟢低 | 3/5 |

### 社交媒体
| 技能 | 来源 | 用途 | 风险 | 评分 |
|------|------|------|------|------|
| twitter-collector | workspace | Twitter 推文采集 | 🟡中 | 3/5 |

### 开发工具
| 技能 | 来源 | 用途 | 风险 | 评分 |
|------|------|------|------|------|
| github | workspace | GitHub Issues/PR/CI 操作 | 🟡中 | 4/5 |

### 记忆/知识管理
| 技能 | 来源 | 用途 | 风险 | 评分 |
|------|------|------|------|------|
| memory-manager | workspace | 记忆压缩检测+快照+搜索 | 🟢低 | 4/5 |
| memory-maintenance | workspace | 记忆维护（清洗+归档） | 🟢低 | 3/5 |
| memory-hygiene | workspace | LanceDB 向量记忆清理 | 🟢低 | 3/5 |

### 办公/效率
| 技能 | 来源 | 用途 | 风险 | 评分 |
|------|------|------|------|------|
| automation-workflows | workspace | 自动化工作流设计 | 🟢低 | 3/5 |
| tencent-docs | workspace | 腾讯文档操作 | 🟡中 | 3/5 |
| tencent-meeting-skill | workspace | 腾讯会议操作 | 🟡中 | 2/5 |

### 其他
| 技能 | 来源 | 用途 | 风险 | 评分 |
|------|------|------|------|------|
| weather | workspace | 天气查询 | 🟢低 | 4/5 |
| skillhub-preference | workspace | 技能发现偏好 | 🟢低 | 3/5 |
| find-skills | workspace | 技能搜索安装 | 🟢低 | 4/5 |
| summarize | 内置 | 摘要生成 | 🟢低 | 3/5 |

## 待合并（冗余组）
- ⚠️ `web-hot` + `cn-trends-aggregator` → 功能重叠 70%
- ⚠️ `memory-manager` + `memory-maintenance` + `memory-hygiene` → 三合一
- ⚠️ `feishu-doc-write` + `feishu-sync` → 功能重叠

## 已卸载
- ❌ tencentcloud-lighthouse-skill (未使用 + 高风险)
- ❌ tencent-cos-skill (未使用 + 高风险)

## 已拒绝安装
- ❌ twitter-openclaw/openclaw-x (ClawHub评分 1.088，写权限)
- ❌ office (功能重叠)
- ❌ self-improve-agent (功能重叠)
- ❌ skill-vetter (手工 review 够用)
