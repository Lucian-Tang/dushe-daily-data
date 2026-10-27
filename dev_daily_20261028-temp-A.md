# 开发者日报 · A 轨素材 · 2026-10-28

共 14 条

## 1. Genie 4 发布：世界模型自带音效和对话

- **来源**：HN Front Page
- **链接**：https://deepmind.google/blog/genie-4-a-new-generation-of-world-simulation/
- **UID**：dev_068893c2

DeepMind 10 月 27 日发布 Genie 4：原生多模态实时世界模型，画面、环境音与人物语音一起生成，能用自然语言随时改天气、换机位、加人。Gemini Omni 负责真实世界的物理与外观，Gemini 3.8 Flash 在循环里拆解多步目标并核对。目前仅向 trusted testers 开放预览，之后才给 AI Ultra 订阅者在 Project Genie 试用。

> 毒舌：世界模型都会配音了，离骗过耳朵只差一步。

## 2. 法官认定 Anthropic 用盗版书训练 Claude

- **来源**：HN Front Page
- **链接**：https://stanforddaily.com/2026/10/27/professors-books-pirated-to-train-claude/
- **UID**：dev_aeb3a261

斯坦福校报报道：2026 年 5 月联邦法官 Alsup 认定 Anthropic 从 LibGen、PiLiMi 等影子图书馆下载盗版书训练 Claude，涉及十余位斯坦福教授。15 亿美元和解覆盖近 50 万部作品，约每部 3000 美元。Tobias Wolff 等 28 位作者嫌少，另案索赔每部最高 15 万美元。合法购书训练仍算合理使用。

> 毒舌：先盗版后赔钱，赔完还顺手把合理使用定了。

## 3. CPython 实验性 JIT 即将被移除

- **来源**：HN Front Page
- **链接**：https://lwn.net/SubscriberLink/1102102/0c00e4d550f25f8c/
- **UID**：dev_79198fe3

LWN 报道：CPython 3.13 的实验性 JIT 即将从主分支移除。指导委员会 6 月要求交 standards-track PEP，说明维护承诺与性能指标，否则删代码。作者 7 月提 PEP 836，委员会列十点质疑：平台一致性、用户可见差异、内存安全，以及兼容性测试排到 2028 年太晚。10 月 19 日作者以没有带宽为由撤回，参考实现只留链接。

> 毒舌：「实验性」三个字，翻译过来就是不用负责。

## 4. 维基百科：AI 新条目占比降到 16%

- **来源**：HN Front Page
- **链接**：https://spectrum.ieee.org/wikipedia-wikiproject-ai-writing-cleanup
- **UID**：dev_b9bc96a2

WikiProject AI Cleanup 2023 年 12 月成立，发起人 Ellia Lebleu 说：当年靠「stands as a testament」这类套话就能识别，2025 年后要看三段式、否定平行句，以及五分钟写完五篇长文的行为。最麻烦是引用，AI 找真来源却讲错内容极普遍。Pangram 估算，2025 年底约 20% 新条目是 AI 生成，2026 年初降到 15–16%。

> 毒舌：用 AI 抓 AI，抓不抓得住全看谁进化快。

## 5. Roblox 悄悄拖走 145GB 模型，含成人内容

- **来源**：HN Front Page
- **链接**：https://open3dlab.com/news/roblox-downloaded-145-gb-of-models-from-our-sites/
- **UID**：dev_9b690068

Open3DLab 披露：10 月 15 至 16 日，UA 标 roblox.com 的爬虫从单一 AWS 地址发 26429 次请求，34 小时读完 18926 个项目页，下走 712 个项目的 1027 个文件共 145.5GB。其中 345 个项目、62.6GB 是成人内容，423 个项目仅授权非商用。它取过 robots.txt 却不遵守。站方 18 日封禁并去信，Roblox 未回复。

> 毒舌：连成人区都照单全收，这叫数据多样性。

## 6. superpowers：30 万星的 agent 方法论

- **来源**：GitHub Trending Daily
- **链接**：https://github.com/obra/superpowers
- **UID**：dev_488567a9

obra/superpowers 30.6 万星、2.7 万 fork，Shell 写的 MIT 项目，2025 年 10 月建仓。它不卖模型卖流程：先问清目标，把 spec 切成能读完的小段让你签字，再产出初级工程师也能照做的实现计划，最后用 subagent 逐任务开发与审查。README 列了近 20 种 harness 装法。

> 毒舌：方法论卖到 30 万星，代码一行没多写。

## 7. 港大 DeepTutor：把辅导做成终身 agent

- **来源**：GitHub Trending Daily
- **链接**：https://github.com/HKUDS/DeepTutor
- **UID**：dev_2347ddd6

港大数据智能实验室的 DeepTutor 4.54 万星，Python、Apache-2.0，2025 年 12 月建仓。聊天、出题、研究、可视化、解题、课程、沉浸阅读共用一套运行时；知识库可挂 LlamaIndex、PageIndex、GraphRAG、LightRAG；记忆分 L1 痕迹、L2 摘要、L3 综合三层。最新版 v1.6.15 于 10 月 19 日发布。

