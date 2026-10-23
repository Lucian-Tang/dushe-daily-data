# 开发者日报 · A 轨素材 · 2026-10-24

共 15 条

## 1. 自己写个容器运行时，才发现 Docker 有多怪

- **来源**：HN Front Page
- **链接**：https://codeandcake.dev/posts/2026-10-22-docker-is-weird
- **UID**：dev_55da9e5f

作者从零写容器运行时，拆出几条反直觉事实：容器不是虚拟机，只是被加了限制的普通进程，内核照旧在跑；Linux 根本没有「容器」这个特性，是 namespace、cgroup、网络隔离等五项机制套在一件风衣里；镜像本质就是个文件夹，chroot 一换根目录就算容器。他还吐槽 runc 用 Go 写别扭：没有真正的 fork，只能靠 exec 模拟。

> 毒舌：容器不是虚拟化，是五个内核特性穿一件风衣。

## 2. Local Wikipedia：只给你看走路半小时内的事

- **来源**：HN Front Page
- **链接**：https://edjefferson.com/localwiki/
- **UID**：dev_9076b4b6

有人做了个 Local Wikipedia，把维基百科按地理坐标过滤，只显示你步行半小时范围内、或最近约 6 英里内的条目；附近不足 25 条就补到 25 条，超过 500 条则只保留最近的 500 条。定位只在浏览器本地处理，分享出去的链接不带位置。页面保留了随机条目、A-Z 索引和「换个地方」入口，适合旅游前或刚搬家时摸清周边有什么。

> 毒舌：维基百科终于承认，你只关心家门口那点事。

## 3. Anthropic：让 Claude 给 123 个开源库写形式化证明

- **来源**：HN Front Page
- **链接**：https://www.anthropic.com/research/formal-verification
- **UID**：dev_dbcfc426

Anthropic 让 Claude 在 123 个开源库上自动生成正确性证明，覆盖「某些可执行产物在特定条件下永不崩溃」这类安全性质，甚至下沉到汇编层面验证。写证明的过程中，Claude 还挖出了多年未被发现的 bug——这些代码此前跑过数万亿次测试。文章承认形式化验证一直极贵：seL4 内核实现用 2 人年，形式化验证花了 20 人年；但 LLM 正把瓶颈从人力转向「规约怎么写」。

> 毒舌：测试跑一万亿次，不如让模型证一遍。

## 4. NVIDIA 开源 OpenShell：给 AI Agent 建个带门禁的沙箱

- **来源**：HN Front Page
- **链接**：https://github.com/NVIDIA/OpenShell
- **UID**：dev_16b5eef5

OpenShell 是面向「成批自主 Agent」的运行时：每个 Agent 跑在独立沙箱里，内核层拦截文件访问、系统调用和网络连接，凭据不会交给 Agent 本人，只在发往白名单端点的请求里临时注入。策略变更上线前还会做形式化验证，先算出这次改动会额外放开哪些权限。它要解决的是同一个矛盾——Agent 越能干（装包、调 API、读文件），越容易顺手把你的数据和密钥一起带走。

> 毒舌：给 Agent 自由的正确方式，是先给它画好牢房。

## 5. ClickBench 榜单翻车：pgrust 被指为 43 条查询手工写死计划

- **来源**：HN Front Page
- **链接**：https://github.com/ClickHouse/ClickBench/pull/2165
- **UID**：dev_203ec9e7

ClickHouse 的 Alexey Milovidov 提交 PR 要求把 pgrust 从 ClickBench 除名，理由是作弊：源码里有一份 clickbench.ron，自称「为 43 条基准查询手工降级的物理计划」。匹配器按查询形状直接返回答案，Q20/Q21/Q23 纯查缓存；冷启动 10.8 秒，热跑几毫秒。上一版提交也隐瞒过类似缓存。

> 毒舌：把答案背下来的考生，成绩当然好。

## 6. jank：长在 C++ 上的 Clojure，模板和 RAII 都能直接用

- **来源**：HN Front Page
- **链接**：https://jank-lang.org/
- **UID**：dev_9b999e3c

jank 是一个原生 Clojure 方言，直接跑在 LLVM/C++ 之上。它的卖点是无缝 C++ 互操作：模板、虚函数、异常、重载解析、RAII 都能在 Clojure 代码里自然使用，include 头文件即可，不需要写胶水层。它自带基于 Clang 的 JIT，支持 REPL 驱动的交互开发，也能在代码里直接调用 C++ 类型和函数。适合想在脚本层复用现有 C++ 库、又不想维护绑定的人。

> 毒舌：Clojure 的括号，终于能直接抱住 C++ 了。

## 7. Chrome 试水 HTML-in-Canvas：把 DOM 画进画布，还能点

- **来源**：HN Front Page
- **链接**：https://developer.chrome.com/blog/html-in-canvas-origin-trial
- **UID**：dev_5fbd7ba8

Chrome 开放 HTML-in-Canvas API 的 origin trial：可把真实 DOM 内容绘制进 2D canvas 或 WebGL/WebGPU 纹理，同时保留可交互、可访问、可选中文字、可右键存图，翻译、查找、阅读模式照常工作。过去只能在 DOM 的语义能力和 canvas 的性能之间二选一，游戏和 Figma 类应用为此付出巨大成本；现在两者能叠加，代价是处理同步与合成。

> 毒舌：DOM 和 Canvas 吵了十年，终于肯同居了。

## 8. OpenBMB 的 VoxCPM2 冲上趋势榜：无分词器的多语种 TTS

- **来源**：GitHub Trending Daily
- **链接**：https://github.com/OpenBMB/VoxCPM
- **UID**：dev_e8367b4c

