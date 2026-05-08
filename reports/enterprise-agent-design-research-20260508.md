# 大厂 Agent 设计方案调研报告

> 调研人：Thomas（产品）
> 日期：2026-05-08
> 目标：理解行业最佳实践，为 Lucia+Thomas+Stephen+校验官 团队提供架构改进参考

---

## 执行摘要

六大方案可以分成三类：
- **模型厂商**（Anthropic、OpenAI）→ 提供 Tool/Agent 基础设施，向下抽象
- **框架厂商**（Microsoft、LangChain）→ 提供编排层，向上抽象
- **应用厂商**（Cognition、Google）→ 提供端到端解决方案

**对我们团队最重要的发现**：大厂普遍具备**持久化状态管理、显式工作流定义、多 agent 通信协议**三大能力，而我们目前主要依赖隐式协作和人工编排，这正是差距所在。

---

## 一、Anthropic — Claude Agent 设计模式

### 核心架构理念
**"工具即一等公民，客户端执行"** —— Claude 的 agentic 能力建立在 Tool Use 原语上，将工具调用作为模型 API 的核心部分而非外部扩展。

### Agent 间通信方式
Claude 本身是单 agent 模型，通信通过两种路径：
1. **MCP（Model Context Protocol）**：标准化协议，连接外部工具和数据源（类似 USB-C），支持双向工具调用和数据获取
2. **Client-side Agent Loop**：应用层在客户端实现 agentic loop（ReAct 模式），模型返回 `tool_use` 块，客户端执行并回传结果

### 工具调用规范
- **Server Tools**：Anthropic 托管（`web_search_20260209`、`web_fetch`、`code_execution`），API 直接返回结果
- **Client Tools**：用户定义的函数，schema 传入 `tools` 参数，Claude 返回结构化调用，客户端执行
- **`strict: true`** 选项保证工具调用严格匹配 schema，不允许参数偏差
- 工具描述和 schema 直接影响模型决策质量

### Safety Layers
- 内置 content policy，在 API 层过滤
- 工具执行完全在客户端控制，可在客户端添加权限校验和审计
- MCP 连接器需明确信任域

### 对我们团队的启示
- **MCP 协议值得重视**：如果 Stephen 能将 Lucia 的核心工具封装为 MCP Server，后续接入任何支持 MCP 的 agent 都更方便
- **我们还没有显式的 ReAct loop 实现**：目前 Lucia 直接调用工具，但行业标准是"模型决定是否调用 → 执行 → 结果回传 → 继续"，需要建立这一循环机制
- **工具描述的工程化**：大厂对每个工具都有精心设计的描述和 schema，我们目前工具描述比较随意

---

## 二、OpenAI — Agents SDK / Swarm

### 核心架构理念
**"轻量级多 agent 编排，以 handoff 为核心原语"** —— Swarm（现演化为 Agents SDK）追求的是**零状态、可测试、易组合**的多 agent 协作模型。

### Agent 间通信方式
- **Handoff（交接）**：一个 agent 通过返回另一个 agent 来转移执行权，这是唯一的跨 agent 通信机制
- **共享消息上下文**：所有 agent 共享同一个 messages 列表（chat history），但**系统提示只保留当前 agent 的**，交接时上下文继承
- **Context Variables**：跨 agent 共享的轻量状态字典
- **完全无状态**：Swarm 的 `client.run()` 本身不保存任何状态，每次调用都是完整的 agent loop

### 工具调用规范
- Agent 的 `functions` 列表本质上是普通 Python 函数
- **Handoff 也是一种函数返回**：当函数返回 `Agent` 对象时，执行权转移
- 函数可以声明 `context_variables` 参数，由框架自动注入

### Swarm → Agents SDK 的演进
- Swarm 是"educational framework"（教育实验）
- Agents SDK 是生产级版本，增加了可观测性、更严格的错误处理
- handoff 模型被 AutoGen 等框架完整继承

### 对我们团队的启示
- **Handoff 模式非常适合 Lucia→Stephen→校验官 的交接场景**：可以让 agent 显式地通过返回"下一个角色"来触发交接
- **Context Variables 可以解决我们跨 agent 状态共享的问题**：避免每个 agent 各自维护一份上下文
- **但 Swarm 的无状态模型对我们来说过于简单**：我们需要持久化记忆和跨会话状态

---

