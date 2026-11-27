# 开发者日报 A 轨候选 2026-11-28

## 1. 离散对数被「确定性亚指数」攻破？一篇 ePrint 论文炸了密码学圈

浙大团队在 ePrint 挂出 2026/3020：假设「2026 年 10 月 OpenAI 的 Cauchy–Hermite 布尔张量收缩构造」成立，则存在统一确定性图灵机，以 p^o(1) 最坏时间求解素域椭圆曲线与 F_p* 上的离散对数，零随机比特，不依赖 GRH 与光滑性启发。若该假设成立，ECDSA 与 DH 全线告急。HN 160 分 71 评。

> 密码学的冬天，从一条假设开始。

- 来源：HN Front Page
- 链接：https://eprint.iacr.org/2026/3020

## 2. 黑五前夜：WebRTC 侧信道盗卡脚本潜伏五家电商

InfoHawk 发现 Lascana、Samsonite、Revolve 等五家电商在黑五前被植入盗卡脚本，载体是被篡改的营销像素、Cookie 同意组件和 CDN 文件。脚本用 WebRTC 建隐蔽信道，在用户输入卡号、CVV、姓名地址电话的瞬间外传，且发生在商店校验支付前——订单被拒也可能已被盗刷，页面毫无异常。厂商 11/24–25 已清理，泄露量未知。

> 付款还没成功，卡已经先出国了。

- 来源：HN Front Page
- 链接：https://www.infohawk.com/news/2026-11-27-black-friday-webrtc-skimmer

## 3. 美国空军云计算平台被攻破

Sky News 11 月 27 日报道，美国空军云计算平台遭黑客入侵，报道未披露入侵路径、影响范围以及是否涉及敏感数据。该条在 HN 拿到 156 分、87 条评论，是当日安全板块热度第二。原文对爬虫返回 403，本条仅依据标题与 HN 榜单信息整理，细节需等官方通报。对把「上云」当默认安全前提的团队，这是一次提醒：云是别人的机房，不是别人的责任。

> 上云不等于上天，照样被人捅下来。

- 来源：HN Front Page
- 链接：https://news.sky.com/story/us-air-forces-cloud-computing-platform-hacked-13617163

## 4. Pimalaya 全家桶一次发版：Himalaya v3 与 pimdir 标准落地

邮件 CLI Himalaya v3.0.0 领衔，Neverest、Cardamum、Calendula、Carillon 齐发 v1，Ortie 与 Comodoro 到 v3，pimdir 规范首发 1.0 并配 Rust 实现 io-pimdir。作者解释为何一次性大版本：这一年主线是整合与标准化，代价是「每个工具都破坏了某些人的用法」。终端党今年最完整的一套 PIM 工具链。

> GUI 邮件客户端，终于可以彻底卸载了。

- 来源：HN Front Page
- 链接：https://blog.pimalaya.org/pimalaya-goes-stable/

## 5. 黑五硬盘实录：同款 20TB 两年贵了 300 美元

Alex Kretzschmar 翻出八年购盘账单：2018 年 10TB 每 TB 18 美元，2023 年 18TB 低至 11.11，2024 年 20TB 只要 12.50；今年黑五同款 20TB EasyStore 标价 549.99 美元，折合 27.50/TB，比两年前贵 300 美元。他每年黑五换盘，如今考虑把十块压成五块重做 zpool。HN 488 分 422 评。

> 黑五的意义，从省钱变成了见证历史。

- 来源：HN Front Page
- 链接：https://blog.ktz.me/black-friday-hard-drive-prices-are-messed-up/

## 6. Claude Code 重构 1572 行函数：测试全绿，人还是不敢合

楼主的 AIGC 项目有个 1572 行后台任务函数，用 Claude Code 分四步重构到 150 行，圈复杂度从 143 降到 7，6471 个测试全过，但文件总长反增 31%。他不放心：比对数据库操作与日志，发现多了一次查询；生成 12000 个成功/失败/超时/限流场景对比新旧行为，结果一致；再故意注入 63 处错误，补测后全部捕获。结论：改码成本降了，验证成本没降。

> 测试全过的那一刻，才是最吓人的。

- 来源：V2EX Share
- 链接：https://www.v2ex.com/t/1260469

## 7. Namo：在飞书里 @ 一下，让本机 Codex 干活

作者受不了 Files 卡顿、资源管理器一碰 NAS 休眠就无响应，用 Rust + GPUI 写了 Windows 文件管理器 Arke：目录读取、排序、缩略图、搜索、复制删除全不在 UI 线程；直读 NTFS 主文件表，几百万文件十秒建索引；两万文件进回收站约 0.25 秒；单 exe 免安装，AGPL-3.0 无遥测。两周破千星，还有视障用户提 issue 推动补无障碍。

> 上下文不用搬了，权限倒要看好。

- 来源：V2EX Share
- 链接：https://www.v2ex.com/t/1260337

## 8. 嫌资源管理器转圈，他用 Rust + GPUI 写了个 Arke

开发者 dofy 开源 Namo，把飞书/Lark 会话接到自己的工作站：私聊发任务或群里 @ 机器人，它在授权目录内改文件、跑测试、整理结果并回到原会话；本地工作台可查任务与执行证据，执行走官方 Codex 或 Claude Code CLI，状态存本地。已发 npm 包，需 Node 24.15+，后台服务目前只完善 macOS。作者提醒：成员共享授权目录，别当多租户隔离用。

