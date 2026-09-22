# 🛠️ 开发者日报 A 轨初选 | 2026-09-23

## 1. gzip 也能当语言模型？系统自带的压缩工具续写出了莎翁
**来源：** HN Front Page  
**链接：** https://nathan.rs/posts/gzip-lm/  
**uid：** dev_e771bfaf

作者受「压缩即预测」这篇论文启发，做了个极端实验：不给神经网络、不给任何训练参数，只用操作系统自带的 gzip 当语言模型。把语料喂进去当先验，再丢一段提示，它就沿着「最容易被压缩」的字节序列往下续写。用 Tiny Shakespeare 实测，输出虽不成句，却明显带上了文风，证明确实藏着个概率模型。文章由此串起 DEFLATE 滑动窗口与信息论里「比特数 = −log₂p」的关系。

> 🗯️ 系统自带的压缩工具，居然也能续写莎翁。

## 2. 八十年破不了的 Enigma 密电，被 GPT-6 破了
**来源：** HN Front Page  
**链接：** https://www.cryptocellar.org/bgac/the-mvueh-break.html  
**uid：** dev_a1d48325

一封 1941 年纳粹德军发出的 Enigma 密电 MVUEH，自 2005 年起无人破译，如今被 AI 攻下。研究者 Carter Leffer 用 OpenAI GPT-6 Astra 找出密钥并送交验证：转子顺序是 253，与当天其他密电的 512 截然不同，密钥设置也自成一格。更耐人寻味的是，其明文与当年刚被破解的第 173 号密电几乎一模一样。这是大模型在历史密码战里一次可考的突破。

> 🗯️ 八十年悬案，让模型顺手给解了。

## 3. 让 Meta 的 Muse 导个文件夹，它把 6.8GB 家底全发了
**来源：** HN Front Page  
**链接：** https://mouse.dev/blog/muse-runtime-export/  
**uid：** dev_f0b5a7a3

一名研究者让 Meta 的 AI 助手 Muse 把「它能看到的文件」打包发到自己的 Google Drive，结果收到约 2.7GB（解压后 6.8GB）的压缩包，里面竟是它所在 Linux 运行环境的整个根文件系统：系统文件、内部文档、集成代码、记忆文件、Agent 日志，甚至还有 SSH 私钥。作者未确认密钥是否可用，已按漏洞赏金流程上报。警示是：一次普通对话就可能把内部敏感文件整包带出。

> 🗯️ 让它导个文件夹，它把家底全交了。

## 4. 反复让 Agent「把 Rust 写快点」，真能跑赢 SOTA 库
**来源：** HN Front Page  
**链接：** https://minimaxir.com/2026/09/agentic-iteration/  
**uid：** dev_27827ea9

作者延续自己 2025 年的实验，这次验证一个更狠的猜想：让 AI Agent 反复「把 Rust 代码写得更快」，能否跑赢当前最先进的库？结论是可以——在给足护栏与约束的前提下，现代 Agent 写出的 Rust 比现有实现明显更快，再通过 PyO3 把速度传导回 Python。作者强调，光靠「写得更好」这句模糊指令远远不够，必须配合基准测试与明确约束，优化才会真正发生。

> 🗯️ 一句「再快点」，Rust 就卷赢 SOTA 了。

## 5. Drop：给 AI Agent 用的 rootless Linux 沙箱
**来源：** HN Front Page  
**链接：** https://droprun.sh/  
**uid：** dev_7c14f07f

作者做了个叫 Drop 的 Linux 沙箱，动机很朴素：以主用户身份跑第三方程序总让人不安。Drop 用 rootless 方式起临时隔离环境（支持 gVisor），专门跑 AI 编码 Agent：让它带着跳过权限确认的参数尽管跑，权限交给操作系统兜底——幻觉出的 rm -rf ~ 碰不到真实家目录，冲着 ~/.ssh 的提示注入也扑空。

> 🗯️ 让 Agent 放心放飞，锅甩给操作系统。

## 6. google/ax：Google 开源的 Agent 编排运行时
**来源：** GitHub Trending Daily  
**链接：** https://github.com/google/ax  
**uid：** dev_a2d596f4

Google 开源了 Agent 编排运行时 AX（Agent Executor）：一个声明式、高吞吐的编排器，目标是在集群里跑「数十亿级」的自主 Agent 任务，底层靠 Agent Substrate 做沙箱执行。用法像 Kubernetes：写一份 task.yaml 声明工作区与网关，AX 就负责沙箱化、接通工作区、隔离网络并规模化调度。项目仍属早期，稳定版前会有破坏性变更。

> 🗯️ 照 K8s 的方子，再炒一遍 Agent。

## 7. Univer：把 Office 拆成零件，喂给 AI Agent 用
**来源：** GitHub Trending Daily  
**链接：** https://github.com/dream-num/univer  
**uid：** dev_58c296ae

Univer 把自己重新定位为「面向 AI Agent 的 Office Harness」：同一运行时里提供表格、文档、演示、Base、看板等能力。它是一套高性能、可定制的 Office SDK，用插件架构加 Canvas 渲染，对外只暴露一个浏览器与 Node.js 通用的 Facade API。对想做嵌入式表格/文档、又想让 Agent 直接操作办公文档的团队，是个值得关注的自建基座。

