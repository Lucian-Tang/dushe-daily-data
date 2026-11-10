# 开发者日报 A 轨素材 · 2026-11-11

> 共 15 条 | HN Front Page 4 · GitHub Trending Daily 3 · V2EX Share 3 · Dev.to 2 · 博客园 Cnblogs 3

## 1. 一个 tar 包，十几种工具解出八种结果

作者用一条 GNU tar 命令造出「最难解的压缩包」：借 pax 头把硬链接改名成 café，再塞进 512 字节 size，恰好等于一个 tar 头。同一个包在十几种实现里解出 8 种结果：bsdtar 把 512 字节写进硬链接，7-Zip 和 Rust 跳过，Java 多造一个文件，Ruby 不解 café 还留下 PaxHeaders 目录，.NET 和 Julia 干脆拒收。

> 一个压缩包，十几种实现，八种人生。

来源：HN Front Page · [https://stoppels.ch/2026/11/07/the-hardest-tarball.html](https://stoppels.ch/2026/11/07/the-hardest-tarball.html) · `dev_397bc829`

## 2. 亚马逊把 Sonnet 换成一个不会说话的决策模型，省了 98%

亚马逊内部工单系统原本用 Claude Sonnet 4.6 打标签，两位工程师换成 Strands Decider：只对选项输出概率和置信度的决策模型，不生成文本。E4B 准确率反超线上 Sonnet，单次调用从 4215ms 降到 897ms，每张工单 token 从 6724 降到 2010，成本少 98%，一年省数百万美元。链路是 SQS + Lambda + SageMaker 端点。

> 98% 的成本省下来，靠的是不让模型说话。

来源：HN Front Page · [https://strandsagents.com/blog/amazon-saves-millions-replacing-sonnet-with-strands-decider](https://strandsagents.com/blog/amazon-saves-millions-replacing-sonnet-with-strands-decider) · `dev_f3e668c6`

## 3. e-means：用十分之一的 epoch 跑赢 k-means

k-means 是机器学习里少见还在用全批量优化的算法，Lloyd 每次迭代都扫全量数据。e-means 改用小批量加指数移动平均更新质心，批大小和步长由 scaling law 自动推导、不用调参，再加新的初始化、死簇复活和收尾阶段。作者称达到同样测试损失只要 1.2 到 3 个 epoch，GPU 端到端快 10 到 45 倍，CPU 上比 Faiss 快 8 到 15 倍。

> 调参调半天，不如换条更新规则。

来源：HN Front Page · [https://e-means.github.io](https://e-means.github.io) · `dev_78569638`

## 4. .NET 11 发布：C# 15 联合类型 + 全面 Agent 化

微软发布 .NET 11：C# 15 带来联合类型和封闭继承，能在编译期检查分支是否穷举；运行时数百项优化，新增 Native AOT CLI host 和常驻 MSBuild server；ASP.NET Core 支持异步验证与 OpenAPI 3.2，MAUI 默认切 CoreCLR；AI 方向给了 Microsoft.Extensions.AI、MCP 和 Agent Framework。

> STS 支持两年，升级比版本号还快。

来源：HN Front Page · [https://devblogs.microsoft.com/dotnet/announcing-dotnet-11](https://devblogs.microsoft.com/dotnet/announcing-dotnet-11) · `dev_8aed28d5`

## 5. addyosmani/agent-skills：11.5 万星的工程流程技能包

Addy Osmani 开源 agent-skills，把资深工程师的工作流做成 Agent 技能包，按定义、计划、实现、验证、评审、上线六个阶段组织，对应 /spec、/plan、/build、/test、/review、/ship 等 9 个命令。仓库已到 11.5 万星，支持 Claude Code、Codex、Cursor，/build auto 能一次批准后逐任务实现、失败即停。

> 11.5 万星，说明大家都缺一套干活流程。

来源：GitHub Trending Daily · [https://github.com/addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) · `dev_98856e0e`

## 6. claude-quickstarts：官方把 Agent 的坑都踩了一遍

Anthropic 的 claude-quickstarts 收录可直接改造成产品的示例：客服 Agent、金融数据分析、计算机操作、浏览器自动化。最值得看的是 Computer Use Best Practices——跑在原生 macOS 上的参考实现，演示怎么写可靠的 computer-use Agent：显式工具定义、图像缩放裁剪、prompt caching、服务端压缩和沙箱 shell。

> 官方示例的价值，在于它替你踩过坑。

来源：GitHub Trending Daily · [https://github.com/anthropics/claude-quickstarts](https://github.com/anthropics/claude-quickstarts) · `dev_a830acbf`

## 7. tokio 团队开源 Topcoat：Rust 的全栈框架

tokio 团队开源 Topcoat，自称 Rust 的「full full-stack」框架：服务端渲染、路由、静态资源、客户端交互一套打包，把 Rust 写 Web 应用时散落的胶水代码收进框架。仓库 6600 星、MIT 协议，README 专门放了 llms.txt 让编码 Agent 直接读 API 和约定。Rust 全栈一直缺一个开箱即用的答案，这是最新一次尝试。

> Rust 全栈的答案，又来了一个。

来源：GitHub Trending Daily · [https://github.com/tokio-rs/topcoat](https://github.com/tokio-rs/topcoat) · `dev_19c76c37`

## 8. Egg：不要 GC、不写生命周期，内存安全靠编译器

V 友 femto 介绍自研语言 Egg：编译成可移植 C99，没有 GC，但释放后使用、重复释放、内存泄漏都是编译错误，也不用写生命周期标注。设计是单一所有者、借用随最后一次使用结束，溢出、除零、越界都 panic；IO 和内存分配必须写进函数签名的 uses，线程间只靠 channel 转移所有权。编译器 eggc 约 1.2 万行，fib(40) 约为 C 的 1.53 倍耗时。

> 不要 GC 不要生命周期，编译器把活全干了。

来源：V2EX Share · [https://www.v2ex.com/t/1255840](https://www.v2ex.com/t/1255840) · `dev_63597ffa`

## 9. myco：让云端 Claude 把糙活派给本地 DeepSeek

为了省额度，作者做了 myco：让云端 Claude 把糙活派给本地跑的 DeepSeek。它不替换现有 agent，而是把 claude.ai、Claude Code、Codex、OpenCode 等节点连起来，让远端 agent 调本地 agent。卖点是「200 美元的 Claude 调 10 美元的 DeepSeek」，另有 Mac 和 Windows 管理界面。

> 200 美元的模型指挥 10 美元的模型。

来源：V2EX Share · [https://www.v2ex.com/t/1255859](https://www.v2ex.com/t/1255859) · `dev_15469fda`

## 10. 做微信小游戏踩的坑：内存按分辨率算，不是按文件大小

一篇把微信小游戏坑位讲透的复盘：iOS 上微信进程内存和显存共用约 1G 到 1.4G，5 秒内两次内存警告就销毁游戏；PNG 文件小但进显存按分辨率算，2048×2048 一张就是 16MB，开 mipmap 再加三分之一。解法是 ASTC 压缩纹理加及时卸载，作者战斗峰值从约 1G 降到 200MB。还提到审核要选「联网」、代码加固混淆选中等否则主包超 4M、新游种子要先做好新手引导。

> 内存按分辨率算，这才叫像素级焦虑。

来源：V2EX Share · [https://www.v2ex.com/t/1255945](https://www.v2ex.com/t/1255945) · `dev_a8c54994`

## 11. Reddit 认定我是机器人，我的 karma 停在 1

作者给内容项目开了个 Reddit 新号，认真写评论、不刷链接，结果每次发帖都弹人机验证，账号 karma 停在 1。平台逻辑并不蠢：零历史、高热情、多社区同时发精致评论，和垃圾农场的画像完全一致，验证码和限流是在抬高造假成本。最后他的工作流变成周中写好文档、半夜手动一条条粘贴，效率工具的最后一步还是人。他的结论是：平台不欠你的自动化一个入口。

> 防机器人的墙，先挡住了认真写字的人。

来源：Dev.to · [https://dev.to/aheadkit/reddit-is-convinced-im-a-robot-my-karma-is-1-4m7i](https://dev.to/aheadkit/reddit-is-convinced-im-a-robot-my-karma-is-1-4m7i) · `dev_b712aa68`

## 12. 把 Jest 换成 Vitest，也值得先写一份 spec

把 Jest 换成 Vitest 被当成机械迁移，作者还是先写 spec：清点 68 个测试文件、约 120 处 jest.fn、15 处 jest.mock、219 次 toBeInTheDocument；明确非目标——不迁移没测试的老包、不换 happy-dom、不改测试行为；完成标准是断言不变全绿、CI 不变、删掉 5 个依赖。结果一天写 spec、一天迁移、5 个小提交。

> 机械迁移也要写 spec，不然就成重写。

来源：Dev.to · [https://dev.to/dennervidal/even-a-mechanical-migration-deserves-a-spec-2ibo](https://dev.to/dennervidal/even-a-mechanical-migration-deserves-a-spec-2ibo) · `dev_71fc992e`

## 13. 只打乱 10% 标签，loss 很健康，模型在背错答案

一篇用真机实验拆「模型学不会」的复盘：只把 10% 训练样本的标签打乱，测试准确率就从 96.2% 掉到 89.3%，而训练 loss 照样降到 0.022，看着非常健康——模型其实在背那 10% 的错答案。全错时准确率 0.098，等于瞎猜。作者给两道防线：抽样可视化检查图文是否对应，以及对图片和标签做哈希校验；结论是数据对齐的优先级高于调参。

> loss 很健康，模型在背错答案。

来源：博客园 Cnblogs · [https://www.cnblogs.com/dawudexiaowu/p/23614706](https://www.cnblogs.com/dawudexiaowu/p/23614706) · `dev_a82eb6c1`

## 14. 把 DSH 当工位用了 64 天：1093 个会话的诚实复盘

作者把 DSH 当日常工位用了 64 天，解开 1093 个会话的 zstd 存档逐条统计：117681 个步骤、338207 次工具调用、22.62B token、39955 个后台作业。两个反直觉发现：三分之二的会话不是他发起的，而是派出去的代理；真正拖慢效率的几乎都和模型聪明程度无关，而是路径找不到、命令超时、要替换的文本已过期。

> 三分之二的会话是派出去的，人成了调度员。

来源：博客园 Cnblogs · [https://www.cnblogs.com/znlgis/p/23617216](https://www.cnblogs.com/znlgis/p/23617216) · `dev_a0836903`

## 15. 图不搬出库，GraphRAG 怎么做多跳查询

供应链溯源要做三级供应商多跳查询，三次 join 套递归 CTE 在千万级数据上要跑四十多秒；上独立图库能进秒级，但同步链路、第二套权限和两份存储成了新麻烦。作者借金仓「库内知识化」讲另一条路：二维表直接图化，零搬迁零冗余，表变图即变，权限沿用库内行级规则，本质是一份数据两种视图。他也划了边界——库内图查询够用时，外挂图库的必要性就下降。

> 图不用搬出库，搬的是运维的命。

来源：博客园 Cnblogs · [https://www.cnblogs.com/dicengwanjialaozhang/p/23614845](https://www.cnblogs.com/dicengwanjialaozhang/p/23614845) · `dev_ddb9c3e2`