## 三、Microsoft AutoGen — 多 agent 对话框架

### 核心架构理念
**"事件驱动的多 agent 运行时，支持分布式扩展"** —— AutoGen 提供了从简单 group chat 到复杂 orchestrator 的完整多 agent 编排谱系，现已演化为 **Microsoft Agent Framework (MAF)**。

### Agent 间通信方式
AutoGen 支持多种通信拓扑，核心是**事件驱动的 pub-sub 模型**：

#### 团队模式对比

| 模式 | 通信方式 | 适用场景 | 复杂度 |
|------|---------|---------|-------|
| **RoundRobinGroupChat** | 轮询制广播 | 简单多 agent 顺序执行 | 低 |
| **SelectorGroupChat** | 中央选择器，决定下一 speaker | 需要动态路由的场景 | 中 |
| **Swarm** | agent 本地决策 handoff，共享消息上下文 | 大量独立能力需要路由 | 中 |
| **GraphFlow** | 有向图精确控制执行路径 | 严格流程控制（条件分支、并行、循环） | 高 |
| **Magentic-One** | Orchestrator 主导的任务分解 | 开放式 web/file 任务 | 高 |

#### Handoff 消息协议
```python
# Handoff 本质上是一个特殊工具
class HandoffMessage:
    source: str          # 来源 agent
    target: str          # 目标 agent
    content: str         # 交接内容
```
交接时，当前 agent 的 chat history 完整传递给下一个 agent。

### Magentic-One 架构（最接近生产级的参考）
```
Orchestrator（主控）
  ├── Task Ledger（任务分解记录）
  ├── Progress Ledger（进度跟踪）
  ├── WebSurfer（浏览器操作）
  ├── FileSurfer（文件操作）
  ├── Coder（代码编写）
  └── ComputerTerminal（代码执行）
```
- Orchestrator 有内外两个循环：外循环更新任务分解，内循环检查进度并决定下一步
- 具备**自我纠正能力**：如果多步无进展，重新规划
- Safety：强调 Docker 隔离、代码执行审批、人类监督

### 工具调用规范
- 基于 `FunctionTool` schema 定义
- 支持 `McpWorkbench` 连接 MCP 服务器
- **Delegate Tools**：专门用于跨 agent 任务委托的工具

### 对我们团队的启示
- **Magentic-One 的 Orchestrator 模式值得研究**：我们目前没有"主控"角色，所有 agent 对等，但复杂任务需要任务分解和进度跟踪
- **GraphFlow 的有向图模式可以低成本引入**：用 DiGraphBuilder 定义 agent 间的固定工作流，非常适合校验官这样的固定流程节点
- **我们当前更像 Swarm + 人工编排**，可以演进到 SelectorGroupChat 或 Magentic-One

---

## 四、Cognition AI — Devin

### 核心架构理念
**"单 agent 极致工具化 + 任务级微调 + 自我改进"** —— Devin 不追求多 agent 协作，而是在单一 agent 上叠加极其丰富的工具调用、长期记忆和任务分解能力。

### 核心架构
- **单一大语言模型作为核心**（经过代码能力的专门微调）
- **工具层极度丰富**：IDE、bash、浏览器、文件系统、API 调用等
- **Task Ledger**：记录任务分解
- **Progress Ledger**：记录当前进度，自我评估完成度
- **Self-improvement 机制**：Devin 会编写辅助脚本来自动化重复步骤

### 与多 agent 的本质区别
| 维度 | Devin | AutoGen/Swarm |
|------|-------|---------------|
| 架构 | 单 agent | 多 agent |
| 通信 | 内部工具调用 | 外部 handoff/消息 |
| 规划 | Task Ledger（集中） | 分布式规划 |
| 错误恢复 | 自我纠正 | 人类或 orchestrator 介入 |

### 对我们团队的启示
- **微调的价值**：Nubank 案例显示，针对特定任务微调后，Devin 的完成率翻倍，速度提升 4 倍。我们如果能对 Lucia 针对"产品需求分析"任务微调，可能效果显著
- **自我改进脚本**：Stephen 可以学习 Devin 的做法——为常见任务编写辅助脚本，减少每次的 token 消耗
- **双 Ledger 机制**：建立 Task/Progress Ledger 对任何复杂任务都有价值，我们目前靠人工跟踪

---

## 五、Google — Gemini Enterprise Agent Platform（原 Vertex AI Agent Builder）

