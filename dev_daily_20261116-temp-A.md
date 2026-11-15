# 开发者日报 A 轨素材 · 2026-11-16

> 共 15 条 | HN Front Page 5 · GitHub Trending Daily 3 · V2EX Share 3 · Dev.to 2 · 博客园 Cnblogs 2

## 1. 159041 个 Lovable 项目里，大量应用在裸奔

Crissy Field 与《商报》分析了 2025 年 12 月到 2026 年 9 月的 159041 个 Lovable 项目，其中 24664 个网站在打开时就把数据库记录发给了未登录访客。用同一个 key 只读请求还能捞到更多：一个德国论坛露出 8 万多份个人档案和 20 多万条聊天记录，某服务商泄露 1000 多条含护照号的证件信息。安全责任条款却划给了用户。

> 平台替你生成应用，也替你泄露数据。

来源：HN Front Page · [https://www.crissyfield.de/research/lovable-en](https://www.crissyfield.de/research/lovable-en) · `dev_353cca19`

## 2. 所有 AI 生成的代码都应该开源

作者主张 AI 生成的代码应全部开源或直接 CC0 入公有领域。理由有两条：模型本身就是拿几十年开源代码、以及 CC 授权要求署名的 Stack Overflow 内容喂出来的，把这份集体知识变成闭源产品等于洗授权；再者纯 AI 生成的代码没有人类作者，按「猴子自拍」判例根本不该享有版权。他也承认现实多是混合，但那种只写 prompt、连输出都不看的部分更该交出来。

> 拿开源喂出来的模型，回头卖你闭源。

来源：HN Front Page · [https://jakub.jankiewicz.org/blog/ai-code-open-source](https://jakub.jankiewicz.org/blog/ai-code-open-source) · `dev_ce2412f8`

## 3. HTTP 新增状态码 483：我不是冰箱

IETF 出现一份新草案，为 HTTP 增加状态码 483「I'm Not a Freezer」：当服务器看懂了一个要求冷冻或冷藏能力的请求、但自己没这个能力时，就返回它。文档还顺手厘清了冰柜、冰箱、低温机房、被冻住的软件进程，以及那些自称提供「冷存储」的在线服务之间的区别，并讨论了它与 418 的关系、缓存和中间代理该怎么处理。草案 11 月 15 日发布，半年后过期。

> 418 是茶壶，483 是冰箱，RFC 像动物园。

来源：HN Front Page · [https://datatracker.ietf.org/doc/draft-banffy-httpbis-not-a-freezer](https://datatracker.ietf.org/doc/draft-banffy-httpbis-not-a-freezer) · `dev_aba8e762`

## 4. 法院驳回撤诉：DRAM 三巨头要接着打官司

11 月 14 日加州北区法官 Noël Wise 全部驳回三星、SK 海力士、美光的联合撤诉动议，指控三家合谋削减 DDR5 等通用 DRAM 供应、把产能转去 HBM 的集体诉讼得以继续。法院认定这不是 2022 年 DRAM II 案重演：HBM 长期锁单、拒签通用 DRAM 长约、美光关停 Crucial、新厂延期、创纪录价格下仍不扩产，加上卡特尔前科，足以支撑合谋的合理推断。

> 内存涨价不是天灾，法院说可能是人祸。

来源：HN Front Page · [https://litnews.ai/articles/garciaguirre-samsung-sk-hynix-micron-dram-conspiracy-suit-survives-dismissal](https://litnews.ai/articles/garciaguirre-samsung-sk-hynix-micron-dram-conspiracy-suit-survives-dismissal) · `dev_94961532`

## 5. 一张图看懂 80 年软件职称变迁

做了多年 Head of DevOps 的作者拉着 Claude 画了张 1940 年代至今的软件职位家谱：104 个职称、七个族系（开发、架构与管理、运维基建、网络与安全、数据与 AI、测试、支持），纵向按五年一行排布，实线表示演化、虚线表示转岗。他顺手发现：1947 年 coding 被当作低薪文书活、多由女性承担；而 SRE、DevOps、平台工程不过是同一份工作换名字。

> 头衔换了一轮又一轮，活还是那点活。

来源：HN Front Page · [https://zwischenzugs.com/2026/11/03/a-family-tree-of-software-job-titles](https://zwischenzugs.com/2026/11/03/a-family-tree-of-software-job-titles) · `dev_cd628d32`

## 6. chrome-devtools-mcp：让 agent 亲手调试浏览器

Chrome 官方 DevTools 团队出的 MCP 服务器，让编码 agent 接管一个真实 Chrome：抓性能 trace、读控制台报错与网络请求、点页面元素、截图，还能拿到无障碍树和 Lighthouse 审计结果。一条 npx 就能挂到 Claude Code、Cursor 上。仓库 5.67 万星，是这轮「让 agent 会调试」里最正统的实现——调试协议本来就是他们家的。

> 协议是自家的，agent 当然先学会调试。

来源：GitHub Trending Daily · [https://github.com/ChromeDevTools/chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp) · `dev_30abfecc`

## 7. Google Labs 的 Agent Skills 库：把设计稿变成前端

Google Labs 放出的 Agent Skills 库，配合 Stitch MCP 把设计稿转前端拆成一组可复用技能，遵循 Agent Skills 开放标准，在 Antigravity、Gemini CLI、Claude Code、Cursor 里都能加载。9.1 千星。意义不在单个技能多强，而是 Google 开始用同一套标准往 agent 生态里塞自己的工具链。

> 谁定下标准，谁就占住整个生态。

来源：GitHub Trending Daily · [https://github.com/google-labs-code/stitch-skills](https://github.com/google-labs-code/stitch-skills) · `dev_783c42e2`

## 8. 腾讯开源 LoopForge：给编码 agent 装审批闸门

腾讯开源的编码 agent 交付工作流引擎，Go 编写，1.3 千星。核心是把 CodeBuddy、Codex、Claude Code 这些 agent 编排进一条带人工审批闸门的流水线：脚本定义步骤，agent 干活，关键节点停下来等人签字，主打 human-on-the-loop 和自托管。它要解决的不是「让 agent 更聪明」，而是「让 agent 的产出能被组织放心合并」。

> agent 干活容易，让人敢合并才难。

来源：GitHub Trending Daily · [https://github.com/Tencent/LoopForge](https://github.com/Tencent/LoopForge) · `dev_b4f2fa73`

## 9. DiffCode：4MB 的 Mac 原生 diff 查看器

代码基本交给 agent 写了，可 review 还得看 diff，而为了看 diff 又得开 Xcode、Android Studio 或 JetBrains 全家桶，一启动吃掉几个 G。V 友于是做了 DiffCode：不是 IDE，是纯 Mac 原生的 diff 查看器，安装包 4MB，启动后内存约 40MB。开源也提供安装包，12 条回复在聊轻量 review 工具该不该独立成品类。

> 为了看 diff 装几个 G 的 IDE，本末倒置。

来源：V2EX Share · [https://www.v2ex.com/t/1257203](https://www.v2ex.com/t/1257203) · `dev_7e81ebc4`

## 10. Codex RC Bridge：手机用个人号，电脑用工作号

Codex 官方远控要求手机和电脑登录同一个 ChatGPT 账号，手机用个人号、电脑用工作号就断线了。作者写了 Codex RC Bridge：两端分别授权配对后，可以在手机上的官方 ChatGPT App 里控制另一个账号下的 Codex，手机不用切号，一台手机也能连多台电脑。Mac 可直接装，也能用 Docker 自建。代价是桥接器要经手凭据，等于把账号安全交给一个自建服务。

> 为了不切号，把账号交给了桥接器。

来源：V2EX Share · [https://www.v2ex.com/t/1257160](https://www.v2ex.com/t/1257160) · `dev_691db7fe`

## 11. LibrioX：书库是一个文件夹，笔记自动变 Markdown

LibrioX 是个本地优先的电子书阅读器，理念是 File Over App：书库就是电脑上的一个文件夹，子文件夹即分类，支持 EPUB、PDF、MOBI、AZW3、FB2；每本做过笔记的书旁边自动生成同名 .md，能直接放进 Obsidian。选中文字就能问 AI、翻译，回答带原文出处；同步走自己的 S3 或 WebDAV。短板：iOS 还在内测、.md 单向写出、只支持无 DRM 文件。

> 笔记锁在阅读器里，等于没写过。

来源：V2EX Share · [https://www.v2ex.com/t/1257220](https://www.v2ex.com/t/1257220) · `dev_eed5a534`

## 12. .NET 10 和 11 同一天停止支持，那还不如选新的

.NET 10（LTS）和 .NET 11（STS）的支持截止日是同一天：2028 年 11 月 14 日。既然终点一样，晚一年出生的 .NET 11 反而更值得作为迁移目标。作者梳理了双轨制来历：2019 年定下每年 11 月发一版、偶数 LTS 奇数 STS；2025 年 9 月起 STS 从 18 个月延长到 24 个月，于是出现同归于尽的排布。文章也写了什么情况下仍该留在 .NET 10。

> 同一个死期，当然选年轻的那个。

来源：Dev.to · [https://dev.to/georgekobaidze/net-11-unpacked-why-im-recommending-sts-this-time-lnj](https://dev.to/georgekobaidze/net-11-unpacked-why-im-recommending-sts-this-time-lnj) · `dev_13681792`

## 13. agent 能抓网页却搜不了，问题不在模型

作者在 DeepSeek Harness 里遇到怪事：web_fetch 一直能用，web_search 却永远搜不出结果。排查后发现差别不在 agent 框架，而在两个工具背后的服务——一个直接抓页面，一个依赖搜索后端。他把这归结成一个常见误判：agent 说「我做不到」，往往不是模型能力问题，而是某个工具的依赖悄悄挂了。修法不是换模型，是给每个工具加一条独立探活。

> agent 说做不到，多半是工具先死了。

来源：Dev.to · [https://dev.to/build996/my-agent-could-fetch-a-url-but-could-not-search-for-one-ddg](https://dev.to/build996/my-agent-could-fetch-a-url-but-could-not-search-for-one-ddg) · `dev_32bc3b78`

## 14. AI 审了我自己写的插件，挑出 58 个问题

作者的插件测试 170 个全绿、双端类型检查 0 错误、发布门禁 19 项全过，然后 npm publish 报 403——版本号还是 rc.10。他让 AI 做了一次只读全面审查，六维度四路并行、每条须带路径和行号，挑出 58 个问题，3 个阻断级全在发布链路上：CI 因 lockfile 停在半年前而第一步就挂、npm publish 少了 --tag、latest 标签停在两个月前。

> 测试全绿，发布链路断了两个月。

来源：博客园 Cnblogs · [https://www.cnblogs.com/Y9931666/p/23672547](https://www.cnblogs.com/Y9931666/p/23672547) · `dev_c29b91aa`

## 15. 让 Codex 自己去观测云查报错

作者把「出问题先翻日志、再复制一大段给 AI」这一步也省了：给 Codex 接上观测云官方的 OWL MCP，只报文档编号、批次号、来源名和时间范围，让它自己去查运行日志。第一次不给入口，Codex 老实回答「无法确定失败阶段」；接上 MCP 后它能自己翻到具体异常，还能对比同批成功与失败的记录。关键细节是查询 Key 只读、任务范围写死，采集 Token 和查询权限是两回事。

> 能自己查日志的 agent，才配叫同事。

来源：博客园 Cnblogs · [https://www.cnblogs.com/guoxiaoyu/p/23673383](https://www.cnblogs.com/guoxiaoyu/p/23673383) · `dev_575cab6a`
