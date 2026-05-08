# Phase 5 串联测试产出 — 2026-04-30

## 环节2：选题质量评估联调 ✅

**输入**：HN采集数据 60条 (hn_grief_20260430_081658.json)
**筛选规则**：Phase 4 运营规划中的糗事判断标准
**产出**：10条合格选题

## 环节3：每日选题列表生成联调 ✅

**输入**：环节2产出 + Phase 4列表格式模板
**产出**：每日选题列表 JSON

```json
{
  "date": "2026-04-30",
  "items": [
    {
      "id": "001",
      "title": "Meta's live demo fails; \"AI\" recording plays before the actor takes the steps",
      "source": "HN (points:466, comments:342)",
      "source_url": "https://www.reddit.com/r/LivestreamFail/comments/1nkbig7/metas_live_staged_demo_fails_the_ai_recording/",
      "platform_tags": ["hn", "reddit"],
      "heat_score": 100,
      "category": "AI硬件翻车",
      "publish_platform": "小红书+Reddit",
      "publish_time": "20:00",
      "notes": "specific_incident+high_points(466)+fail_theme+visual_content+known_brand | engagement: 466pts/342cmts"
    },
    {
      "id": "002",
      "title": "'Shame': Mark Zuckerberg's Meta 'AI glasses' fail live demo, video emerges",
      "source": "HN (points:19, comments:3)",
      "source_url": "https://indianexpress.com/article/trending/trending-globally/mark-zuckerberg-meta-ai-glasses-fail-live-demo-video-emerges-10257294/",
      "platform_tags": ["hn", "reddit"],
      "heat_score": 75,
      "category": "AI硬件翻车",
      "publish_platform": "Reddit",
      "publish_time": "09:00",
      "notes": "specific_incident+fail_theme+visual_content+known_brand | engagement: 19pts/3cmts"
    },
    {
      "id": "003",
      "title": "AI has failed to replace a single software application or feature",
      "source": "HN (points:21, comments:23)",
      "source_url": "https://news.ycombinator.com/item?id=46827128",
      "platform_tags": ["hn", "reddit"],
      "heat_score": 50,
      "category": "AI替代人类",
      "publish_platform": "Reddit",
      "publish_time": "09:00",
      "notes": "specific_incident+fail_theme | engagement: 21pts/23cmts"
    },
    {
      "id": "004",
      "title": "A failed AI girlfriend product, and my lessons",
      "source": "HN (points:253, comments:382)",
      "source_url": "https://mazzzystar.github.io/2023/11/16/ai-girlfriend-product/",
      "platform_tags": ["hn", "reddit"],
      "heat_score": 45,
      "category": "AI商业化失败",
      "publish_platform": "小红书+Reddit",
      "publish_time": "20:00",
      "notes": "high_points(253)+fail_theme | engagement: 253pts/382cmts"
    },
    {
      "id": "005",
      "title": "AI Failures in 2017",
      "source": "HN (points:212, comments:92)",
      "source_url": "https://syncedreview.com/2017/12/23/2017-in-review-10-ai-failures/",
      "platform_tags": ["hn", "reddit"],
      "heat_score": 45,
      "category": "AI产品翻车",
      "publish_platform": "小红书+Reddit",
      "publish_time": "20:00",
      "notes": "high_points(212)+fail_theme | engagement: 212pts/92cmts"
    },
    {
      "id": "006",
      "title": "Not worried about AI that passes Turing test, but AI that fails it on purpose",
      "source": "HN (points:83, comments:80)",
      "source_url": "https://old.reddit.com/r/C_S_T/comments/ae288t/im_not_worried_about_ai_that_can_pass_the/",
      "platform_tags": ["hn", "reddit"],
      "heat_score": 35,
      "category": "AI产品翻车",
      "publish_platform": "Reddit",
      "publish_time": "09:00",
      "notes": "med_points(83)+fail_theme | engagement: 83pts/80cmts"
    },
    {
      "id": "007",
      "title": "Generative AI's failure to induce robust models of the world",
      "source": "HN (points:76, comments:82)",
      "source_url": "https://garymarcus.substack.com/p/generative-ais-crippling-and-widespread",
      "platform_tags": ["hn", "reddit"],
      "heat_score": 35,
      "category": "AI产品翻车",
      "publish_platform": "Reddit",
      "publish_time": "09:00",
      "notes": "med_points(76)+fail_theme | engagement: 76pts/82cmts"
    },
    {
      "id": "008",
      "title": "74% of CEOs worry AI failures could cost them their jobs",
      "source": "HN (points:55, comments:73)",
      "source_url": "https://cfo.economictimes.indiatimes.com/news/74-of-ceos-worry-ai-failures-could-cost-them-their-jobs-report/118923383",
      "platform_tags": ["hn", "reddit"],
      "heat_score": 35,
      "category": "AI替代人类",
      "publish_platform": "Reddit",
      "publish_time": "09:00",
      "notes": "med_points(55)+fail_theme | engagement: 55pts/73cmts"
    },
    {
      "id": "009",
      "title": "Why AI is failing at giving good advice",
      "source": "HN (points:37, comments:38)",
      "source_url": "https://maximzubarev.com/why-ai-is-failing-at-giving-good-advice",
      "platform_tags": ["hn", "reddit"],
      "heat_score": 20,
      "category": "AI产品翻车",
      "publish_platform": "Reddit",
      "publish_time": "09:00",
      "notes": "fail_theme | engagement: 37pts/38cmts"
    },
    {
      "id": "010",
      "title": "Top AI models fail at >96% of tasks",
      "source": "HN (points:24, comments:10)",
      "source_url": "https://www.zdnet.com/article/ai-failed-test-on-remote-freelance-jobs/",
      "platform_tags": ["hn", "reddit"],
      "heat_score": 20,
      "category": "AI产品翻车",
      "publish_platform": "Reddit",
      "publish_time": "09:00",
      "notes": "fail_theme | engagement: 24pts/10cmts"
    }
  ]
}
```

## 筛选标准（来自Phase 4）
- 事件性：排除泛泛的AI讨论/研究报告/论文
- 意外性：fail/意外主题优先
- 可传播性：有视频/demo/具体事件优先
- 版权风险：排除特定个人隐私内容
- 加分：知名AI公司/产品、多平台热点、高互动

## 下一步
环节2+3 ✅ 产出已就绪，等待 Stephen 配图方案完成后，可进入环节4（文案+配图生成）。
