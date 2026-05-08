# GitHub Trending采集器测试报告 — github-collector-007

> 测试时间：2026-05-02

---

## 测试结论

| 项目 | 结果 |
|------|------|
| 脚本路径 | `collectors/github/github_collector.py` |
| 数据源 | GitHub Search API (`api.github.com/search/repositories`) |
| 查询策略 | 7天内新建仓库，按stars排序 |
| 稳定性 | ✅ 通过 |
| 反爬 | ✅ 官方API，无需绕过 |
| 输出格式 | JSON |
| 单次耗时 | <5秒 |

---

## 修复内容

1. **弃用HTML解析**：GitHub Trending 页面需要登录，HTML解析结果全为登录跳转
2. **改用Search API**：获取7天内新建仓库，按stars排序，等效于Trending
3. **增加字段**：stars/forks/created_at/url/name/description/language

---

## 测试数据（2026-05-02）

| 排名 | 仓库名 | ★ Stars | 语言 | 描述 |
|------|--------|---------|------|------|
| 1 | nexu-io/open-design | 12759 | TypeScript | Local-first Claude Design替代 |
| 2 | cursor/cookbook | 3002 | TypeScript | - |
| 3 | theori-io/copy-fail-CVE-2026-31431 | 2628 | Python | - |
| 4 | denuitt1/mhr-cfw | 1374 | Python | GAS隧道VPN |
| 5 | willchen96/mike | 1156 | TypeScript | OSS AI法律平台 |
| 6 | darrylmorley/whatcable | 917 | Swift | macOS USB-C检测工具 |
| 7 | DanOps-1/Gpt-Agreement-Payment | 888 | Python | ChatGPT订阅协议重放工具 |
| 8 | b-nnett/codex-plusplus | 785 | TypeScript | Codex++ |
| 9 | GENEXIS-AI/chromex | 742 | TypeScript | Codex Chrome侧边栏 |
| 10 | t8y2/dbx | 636 | Vue | 轻量跨平台数据库客户端 |

**获取总数：25条**

---

## 使用方法

```bash
cd /root/.openclaw/workspace/daily-digest/collectors/github
python3 github_collector.py
# 输出文件：github_trending_YYYYMMDD_HHMMSS.json
```

---

## 限制说明

GitHub Search API 未认证限速 60 req/hr，脚本每次请求1次，风险极低。

---

## 状态：✅ 可用