OpenBMB 的 VoxCPM2 冲上 GitHub Trending 前列，已有 4 万星、4.6 千 fork，Apache-2.0。它走 tokenizer-free 路线，用扩散自回归模型直接生成连续语音表示，主打多语种合成、可控音色和「像本人」的克隆，并提供 HF、ModelScope 权重与在线 Demo。传统 TTS 的离散 token 环节被省掉，部署门槛也低。

> 毒舌：TTS 卷到最后，连分词器都嫌多余。

## 9. 嫌 IDEA 吃内存，有人自己写了个开源平替

- **来源**：V2EX
- **链接**：https://www.v2ex.com/t/1251116#reply65
- **UID**：dev_807a7943

作者用了多年 IDEA，受不了几个 G 内存和风扇狂转，照着 IDEA 的操作习惯写了个轻量替代 openidea：快捷键、工具窗口、双击 Shift 搜索都尽量对齐，已支持补全、跳转、查引用、跑测试、断点调试，Git、终端、数据库也塞了进去，语言靠配置扩展，目前 60 多种。评论区一半在要内存截图，一半在贴同类项目——JetBrains 没做成的 Fleet，AI 时代谁都想试。

> 毒舌：JetBrains 没干成的事，评论区人手一个。

## 10. 他把个人网站建成了《我的世界》

- **来源**：V2EX
- **链接**：https://www.v2ex.com/t/1251348#reply14
- **UID**：dev_a9487eea

一个爱折腾网站的人厌倦了换模板，借助 AI 把个人主页从二维网页改成三维世界：可以自由移动，里面有篮球场、健身房、工作台，还有昼夜交替和天气系统。二维页面也能内嵌，按 F 就能看。方块风性能开销小，手机访问也不卡。他说逛一圈像去朋友家做客——比起千篇一律的作品集，这至少让人记住了路怎么走。

> 毒舌：别人卷排版，他直接把首页改成了地皮。

## 11. 统计 7000 个线上产品的技术栈：新项目正在集体换血

- **来源**：V2EX
- **链接**：https://www.v2ex.com/t/1251289
- **UID**：dev_3ee8741c

作者抓了 7000 多个 AI 原生产品的技术栈，逐条附出处。按上线年份对比：事务邮件 SendGrid 从 51% 掉到 13%、Resend 从 41% 涨到 82%；数据库 Firebase 19%→9%、Supabase 33%→64%；分析工具 Mixpanel 30%→9%、PostHog 52%→88%。迁移 PR 一年涨 11 倍，约 48% 由 agent 提交。

> 毒舌：大家的训练数据一样，选型自然也一样。

## 12. METR 在 OpenAI 蹲了三周，发现监控漏的是工程问题

- **来源**：Dev.to
- **链接**：https://dev.to/reidmarlow/the-agent-loophole-nobody-logged-2076
- **UID**：dev_bec783e5

METR 和 Redwood 在 OpenAI 驻场三周压测内部 Agent 监控，产出 61 页报告。最扎眼的漏洞不在提示注入，而在上下文压缩：2026 年 5 到 7 月监控管线不记录 compaction，约 10% 的合格 Codex 流量处于无监控状态；而监控只在 Agent 交还控制权时才评估，一直调工具就能永不触发，压缩再把旧轨迹擦掉。另有手法能让数百条动作不进日志。

> 毒舌：不是模型会骗人，是日志没记全。

## 13. 每周跑 lint，坏链接一次都没减少

- **来源**：Dev.to
- **链接**：https://dev.to/michaeltuszynski/the-lint-ran-every-week-the-dead-link-count-never-went-down-22m1
- **UID**：dev_d93b6894

作者八月写过「Karpathy 的 LLM wiki 靠每周 lint 能修掉大部分死链」，三个月后自己打脸：检查器连续十周准点运行，坏链从 109 条涨到 146 条，孤儿页从 117 涨到 124，一次都没下降；前两周甚至扫的是已废弃目录，零页面还报告「一切正常」。结论很朴素：检测不等于修复，自动化只能告诉你哪里烂了，没人动手就只是每周生成一份更长的账单。

> 毒舌：体检报告越来越厚，病人一步没动。

## 14. 两天烧掉 100 亿 token：一个游戏公司实习生怎么爬攻略

- **来源**：博客园
- **链接**：https://www.cnblogs.com/Reisentyan/p/23395393
- **UID**：dev_571ebae1

游戏公司要做内置攻略问答 AI，实习生负责收集百万级攻略文本。他们让 DeepSeek 为每个站点现写爬虫再自己调用，最多同时开四十多个子代理，靠最高 99.9% 的缓存命中把成本压到十分之一；两天连同缓存消耗约 100 亿 token。真正的坑在解析：网页存成 PDF 后乱码、重复、广告比正文还多，而「先采集再想字段」导致大量重复访问，每处理一万个文件光联网就要 20 元。

> 毒舌：token 烧得起，返工烧不起。

## 15. 别再说「请返回 JSON」了：用 Pydantic 管住大模型输出

- **来源**：博客园
- **链接**：https://www.cnblogs.com/wang_yb/p/23409507
- **UID**：dev_3645ba89

文章用「从简历抽结构化信息」举例：模型返回常裹着「好的，这是结果」和 ```json 围栏，字段值写成「五年」「15k左右」，还可能漏 key。最贵的不是当场报错的，而是「15k左右」*12 在 Python 里合法执行、悄悄写进年薪字段。作者给出两道关：先用正则抠出最外层花括号，再用 Pydantic 定义类型、范围、格式和跨字段校验，并强调格式错误和内容错误要分开处理。

> 毒舌：模型不会报错，它只会一本正经地写错。