> 毒舌：终身辅导听着感人，先看它记不记得住你。

## 8. openbot：本地桌面里养一队 AI 同事

- **来源**：GitHub Trending Daily
- **链接**：https://github.com/nightly-labs/openbot
- **UID**：dev_a39c4e1f

nightly-labs/openbot 2122 星，TypeScript + Electron，2026 年 8 月建仓。每个 agent 独占 workspace 与会话，可接 Codex、Claude Code、Grok CLI、Cursor 等后端，配 FIFO 队列、文件互传与内嵌浏览器。作者警告仍是开发预览，agent 默认 danger-full-access 且从不请求批准。

> 毒舌：默认不请求批准，出了事也别找它批准。

## 9. QuireKit 开源：浏览器里真分页的编辑器

- **来源**：V2EX Share
- **链接**：https://www.v2ex.com/t/1252080
- **UID**：dev_ef8c62eb

V2EX 作者开源 QuireKit：保留 ProseMirror 的文档、事务与协同语义，把视图层换成自研排版引擎，分页、断行、光标全部自己算，用 Canvas / SVG 绘制。首日发了 125 个 npm 包（0.0.1-alpha），提供类 Word 的 Classic、块编辑器与 Markdown 编辑器，支持表格跨页、页眉页脚、DOCX 往返。核心 MIT，排版引擎为 AGPL。

> 毒舌：分页这两个字，做起来才知道 Word 有多难抄。

## 10. 把全球 2 万个 AI 岗位画成一张星图

- **来源**：V2EX Share
- **链接**：https://www.v2ex.com/t/1252306
- **UID**：dev_6e265589

V2EX 作者把全球 AI 岗位铺成星图：一个点就是一个岗位，按研究、AI 工程、基础设施、硬件、数据、产品商业、政策合规分旋臂，可切地区、级别、方向、时间。数据来自 Greenhouse、Lever、Ashby 等招聘页，加上领英与 X 的招聘帖，现覆盖 1187 家公司、2.1 万个岗位；招聘页 6 小时更新一次。国内公司禁爬，国内岗位几乎没有。

> 毒舌：盯着星图找饭碗，比刷招聘 App 有仪式感。

## 11. SoMark 开源 OXR：1.3B 三榜第一

- **来源**：V2EX Share
- **链接**：https://www.v2ex.com/t/1252155
- **UID**：dev_fea3fbba

SoMark 开源 OXR：1.3B 模型把 PDF 与图片转成 Markdown / JSON，支持表格、公式、代码块等 13 类元素并带版面坐标。三项基准第一：OmniDocBench 97.18、olmOCR-Bench 87.84、DocParsingBench 87.76；单卡 RTX PRO 6000 解析 100 页约 101 秒，21 个开源模型里最快。免费 API 不用 Key。

> 毒舌：1.3B 打赢一堆大模型，参数真不是万能。

## 12. Gemkit：Web Components 的 SSR 框架

- **来源**：V2EX Share
- **链接**：https://www.v2ex.com/t/1252367
- **UID**：dev_13ac69fa

mantou132 给自研 Web Components 库 Gem 补上 SSR：先用 jsdom 跑通 Declarative Shadow DOM 水合，再改成字符串渲染。RealWorld 实测首屏 JS 25.9KB，SvelteKit 44KB、Nuxt 85.8KB、Next 103.5KB；SSR 吞吐 1382 req/s，SvelteKit 1437。仍是 0.x 项目。

> 毒舌：26KB 首屏很香，0.x 版本很要命。

## 13. 删掉 .env 不算完，密钥还在历史里

- **来源**：Dev.to
- **链接**：https://dev.to/anas_sheikh_2/you-deleted-the-env-file-from-git-your-secrets-are-still-public-4ki6
- **UID**：dev_feb6b7f4

git rm .env 只是新增一条「文件不存在」的记录，旧提交里的明文还在，git log --all --full-history 一查便知，fork、别人的 clone、托管平台缓存也都留着。正确顺序是先轮换数据库密码、API key、JWT 签名密钥，再谈清理历史。文章还点了 Next.js 的坑：NEXT_PUBLIC_ 前缀的变量会被打进前端 bundle。

> 毒舌：删文件只要一秒，轮换密钥才是真活儿。

## 14. 监控全绿，仓库少了 4812 条订单

- **来源**：Dev.to
- **链接**：https://dev.to/pipelinewhiteboard/the-silent-cdc-bug-data-loss-with-no-errors-5ahh
- **UID**：dev_a143ae8a

CDC 系列第三篇列了四种零报错丢数据：故障切换后重建 slot，窗口内事件永不解码，offset 校验默认关闭；表加进 include.list 却没进 publication；TOAST 占位符 __debezium_unavailable_value 被 sink 写回；errors.tolerance=all 又没配 DLQ。订单少 4812 条时面板全绿。

> 毒舌：仪表盘全绿的时候，最该去数一遍订单。
