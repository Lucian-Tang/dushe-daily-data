# QA 报告 · 开发者日报 A 轨 2026-11-29

> 复核修订版：2026-11-29 00:34 复核发现 content 含空格实测 181–230 字、12 条超 200 上限，已全部压缩；以下数字均为脚本对最终 JSON 实测，非估算。

- 条数：15（要求 12–15）
- uid 唯一：15/15 ✅
- 近 3 天 CDN URL 重叠：0 条 ✅
- 字段齐全（title/content/quote/source/url/category/lang/published/uid）：✅
- content 长度（含空格，Python `len()` 实测）：181–200，均值 193.9 ✅（全部 ≤200，无 <160）
- quote 长度（含空格实测）：15–20 ✅
- title 长度：最长 40 ✅（≤40）
- published：全部 2026-11-29 ✅
- 语言：{'en': 10, 'zh': 5}
- 来源分布：{'HN Front Page': 7, 'HN Show HN': 2, 'V2EX Share': 3, '博客园 Cnblogs': 2, 'GitHub Trending Daily': 1}
- 分类分布：{'security': 3, 'tool': 3, 'ai': 4, 'devops': 1, 'hardware': 1, 'discussion': 1, 'mobile': 1, 'opensource': 1}

## 本次修订

- 压缩 12 条超限 content（第 1、3、5、6、8、9、10、11、12、13、14、15 条）至 160–200 字，保留原有关键数字与结论。
- 未改动 3 条：第 2 条（192）、第 4 条（188）、第 7 条（181）。
- md 正文已按最终 JSON 重新生成。

## 去重对比文件

- reports/dev-daily/2026-11-26-temp-A.json / 2026-11-26-temp-B.json
- reports/dev-daily/2026-11-27-temp-A.json / 2026-11-27-temp-B.json
- reports/dev-daily/2026-11-28-temp-A.json / 2026-11-28-temp-B.json
- dushe-daily-data/dev_daily_20261126.json / 20261127.json / 20261128.json

合计 89 个历史 URL；原始数据 182 条中 9 条与其重复（含 infohawk 盗卡脚本、bouncemarket，以及 6 个已用 GitHub Trending 仓库），已全部剔除。本批 15 条按 url 精确比对，重叠 0。

## URL 可用性

| # | 状态 | 来源 | URL |
|---|---|---|---|
| 1 | 200 | HN Front Page | https://malspark.com/blog/malicious-gguf-models-hugging-face/ |
| 2 | 200 | HN Front Page | https://unkernel.dev |
| 3 | 200 | HN Front Page | https://research.google/blog/supercharging-transformer-residual-connections/ |
| 4 | 200 | HN Front Page | https://tabernet.es/ |
| 5 | 200 | HN Front Page | https://xinyadu.github.io/blog/claude-code-sabotage.html |
| 6 | 200 | HN Front Page | https://koppar.ai/blog/lte-modem-bring-up/ |
| 7 | 200 | HN Front Page | https://www-cs-faculty.stanford.edu/~knuth/moratorium.html |
| 8 | 200 | HN Show HN | https://github.com/Ri4dH/ramgod |
| 9 | 200 | HN Show HN | https://mquan.github.io/netflix_challenge/ |
| 10 | 200 | V2EX Share | https://www.v2ex.com/t/1260635#reply1 |
| 11 | 200 | V2EX Share | https://www.v2ex.com/t/1260524#reply4 |
| 12 | 200 | V2EX Share | https://www.v2ex.com/t/1260534#reply0 |
| 13 | 200 | 博客园 Cnblogs | https://www.cnblogs.com/emiyazero/p/23814514 |
| 14 | 200 | 博客园 Cnblogs | https://www.cnblogs.com/allen0118/p/23810243 |
| 15 | 200 | GitHub Trending Daily | https://github.com/nginx/nginx |

全部 200，无 403/401 反爬项，无需替换。

## 抓取与选源备注

- `python3 scripts/fetch_dev.py` 产出 `data/raw_dev_20261129.json`，共 182 条：V2EX Tech 50、V2EX Share 50、HN Show HN 20、HN Front Page 20、博客园 20、Dev.to 12、GitHub Trending 10。
- 开源中国 OSChina 返回 0 条（RSS 空），已跳过；无超时失败源。
- Dev.to 当日 12 条多为 SEO 软文/房产规范/德语发票类，无实质开发内容，本批未选。
- V2EX Tech 多为旧帖（ID 11xxxx–125xxxx）且水贴比例高，本批仅从 V2EX Share 选新帖。
- GitHub Trending 10 条中 7 个仓库近 3 天已用，仅 nginx/nginx 可用。
