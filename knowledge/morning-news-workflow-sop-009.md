# 早报生产SOP — morning-news-workflow-solidify-009

> 本文档固化「采集→选题→封面→文案→发布」全流程标准化操作步骤
> 版本：v1.0 | 日期：2026-05-02 | 负责人：Stephen + Thomas

---

## 一、流程总览

```
[14:30] 采集并行 → [14:50] 选题 → [15:10] 封面+文案并行 → [15:25] Lucia发布
   ↓           ↓            ↓              ↓                  ↓
 Stephen    Thomas      Stephen+Thomas    Thomas写→Stephen图     Lucia
```

**时间节点（单次早报，总耗时约55分钟）：**
- 14:30-14:50 采集（20分钟）
- 14:50-15:10 选题+文案框架（20分钟）
- 15:10-15:25 配图+全文（15分钟）
- 15:25-15:35 发布（10分钟）

---

## 二、各环节标准操作步骤

### Step 0 — 准备（14:25）

| 操作 | 执行方 | 标准 |
|------|--------|------|
| 确认当日特殊节日/事件 | Lucia | 检查日历，有重大事件提前通知Thomas调整选题方向 |
| 创建状态文件 | Lucia | 在 `~/.openclaw/shared/tasks/morning-news-YYYYMMDD.json` 创建任务记录 |
| 通知开始 | Lucia | 群里发：【开始】早报生产任务，ID: morning-news-YYYYMMDD |

---

### Step 1 — 采集（14:30-14:50）

**执行方：Stephen（并行执行4个采集器）**

#### 1.1 启动采集脚本

```bash
cd /root/.openclaw/workspace/daily-digest

# 并行跑4个采集器（后台运行）
python3 collectors/hn/hn_collector.py &
python3 collectors/v2ex/v2ex_collector.py &
python3 collectors/baidu/baidu_collector.py &
python3 collectors/github/github_collector.py &

wait  # 等待所有采集完成
```

#### 1.2 输出文件校验

| 平台 | 期望文件 | 校验标准 |
|------|---------|----------|
| HN | `collectors/hn/hn_top_YYYYMMDD_HHMMSS.json` | ≥20条，每条含 title/score/comments/url |
| V2EX | `collectors/v2ex/v2ex_top_YYYYMMDD_HHMMSS.json` | ≥9条，每条含 title/node/replies |
| 百度 | `collectors/baidu/baidu_hot_YYYYMMDD_HHMMSS.json` | ≥20条，每条含 title/hotScore/labelTag |
| GitHub | `collectors/github/github_trending_YYYYMMDD_HHMMSS.json` | ≥10条，每条含 name/stars/language/description |

#### 1.3 状态回报

```
【完成】task_id: morning-news-run-collector-001, step: collection, output: HN 30条/V2EX 9条/百度 50条/GitHub 25条
```

#### 1.4 异常处理

| 异常 | 处理方式 |
|------|---------|
| 单平台采集失败 | 该平台跳过，其他平台继续；最终报告中标注「[平台]数据缺失」 |
| 采集超时（>15分钟） | 标记failed，启动fallback使用最近一次缓存数据（`raw/hot-raw-YYYYMMDD.json`） |
| 数据量不足 | 记录warnning，Thomas选题时注意数据源偏差 |
| 百度API返回空 | 自动切换HTML正则兜底（已内置在baidu_collector.py） |

---

### Step 2 — 选题（14:50-15:05）

**执行方：Thomas**

#### 2.1 选题标准

从采集数据中选 **3个本期选题**，按以下优先级：

1. **热度**：分数/热度值排名靠前
2. **时效性**：当天新发生的事件优先
3. **可深挖**：有2个以上扩展角度（技术原理+商业影响+社区反应）
4. **受众匹配**：工程师/开发者读者群

#### 2.2 选题输出格式

每个选题输出：
```
## 选题{N}
标题：[一句话标题]
来源：[HN/V2EX/百度/GitHub]
热度信号：{分数/热度值}
核心角度：[从哪个角度切入]
延伸角度：[还有什么可写的]
```

#### 2.3 选完后的动作

- 群里发：【完成】task_id: morning-news-topic-select-002, step: topic-selection, output: Top3选题（附标题）
- Stephen同步开始配图生成（**不必等文案完成**）

#### 2.4 异常处理

| 异常 | 处理 |
|------|------|
| 采集数据质量差（全是旧闻） | 标注数据质量问题，降低该来源权重，跳过异常数据 |
| 热度信号不明确 | Thomas主观判断为主，参考历史数据趋势 |
| 多个好选题冲突 | Thomas选择最有一个，报Lucia确认 |

---

### Step 3 — 配图（15:05-15:20）

**执行方：Stephen（与Step 4文案并行）**

#### 3.1 配图生成标准

**规格：**
- 尺寸：1200×630px（微信封面图标准比例）
- 风格：深色科技风，暗色系背景（#1a1a2e 或类似），高对比度
- 字体：清晰可辨，无中文（避免渲染问题）
- 布局：标题文字居中或左侧，视觉元素丰富但不杂乱

#### 3.2 配图Prompt模板

