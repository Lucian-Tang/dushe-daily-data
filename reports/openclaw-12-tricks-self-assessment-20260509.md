# OpenClaw 12 技巧自评报告

**团队：** Lucia/COO + Thomas/产品 + Stephen/工程 + 校验官/QA
**评估人：** Stephen（工程）
**日期：** 2026-05-09
**背景：** 4人团队（1人+3 agent），Lucian 为 CEO，Lucia 为监督者，Thomas 产品经理，Stephen 研发，校验官 QA

---

## 概览评分总表

| # | 技巧 | 状态 | 评分(1-5) | 优先级 |
|---|------|------|-----------|--------|
| 1 | SOUL 文件 | ✅ 已用 | 4 | P1 |
| 2 | Identity 文件 | ✅ 已用 | 4 | P1 |
| 3 | Users 文件 | ✅ 已用 | 3 | P2 |
| 4 | Agents 多代理 | ✅ 已用 | 3 | P0 |
| 5 | Tools 配置 | ⚠️ 部分用 | 2 | P1 |
| 6 | 记忆增强 | ⚠️ 部分用 | 3 | P0 |
| 7 | Errors 文档 | ❌ 没用 | 1 | P2 |
| 8 | 自主权限 | ⚠️ 部分用 | 2 | P1 |
| 9 | 技能加载 | ⚠️ 部分用 | 3 | P0 |
| 10 | 多实例 | ⚠️ 部分用 | 2 | P2 |
| 11 | Heartbeat | ✅ 已用 | 4 | P0 |
| 12 | 群聊管理 | ✅ 已用 | 3 | P1 |

---

## 逐项评估

### 1. SOUL 文件

**状态：** ✅ 已用（每个 agent 均有独立 SOUL.md）

**评分：4/5**

**现状分析：**
- Lucia 主 Agent：SOUL 完整，定义"毒舌但有温度"风格 + 主动搭话规范
- Stephen（工程）：SOUL 定义"工程质量第一"，输出标准清晰
- Thomas（产品）：沿用 AGENTS.md 默认模板，未定制产品侧 SOUL
- 校验官（QA）：无独立 SOUL，直接复用 checklist-prompts.md 中的审查原则

**改进建议：**
- Thomas 应补充专属 SOUL，定义产品决策风格（如：数据驱动、克制 MVP、竞品优先）
- 校验官 SOUL 应独立出来，定义"不生产只把关"的角色边界和审查语气
- 各 SOUL 之间建议有交叉引用（如 Stephen SOUL 引用"安全有一票否决权"，Lucia SOUL 引用此条作团队纪律）

---

### 2. Identity 文件

**状态：** ✅ 已用（每个 agent 均有独立 IDENTITY.md）

**评分：4/5**

**现状分析：**
- Lucia：Name/Emoji/Role/Vibe 齐全，Avatar 为 "not set yet"
- Stephen：Name+Role+Vibe+工作边界清晰，包含安全一票否决权声明
- Thomas/校验官：依赖 AGENTS.md 全局定义，独立 IDENTITY 缺失

**改进建议：**
- Thomas 和校验官应补充独立 IDENTITY.md，与 Stephen 同级
- Avatar 配置列入待办（Lucia 的 avatar 至今未设置）
- IDENTITY 建议统一字段：Name / Emoji / Role / Vibe / 工作边界 / 专业领域

---

### 3. Users 文件

**状态：** ✅ 已用（主 workspace 有 USER.md，子 agent 未单独配置）

**评分：3/5**

**现状分析：**
- 主 workspace USER.md 记录 Lucian 基本信息（Name/Timezone/偏好）
- 各子 agent 未配置独立 USER.md，不清楚各自"服务对象"是谁
- 无跨 agent 的团队成员信息共享机制

**改进建议：**
- 考虑建立 `shared/team-members.md`，记录 4 人团队各自角色和联系上下文，供所有 agent 引用
- 子 agent 的 USER.md 可简化（指向 team-members.md + 个人专属 context）
- 目前 USER.md 只服务主 agent，子 agent 无法感知 Lucian 的个性化偏好（如"不喜欢废话"这个细节 Stephen 并不一定每次都读到）

