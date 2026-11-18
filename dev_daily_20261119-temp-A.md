# 开发者日报 A 轨素材 · 2026-11-19

> 共 15 条 | HN Front Page 6 · GitHub Trending Daily 3 · V2EX Share 3 · Dev.to 1 · 博客园 Cnblogs 2

## 1. NGINX 两个 HTTP/2 漏洞：无需认证就能拿服务器

Wiz 联合 Ikotas Labs、Metnir、Rapid7 和 Xint 各自独立发现 NGINX 的 HTTP/2 处理存在两个无需认证的远程代码执行漏洞，编号 CVE-2026-123633 与 CVE-2026-123007，均评为严重级。NGINX 是超过 2.25 亿个网站的前门，打穿就能接管服务器、偷数据或篡改页面。文章给了检测思路和缓解建议，剩下的就看谁先升级到修复版本。

> 两亿个网站的前门，锁居然是坏的。

来源：HN Front Page · [https://www.wiz.io/blog/nginx-http2-rce-vulnerabilities](https://www.wiz.io/blog/nginx-http2-rce-vulnerabilities) · `dev_6e81a9c2`

## 2. 微软 ONNX Runtime 仓库从 GitHub 消失

microsoft/onnxruntime 的原地址现在返回 404，帖子在 HN 拿到 422 分、86 条评论。ONNX Runtime 是微软主推的跨平台推理引擎，PyTorch、Hugging Face 等一大票项目的部署链路都压在上面，仓库突然消失让下游只能一脸问号。微软没有公开说明，社区在猜是误操作、迁移还是别的动作，眼下 fork 和镜像成了唯一退路。

> 删库跑路，这回是微软自己动刀。

来源：HN Front Page · [https://github.com/microsoft/onnxruntime](https://github.com/microsoft/onnxruntime) · `dev_e755ebfc`

## 3. Quad9 退出法国：DNS 解析器不该当版权警察

瑞士非营利组织 Quad9 宣布 11 月 24 日起停止响应来自法国的 DNS 查询。原因不是成本，而是巴黎法院因它拒绝替 beIN Sports 屏蔽盗播域名而判了罚款，法国还有约 20 起类似诉讼在排队。Cloudflare 称这是「煤矿里的金丝雀」：把封禁清单塞进公共解析器，等于让中立基础设施替版权方执法。Quad9 的 CTO 在 HN 上征集有理有据的长文递交给政策制定者。

> 让 DNS 查盗版，下一个查的就是你。

来源：HN Front Page · [https://techstackups.com/articles/quad9-leaves-france-dns-blocking/](https://techstackups.com/articles/quad9-leaves-france-dns-blocking/) · `dev_c89054fe`

## 4. 哈佛工作论文：代码多了 30%，评审慢了 49%

哈佛博士生 Fiona Chen 与 James Stratton 的工作论文覆盖 718 家公司、约 72.6 万名工程师，数据取自 Jellyfish 的研发分析平台并关联 Revelio Labs 履历。结论很刺眼：采用 AI 编码 Agent 的公司代码量增加约 30%，但完成的工作量没有可测提升，代码通过评审的时间反而长了 49%——瓶颈从写码挪到了评审。论文尚未同行评审，但给「AI 提效」的账本添了一笔反向证据。

> AI 写得更快，人看得更慢，账没变。

来源：HN Front Page · [https://complexdiscovery.com/harvard-researchers-find-ai-coding-agents-shifted-the-bottleneck-to-code-review/](https://complexdiscovery.com/harvard-researchers-find-ai-coding-agents-shifted-the-bottleneck-to-code-review/) · `dev_afb4c7d8`

## 5. 随机实验：AI 摘要让外链点击少了四成

RevScope 引用一项随机实验：对部分美国桌面用户隐藏 Google AI Overviews，与仍看到摘要的用户对比，外部网站点击量下降约 40%。目前 AI 摘要已覆盖 DataForSEO 追踪的美国关键词一半以上，两年前只有 6%。文章认为 GEO（生成引擎优化）暂时补不上缺口——今年 3 月 AI 助手给网站带去的流量只占 0.3%，排名还在，被点开的概率没了。

> 排名第一，没人点你，等于没排。

来源：HN Front Page · [https://revscope.co/blog/search-seo-geo-2026/](https://revscope.co/blog/search-seo-geo-2026/) · `dev_c5b0f8fb`

## 6. 有人实测：Claude 在蛋白质序列上大规模训练过

研究者 Xinming Tu 做了个「下一个氨基酸」测试：给 Claude Fable 5.2 和 Opus 5.5 一段冷门细菌蛋白的开头，让它们预测下一位。结果能预测，把序列打乱后立刻失效，其他前沿模型全做不到；模型在大家族上表现更好，连一篇论文都没有的家族也能猜。Fable 5.2 超过所有被测的开源蛋白语言模型，Opus 5.5 与 100 亿参数的 ProtGPT3 持平，指向训练数据里确实有蛋白序列。

> 号称通用模型，背地里补了生物课。

来源：HN Front Page · [http://xinmingtu.cn/blog/2026/claude-opus-5-5-protein-sequences/](http://xinmingtu.cn/blog/2026/claude-opus-5-5-protein-sequences/) · `dev_b9070205`

## 7. Cursor 开源插件规范：17k 星，先占接口标准

Cursor 把自家的插件规范和一批官方插件一起开源，TypeScript 编写，已拿到 1.7 万星。它不只是几个示例，而是一套「编辑器里的 Agent 该怎么扩展」的约定：插件如何声明能力、如何挂到对话和编辑器动作上、如何与内置工具共存。对做 IDE Agent 的团队来说，这等于 Cursor 先把接口标准摆上台面，跟不跟是另一回事。

> 先定标准的人，收的从来是生态税。

来源：GitHub Trending Daily · [https://github.com/cursor/plugins](https://github.com/cursor/plugins) · `dev_5768e4f8`

## 8. CLI-Anything：5.9 万星，把软件改造成 Agent 的 CLI

港大数据智能实验室的 CLI-Anything 已拿 5.9 万星，目标是「让所有软件都变成 Agent 原生」。做法是给现有软件套一层结构化 CLI：参数、输出、错误码都约定好，Agent 不用截图点按钮，直接调命令再解析结果，配套 CLI-Hub 分发。它踩的是同一个痛点——MCP 和 GUI 自动化都不稳，能被脚本化的命令行反倒是 Agent 最好用的手。

> GUI 给人类看，CLI 才给 Agent 用。

来源：GitHub Trending Daily · [https://github.com/HKUDS/CLI-Anything](https://github.com/HKUDS/CLI-Anything) · `dev_5329d8ec`

## 9. NVIDIA 开源 SkillEvaluator：给 Agent 技能上质量门

NVIDIA 的 SkillEvaluator 用 Python 写成，是一个多层级的 AI 技能与插件评估框架：做质量门禁、检测技能之间的语义重叠、自动生成合成评测集，还能在真实 Agent 里跑，量化一个技能究竟怎么改变 Agent 的行为，目前 3.5k 星。技能生态膨胀到没人看得过来时，「这个技能值不值得装」就从感觉问题变成了工程问题。

> 技能越多越乱，先给每个技能打分。

来源：GitHub Trending Daily · [https://github.com/NVIDIA/SkillEvaluator](https://github.com/NVIDIA/SkillEvaluator) · `dev_e3cfeb3a`

## 10. mitmAny：把真实抓包接进 MCP，让 AI 读报文

作者开源了 mitmAny，一个把 HTTP/HTTPS 抓包接到 AI 的桌面工具：内置 MCP 服务，你正常操作网站或 App，它把请求和响应交给 Codex 等客户端分析，可以追问分页逻辑、登录流程，还被要求引用请求编号、标出不确定的推断。支持 Windows、macOS 和 Android USB 抓包，自带 JSON 查看。比截图喂模型靠谱的地方在于：证据是原始报文。

> 别让 AI 猜接口，把报文摔它脸上。

来源：V2EX Share · [https://www.v2ex.com/t/1257981](https://www.v2ex.com/t/1257981) · `dev_5c250110`

## 11. TaroBird：在地铁上用手机批准电脑上的 Agent

用 Codex、Claude Code 的人都遇到过：任务跑着，人一离开就卡在「是否继续」上，一等一下午。作者做了 TaroBird——电脑上的 Agent 照常跑，手机端能看进度、回答提问、点批准，做完的文件直接推到手机。它没有再造一个 Agent，底层仍是官方 CLI，支持 Codex、Claude Code、Kimi Code 等。本质上把「人在回路」从桌前挪进了口袋。

> Agent 不缺脑子，缺个随时点同意的人。

来源：V2EX Share · [https://www.v2ex.com/t/1257920](https://www.v2ex.com/t/1257920) · `dev_6d5bc0f0`

## 12. 1.7MB 的 3D 滑雪游戏：没有一个贴图和音频文件

V2EX 上有人分享独立游戏《雪迹》（Cold Smoke），主打放松体验的 3D 滑雪，作者 Huisky，整包约 1.7MB，而且不含任何图片、音频、模型或贴图素材：雪山、树林、天空、极光，连背景音乐和风声都由代码生成，据介绍 Fable 5.2 参与了实现。体积小到极致反而说明一件事——模型已经能写出「资产全靠算」的完整作品。

> 1.7MB 装下一座雪山，美术先下班。

来源：V2EX Share · [https://www.v2ex.com/t/1258088](https://www.v2ex.com/t/1258088) · `dev_c49b9854`

## 13. 用茶馆账本讲清 Bitcask：只追加，从不擦除

Dev.to 一篇讲 Bitcask 的文章用茶摊老板的账本作比喻：从不涂改，每笔新记录都写在最下面；本子写满就收进抽屉、永不回写；查余额只需记住「哪本、哪一行」。对应到存储就是追加日志加一张内存哈希表：目录里只有一个活跃文件，超过阈值就滚动成不可变文件，读时查索引直接定位。没有 LSM 分层、没有布隆过滤器、没有 B 树分裂，六页论文的机关就这些。

> 不删不改，账本反而查得最快了。

来源：Dev.to · [https://dev.to/nimxch/ramu-kakas-notebook-how-bitcask-stores-data-without-ever-erasing-anything-2jaj](https://dev.to/nimxch/ramu-kakas-notebook-how-bitcask-stores-data-without-ever-erasing-anything-2jaj) · `dev_2441650b`

## 14. Anthropic 的 always-on Agent：大部分时间在睡觉

博客园一篇解读 Anthropic《Building always-on agents》的文章，把「持续工作」拆成 Run 与 Session：Agent 大部分时间休眠，事件到来才启动 Run，做完继续睡。系统用持久化 Event Inbox 把接收与执行分开，Handler 只写库和去重，Worker 再唤醒 Agent、决定恢复旧 Session 还是新建。文章强调副作用操作要幂等，同一 Inbox 只留一个活跃 Worker。

> 让 Agent 睡觉，比让它一直转便宜。

来源：博客园 Cnblogs · [https://www.cnblogs.com/Qiniu-developer/p/23708543](https://www.cnblogs.com/Qiniu-developer/p/23708543) · `dev_a7f513b0`

## 15. 相似度全挤在 0.9：向量没归一化的量纲灾难

博客园「AI 工程师踩坑实录」收官篇复现了一个不出声的坑：用 transformers 原始 API 取 bge-small-zh 的 CLS 向量，六段文档范数在 6.4 到 7.2 之间，未归一化的点积跨 11.7 到 36.2，归一化后回落到 0.232 到 0.734。根因是点积等于余弦乘以两个不受控的范数，于是阈值设不了、跨查询不可比。修法就一行——入库和查询两侧都除范数，只做一边等于没做。

> 分数不对劲，先看范数，别怪模型。

来源：博客园 Cnblogs · [https://www.cnblogs.com/dawudexiaowu/p/23703439](https://www.cnblogs.com/dawudexiaowu/p/23703439) · `dev_e1ee2a6b`
