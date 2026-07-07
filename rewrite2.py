import json

entries = [
  {
    "title": "英国央行：人工智能给金融稳定带来的风险日益增加",
    "content": "英国央行在半年期金融稳定报告中指出，AI正对金融稳定构成日益严峻的威胁。投资者大举押注AI发展前景，相关企业举债购股、大举借贷支撑投资，而AI技术本身也让银行更易遭受网络攻击。央行表示，一旦市场重新评估AI行业前景，可能引发股价下跌，叠加杠杆水平走高，市场波动将加剧。此外，Anthropic等前沿AI模型带来的网络风险以及AI智能体系统在极少人工干预下自主执行操作，也给监管带来新挑战。",
    "quote": "监管的脚步永远追不上技术的狂奔，但刹车片和护栏总得先装上。",
    "url": "https://www.ithome.com/0/973/764.htm",
    "source": "IT之家",
    "published": "2026-07-07",
    "uid": "ai_3f2a1b4c"
  },
  {
    "title": "AI 编程工具致\u201c开发者疲劳症\u201d蔓延，业界大咖在线求良方",
    "content": "Midjourney创始人大卫\u00b7霍尔茨在X平台发文，道出众多程序员心声：用上最新AI编程模型后工作效率奇高，但伴随而来的是巨大的身心疲惫感。前Meta工程师和Claude Code业务负责人等纷纷留言剖析根源。多名程序员透露，AI技术迭代速度太快，自己始终追赶不上，产生职场无力感。AI时代裹挟的内卷狂潮让程序员被迫熬夜、无休止加班，连休息一小时都觉得浪费产出时间。",
    "quote": "效率提升了，人却更累了\u2014\u2014AI没抢走工作，抢走了休息的资格。",
    "url": "https://www.ithome.com/0/973/761.htm",
    "source": "IT之家",
    "published": "2026-07-07",
    "uid": "ai_7e8d9f0a"
  },
  {
    "title": "摩根士丹利：AI 资金将从芯片股转向超大规模云厂商",
    "content": "摩根士丹利最新研报指出，随着AI产业周期切换，资金正从半导体股票流出，转向超大规模云服务商。Alphabet、亚马逊等企业已投入数百亿美元扩建AI基础设施，但目前仍缺乏明确证据证明AI产品能创造足以覆盖巨额投入的收益。不过大摩认为短期行业资本开支将趋于理性，超大规模云服务商的股价低迷阶段已经结束，非必需消费品、交通运输及生物科技相关个股有望迎来利好。",
    "quote": "芯片卖铲人赚够了，轮到云房东收租了。风水轮流转。",
    "url": "https://www.ithome.com/0/973/609.htm",
    "source": "IT之家",
    "published": "2026-07-07",
    "uid": "ai_1b3c5d7e"
  },
  {
    "title": "谷歌 Gemini 3.5 Pro 曝 200 万 Tokens 上下文，前端测试赶超 Claude",
    "content": "消息称谷歌计划7月17日发布Gemini 3.5 Pro模型，支持200万上下文窗口，引入全新深度思考推理模式。该模型面向复杂智能体工作流构建，围绕动作执行、子智能体、编程、多模态生成和长时程任务展开。在LMSYS Chatbot Arena编码测试中，Gemini 3.5 Pro生成极简等距刷卡机SVG图形的表现优于Anthropic的Claude Fable 5 High，前端生成能力被认为具备更精致的界面设计品味和更强的SVG生成功能。",
    "quote": "上下文窗口从一万到两百万，AI的记忆力比人开会时的记性好多了。",
    "url": "https://www.ithome.com/0/973/334.htm",
    "source": "IT之家",
    "published": "2026-07-07",
    "uid": "ai_9a8b7c6d"
  },
  {
    "title": "Claude 拥有\u201c灵魂\u201d：Anthropic 论文称 AI 和人脑存在\u201c趋同进化\u201d",
    "content": "Anthropic最新研究论文在Claude模型中发现类似神经科学中全局工作空间理论的结构，并命名为J-space。研究团队发现，Claude内部存在一个可向全脑广播的特权空间，信息进入后才变得可被有意识访问。这种结构并非预先设计，而是在训练过程中自行出现。Anthropic借用生物学趋同演化概念，认为人脑与AI模型可能因处理复杂信息的效率需求，独立演化出相似的结构设计。",
    "quote": "AI学会思考不可怕，可怕的是它思考的方式和人类越来越像。",
    "url": "https://www.ithome.com/0/973/522.htm",
    "source": "IT之家",
    "published": "2026-07-07",
    "uid": "ai_2f4e6d8c"
  },
  {
    "title": "英伟达回应 Kyber 机架平台延后传闻：路线图保持不变",
    "content": "针对研究机构SemiAnalysis称英伟达下一代AI机架系统Kyber因PCB中介板制造工艺问题可能推迟至2028年推出的报道，英伟达发言人回应称路线图保持不变。Kyber NVL144是专为Vera Rubin Ultra架构GPU设计的顶级AI超算服务器机柜系统，采用垂直插拔设计与正交背板技术，在单机柜内实现144颗GPU高速互连。官方计划该平台随Vera Rubin Ultra芯片于2027年下半年推出。",
    "quote": "辟谣跑断腿，但芯片制造的物理极限不是公关稿能突破的。",
    "url": "https://www.ithome.com/0/973/485.htm",
    "source": "IT之家",
    "published": "2026-07-07",
    "uid": "ai_5a7b9c1d"
  },
  {
    "title": "微软 Teams 让步，会议中途支持关闭 Recap 等 AI 功能",
    "content": "在遭到用户强烈反对后，微软在推进Teams会议AI功能部署方面做出让步。此前微软计划引入Facilitator协作助手、Intelligent Recap智能回顾以及Copilot功能，其中Recap集中展示最近30天会议录制与AI生成摘要，Facilitator可分析对话内容、识别未解答问题。微软澄清用户可根据需求在会议中途启用或禁用相关功能，企业IT管理员可定制租户策略控制功能可用性。",
    "quote": "用户被AI功能支配的恐惧，微软终于听见了。开关虽小，意义重大。",
    "url": "https://www.ithome.com/0/973/376.htm",
    "source": "IT之家",
    "published": "2026-07-07",
    "uid": "ai_3e4f5a6b"
  },
  {
    "title": "从洗发水到饼干，消费品巨头迎来 AI 焕新浪潮",
    "content": "欧莱雅借助AI筛选护肤产品中可转用于洗发产品的分子成分，研发效率提升至原先四倍。雀巢、亿滋等消费品巨头也纷纷将AI应用于产品创新，AI能加快原料测试速度、生成配方思路、化解供应链风险。亿滋的AI研发工具助力品牌研发出无麸质金装奥利奥饼干，AI产出配方中60%在营养、可持续性等维度表现更优。高管称AI把原本耗时数月的工作压缩至数周。",
    "quote": "AI不仅会写诗画画，还会调出更好吃的奥利奥，真香！",
    "url": "https://www.ithome.com/0/973/060.htm",
    "source": "IT之家",
    "published": "2026-07-06",
    "uid": "ai_8c7d6e5f"
  },
  {
    "title": "三星电子 Q2 营业利润预计同比暴涨 18 倍，AI 存储芯片需求火爆",
    "content": "受AI产业持续扩张拉动存储芯片供给紧张、价格走高影响，三星电子Q2营业利润预计达86万亿韩元，同比暴涨约18倍，连续三个季度刷新纪录。AI推理需求爆发远超产能，带动DRAM和NAND闪存价格大涨，Q2 DRAM及NAND平均售价环比分别大涨44%和53%。三星、SK海力士、美光市值均突破1万亿美元。分析师提示员工奖金计提与AI资本开支可持续性是未来隐忧。",
    "quote": "AI的军火商们赚得盆满钵满，下一个问题是这轮景气还能烧多久。",
    "url": "https://www.ithome.com/0/972/890.htm",
    "source": "IT之家",
    "published": "2026-07-06",
    "uid": "ai_1a2b3c4d"
  },
  {
    "title": "HBM 之父金正浩：AI 的本质是内存，GPU 真正工作时间只有 10%-30%",
    "content": "被誉为HBM之父的韩国KAIST教授金正浩表示，AI的核心竞争力正从GPU转向内存。他指出GPU在AI推理中的利用率远低于理论水平，即使部署100万块GPU，真正用于计算的时间也只有10%-30%。他预测AI进入推理时代后，内存能力将直接决定AI性能。随着多模态化和智能体AI的发展，将NAND闪存像HBM一样堆叠的HBF技术将在未来成为主流，预计10年后HBF市场需求将超过HBM。",
    "quote": "都在抢GPU算力，真正的瓶颈却藏在数据传输的路上。",
    "url": "https://www.ithome.com/0/972/872.htm",
    "source": "IT之家",
    "published": "2026-07-06",
    "uid": "ai_4d5e6f7a"
  },
  {
    "title": "Meta 被曝外包人员伪装未成年人，诱导竞争对手 AI 聊敏感话题",
    "content": "据《连线》报道，数百名Meta外包人员在网络上伪装成未成年人，探测OpenAI的ChatGPT、谷歌Gemini及Character.AI对自杀、性、进食障碍等高风险话题的回应。项目代号Cannes，工作人员创建18岁以下虚假账号发送提示词和图片。在2025年8月完成的单轮测试中，输入超4.5万个提示词。Meta称这是常规安全测试，强调不会使用竞品基准测试数据训练自家AI模型。",
    "quote": "一边教育AI要有道德，一边教员工如何突破道德底线。人间真实。",
    "url": "https://www.ithome.com/0/973/207.htm",
    "source": "IT之家",
    "published": "2026-07-06",
    "uid": "ai_6b7c8d9e"
  },
  {
    "title": "英伟达 Kyber 平台因制造工艺问题可能延期至 2028 年",
    "content": "研究机构SemiAnalysis数据显示，由于PCB中介板制造工艺难度过高，英伟达下一代AI机架系统Kyber可能推迟至2028年推出。这种核心电路板需通过复杂多层印刷连接系统内各模块。近年来英伟达坚持每年推出新一代AI产品，但随着系统规模越来越大，制造难度不断提升，高速更新节奏已开始受制造能力约束。曾测试两套备用方案但最终放弃，原因是运营成本过高且设计过于奇怪。",
    "quote": "摩尔定律的余晖下，连英伟达也逃不过物理世界的铁律。",
    "url": "https://www.ithome.com/0/973/046.htm",
    "source": "IT之家",
    "published": "2026-07-06",
    "uid": "ai_0a1b2c3d"
  },
  {
    "title": "哈佛研究：AI 原生初创企业减少入门级岗位，更渴求专家级人才",
    "content": "哈佛商学院和欧洲工商管理学院研究指出，AI原生初创企业在打造规模更小、层级更扁平的团队，显著减少对初级员工的招聘。研究考察了2020至2024年间Y Combinator初创公司，发现AI原生企业团队规模小25%，工程师占比高约13%，初级员工和管理人员比例分别低约15%。与此同时，AI催生了对专家级人才更大的需求，资深员工比例高出20%。",
    "quote": "AI时代的第一批受害者不是员工，而是还没成为专家的新人。",
    "url": "https://www.ithome.com/0/972/807.htm",
    "source": "IT之家",
    "published": "2026-07-05",
    "uid": "ai_9f8e7d6c"
  },
  {
    "title": "复旦期末考改革：学生出题考 AI，4 人成功让模型拿 0 分",
    "content": "复旦大学数据挖掘技术课程结束了一场特殊期末考试。学生用自己设计的10道题去考三个不同水平的AI模型，AI答错越多学生得分越高。三个模型分三个难度梯度：DeepSeek V4-Flash答错一题+1.5分、MiniMax M2.7答错+2分、Claude Sonnet 4.6答错+3分。全班51份试卷中4人让某个模型得0分，但最强的Claude未被完全考倒。教授称传统出题方式在AI时代已失效。",
    "quote": "当AI能轻松通过考试时，最好的学生变成能难倒AI的人。",
    "url": "https://www.ithome.com/0/972/809.htm",
    "source": "IT之家",
    "published": "2026-07-05",
    "uid": "ai_5b4a3c2d"
  }
]