---

### 4. Agents 多代理

**状态：** ✅ 已用（4 agents 运行中，Lucia 监督分发）

**评分：3/5**

**现状分析：**
- 架构清晰：Lucia(监督) → Thomas(产品) + Stephen(工程) + 校验官(QA)
- 协作规则定义在 agents/AGENTS.md，分工明确
- Stephen 的 status.json 有完整 phase1 产出记录，Thomas 有 last_output
- 校验官为最新建立（2026-05-08），工作流已定义但实际送审流程尚未完全跑通

**改进建议（P0）：**
- 缺乏机器可读的 agent 能力注册表（哪个 agent 能做什么，无统一清单）
- 任务分发依赖 Lucia 人工判断，建议在 agents/AGENTS.md 增加「能力矩阵」章节
- 校验官的 spawn 流程应写成 SOP，减少 Lucia 每次手动构造 prompt 的成本
- 缺少跨 agent 状态同步机制：Thomas 完成任务 → Stephen 需要知道 → 目前靠 Lucia 中转，效率低

---

### 5. Tools 配置

**状态：** ⚠️ 部分用（主 agent 有 TOOLS.md，子 agent 未配置）

**评分：2/5**

**现状分析：**
- 主 workspace 的 TOOLS.md 基本为空（只有模板示例，无实际内容）
- 各子 agent 的 TOOLS.md 同样为模板状态
- config/ 目录下有 sources.yaml/dev 配置，但与 TOOLS.md 完全脱节
- skills/ 目录有 20+ 技能，但哪些已激活、哪些有配置需求，无统一记录

**改进建议：**
- TOOLS.md 应作为各 agent 的"本地工具清单"，记录已配置的 CLI 路径、API key 位置、快捷命令
- 建议增加「已激活技能注册表」：技能名 / 配置状态 / 最后验证时间
- 主 agent TOOLS.md 补充飞书/Tavily/腾讯文档等已配置工具的接入说明
- 当前 TOOLS.md 为空是较大风险点——新开 session 时无法快速知道工具环境

---

### 6. 记忆增强

**状态：** ⚠️ 部分用（MEMORY.md 有内容，daily/ 有日志，但分散且不规范）

**评分：3/5**

**现状分析：**
- 主 agent：MEMORY.md + memory/YYYY-MM-DD.md 双重机制，Stephen 有独立 MEMORY.md
- memory/ 目录已有 2026-04-29 → 2026-05-09 共 9 天的日志
- 有 memory-hygiene 和 memory-manager 两个技能，但未见实际使用记录
- heartbeat-state.json 记录检查时间戳，但与记忆系统无联动
- 各 agent memory/ 目录使用程度不一：Stephen 有 daily/ 子目录，Thomas/校验官 无独立记忆积累

**改进建议（P0）：**
- 制定「记忆写入规范」：哪些事件必须记录（决策/错误/完成/阻塞），避免记忆碎片化
- Stephen 的 MEMORY.md 有内容，但 Thomas/校验官 的 memory/ 为空，需要补充基线状态
- 引入 memory_manager 技能进行定期压缩和索引（当前记忆中非结构化，内容增长后检索效率下降）
- 建议增加跨 agent 记忆共享机制：Stephen 的技术决策结论应可被 Thomas 查到

---

### 7. Errors 文档

**状态：** ❌ 没用（不存在专门的错误处理文档）

**评分：1/5**

**现状分析：**
- 整个 workspace 无 errors.md、ERRORS.md 或类似错误知识库
- HEARTBEAT.md 有 cron 故障监控逻辑，但没有系统性的错误分类和恢复手册
- 错误处理知识散落在 daily/ 日志中，无结构化积累
- 飞书日志文件（bitable-*.log）有错误记录，但未提取为知识

**改进建议（P2）：**
- 建立 `errors/README.md`，记录已知错误类型 → 原因 → 解决步骤
- 模板：`## 错误码/关键词 | 原因 | 解决步骤 | 记录时间`
- 每修复一个线上问题，同步更新此文档
- 这是长期技术债务，单次修复不等于真正积累；建议作为 P2 长期建设

