import json, subprocess, sys

APP = "RIYebA1R7aKZ02sCHBhc9Twxntf"
TBL = "tbl2LN4fBmsg0L4r"

tasks = [
    {"task_id": "multi-agent-collab-20260501", "name": "Multi-Agent协作机制与最佳实践", "link": "https://feishu.cn/docx/XvYWdS0CJonlwDxka9PcsnDvnnh", "desc": "验证 Lucia/Stephen/Thomas 三Agent协作模式，确立调度中心角色与 sessions_send 规范", "owner": "ou_229a693d4119ce6c9459b27e38fb254c", "ts": 1746134400000},
    {"task_id": "claude-code-investigation-20260501", "name": "Claude Code歧视OpenClaw用户", "link": "https://feishu.cn/docx/NWsjd4falornbUx2vXicDDSfnAb", "desc": "测试 GitHub Copilot 是否对 OpenClaw 用户存在歧视性定价或拒绝服务", "owner": "ou_229a693d4119ce6c9459b27e38fb254c", "ts": 1746134400000},
    {"task_id": "linkedin-privacy-scan-20260501", "name": "LinkedIn隐私扫描", "link": "https://feishu.cn/docx/GdNXdQEf6oAbs3xy4GJcMgoEnYf", "desc": "AI代码助手的隐私政策调研，验证数据是否被用于模型训练", "owner": "ou_229a693d4119ce6c9459b27e38fb254c", "ts": 1746134400000},
    {"task_id": "openclaw-personality-generator-20260501", "name": "OpenClaw人格生成器", "link": "https://feishu.cn/docx/J2eUdErDqo4rFexZMqXcFmHRnuh", "desc": "为 Lucia 生成专属人格设定，包括 SOUL.md 和 IDENTITY.md，8维度人格框架", "owner": "ou_229a693d4119ce6c9459b27e38fb254c", "ts": 1746134400000},
    {"task_id": "questionnaire-personality-20260501", "name": "问卷式人格生成器", "link": "https://feishu.cn/docx/CwAXdsMTaojWTWxKVnucJTprnjc", "desc": "问卷形式的 Lucia 人格特征采集工具，24题覆盖8维度，单选+李克特量表", "owner": "ou_229a693d4119ce6c9459b27e38fb254c", "ts": 1746134400000},
    {"task_id": "hot-topics-tracker-20260501", "name": "热点追踪", "link": "https://feishu.cn/docx/WAlId82umoXJ2hx7js4cCdlRnIn", "desc": "基于热点追踪系统产出的技术社区向文章，510字，面向开发者读者", "owner": "ou_229a693d4119ce6c9459b27e38fb254c", "ts": 1746134400000},
    {"task_id": "multi-platform-trending-20260501", "name": "多平台热点交叉分析报告", "link": "https://feishu.cn/docx/QWDbdq5jpouvAhx8MpbcTgqdnsc", "desc": "6个主流内容平台同时并行采集热点，汇总跨平台热度分析，Thomas文案+Stephen配图", "owner": "ou_229a693d4119ce6c9459b27e38fb254c", "ts": 1746134400000},
    {"task_id": "lobster-pa-001", "name": "Lobster PA项目", "link": "https://feishu.cn/docx/Nl9Gdy4CCoqT6FxyaTmcyVLennf", "desc": "Lobster PA项目报告", "owner": "ou_229a693d4119ce6c9459b27e38fb254c", "ts": 1746134400000},
    {"task_id": "novel-gen-001", "name": "网络小说生成项目", "link": "https://feishu.cn/docx/Nxv2dBhiLoZgUaxUNZJcb7gUnGb", "desc": "测试网络小说生成全流程：GPT类/专用长文本/中文预训练模型/Agent流水线", "owner": "ou_229a693d4119ce6c9459b27e38fb254c", "ts": 1746134400000},
    {"task_id": "novel-intl-001", "name": "海外网文市场机会调研", "link": "https://feishu.cn/docx/MKQLdTyaVoAUvjxqcoIcDbD3nqt", "desc": "调研海外网文平台（Webnovel/Wattpad/Royal Road等）及中国网文出海机会", "owner": "ou_229a693d4119ce6c9459b27e38fb254c", "ts": 1746134400000},
    {"task_id": "openclaw-version-001", "name": "OpenClaw版本调研", "link": "https://feishu.cn/docx/OZBmdH6SSoP8CixcPZdcuL5Cnab", "desc": "调研 OpenClaw 各版本能力差异，评估是否需要升级及升级路径", "owner": "ou_229a693d4119ce6c9459b27e38fb254c", "ts": 1746134400000},
    {"task_id": "optimize-001", "name": "优化方案报告", "link": "https://feishu.cn/docx/GMwNd1wlHoGyJUx2yGdcDyLvnEe", "desc": "对早报系统任务链路的优化分析，提出状态机+Pipeline 等改进方案", "owner": "ou_229a693d4119ce6c9459b27e38fb254c", "ts": 1746134400000},
    {"task_id": "skill-research-001", "name": "技能研究报告", "link": "https://feishu.cn/docx/S3e9dTfV6oeSDSxkcnVcZcsWnKd", "desc": "Clawhud 和 GitHub 热门技能平台调研，分析52.7k工具数据，Stephen+Thomas双报告", "owner": "ou_229a693d4119ce6c9459b27e38fb254c", "ts": 1746134400000},
    {"task_id": "long-task-queue-20260502", "name": "长任务队列机制方案", "link": "https://feishu.cn/docx/JLjId5PBVoSXolxjlJbc5Nzpnvb", "desc": "为 Lucia 建立长期记忆能力，支持任务持久化、Boss任务队列写入、跨session恢复", "owner": "ou_229a693d4119ce6c9459b27e38fb254c", "ts": 1746144000000},
    {"task_id": "long-term-memory-research-20260502", "name": "长时记忆最佳实践调研", "link": "https://feishu.cn/docx/JLjId5PBVoSXolxjlJbc5Nzpnvb", "desc": "Stephen 调研结论：推荐飞书多维表格为核心方案，扩展现有架构，无需引入外部系统", "owner": "ou_e1f7eb7502f403e1704adecb6646a506", "ts": 1746144000000},
    {"task_id": "daily-review-20260501", "name": "【每日复盘】2026-05-01", "link": "https://feishu.cn/docx/I4LsdNqhroRlA0xhkcJch3Y0nif", "desc": "Lucia 主持的三方复盘会议，Stephen/Thomas/Lucia 参与，总结首日协作验证的得失", "owner": "ou_229a693d4119ce6c9459b27e38fb254c", "ts": 1746134400000},
    {"task_id": "morning-news-001", "name": "早报采集方案设计", "desc": "早报系统的采集方案设计，探索不同来源的热点内容采集模式", "owner": "ou_229a693d4119ce6c9459b27e38fb254c", "ts": 1746134400000},
    {"task_id": "knowledge-base-001", "name": "知识库项目", "desc": "调研结论已在群消息/复盘文档中，无技术产出物", "owner": "ou_229a693d4119ce6c9459b27e38fb254c", "ts": 1746134400000},
    {"task_id": "hot-news-001", "name": "热点新闻采集", "desc": "调研结论已在群消息/复盘文档中，无技术产出物", "owner": "ou_229a693d4119ce6c9459b27e38fb254c", "ts": 1746134400000},
    {"task_id": "awesome-insight-001", "name": "Awesome Insight项目", "desc": "调研结论已在群消息/复盘文档中，无技术产出物", "owner": "ou_229a693d4119ce6c9459b27e38fb254c", "ts": 1746134400000},
    {"task_id": "optimize-002", "name": "优化方案002", "desc": "调研结论已在群消息/复盘文档中，无技术产出物", "owner": "ou_229a693d4119ce6c9459b27e38fb254c", "ts": 1746134400000},
    {"task_id": "hot-trend-parallel-001", "name": "热点并行测试", "desc": "调研结论已在群消息/复盘文档中，无技术产出物", "owner": "ou_229a693d4119ce6c9459b27e38fb254c", "ts": 1746134400000},
    {"task_id": "pilot-test-project", "name": "Pilot测试项目", "desc": "调研结论已在群消息/复盘文档中，无技术产出物", "owner": "ou_229a693d4119ce6c9459b27e38fb254c", "ts": 1746134400000},
]

for t in tasks:
    fields = {
        "task_id": t["task_id"],
        "背景描述": t["desc"],
        "创建时间": t["ts"],
        "状态": "completed",
        "负责人": [{"id": t["owner"]}]
    }
    if "link" in t and t.get("link"):
        fields["产出链接"] = {"link": t["link"], "text": t["name"]}

    cmd = [
        "python3", "-c",
        f"""
import json, subprocess
data = {json.dumps(fields, ensure_ascii=False)}
result = subprocess.run(
    ["node", "/root/.local/share/pnpm/global/5/.pnpm/openclaw@2026.4.21_@napi-rs+canvas@0.1.99/node_modules/openclaw/dist/extensions/feishu/cli/bitable.js",
     "create_record", "--app_token={APP}", "--table_id={TBL}", "--fields=" + json.dumps(data)],
    capture_output=True, text=True
)
print(result.stdout, result.stderr)
"""
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(f"[{t['task_id']}] rc={r.returncode}")
    if r.stdout:
        print(r.stdout[:200])
    if r.stderr:
        print(r.stderr[:200])

print("DONE")