### 核心架构理念
**"企业级全生命周期平台，覆盖 Build→Scale→Govern→Optimize 四大支柱"** —— Google 不只是做 agent 框架，而是提供了完整的企业 AI 治理和安全体系。

### 四大支柱架构

#### Build（构建）
- **Agent Development Kit (ADK)**：模块化、模型无关的 agent 构建框架
- **Agent Studio**：低代码可视化画布，设计 agent 推理循环
- **Agent Garden**：预构建 agent 模板库
- **RAG Engine**：私有数据连接，降低幻觉
- **Vector Search**：AI 原生向量搜索

#### Scale（扩展）
- **Agent Runtime**：高性能运行时，支持亚秒级冷启动和长时运行
- **Sessions**：单次交互内的状态管理
- **Memory Bank**：跨会话持久记忆
- **Code Execution**：沙箱代码执行环境

#### Govern（治理）
- **Agent Registry**：企业级 agent 目录和版本管理
- **Agent Identity**：每个 agent 独立身份，支持细粒度权限
- **Agent Gateway**：中央策略执行点，统一管理工具调用认证和安全策略
- **AI Threat Scanning**：针对 agentic 系统的实时威胁检测

#### Optimize（优化）
- **Agent Evaluation**：自动化评估（Multi-Turn AutoRaters）
- **Simulation**：合成测试场景生成
- **Observability**：统一追踪查看器（类似 LangSmith）
- **Prompt Optimization**：基于失败模式的提示词自动优化

### 对我们团队的启示
- **治理能力严重缺失**：我们目前没有任何 agent 级别的权限控制、审计日志或安全策略，Google 的 Agent Gateway 概念非常值得借鉴
- **Memory Bank**：我们只有每日 memory 文件，没有系统化的跨会话持久化机制
- **Agent Registry**：如果我们有多个 agent，需要一个中心目录来管理它们的能力、版本和权限
- **最小可行追赶**：先实现 Sessions（状态管理）和 Memory（持久化），治理能力逐步建立

---

## 六、LangGraph / LangChain — 工作流编排模式

### 核心架构理念
**"图模型作为 agent 编排的本质抽象"** —— LangGraph 受 Pregel（Google）和 Apache Beam 启发，将所有 agent 行为建模为图中的节点和边，提供最小化的运行时基础设施。

### 核心概念
- **State**：跨节点流动的共享状态（通常是一个 dict）
- **Node**：一个 agent 或一项操作（Python 函数）
- **Edge**：节点间的连接，决定下一个执行的节点
- **Conditional Edge**：基于当前状态决定下一个节点

### 与其他框架的本质区别
| 维度 | LangGraph | AutoGen |
|------|-----------|---------|
| 抽象层次 | 极低（基础设施层） | 高（对话和团队层） |
| 状态管理 | 内置、可持久化 | 依赖外部或应用层 |
| 控制流 | 完全显式（图定义） | 半显式（事件驱动） |
| 适用人群 | 底层框架开发者 | 应用开发者 |

### 关键能力

#### 1. 持久化执行（Durable Execution）
```python
# agent 可在任意节点中断，重启后从断点继续
# 这解决了长时任务的网络中断问题
checkpoint = graph.checkpoint()
# 保存 checkpoint，可在不同进程/机器恢复
```

#### 2. Human-in-the-Loop（中断机制）
```python
# 在关键节点暂停，等待人类输入
graph.update_state(state, {"action": "human_approval"})
# 支持审查、修改、批准或拒绝
```

#### 3. 内存管理
- **Short-term Memory**：当前任务的工作状态（图 State）
- **Long-term Memory**：跨会话持久化（可对接向量数据库）

#### 4. 子图（Subgraph）
- 支持构建层级 agent：主图中的某个节点本身又是一个完整的子图
- 这使得多 agent 协作可以作为"单一 agent"被更高层编排

### LangGraph 的设计哲学
> "Other agentic frameworks can work for simple, generic tasks but fall short for complex tasks bespoke to a company's needs. LangGraph provides a more expressive framework."

即：**其他框架做通用任务可以，做企业定制化复杂任务就暴露局限**。

