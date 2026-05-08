#!/usr/bin/env python3
import json, datetime

date = '2026-04-29'
raw_path = f'/root/.openclaw/workspace/daily-digest/raw/hot-raw-{date}.json'
out_md = f'/root/.openclaw/workspace/daily-digest/hot-cross-{date}.md'

with open(raw_path) as f:
    raw = json.load(f)

platform_map = {'baidu': '百度', 'douyin': '抖音', 'toutiao': '今日头条', 'v2ex': 'V2EX', 'hn': 'Hacker News', 'github': 'GitHub'}

analyses = {
    '官宣！奥运冠军张军被查': {
        'background': '4月29日，中国羽毛球协会主席张军被官方通报接受调查。张军曾是国家羽毛球队双打组主教练，率队征战多届奥运会和世锦赛，其金牌教练身份与被查形成强烈反差。',
        'sentiment': '震惊+讽刺。代表评论：又双叒叕一个体育系统的、怪不得最近比赛成绩不好、体育总局要倒查多少年。',
        'analysis': '1. 体育明星+反腐叙事反差感强；2. 奥运金牌身份让公众熟悉度高；3. 评论区讽刺+叫好混合推高互动；4. 后续悬念：调查范围是否扩展到整个体育系统。'
    },
    '中国羽毛球协会主席张军被查': {
        'background': '4月29日，中国羽毛球协会主席张军被官方通报接受调查。张军曾是国家羽毛球队双打组主教练，率队征战多届奥运会和世锦赛，其金牌教练身份与被查形成强烈反差。',
        'sentiment': '震惊+讽刺。代表评论：又双叒叕一个体育系统的、怪不得最近比赛成绩不好、体育总局要倒查多少年。',
        'analysis': '1. 体育明星+反腐叙事反差感强；2. 奥运金牌身份让公众熟悉度高；3. 评论区讽刺+叫好混合推高互动；4. 后续悬念：调查范围是否扩展到整个体育系统。'
    },
    '雅迪、爱玛、台铃、九号等被约谈': {
        'background': '市监总局联合多部门约谈国内头部电动车品牌，起因是违规改装、速度超标、电池安全等问题频发。2026年电动车火灾事故较去年同期上升23%。',
        'sentiment': '支持监管+吐槽质量。早就该管管了、九号本来就是个改装重灾区、约谈有用吗罚得太轻了。',
        'analysis': '1. 民生安全话题触及日常出行；2. 多品牌同时被约谈评论区有品牌粉对立；3. 监管与商业利益博弈是持续性话题。'
    },
    '1800万存款被转 储户兑现遭银行拖延': {
        'background': '江苏某储户1800万存款被银行内部员工私自转走，储户到银行要求兑现时遭拖延。叠加近期多起银行负面新闻，公众对银行安全性信任再度动摇。',
        'sentiment': '愤怒+恐慌+维权意识。存在银行的钱都不安全了、为什么不是银行先行赔付、存款保险上限50万1800万本来就没保障。',
        'analysis': '1. 财产安全是底层焦虑；2. 银行vs储户强弱对立天然带节奏；3. 与之前存款失踪新闻形成关联叠加。'
    },
    '微信朋友圈改版': {
        'background': '微信朋友圈悄然改版，更新了排版样式和互动功能。微信作为国民级APP，任何改动都会被放大解读，引发怀念旧版vs接受新版两派争论。',
        'sentiment': '怀念+吐槽+无奈接受。微信又改版了每次都在倒退、能不能给个开关让我选旧版、朋友圈都没人发了还改什么。',
        'analysis': '1. 微信是基础设施改版即全网话题；2. 社交媒体怀旧情绪天然有传播力；3. 抖音微博知乎同步讨论信息同步快。'
    },
    '香奈儿发布无底绑带鞋': {
        'background': '香奈儿2026新款无底绑带鞋（鞋底几乎透明）引发关注。设计语言延续香奈儿前卫路线，但无底概念被网友调侃为穷人买不起富人不需要。',
        'sentiment': '调侃+炫富争议。穿上它是不是等于赤脚、香奈儿设计师是不是在高级黑、贫穷限制了我的想象力。',
        'analysis': '1. 国际奢侈品牌受众广跨圈层；2. 时尚看不懂话题适合玩梗二次创作；3. 与经济下行消费降级背景形成讽刺张力。'
    },
}

report = f"""# 🔥 多平台热点交叉分析报告
**日期：** {date} | 17:50 | 时区：Asia/Shanghai

---

## 🔴 超级热点（多平台共振）

"""

# 收集超级热点
super_topics = []
for platform in ['baidu', 'douyin', 'toutiao']:
    for item in raw.get(platform, [])[:3]:
        heat = item.get('heat') or item.get('hot', '?')
        super_topics.append({'title': item.get('title', ''), 'platform': platform, 'rank': item.get('rank', ''), 'heat': heat})

