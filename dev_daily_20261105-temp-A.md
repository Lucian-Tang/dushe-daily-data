# 开发者日报 · A 轨素材 · 2026-11-05

共 15 条

## 1. GPUWorks：40MB 的控制面，不装 K8s 也能管混合 GPU 集群

- **来源**：HN Show HN
- **链接**：https://github.com/flitai-io/gpuworks
- **UID**：dev_ee00cbd9

GPUWorks 把整个 GPU 管理与 MaaS 控制面压到约 40MB，不依赖 Kubernetes。自有服务器、云主机和 Mac 用一条命令接入同一集群，NVIDIA、AMD、昇腾、平头哥 PPU、海光与 Apple Silicon 可以混跑。内置 392 个模型、1235 套启动规格，选模型后自动估算显存、挑卡并拉起 vLLM 或 SGLang，对外提供 OpenAI 兼容端点。

> 毒舌：不装 K8s，40MB 就想管全部 GPU。

## 2. Hyperbutler：Windows 上不要 WSL 的 Docker，空闲只吃 319MB

- **来源**：HN Show HN
- **链接**：https://hyperbutler.dev/
- **UID**：dev_224108cc

Hyperbutler 在 Windows 上用 Host Compute Service 启极简 Linux 虚拟机，把 dockerd 跑在里面，原版 docker CLI 直接可用，不需要 WSL。对比 Docker Desktop：空闲内存 319MiB 对 1.7–2.7GB，启动到跑容器 2.5 秒对 5.6 秒，删完 5GB 镜像后磁盘占用 1.5GiB 对 6.8GiB。当前 v0.1.0，Apache-2.0，仅支持 Win11 x64。

> 毒舌：为了不用 WSL，先造一个更小的 WSL。

## 3. Evergreen：把不变量写进代码，让编译器替你做证明

- **来源**：HN Front Page
- **链接**：https://evergreenlang.net
- **UID**：dev_b81513ef

Evergreen 是一个主打「可证明安全」的系统语言：把前置条件、后置条件和数据不变量写在代码旁，由编译器生成并检查证明义务；内存层用显式布局、所有权与借用追踪；归纳证明、lemma 与 ideal 计算在检查后被擦除，不进入运行时。官网提供 WASM 编译器与在线 playground，示例包括非零类型、溢出检查和 UTF-8 字符串，口号是「比 C 更强，比 Rust 更安全」。

> 毒舌：又一个「比 Rust 更安全」的语言，先跑个 demo。

## 4. mcp-meta：104 个 MCP 工具折叠成 2 个，Schema 瘦身 99.4%

- **来源**：V2EX Share
- **链接**：https://www.v2ex.com/t/1254539
- **UID**：dev_98ecd775

mcp-meta 夹在 MCP 客户端和多个上游 Server 之间，对模型只暴露两个懒加载元工具：mcp_tools 查 Server 概览或按需拉取紧凑签名，mcp_call 指定 Server 和工具发起调用。作者实测挂 14 个 Server、104 个工具时，每轮光 Schema 就烧掉 14.2 万字符；接入后降到 892 字符，减少 99.4%，调用能力不丢。纯 Python 标准库、零依赖，MIT 开源。

> 毒舌：工具还没调用，Schema 先把上下文吃完了。

## 5. 强化学习驱动的逆向 Agent，想解决无人值守和高难样本

- **来源**：V2EX Share
- **链接**：https://www.v2ex.com/t/1254571
- **UID**：dev_bcce8e55

作者做了个强化学习驱动的逆向工程 Agent，目标是把复杂逆向任务从「人盯着跑」变成无人值守：支持 Web、PE、ELF、APK 和固件等方向，分析过程中会持续学习，并把用过的方法与结果沉淀下来，后续任务可以复用经验，减少中途跑偏或过早宣布完成。项目仍在迭代，作者公开了 GitHub 仓库，欢迎用真实样本交流。

> 毒舌：逆向最怕的不是难，是 AI 说它搞定了。

