# OpenClaw Lobster 任务流框架技术调研报告

> 调研人：Stephen（研发工程师）| 日期：2026-05-07

---

## 1. 概述：Lobster 与 TaskFlow 的关系

**Lobster**（"龙虾"）是 OpenClaw 中的**工作流编排 DSL 层**，以 `.lobster` YAML 文件为载体，负责描述多步骤任务的流程逻辑（条件分支、管道、状态推进）。

**TaskFlow** 是 Lobster 的**底层持久化运行时**。两者是上下层关系：

```
Lobster（YAML 编排层）→ TaskFlow API（持久化/状态管理层）
```

- **TaskFlow** 负责：flow 身份、步骤状态（`currentStep`）、跨步骤状态（`stateJson`）、等待态（`waitJson`）、子任务链接、revision 冲突检测。
- **Lobster** 负责：YAML DSL 解析、step 拓扑（顺序/分支）、`stdin/stdout` 管道连接、`condition` 条件求值、调用 TaskFlow API 完成实际执行。

简言之：**Lobster 是 TaskFlow 的" authoring layer"（创作层），TaskFlow 是 Lobster 的"runtime substrate"（持久化运行时）。**

> Lobster 最早是外部 CLI（`lobster.bot`），现已作为 OpenClaw 插件集成，bundled workflow 在进程内运行（不再跨进程），减少了 transport 开销（CHANGELOG #61523）。

---

## 2. 核心概念

### 2.1 `steps` — 工作流步骤

```yaml
steps:
  - id: fetch
    command: gog.gmail.search --query 'newer_than:1d' --max 20

  - id: classify
    command: openclaw.invoke --tool llm-task ...
    stdin: $fetch.stdout
```

每个 step 有：
- `id`：唯一标识，跨步骤引用的锚点
- `command`：要执行的命令（可以是 CLI 工具、LLM 调用、外部脚本）
- `stdin`（可选）：该 step 的标准输入，引用前序 step 的输出
- `condition`（可选）：Guard 条件，为 `false` 时该 step 跳过

### 2.2 `condition` — 条件 Guard

```yaml
condition: $classify.json.items[0].route == "business"
```

