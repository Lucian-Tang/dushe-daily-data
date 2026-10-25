# 开发者日报 · A 轨素材 · 2026-10-26

共 15 条

## 1. Cerebras 把 3 万亿参数模型铺满晶圆：1000-2000 token/s

- **来源**：HN Front Page
- **链接**：https://www.cerebras.ai/blog/how-we-deploy-trillion-parameter-frontier-models-on-cerebras
- **UID**：dev_072f03cd

Cerebras 详解如何在 WSE-3T 晶圆上部署万亿参数模型：单片只有 44GB 片上内存，3 万亿参数的 Kimi K3 光权重就要数 TB，只能按层切分到多片晶圆，再配合 4-bit 量化与 256k 上下文做并发调度，最终跑到 1000-2000+ token/s。官方称该配置在 Terminal-Bench 2.1 上拿到 88.3%，逼近闭源旗舰。

> 毒舌：内存不够晶圆来凑，这才是真·堆硬件。

## 2. 尼康摄影大赛冠军被撤：科学家看出 AI 痕迹

- **来源**：HN Front Page
- **链接**：https://www.techspot.com/news/114171-nikon-photography-contest-winner-loses-title-after-scientists.html
- **UID**：dev_4db5c340

尼康第 16 届 Small World in Motion 显微摄影比赛冠军被撤销，原因是评审科学家发现画面里出现「凭空长出来的微观结构」等生成痕迹。作品此前已拿下最高奖，复核后头衔被收回。这已是今年又一起 AI 作品混进人类赛事的事件，评委的眼睛显然跟不上生成模型，最后还得靠专业科学家救场。

> 毒舌：评委看不出来，显微镜看出来了。

## 3. Dan Luu：我们该对软件更有野心一点

- **来源**：HN Front Page
- **链接**：https://danluu.com/ambitious/
- **UID**：dev_97ce664f

Dan Luu 借 Michael Malis 用 Rust 重写 Postgres（pgrust）说事：外界默认这类项目是「AI 生成的垃圾」，但 Malis 的测试严谨到反过来挖出了 Postgres 的数值、JSONPath、pgcrypto 等多个真实 bug。他的观点是，哪怕 pgrust 最终失败，这种做难而正确的事的尝试也会给生态留下长期价值，而不是又一批 CRUD。

> 毒舌：别人卷 CRUD，他卷数据库内核，差距这么来的。

## 4. Farol：给 PR 画一张风险地图，专治闭眼点合并

- **来源**：HN Front Page
- **链接**：https://github.com/winnin/farol
- **UID**：dev_0d8d0a4f

开源 CLI 兼 GitHub Action，在 AI 代码审查之后再补一层：标出本次 PR 里风险最高的文件、它们能触达哪些模块、diff 覆盖率以及接口契约变化，让审批者知道点下 Merge 到底在赌什么。作者把它定位成 AI review 之后的第二道关，适合改动面大、评审人又不熟代码的场景。TypeScript 编写，目前 78 星，很早期。

> 毒舌：AI 审完你再审，锅总得有人背。

## 5. TradingAgents：让一群 AI 分工炒股，11.4 万星

- **来源**：GitHub Trending Daily
- **链接**：https://github.com/TauricResearch/TradingAgents
- **UID**：dev_6f30af7b

TauricResearch 开源的金融交易框架，把投研流程拆成基本面、情绪、技术面、多空研究员、交易员和风控等多个 LLM 角色，让它们互相辩论后再出决策，而不是一个大模型拍脑袋。Python 实现，可接不同模型与行情数据源，GitHub 已 11.4 万星，是多智能体落地里最出圈的案例之一。

> 毒舌：一群 AI 开会炒股，亏了都不知道骂谁。

## 6. Impeccable：给 AI 编程 Agent 补一节审美课，8.7 万星

- **来源**：GitHub Trending Daily
- **链接**：https://github.com/pbakaus/impeccable
- **UID**：dev_9fb0f0ea

面向 AI 编程 Agent 的设计语言：1 个 skill、24 条命令、62 条确定性检测规则，专治 AI 生成前端的通病——全是 Inter 字体、紫蓝渐变、卡片套卡片、彩底灰字、每个标题上面一块圆角图标。装好后用 /impeccable 调 polish、audit、critique 等命令，确定性规则不调模型、不要 API Key，还能在浏览器里实时迭代。Rust 实现。

> 毒舌：AI 审美的尽头，是同一套 SaaS 模板。

## 7. Coolify：自托管的 Vercel 替代品，6.4 万星

- **来源**：GitHub Trending Daily
- **链接**：https://github.com/coollabsio/coolify
- **UID**：dev_6a25c5f3

开源 PaaS，装在自己的服务器上就能获得类似 Vercel、Heroku、Netlify 的体验：Git 推送自动部署、静态站点、数据库、全栈应用，外加 360 多个一键服务模板。PHP 编写，支持多服务器编排与自动 HTTPS。对预算敏感又想保住数据主权的团队，它是「Vercel 账单太贵」之后最常被提到的去处。

> 毒舌：Vercel 账单吓人？自己买台服务器呗。

## 8. JetBrains 也做 Vibe Coding IDE：thinkrail 开源

- **来源**：GitHub Trending Daily
- **链接**：https://github.com/JetBrains/thinkrail
- **UID**：dev_6a08f508

