# 🛠️ 开发者日报 A 轨初选 | 2026-10-08

## 1. Chrome 开始原生支持 JPEG XL
**来源：** HN Front Page  
**链接：** https://developer.chrome.com/blog/jpeg-xl-in-chrome  
**uid：** dev_824eb396

Google 在 Chrome 官方博客宣布开始内置 JPEG XL 图片格式支持。JPEG XL 在同等画质下体积比 JPEG 小约三成，且兼顾无损与有损、支持从旧格式无损转码。经历了前两年「要删又没删」的反复，这次落地给纠结图片优化的前端和 CDN 团队一个明确信号。

> 🗯️ 喊了几年要砍，结果又默默加回来了。

## 2. 研究：AI 导购会给不同用户报不同价
**来源：** HN Front Page  
**链接：** https://www.bloomberg.com/news/newsletters/2026-10-07/study-claude-chatgpt-ai-bots-offer-different-shopping-prices-based-on-wealth  
**uid：** dev_647109f2

彭博报道一项研究：Claude、ChatGPT 这类 AI 助手在充当购物代理时，会根据用户画像（如财富水平）给出不同报价。这戳中了「AI 代理帮用户砍价」叙事里最尴尬的一面——代理到底代表谁的利益？做电商与 AI 导购的团队，得重新想想推荐与定价的透明度。

> 🗯️ 以为请了个帮你省钱的管家，结果它替商家杀熟。

## 3. 《战神》PSP 版被静态重编译跑进浏览器
**来源：** HN Front Page  
**链接：** https://github.com/snuri00/psp-web-recomp  
**uid：** dev_5492ba1e

开发者把 PSP 版《战神》静态重编译成 WebAssembly，靠自研的 HLE 内核与 WebGL2 渲染器，在浏览器里无需模拟器直接运行。相比逐指令模拟，静态重编译性能好得多，也让「老游戏进浏览器」多了一条可行路线，复古游戏与 WASM 爱好者都在围观。

> 🗯️ 模拟器还没退役，重编译已经先一步上桌了。

## 4. Mecum：让 Agent 直接操作 Mac 上的任何软件
**来源：** HN Show HN  
**链接：** https://github.com/ForteAI-Org/mecum  
**uid：** dev_b8cccd8a

开源的 macOS 应用 Mecum，让 AI Agent 能操作 Mac 上任意桌面软件，同时你还能继续正常使用电脑。它主打「不抢你的鼠标键盘」，把 Agent 的自动化限制在可控范围内。对想给本地桌面流程加自动化的开发者，是个比纯脚本更省心的实验品。

> 🗯️ 让 AI 帮你点鼠标，还得防着它顺手清空回收站。

## 5. Epic 开源的图形化调试器 RadDebugger
**来源：** GitHub Trending Daily  
**链接：** https://github.com/EpicGames/raddebugger  
**uid：** dev_b3ae9159

Epic Games 开源的 RadDebugger 是一款原生、多进程的图形化调试器，用 C 写成，主打调试 C/C++ 项目的流畅体验与可视化。作为游戏大厂放出的调试工具，它补上了开源世界在「好用 GUI 调试器」上的短板，Windows 开发者值得一试。

> 🗯️ Epic 打游戏的名声在外，做工具也是真下本。

## 6. cua：给「电脑操作 Agent」做基础设施
**来源：** GitHub Trending Daily  
**链接：** https://github.com/trycua/cua  
**uid：** dev_2f06de8a

来自 trycua 的开源项目 cua，定位计算机使用（Computer-Use）Agent 的底层设施：提供跨操作系统的驱动、多机集群与评测基准，用于训练、评估和生成数据。随着 AI 操作电脑成为热点，谁掌握这类基础设施，谁就卡住了 Agent 落地的关键一环。

> 🗯️ 卷模型卷不动了，开始卷 Agent 的手和脚。

## 7. claude-mem：给 Agent 装上跨会话记忆
**来源：** GitHub Trending Daily  
**链接：** https://github.com/thedotmack/claude-mem  
**uid：** dev_55490f36

开源项目 claude-mem 给编码 Agent 加上跨会话的持久记忆：记录 Agent 在会话中的行为，用 AI 压缩后注入后续会话，兼容 Claude Code、Codex、Gemini 等多个工具。对天天重启会话、上下文反复丢失的开发者，这是把「记忆」外包出去的一种解法。

> 🗯️ Agent 终于不用每次都假装第一次见你。

## 8. 用户发现 DeepSeek 网页端能刷到别人的对话
**来源：** V2EX Tech  
**链接：** https://www.v2ex.com/t/1213000#reply1  
**uid：** dev_ffb35265