---

### 8. 自主权限

**状态：** ⚠️ 部分用（AGENTS.md 有 Red Lines 定义，但权限体系未结构化）

**评分：2/5**

**现状分析：**
- AGENTS.md 定义了"Ask first"和"Safe to do freely"两个层级，但较为粗粒度
- Red Lines 规则存在（不外泄数据、不发外部内容、不做破坏性操作）
- 无正式的角色权限矩阵（如：校验官无权修改代码，Thomas 无权直接触发 cron）
- 实际执行依赖 agent 自觉遵守，无强制校验机制

**改进建议（P1）：**
- 建立 `agents/permissions.md`，明确定义每个 agent 的"可执行操作清单"
- 示例：Stephen 可执行 exec/文件读写，但发飞书消息需 Lucia 中介；Thomas 只能读文件
- HEARTBEAT.md 中的 cron 故障处理涉及自动修复操作，需明确"修复"的具体权限边界
- 建议权限分级：Read / Write / Execute / External（发消息/邮件/发帖）

---

### 9. 技能加载

**状态：** ⚠️ 部分用（skills/ 有 20+ 技能目录，但加载机制不透明）

**评分：3/5**

**现状分析：**
- 有 agent-skills/ 项目（含完整 skills/ 子目录），但未接入主 workspace
- workspace/skills/ 有 20+ 技能（douyin-hot、weather、feishu-*、github 等）
- 无统一的"已安装技能清单 + 激活状态"文档
- skills/ 目录下部分技能有对应 skill 配置文件，部分无（如 cn-trends-aggregator 等）

**改进建议（P0）：**
- 建立 `skills/registry.md`：`技能名 | 来源 | 用途 | 上次使用 | 备注`
- 明确哪些技能在主 agent 激活，哪些只在特定 sub-agent 场景使用
- agent-skills/ 项目与 workspace/skills/ 的关系需明确：是继承还是独立？建议统一纳入 registry
- 部分中文技能（baidu-hot-monitor、douyin-hot）配置状态不明，建议补充配置说明文档

---

### 10. 多实例

**状态：** ⚠️ 部分用（通过 sub-agent spawn 实现，但缺乏统一管理）

**评分：2/5**

**现状分析：**
- OpenClaw 支持 sub-agent 机制（当前任务即通过 sub-agent 完成）
- 无实例生命周期管理：spawn 了多少实例、哪些还在运行、哪些已超时，无统一视图
- 校验官的 spawn 流程依赖 Lucia 手动构造 prompt，无标准化模板
- jobs.json 记录 cron 脚本，但 cron 本身不等于多实例管理

**改进建议（P2）：**
- 建立 `instances/registry.json`：记录活跃实例的 session_id / 创建时间 / 用途 / 状态
- 每次 spawn sub-agent 后登记，完成后标记，减少孤儿实例
- 校验官的 spawn 应标准化为 `openclaw session spawn --agent=qa --context=<task>` 形式
- 这项是 P2，当前规模下 Lucia 人工管理尚可支撑，但团队扩张后会成瓶颈

---

### 11. Heartbeat

**状态：** ✅ 已用（HEARTBEAT.md 定义完整，且实际运行中）

**评分：4/5**

**现状分析：**
- HEARTBEAT.md 定义了心跳扫描（bitable 任务队列 + cron 故障监控）和随机搭话两个模块
- heartbeat-state.json 记录了 lastBitableScan / lastCronCheck 时间戳
- cron 监控逻辑具体（超时→重建，崩溃→分析，连续3次失败→降级）
- 随机搭话规则详细（时间窗口/频率/内容/风格要求）

**改进建议：**
- 随机搭话部分有重复内容（上午搭话/下午搭话各出现两次，内容相同），建议去重
- HEARTBEAT.md 目前只有主 agent 的定义，子 agent（Stephen/Thomas）应有各自的 HEARTBEAT.md
- 建议增加"沉默检测"：如果某 agent 超过 N 小时无心跳，主动告警（当前只监控 cron，不监控 agent 自身状态）
- 随机搭话的内容生成应与 memory/ 联动（基于最新记忆决定话题，而非固定模板）