JetBrains 放出的轻量 IDE，主打围绕你的工作方式自我定制的 vibe coding：把 AI 对话、代码编辑和项目结构放进一个界面，减少在终端、编辑器和聊天窗之间来回切。TypeScript 实现，开源可改。相比 Cursor 那类重客户端，它更像把 IDE 拆小、让 Agent 主导流程的一次尝试，目前 1200 多星，还在早期。

> 毒舌：IDE 厂商终于发现，用户不想开三个窗口。

## 9. ESP32 当手：网页 Harness 全自动操作 iPhone 点外卖

- **来源**：V2EX Share
- **链接**：https://www.v2ex.com/t/1251717
- **UID**：dev_712917a2

作者用 Safari 里跑的网页 Harness 读取手机屏幕、调用模型决策，再让 ESP32 模拟蓝牙键鼠去点 iPhone，全程不接线、不装 App，手机和开发板连同一个 Wi-Fi 即可。支持自选模型，也能把常用操作写成可复用技能，比如自动点外卖。门槛是需要 iOS/iPadOS 27 以上，等于用几十块钱的开发板绕过了 iOS 的自动化封锁。

> 毒舌：苹果不给的自动化，一块开发板给了。

## 10. 用 Agent 写一下午代码，为什么反而更累？

- **来源**：V2EX Share
- **链接**：https://www.v2ex.com/t/1251606
- **UID**：dev_c69cb07e

作者的体验很典型：Coding Agent 写了一下午，人却精疲力尽，产出还不显著。他归因于大量重复的细节习惯要反复交代，比如要求 AI 在独立 worktree 和分支上开发、按固定流程提交。为此他做了开源 AI 助手 Pot，把这些口头规矩固化成可复用配置，省掉每轮沟通成本。结论挺扎心：累的不是写代码，是当 AI 的项目经理。

> 毒舌：代码是 AI 写的，班还得你来加。

## 11. Reelay：盯 TG 频道自动转存 115，追剧全自动

- **来源**：V2EX Share
- **链接**：https://www.v2ex.com/t/1251604
- **UID**：dev_9769b242

作者追剧的原流程是：看到资源、复制链接、开 115 转存、手动改名挪目录、等 Emby 刮削，还得天天盯更新。Reelay 用你自己的 Telegram 账号盯指定频道或 Bot，新消息进来后由 AI 识别片名与集数，自动转存 115、按规则命名归档，再交给 Emby 刮削，把整条链路串成无人值守。已开源，适合自建媒体库的重度用户。

> 毒舌：追剧自动化到这份上，比上班还卷。

## 12. Later：截图不用整理，开源视觉模型自动变待办

- **来源**：Dev.to
- **链接**：https://dev.to/phoenix1808/later-keep-screenshotting-an-open-weight-model-turns-your-screenshots-into-one-tap-actions-igi
- **UID**：dev_a4a1f23b

安卓应用 Later 抓住一个真实痛点：相册里全是「以后再看」的截图，然后就没有以后了。它在后台用开源视觉模型读每张新截图，直接转成对应动作——活动海报变日历事件、电费单变缴费提醒、周一前交表变待办、咖啡馆变地图链接，银行验证码则直接跳过不存。晚上 8 点一条通知汇总当天 12 张截图，一键处理。

> 毒舌：截图一时爽，整理火葬场，现在 AI 替你烧。

## 13. HyCanvas 从 ELv2 换到 AGPL：一次许可证取舍

- **来源**：Dev.to
- **链接**：https://dev.to/dev-sahoo/we-relicensed-hycanvas-from-elv2-to-agpl-heres-why-iek
- **UID**：dev_f954a92b

HyCanvas 是浏览器里的设计工具，对标 Canva，单个 Go 二进制内嵌前端，只依赖 PostgreSQL。作者解释 v0.3.17 起许可证从 Elastic License 2.0 改为 AGPL-3.0-only：ELv2 限制太多、社区不认，AGPL 既保证自托管自由，又能防止云厂商直接拿去做托管服务卖钱。文章也谈了 CLA 和商业授权怎么安排。

> 毒舌：许可证选得好，云厂商一分钱薅不到。

## 14. 一个人 + AI，66 天从空目录到生产环境

- **来源**：博客园 Cnblogs
- **链接**：https://www.cnblogs.com/zhuxiaoxiao/p/23432906
- **UID**：dev_d46c31ae

作者 8 月 20 日建了个空目录和一份 PRD，10 月 25 日 P2P 内网穿透产品已上线成交，全程没手写一行业务代码。结果是 193 次提交、约 6.8 万行代码、995 项自动化测试、编译零警告，CI 还卡了覆盖率门槛。文章复盘了全自动编程的方法论：怎么拆任务、怎么让 AI 自查、怎么用生产日志回流驱动重构。

> 毒舌：六十六天六万八千行，手都没碰键盘。

## 15. 从审核员到监工：AI 正在重写评价体系

- **来源**：博客园 Cnblogs
- **链接**：https://www.cnblogs.com/Li-runqing/p/23432895/ai-overseer
- **UID**：dev_03ac7eb4

作者在程序员节活动后的复盘：五个月前他还在分享怎么给 AI 写全局规则，如今大部分提示词已不重要，身份从审核 AI 产物的审核员，变成只确认 AI 在干活的监工。他举了两个压力信号：OpenAI 用内部模型一次在 GitHub 发了 722 篇数学论文；PHP、Node、Java、Linux 同时爆高危漏洞，而 PHP 只有一名全职维护者。

> 毒舌：AI 产能过剩，人类注意力破产。
