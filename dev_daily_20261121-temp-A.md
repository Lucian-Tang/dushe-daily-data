# 开发者日报 A 轨素材 · 2026-11-21

> 共 14 条 | HN Front Page 8 · Dev.to 4 · 博客园 Cnblogs 2

## 1. AI 从零设计出 CPU：Frostbite 每瓦性能 4.59 倍

Architect Labs 发布 Frostbite：一套由 AI 从指令集、微架构、RTL 一路做到最终 GDS 的通用 CPU 新架构。核心利用交互网「每步局部、依赖显式、每个值只有一个所有者」的性质。在 25 个负载（其中 15 个留到最终评测）上，每瓦性能达到一颗已流片的现代双发射顺序超标量核的 4.59 倍，面积效率同步提升。HN 421 分、256 条评论。

> 人类设计停滞多年，AI 一上手就掀桌子。

来源：HN Front Page · [https://architectlabs.com/blog/frostbite](https://architectlabs.com/blog/frostbite) · `dev_fded32d7`

## 2. PostgreSQL 19 发布：REPACK 上线，逻辑复制免重启

PostgreSQL 19 于 11 月 19 日发布，新增 REPACK 命令回收磁盘空间并重排表内容，带 CONCURRENTLY 时读写不被阻塞；两个新扩展可以固定或自动套用执行计划建议；只要预写日志级别够，开逻辑复制不必重启，序列值也能同步；备库新增等待命令，可实现读己之写；自动清理支持索引并行。HN 328 分。

> VACUUM FULL 终于等来一个体面的替代品。

来源：HN Front Page · [https://www.postgresql.org/docs/release/19.0/](https://www.postgresql.org/docs/release/19.0/) · `dev_e2ddb871`

## 3. FFmpeg 9.1「Gauss」发布：AAC 编码器大改

FFmpeg 9.1（代号 Gauss）发布：AAC 编码器做了大幅改进，新增 APV 的 Vulkan 编码器、基于图的码流过滤接口、对 ASTC 图像编解码的支持、DVD-Audio 无损解码、H.264 数据分区，以及用显卡做零拷贝推理的 ONNX 后端；同时补上 libcurl 协议和新的硬件解码路径，另修了一批解码器的老问题。HN 243 分。

> 多媒体界的瑞士军刀，又磨了一遍刀刃。

来源：HN Front Page · [https://ffmpeg.org/download.html#release_9.1](https://ffmpeg.org/download.html#release_9.1) · `dev_186d387a`

## 4. OpenSSL 9.8 分漏洞：EVP_EncodeBlock 写越界

OpenSSL 披露编号 CVE-2026-121481 的漏洞，通用漏洞评分 9.8：调用 EVP_EncodeBlock() 时，若输入长度接近整数上限，编码后长度的计算会溢出，从而越过调用方缓冲区写入。修复补丁改为对非法输入直接返回负一，并给对应的解码函数加上同样保护，同时修正 http_client.c 里一处长度检查。HN 332 分。

> 整数溢出这口老井，三十年还能捞出人来。

来源：HN Front Page · [https://github.com/openssl/openssl/pull/33652](https://github.com/openssl/openssl/pull/33652) · `dev_ff7f3634`

## 5. 欧盟日本开闸三年，iOS 仍无一个非 WebKit 浏览器

Mozilla 发文：DMA 生效后 Firefox 在 iOS 的日活翻倍，但苹果仍要求所有 iOS 浏览器基于 WebKit。欧盟与日本虽强制开放替代引擎，苹果给出的合规条件近三年无人能过，至今没有一个非 WebKit 浏览器上架。Mozilla 称这些条件「尽可能让人痛苦」，并质疑规则只看条文、不看结果。HN 81 分、21 条评论。

> 开放是开放的，只是门槛修在了天花板上。

来源：HN Front Page · [https://blog.mozilla.org/en/mozilla/internet-policy/apple-ios-browser-engine-rules/](https://blog.mozilla.org/en/mozilla/internet-policy/apple-ios-browser-engine-rules/) · `dev_8272a310`

## 6. 只靠 AI 写码的人，评审能力也会一起退化

开发者 cekrem 写文反驳「靠 AI 写码、自己只做评审」的流行说法：任何手艺停止练习都会退步，软件工程却假装例外。他用跑步、吉他手和作家的类比说明，读得多不等于评审得准，判断力来自亲手写、亲手踩坑。文章强调讨论的不是短期产出质量，而是工匠是否还在练手。HN 128 分、51 条评论。

> 只看别人游泳，迟早会忘了水有多呛。

来源：HN Front Page · [https://cekrem.github.io/posts/if-you-stop-writing-code-you-also-get-worse-at-reviewing-it/](https://cekrem.github.io/posts/if-you-stop-writing-code-you-also-get-worse-at-reviewing-it/) · `dev_a9069d31`

## 7. Anthropic 员工称与 Claude 一起证明了黎曼猜想

一份 4 页短文出现在 alpo.ge：作者称与 Claude 合作找到了黎曼猜想的证明，方法还可推广到广义黎曼猜想，并已用 Lean 完成无假设形式化，但因篇幅只公开 Lean 代码。文中提到关键一步是 theta 提升链长度取 √X，并承认发布时机敏感、自己尚未完全消化这套数学。HN 948 分、592 条评论，质疑与震惊齐飞。

> 四页纸加一个压缩包，数学界先别急着开香槟。

来源：HN Front Page · [https://alpo.ge/remark.pdf](https://alpo.ge/remark.pdf) · `dev_83cf23c9`

## 8. 英国悄悄修掉冰柜漏洞：数万台设备差点被远程升温

BBC 披露一场未公开的网络安全行动：10 月底研究人员在商用制冷设备中发现一个可被远程利用的重大漏洞，若被黑客先找到，英国超市、仓库、餐厅和体育馆的数万台冰柜可能被集体升温。Omega Solution、IT 团队与英国国家网络安全中心连夜通知数十家企业并完成加固；此前欧洲已有多起冷柜被攻击、食品腐烂的事件。HN 114 分。

> 物联网最魔幻的地方：黑客能给你的晚饭加热。

来源：HN Front Page · [https://www.bbc.co.uk/news/articles/c6eq49zyx7p4o](https://www.bbc.co.uk/news/articles/c6eq49zyx7p4o) · `dev_922e8249`

## 9. Node.js 背压算错字节数：中文响应能多缓存三倍

作者发现 Node.js 的 HTTP 响应对象按字符串长度统计缓冲区，而它数的是 UTF-16 码元不是字节：两字节字符少算一半，中文常见少算三倍。结果是写入早已超过水位线仍返回成功，套接字暂停得太晚。已提交的修复 PR #66039 改用真实字节长度，并把首次写入时附带的响应头字节也算进去。

> 四行代码复现，十年老模块的面子挂不住。

来源：Dev.to · [https://dev.to/quantumbreakz/why-nodejs-http-backpressure-must-count-bytes-not-string-length-19d2](https://dev.to/quantumbreakz/why-nodejs-http-backpressure-must-count-bytes-not-string-length-19d2) · `dev_1e061d1b`

## 10. 一个 YAML 缩进，让 Prometheus 抓了两遍

Grafana Pyroscope 的 Helm chart 里，服务监控靠标签选择服务，从不看注解。一次为支持自定义注解做的重构，把 prometheus.io/service-monitor 这个排除键缩进了注解字段，规则静默失效，Prometheus 于是用两个任务抓同一批容器，指标翻倍、面板求和也算重。渲染时完全不报错，修复已提交。

> YAML 不报错，账单替你报错。

来源：Dev.to · [https://dev.to/quantumbreakz/labels-vs-annotations-how-one-yaml-indent-made-prometheus-scrape-pyroscope-twice-23dp](https://dev.to/quantumbreakz/labels-vs-annotations-how-one-yaml-indent-made-prometheus-scrape-pyroscope-twice-23dp) · `dev_846e17d1`

## 11. 给 MCP 服务器接 OAuth 2.1：别让 Agent 拿共享密钥

作者为 Nitspot CRM 做 MCP 连接器，总结出一套授权设计：OAuth 2.1 加 PKCE（只允许 S256）、动态客户端注册、401 时用 WWW-Authenticate 指向 /.well-known 元数据做发现。关键决定是把 access token 当成真实用户会话，交给数据库行级安全鉴权，销售看不到交易、管理员可以；重定向 URI 精确匹配，授权码一次性使用。

> Agent 可以有权限，但不能有特权。

来源：Dev.to · [https://dev.to/quantumbreakz/how-to-build-a-secure-mcp-server-with-oauth-21-lessons-from-a-crm-connector-42ml](https://dev.to/quantumbreakz/how-to-build-a-secure-mcp-server-with-oauth-21-lessons-from-a-crm-connector-42ml) · `dev_d04b2866`

## 12. pandas 取每组前 N 行：七个坑和一条稳的路

取每组前 N 行时，别对分组对象直接调 nlargest，它根本没这个方法。作者在 pandas 3.0.6 上列了七个坑：只需要值，用 groupby(key)[col].nlargest(n)；需要整行，就先排序再 groupby().head(n)。后一条路能给出可重复的并列排序，也能自己决定缺失值怎么填。文章用 75 万行的模拟面板演示，并列、空值和重复索引都会让结果多出意外的行。

> 并列值一多，排行榜就开始自己加戏。

来源：Dev.to · [https://dev.to/dustinliang/pandas-nlargest-per-group-7-pitfalls-when-picking-the-top-n-rows-per-day-in-a-mentions-panel-43nn](https://dev.to/dustinliang/pandas-nlargest-per-group-7-pitfalls-when-picking-the-top-n-rows-per-day-in-a-mentions-panel-43nn) · `dev_20dd119c`

## 13. 三层 B+ 树能装多少行？把 MySQL 索引算给你看

文章从「两千万行主键查询为什么快」讲起：InnoDB 页 16KB，非叶子页只存 key 和页指针，bigint 主键加 6 字节指针约 14 字节，一页放约 1170 项；叶子页按一行 1KB 算放 16 行。三层就是 1170×1170×16，约 2190 万行，多数业务表只有 2 到 4 层。文中还对比 int、bigint、binary(16) 与 char(36) 主键的容量差距。

> 面试只会答「因为快」的人，该抄十遍。

来源：博客园 Cnblogs · [https://www.cnblogs.com/leikooo/p/23726844](https://www.cnblogs.com/leikooo/p/23726844) · `dev_3abb3048`

## 14. 四十行七条时序语义：用定向变异测试逐个撞护栏

张善友把 Node 的子进程管理模块移植到 .NET，WindowsJobOwner 只有三个动作，却挤着七条互相牵制的时序语义。文章用定向变异测试逐条验证：先问「这条语义没护栏会怎样」，再设计一处能编译但语义错误的改动，跑测试看是否变红；并强调必须区分 killed、survived 与 stillborn，核对测试总数，否则 import 失败也会被记成击杀成功。

> 覆盖率九成却一改就绿，测试写了个寂寞。

来源：博客园 Cnblogs · [https://www.cnblogs.com/shanyou/p/23726584](https://www.cnblogs.com/shanyou/p/23726584) · `dev_24469b58`