### 对我们团队的启示
- **我们最缺的是状态管理**：LangGraph 的 State + Checkpoint 机制直接解决我们跨 session 记忆丢失的问题
- **子图模式可以解决 Stephen/Lucia 的协作**：Stephen agent 可以是主图中的一个"子 agent"，内部有自己的工作流程
- **中断机制是校验官的天然搭档**：在输出最终结果前插入 human approval 是 LangGraph 的原生能力
- **低成本引入路径**：先引入 LangGraph 的状态管理概念，即使不用完整框架，也能在现有架构中实现持久化

---

## 七、横向对比分析

### 架构模式全景图

```
┌─────────────────────────────────────────────────────────────────────┐
│  单 Agent 极致工具化                    多 Agent 协作编排           │
│  Cognition Devin                         LangGraph/AutoGen/Swarm    │
│                                                                     │
│  ┌──────────┐     ┌──────────┐     ┌──────────────┐                 │
│  │  Model   │     │  Model   │     │  Orchestrator │                 │
│  │   +      │     │   +      │     │  / Selector   │                 │
│  │ Tools    │     │ Tools    │     ├──────────────┤                 │
│  │   +      │     │   +      │     │  多 Agent    │                 │
│  │ Ledger   │     │ Handoffs │     │  (对等或层级) │                 │
│  └──────────┘     └──────────┘     └──────────────┘                 │
│                                                                     │
│  模型厂商(Anthropic/OpenAI)  ──→  框架厂商(AutoGen/LangGraph)      │
│  提供 Tool/Agent 原语             提供编排层                        │
└─────────────────────────────────────────────────────────────────────┘

企业平台(Google)  ──→  全生命周期覆盖 + 治理 + 安全
```

### 各方案核心指标对比

| 维度 | Anthropic | OpenAI Swarm | AutoGen | Devin | Google Agent Platform | LangGraph |
|------|-----------|--------------|---------|-------|----------------------|-----------|
| **架构复杂度** | 低（单 agent） | 低 | 高 | 中 | 极高 | 中 |
| **多 Agent 协作** | 无（靠 MCP 扩展） | 有（handoff） | 完整谱系 | 无 | 有 | 有（图模型） |
| **状态管理** | 无（客户端负责） | 无 | 部分 | 有 | 完整（Memory Bank） | 完整（State+Checkpoint） |
| **Human-in-loop** | 靠客户端 | 靠 handoff to user | 多种机制 | 任务级审批 | 原生支持 | 原生 interrupt |
| **安全/治理** | API 层过滤 | 无 | 基础 | 人类监督 | 企业级（Gateway） | 无 |
| **可观测性** | 基础 | 无 | 日志 | 有限 | 完整（Trace Viewer） | LangSmith 集成 |
| **学习门槛** | 低 | 低 | 中 | 中 | 高 | 中 |
| **开源** | 否 | 是（Swarm） | 是 | 否 | 否 | 是 |

---

## 八、核心问题回答

### Q1：大厂的 Agent 架构跟我们当前的架构有什么本质区别？

**本质区别在于三个维度：**

#### 1. 状态管理
- **大厂**：持久化状态（LangGraph Checkpoint、Google Memory Bank、AutoGen 的 checkpoint）、跨会话记忆
- **我们**：主要靠每日 memory 文件，没有系统化状态管理。Lucia 每次 session 从零开始

#### 2. 显式 vs 隐式编排
- **大厂**：工作流显式定义（GraphFlow DiGraph、Swarm handoffs、Magentic-One orchestrator）
- **我们**：Stephen/Lucia/校验官 的协作靠隐式约定，没有在代码/配置层面定义工作流拓扑

#### 3. 工具/通信标准化
- **大厂**：MCP/Function Tool 有标准化 schema，工具描述经过工程化优化
- **我们**：工具定义比较随意，没有 schema 约束，没有工具发现机制

---

### Q2：我们缺失了什么关键能力？

按优先级排序：

#### 🔴 高优先级（立即可追赶）
1. **ReAct Loop 实现**：我们目前是"直接调用"，不是"模型决策后调用"。需要建立 observe→think→act 循环
2. **跨 Agent 状态共享**：Stephen 的输出如何传给 Lucia？目前靠文件或人工，没有显式上下文传递机制
3. **工具 schema 规范化**：给每个工具写清晰的描述和严格的参数 schema

#### 🟡 中优先级（下一个 milestone）
4. **Checkpoint/持久化**：任务中途断后能从断点恢复，而不是从头开始
5. **Human-in-the-loop 机制**：校验官的角色应该有"暂停等待确认"的能力
6. **可观测性**：每个 agent 的决策过程应该有日志/trace，方便调试

