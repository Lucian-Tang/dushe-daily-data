# 🛠️ 开发者日报 | 2026-09-14 (Phase B - 补充精选)

## 1. Show HN：开源版 Modal —— 自托管 GPU 推理控制平面 beta9

beta9 是一个开源的 GPU 推理与任务编排平台，被作者称为「Modal 的开源对标品」。它把控制平面公开出来，提供一套高度优化的图元：GPU 推理、沙箱运行、任务调度等，让团队可以在自己的 Kubernetes 集群或裸机上跑 agent 与无服务器推理，而不必把算力账单一并交给闭源托管平台。适合想自建 AI infra、又不想从零造轮子的团队。

> 不想给托管平台交保护费，就把控制平面搬回家。

来源: HN Show HN | https://github.com/beam-cloud/beta9/

## 2. Show HN：Hop —— 让会话跟着项目走，而不只是 tmux

作者做 Hop 的起因很朴素：每个项目都会攒下一堆浏览器标签，而 tmux 的「会话」却只能装终端。尤其在编码 agent 流行之后，一个项目同时牵连着编辑器、agent 会话、本地服务与文档，散在多个窗口里根本管不过来。Hop 想把「项目会话说」从终端扩展到与之相关的所有东西，让上下文按项目聚合、随手切回。

> tmux 只管终端，可项目早就不止终端了。

来源: HN Show HN | https://github.com/artemave/hop

## 3. Show HN：给 Proton 全家桶做了个命令行工具，一个静态二进制

作者为 Proton 做了一套命令行工具，覆盖 Mail、Drive、Calendar、Pass 和 Contacts。Proton 的网页界面功能齐全，却一直没有统一的 CLI，于是他用一个静态二进制把五大服务收进终端，Linux、macOS、Windows 通用。适合重度依赖 Proton、又想在脚本和自动化里直接调用邮箱、日历、密码库的开发者。

> 网页点得手酸，不如一行命令把 Proton 全家桶叫来。

来源: HN Show HN | https://github.com/roman-16/proton-cli

## 4. Show HN：ThreadShelf —— 把导不出来的 AI 对话攒成可搜索的收藏架

作者的 AI 对话散落在 OpenRouter、AI Studio、LM Studio 各处，既没法好好搜索，也难复用，OpenRouter 甚至没有像样的批量导出。于是他做了 ThreadShelf：把这些「导不出来」的聊天记录集中收纳、检索和再利用，做成一座可按主题翻找的对话书架。适合长期用多个模型、又舍不得丢掉历史上下文的人。

> AI 聊完就散，ThreadShelf 把它们捡回来上架。

来源: HN Show HN | https://github.com/ChrystianSchutz/ThreadShelf

## 5. 别再一次性脚本了：我把零散需求做成了一个 Python CLI 工具箱

作者发现，每次让 AI 助手处理小任务，它都会顺手写一个临时脚本：转图片、压 PDF、CSV 转 Excel……脚本能用，但用完就丢，下次还得从头再来。于是他改变思路，把这些零碎需求沉淀成一个统一的 Python CLI 工具箱，命令化、可复用、能持续维护，而不是让一堆一次性脚本散落在硬盘里，越攒越乱。

> AI 写的一次性脚本，本质是另一种技术债。

来源: Dev.to | https://dev.to/mehakb7/i-built-a-python-cli-toolbox-instead-of-writing-one-off-scripts-2f7i

## 6. 发票改错该「原地编辑」还是「记一笔新单据」？

作者用 TypeScript/Express 搭了一套发票管理 API，围绕「受控生命周期」设计：草稿可随意编辑，已定稿的发票则不允许直接改动。核心取舍在于——更正不再表现为对原单据的覆盖，而是生成一份新的更正文档，把每次修改都留成可追溯的记录。这种建模方式让审计、对账和追责都有据可查，适合对合规性敏感的业务系统。

> 改发票不覆盖原单，账才追得回来。

来源: Dev.to | https://dev.to/uttrai262005/modeling-invoice-corrections-as-new-documents-not-edits-40el

## 7. 解析器报错了，可那个文件根本没坏

一个从文档里抽取需求表的构建步骤，每次运行都抛出 FAIL_MAP reason=parse。字面上看只有两种可能：要么文档格式确实坏了，要么解析器错了。作者顺着这条线索复盘了整个排查过程——最后发现问题既不在数据、也不在解析逻辑本身，而是藏在更上游的地方。文章示范了遇到「不可能的错误」时，怎样一步步缩小范围，而不是急着改解析器。

