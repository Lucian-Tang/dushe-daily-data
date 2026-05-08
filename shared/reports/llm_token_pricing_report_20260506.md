# 大模型 Token Plan 性价比调研报告

**调研日期：** 2026-05-06  
**参与方：** 产品 + 研发（汇总：Lucia）

---

## 一、主流厂商定价一览（$/M tokens）

### 1. OpenAI（官方 API）

| 模型 | Input | Input(Cached) | Output | 备注 |
|------|-------|---------------|--------|------|
| GPT-5.5 | $5.00 | $0.50 | $30.00 | 旗舰推理模型 |
| GPT-5.4 | $2.50 | $0.25 | $15.00 | 专业级 |
| GPT-5.4 mini | $0.75 | $0.075 | $4.50 | 高性价比迷你 |
| Batch API | **-50%** on Input & Output | | | 异步24h交付 |

**结论：** GPT-5.4 mini 是 OpenAI 家性价比最高的正经模型，输入仅 $0.75/M，配合缓存读 $0.075/M 相当便宜。

---

### 2. Anthropic（via AWS Bedrock）

| 模型 | Input | Output | 缓存读 | 备注 |
|------|-------|--------|--------|------|
| Claude 3.5 Sonnet | $6.00 | $30.00 | $0.60 | Bedrock 标准价 |
| Claude 3.5 Sonnet v2 | $6.00 | $30.00 | $0.60 | 同价，多了扩展访问 |
| Batch | $3.00 | $15.00 | - | 50%折扣 |

**结论：** Claude 3.5 Sonnet 输出 $30/M 偏贵，但缓存读 $0.60/M 是不错的优化点。Anthropic 官方控制台是订阅制（Pro $17/月），API 价格需走 AWS。

---

### 3. DeepSeek（via AWS Bedrock）

| 模型 | Input | Output | 地区 |
|------|-------|--------|------|
| DeepSeek v3.2 | $0.62 | $1.85 | 美东/美西/欧洲 |
| DeepSeek v3.2 | $0.74 | $2.22 | 亚太 Mumbai/东京等 |
| DeepSeek v3.1 | $0.5974 | $1.7304 | 亚太多区 |
| Flex（亚太悉尼）| $0.2987 | $0.8652 | 最低价 |

**结论：** DeepSeek 是这波调研里的价格屠夫，v3.2 输入不到 $1/M，输出 $1.85-2.22/M，美区比亚太更便宜。

---

### 4. MiniMax（via Together AI）

| 模型 | Input | Input(Cached) | Output |
|------|-------|---------------|--------|
| MiniMax M2.7 | $0.30 | $0.06 | $1.20 |
| MiniMax M2.5 | $0.30 | $0.06 | $1.20 |

**结论：** 输入 $0.30/M，缓存读 $0.06/M，输出 $1.20/M——**Together AI 上最低价的顶级模型之一**，性价比极突出。

---

### 5. 国产其他（via Together AI）

| 模型 | Input | Input(Cached) | Output |
|------|-------|---------------|--------|
| GLM-5.1 | $1.40 | - | $4.40 |
| GLM-5 | $1.00 | - | $3.20 |
| Kimi K2.6 | $1.20 | $0.20 | $4.50 |
| Qwen3.6-Plus | $0.50 | - | $3.00 |
| Qwen3.5-397B | $0.60 | - | $3.60 |
| Qwen3-Coder-Next | $0.50 | - | $1.20 |

---

### 6. Google（Gemma 3 on AWS Bedrock）

| 模型 | Input | Output |
|------|-------|--------|
| Gemma 3 4B | $0.04 | $0.08 |
| Gemma 3 12B | $0.09 | $0.29 |
| Gemma 3 27B | $0.23 | $0.38 |

**结论：** 小模型极端便宜，4B 型号几乎不要钱，适合轻量任务。

---

### 7. 特殊：xAI Grok 4.3（via OpenRouter）

| 方向 | 价格 |
|------|------|
| Input | $1.25/M |
| Output | $2.50/M |
| 缓存读 | $0.20/M |

---

## 二、性价比综合排名（按 Input + Output 混合成本）

> 假设 Input:Output = 3:1（大多数业务场景比例）

| 排名 | 模型 | 混合成本/1M | 来源 |
|------|------|-------------|------|
| 🥇 | MiniMax M2.7 | **$0.525** | Together AI |
| 🥈 | DeepSeek v3.2 | **$1.01** | AWS Bedrock |
| 🥉 | Qwen3.6-Plus | $1.125 | Together AI |
| 4 | Kimi K2.6 | $1.65 | Together AI |
| 5 | GLM-5 | $1.90 | Together AI |
| 6 | GPT-5.4 mini | $1.89 | OpenAI 官方 |
| 7 | Claude 3.5 Sonnet | $12.00 | AWS Bedrock |

---

## 三、采购建议

### 💰 省钱优先（研发评估）
- **主力模型**：MiniMax M2.7 ($0.30/$1.20) — 性价比之王，TPM 充足时首选
- **国产备选**：DeepSeek V3.2 — 价格接近阿里百度官方，不绑平台
- **轻量场景**：Gemma 3 27B ($0.23/$0.38) 或 Qwen3-Coder-Next

### 🔬 性能优先（产品评估）
- **复杂推理/代码**：Claude 3.5 Sonnet v2 或 GPT-5.4，虽然贵但能力强
- **Agent 工作流**：GPT-5.4 mini 性价比均衡，带缓存折扣后很香

### 📦 批量任务
- OpenAI Batch API（-50%）、Together AI Batch、AWS Bedrock Batch 均可考虑
- DeepSeek Flex 亚太区 $0.30/$0.87 是批量任务地板价

### ☁️ 平台建议
| 场景 | 推荐平台 |
|------|---------|
| 追求性价比+稳定 | **Together AI**（MiniMax/Qwen/GLM） |
| 需要 Claude/GPT | **AWS Bedrock**（统一账单+合规） |
| 深度推理需求 | **OpenAI 官方**（Batch+Priority） |
| 国产合规需求 | **火山引擎/百度智能云**（需单独询价） |

---

## 四、待确认项（产品和研发跟进）

1. **实际业务 Input:Output 比例**——影响混合成本计算准确性
2. **TPM 需求上限**——决定走 Serverless 还是 Dedicated
3. **是否需要多模型冗余**——主备策略影响采购量
4. **数据合规要求**——是否必须国内云（阿里/火山/百度）
5. **批量任务的 SLA 要求**——Batch 24h 交付是否接受

---

**Lucia 建议：** 第一期先用 **Together AI 的 MiniMax M2.7** 跑主力流量，研发侧对接成本监控；产品侧按场景分流——简单任务走 Qwen3-Coder-Next，复杂推理走 GPT-5.4 mini/Claude。这样大概能比纯用 OpenAI 节省 60-70% 成本。

待确认：火山引擎和百度智能云的详细报价（国产合规场景）