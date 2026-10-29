# 开发者日报 A 轨素材 · 2026-10-30

共 15 条 | 来源：HN Front 8 / GitHub Trending 2 / V2EX 3 / Dev.to 2

## 1. Mistral 放出万亿参数旗舰 Mistral Large 4 的权重
- 来源：HN Front Page | https://mistral.ai/news/mistral-large-4-oss/
- uid：`dev_c14ed24d`

Mistral 把旗舰 Mistral Large 4（代号 Le Chonk）的权重公开了：1 万亿参数、原生多模态，官方称它是最强的开源权重编码模型，防御性网络安全也排在开源前列。相比本月早些时候的预览版，这次补的是编码、防御安全和推理效率，三种推理模式按性价比切换。模型全部在欧洲基础设施上从零训练，强调可审计的血统与自托管。

> 一万亿参数，欧洲人先把钥匙交了。

## 2. 同一批机架多榨 27% GPU：Blackwell 缺的不是硬件是调度
- 来源：HN Front Page | https://skypilot.ai/blog/grace-blackwell-needs-a-new-scheduler
- uid：`dev_0f15f4a4`

SkyPilot 拆解 Grace Blackwell NVL72：整机架 72 张 GPU 走统一 NVLink，任务一旦跨机架就退回 InfiniBand，同样训练任务性能掉 43%。麻烦在于机架局部性很难保：节点故障下线、任务错峰结束，空闲容量被摊到各机架。他们用拓扑感知放置、原地故障恢复和自动碎片整理，把同一批机架里可用的 GPU 提高了 27%。

> 买的是 NVL72，跑的是 InfiniBand。

## 3. AI 爱引用的数字，一半是「僵尸数据」
- 来源：HN Front Page | https://trakkr.ai/trakkr-research/zombie-stats
- uid：`dev_653e86df`

Trakkr 拿 200 个要数字的问题问了 ChatGPT、Perplexity、Gemini、Claude 和 Google AI Overviews，再顺着引用一层层点下去。典型例子：五家都说 44% 的销售跟进一次就放弃；点进去是 2020 年一家销售公司的统计页，再点是一篇 2017 年的自由撰稿人样稿，再往里只有两份 PPT 和两条新闻，没有问卷、没有样本、没有日期。

> 数字走得比证据远，还自带引用。

## 4. Alpine 的 GitLab 被打了：没证据也当已被攻陷重建
- 来源：HN Front Page | https://alpinelinux.org/posts/GitLab-security-incident-CVE-2026-97229.html
- uid：`dev_a993ec63`

Alpine Linux 通报：10 月 20 至 21 日有人试图用 GitLab 的 CVE-2026-97229 打他们的实例，攻击「差点成功」。漏洞在 GitLab 用 Ruby 正则引擎 Onigmo 处理 CI 配置的路径上，CVSS 10.0；GitLab 10 月 12 日已发修复，上游 Ruby 10 月 23 日才跟上。官方没找到入侵证据但无法排除，直接把实例按已失陷重建、重置全部密码，并确认 aports 仓库与 10 月 21 日发行物未被篡改。

> 修完还得重建，这才叫不赌运气。

## 5. PHP2Shell 串内核提权，拿下 25 台服务器含政府环境
- 来源：HN Front Page | https://dreamgroup.com/blog/chained-php2shell-exploit-roots-25-servers
- uid：`dev_3c19cd01`

Dream 研究团队 10 月 25 日发现一套疑似 AI 辅助的攻击链：把 PHP2Shell（CVE-2026-109618/109619）与 Fragnesia 内核提权（CVE-2026-46300）串起来，攻陷 25 台服务器，其中包括美国政府相关环境。入口是某防火墙厂商暴露的管理界面，得手后转向 Active Directory 抓凭证、枚举目录；现场留下攻击清单、利用日志和约 40 个后利用脚本。

> 从一个管理后台，直通整个域控。

## 6. 一条畸形短信，零点击打掉 Android 通话
- 来源：HN Front Page | https://smsofdeath.com/
- uid：`dev_4b64e11f`

研究者 Mark Blaszczyk 公开 Android 电话栈的零点击漏洞：一条畸形 WAP Push 短信（端口 2948）就能让 com.android.phone 崩溃，正在进行的通话包括紧急呼叫直接掉线，用户无需任何操作。根因是 WapPushOverSms 把 5 字节 uintvar 长度无检查地转成 int，再拿去 new byte[]，负长度抛异常打死主线程。5 月上报，Google 判为非安全问题、不修，10 月 29 日按 90 天期限公开，未分配 CVE。

> 五字节短信，Google 说不算安全问题。

## 7. Qwenputer：把一颗 RISC-V CPU 编译进 Qwen3.5 权重
- 来源：HN Front Page | https://divagr.com/blog/qwenputer
- uid：`dev_e91143cc`

有人往 Qwen 3.5 4B 的权重里塞了一颗能跑的 RISC-V CPU：拿模型自己的 Gated DeltaNet 线性注意力层状态当 RAM，CPU 完全在前向计算里执行，不靠工具、不靠沙箱，能跑算术、C 和 MicroPython，还塞了个实验性文件存储。作者强调这不是插件而是权重的一部分，并顺带演示了混合模型可以把推理藏进 RNN 状态里，躲开 CoT 监控。

> CPU 编译进权重，沙箱不知道该关谁。

## 8. Stack Overflow 月提问跌破 1000 条
- 来源：HN Front Page | https://news.ycombinator.com/item?id=50282454
- uid：`dev_34444374`