> 报错说是文件坏了，真相是代码先撒了谎。

来源: Dev.to | https://dev.to/mahirhir/my-parser-reported-a-parse-error-on-a-file-that-was-never-malformed-3agi

## 8. 把 DeepSeek Harness 从源码跑成桌面应用：WinSW 封装实战

DeepSeek Harness（DSH）是 DeepSeek 推出的 AI 编程助手，用 dsh web 就能在浏览器里访问它的 Web UI。但源码编译版没有现成桌面客户端，每次都得手动敲命令启动，终端一关服务就断。作者完整记录了用 WinSW 把源码编译版封装成常驻系统服务的过程，并扩展到桌面应用等多形态使用方式，让 DSH 从「临时跑一下」变成「开机就在」的生产级工具。

> 好工具不该靠一个不能关的终端窗口续命。

来源: 博客园 Cnblogs | https://www.cnblogs.com/znlgis/p/22954862

## 9. 软件开发到底有多难？别被「拷打 AI 就能出软件」骗了

作者科班出身、也写过几个小项目，他观察到：AI 席卷之后，仿佛进入了「只要拷打 AI 就能生成完整软件」的时代，这种「随手就能做出精美小程序」的错觉，让很多人严重低估了软件开发的难度。他提醒，程序里没有哪个字节的流动是理所当然的，网页上也没有哪个像素是凭空出现的——真正的工程复杂度，藏在看不见的边界条件与权衡里。

> AI 让写代码变简单，也让低估难度更危险。

来源: 博客园 Cnblogs | https://www.cnblogs.com/Reisentyan/p/22955612

## 10. Etherfi AtomicQueue 攻击复盘：订单校验没实现，用户授权被滥用

20260911，Etherfi AtomicQueue 合约遭攻击，一名用户 14.44 枚 liquidETH（约 3.8 万美元）被盗。根因是订单检查逻辑被绕过：本该在成交前验证的条件没有真正实现，导致用户的代币授权被攻击者盗用。作者附上攻击交易与链上分析，复盘了漏洞的触发路径，提醒 DeFi 协议「写了校验」和「校验真的生效」之间，可能隔着一次真金白银的损失。

> 校验逻辑写了不等于生效，链上只认结果。

来源: 博客园 Cnblogs | https://www.cnblogs.com/ACaiGarden/p/22949179

## 11. 自荐开源：一台 N100 小主机，囊括内网穿透、科学上网、AI 网关与服务发现

作者把自己作为程序员的老痛点摊开：跨公网访问家里的机器、稳定的科学访问、统一的 AI 网关、多台机器之间互相发现。单拎出来每一项都有现成轮子，可凑在一起就是一堆配置，换台机器还得再来一遍。于是他做了个「开发中枢」：一台常亮的 Linux 盒子跑 hub，各服务器装 agent，其他电脑装 client，把这些能力收进一套面板里统一管。

> 四个轮子各自都挺好，凑一起就是一坨配置。

来源: V2EX Share | https://www.v2ex.com/t/1241622

## 12. SerenaDesktop：让 ChatGPT 负责思考、Codex 负责干活

作者的 20x Codex 额度总不够用，于是想出让 ChatGPT 出思路、写好提示词，再由 Codex 动手执行。但很快撞上问题：Codex 本地的文档和代码，ChatGPT 看不到，时间一长两边上下文就跑偏，提示词也越来越离谱。他由此开发 SerenaDesktop，试图把「思考」与「执行」两个模型接起来，让分工真正闭环，而不是靠人肉复制粘贴。

> 让 ChatGPT 想、Codex 干，中间那根线才是难点。

来源: V2EX Share | https://www.v2ex.com/t/1241573

## 13. 开源自荐：Flotilla-MCP，一个跨多台服务器的 MCP 系统

作者开源了 flotilla-mcp，目标是管理分布在多台服务器上的 MCP（模型上下文协议）服务。目前是 1.0 版本，作者坦言加服务器还很麻烦，属于「先沉淀一下」的阶段；后续 2.0 计划做 Web 面板和统一 gateway。帖子里直接向手头攒了十几二十台机器的折腾党征集体验与意见，适合正在被一堆 MCP 端点分散管理折磨的人围观。

> MCP 一多，端点管理就成了新的运维负担。

来源: V2EX Share | https://www.v2ex.com/t/1241481