---

### 12. 群聊管理

**状态：** ✅ 已用（Feishu 群已配置，消息收发规则在 SOUL/AGENTS.md 中分散定义）

**评分：3/5**

**现状分析：**
- Feishu 插件已配置，支持 send/read/react 等操作
- 群聊规则定义在 AGENTS.md（Know When to Speak / React Like a Human）
- 实际群内使用：有任务通知（bitable 扫描结果）、有状态同步（【开始】/【完成】）
- 但"群聊 SOP"不成体系：任务分发、状态同步、校验官送审的群内规范未独立文档化

**改进建议（P1）：**
- 建立 `feishu-group-sop.md`：群内消息规范（哪些场景必须 @谁 / 状态播报格式 / 送审触发词"送审"→ Lucia spawn）
- 当前群聊规则散落在 AGENTS.md + HEARTBEAT.md + 各 SOUL 中，建议独立抽取
- 群内 emoji 反应规范建议具体化（当前 AGENTS.md 只有示例，无强制规范）
- 建议定义消息优先级：P0紧急（cron 崩溃全员通知）/ P1重要（任务开始完成）/ P2普通（闲聊/搭话）

---

## 优先级汇总

### P0（影响当前核心工作流，必须立即推进）

| 技巧 | 原因 |
|------|------|
| **Agents 多代理** | 跨 agent 状态同步和任务分发机制缺失，影响团队协作效率 |
| **记忆增强** | 各 agent 记忆积累不一致，重要决策无结构化积累，存在丢失风险 |
| **技能加载** | 20+ 技能无统一注册表，配置状态不透明，难以排查工具问题 |

### P1（提升团队效率和规范性，建议本月完成）

| 技巧 | 原因 |
|------|------|
| **SOUL 文件** | Thomas/校验官 缺 SOUL，角色边界不清晰 |
| **Identity 文件** | Thomas/校验官 缺 IDENTITY，与 Stephen 不对称 |
| **自主权限** | 权限体系未结构化，安全边界依赖自觉，有风险敞口 |
| **群聊管理** | 群聊 SOP 未文档化，规范散落各处，新成员上手困难 |
| **Heartbeat** | 子 agent 无各自 HEARTBEAT，主 agent 心跳监控不完整 |

### P2（长期建设，不紧急但重要）

| 技巧 | 原因 |
|------|------|
| **Users 文件** | 团队成员信息共享机制缺失，影响个性化服务能力 |
| **多实例** | 实例管理靠人工，团队扩张后必成瓶颈 |
| **Errors 文档** | 错误知识零散积累，无法复用，每次从零排查 |
| **Tools 配置** | TOOLS.md 全局为空，实际工具配置无文档化 |

---

## 快速修复建议（3 项可立即行动）

1. **立刻补充 Thomas/校验官 的 SOUL.md 和 IDENTITY.md**（各 20 行，约 30 分钟）：对齐团队完整性标准
2. **建立 skills/registry.md**（约 15 分钟）：列表形式，`技能名 | 用途 | 配置状态`，立即提升工具透明度
3. **补充主 agent HEARTBEAT.md 的沉默检测逻辑**（约 10 分钟）：增加"agent N 小时无心跳则告警"，完善自监控

---

## 附：各 Agent 当前状态速查

| Agent | SOUL | IDENTITY | HEARTBEAT | MEMORY | status.json |
|-------|------|----------|-----------|--------|-------------|
| Lucia | ✅ 完整 | ✅ 完整 | ✅ 完整 | ✅ 有 | ✅ 有 |
| Stephen | ✅ 完整 | ✅ 完整 | ⚠️ 空(keep empty) | ✅ 有 | ✅ 有 |
| Thomas | ❌ 缺 | ❌ 缺 | ❌ 缺 | ⚠️ 空白 | ✅ 有 |
| 校验官 | ❌ 缺 | ❌ 缺 | ❌ 缺 | ❌ 无 | ✅ 有 |

---

*本报告由 Stephen（工程）撰写，基于 workspace 文件系统扫描 + 运行时状态分析*
*下次评估建议由 Lucia 监督，每 2 周迭代一次*