- 使用 [JMESPath](https://jmespath.org/) 表达式对前序 step 的输出进行条件判断
- 结果为 `false` 时该 step 不执行（跳过）
- 支持跨 step 引用：`$<step_id>.stdout`（原始文本）、`$<step_id>.json`（解析后 JSON）

### 2.3 `stdin/stdout` 管道

Lobster 的核心连接机制：**每个 step 的输出自动物化为 `$<step_id>.stdout`**（原始文本）和 **`$<step_id>.json`**（JSON 解析对象），下游 step 通过 `stdin` 引用：

```yaml
# step A 输出 → step B 输入
- id: classify
  stdin: $fetch.stdout   # 接收 fetch step 的标准输出

- id: post_business
  stdin: $classify.stdout  # 接收 classify step 的标准输出
```

### 2.4 跨步骤引用：`$<step_id>.json`

```yaml
condition: $classify.json.items[0].route == "personal"
```

引用 `<step_id>.json` 时，Lobster 内部将前序 step 的 JSON stdout 解析为对象，调用方可用 JMESPath 路径直接访问字段。这使得 step 之间可以传递结构化数据（如分类结果、PR metadata）。

---

## 3. 官方示例分析

### 3.1 `inbox-triage`（邮件分拣）

```yaml
name: inbox-triage
steps:
  - id: fetch
    command: gog.gmail.search --query 'newer_than:1d' --max 20

  - id: classify
    command: openclaw.invoke --tool llm-task --action json ...
    stdin: $fetch.stdout

  - id: post_business
    command: slack-route --bucket business
    stdin: $classify.stdout
    condition: $classify.json.items[0].route == "business"

  - id: wait_for_business_reply
    command: echo '{"status":"waiting","reason":"slack_reply"}'
    condition: $classify.json.items[0].route == "business"

  - id: notify_personal
    command: message --provider telegram ...
    condition: $classify.json.items[0].route == "personal"

  - id: stash_for_eod
    command: summary-append --bucket eod
    stdin: $classify.stdout
    condition: $classify.json.items[0].route == "later"
```

**流程解读：**

1. `fetch` 获取新邮件列表
2. `classify` 通过 LLM 将每封邮件分类为 `business` / `personal` / `later`
3. 三条分支并行（由 condition 控制）：
   - `business` → 发 Slack + 进入 `waiting` 态等待回复
   - `personal` → 直接通过 Telegram 通知用户
   - `later` → 加入待汇总列表
4. 当条件为 `business` 时，`wait_for_business_reply` 会将整个 flow 推进到 `waiting` 态（调用 `setWaiting`），等待外部 Slack 回复后 resume

**设计亮点：** 一个 flow 覆盖"主动通知 + 等待回复 + 事后汇总"三种路由，不需要写多套脚本，condition 天然处理了互斥分支。

---

### 3.2 `pr-intake`（PR 自动审查）

```yaml
name: pr-intake
steps:
  - id: fetch
    command: gh pr list --repo owner/repo --state open ...

  - id: classify
    command: openclaw.invoke --tool llm-task --action json ...
    stdin: $fetch.stdout

  - id: close_low_signal
    command: pr-close-low-signal
    stdin: $classify.stdout
    condition: $classify.json.items[0].nextAction == "close"

  - id: request_changes
    command: pr-request-changes
    stdin: $classify.stdout
    condition: $classify.json.items[0].nextAction == "request_changes"

  - id: refactor_branch
    command: pr-refactor-branch
    stdin: $classify.stdout
    condition: $classify.json.items[0].nextAction == "refactor"

  - id: escalate
    command: echo '{"status":"notify","target":"maintainer"}'
    condition: $classify.json.items[0].nextAction == "maintainer_review"
```

**流程解读：**

1. `fetch` 通过 `gh` CLI 获取仓库所有 open PR
2. `classify` 用 LLM 推理每个 PR 的处理意图：`close` / `request_changes` / `refactor` / `maintainer_review`
3. 四条分支并行（condition 控制），每个分支执行对应操作：
   - 低价值 PR → 直接 close
   - 需要改动的 → request_changes
   - 需要重构的 → refactor_branch
   - 高价值/复杂 PR → 通知 maintainer 人工处理

**设计亮点：** 典型的"AI 初筛 + 自动化执行 + 人工兜底"模式，所有 PR 处理逻辑集中在一个 YAML 文件中，替换命令插件即可适配不同仓库。

---

## 4. TaskFlow API 生命周期

TaskFlow 提供以下核心 API（`api.runtime.tasks.flow`）：

| API | 作用 | 典型场景 |
|---|---|---|
| `createManaged` | 创建一个新的 managed flow，指定 `controllerId`、`goal`、`currentStep`、`stateJson` | 初始化整个工作流 |
| `runTask` | 在 flow 下启动一个子任务（subagent/ACP），链接到 flow | 派发 classify 任务 |
| `setWaiting` | 将 flow 推进到 `waiting` 态，附带 `waitJson` 描述等待原因 | 等待 Slack 回复、等待人工审批 |
| `resume` | 从 `waiting` 态恢复 flow，更新 `currentStep` 和 `stateJson` | 外部事件触发 resume |
| `finish` | 正常结束 flow，持久化最终 `stateJson` | 流程完成 |
| `fail` | 异常结束 flow | 出错时标记 |
| `requestCancel` / `cancel` | 请求取消整个 job | 需要中断时调用 |

**完整生命周期时序：**

```
createManaged() → runTask() → [可能多次 setWaiting() ↔ resume()]
                              → finish()
```
或中途 `fail()` / `cancel()`。

**revision 机制：** 每次 mutation（setWaiting / resume / finish）都需要携带 `expectedRevision`，乐观锁防止并发冲突。Lobster 执行器负责维护这个 revision。

---

## 5. 技术架构：Lobster → TaskFlow 分层设计

```
┌─────────────────────────────────────────────┐
│  Lobster（YAML 编排层 / DSL）                │
│  - 解析 .lobster YAML                        │
│  - 计算 step 依赖拓扑（DAG）                  │
│  - 求值 condition 表达式                     │
│  - 管理 stdin/stdout 管道连接                │
│  - 调用 TaskFlow API 执行实际命令             │
└────────────────────┬────────────────────────┘
                     │ TaskFlow API calls
                     ▼
┌─────────────────────────────────────────────┐
│  TaskFlow（持久化运行时层）                   │
│  - createManaged / runTask / setWaiting /    │
│    resume / finish / fail / cancel           │
│  - stateJson 持久化（跨步骤状态）              │
│  - waitJson 持久化（等待态元数据）             │
│  - revision 冲突检测                         │
│  - 子任务（subagent）链接与生命周期管理         │
└─────────────────────────────────────────────┘
```

**关键设计原则（来自 TaskFlow SKILL.md）：**

1. **TaskFlow 管状态，Lobster 管流程**：condition 逻辑在 Lobster YAML 中，业务决策在 Lobster 层；TaskFlow 只负责推进状态，不管分支逻辑。
2. **最小化 stateJson**：只存恢复所需的最小状态，不存中间计算结果。
3. **revision-checked mutations**：所有写操作都带版本号，TaskFlow 内部做乐观锁。
4. **等待语义清晰**：`waitJson` 必须包含人/系统可读的理由（如 `{kind:"reply", channel:"slack", threadKey:"..."}`），方便调试和人工介入。

---

## 6. 适用场景评估

### 6.1 选 Lobster（YAML 工作流）的场景

| 场景 | 原因 |
|---|---|
| **多步骤管道任务**（fetch → classify → route → notify） | YAML 天然描述 DAG，stdin/stdout 管道简洁 |
| **需要持久化 + 断点恢复**（等待外部回复） | TaskFlow 持久化 waiting 态，重启不丢 |
| **条件分支多且复杂**（3+ 分支，每个分支执行不同工具） | condition + 多分支 YAML 比手写 if-else 更可维护 |
| **需要审计/版本化流程** | YAML 文件可 git 管理，diff 友好 |
| **非工程师可读可改** | 业务人员可读 YAML，不需要写代码 |

### 6.2 选直接用 subagent 的场景

| 场景 | 原因 |
|---|---|
| **单步强推理任务**（一个复杂任务，一个模型调用搞定） | subagent 直接派生子任务，更简单 |
| **无状态一次性任务**（查天气、搜网页、发消息） | 不需要持久化，不需要断点恢复 |
| **流程逻辑极简单**（两步以内） | 引入 TaskFlow 增加不必要的复杂度 |
| **需要大量自定义代码**（复杂业务规则） | YAML DSL 表达能力有限 |

### 6.3 选写脚本（Shell/Python）的场景

| 场景 | 原因 |
|---|---|
| **纯命令执行**（文件处理、数据转换、调用已有 CLI） | 直接 exec，不走 agent 层 |
| **性能敏感**（高频、小颗粒度任务） | agent/session 启动有冷启动开销 |
| **已有成熟脚本体系**（不需要 AI 判断） | 直接复用，不需要套一层 agent |
| **复杂流程控制**（循环、异常处理、事务） | YAML DSL 循环支持弱，需要脚本能力 |

---

## 7. 建议：什么场景适合引入 Lobster

### 推荐引入 Lobster

1. **需要"AI 初筛 + 自动化执行 + 人工兜底"的工作流**  
   例如：PR review pipeline、issue routing、订单审核、内容 moderation。LLM 负责分类/判断，后续步骤自动执行或等待人工审批。

2. **需要断点恢复的多步骤任务**  
   例如：跨天的邮件处理流程、周报生成、数据同步任务。TaskFlow 持久化 waiting 态，agent 重启后自动 resume。

3. **业务逻辑需要版本化和团队协作**  
   YAML 工作流文件可提交 git review，团队成员可以 review/PR 流程变更，适合有合规或审计要求的场景。

4. **需要多渠道路由的收件箱任务**  
   典型的 inbox-triage 模式：一份输入 → LLM 分类 → 分发到 Slack/Telegram/Email/待汇总。Lobster condition 完美建模这类互斥路由。

5. **长时间运行的 Cron 任务**  
   Cron 触发 Lobster 工作流，工作流内部自行管理步骤状态，不依赖单次 agent 会话的生命周期。

### 暂不引入（优先其他方案）

- **简单的一次性任务**：查信息、发消息、文件处理 → 直接 exec 或 subagent
- **已有成熟 CI/CD 流水线**：GitHub Actions / GitLab CI 已能覆盖大部分 CI/CD 场景，Lobster 适合偏 AI 决策的流程
- **强计算/循环逻辑**：需要大量循环、条件分支嵌套 → 考虑 Python 脚本 + Lobster 只负责 AI 决策步骤

### 引入路径建议

1. **从小场景开始**：选一个"分类 + 路由"类任务（如 issue 分发、邮件分类）作为 pilot，验证 Lobster + TaskFlow 端到端链路
2. **提取可复用工具**：将 `gh pr list`、`pr-close-low-signal` 等命令封装为 OpenClaw tool，降低 YAML 中 command 的耦合度
3. **监控 waiting 态 flow**：部署初期关注 `setWaiting` → `resume` 链路是否顺畅，人工介入点是否合理
4. **YAML 模块化**：复杂 flow 拆分为 sub-lobster（如 `common/classify.lobster`、`common/notify.lobster`），主 flow import 组合

---

## 参考资源

- TaskFlow SKILL.md：`skills/taskflow/SKILL.md`
- TaskFlow inbox-triage SKILL.md：`skills/taskflow-inbox-triage/SKILL.md`
- 官方示例：
  - `skills/taskflow/examples/inbox-triage.lobster`
  - `skills/taskflow/examples/pr-intake.lobster`
- CHANGELOG 相关变更：#58336（TaskFlow 初始引入）、#61523（in-process Lobster）、#64755（lobster/core runtime）、#69559（managed approval resumes）