> Windows 自带的那位，该退休了。

- 来源：V2EX Share
- 链接：https://www.v2ex.com/t/1260336

## 9. Casdoor：Keycloak/Auth0/Okta 能迁了，Agent 用 MCP 管身份

开源 IAM/SSO 项目 Casdoor（Go + React，Apache 2.0，1.49 万 star，今年 2 月进 CNCF 全景图）发布月度更新：支持从 Keycloak、Auth0、Okta 迁入；AI Agent 可通过 MCP 管理；登录流程做成免代码配置。对想摆脱商业 IdP 定价、又得给 agent 发身份的团队，这三项正好戳中迁移与自动化的痛点。

> 身份这件事，终于轮到 agent 领工牌。

- 来源：V2EX Share
- 链接：https://www.v2ex.com/t/1260446

## 10. AWS NAT 网关每月白烧 200 美元？30 秒审计法

文章拆解 NAT Gateway 两个收费陷阱：一是闲置基线税，每 AZ 每小时 0.045 美元，三 AZ 一年约 1170 美元，五个开发/预发 VPC 每月白扔约 486 美元；二是数据处理费按 GB 计，跨 AZ 与出公网都烧钱。30 秒审计法是查 CloudWatch 的 BytesOutToDestination 与网关数量，非生产环境改单 AZ 或换 VPC Endpoint。

> 云账单不会骗人，只会悄悄加零。

- 来源：Dev.to
- 链接：https://dev.to/haseeb0505/why-your-aws-nat-gateway-bill-is-200mo-higher-than-it-should-be-and-how-to-audit-it-in-30s-3lgd

## 11. WordPress 冒出 w2s_ 管理员？你已被 wp2shell 拿下

如果 WordPress 里冒出 w2s_ 开头或 wp2shell.local 邮箱的管理员账号，说明站点已被 wp2shell 脚本攻陷。这是 WordPress 核心的未授权 RCE 链，默认安装即可中招、无需插件，组合了 REST API 批量端点 /wp-json/batch/v1 的路由混淆漏洞（CVE-2026-63030）。别只删账号——漏洞可能仍开着，密码哈希可能已泄露。

> 删掉管理员账号，不等于把门关上。

- 来源：Dev.to
- 链接：https://dev.to/kevinlearynet/found-w2s-admin-users-in-wordpress-your-site-was-hit-by-wp2shell-5bgh

## 12. Stagehand：让 Agent 用自然语言点按钮的浏览器框架

Browserbase 出品的 Stagehand，MIT 协议，2024 年 3 月开源，两年半 2.6 万 star，同仓库维护 TS/Python/Go 三套 SDK。核心是 act/observe/extract：act 用自然语言点击输入，改版后自动重定位；observe 只返回可交互选择器，密码不进上下文；extract 按 zod schema 抽数据。支持持久化登录态与确定性回放。

> 选择器天天过期，人话永远不过期。

- 来源：博客园 Cnblogs
- 链接：https://www.cnblogs.com/jinjiangongzuoshi/p/23798330

## 13. 缓存命中率 99.96%：启智机器人 JuiceFS 生产实践

启智机器人「大衍」具身智能平台用 JuiceFS 统一采集端与训练端：边缘走 S3 Gateway 上传，K8s 容器经 CSI 以 POSIX 读写；Redis 存元数据、MinIO 存对象、GPFS 承载热点缓存。主卷 inode 约 8063 万，日均回传 10TB。视频拆帧产生海量小文件（估算可达 3.6 亿），治理后文件数减少 99.92%，缓存命中率中位数 99.96%。

> 缓存不命中的时候，锅总在别人身上。

- 来源：博客园 Cnblogs
- 链接：https://www.cnblogs.com/JuiceData/p/23800843

## 14. 全备都在，WAL 断了：一次没变成事故的恢复失败

PostgreSQL 16 环境，每周日 02:00 全备保留 30 天，WAL 归档只留 7 天。审计要 11 月 7 日 18:00 的状态，而提问已是 11 月 26 日，目标时刻在 19 天前。作者恢复 11 月 1 日全备并按 recovery_target_time 往前滚，日志走到 consistent recovery state 后停住，第二次才确认：全备齐全，断的是 WAL。

> 备份策略写得漂亮，恢复点才见真章。

- 来源：博客园 Cnblogs
- 链接：https://www.cnblogs.com/xiaoman618/p/23799760

## 15. cursor/plugins 冲上 Trending：Cursor 开始定插件标准

Cursor 官方开源 cursor/plugins，定位「插件规范 + 官方插件集」，一天内 19.9k star、2.2k fork，854 次提交，Issue 147、PR 562。仓库里有 .claude-plugin 目录，说明它在兼容 Claude 的插件形态，同时给自家编辑器立规矩。对写 agent 工具链的人，这是一份现成的插件接口参考；对生态来说，编辑器厂商开始抢标准话语权。

> 插件标准谁定下来，生态就归谁。

- 来源：GitHub Trending Daily
- 链接：https://github.com/cursor/plugins
