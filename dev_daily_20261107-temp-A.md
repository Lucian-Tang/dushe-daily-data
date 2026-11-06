# 开发者日报 A 轨素材 · 2026-11-07

> 共 15 条 | HN 5 · GitHub 2 · V2EX 4 · 博客园 2 · Dev.to 2

## 1. Gemini Omni 1.2 Flash 发布：15 秒视频，价格再降 30%

Google 把 Omni 1.2 Flash 推到正式可用：原生支持最长 15 秒视频，可按 1 秒步长指定 3–15 秒；支持多轮对话式改片，改一个细节不用整段重生成；角色、商品、风格参考图加上最长 3 秒的运动片段和音频提示，全程保持一致性。价格比 1.1 降 30%，720p 每秒 0.07 美元，可以先出 360p/720p 草稿，再升到 1080p/4K。

> 视频模型开始按秒卖，创意按帧贬值。

来源：HN Front Page · [https://blog.google/innovation-and-ai/technology/developers-tools/introducing-gemini-omni-1-2-flash/](https://blog.google/innovation-and-ai/technology/developers-tools/introducing-gemini-omni-1-2-flash/) · `dev_7048d57e`

## 2. 荷兰 ASN 银行封杀非 Google 认证 Android，GrapheneOS 用户被挡在门外

ASN 银行 App 在激活 iDEAL/Wero 时要求通过 Google Play Integrity 认证，非 Google 认证系统（含 GrapheneOS）直接无法使用。开发者拆解发现，服务端只信 Google 的两条根证书链，连 App 发布审核也依赖 Play 判定。评论区的评价很刺：不是安全做不到，是“Google 说没问题”比自建密钥白名单更好向审计交代。HN 487 分。

> 银行把身份验证外包给 Google，还叫安全。

来源：HN Front Page · [https://github.com/PrivSec-dev/banking-apps-compat-report/issues/105](https://github.com/PrivSec-dev/banking-apps-compat-report/issues/105) · `dev_63bcc082`

## 3. 有人把 Blender 的 UI 抽出来做成跨语言框架，号称比 GPUI 快一倍

BUI 把 Blender 的 GPU 加速界面层从原代码库解耦，支持 Rust、Python、JS、React、C/C++。它沿用 Blender 的实例化控件绘制：空闲 UI 不占 CPU，悬停只重绘碰到的那一个控件，GPU 渲染器可选。基准里每帧 CPU 比 gpui-fast 低 2–4 倍、内存更少、首帧约 5ms。HN 494 分。

> UI 框架卷到最后，开始比谁更像 Blender。

来源：HN Front Page · [https://github.com/ppmpreetham/BUI](https://github.com/ppmpreetham/BUI) · `dev_06ff008b`

## 4. 大学图书馆被 AI 爬虫围攻：一天 1.1 万次芬兰音乐检索

CBC 报道，多所大学图书馆的在线资源正被数据抓取机器人持续冲击，整批馆藏被打到下线，学生、研究者和公众都无法访问。圣何塞州立大学的管理员形容机器人“就在互联网上，朝我们狂轰滥炸”；有学校一天之内收到超过 1.1 万次关于芬兰音乐的检索。AI 公司为训练大模型四处找内容，图书馆成了最软的靶子。

> 训练数据不够，就去把图书馆爬断线。

来源：HN Front Page · [https://www.cbc.ca/news/world/university-libraries-ai-data-scraping-bots-9.7408287](https://www.cbc.ca/news/world/university-libraries-ai-data-scraping-bots-9.7408287) · `dev_cf76924c`

## 5. Zalando 开源 Agentic Identity Broker：给 AI Agent 发可撤销的 OAuth 委托

Show HN 项目 AIB 是 Zalando 孵化器里的 MIT 许可 OAuth2 broker，让用户把受限权限委托给 AI Agent，而不是把长期 token 直接塞进 prompt。它把授权、同意和撤销收拢到一处，Agent 每次调用都走可审计的委托链。作者在帖子里说，做这个是因为 Agent 拿全权凭证的方式已经没法向安全团队交代。GitHub 38 星，262 次提交。

> Agent 拿万能钥匙的时代，该结束了。

来源：HN Front Page · [https://github.com/zalando-incubator/agentic-identity-broker](https://github.com/zalando-incubator/agentic-identity-broker) · `dev_8a5e79c9`

## 6. Zed 冲上 GitHub 日榜：9.3 万星的 Rust 编辑器还在加速

Zed 是 Atom 和 Tree-sitter 作者做的多人协作代码编辑器，主打“thought 级速度”，原生 Rust + GPU 渲染。今天它出现在 GitHub Trending 日榜，仓库约 9.3 万星。在 VS Code 插件化路线和 AI 编辑器混战之间，Zed 的赌注是延迟和协作体验——把编辑器的基本盘重新做一遍，而不是在 Electron 上叠功能。

> 编辑器赛道打了十年，最后拼的还是毫秒。

来源：GitHub Trending Daily · [https://github.com/zed-industries/zed](https://github.com/zed-industries/zed) · `dev_40146045`

## 7. NVIDIA 开源 auto-ontology：给 Agent 搭一层可查询的语义图谱

Auto Ontology 是 NVIDIA 开源的 Python 框架，用语义图谱给数据建推理层：把实体、关系抽成 ontology，让模型生成确定性的查询，而不是每次凭上下文瞎猜。项目定位是提升检索质量、让 Agent 的推理过程可解释，今天在 GitHub Trending 日榜上约 8600 星。对需要跨多数据源做 RAG 的团队，这种“先建图再问”的路线值得看一眼。

> RAG 不够用，是因为连张图都没有。

来源：GitHub Trending Daily · [https://github.com/NVIDIA/auto-ontology](https://github.com/NVIDIA/auto-ontology) · `dev_758fe142`

## 8. 5 MB 的原生 API 客户端 CurlGo：不偷偷给编辑器装插件

作者起因是 Postman 12.33.4 被曝在后台给 Codex 和 Claude Code 装插件、改配置，而且又慢又卡，于是做了 macOS 原生 API 客户端 CurlGo，安装包 4.97 MB。它支持 HTTP、SSE、WebSocket，定位是面向 Agent 的轻量调试工具，不自动装插件、不改别人的配置。对只想发个请求的人来说，这个体积本身就是卖点。

> 一个 API 客户端，先学会别乱装东西。

来源：V2EX Share · [https://www.v2ex.com/t/1254853](https://www.v2ex.com/t/1254853) · `dev_36a3022e`

## 9. 个人站点最省钱的部署组合：Vercel + Cloudflare

V2EX 帖子讨论纯前端站点的低成本部署：对后端依赖不强的工具站、内容站，可以直接静态化，Vercel 负责构建和托管，Cloudflare 负责解析和加速，一年只剩域名续费。需要自动更新数据时，再挂一层定时任务或 Serverless 接口，把数据写成 JSON 让前端拉。发帖人认为这套方案特别适合个人做出海站点，先把成本压到接近零。

> 省钱省到最后，只剩域名在花钱。

来源：V2EX Tech · [https://www.v2ex.com/t/1252324](https://www.v2ex.com/t/1252324) · `dev_826ffc08`

## 10. 桌面 Markdown 编辑器全是网页套壳？他们用 C++/Qt 写了个原生的

作者认为 Typora、Obsidian、MarkText 基本都是网页内核或 Electron 套壳，启动慢、吃内存、大文件卡。Muffin 用 C++20 + Qt 6 纯原生实现，不捆 Chromium、不依赖 Node，换来更快的冷启动和更低内存；配合懒加载视口布局，大文档首屏也不用等整个文件解析完。代价是开发量大，作者说这是主动选难的路。

> 套壳套了十年，终于有人肯写原生。

来源：V2EX Share · [https://www.v2ex.com/t/1255035](https://www.v2ex.com/t/1255035) · `dev_d40ed2fe`

## 11. 开源 iPhone-control：在 Linux 上用 Rust 让 AI 操作真机

作者之前用 go-ios、pymobiledevice3、WDA 拼方案，每个都要单独装、单独签名，隧道还动不动断，于是用 Rust 重写。项目提供 15 个 MCP 工具，覆盖截图、点击、滑动、长按、输入中文、按实体键、开关 App、打开链接；能读界面元素，AI 可以直接说“点设置”而不用猜坐标。目标是让 Linux 上的 Agent 真正操作 iPhone，而不是靠模拟器。

> Agent 的手，终于伸进 iOS 了。

来源：V2EX Share · [https://www.v2ex.com/t/1255024](https://www.v2ex.com/t/1255024) · `dev_3c055a34`

## 12. CRC 字段神秘消失：一次指针强转引发的编译器删代码

嵌入式设备升级编译器后，写入 flash 的记录回读校验必失败，CRC 永远是 0xFFFF，其余字段全对。根因是把 uint8_t[] 缓冲区强转成结构体指针写入，违反 C 的有效类型规则，属于 UB；编译器据此认定结构体写和字节读是两个不相干对象，把 crc 赋值当死存储消除，CRC 计算也成了死代码。反汇编里那行确实没生成任何指令。修复方式是先构造头，再 memcpy 进输出缓冲。

> UB 不报错，它只是悄悄把你的代码删了。

来源：博客园 Cnblogs · [https://www.cnblogs.com/USTHzhanglu/p/23577592](https://www.cnblogs.com/USTHzhanglu/p/23577592) · `dev_0caa6b74`

## 13. MySQL 深分页为什么慢：别只会把 offset 换成游标

LIMIT 100000,10 会沿索引读 100010 行、丢掉前 10 万行；如果走二级索引，每一行还要回表拿完整数据，于是变成“无效扫描 + 无效回表”双重损耗。作者给出选型：C 端顺序翻页用游标分页，千万级表能从几秒压到几毫秒；需要跳页、筛选条件多的后台用延迟关联，子查询只取 id 再回表 10 次；百万以内别过度设计。上线两周后慢查询日志里再没出现这条 SQL。

> 分页慢不是数据库的错，是你让它白干。

来源：博客园 Cnblogs · [https://www.cnblogs.com/codigger/p/23569594](https://www.cnblogs.com/codigger/p/23569594) · `dev_408b12f1`

## 14. 机器人没叠好积木，该修规划器还是控制器？

Dev.to 文章借 Ai2 的 ToyBlocks 讲分层机器人的评测：高层 planner 选技能和目标，低层 controller 负责执行，任何一层都可以换成 oracle 参考实现，在仿真里做受控替换。作者用一个简单模型说明：规划成功率 0.9、执行成功率 0.6，和反过来的一组，总体成功率都是 0.54，只看总分根本分不清哪层弱。分别替换一层，才能看出瓶颈在哪。

> 只看总分，等于什么都没看。

来源：Dev.to · [https://dev.to/panditshivam/when-a-robot-misses-the-stack-which-model-needs-fixing-59i4](https://dev.to/panditshivam/when-a-robot-misses-the-stack-which-model-needs-fixing-59i4) · `dev_20010636`

## 15. Antigravity 上线 Remote Agents：关掉电脑，Agent 继续在云 VM 里干活

Google Antigravity v2.29 开始推送 Remote Agents：会话和工具跑在 Google 托管的隔离云 VM，关电脑换设备都不中断，可从桌面端、CLI 或网页接着聊。Agent 看不到本地磁盘，只能显式挂载 GitHub 仓库、Drive 文件或上传内容。它和 Remote Control 相反：后者 Agent 跑在你机器上。目前仅限 AI Pro/Ultra 订阅。

> 把权限交出去，把睡眠买回来。

来源：Dev.to · [https://dev.to/mayabrennan/googles-antigravity-remote-agents-mean-the-agent-works-while-you-sleep-heres-what-that-actually-n3h](https://dev.to/mayabrennan/googles-antigravity-remote-agents-mean-the-agent-works-while-you-sleep-heres-what-that-actually-n3h) · `dev_25402b5c`