```
A sleek tech newsletter cover image, dark theme, futuristic technology aesthetic, 
neon blue and purple accent colors, digital circuit patterns in background, 
bold headline text "【话题标题】" in clean sans-serif font, modern minimal design, 
high contrast, wide composition, suitable for social media sharing, 1200x630px
```

#### 3.3 生成后检查

| 检查项 | 标准 |
|--------|------|
| 分辨率 | ≥1024×536 |
| 可读性 | 文字在缩略图场景下依然可辨 |
| 无乱码 | 无中文、无乱码字符 |
| 相关性 | 视觉元素与选题内容相关 |

#### 3.4 异常处理

| 异常 | 处理 |
|------|------|
| 生成图片质量差 | 调整prompt，重新生成，最多3次 |
| 多次生成仍失败 | 降级使用纯色背景+文字图，标注「简化版封面」 |
| 尺寸不符 | 使用 image_generate 的 size 参数指定 1024x1024 或 1024x512 |

---

### Step 4 — 文案（15:05-15:20）

**执行方：Thomas（与Step 3配图并行）**

#### 4.1 文案结构

```
标题：[吸引点击的标题，≤30字]
副标题：[可选，一句话说明本文价值]

一、选题背景（200字）
  - 什么事/为什么重要

二、技术解读（300字）
  - 技术原理/实现细节
  - 为什么这个技术有意思

三、行业影响（200字）
  - 对从业者/用户/市场的影响

四、社区反应（100字）
  - HN/V2EX等社区的讨论热度

五、延伸阅读（100字）
  - 相关工具/项目/延伸阅读链接
```

#### 4.2 质量标准

- 800-1500字
- 有数据支撑（采集数据中的具体数字）
- 有观点，不只是信息罗列
- 适配微信公众号格式（段落不超过5行，避免大段文字）

#### 4.3 输出格式

写完后的文件：`daily-digest/output/morning-news-YYYYMMDD-v1.md`

#### 4.4 异常处理

| 异常 | 处理 |
|------|------|
| 写不完（>15分钟） | 标注超时，优先保证核心模块（一/二/三），跳过延伸阅读 |
| 数据不足 | 减少模块数量，主攻最丰富的角度 |
| 被要求重写 | Thomas重新写，Stephen同步更新配图 |

---

### Step 5 — 发布（15:25-15:35）

**执行方：Lucia**

#### 5.1 发布渠道与规则

| 渠道 | 时机 | 格式要求 |
|------|------|----------|
| 微信公众号 | 主渠道，完整发布 | 标题+正文+封面图，格式要求：段落≤5行，重点加粗 |
| 知乎专栏 | 同步发布 | 标题+正文，底部附微信公众号摘要版链接 |
| Twitter/X摘要 | 有爆点时发 | 140字以内，附链接，格式：标题+核心数字+链接 |

#### 5.2 发布前检查

- [ ] 封面图已上传到微信公众号
- [ ] 标题已确认（与Thomas确认）
- [ ] 无错别字（发给Lucia前Thomas自检）
- [ ] 内链/外链已确认有效

#### 5.3 异常处理

| 异常 | 处理 |
|------|------|
| 微信公众号上传失败 | 跳过，发布知乎专栏+Twitter，微信公众号改天补发 |
| 链接失效 | 删除失效链接，保留文字内容 |
| 图片上传失真 | 压缩后重传，或降低分辨率 |

---

## 三、时间节点汇总

```
14:25 — Lucia确认日历，发【开始】通知
14:30 — Stephen并行启动4个采集器
14:50 — 采集完成，Stephen回报；Thomas开始选题
15:00 — Thomas完成选题，Stephen开始配图（并行）
15:05 — Thomas开始写文案（并行）
15:20 — 配图+文案同时完成（Thomas写完回报，Stephen图完成）
15:25 — Lucia开始发布
15:35 — 发布完成，群里发【完成】通知，更新飞书看板
```

---

## 四、双文档规范

| 文档类型 | 飞书文档 | 本地文件 |
|----------|----------|----------|
| SOP本文 | 创建飞书文档，链接填入bitable「产出链接」 | `/root/.openclaw/workspace/knowledge/morning-news-workflow-sop-009.md` |
| 每期执行记录 | 复用本期产出文档（如早报全文） | 采集JSON文件保留30天 |

---

## 五、异常处理总览

| 场景 | 级别 | 处理方式 |
|------|------|----------|
| 单平台采集失败 | P2 | 跳过，数据标注缺失，继续其他平台 |
| 采集整体超时 | P1 | 触发fallback，使用最近缓存数据，通知Thomas数据可能旧 |
| 选题数据质量差 | P1 | Thomas调整选题标准，降低该来源权重 |
| 配图生成失败 | P2 | 最多重试3次，仍失败用简化版 |
| 文案超时 | P1 | 优先保核心模块，跳过延伸阅读 |
| 发布失败 | P0 | 降级发布知乎+Twitter，微信公众号改天补 |
| 整个流程超时>60分钟 | P0 | Lucia立即通知Boss，决策是否取消本期 |

---

*本文档为早报生产SOP v1.0，每期执行后由Stephen/Thomas复盘更新*