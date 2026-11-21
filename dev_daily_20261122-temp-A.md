# 开发者日报 A 轨素材 · 2026-11-22

> 共 15 条 | HN Front Page 6 · GitHub Trending Daily 2 · V2EX Share 3 · Dev.to 2 · 博客园 Cnblogs 2

## 1. Lean 社区宣布：黎曼猜想的证明已被机器验证通过

11 月 20 日，Levent Alpöge 以 Lean 库形式发布黎曼猜想的证明，1700 万行代码仅依赖 Mathlib。Lean 社区用一天完成复核：代码干净编译；所证命题经 comparator 与 con-leche 独立比对，确认就是 Mathlib 里标准的黎曼猜想陈述；导出的原始证明又被 Lean 内核、con-ron 及第三方检查器验证。两个检查器自带相对集合论的证明。

> 数学家熬了一百六十年，机器一天点了个头。

来源：HN Front Page · [https://leanprover-community.github.io/blog/posts/riemann-hypothesis/](https://leanprover-community.github.io/blog/posts/riemann-hypothesis/) · `dev_69436191`

## 2. GPGME 曝严重漏洞：构造超长 user id 可致 double free

GnuPG 公布 GPGME 严重漏洞 CVE-2026-129975：用带超长 user id 的 OpenPGP 密钥可触发 double free，能向应用外泄数据，不排除被用于 RCE。根因是读 gpg 状态行时缓冲区扩容后的新指针只在函数末尾回写，中途因读错误提前返回就留下已释放内存的旧指针。2.3.0 之前所有版本受影响，邮件客户端、Gpg4win 均中招，已发 2.3.1。

> 加密工具自己漏了，锁再厚也没用。

来源：HN Front Page · [https://lists.gnupg.org/pipermail/gnupg-announce/2026q4/000517.html](https://lists.gnupg.org/pipermail/gnupg-announce/2026q4/000517.html) · `dev_37d28a35`

## 3. 一行日志让欢迎页慢 15 秒：AI 不会替你顶需求

作者复盘自家 Google Forms 插件的性能事故：一条「记录安装」的日志把欢迎页拖慢到 15 秒。AI 生成的三层 try/catch——取邮箱、取 user id、写错误日志——每层背后都是多次 Google 调用，而它恰是安装后执行的第一行。作者说这正是 AI 替不了架构师之处：要么先只记时间戳，要么先渲染页面再异步补日志，而不是把市场诉求直接译成阻塞调用。

> AI 会写代码，但不会替你跟市场部吵架。

来源：HN Front Page · [https://manidoraisamy.com/developer-to-architect.html](https://manidoraisamy.com/developer-to-architect.html) · `dev_f7cbebcb`

## 4. DreamCoder：写了十五年的 Emacs 老手，造了个不一样的 AI 编程 harness

《Mastering Emacs》作者 Mickey Petersen 发布做了十五个月的 DreamCoder。他的不满很具体：Claude Code 之后所有厂商都在抄终端界面，连多行复制粘贴都难受，GUI 版本反成二等公民，界面还千篇一律——侧边栏加聊天框。他认为认真写代码的人需要更多，于是自己做了一套图形界面优先的 harness，文中也回顾了他这一年多观察 AI 编程工具的感想。

> 看不惯终端，就自己造，Emacs 人的老毛病。

来源：HN Front Page · [https://www.masteringemacs.org/article/announcing-dreamcoder](https://www.masteringemacs.org/article/announcing-dreamcoder) · `dev_7e78ad59`

## 5. 一根线惹的祸：显示器把千兆下载砍掉了 75%

作者家里是 2.5G 对称宽带，某天测速下载只剩 600Mbps，上传仍有 2.4Gbps。ISP 查不出问题，换笔记本也一样。真凶是他为「一根线换电脑」把外设全插在 Studio Display XDR 上：网卡接显示器时下载中 ping 有线机器失败率 10%，走 Wi-Fi 为 0%，macOS 日志却无丢帧错误——包在到电脑前就被显示器那一跳丢了。网卡直插 Mac 立刻满速。

> 显示器兼职当交换机，还顺手限了个速。

来源：HN Front Page · [https://blog.tymscar.com/posts/studiodisplayethernet/](https://blog.tymscar.com/posts/studiodisplayethernet/) · `dev_a9f1b5b1`

## 6. ClawDOS：在 4.77MHz 的 IBM PC XT 上跑 AI 编程 agent

有人把 AI 聊天和编程 agent 塞进了真正的 IBM PC XT：8088 处理器 4.77MHz、640K 内存、CGA 显卡，项目叫 ClawDOS，跑在实机而非模拟器上。作者的动力很朴素——这是他五岁时家里第一台电脑，靠它学会打字和 DOS 才玩得上「学字母」的小游戏。项目展示了在极端受限的硬件上，「对话 + 写代码」这个循环还能怎么运转，读起来更像一封写给早期 PC 的情书。

> 4.77MHz 上跑 agent，等响应够泡杯茶。

来源：HN Front Page · [http://ricapar.net/ClawDOS/](http://ricapar.net/ClawDOS/) · `dev_66de8d3b`

## 7. obra/superpowers：把开发方法论打包成 agent 技能框架

obra/superpowers 是 GitHub 趋势上的 agentic skills 框架，主张把开发方法论本身做成可复用的技能包，而不是给 agent 一堆散装提示词。仓库提供 .claude-plugin、.codex-plugin、.cursor-plugin 等多套适配，同一份技能能装进不同 harness，累计 687 次提交，适合搭工作流时抄结构。

> 把方法论打包成插件，这届 agent 挺讲究。

来源：GitHub Trending Daily · [https://github.com/obra/superpowers](https://github.com/obra/superpowers) · `dev_488567a9`

## 8. Claude-BugHunter：82 个技能、681 条披露报告模式的红队技能包

elementalsouls/Claude-BugHunter 是一套面向漏洞挖掘和外部红队工作的 Claude Code 技能包：82 个技能、15 个斜杠命令，整理了 681 条已公开披露的报告模式，覆盖 24 类核心漏洞，另附企业身份与基础设施的攻击矩阵。它的价值不在让模型更会说话，而是把这些年公开报告里的套路固化成可调用的流程，做渗透测试和 SRC 的人可以当作业模板直接上手。

> 红队经验做成技能包，新手也能照着捅。

来源：GitHub Trending Daily · [https://github.com/elementalsouls/Claude-BugHunter](https://github.com/elementalsouls/Claude-BugHunter) · `dev_1a9ba9eb`

## 9. 21 岁中医学生开源 Agent 记忆系统：262k 多跳 48.3%

21 岁中医学大三学生开源了 Agent 记忆系统 WhaleYing Memory，跑在无独显 Windows 轻薄本上。它把长文抽成 facts／cards／metrics／identities 四表，用 supersession 记录版本取代关系，再做混合检索与 Self-Ask 多跳。MemoryAgentBench 262k 单跳 93.2%、多跳 48.3%，高于 CAR 的 41%。

> 中医学生把记忆做明白了，科班的该脸红。

来源：V2EX Share · [https://www.v2ex.com/t/1258680](https://www.v2ex.com/t/1258680) · `dev_3fb05909`

## 10. 两周 229 条：V2EX「分享创造」都在卷什么

有人把 V2EX「分享创造」11/07–11/21 两周的 229 条帖子按回复数排序：Mac 截图录屏二合一 Fotilo（157 回复）、一个 App 刷多论坛的「看帖」（132）、SwiftUI 系统监控 Ebb（100）；最硬的是逆向 macOS 屏幕共享高性能模式的免费远程桌面 Ferry，以及 Rust 写、支持 AV1 硬件编码 120fps 的 Airhand。

> 两周 229 个轮子，独立开发者的体力真好。

来源：V2EX Share · [https://www.v2ex.com/t/1258800](https://www.v2ex.com/t/1258800) · `dev_b57ca74b`

## 11. Edge 插件被拒一次：认证备注要写「怎么测」，不是「是什么」

作者把 ConvoExport 提交 Edge 商店，v1.0.0 因政策 1.3「Product is Testable」被拒：没给测试步骤，也没说明账号情况。重提时他在认证备注里写了 1237 字，给出公开 ChatGPT 分享链接的逐步测试路径，并声明无需测试账号、未编造凭据，随后过审。他的结论是：审核员测不了你的产品时，一条公开可复现的路径比测试账号更管用。

> 审核不是考试，是给陌生人写说明书。

来源：V2EX Share · [https://www.v2ex.com/t/1258806](https://www.v2ex.com/t/1258806) · `dev_429cb270`

## 12. 复制按钮亮了，剪贴板里真有东西吗

复制按钮的正确写法：点击只代表用户「想复制」，navigator.clipboard.writeText() 返回的 Promise 才代表真写进去了。作者把埋点挪到 await 之后，写入失败就弹对话框、把文本预先选中让用户手动复制，而不是假装成功。文中还讨论了权限被拒、非安全上下文、iframe 限制下 writeText 会 reject，以及「点击即上报成功」如何让数据失真。

> 按钮亮一下就算成功，埋点全是幻觉。

来源：Dev.to · [https://dev.to/ranchjiao0607/the-copy-button-was-clicked-did-anything-reach-the-clipboard-34ef](https://dev.to/ranchjiao0607/the-copy-button-was-clicked-did-anything-reach-the-clipboard-34ef) · `dev_fe2a4326`

## 13. Eval Pyramid 第三篇：从一个失败追到发布闸门

《The Eval Pyramid》第三篇用一个退款 agent 的失败做教学：四次试验三次通过，第四次告诉客户「49 美元退款已处理」，而支付流水是空的——聚合指标说可以上线，关键闸门说不。失败从任务 fixture 追到发布闸门：fixture 只给输入不给答案，harness 通过独立观察者从工具服务读结果，而不是相信 agent 自述。

> 平均分很好看，就是钱没退出去。

来源：Dev.to · [https://dev.to/bharadwajpendyala/the-eval-pyramid-part-iii-trace-one-failure-from-fixture-to-release-gate-39fd](https://dev.to/bharadwajpendyala/the-eval-pyramid-part-iii-trace-one-failure-from-fixture-to-release-gate-39fd) · `dev_3ca4169e`

## 14. 为什么 PPO 训不出顶级象棋引擎：优化目标和搜索要的不一样

一篇中国象棋 AI 的实验复盘：作者先复现腾讯「无搜索象棋 AI」的思路，再把 PPO 模型分别接进 α-β、MCTS、BFMS 三种搜索，结果三种搜索全部失败。文章给出一条主线解释——PPO 优化的是「最优解」，而所有搜索算法需要的是「全宽度排序」，两者目标并不一致。文中数字全部来自等节点对战、同开局、可复现脚本，文献结论均给出出处，属于少见的把负结果写清楚的工程记录。

> PPO 只认第一名，搜索却要全班排名。

来源：博客园 Cnblogs · [https://www.cnblogs.com/strawberryPudding/p/23741963](https://www.cnblogs.com/strawberryPudding/p/23741963) · `dev_f740050b`

## 15. 源码级拆解：开源 WAF 的 1 秒滑动窗口限流

作者拆解开源 WAF「盾甲」的流控源码，重点是 qps.php 里那套 1 秒滑动窗口：固定窗口的致命缺陷是攻击者可以在两个窗口的交界处，用 20 毫秒打出 200 次请求；滑动窗口结合历史时间戳做权重计算，能准确算出「刚刚过去的一秒」里到底进了多少请求。实现上同时限制全局 QPS 防 DDoS 和单 IP QPS 防 CC，保证恶意流量挤不掉正常用户，是后端最基础也最容易忽略的一道防线。

> 固定窗口限流，等于给攻击者留了门。

来源：博客园 Cnblogs · [https://www.cnblogs.com/anye1991/p/23735610](https://www.cnblogs.com/anye1991/p/23735610) · `dev_dcfba695`