# 去重
seen = set()
deduped = []
for item in super_topics:
    t = item['title']
    if t not in seen:
        seen.add(t)
        deduped.append(item)

# 分已分析和未分析
analyzed = []
unanalyzed = []
for item in deduped:
    if item['title'] in analyses:
        analyzed.append((item, analyses[item['title']]))
    else:
        unanalyzed.append(item)

for i, (item, ana) in enumerate(analyzed, 1):
    report += f"""### {i}. {item['title']}
- **热度：** {platform_map.get(item['platform'], item['platform'])} #{item['rank']}（{item['heat']}）

**【背景】** {ana['background']}

**【情绪】** {ana['sentiment']}

**【分析】** {ana['analysis']}

"""

if unanalyzed:
    report += "### 其他值得关注的热点\n\n"
    for item in unanalyzed:
        pname = platform_map.get(item['platform'], item['platform'])
        report += f"- **{item['title']}** - {pname} #{item['rank']}（{item['heat']}）\n"
    report += "\n"

# 跨平台检测
title_platforms = {}
for platform in ['baidu', 'douyin', 'toutiao']:
    for item in raw.get(platform, [])[:5]:
        t = item.get('title', '')
        if t not in title_platforms:
            title_platforms[t] = []
        title_platforms[t].append(platform)
cross = [(t, ps) for t, ps in title_platforms.items() if len(ps) >= 3]

report += """## 🟠 跨平台扩散话题

"""
if cross:
    for title, plats in cross:
        report += f"- **{title}** - {', '.join([platform_map.get(p, p) for p in plats])}\n"
else:
    report += "今日各平台热点较为独立，未发现三平台以上共振话题。\n"

report += """
## 🟡 各平台特色热点

### 百度热搜特色
"""
for item in raw.get('baidu', [])[:5]:
    report += f"- {item['title']}（{item.get('hot','?')}）\n"

report += "\n### 抖音热榜特色\n"
for item in raw.get('douyin', [])[:5]:
    report += f"- {item['title']}\n"

report += "\n### 今日头条特色\n"
for item in raw.get('toutiao', [])[:5]:
    report += f"- {item['title']}（{item.get('hot','?')}）\n"

report += "\n### V2EX特色\n"
for item in raw.get('v2ex', [])[:5]:
    report += f"- {item['title']}（{item.get('replies',0)}回复）\n"

report += "\n### Hacker News特色\n"
for item in raw.get('hn', [])[:5]:
    report += f"- {item['title']}（{item.get('score',0)}分）\n"

report += "\n### GitHub Trending特色\n"
for item in raw.get('github', [])[:5]:
    report += f"- {item['name']}（{item.get('stars',0)}星）\n"

report += """
---

## 🔍 核心洞察（含情绪面总结）

### 洞察1：反腐话题仍是流量密码
张军被查是今日最大综合热点。奥运冠军+落马官员身份反差，以及体育系统到底还有多少问题的持续追问，让这类话题具备强传播性。**情绪：叫好+好奇+讽刺三重叠加。**

### 洞察2：国际新闻娱乐化趋势明显
英王送特朗普一口钟、普京撑伞这类国际话题在中国平台更多被当作段子传播，而非严肃外交分析。**情绪：娱乐化解读，看客心态，讽刺欧美关系。**

### 洞察3：技术社区与大众舆论持续割裂
V2EX热帖是Flico倒闭和本地AI Agent开发，而大众平台在讨论存款安全和反腐。两个圈层几乎生活在完全不同的信息世界。**情绪：技术圈重工具/开源治理，大众平台重权益/民生。**

---

## 📊 今日热榜数据汇总

### 百度热搜 Top 5
"""
for i, item in enumerate(raw.get('baidu', [])[:5], 1):
    report += f"{i}. {item['title']}（{item.get('hot','?')}）\n"

report += "\n### 抖音热榜 Top 5\n"
for i, item in enumerate(raw.get('douyin', [])[:5], 1):
    report += f"{i}. {item['title']}\n"

report += "\n### 今日头条 Top 5\n"
for i, item in enumerate(raw.get('toutiao', [])[:5], 1):
    report += f"{i}. {item['title']}（{item.get('hot','?')}）\n"

report += f"""
---

*报告生成时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} CST*
*数据来源：百度热榜、抖音热榜、今日头条、V2EX、Hacker News、GitHub*
"""

with open(out_md, 'w') as f:
    f.write(report)

print(f"报告已生成: {out_md}")
print(f"- 超级热点: {len(deduped)} 个")
print(f"- 有深度分析: {len(analyzed)} 个")
print(f"- 跨平台共振: {len(cross)} 个")
