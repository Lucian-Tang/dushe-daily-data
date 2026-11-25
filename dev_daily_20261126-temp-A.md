# 开发者日报 A 轨素材 · 2026-11-26

> 共 15 条 | HN Front Page 6 · V2EX Share 3 · GitHub Trending Daily 2 · Dev.to 2 · 博客园 Cnblogs 2

## 1. Claude-BugHunter 冲上 Trending：84 个技能把 Claude 变成红队打手

elementalsouls/Claude-BugHunter 是一个面向外部红队与漏洞挖掘的 Claude Code 技能包：84 个技能、15 个 slash 命令，内置 24 类核心漏洞的 681 份已披露报告模式，还带企业身份与基础设施攻击矩阵。两万多 star 说明安全圈已经把 agent 当常规工具用了；但真拿它去打目标之前，先想清楚授权范围，AI 帮你写报告不帮你担责任。

> 84 个技能齐活，就差一张合法授权书。

来源：GitHub Trending Daily · [https://github.com/elementalsouls/Claude-BugHunter](https://github.com/elementalsouls/Claude-BugHunter) · `dev_1a9ba9eb`

## 2. superpowers 32 万星：一套把 agent 关进流程里的开发方法论

obra/superpowers 是一套 agentic skills 框架和软件开发方法论，32 万 star 已经不能用「工具」形容了。它的核心不是给模型加能力，而是用固定流程约束模型：先澄清需求、再出计划、再分步实现、每步验证。换句话说，它治的是 agent 上来就瞎写代码的毛病；至于流程能不能救回判断力，那得看用的人。

> 给 agent 上流程，等于给野马套缰绳。

来源：GitHub Trending Daily · [https://github.com/obra/superpowers](https://github.com/obra/superpowers) · `dev_488567a9`

## 3. iOS Safari 的 60 FPS 天花板，被滚动合成器绕过去了

WebKit 在 iOS 上把 requestAnimationFrame 和触摸事件锁在 60Hz，哪怕屏幕是 120Hz，除非你去开发者设置里翻那个「Prefer Page Rendering Updates near 60fps」开关。作者把交互交给合成器驱动的滚动：手指到数字化仪、到合成器、再到 GPU，全程不走 JS 回环，动画就能跑满高刷。结论很刺：想要原生手感，别跟 rAF 较劲。

> 别卷 JS 性能了，把活交给合成器。

来源：HN Front Page · [https://rida.dev/blog/bypassing-ios-safari-60-fps-limit](https://rida.dev/blog/bypassing-ios-safari-60-fps-limit) · `dev_fcb70c4a`

## 4. 用 5600 个 Lambda 跑 Qwen：一场 80 倍负利润的行为艺术

作者把 Qwen 推理拆到 5600 个 AWS Lambda 上跑，标题直接写明「80 倍负利润」。这类文章的乐趣不在省钱，而在验证 serverless 的边界：冷启动、函数间通信、状态传递、并发配额，每一条都会把天真的想法打回去。当玩具很爽，当生意就是给 AWS 交学费，但至少他替你把坑都踩了一遍。

> 亏 80 倍还坚持跑完，这叫科研精神。

来源：HN Front Page · [https://noahbuilt.it/writing/qwen-on-5600-lambdas](https://noahbuilt.it/writing/qwen-on-5600-lambdas) · `dev_58475d9a`

## 5. 3 美元接管美国财政部子域名，这漏洞便宜得离谱

Intruder 的研究人员发现美国财政部若干子域名存在悬空 DNS 记录，指向已释放的云资源，于是花每个 3 美元注册对应资源就完成了接管。子域名接管是老问题，但出现在 .gov 域名上就变成钓鱼与信任链攻击的现成跳板。资产清单没人清、下线没人回收，安全预算再多也补不上这种管理漏洞。

> 接管一个 gov 子域，比买杯咖啡还便宜。

来源：HN Front Page · [https://www.intruder.io/research/taking-over-us-treasury-subdomains-for-3-each](https://www.intruder.io/research/taking-over-us-treasury-subdomains-for-3-each) · `dev_e76fcb15`

## 6. Google 放出整数分解论文，HN 在传「P 是不是被攻破了」

Google Research 仓库里出现一批关于整数分解、离散对数等方向的论文，加上 Reddit 上「某实验室可能破解了 P 问题」的传言，HN 直接把这条顶到 220 分、180 多条评论。冷静点看：整数分解有多项式算法和 RSA 被破是两件事，论文也未必经过同行评审。但密码学圈这一晚估计没人睡得着。

> 传言跑得比论文快，密码学圈先失眠。

来源：HN Front Page · [https://github.com/google-research/google-research/tree/master/cogentic_research_papers](https://github.com/google-research/google-research/tree/master/cogentic_research_papers) · `dev_ed654fc3`

## 7. Windows 响度均衡被逆向出来，移植到了 PipeWire

有人把 Windows 的 Loudness Equalization（响度均衡）逆向实现并移植到 Linux 的 PipeWire，206 分说明被「看片时爆炸声太响、对白听不清」折磨过的人有多少。动态范围压缩本来是影院和广播的老技术，桌面 Linux 一直缺个好用的默认实现。这种小而具体的补丁，比又一个「年度 Linux 桌面元年」宣言有用得多。

> Linux 桌面的进步，靠这种脏活累活。

来源：HN Front Page · [https://github.com/xoxorwr/pw-loudness-eq](https://github.com/xoxorwr/pw-loudness-eq) · `dev_66062635`

## 8. 老 Nvidia、ATI 技术演示复活：在浏览器里重跑 20 年前的 GPU Demo

有人把早年 Nvidia 和 ATI 的显卡技术演示收集起来，重新在浏览器里跑通，262 分、50 多条评论，一堆人当场回忆起当年换显卡的理由。技术上这靠 WebGL/WASM 把老着色器和固定管线效果重新实现，工作量不小。它的价值不在怀旧，而在于给图形学教学提供了活的标本——比看截图强。

> 当年为这些 demo 换显卡，现在用浏览器白嫖。

来源：HN Front Page · [https://gpu-demo-gallery.pages.dev/](https://gpu-demo-gallery.pages.dev/) · `dev_0b9958ab`

## 9. Pi Bot 开源：一群在你自己电脑上干活的 AI Bot，大脑也在本机

Pi Bot 是一个 11 月 21 日以 Apache-2.0 开源的桌面应用：一群有名字的 Bot，可以私聊也可以拉进群分工，统筹拆计划、成员各做一步，交付文件由程序检查，不通过就派回去返工。Bot 在你指定的文件夹里跑命令、改文件、操作电脑、调 MCP，高风险步骤先停下等你批准，每一步都记在本地操作记录里。卖点是数据不出机器，代价是算力和运维都得自己扛。

> bot 住进你电脑，隐私和电费一起留下。

来源：V2EX Share · [https://www.v2ex.com/t/1259779#reply0](https://www.v2ex.com/t/1259779#reply0) · `dev_a3587c14`

## 10. 1.5MB 的中文文本脱敏小模型：2K 字 17ms，无依赖

作者蒸馏了一个 1.5MB 的文本脱敏小模型，能识别姓名、住址、证件号等实体，支持中英，无依赖，2K 字识别 17ms，还配了在线 demo。小模型在垂直任务上打赢通用大模型是这两年最实用的趋势：不上传数据、不走网络、成本近乎为零，正好卡在合规要求最难受的位置。缺点是实体边界和长尾场景还得靠规则兜底。

> 1.5MB 就能识别你是谁，大模型白练了。

来源：V2EX Share · [https://www.v2ex.com/t/1259724#reply2](https://www.v2ex.com/t/1259724#reply2) · `dev_44aad4a4`

## 11. 把 @playwright/mcp 换成纯 Rust 管道：内存降 90.7%，速度反超 Chrome 2.76 倍

作者给 agent 复用本地 Chrome 登录态的工具 sessfork 换了后台：不用 Node 版 @playwright/mcp，改用纯 Rust 浏览器 Moli 做 12 标签页重型 DOM 压测，结果内存暴降 90.7%、速度反超 Chrome 2.76 倍，还附了 M4 上的复现步骤。结论反直觉：MCP 那层封装看着方便，实际是性能税。给 agent 造基础设施，迟早要把它剥掉。

> MCP 一时爽，压测火葬场。

来源：V2EX Share · [https://www.v2ex.com/t/1259622#reply7](https://www.v2ex.com/t/1259622#reply7) · `dev_68fe898f`

## 12. Obsidian 接 Claude Desktop/Cursor：用 TOON 把 token 开销砍掉 36.7%–45%

把个人 Obsidian 库通过 MCP 接进 Claude Desktop 或 Cursor，很快会撞上两个瓶颈：网页剪藏污染上下文、笔记体积撑爆 token 预算。作者的做法是先用 TOON（Token-Oriented Object Notation）做结构化压缩，再控制检索粒度，把 token 开销降了 36.7% 到 45%。思路不新但很实用：AI 时代，上下文管理就是新的数据库调优。

> 上下文不是越多越好，是越贵越要省。

来源：Dev.to · [https://dev.to/obolonsky/connecting-obsidian-to-claude-desktop-cursor-via-mcp-toon-cutting-token-overhead-by-367-45-1fa4](https://dev.to/obolonsky/connecting-obsidian-to-claude-desktop-cursor-via-mcp-toon-cutting-token-overhead-by-367-45-1fa4) · `dev_79ebe3bd`

## 13. .NET 11 发布当天，.NET 8 和 9 一起停止支持

.NET 11 正式发布，同时 .NET 8 和 9 停止支持。文章梳理了 C# 15 的联合类型、封闭层次等新特性，以及 ASP.NET Core、Blazor、SDK、EF Core、MAUI 和 AI 开发链路的变化，并给出升级前要确认的目标框架、破坏性变更和第三方包兼容清单。对企业项目来说，这不是「要不要升」，而是「什么时候被迫升」——先查依赖再动手。

> 微软的节奏：新版发布，旧版当场去世。

来源：博客园 Cnblogs · [https://www.cnblogs.com/shenchuanchao/p/23779842/dotnet-11-released-dotnet-8-9-dead-upgrade-or-wait](https://www.cnblogs.com/shenchuanchao/p/23779842/dotnet-11-released-dotnet-8-9-dead-upgrade-or-wait) · `dev_689bc3f2`

## 14. 订单超时自动关闭：7 种方案，选错一个就等着背锅

下单 30 分钟不付款自动关单、释放库存，外卖 15 分钟、酒店 1 小时，听着像改个状态就完事，实际要连带释放库存、退优惠券、记流水、发通知，还要保证幂等和最终一致。文章把定时轮询、延迟队列、时间轮、Redis 过期监听、数据库调度等 7 种方案摊开对比，各有各的坑：轮询扫表会拖垮库，Redis 过期事件不可靠，延迟消息又怕堆积。

> 关单不是改状态，是七场事故的入口。

来源：博客园 Cnblogs · [https://www.cnblogs.com/codigger/p/23774706](https://www.cnblogs.com/codigger/p/23774706) · `dev_97a8a1f8`

## 15. 在 4GB 显存的 GTX 1650 上跑 Gemma E2B：约束部署的真实手感

作者在 4GB 显存的 GTX 1650 上折腾 Gemma E2B，记录量化、上下文长度、KV cache 与吞吐之间的反复取舍。结论对大多数人有参考价值：小显存不是不能跑，而是每一步都要换算法——降精度、切分模型、限制上下文，最后得到的性能数字往往比宣传低一个量级。边缘部署的真相是，硬件预算决定你能谈什么体验。

> 4GB 显存跑大模型，跑的是耐心。

来源：Dev.to · [https://dev.to/gde/thinking-on-constrained-deployments-gemma-e2b-on-4gb-1650-487c](https://dev.to/gde/thinking-on-constrained-deployments-gemma-e2b-on-4gb-1650-487c) · `dev_8a852662`