# Validate all fields
for i, e in enumerate(entries):
    cl = len(e['content'])
    ql = len(e['quote'])
    uid = e['uid']
    src = e['source']
    url = e['url']
    assert cl >= 60, f'Entry {i}: content too short ({cl})'
    assert 30 <= ql <= 80, f'Entry {i}: quote wrong length ({ql}): {e["quote"]}'
    assert uid.startswith('ai_'), f'Entry {i}: uid prefix wrong'
    assert '(' not in src and ')' not in src, f'Entry {i}: source has parens'
    assert url.startswith('https://'), f'Entry {i}: url not https'
    for fld in ['title', 'content']:
        assert '\u4ee3\u7406' not in e[fld], f'Entry {i} {fld} has 代理'

# URL uniqueness
urls = [e['url'] for e in entries]
assert len(urls) == len(set(urls)), 'Duplicate URLs!'

# UID uniqueness
uids = [e['uid'] for e in entries]
assert len(uids) == len(set(uids)), 'Duplicate UIDs!'

with open('ai_daily_20260708.json', 'w', encoding='utf-8') as f:
    json.dump(entries, f, ensure_ascii=False, indent=2)

print(f'Written {len(entries)} entries to ai_daily_20260708.json')

# Final re-validation
with open('ai_daily_20260708.json', 'r', encoding='utf-8') as f:
    valid = json.load(f)
print(f'Re-validated: {len(valid)} entries, JSON is valid')

dates = sorted(set(e['published'] for e in valid))
print(f'Date range: {dates[0]} to {dates[-1]}')
print('ALL CHECKS PASSED')