## 6. 给 PA 补两个小工具：安全传 token，以及 MCP Webhook 通知

- **来源**：V2EX Share
- **链接**：https://www.v2ex.com/t/1254570
- **UID**：dev_c7e3e83e

V2EX 作者给「原始 PA」补了两个小工具：secure-input 让 AI 在需要时安全地向用户索要 token，或把 token 发给用户，避免明文暴露在对话里；mcp-webhook-events 用 MCP Events 给 PA 增加 Webhook 通知，适合 Dot 这类工具。两个项目都是自用 vibe 产物，作者直言自己也不会用，建议直接让 AI 教配置。

> 毒舌：让 AI 管 token，先教会它别把 token 说出去。

## 7. Promise.all 不限制并发，你得自己造一个有界池

- **来源**：Dev.to
- **链接**：https://dev.to/jitsumi/promiseall-doesnt-limit-concurrency-heres-a-small-pool-that-does-33cn
- **UID**：dev_fa092203

Promise.all 不限制并发：ids.map(id => fetchRecord(id)) 在 Promise.all 等待前就把请求全发出去了，把 promise 包成函数再排队也来不及。正确做法是把输入保留为数据，把「启动任务」的回调交给有界池，只有槽位空出来才调用；池按输入顺序返回 fulfilled 或 rejected 结果，单条失败不影响其余任务。它只适用于独立 I/O，不提供 CPU 并行。

> 毒舌：Promise.all 只负责等，不负责刹车。

## 8. CLAUDE.md 该写多长：200 行、500 行还是 32KiB

- **来源**：Dev.to
- **链接**：https://dev.to/clogmeter/how-long-should-claudemd-agentsmd-be-51m8
- **UID**：dev_5d29e5c9

Claude Code 建议 CLAUDE.md 控制在 200 行内，Cursor 每文件不超过 500 行，Codex 的 AGENTS.md 默认上限 32KiB，超出会被截断。真正的限制不是行数，而是注意力预算：常驻指令每轮花 token，还和系统提示、工具描述抢注意力；重复冲突的规则会让模型随便选，长会话还会压缩早期规则。建议先量 token，把流程移到按需 skill，用 hook 或 CI 兜底「绝不」类规则。

> 毒舌：写满 500 行规则，模型只记住了前 50 行。

## 9. Apex npm 投毒排查：从锁文件一路查到 MCP 和 DNS

- **来源**：Dev.to
- **链接**：https://dev.to/facilishz/a-practical-hunt-workflow-for-malicious-npm-packages-and-their-infrastructure-3e31
- **UID**：dev_f213f38c

Apex npm 投毒排查链：恶意包 @apexacc/cli 通过启动器下发平台专属可执行文件，Windows 分支用 PowerShell、VBScript、UAC 与多种 loader 落地原生 stealer，macOS 分支用密码弹窗、CloudSyncD 和 C2 端点，还牵出模型 API 与远程 MCP。取证分四段：包与锁文件、进程执行、DNS/代理/身份、ZoomEye 外部测绘，强调先保全再清理。

> 毒舌：只查 npm 日志，等于只看犯罪现场的门铃。

## 10. RSI 不只发生在模型：五种状态才决定改进能否继承

- **来源**：博客园 Cnblogs
- **链接**：https://www.cnblogs.com/fanzhidongyzby/p/23552080/rsi
- **UID**：dev_b64528c2

递归自我改进从「模型变强」拆成五类可继承状态：数据、Harness、模型参数、Swarm 组织与 Meta 策略，改进要经过候选、验收、继承才算数。Anthropic 称 2026 年 5 月超 80% 生产代码可归因 Claude，但代码量不等于效率；AlphaEvolve 把某内核加速 23%，整体训练只降约 1%；GLM-5.3 的 Infra Agent 把端到端吞吐做到基线三倍。局部收益不能直接乘成 RSI 加速。

> 毒舌：内核快 23%，训练只快 1%，这才叫分母。