有 V2EX 用户发帖称，在 DeepSeek 网页和 App 输入特定 think 标记，竟能看到其他用户的历史对话内容，且发帖时称尚未修复。这属于典型的越权访问与数据隔离缺陷，无论最终原因如何，都再次提醒大模型产品在会话隔离上不能掉以轻心。

> 🗯️ 能让 AI 看别人聊天记录，也能让别人看你问它啥。

## 9. 讨论：大模型的最终归宿是机器人，不是写代码
**来源：** V2EX Tech  
**链接：** https://www.v2ex.com/t/1233752#reply0  
**uid：** dev_cceeffe8

V2EX 上一个帖子引发讨论：作者认为 AI Coding 市场已供大于求，软件需求接近饱和，大模型的真正归宿是机器人——CV 提供视觉、LLM 提供语言、算力集群提供算力，通用机器人的软件架构基本齐活。观点未必对，但对判断下一个风口有参考价值。

> 🗯️ 代码写到饱和，下一步该给机器人做大脑了。

## 10. catbus：一套命令操作 10 个内容平台
**来源：** V2EX Share  
**链接：** https://www.v2ex.com/t/1246731#reply10  
**uid：** dev_c2d00999

开发者开源的命令行工具 catbus，把小红书、抖音、TikTok、B 站、快手、微博、闲鱼、淘宝、京东、X 这 10 个平台的网页端能力整合进同一套命令，安装后即可用统一语法搜索、抓取内容。对做多平台数据采集与自动化的人，省去了逐个平台写爬虫的麻烦。

> 🗯️ 一个 CLI 打十个平台，爬虫工程师的饭碗又薄了。

## 11. 花 600 美元、20 多轮，他训了两个本地 Computer-Use 小模型
**来源：** V2EX Share  
**链接：** https://www.v2ex.com/t/1246631#reply7  
**uid：** dev_97245745

开发者用三周业余时间做了 DeskMind：一个在 Mac 上替你操作电脑的 Agent，决策核心是两个本地小模型（Qwen3.5 0.8B 与 4B 微调，跑在 MLX 上），不走云端也不按次付费。思路是把每步操作变成选择题打分，而不是生成文本，比云端方案更私密也更便宜。

> 🗯️ 别人烧 API，他烧显卡，还顺手把成本打了下来。

## 12. SPDX 还是 CycloneDX：先选个能落地的 SBOM 格式
**来源：** Dev.to  
**链接：** https://dev.to/bianliang/spdx-or-cyclonedx-choosing-an-sbom-format-you-can-actually-operate-3ko9  
**uid：** dev_e58618f2

Dev.to 文章对比 SPDX 与 CycloneDX 两种主流 SBOM（软件物料清单）格式，重点不在谁更「标准」，而在于选一个团队真正能运营起来的。随着供应链安全合规要求变严，SBOM 从可选变成必备，格式选错的代价会在后续工具链集成时集中爆发。

> 🗯️ 格式之争吵得凶，能跑起来的才叫标准。

## 13. 在 EKS 上搭一套有韧性的 Kubernetes 应用
**来源：** Dev.to  
**链接：** https://dev.to/jamiu_cloud/resilient-kubernetes-application-1875  
**uid：** dev_fb72e84c

一篇偏工程实践的文章，演示如何在 Amazon EKS 上部署一套生产级的高可用架构：用 Helm 管理、StatefulSet 加 EBS 持久化存储、HPA 自动扩缩容、ALB Ingress，再配上 Redis 与 PostgreSQL。适合想系统练一遍 K8s 韧性设计、又缺完整案例的后端工程师。

> 🗯️ 教程里秒级扩容，生产里先问你有没有预算。

## 14. 从「调模型」到「搭系统」：Harness Engineering 是什么
**来源：** 博客园 Cnblogs  
**链接：** https://www.cnblogs.com/codigger/p/23213917  
**uid：** dev_c6d6b095

博客园文章解读 2026 年 AI 圈的新热词 Harness Engineering（驾驭工程），讨论它到底是新瓶旧酒还是真需求。核心观点是：AI 工程的重心正从「调模型」转向「搭系统」——围绕模型构建工具、记忆、评测与反馈的整套脚手架，才是决定落地效果的关键。

> 🗯️ 热词年年有，这回听着还真像那么回事。

## 15. 让 Agent 平时睡大觉，数据一变就醒来干活
**来源：** 博客园 Cnblogs  
**链接：** https://www.cnblogs.com/shanyou/p/23212659  
**uid：** dev_a10685c3

张善友在博客园分享 Ambient Agent（环境智能体）的落地经验：难点不在「让 Agent 做什么」，而在何时叫醒它、如何保证恰好执行一次、进程崩溃与网络抖动后如何体面收场。文章把事件驱动、幂等与容错这些老工程问题，重新放进了 Agent 的语境里。

> 🗯️ Agent 的最大难题不是聪明，是别装睡也别诈尸。
