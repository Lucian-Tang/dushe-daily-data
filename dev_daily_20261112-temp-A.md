# 开发者日报 A 轨素材 · 2026-11-12

> 共 15 条 | HN Front Page 4 · GitHub Trending Daily 3 · V2EX Share 3 · Dev.to 2 · 博客园 Cnblogs 3

## 1. 48 个 AI Agent 翻 1200 平方公里雷达图，找出玛雅遗址

作者在秘鲁旅行时起念，让几个大模型出主意，最后选 NASA 公开的 LiDAR：把约 1200 平方公里丛林条带转成图，48 个 Agent 像耐心的考古学家逐张找金字塔、平台和广场，滤掉自然山丘与天坑，全程没用专用模型。不到 72 小时，从念头走到墨西哥政府的正式回复。11 月 11 日作者更新：遗址其实已在 2025 年论文里测绘过，Agent 读文献时漏了，所以是重新发现，不是首次发现。

> 48 个 Agent 会看图，就是不肯先查文献。

来源：HN Front Page · [https://pietromiotti.com/latest/maya-site/](https://pietromiotti.com/latest/maya-site/) · `dev_515592b3`

## 2. 把 SSH 私钥塞进 Secure Enclave：Touch ID 签一次，密钥永不落地

作者嫌 ~/.ssh 的私钥只靠文件权限保护，一篇恶意脚本就能全拷走，于是试原生方案：macOS 自 Sequoia 起支持 Secure Enclave 背书的 SSH 密钥，用 sc_auth 生成不可导出、每次签名都要 Touch ID 的 P-256 密钥，磁盘上只剩一个引用。他也列了 Secretive、YubiKey、1Password 几条路，最后嫌流程太丑没自用，但方案确实能跑。

> 私钥存在芯片里，拷贝都无从下手。

来源：HN Front Page · [https://gatezh.com/posts/macos-secure-enclave-ssh-keys/](https://gatezh.com/posts/macos-secure-enclave-ssh-keys/) · `dev_82a20f2a`

## 3. 电压毛刺打穿 GA100：8GB 矿卡 CMP 170HX 变成 A100-80G

作者在 GA100 核心上找到电压故障注入点，能烧任意熔丝，于是把 CMP 170HX 8GB 矿卡解锁成 81920 MiB 显存的「A100-80G」，还把屏蔽的 SM 全开，实测 FP16 吞吐约为零售 A100 的 1.18 倍——零售版锁在 108 个 SM 保良率。NVLink、PCIe Gen4、NVJPG、NVDEC、MIG 也能一并解锁，后三项他没逐一验证。

> 老黄按型号切菜，他直接把刀抢了。

来源：HN Front Page · [https://blog.kate.land/posts/using-voltage-glitching-to-unlock-the-a100/](https://blog.kate.land/posts/using-voltage-glitching-to-unlock-the-a100/) · `dev_0336410e`

## 4. Atuin 18.24 把 Agent 会话变成可跨机器搜索的历史

Atuin 作者发现自己机器上一半以上命令不是自己敲的，Agent 会话散落在笔记本、开发机、临时实例和德国一台便宜裸机上，既搜不到也留不住。Atuin 18.24 起推出 Threads：跨机器搜索 Agent 会话、在任意机器 resume，或把会话 fork 到另一个 harness——在开发机的 Claude Code 开工，回本地用 Codex 接着干，上下文不丢。

> shell 历史跟人走，Agent 记忆也得跟上。

来源：HN Front Page · [https://blog.atuin.sh/threads-agent-sessions/](https://blog.atuin.sh/threads-agent-sessions/) · `dev_7d2dff02`

## 5. OpenAI 开源 codex-security：扫漏洞、验证、出补丁一条链

OpenAI 把 Codex 的安全工作流开源成 CLI 和 SDK：可扫整库、指定路径或 Git 变更，深度扫描会重复标准扫描并去重；对候选问题做验证、生成补丁、复核已有修复，还能起草 SECURITY.md、保存威胁模型、按自定规则评严重度。支持 SARIF/JSON/CSV 导出、GitHub Action，以及 Linear、Jira 工单对接。

> 把安全审计做成流水线，比喊口号实在。

来源：GitHub Trending Daily · [https://github.com/openai/codex-security](https://github.com/openai/codex-security) · `dev_c7d55997`

## 6. shadcn/improve：贵模型写计划，便宜模型去执行

shadcn 的新 skill 只做一件事：让最强的模型审代码库、判断什么值得做、写成自包含的实施计划，再交给便宜模型执行，自己从不改代码——「计划就是产品」。命令有 full audit、quick、deep、security 和 execute，产物是纯 markdown，任何支持 Agent Skills 的工具都能接，也能发成 GitHub issue。

> 贵脑子做决策，便宜手做体力活。

来源：GitHub Trending Daily · [https://github.com/shadcn/improve](https://github.com/shadcn/improve) · `dev_f930a74b`

## 7. Chrome、Edge、Firefox、MDN 联手给编码 Agent 灌现代 Web 知识

GoogleChrome 开源 modern-web-guidance 的源仓库，内容是给编码 Agent 装的一套 Web 平台技能：把现代 API、最佳实践和浏览器兼容数据直接塞进 Agent，让它别再生成 jQuery 时代的老写法。仓库包含编写、校准、评测这些内容的代码和文档，由 Chrome、Edge、Firefox、MDN 团队与社区共同维护，还带一个评测看板。

> 三家浏览器一起教 AI，别再写十年前的前端。

来源：GitHub Trending Daily · [https://github.com/GoogleChrome/modern-web-guidance-src](https://github.com/GoogleChrome/modern-web-guidance-src) · `dev_91d311c7`

## 8. npx cc-clean：给 Claude Code 和 Codex 的会话瘦身

作者同时用 Claude 和 Codex，session 越攒越多，磁盘不够又不敢删，于是研究底层存储，做了 cc-clean。它清的是不影响 resume 的冗余：会话里的 Base64 内嵌图片、命令输出、Codex 加密推理状态和旧压缩快照、Claude 的 API 请求存档和 Hook 内容等 16 类。一条 npx cc-clean@latest 就能跑，原始记忆保留，随时可恢复。

> 上下文舍不得删，那就给它减个肥。

来源：V2EX Share · [https://www.v2ex.com/t/1256010](https://www.v2ex.com/t/1256010) · `dev_0adf48fc`

## 9. 读完一篇架构文，他花 10 天做出 7×24 在线的 Super-agent

作者 10 月 31 日读到 DeepSeek Harness 团队的《Super-agent 设计探索》，当晚决定落地，10 天后上线 SaaS：存算分离、云端 Loop 与重状态环境解耦、水平可扩展。动机很实在——同时开五六个项目、每个 3–5 个 session，自己就是「人肉 Router」，希望躺沙发上用语音派活。设计围绕连续、高效、主动、持久四个特征，Router 层做成双层架构。

> 人肉 Router 当久了，谁都想把自己外包。

来源：V2EX Share · [https://www.v2ex.com/t/1256266](https://www.v2ex.com/t/1256266) · `dev_14ffa9f4`

## 10. Casvisor：Apache-2.0 堡垒机，一个 Go 二进制装下四种协议

团队嫌 JumpServer 把 RDP 和数据库代理放进企业版，其他开源方案不是限制规模就是闭源，于是自己写 Casvisor：单个 Go 二进制支持 SSH、RDP（自研 gordp，支持 NLA、GFX、高 DPI）、VNC、Telnet 和 SSH 网关。权限按用户组乘资产配，命令正则拦截，四种协议全程录像，改权限立即踢掉在线会话。

> 开源堡垒机，最后都死在「企业版」三个字上。

来源：V2EX Share · [https://www.v2ex.com/t/1256259](https://www.v2ex.com/t/1256259) · `dev_64f06cb3`

## 11. Qwen3 Coder 30B 当廉价子代理：百万输入 0.0675 美元

作者把「加类型标注」「修 off-by-one」的活从贵模型手里拿走，交给 30B 的 Qwen3 Coder（支持 tool calling），走 OpenAI 兼容端点：输入每百万 token 0.0675 美元、输出 0.27 美元，上下文 98K。文中给了 Claude Code、Codex CLI 和 opencode 的接法；实测修一个故意写错的 add() 用 6 轮、11.3 秒。

> 杀鸡用牛刀，账单一来就知道疼。

来源：Dev.to · [https://dev.to/synap402/running-qwen3-coder-30b-as-a-cheap-subagent-for-claude-code-codex-and-opencode-2chh](https://dev.to/synap402/running-qwen3-coder-30b-as-a-cheap-subagent-for-claude-code-codex-and-opencode-2chh) · `dev_f15064ba`

## 12. 最容易被忽略的入口：没人审的 CI/CD 流水线

代码有人 review、依赖有人扫，但握着密钥、部署权限和生产凭据的 CI 配置，往往从教程复制来就没再看。文章举了一个看着很正常的 GitHub Actions：permissions: write-all、action 锁在 @main、run 里硬编码 AKIA 密钥，三个问题 CI 一声不吭。plumber-linter 专扫这类：硬编码密钥、过宽权限、未锁 action、缺失分支保护。

> 门锁三道，钥匙却大咧咧挂门口。

来源：Dev.to · [https://dev.to/parasraju/your-cicd-pipeline-is-the-easiest-way-into-your-repo-and-nobodys-checking-it-21hj](https://dev.to/parasraju/your-cicd-pipeline-is-the-easiest-way-into-your-repo-and-nobodys-checking-it-21hj) · `dev_79a17b35`

## 13. 130 行裸写 RAG：3B 模型答对 18/20 道公司制度题

作者不用任何框架，用 130 行 Python 搭最小 RAG：10 篇制度文档切 300 字块、相邻留 30 字重叠，bge-m3 本地 embedding 成 1024 维，余弦相似度取 top-3，拼 prompt 时加「资料里没有就说无法回答」和编号出处，最后交给 qwen2.5:3b 做阅读理解。20 道题检索命中 16/16，答对 18 道。

> 模型一点没变，变的是喂资料的姿势。

来源：博客园 Cnblogs · [https://www.cnblogs.com/wtang/p/23633603](https://www.cnblogs.com/wtang/p/23633603) · `dev_de3acc6e`

## 14. 端侧 Agent 防注入：把外部数据永远按数据对待

文章认为普通 Agent 一戳就破，是因为系统指令、用户提问、笔记邮件和网页混在同一条文本流里；防注入是在外面套一层确定性安全运行时：动态随机边界加词间打标（Spotlighting）让模型分得清哪段是数据，流式熔断用 NFKC 归一化和金丝雀令牌，Evidence Ledger 核对输出引用是否真查过，只读工具沙箱加人工确认兜住底线。

> 提示词防不住注入，边界才防得住。

来源：博客园 Cnblogs · [https://www.cnblogs.com/duwenlong/p/23631569](https://www.cnblogs.com/duwenlong/p/23631569) · `dev_9f30fff4`

## 15. 15MB 的 WebSocket 消息：binaryType 选错，零拷贝白做

作者从 7 行序列化代码聊起：message.encode('utf-8') 只是文本转字节，不是 zlib 流——zlib 头是 78 01/5E/9C/DA，JSON 开头是 7B，看前两字节就够。接着解释后端发 bytes 前端却拿到 Blob，是 binaryType 默认值导致，15MB 大消息用 Blob 和 ArrayBuffer 接收性能差一个量级，以及要不要上 zlib 压缩。

> 十五兆的消息，卡在没设 binaryType。

来源：博客园 Cnblogs · [https://www.cnblogs.com/yellow3gold/p/23630713](https://www.cnblogs.com/yellow3gold/p/23630713) · `dev_c1c460ee`