HN 热帖：Stack Overflow 现在每月新提问不到 1000 条，数据来自官方 SEDE 查询的公开图表，帖子 696 分、593 条评论。对比巅峰期每月数以万计的新问题，这个跌幅已经不是周期波动。评论区把原因归给 AI 直接给答案、严格的关闭与降权机制，以及「问之前先被劝退」的体验；也有人提醒，问题少了不等于知识库没价值，但新人提问那条路确实断了。

> 问答站死于没人提问，不是没人回答。

## 9. claude-mem：给编码 agent 装一套持久记忆
- 来源：GitHub Trending Daily | https://github.com/thedotmack/claude-mem
- uid：`dev_55490f36`

claude-mem 做的是 agent 的跨会话记忆：自动抓取会话里的工具调用观察，用模型压成语义摘要，下次会话再把相关片段注入回去。支持 Claude Code、Codex、Gemini、OpenClaw、Hermes、Copilot、OpenCode 等一长串宿主，README 提供三十多种语言版本。安装一条 npx 命令，登录后领记忆 key，默认走托管记忆，也能切成本地 observer。

> agent 的记性，终于外包给了一个库。

## 10. OpenMausBot：把一群本地 agent 养成聊天列表里的同事
- 来源：GitHub Trending Daily | https://github.com/milind-soni/OpenMausBot
- uid：`dev_b6d6e03b`

GitHub 今日趋势里的 OpenMausBot 是 Grok Bot 的开源替代：Electron + React 19 + TypeScript 的本地优先客户端，侧边栏每个 bot 都是真的 agent，底层跑 Claude 或 Codex，各有自己的性格、模型、云电脑和已连接应用。用法像聊联系人——看它干活，关键时刻点批准。作者明确声明与 xAI、Meta、OpenAI、Manus 无关，提供签名的 macOS、Windows 安装包。

> 把 agent 当同事养，还得给它配工位。

## 11. 一张 4090 从零走通 QLoRA 微调与 vLLM 部署
- 来源：V2EX Share | https://www.v2ex.com/t/1252859
- uid：`dev_3ddd1aa0`

V2EX 网友把自己从零走通 LoRA 的过程写成开源中文手册：一张 4090（24G）、基座 Qwen3-4B-Instruct，任务是让模型用中文回答小学生科学问题，风格差异一眼能看出来。链路是 QLoRA 微调、保存重载、BF16 合并、vLLM 部署成 OpenAI 兼容 API、再压测，9 章正文加 5 个附录，配可直接跑的 Notebook 和 560 段对话数据集，1 epoch 约 72 步。

> 一张 4090，把微调从玄学拉回流程。

## 12. 用 Go 从零写 coding agent，15 章每章都能跑
- 来源：V2EX Share | https://www.v2ex.com/t/1252848
- uid：`dev_e25bcf56`

作者用 Go 从零写了个终端 coding agent Mino，不用任何 agent 框架，只调官方 OpenAI Go SDK 的 Responses API，同时整理成 15 章教程，每章对应一个可运行版本。内容覆盖流式问答、JSONL 历史与重启恢复、逐次批准的 Bash、工具调用中断后的如实恢复、上下文压缩、项目 Skills、MCP、权限策略、Evals 和 macOS Seatbelt 沙箱，中英双语，需要一点 Go 基础。

> 十五章节，把 agent 的黑箱拆成零件。

## 13. macOS 27 蓝牙键盘延迟，被一个小工具改回来了
- 来源：V2EX Share | https://www.v2ex.com/t/1252823
- uid：`dev_31723032`

升级 macOS 27 后蓝牙键盘延迟高、丢字，作者查到原因是系统给 LE 键盘下发 peripheralLatency: 22，两次按键间最长 345ms；本指望蓝牙 5.3 的 subrating 抵消，老键盘不支持，请求失败后延迟还不回滚，系统里也没有开关。KeyAwake 用一条 CoreBluetooth 连接把延迟压回 0：菜单栏常驻、只处理键盘、空闲 3 分钟释放链路，还每分钟记录信号强度与丢包 CSV 便于排查。

> 系统给你 345 毫秒，自己写个驱动抢回来。

## 14. 贴给 coding agent 的日志，第二天还在某个记录里
- 来源：Dev.to | https://dev.to/jeff_pdc/redact-before-you-paste-it-into-the-coding-agent-31go
- uid：`dev_002aae11`

作者复盘一次真实翻车：调试时把带 Bearer token、内部域名和三行客户邮箱的 curl 响应整段贴给 coding agent，答案很好，第二天才想起这段内容还留在某个记录里。文章列了该替换的东西：token 换占位符再轮换、内部主机名换成 service.internal、邮箱只报数量、.env 只给一行非密配置、堆栈里的 session ID 抹掉但保留帧。核心原则是给形状不给值。

> agent 会忘，聊天记录可不会。

## 15. 449MB 决策模型接管客服工单分诊，不再解析 LLM 输出
- 来源：Dev.to | https://dev.to/pielounw/triage-support-tickets-locally-with-a-449-mb-decision-model-3525
- uid：`dev_dfa30716`

客服工单要判断三件事：归谁、要不要退款、有多急。常规做法是让 LLM 输出再写解析器，然后为它答「Billing（大概）」再写第二个解析器。NobodyWho 改用决策模型：选项预先给定，模型只输出每个选项的概率，一个 token 都不生成，所以没法凭空发明第四个部门。底层是 Apache-2.0 的 Laya，Q8_0 的 GGUF 只有 449MB，可以在本地跑。

> 不生成 token 的模型，编不出第四个部门。