#### 🟢 低优先级（长期演进）
7. **Agent Registry**：管理多个 agent 的能力和版本
8. **安全/Gateway**：工具调用的权限控制和审计
9. **针对任务的微调**：参考 Nubank 案例，对 Lucia 做产品分析专项微调

---

### Q3：哪些设计模式可以低成本引入？

#### 低成本引入清单（预计 1-2 周可落地）

| 模式 | 来源 | 引入方式 | 价值 |
|------|------|---------|------|
| **Handoff 模式** | OpenAI Swarm/AutoGen | Stephen/Lucia 之间增加显式交接协议（例如返回一个 `next_agent` 标记） | 协作拓扑显式化，可追踪 |
| **ReAct Loop** | Anthropic | 在 Lucia 的核心逻辑层加入"是否需要工具→执行→判断完成"的循环 | 减少幻觉，提高可靠性 |
| **Context Variables** | OpenAI Swarm | 建立跨 agent 共享的 `context_dict`，Stephen 写入，Lucia 读取 | 解决状态传递问题 |
| **DiGraph 工作流** | AutoGen GraphFlow | 用 JSON/配置文件定义 Stephen→Lucia→校验官 的固定流程 | 流程可配置、可版本化 |
| **双 Ledger** | Devin | 建立 `task_log.md` 和 `progress_log.md`，记录任务分解和当前进度 | 复杂任务可追踪 |
| **MCP Server** | Anthropic MCP | 将 Lucia 的核心工具封装为 MCP Server | 工具可发现、可复用 |

#### 中等成本（需要 1 个月左右）

| 模式 | 来源 | 说明 |
|------|------|------|
| **Checkpoint 机制** | LangGraph | 任务状态可保存/恢复，需要改造现有执行框架 |
| **Human interrupt** | LangGraph | 校验官节点支持暂停等待人工确认 |
| **Memory Bank** | Google | 系统化跨会话持久记忆，不只是 daily notes |

---

## 九、对我们团队架构的具体建议

### 立即行动（本周）

1. **建立 Context Variables 机制**
   - 一个 JSON 文件（如 `context.json`）作为跨 agent 状态共享层
   - Stephen 写入分析结果 → Lucia 读取上下文 → 校验官检查

2. **规范化工具 Schema**
   - 给 Lucia 的每个工具写完整的 docstring + input schema
   - 重点：避免模糊描述，参数类型明确

3. **引入简单的 ReAct Loop**
   - 在 Lucia 核心层加一个 "do I need to use a tool?" 的决策判断
   - 不需要完整框架，用 if-else 即可

### 短期（2-4 周）

4. **用 GraphFlow 思想定义工作流**
   - Stephen→Lucia→校验官 定义为一个固定的有向图
   - 配置文件描述节点关系，而不是写死在代码里

5. **建立 Checkpoint 概念**
   - 每个大任务开始时保存 context snapshot
   - 失败后可以从 snapshot 恢复

### 中期（1-2 个月）

6. **引入 MCP Server**
   - Stephen 的搜索能力封装为 MCP Server
   - Lucia 可以通过 MCP 调用 Stephen

7. **校验官增加 interrupt 能力**
   - 遇到不确定的地方主动暂停，等待人工确认
   - 类似 LangGraph 的 interrupt 机制

---

## 附录：参考资料

| 来源 | URL | 主要内容 |
|------|-----|---------|
| Anthropic Tool Use Docs | docs.anthropic.com/en/docs/build-with-claude/tool-use | 工具使用原语、Client/Server Tools |
| OpenAI Swarm | github.com/openai/swarm | Handoff 模式、轻量级编排 |
| AutoGen AgentChat | microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide | 多 agent team 模式 |
| Magentic-One | microsoft.github.io/autogen/.../magentic-one.html | Orchestrator 架构设计 |
| Google Agent Platform | docs.cloud.google.com/gemini-enterprise-agent-platform/overview | 企业级全生命周期平台 |
| LangGraph | github.com/langchain-ai/langgraph | 图模型编排、状态管理 |
| Cognition Devin | devin.ai | 单 agent 极致工具化案例 |

---

*本报告由 Thomas（产品）基于公开资料调研生成，仅供内部参考。*