## 11. uni-app 跑鸿蒙蓝牙全瞎：不报错、不回调，只能自己补

- **来源**：博客园 Cnblogs
- **链接**：https://www.cnblogs.com/xyyt/p/23551290
- **UID**：dev_ada2ce08

uni-app 蓝牙 API 在 HarmonyOS Next 上被标为不支持，不报错、不回调，await 永远挂着。三层补齐：UTS 插件封装 @kit.ConnectivityKit，前端做同名同签名垫片，再注入纯 JS 厂商 SDK，协议代码一行没改。坑在于插件产物有 4 份副本不同步、原生监听注册与解注不成对导致随机「连接成功却报失败」、持久化 deviceId 随设备重启失效。附 ArkTS 错误对照表和真机自查清单。

> 毒舌：不报错也不回调，鸿蒙的蓝牙学会了装死。

## 12. 1010 行库存导出超时：一个缺失索引扫了 60 万行

- **来源**：博客园 Cnblogs
- **链接**：https://www.cnblogs.com/SheepDog/p/23550837
- **UID**：dev_ee29a3c3

某冷库导出库存只有 1010 条，却反复触发 JDBC 10 秒读超时。作者从异常栈定位到一条标量子查询：为每条库存按 batch_id 去 60.9 万行的二维码表取果框编号，而 batch_id 没有索引，最坏估算要检查约 6 亿行次。加 IS NOT NULL 没用，因为优化器仍要扫描；最终只加一个普通索引、不改 Java 代码，就把该子查询的预计扫描行数从约 60 万降到 1。文章强调返回行数少不等于查询便宜。

> 毒舌：返回 1010 行，数据库扫了 6 亿行。

## 13. Coding Agent 推理优化：单用户 Decode 2.8 倍是怎么来的

- **来源**：博客园 Cnblogs
- **链接**：https://www.cnblogs.com/Qiniu-developer/p/23548452
- **UID**：dev_a7b9d530

Modal 公开 Coding Agent 推理优化：在 Kimi K2.6、SGLang 和 B200 上，单用户 Decode 提升 2.8 倍，单实例吞吐提升 5.6 倍。他们放弃显存更大的 TP8 选 TP4，因为 TP8 每卡吞吐没翻倍；推测解码用真实 Coding Trace 微调 DFlash，平均接受长度从 5.00 提到 5.84，再快 20%；还把 KV Cache 从 BF16 换 FP8，并优化多 Session 路由，缓解长上下文 KV 不足。

> 毒舌：堆到 8 卡不难，难的是每张卡都不闲着。

## 14. GitHub spec-kit：把「先写规格」做成 coding agent 的流程

- **来源**：GitHub Trending Daily
- **链接**：https://github.com/github/spec-kit
- **UID**：dev_9f47cb6d

GitHub 开源的 Spec Kit 把「先写规格再让 coding agent 干活」做成流程：先建 constitution，再依次 specify、plan、tasks、implement、converge；用 extension、preset、workflow、bundle 和 catalog 组合命令、质量门禁与规范，支持 Copilot、Claude Code 等 agent，Python 3.11+ 安装。

> 毒舌：先写清要什么，再让 AI 动手，顺序别反。

## 15. PR-Agent：一次 LLM 调用审一个 PR，老牌开源评审器还在跑

- **来源**：GitHub Trending Daily
- **链接**：https://github.com/The-PR-Agent/pr-agent
- **UID**：dev_3b7ba8aa

PR-Agent 是老牌开源 AI 代码评审工具，社区维护，明确不是 Qodo 免费版。每个 /review、/improve、/ask 基本只发一次 LLM 调用，约 30 秒；用 PR Compression 处理大 PR，支持 GitHub、GitLab、BitBucket 等平台，也能 CLI、Action、Docker、webhook 部署，模型经 LiteLLM 接 OpenAI、Claude、Gemini。

> 毒舌：一次 LLM 调用就敢审 PR，省的是钱不是责任。