> 🗯️ 把 Office 拆成零件，整包喂给 Agent。

## 8. MiMo-V2.6 发布，社区先替它喊了性价比
**来源：** V2EX Share  
**链接：** https://www.v2ex.com/t/1243827  
**uid：** dev_8845a4bc

V2EX 上有开发者发帖报出 MiMo-V2.6 发布，并贴上 OpenRouter 的模型排行与性价比链接，评价「性价比相当不错」。帖子评论区很快热起来，有人开始拿它和同价位模型对比编码、中文任务上的表现。这条更像模型圈的一手情报帖：新版本刚出，真实能力还得靠实测与榜单交叉验证，但至少从价格/性能比看，又多了一个可选的国产模型。

> 🗯️ 新版本刚上线，性价比先喊为敬。

## 9. 面向 AI 的 Unity APK 逆向分析工作流，用 12 个 Skill 固化流程
**来源：** V2EX Share  
**链接：** https://www.v2ex.com/t/1243862  
**uid：** dev_411dfc61

开发者开源了一套「面向 AI 的 Unity APK 逆向分析工作流」，本质是把逆向的整套流程拆成 12 个 Skill，方便 AI 按部就班地执行。作者很坦诚：技术上没什么独门绝技，价值在于把散落的步骤固化成可复用的技能包，目前只支持 Unity 打包的 APK，后续还会补更多 Skill。对做移动端安全研究或自动化逆向的人来说，这份「流程即代码」的整理挺实用。

> 🗯️ 逆向没黑科技，把流程喂给 AI 就行。

## 10. 「AI 大模型的最终归宿不是软件，是机器人」
**来源：** V2EX Tech  
**链接：** https://www.v2ex.com/t/1233752  
**uid：** dev_753cbbb0

楼主抛出一个观点：AI Coding 已经把软件市场卷到供大于求，需求基本饱和，所以大模型的最终归宿不是软件，而是机器人。他的推演是——CV 提供视觉、LLM 提供语言与决策、云计算与算力集群托底，一个通用机器人的「软件基座」其实已经成型，缺的只是硬件与工程化。帖子引来不少反驳，但「软件之后是具身智能」这个判断，确实是今年开发者圈反复出现的声音。

> 🗯️ 软件都卷满了，下一步只能去搬砖。

## 11. 2026 年值得看的五个 MCP 网关
**来源：** Dev.to  
**链接：** https://dev.to/therealmrmumba/top-5-mcp-gateways-in-2026-4f4j  
**uid：** dev_cf3e9bde

文章指出，MCP 解决的是「把 Agent 接上外部工具」；但当组织有几十个 AI 应用、上百个工具、多支团队时，难点就从「连接」变成「管理」：谁能用哪个工具、怎么鉴权、怎么审计调用、怎么把多个 MCP server 收口到一个端点。作者盘点了 2026 年值得看的五个 MCP 网关方案，并强调它们不可互换，要按实际要治理的对象来选。

> 🗯️ 接得上不算本事，管得住才值钱。

## 12. 机器人/物理 Agent Harness 横向拆解：从「更强的模型」到「更好的系统」
**来源：** 博客园 Cnblogs  
**链接：** https://www.cnblogs.com/rossiXYZ/p/22957482  
**uid：** dev_9835f611

一篇系统性长文，主题是为什么模型越来越强，机器人/物理 Agent 的系统却仍不可靠。作者把难点拆成几个层次，给出三条解题主线：解耦、基元化与「把经验外置」，并用一张映射表梳理各家做法。随后逐一拆解 X-OmniClaw、MemoHarness、HumanCLAW 等五个项目，对比其架构、数据流、优缺点与改进方向，最后给出对具身智能趋势的判断。想啃 Agent Harness 设计的人值得一读。

> 🗯️ 模型再强，缰绳没拴好照样翻车。

## 13. 「我用 AI 做完整项目后，总结出一套把需求钉死的工作流」
**来源：** 博客园 Cnblogs  
**链接：** https://www.cnblogs.com/codigger/p/23074289  
**uid：** dev_f3317cd1

一位做了十几年的开发者复盘：今年最大的变化，是把 Codex、Claude Code 这类 Agent 真正用进项目。他在用它们做完一个本地 epub 阅读器后，总结出核心主张——用 AI 写代码不能只甩一条指令，必须建立一套「把预期逐步固化」的工作流：先把需求钉死，再让 Agent 按规格逐步实现，减少返工。踩过的坑与攒下的经验，对正把 Agent 引入日常开发的人很有参考价值。

> 🗯️ 需求不钉死，Agent 就给你自由发挥。

## 14. OpenMCP：MCP 协议被「硬分叉」了
**来源：** HN Show HN  
**链接：** https://github.com/enclawed/omcp  
**uid：** dev_eac2c5cb

有人发起了 OpenMCP（omcp）——Model Context Protocol 的一个社区「硬分叉」。理由是要让协议保持开放、无需许可：异步开发、透明评审、按技术优劣而非闭门审批决定走向。仓库含 omcp 的规范、协议 schema 与文档，schema 先以 TypeScript 定义，再导出 JSON Schema。这是 MCP 生态里少见的「治理分歧直接演变成分叉」的动作。

> 🗯️ 协议谈不拢，那就直接另起炉灶。
